# Debug Workflow Quickstart

Condensed reference for the nmon2 LLM-assisted debugging pipeline. See `DebugWorkflow.md` for full details.

All scripts run from the **repo root**, read `LocalLLMDebug/.env`, and call the local Ollama server.

---

## Model Selection (pick this first)

The default `num_ctx` for `qwen2.5-coder:32b` is **32768** — that's ~8 GB of KV cache, enough to push total VRAM past a 24 GB card and force partial CPU offload (→ 4× slower inference → timeouts). Create two reduced-context variants once, then use them per-script.

### One-time setup on the Ollama server (PowerShell)

```powershell
# 8k variant — fits all analysis-only calls
@"
FROM qwen2.5-coder:32b
PARAMETER num_ctx 8192
"@ | Set-Content -Encoding ASCII Modelfile
ollama create qwen2.5-coder:32b-8k -f Modelfile

# 12k variant — needed for bughunt fix calls + big synth passes
@"
FROM qwen2.5-coder:32b
PARAMETER num_ctx 12288
"@ | Set-Content -Encoding ASCII Modelfile
ollama create qwen2.5-coder:32b-12k -f Modelfile
```

Verify each fits fully on GPU:
```powershell
ollama ps    # PROCESSOR column should say "100% GPU"
```

### VRAM fit on a 24 GB card (qwen 32b q4_K_M ≈ 19.85 GB)

| Variant                   | KV cache | Total    | Fit on 24 GB?              |
|---------------------------|----------|----------|----------------------------|
| `qwen2.5-coder:32b-8k`    | ~2.0 GB  | ~22.9 GB | Resident, fast             |
| `qwen2.5-coder:32b-12k`   | ~3.0 GB  | ~23.9 GB | Resident, tight            |
| `qwen2.5-coder:32b` (32k) | ~8.0 GB  | ~28.9 GB | **Partial offload — slow** |

### Per-script recommendation

| Script                            | Model                       | Why                                |
|-----------------------------------|-----------------------------|------------------------------------|
| `Arch_Analysis_Pipeline.py`                 | `qwen2.5-coder:32b-8k`      | All steps fit under 8k             |
| `bughunt_local.ps1`               | `qwen2.5-coder:32b-8k`      | Analysis-only, 900-token output    |
| **`bughunt_iterative_local.ps1`** | **`qwen2.5-coder:32b-12k`** | 4000-token fix calls need headroom |
| `dataflow_local.ps1`              | `qwen2.5-coder:32b-8k`      | Synth input fits under 8k          |
| **`interfaces_local.ps1`**        | **`qwen2.5-coder:32b-12k`** | Synth reads 10k+ tokens            |
| **`testgap_local.ps1`**           | **`qwen2.5-coder:32b-12k`** | Synth reads 10k+ tokens            |

### Wiring it up

Both models live in a single `LocalLLMDebug/.env`. The three heavy scripts
(`bughunt_iterative_local.ps1`, `interfaces_local.ps1`, `testgap_local.ps1`)
automatically prefer `LLM_MODEL_HIGH_CTX` when it's set; every other script
uses `LLM_MODEL`.

```ini
# LocalLLMDebug/.env
LLM_MODEL=qwen2.5-coder:32b-8k             # used by most scripts
LLM_MODEL_HIGH_CTX=qwen2.5-coder:32b-12k   # override for the three heavy scripts
LLM_TIMEOUT=300
```

```powershell
# No -EnvFile gymnastics — every script reads the same .env and picks the right model

# 8k (default) — uses LLM_MODEL
.\LocalLLMDebug\bughunt_local.ps1
.\LocalLLMDebug\dataflow_local.ps1

# 12k (auto) — uses LLM_MODEL_HIGH_CTX automatically
.\LocalLLMDebug\bughunt_iterative_local.ps1 -TargetDir src/nmon
.\LocalLLMDebug\interfaces_local.ps1
.\LocalLLMDebug\testgap_local.ps1
```

If you leave `LLM_MODEL_HIGH_CTX` unset (or comment it out), the three heavy
scripts fall back to `LLM_MODEL` — convenient when running `qwen2.5-coder:14b`
on a smaller GPU, where one model handles everything.

**Smaller GPU (<24 GB)**: drop to `LLM_MODEL=qwen2.5-coder:14b`. The 14b footprint (~9 GB at q4) fits on 12 GB cards with its default 32k context and needs no custom variants. Expect ~80% of the review depth of 32b but far fewer timeouts.

**Don't use `devstral-small-2`**: agentic model, not a reviewer. It over-rewrites, hallucinates findings, and triggers the `BLOAT` / `DIVERGING` guards constantly. Every convergence guard in the script exists because of what devstral did on earlier runs.

---

## Pipeline at a Glance

| Phase | Script                        | Purpose                                                 | Output                       |
|-------|-------------------------------|---------------------------------------------------------|------------------------------|
| 1     | `Arch_Analysis_Pipeline.py`             | Architecture docs (per-file + overview + xref + graphs) | `1. src/`                    |
| 1     | `dataflow_local.ps1`          | Cross-module data flow trace                            | `architecture/DATA_FLOW.md`  |
| 1     | `interfaces_local.ps1`        | Function contracts + silent failure modes               | `architecture/INTERFACES.md` |
| 2     | `bughunt_local.ps1`           | Single-pass bug scan (no fixes)                         | `bug_reports/`               |
| 3     | `testgap_local.ps1`           | Test coverage gap audit                                 | `test_gaps/GAP_REPORT.md`    |
| 4     | `bughunt_iterative_local.ps1` | Iterative analyse-and-fix loop                          | `bug_fixes/`                 |

**Recommended order:** Arch_Analysis_Pipeline → dataflow → interfaces → bughunt → testgap → bughunt_iterative.

All outputs are SHA1-cached — re-runs only re-process changed files. Use `-Clean` to wipe outputs and caches; `-Force` (where supported) ignores the cache without deleting outputs.

---

## Script Options

### `python LocalLLMAnalysis/Arch_Analysis_Pipeline.py` (in LocalLLMAnalysis)
Orchestrates the six-step architecture pipeline over each subsection in `.env`.

| Option           | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `--dry-run`      | Show commands without running them                                          |
| `--start-from N` | Skip the first N-1 subsections                                              |
| `--skip-lsp`     | Omit `generate_compile_commands` + `serena_extract` (always use for Python) |

### `bughunt_local.ps1`
Single-pass, non-modifying bug scanner. Writes `bug_reports/<rel>.md` + `SUMMARY.md`.

| Option              | Default | Description                               |
|---------------------|---------|-------------------------------------------|
| `-TargetDir <path>` | `.`     | Directory to scan                         |
| `-Clean`            | off     | Delete all reports + caches, then re-scan |
| `-Force`            | off     | Ignore SHA1 cache, re-scan every file     |
| `-EnvFile <path>`   | `.env`  | Alternate env file                        |

### `bughunt_iterative_local.ps1`
Iterative analyse-and-fix loop running up to 4 analysis types per iteration. Stages fixes in `bug_fixes/`. Tracks the best (lowest-HIGH) version across iterations and reverts to it on any non-CLEAN exit, so a bad run can never leave a file worse than it started.

| Option               | Default | Description                            |
|----------------------|---------|----------------------------------------|
| `-TargetDir <path>`  | `.`     | Source directory to process            |
| `-TestDir <path>`    | `tests` | Test directory for the test loop       |
| `-MaxIterations <n>` | `3`     | Max fix attempts per file              |
| `-ApplyFixes`        | off     | Write fixes back to source immediately |
| `-SkipBugs`          | off     | Disable bug analysis                   |
| `-SkipDataflow`      | off     | Disable data-flow analysis             |
| `-SkipContracts`     | off     | Disable contract analysis              |
| `-SkipTests`         | off     | Disable test-quality loop              |
| `-Clean`             | off     | Delete all output + caches             |
| `-Force`             | off     | Ignore SHA1 cache                      |
| `-EnvFile <path>`    | `.env`  | Alternate env file                     |

Stop statuses: `CLEAN`, `MAX_ITER`, `DIVERGING`, `BLOAT`, `STUCK`, `SYNTAX_ERR`, `ERROR`.

Convergence guards (tune via `.env`, not CLI):

| Env key                   | Default | Effect                                                |
|---------------------------|---------|-------------------------------------------------------|
| `BUGHUNT_BLOAT_RATIO`     | `1.5`   | Reject fix that grows file beyond this ratio vs. orig |
| `BUGHUNT_BLOAT_MIN_SLACK` | `15`    | Absolute line floor for tiny files                    |
| `BUGHUNT_DIVERGE_AFTER`   | `2`     | Abort after N consecutive non-improving iterations    |
| `LLM_TIMEOUT`             | `300`   | Per-LLM-call timeout (seconds); other scripts use 120 |

### `dataflow_local.ps1`
Two-pass extraction + synthesis. Produces `architecture/DATA_FLOW.md`.

| Option              | Default | Description                           |
|---------------------|---------|---------------------------------------|
| `-TargetDir <path>` | `.`     | Restrict extraction to a subdirectory |
| `-Clean`            | off     | Delete all extractions + output       |
| `-EnvFile <path>`   | `.env`  | Alternate env file                    |

No `-Force`. To re-extract one file, delete its `<sha1>.txt` from `architecture/.dataflow_state/extractions/`.

### `testgap_local.ps1`
Maps source → test files, runs per-file gap analysis, then synthesises a prioritised gap report.

| Option            | Default | Description            |
|-------------------|---------|------------------------|
| `-SrcDir <path>`  | `src`   | Source root            |
| `-TestDir <path>` | `tests` | Test root              |
| `-Clean`          | off     | Delete output + caches |
| `-EnvFile <path>` | `.env`  | Alternate env file     |

No `-Force` or `-TargetDir`. Per-file invalidation: delete the entry in `test_gaps/.testgap_state/cache/`.

### `interfaces_local.ps1`
Extracts per-function contracts (Requires / Guarantees / Raises / Silent failure / Thread safety), then synthesises `INTERFACES.md`.

| Option              | Default | Description                       |
|---------------------|---------|-----------------------------------|
| `-TargetDir <path>` | `.`     | Restrict to a subdirectory        |
| `-Clean`            | off     | Delete all contract docs + caches |
| `-EnvFile <path>`   | `.env`  | Alternate env file                |

---

## Quick Recipes

**Full cold start**
```powershell
python LocalLLMAnalysis/Arch_Analysis_Pipeline.py --skip-lsp
.\LocalLLMDebug\dataflow_local.ps1
.\LocalLLMDebug\interfaces_local.ps1
.\LocalLLMDebug\bughunt_local.ps1
.\LocalLLMDebug\testgap_local.ps1
```

**Wrong GPU metric on screen**
```powershell
.\LocalLLMDebug\bughunt_iterative_local.ps1 -TargetDir src/nmon/gpu -SkipTests
```
Then read `DATA_FLOW.md` (Handoff Points) + `INTERFACES.md` (Silent Failure Modes).

**Tests pass but production broken**
```powershell
.\LocalLLMDebug\testgap_local.ps1
.\LocalLLMDebug\bughunt_iterative_local.ps1 -SkipBugs -SkipDataflow -SkipContracts
```

**Auto-fix one subsystem on a branch**
```powershell
.\LocalLLMDebug\bughunt_iterative_local.ps1 -TargetDir src/nmon -ApplyFixes
```

---

## What to Load Into Claude Code

| Question                     | File                                                          |
|------------------------------|---------------------------------------------------------------|
| What does this module do?    | `1. src/<rel>.md`                                             |
| Where does data flow?        | `architecture/DATA_FLOW.md`                                   |
| What can fail silently here? | `architecture/INTERFACES.md` (or `interfaces/<rel>.iface.md`) |
| Known bugs?                  | `bug_reports/SUMMARY.md` → specific `bug_reports/<rel>.md`    |
| What did the fixer do?       | `bug_fixes/<rel>.iter_log.md`                                 |
| Test coverage?               | `test_gaps/GAP_REPORT.md`                                     |
