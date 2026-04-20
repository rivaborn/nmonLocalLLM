Create a detailed architecture and implementation plan for a Rich-based Python terminal dashboard application named **nmon**.

---

## Project Identity

- **Package name:** `nmon`
- **Source layout:** `src/nmon/` (Python src-layout, PEP 517)
- **Tests:** `tests/`
- **Config files at repo root:** `pyproject.toml`, `.env.example`, `Architecture Plan.md`

---

## Purpose

`nmon` monitors all NVIDIA GPUs in the system and an optional local Ollama LLM server, presenting a live Rich terminal dashboard with keyboard-switchable views and historical charts.

---

## Environment & Runtime Targets

| Item | Value |
|---|---|
| Ollama base URL | `http://192.168.1.126:11434` (configurable via `.env`) |
| Target GPU | NVIDIA RTX 3090 (plan must also support multi-GPU) |
| Target Ollama model | Devstral Small 2 (plan must support any loaded model) |
| Python | ≥ 3.11 |
| Execution context | `aider` + local LLM; plan must be executable incrementally |

---

## Tech Stack (mandatory — do not substitute)

| Concern | Library |
|---|---|
| Terminal UI | `rich` (`rich.live.Live`, `rich.layout.Layout`, `rich.panel.Panel`, `rich.table.Table`, `rich.text.Text`) |
| GPU metrics | `nvidia-ml-py` (`pynvml`) |
| Ollama API | `httpx` (async, with `asyncio`) |
| Configuration | `python-dotenv` + `pydantic-settings` (`BaseSettings`) |
| Persistence | `sqlite3` (stdlib) for metric history; plain JSON for user preferences (threshold value, toggle states) |
| Testing | `pytest`, `pytest-asyncio`, `pytest-mock` |
| Build | `pyproject.toml` with `[build-system]` = `hatchling` |

---

## Repository Layout

```
nmon/                          ← repo root
├── pyproject.toml
├── .env.example
├── Architecture Plan.md
├── preferences.json           ← runtime-written user prefs (gitignored)
├── nmon.db                    ← runtime-written SQLite DB (gitignored)
├── src/
│   └── nmon/
│       ├── __init__.py
│       ├── main.py            ← entry point: `python -m nmon`
│       ├── config.py          ← Settings (pydantic-settings BaseSettings)
│       ├── db.py              ← SQLite schema, read/write helpers
│       ├── gpu_monitor.py     ← pynvml polling, GpuSnapshot dataclass
│       ├── ollama_monitor.py  ← httpx polling, OllamaSnapshot dataclass
│       ├── history.py         ← HistoryStore: in-memory ring buffer + DB flush
│       ├── alerts.py          ← AlertState: alert bar logic
│       ├── views/
│       │   ├── __init__.py
│       │   ├── dashboard_view.py
│       │   ├── temp_view.py
│       │   ├── power_view.py
│       │   └── llm_view.py
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── sparkline.py   ← reusable ASCII/Unicode chart widget
│       │   └── alert_bar.py   ← top alert bar renderable
│       └── app.py             ← NmonApp: orchestrates Live, Layout, event loop
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_db.py
    ├── test_gpu_monitor.py
    ├── test_ollama_monitor.py
    ├── test_history.py
    ├── test_alerts.py
    ├── test_dashboard_view.py
    ├── test_temp_view.py
    ├── test_power_view.py
    ├── test_llm_view.py
    ├── test_sparkline.py
    ├── test_alert_bar.py
    └── test_app.py
```

---

## Data Models

All dataclasses live in the module where they are first defined. No duplication.

### `GpuSnapshot` — defined in `gpu_monitor.py`

```
GpuSnapshot:
    gpu_index: int
    timestamp: float          # time.time()
    temperature_c: float
    mem_junction_temp_c: float | None   # None if GPU does not support it
    memory_used_mb: float
    memory_total_mb: float
    power_draw_w: float
    power_limit_w: float
```

### `OllamaSnapshot` — defined in `ollama_monitor.py`

```
OllamaSnapshot:
    timestamp: float
    reachable: bool
    loaded_model: str | None
    model_size_bytes: int | None
    gpu_use_pct: float | None    # 0–100; None if unavailable
    cpu_use_pct: float | None
    gpu_layers: int | None       # layers offloaded to GPU
    total_layers: int | None
```

### `AlertState` — defined in `alerts.py`

```
AlertState:
    active: bool
    message: str
    color: str          # "orange" | "red"
    expires_at: float   # time.time() + min_display_seconds
```

### `UserPrefs` — defined in `config.py`

```
UserPrefs:
    temp_threshold_c: float = 95.0
    show_threshold_line: bool = True
    show_mem_junction: bool = True
    active_view: int = 0          # 0=Dashboard,1=Temp,2=Power,3=LLM
```

`UserPrefs` is serialized to/from `preferences.json` at startup and on every change.

### `Settings` — defined in `config.py` (pydantic-settings `BaseSettings`)

```
Settings:
    ollama_base_url: str = "http://192.168.1.126:11434"
    poll_interval_s: float = 2.0      # adjustable at runtime via +/-
    history_hours: int = 24
    db_path: str = "nmon.db"
    prefs_path: str = "preferences.json"
    min_alert_display_s: float = 1.0
    offload_alert_pct: float = 5.0    # red threshold
```

Loaded from environment / `.env` file via `python-dotenv`.

---

## SQLite Schema (`db.py`)

Two tables:

```sql
CREATE TABLE gpu_metrics (
    id          INTEGER PRIMARY KEY,
    gpu_index   INTEGER NOT NULL,
    ts          REAL NOT NULL,
    temp_c      REAL,
    mem_junc_c  REAL,
    mem_used_mb REAL,
    power_w     REAL
);

CREATE TABLE ollama_metrics (
    id          INTEGER PRIMARY KEY,
    ts          REAL NOT NULL,
    gpu_use_pct REAL,
    cpu_use_pct REAL,
    gpu_layers  INTEGER,
    total_layers INTEGER
);
```

Rows older than `settings.history_hours` are pruned on startup and every hour.

---

## Functional Requirements

### 1 — GPU Monitoring (`gpu_monitor.py`)

1.1 Poll all detected NVIDIA GPUs via `pynvml` at `settings.poll_interval_s`.  
1.2 Collect per-GPU: temperature, memory used/total, power draw/limit.  
1.3 If the GPU reports `nvmlDeviceGetMemoryBusTemperature` (memory junction temp), collect it; otherwise store `None`.  
1.4 Return a `list[GpuSnapshot]` from `poll() -> list[GpuSnapshot]` (synchronous).

### 2 — Ollama Monitoring (`ollama_monitor.py`)

2.1 On startup, probe `GET /api/tags` to detect Ollama presence; set `reachable=False` on any exception.  
2.2 Each poll: `GET /api/ps` for running model info; parse `gpu_layers`, `total_layers`, model name, model size.  
2.3 Derive `gpu_use_pct = (gpu_layers / total_layers) * 100` if both are non-None, else `None`.  
2.4 Derive `cpu_use_pct = 100 - gpu_use_pct` if `gpu_use_pct` is non-None, else `None`.  
2.5 All HTTP calls must be async (`async def poll(client: httpx.AsyncClient) -> OllamaSnapshot`).  
2.6 Timeout: 3 seconds. On timeout or connection error, return `OllamaSnapshot(reachable=False, ...)`.

### 3 — History (`history.py`)

3.1 `HistoryStore` holds an in-memory `deque` of `GpuSnapshot` lists and `OllamaSnapshot` objects, capped at `history_hours × 3600 / poll_interval_s` entries.  
3.2 Provides query methods:
- `gpu_series(gpu_index: int, hours: float) -> list[GpuSnapshot]`
- `ollama_series(hours: float) -> list[OllamaSnapshot]`
- `gpu_stat(gpu_index: int, field: str, hours: float, stat: Literal["max","avg","current"]) -> float | None`

3.3 Flushes new snapshots to SQLite every 60 seconds via `flush_to_db(db: DbConnection) -> None`.  
3.4 On startup, loads last `history_hours` of rows from SQLite to pre-populate the deque.

### 4 — Alert Logic (`alerts.py`)

4.1 `compute_alert(snapshot: OllamaSnapshot, settings: Settings, now: float) -> AlertState | None`:
- If Ollama is unreachable or `gpu_use_pct` is None → return `None`.
- If `gpu_use_pct < 100` and GPU layers are being used → produce alert.
- If offload `> 0%` and `≤ settings.offload_alert_pct` → color `"orange"`.
- If offload `> settings.offload_alert_pct` → color `"red"`.
- `expires_at = now + settings.min_alert_display_s`.

4.2 The alert bar remains visible until `time.time() >= expires_at`.

### 5 — Views & Keyboard Navigation (`app.py`, `views/`)

The app renders a single `rich.layout.Layout` inside `rich.live.Live`. Views are keyboard-switchable; only one view body is rendered at a time.

| Key | View index | Label |
|---|---|---|
| `1` | 0 | Dashboard |
| `2` | 1 | Temp |
| `3` | 2 | Power |
| `4` | 3 | LLM Server (only shown if Ollama detected) |
| `←` / `→` | prev/next | wrap-around |
| `+` / `-` | — | increase/decrease poll interval by 0.5 s (min 0.5 s) |
| `↑` / `↓` | — | adjust temp threshold ±0.5 °C (Temp view active only) |
| `t` | — | toggle threshold line (Temp view active only) |
| `m` | — | toggle mem junction series (Temp view active only) |
| `Ctrl+Q` | — | quit |

#### 5.1 Dashboard View (`dashboard_view.py`)

- Per-GPU panel (one per detected GPU):
  - Current temp, 24 h max temp, 1 h avg temp
  - Current memory used / total (MB and %)
  - Current power draw / limit (W)
- Mem Junction panel (below GPU panel, hidden if no GPU supports it):
  - Current mem junction temp, 24 h max, 1 h avg
- LLM Server panel (only if Ollama detected):
  - Loaded model name, model size (human-readable bytes)
  - GPU use % (green if 100%, red otherwise)
  - CPU use % (green if GPU=100%, red otherwise)
  - GPU offload indicator: `{gpu_layers}/{total_layers} layers on GPU`

#### 5.2 Temp View (`temp_view.py`)

- Time-range selector: `[1h] [4h] [12h] [24h]` — highlight active range; switch with `1`/`2`/`3`/`4` **only when Temp view is active**.
- One chart per GPU showing core temperature series over selected range.
- Mem junction temp as a separate series in a visually distinct color (e.g., cyan vs. white).
- Toggle mem junction series with `m`.
- Configurable threshold horizontal line at `prefs.temp_threshold_c`:
  - Toggle with `t`; adjust with `↑`/`↓` (±0.5 °C).
  - Displayed as a labeled dashed line.
  - Persisted to `preferences.json` on every change.
- X-axis labels: elapsed time as `HH:MM:SS` (not "pts").
- Chart direction: left = oldest, right = newest (increases plot upward).

#### 5.3 Power View (`power_view.py`)

- Same time-range selector as Temp view (scoped to Power view when active).
- One chart per GPU showing power draw (W) over selected range.
- Horizontal guide lines at `0 W` and `power_limit_w`.
- X-axis: elapsed `HH:MM:SS`.

#### 5.4 LLM Server View (`llm_view.py`)

- Only rendered when Ollama was detected on startup.
- Combined chart: GPU use % and CPU use % as two series on the same chart.
- Horizontal guide lines at 0% and 100%.
- Same time-range selector as other views.
- X-axis: elapsed `HH:MM:SS`.
- Chart direction: left = oldest, right = newest.

#### 5.5 Alert Bar (`widgets/alert_bar.py`)

- Appears at the very top of the layout on every view.
- Orange background if `color == "orange"`; red background if `color == "red"`.
- Hidden (zero-height) when no active alert.
- Minimum display time enforced by `expires_at`.

#### 5.6 Sparkline / Chart Widget (`widgets/sparkline.py`)

- Renders a Unicode block-character chart inside a `rich.panel.Panel`.
- Constructor: `Sparkline(title: str, series: list[tuple[str, list[float]]], y_min: float, y_max: float, width: int, height: int, guide_lines: list[float] | None = None, threshold: ThresholdLine | None = None)`
- `ThresholdLine` dataclass: `value: float`, `label: str`, `visible: bool`
- Each series entry: `(label, values)` — rendered in a distinct color from a fixed palette.
- Guide lines drawn as labeled dashed rows.

---

## Error-Handling Strategy

| Scenario | Behavior |
|---|---|
| `pynvml` init fails | Log error to stderr; exit with code 1 and clear message |
| `pynvml` poll raises per-GPU | Skip that GPU for this poll cycle; log warning; do not crash |
| Ollama unreachable at startup | Set `ollama_detected = False`; hide LLM view and panel |
| Ollama unreachable mid-run | Store `OllamaSnapshot(reachable=False)`; show "Ollama offline" in LLM panel |
| SQLite write error | Log warning; continue in-memory only; retry next flush cycle |
| Keyboard read error | Log warning; continue rendering |

All exceptions must be caught at the boundary of each subsystem, never silently swallowed at the top level.

---

## Configuration (`.env.example`)

```dotenv
NMON_OLLAMA_BASE_URL=http://192.168.1.126:11434
NMON_POLL_INTERVAL_S=2.0
NMON_HISTORY_HOURS=24
NMON_DB_PATH=nmon.db
NMON_PREFS_PATH=preferences.json
NMON_MIN_ALERT_DISPLAY_S=1.0
NMON_OFFLOAD_ALERT_PCT=5.0
```

---

## Testing Strategy

- **Unit tests for every function and method** — no exceptions.
- `pynvml` calls are mocked via `pytest-mock`; tests must not require a real GPU.
- `httpx` calls are mocked via `httpx.MockTransport` or `respx`.
- `sqlite3` tests use an in-memory database (`:memory:`).
- `HistoryStore` tests inject synthetic `GpuSnapshot` / `OllamaSnapshot` lists to verify `gpu_stat` calculations and series slicing.
- View rendering tests assert that `rich` renderables are constructed without raising and contain expected text fragments (use `rich.console.Console(record=True)`).
- `AlertState` tests cover: no alert, orange threshold, red threshold, expiry logic.
- All async functions tested with `pytest-asyncio`.
- Coverage target: 100% of `src/nmon/` lines (enforced in `pyproject.toml` via `[tool.pytest.ini_options]`).

---

## `pyproject.toml` Requirements

Must include:
- `[build-system]` using `hatchling`
- `[project]` with `name = "nmon"`, `requires-python = ">=3.11"`, full `dependencies` list
- `[project.scripts]` entry: `nmon = "nmon.main:main"`
- `[tool.pytest.ini_options]` with `testpaths = ["tests"]`, `asyncio_mode = "auto"`, `--cov=src/nmon`, `--cov-fail-under=100`
- `[tool.hatch.build.targets.wheel]` with `packages = ["src/nmon"]`

---

## Deliverables

The Architecture Plan (`Architecture Plan.md`) must include all of the following:

1. **Project structure** — full annotated file tree.
2. **Module sections** — one `## Module: src/nmon/<path>.py` section per file; each section contains: purpose, all class/function signatures with types, step-by-step pseudocode, and a `Test file:` reference.
3. **Data model definitions** — canonical location for every dataclass.
4. **SQLite schema** — full DDL.
5. **Dependency graph** — ordered list of implementation steps with explicit "depends on step N" annotations.
6. **Error-handling table** — mapping scenario → behavior for every subsystem.
7. **Testing approach** — mocking strategy, fixtures, and coverage requirements per module.
8. **Design Decisions** — entries must be concrete decisions with stated rationale. Every entry must include: the decision, the alternative(s) considered, and why this choice was made. Deferred or unanswered questions are not acceptable.

---

## Hard Constraints for Architecture Plan Generation

The following are non-negotiable rules. The Architecture Plan is invalid
(and Stage 3 must not run) if any is violated:

1. **Single source of truth per symbol.** Each class, function,
   dataclass, and module-level constant is defined in EXACTLY ONE
   module section. Other sections may reference it by name but must
   not restate its signature, fields, or body. Sections for
   `__init__.py` files list re-exports only — they name the public
   symbols the package exposes and nothing else (no class bodies,
   no method signatures).

2. **No open questions on prompt-specified items.** If this Planning
   Prompt names a concrete requirement (endpoint, field, signature,
   behavior), the Architecture Plan must implement it. "Open Question"
   is not an acceptable deliverable for anything specified above. When
   a genuine ambiguity remains (an implementation detail this prompt
   did not address), record a Design Decision with rationale — not a
   question.

3. **Signature fidelity.** Every method signature in the Architecture
   Plan must match this Planning Prompt verbatim on: async/sync
   modifier, parameter names, parameter types, return type. Do not
   rename parameters or re-order them.

4. **Import-path canonicalization.** Before writing any pseudocode
   that imports a symbol, the plan must declare which module owns
   that symbol. Any cross-module reference uses the canonical import
   path and no synonyms (do not rename `Config` to `AppConfig` or
   `ConfigLoader` across sections).

5. **Each module section names its test file.** Every
   `## Module: src/<pkg>/**/<name>.py` section must end with an
   explicit `Test file: tests/test_<name>.py` reference so Stage 3's
   step planner can pair production modules with their tests.

---