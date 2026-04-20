# Prompt Updates

Generated: 2026-04-19 12:17:06

## Critique of the Original Prompt

### What Was Unclear

**Tech stack was underspecified for HTTP calls.**
The original said "Ollama endpoint: http://..." but named no HTTP library. An LLM generating an architecture plan could choose `requests`, `aiohttp`, `urllib`, or `httpx`, leading to divergent async/sync patterns. The improved prompt mandates `httpx` with `asyncio`.

**No data model definitions.**
The original listed metrics to collect but never defined dataclasses, field names, or types. A downstream planner would invent its own names, breaking import-path consistency across modules. The improved prompt specifies `GpuSnapshot`, `OllamaSnapshot`, `AlertState`, `UserPrefs`, and `Settings` with exact field names and types.

**"Tabs" was ambiguous.**
The original said "translate tabs into keyboard-switchable views" but did not specify which keys switch views when a view's own number keys (`1`/`2`/`3`/`4`) are already used for time-range selection. This creates an unresolvable key-conflict. The improved prompt resolves this by scoping time-range keys to when the relevant view is active, and using `←`/`→` for view navigation.

**Persistence was not specified.**
The original said "retain at least 24 hours of history" but named no storage mechanism. SQLite vs. CSV vs. pickle would be left to the planner's discretion, causing inconsistent implementations. The improved prompt mandates SQLite with explicit DDL.

**"Update interval must be adjustable" had no mechanism.**
No key was specified, no minimum, no step size. The improved prompt adds `+`/`-` keys, 0.5 s step, 0.5 s minimum.

**Configuration source was unspecified.**
No mention of `.env`, environment variables, or a config library. The improved prompt mandates `pydantic-settings` + `python-dotenv` with explicit field names matching `NMON_` prefixed env vars.

**`preferences.json` was never mentioned.**
The original required persisting the threshold value across restarts but named no file or format. The improved prompt introduces `UserPrefs` serialized to `preferences.json`.

**"Every function must have unit tests" lacked any mocking strategy.**
Without specifying that `pynvml` and `httpx` must be mocked, a planner might require real hardware or a live server to run the test suite. The improved prompt specifies mock transports and in-memory SQLite.

---

### What Was Contradictory

**Number keys for both view switching and time-range switching.**
The original said views switch on `1/2/3/4` and time-range controls exist for `1h/4h/12h/24h` — the same keys. This is a direct contradiction. Resolved by making time-range keys view-scoped.

**"GPU use percentage" derivation was undefined.**
The original asked to show GPU use % from Ollama but the Ollama API does not return a direct GPU percentage; it returns layer counts. The derivation `gpu_use_pct = gpu_layers / total_layers * 100` was implied but never stated, leaving the planner to guess. The improved prompt states the derivation formula explicitly.

**"Open Questions" in deliverables contradicted "no open questions".**
The Hard Constraints section (required verbatim) prohibits open questions, but the original deliverables list included "Open Questions" as a line item. Renamed to "Design Decisions" with a mandatory structure (decision, alternatives, rationale).

---

### What Was Missing

**No `pyproject.toml` specification.** Added with mandatory fields, entry point, coverage enforcement, and `hatchling` build backend.

**No `.env.example` requirement.** Added with all `NMON_`-prefixed variables.

**No Python version requirement.** Added `>= 3.11` (required for `match`, `TypeAlias`, and modern `asyncio` patterns).

**No explicit `__m__` entry point.** Added `nmon = "nmon.main:main"` script entry.

**No `widgets/` subpackage.** The original implied reusable chart and alert bar components but gave them no home. Added `widgets/sparkline.py` and `widgets/alert_bar.py` with explicit signatures.

**No `Sparkline` widget specification.** Charts were mentioned throughout but no reusable widget was defined, meaning each view would invent its own charting code. Added `Sparkline` with a `ThresholdLine` dataclass and a fixed constructor signature.

**No error-handling table.** The original said "error-handling strategy" with no content. The improved prompt provides an explicit scenario → behavior table covering all subsystem boundaries.

**No coverage target.** The improved prompt adds 100% line coverage enforced via `--cov-fail-under=100` in `pyproject.toml`.

**No `HistoryStore` query API.** The original mentioned history but not how views would retrieve it. The improved prompt defines `gpu_series`, `ollama_series`, and `gpu_stat` with exact signatures.