# Generate_aidercommands.ps1

## Overview

`Generate_aidercommands.ps1` is a four-stage PowerShell pipeline that uses Claude to
transform a rough project idea into ready-to-execute aider commands. It bridges the gap
between human intent and local LLM code generation: Claude handles the architectural
thinking, and the local LLM (via aider) handles the implementation.

The script lives in `LocalLLMCoding/` and operates on prompt files in a target directory
(default: `LocalLLMCodePrompts/`). It is designed to be run repeatedly as a project
evolves -- each iteration builds on previously implemented plans.

Stages 2 and 3 use a two-pass approach: a planning pass decomposes the work into
sections/steps, then each section/step is generated individually. This avoids output
truncation on large documents and makes the pipeline resumable at a granular level.

## Pipeline Stages

### Stage 0 -- Summarize Existing Codebase (automatic)

Runs automatically when `Implemented Plans/` contains one or more previously completed
architecture plans. Skipped entirely on the first run when no prior plans exist.

- **Input**: All `Architecture Plan *.md` files from `Implemented Plans/`
- **Output**: `Implemented Plans/Codebase Summary.md`
- **Claude calls**: 1
- **What Claude does**: Reads every implemented plan in chronological order and produces
  a single consolidated summary of the codebase as it exists today. Where later plans
  modified earlier designs, the summary reflects the final state only. The summary
  covers project structure, data models, module inventory, dependencies, configuration,
  and established patterns.
- **Why**: Raw plans accumulate over iterations and can grow to 100KB+ with overlapping
  or contradictory details. A compact summary gives stages 2 and 3 clean context
  without bloating the prompt.

### Stage 1 -- Improve Initial Prompt

- **Input**: `InitialPrompt.md` (in the target directory)
- **Output**: `Implementation Planning Prompt.md` + `PromptUpdates.md`
- **Claude calls**: 1
- **What Claude does**: Reviews the rough prompt for gaps, contradictions, and ambiguity.
  Produces a refined planning prompt that specifies tech stack, data model, UI
  requirements, testing strategy, and architecture deliverables. Separately outputs a
  critique documenting what was changed and why.
- **Separator protocol**: Claude's response is split on the literal line
  `---PROMPT_UPDATES---`. Everything before it becomes the improved prompt; everything
  after becomes the critique saved in `PromptUpdates.md`.

### Stage 2 -- Generate Architecture Plan (two-pass)

- **Input**: `Implementation Planning Prompt.md` + `Codebase Summary.md` (if it exists)
- **Output**: `Architecture Plan.md`
- **Claude calls**: 1 (planning) + N (one per section, typically 10-15)

Stage 2 uses a two-pass approach to avoid output truncation on large architecture plans:

**Stage 2a -- Section planning** (one Claude call): Asks Claude to decompose the
architecture plan into a numbered section list. Each entry specifies a section title and
what it covers. The list is saved to `.section_plan.md` in the target directory.

**Stage 2b -- Per-section generation** (one Claude call per section): Loops through each
section in the plan. Each call receives the full planning prompt as context and generates
one detailed section of the architecture plan. Each section is appended to
`Architecture Plan.md` as it completes. Progress is saved after each section.

### Stage 3 -- Generate Aider Commands (two-pass)

- **Input**: `Architecture Plan.md` + `Codebase Summary.md` (if it exists)
- **Output**: `aidercommands.md`
- **Claude calls**: 1 (planning) + N (one per step, typically 15-25)

Stage 3 uses the same two-pass approach:

**Stage 3a -- Step planning** (one Claude call): Asks Claude to decompose the
architecture plan into ordered implementation steps. Each entry specifies a step number,
title, and target files. The list is saved to `.step_plan.md` in the target directory.

**Stage 3b -- Per-step generation** (one Claude call per step): Loops through each step.
Each call receives the architecture plan as context and generates one self-contained
aider command with complete type definitions, function signatures, imports, and
pseudocode. Each step is appended to `aidercommands.md` as it completes.

### Output Format of aidercommands.md

Each step in the generated file follows this structure:

```
## Step N -- Title

\```bash
aider --yes src/project/module.py
\```
\```
<self-contained prompt with full context for the local LLM>
\```
```

The prompts are intentionally verbose because the local LLM has no access to the
architecture plan or codebase summary. Every type, signature, and behavioral detail
needed for implementation is repeated inline.

## Resumability

The script tracks progress in a `.progress` file in the target directory. If the script
is interrupted (rate limit, network error, Ctrl+C), re-running it automatically resumes
from where it stopped.

### How it works

- After each stage or sub-step completes, the `.progress` file is updated with the last
  completed stage and sub-step number
- On startup, the script reads `.progress` and adjusts `-FromStage` to skip completed
  work
- Stages 2 and 3 also track per-section/per-step progress via `.section_plan.md` and
  `.step_plan.md` files that persist between runs

### Resume scenarios

| Scenario                          | What happens on re-run                           |
|-----------------------------------|--------------------------------------------------|
| Interrupted during Stage 1        | Restarts Stage 1 (single call, no sub-steps)     |
| Interrupted at Stage 2, section 5 | Skips sections 1-4, resumes from section 5       |
| Rate limited at Stage 3, step 12  | Skips stages 0-2 and steps 1-11, resumes step 12 |
| All stages completed              | Prints message and exits (use `-Restart`)        |

### Controlling resume behavior

```powershell
# Auto-resume (default) -- picks up where it left off
.\LocalLLMCoding\Generate_aidercommands.ps1

# Ignore saved progress, start fresh
.\LocalLLMCoding\Generate_aidercommands.ps1 -Restart

# Manual override -- start from a specific stage regardless of progress
.\LocalLLMCoding\Generate_aidercommands.ps1 -FromStage 2 -Restart
```

The `.progress` file is automatically deleted when all stages complete successfully.

## CLI Parameters

| Parameter      | Type       | Default              | Description                                                         |
|----------------|------------|----------------------|---------------------------------------------------------------------|
| `-TargetDir`   | `string`   | `LocalLLMCodePrompts`| Folder containing `InitialPrompt.md` and where output files are written. Relative paths resolve against the current working directory. |
| `-Claude`      | `string`   | `Claude1`            | Claude account to use. Maps to `CLAUDE_CONFIG_DIR`: `Claude1` = `.clauderivalon`, `Claude2` = `.claudefksogbetun`. |
| `-Model`       | `string`   | `opus`               | Claude model to use. Accepts aliases (`sonnet`, `opus`, `haiku`) or full model IDs (`claude-sonnet-4-6`, `claude-opus-4-6`). Applied to all stages. |
| `-SkipStage`   | `int[]`    | (none)               | Skip one or more stages. Accepts a list: `-SkipStage 1,2` skips stages 1 and 2. Stage 0 cannot be skipped (it runs automatically when prior plans exist). |
| `-FromStage`   | `int`      | `1`                  | Start from a specific stage, skipping all earlier stages. Valid values: 1, 2, 3. Stage 0 always runs if applicable. |
| `-Restart`     | `switch`   | `$false`             | Ignore saved progress and start from stage 1 (or the stage specified by `-FromStage`). Without this flag, the script auto-resumes from where it last stopped. |
| `-Force`       | `switch`   | `$false`             | Overwrite existing output files without prompting. By default, the script shows file name, size, and last-modified date before overwriting and asks for confirmation. |
| `-DryRun`      | `switch`   | `$false`             | Parse and preview all stages without calling Claude. Shows prompt sizes and first 200 characters of each prompt. |

## Overwrite Protection

Before each stage writes output, the script checks if the target files already exist.
If they do, it displays:

```
  The following output files already exist:
    Architecture Plan.md  (35.3 KB, modified 2026-04-13 10:30:00)
  Overwrite? [y/N]
```

Answering `N` (or pressing Enter) skips that stage. Each stage is checked independently,
so you can decline to overwrite the architecture plan but still regenerate
aidercommands.md. Use `-Force` to bypass all prompts.

## Account Selection

The `-Claude` parameter controls which Claude account is used. The script sets
`CLAUDE_CONFIG_DIR` directly (mirroring the wrapper functions in the PowerShell
profile) and calls `claude.exe`, which avoids stdin-forwarding issues that occur when
piping through PowerShell function wrappers.

| Value     | Config Directory                    |
|-----------|-------------------------------------|
| `Claude1` | `$env:USERPROFILE\.clauderivalon`   |
| `Claude2` | `$env:USERPROFILE\.claudefksogbetun`|

## Model Selection and Extended Thinking

The `-Model` parameter currently applies to all stages. All stage prompts include
`ultrathink.` to trigger Claude's extended thinking mode. However, not all stages
benefit equally from Opus or extended thinking.

### Analysis by stage

**Stage 0 -- Summarize Existing Codebase**

The task is synthesis: read multiple documents and produce a consolidated view. This is
mostly mechanical -- resolve contradictions, keep the latest version of each design
decision, and format the result. Extended thinking adds little value here because the
challenge is comprehensiveness, not deep reasoning.

Recommended: **Sonnet**, no ultrathink.

**Stage 1 -- Improve Initial Prompt**

A short review/editing task. The initial prompt is typically small (under 1KB) and the
improvements are straightforward -- identify missing details, resolve contradictions,
add specificity. This does not require the depth of reasoning that Opus provides.

Recommended: **Sonnet**, no ultrathink.

**Stage 2a -- Section Planning**

Structural decomposition of requirements into architecture plan sections. Getting the
section breakdown right matters because it determines the completeness of the
architecture plan. A poor decomposition results in missing modules or overlooked
concerns. This is a single short call, so cost is not a factor.

Recommended: **Opus** with ultrathink.

**Stage 2b -- Per-Section Architecture**

This is where the real architectural reasoning happens. Each section requires Claude to
make design decisions: choosing data structures, defining interfaces, planning error
handling, resolving tradeoffs between simplicity and flexibility. The quality of function
signatures, pseudocode, and module boundaries directly determines how well the local LLM
can implement each file. Bad decisions here cascade through the entire codebase.

This is the most thinking-intensive stage of the pipeline.

Recommended: **Opus** with ultrathink.

**Stage 3a -- Step Planning**

Dependency analysis: decompose the architecture into ordered implementation steps. The
architecture plan already defines the modules, so this is mostly about determining build
order -- what depends on what, when to introduce tests. Correct ordering matters (you
can't import a module that doesn't exist yet), but the architecture plan provides
enough structure that this is more analytical than creative.

Recommended: **Opus**, ultrathink optional.

**Stage 3b -- Per-Step Aider Commands**

Extraction and formatting: take the relevant portion of the architecture plan and
reformat it as a self-contained prompt for the local LLM. The architectural decisions
are already made in Stage 2 -- this stage is about being thorough in transcribing
every type, signature, import, and behavioral detail into the prompt. Sonnet excels at
this kind of structured, detail-oriented work.

This is also the highest-volume stage (one call per implementation step, typically
15-25 calls), making it the most expensive stage in the pipeline. Using Sonnet here
significantly reduces total cost.

Recommended: **Sonnet**, no ultrathink.

### Summary table

| Sub-stage           | Task type                 | Recommended model    | Ultrathink | Call volume |
|---------------------|---------------------------|----------------------|------------|-------------|
| Stage 0             | Synthesis/summarization   | Sonnet               | No         | 1           |
| Stage 1             | Review/editing            | Sonnet               | No         | 1           |
| Stage 2a (plan)     | Structural decomposition  | Opus                 | Yes        | 1           |
| Stage 2b (sections) | Architectural reasoning   | Opus                 | Yes        | 10-15       |
| Stage 3a (plan)     | Dependency analysis       | Opus                 | Optional   | 1           |
| Stage 3b (steps)    | Extraction/formatting     | Sonnet               | No         | 15-25       |

### Cost implications

A typical run with 12 architecture sections and 20 implementation steps makes
approximately 36 Claude API calls. Using Opus for all of them is expensive. Applying
the per-stage recommendations:

- **Opus calls**: 2a + 2b + 3a = 1 + 12 + 1 = 14 calls (architectural work)
- **Sonnet calls**: 0 + 1 + 3b = 1 + 1 + 20 = 22 calls (synthesis and formatting)

This focuses Opus on the stages where deep reasoning produces measurably better output,
and uses Sonnet for the high-volume stages where the task is structured extraction
rather than creative reasoning.

### Current implementation

The script currently uses a single `-Model` parameter for all stages. Per-stage model
selection is a planned enhancement that would allow specifying different models for
different stages, e.g.:

```powershell
# Hypothetical per-stage model selection
.\LocalLLMCoding\Generate_aidercommands.ps1 -ArchModel opus -CommandModel sonnet
```

## File Layout

### Input (required in target directory)

| File                | Purpose                                              |
|---------------------|------------------------------------------------------|
| `InitialPrompt.md`  | Rough project idea or feature request                |

### Output (generated in target directory)

| File                              | Stage | Purpose                                                      |
|-----------------------------------|-------|--------------------------------------------------------------|
| `Implementation Planning Prompt.md` | 1   | Refined, unambiguous planning prompt                        |
| `PromptUpdates.md`                | 1     | Critique of the initial prompt with changelog               |
| `Architecture Plan.md`            | 2     | Full architecture plan with pseudocode and test strategy    |
| `aidercommands.md`                | 3     | Self-contained aider steps for local LLM execution          |

### Output (generated in project root)

| File                                       | Stage | Purpose                                              |
|--------------------------------------------|-------|------------------------------------------------------|
| `Implemented Plans/Codebase Summary.md`    | 0     | Consolidated summary of all previously implemented plans |

### Temporary files (in target directory, cleaned up on completion)

| File                 | Stage | Purpose                                                    |
|----------------------|-------|------------------------------------------------------------|
| `.progress`          | All   | Tracks last completed stage and sub-step for resume        |
| `.section_plan.md`   | 2     | Section list for the architecture plan (deleted on completion) |
| `.step_plan.md`      | 3     | Step list for aider commands (deleted on completion)       |

## Iterative Development Workflow

The script is designed for repeated use as a project evolves:

```
First iteration (new project):

  InitialPrompt.md
       |
       v
  Generate_aidercommands.ps1     (no Stage 0 -- no prior plans)
       |
       v
  run_aider.py                   (executes aider steps with local LLM)
       |
       v
  Implemented Plans/             (Architecture Plan 1.md archived here)


Second iteration (adding features):

  New InitialPrompt.md
       |
       v
  Generate_aidercommands.ps1     (Stage 0 summarizes Plan 1)
       |                         (Stages 2-3 receive codebase context)
       v
  run_aider.py                   (extends existing code, not rewriting)
       |
       v
  Implemented Plans/             (Architecture Plan 2.md archived here)
```

After `run_aider.py` completes all steps, it:
1. Marks the prompts folder as completed (`.completed` marker)
2. Copies `Architecture Plan.md`, `aidercommands.md`, `Implementation Planning Prompt.md`,
   and `PromptUpdates.md` to `Implemented Plans/` with sequential numbering
   (e.g., `Architecture Plan 2.md`, `aidercommands 2.md`)

On the next run, `Generate_aidercommands.ps1` reads those archived plans in Stage 0
and generates a fresh `Codebase Summary.md`, ensuring Claude understands the current
state of the codebase before planning new work.

## Usage Examples

```powershell
# Full pipeline with defaults (Claude1, opus model)
.\LocalLLMCoding\Generate_aidercommands.ps1

# Re-run after interruption -- auto-resumes from where it stopped
.\LocalLLMCoding\Generate_aidercommands.ps1

# Ignore saved progress and start fresh
.\LocalLLMCoding\Generate_aidercommands.ps1 -Restart

# Use a different prompts folder
.\LocalLLMCoding\Generate_aidercommands.ps1 -TargetDir .\LocalLLMCodePrompts_V2

# Use second Claude account with Sonnet
.\LocalLLMCoding\Generate_aidercommands.ps1 -Claude Claude2 -Model sonnet

# Skip prompt improvement, regenerate architecture and commands only
.\LocalLLMCoding\Generate_aidercommands.ps1 -FromStage 2 -Restart

# Only regenerate aider commands from existing Architecture Plan
.\LocalLLMCoding\Generate_aidercommands.ps1 -FromStage 3 -Restart

# Skip stages 1 and 2, only run stage 3
.\LocalLLMCoding\Generate_aidercommands.ps1 -SkipStage 1,2

# Preview without calling Claude
.\LocalLLMCoding\Generate_aidercommands.ps1 -DryRun

# Overwrite everything without confirmation prompts
.\LocalLLMCoding\Generate_aidercommands.ps1 -Force

# After generation, execute the plan with the local LLM
python .\LocalLLMCoding\run_aider.py
python .\LocalLLMCoding\run_aider.py --prompts-dir LocalLLMCodePrompts_V2
```

## Prerequisites

- **Claude Code CLI** (`claude`) installed and available in PATH
- **PowerShell 5.1+** (Windows PowerShell or PowerShell Core)
- At least one Claude account configured (Claude1 or Claude2 via `CLAUDE_CONFIG_DIR`)
- An `InitialPrompt.md` file in the target directory describing the work to be done
