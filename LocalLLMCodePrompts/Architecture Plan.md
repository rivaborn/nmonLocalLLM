# Architecture Plan


## Project Structure

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
    ├── test_app.py
    └── test_main.py
```

## Data Model

Each dataclass is declared exactly once, in the owning module section. This section is a cross-reference index only — see the linked module sections for field definitions.

| Symbol | Canonical location |
|---|---|
| `GpuSnapshot` | `## Module: src/nmon/gpu_monitor.py` |
| `GpuMonitorProtocol` | `## Module: src/nmon/gpu_monitor.py` |
| `OllamaSnapshot` | `## Module: src/nmon/ollama_monitor.py` |
| `OllamaMonitorProtocol` | `## Module: src/nmon/ollama_monitor.py` |
| `AlertState` | `## Module: src/nmon/alerts.py` |
| `UserPrefs` | `## Module: src/nmon/config.py` |
| `Settings` | `## Module: src/nmon/config.py` |
| `DbConnection` | `## Module: src/nmon/db.py` |
| `ThresholdLine` | `## Module: src/nmon/widgets/sparkline.py` |
| `Sparkline` | `## Module: src/nmon/widgets/sparkline.py` |
| SQLite DDL | `## Module: src/nmon/db.py` |

## Module: src/nmon/__init__.py

Standard Python package-marker file. Owns no classes, functions, or
module-level constants — its role is to make the containing directory
importable as a package and (optionally) shorten import paths by
re-exporting selected symbols from sibling modules.

**Imports:** no intra-project imports beyond any re-exports. If re-exports
are kept, their canonical source is the sibling module section that
owns each symbol (see other `## Module: src/...` sections).

**Re-exports:** optional, determined at implementation time. May be empty.

### Testing strategy

Test file: none — a `__init__.py` with no logic has no behaviour to
assert beyond importability, which is covered implicitly by every
sibling module's test that imports from this package.


## Module: src/nmon/main.py
Imports: NmonApp from nmon.app; Settings, UserPrefs from nmon.config; HistoryStore from nmon.history

```pseudocode
def main() -> None:
    1. Load settings from environment using Settings.model_validate_env().
    2. Initialize HistoryStore with settings.history_hours and settings.db_path.
    3. Initialize GpuMonitorProtocol with settings.poll_interval_s.
    4. Initialize OllamaMonitorProtocol with settings.ollama_base_url, settings.poll_interval_s.
    5. Load user preferences from prefs_path using UserPrefs.model_validate_json().
    6. Create NmonApp instance with:
       - gpu_monitor: GpuMonitorProtocol
       - ollama_monitor: OllamaMonitorProtocol
       - history_store: HistoryStore
       - settings: Settings
       - prefs: UserPrefs
    7. Run NmonApp's event loop via app.run().
    8. On Ctrl+C or SIGTERM, gracefully shut down all monitors and flush history to DB.
```

### Testing strategy
Test file: tests/test_main.py
- External dependencies to mock: pynvml, httpx.AsyncClient, sqlite3.Connection, rich.live.Live
- Behaviors to assert:
  - `main()` loads settings from environment and validates them
  - `main()` initializes all subsystems (monitors, history store, app)
  - `main()` starts the NmonApp event loop successfully
  - `main()` handles SIGTERM gracefully by shutting down all components
  - `main()` persists user preferences to disk on exit
  - `main()` raises SystemExit when pynvml init fails
- pytest fixtures and plugins: pytest-asyncio, monkeypatch, tmp_path
- Coverage goal: must exercise both happy path and error path (pynvml init failure)

## Module: src/nmon/config.py
Imports: UserPrefs from nmon.config; Settings from nmon.config

```pseudocode
class Settings(BaseSettings):
    ollama_base_url: str = "http://192.168.1.126:11434"
    poll_interval_s: float = 2.0
    history_hours: int = 24
    db_path: str = "nmon.db"
    prefs_path: str = "preferences.json"
    min_alert_display_s: float = 1.0
    offload_alert_pct: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="NMON_")
```

```pseudocode
class UserPrefs:
    temp_threshold_c: float = 95.0
    show_threshold_line: bool = True
    show_mem_junction: bool = True
    active_view: int = 0                  # 0=Dashboard,1=Temp,2=Power,3=LLM
    active_time_range_hours: float = 1.0  # shared across Temp, Power, LLM views
```

```pseudocode
def load_settings() -> Settings:
    1. Load environment variables using python-dotenv.
    2. Instantiate Settings with loaded values.
    3. Return Settings instance.
```

```pseudocode
def load_user_prefs() -> UserPrefs:
    1. Check if preferences.json exists.
    2. If not, create default UserPrefs instance.
    3. If yes, deserialize JSON into UserPrefs.
    4. Return UserPrefs instance.
```

```pseudocode
def save_user_prefs(prefs: UserPrefs) -> None:
    1. Serialize UserPrefs to JSON.
    2. Write JSON to prefs_path.
    3. Handle any file I/O errors by logging warning and continuing.
```

### Testing strategy
Test file: tests/test_config.py
- External dependencies to mock: `pathlib.Path.exists`, `json.load`, `json.dump`, `open`
- Behaviors to assert:
  - `load_settings()` reads `.env` and populates defaults correctly
  - `load_settings()` raises `pydantic.ValidationError` on invalid env values
  - `load_user_prefs()` returns default prefs when file doesn't exist
  - `load_user_prefs()` deserializes JSON correctly when file exists
  - `save_user_prefs()` writes valid JSON to disk
  - `save_user_prefs()` handles file write errors gracefully
- pytest fixtures and plugins: `tmp_path`, `monkeypatch`, `pytest-asyncio`
- Coverage goal: must exercise both happy path and error handling branches for file I/O operations

## Module: src/nmon/db.py
Imports: GpuSnapshot from nmon.gpu_monitor; OllamaSnapshot from nmon.ollama_monitor

### Purpose
SQLite database schema and helper functions for persisting GPU and Ollama metrics history. Provides functions to initialize the schema, prune old data, and flush in-memory snapshots to disk.

```pseudocode
DbConnection = sqlite3.Connection   # type alias; callers manage connection lifetime
```

### SQLite Schema
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

### Functions
```pseudocode
def init_db(db_path: str) -> None
1. Connect to SQLite database at db_path.
2. Create gpu_metrics table if it does not exist.
3. Create ollama_metrics table if it does not exist.
4. Return silently on success; log error and re-raise on failure.

def prune_old_data(db_path: str, history_hours: int) -> None
1. Connect to SQLite database at db_path.
2. Calculate cutoff timestamp as current time minus history_hours * 3600.
3. Delete rows from gpu_metrics where ts < cutoff.
4. Delete rows from ollama_metrics where ts < cutoff.
5. Return silently on success; log warning and continue on failure.

def flush_to_db(db_path: str, gpu_snapshots: list[GpuSnapshot], ollama_snapshot: OllamaSnapshot | None) -> None
1. Connect to SQLite database at db_path.
2. Insert each GpuSnapshot into gpu_metrics table.
3. Insert OllamaSnapshot into ollama_metrics table if not None.
4. Return silently on success; log warning and continue on failure.
```

### Testing strategy
Test file: tests/test_db.py
- External dependencies to mock: sqlite3.connect, time.time
- Behaviors to assert:
  - `init_db()` creates tables if they don't exist
  - `init_db()` does not fail if tables already exist
  - `prune_old_data()` removes rows older than history_hours
  - `prune_old_data()` preserves rows newer than history_hours
  - `flush_to_db()` inserts all GPU snapshots into gpu_metrics
  - `flush_to_db()` inserts Ollama snapshot into ollama_metrics if not None
  - `flush_to_db()` handles database connection errors gracefully
- pytest fixtures and plugins: tmp_path, monkeypatch, pytest-asyncio
- Coverage goal: must exercise both happy path and error handling branches for all functions

## Module: src/nmon/gpu_monitor.py
Imports: (no intra-project imports — this module defines root-level dataclasses)

```pseudocode
dataclass GpuSnapshot:
    gpu_index: int
    timestamp: float          # time.time()
    temperature_c: float
    mem_junction_temp_c: float | None   # None if GPU does not support it
    memory_used_mb: float
    memory_total_mb: float
    power_draw_w: float
    power_limit_w: float
```

```pseudocode
class GpuMonitorProtocol(Protocol):
    def poll(self) -> list[GpuSnapshot]: ...
```

```pseudocode
def poll() -> list[GpuSnapshot]
1. Initialize pynvml if not already initialized.
2. Get the number of GPUs in the system.
3. For each GPU index from 0 to num_gpus - 1:
   a. Attempt to get the GPU handle.
   b. If handle retrieval fails, log warning and continue to next GPU.
   c. Collect temperature using nvmlDeviceGetTemperature.
   d. Try to collect memory junction temperature using nvmlDeviceGetMemoryBusTemperature; if unavailable, set to None.
   e. Get memory info using nvmlDeviceGetMemoryInfo.
   f. Get power usage using nvmlDeviceGetPowerUsage.
   g. Get power limit using nvmlDeviceGetPowerLimit.
   h. Create a GpuSnapshot with collected data.
4. Return list of GpuSnapshot objects.
```

### Testing strategy
Test file: tests/test_gpu_monitor.py
- External dependencies to mock: pynvml (via pytest-mock)
- Behaviors or edge cases to assert:
  - `poll()` returns empty list when pynvml init fails
  - `poll()` skips a GPU and logs warning when handle retrieval fails
  - `poll()` correctly handles missing memory junction temp (returns None)
  - `poll()` returns valid GpuSnapshot data for each detected GPU
  - `poll()` raises no exceptions when GPU metrics are accessible
- pytest fixtures and plugins to use: pytest-mock, monkeypatch
- Coverage goals: must exercise both the happy path AND the error-handling branches for each GPU in the system

## Module: src/nmon/ollama_monitor.py
Imports: Settings from nmon.config; httpx from httpx

```pseudocode
dataclass OllamaSnapshot:
    timestamp: float
    reachable: bool
    loaded_model: str | None
    model_size_bytes: int | None
    gpu_use_pct: float | None    # 0–100; None if unavailable
    cpu_use_pct: float | None
    gpu_layers: int | None       # layers offloaded to GPU
    total_layers: int | None
```

```pseudocode
class OllamaMonitorProtocol(Protocol):
    async def poll(self, client: httpx.AsyncClient) -> OllamaSnapshot: ...
```

```pseudocode
class OllamaMonitor:
    1. Initialize with settings: Settings.
    2. Store settings in instance variable.
    3. Set ollama_detected: bool = False.
    4. Set ollama_client: httpx.AsyncClient = None.

def probe_ollama(client: httpx.AsyncClient, base_url: str) -> bool
    1. Attempt GET /api/tags with 3s timeout.
    2. If successful, set ollama_detected = True.
    3. If any exception (timeout, connection, HTTP error), return False.
    4. Return ollama_detected.

async def poll(client: httpx.AsyncClient) -> OllamaSnapshot
    1. If not ollama_detected, return OllamaSnapshot(reachable=False, ...).
    2. Attempt GET /api/ps with 3s timeout.
    3. If timeout or connection error, return OllamaSnapshot(reachable=False, ...).
    4. Parse response JSON for model info.
    5. Extract loaded_model, model_size_bytes, gpu_layers, total_layers.
    6. Compute gpu_use_pct = (gpu_layers / total_layers) * 100 if both non-None.
    7. Compute cpu_use_pct = 100 - gpu_use_pct if gpu_use_pct is not None.
    8. Return OllamaSnapshot(
        timestamp=time.time(),
        reachable=True,
        loaded_model=loaded_model,
        model_size_bytes=model_size_bytes,
        gpu_use_pct=gpu_use_pct,
        cpu_use_pct=cpu_use_pct,
        gpu_layers=gpu_layers,
        total_layers=total_layers
    ).
```

### Testing strategy
Test file: tests/test_ollama_monitor.py
- External dependencies to mock: httpx.AsyncClient, httpx.TimeoutException, httpx.ConnectError
- Behaviors to assert:
  - `probe_ollama()` returns False when Ollama is unreachable
  - `probe_ollama()` returns True when Ollama is reachable
  - `poll()` returns `OllamaSnapshot(reachable=False)` on timeout
  - `poll()` returns `OllamaSnapshot(reachable=False)` on connection error
  - `poll()` correctly parses model info from `/api/ps` response
  - `poll()` computes `gpu_use_pct` and `cpu_use_pct` from layer counts
  - `poll()` returns `None` for `gpu_use_pct` and `cpu_use_pct` when layer counts are missing
- pytest fixtures and plugins: pytest-asyncio, respx, monkeypatch
- Coverage goal: must exercise both the happy path AND the timeout/connection error branches

## Module: src/nmon/history.py
Imports: GpuSnapshot from nmon.gpu_monitor; OllamaSnapshot from nmon.ollama_monitor; Settings from nmon.config; DbConnection from nmon.db

```pseudocode
class HistoryStore:
    def __init__(self, settings: Settings) -> None:
        1. Initialize in-memory deque for GPU snapshots.
        2. Initialize in-memory deque for Ollama snapshots.
        3. Store settings for history duration and poll interval.
        4. Load existing data from SQLite DB into in-memory buffers.

    def add_gpu_samples(self, samples: list[GpuSnapshot]) -> None:
        1. Append samples to in-memory GPU deque.
        2. Trim deque to max size based on history_hours and poll_interval.
        3. If deque size exceeds threshold, flush to DB.

    def add_ollama_sample(self, sample: OllamaSnapshot) -> None:
        1. Append sample to in-memory Ollama deque.
        2. Trim deque to max size based on history_hours and poll_interval.
        3. If deque size exceeds threshold, flush to DB.

    def gpu_series(self, gpu_index: int, hours: float) -> list[GpuSnapshot]:
        1. Calculate start timestamp from current time and hours.
        2. Filter in-memory GPU deque for matching gpu_index and timestamp range.
        3. Return filtered list of snapshots.

    def ollama_series(self, hours: float) -> list[OllamaSnapshot]:
        1. Calculate start timestamp from current time and hours.
        2. Filter in-memory Ollama deque for timestamp range.
        3. Return filtered list of snapshots.

    def gpu_stat(self, gpu_index: int, field: str, hours: float, stat: Literal["max","avg","current"]) -> float | None:
        1. Retrieve gpu_series for given gpu_index and hours.
        2. Filter series to only include snapshots with non-None values for field.
        3. Compute max/avg/current based on stat parameter.
        4. Return computed value or None if no valid data.

    def flush_to_db(self, db: DbConnection) -> None:
        1. Begin DB transaction.
        2. Insert all GPU samples from in-memory deque into gpu_metrics table.
        3. Insert all Ollama samples from in-memory deque into ollama_metrics table.
        4. Prune old rows from both tables based on settings.history_hours.
        5. Commit transaction; log warning on failure.
```

### Testing strategy
Test file: tests/test_history.py
- External dependencies to mock: sqlite3, time.time
- Behaviors to assert:
  - `add_gpu_samples()` correctly appends and trims deque
  - `add_ollama_sample()` correctly appends and trims deque
  - `gpu_series()` returns correct time-range filtered data
  - `ollama_series()` returns correct time-range filtered data
  - `gpu_stat()` computes max/avg/current correctly
  - `flush_to_db()` writes to DB and prunes old rows
  - On DB write failure, warning is logged and operation continues
- pytest fixtures and plugins: tmp_path, monkeypatch, pytest-asyncio
- Coverage goals: must exercise both happy path and DB write error branch

## Module: src/nmon/alerts.py
Imports: OllamaSnapshot from nmon.ollama_monitor; Settings from nmon.config

```pseudocode
dataclass AlertState:
    active: bool
    message: str
    color: str          # "orange" | "red"
    expires_at: float   # time.time() + min_display_seconds
```

### compute_alert(snapshot: OllamaSnapshot, settings: Settings, now: float) -> AlertState | None
1. If `snapshot.reachable` is False or `snapshot.gpu_use_pct` is None, return None.
2. If `snapshot.gpu_use_pct` is less than 100 and GPU layers are being used:
   a. Set `message` to "GPU offload below 100%". 
   b. If `snapshot.gpu_use_pct` is greater than `settings.offload_alert_pct`, set `color` to "red".
   c. Else, set `color` to "orange".
   d. Set `expires_at` to `now + settings.min_alert_display_s`.
   e. Return `AlertState(active=True, message=message, color=color, expires_at=expires_at)`.
3. Return None.

### Testing strategy
Test file: tests/test_alerts.py
- External dependencies to mock: httpx.AsyncClient, time.time
- Behaviors to assert:
  - `compute_alert` returns None when Ollama is unreachable
  - `compute_alert` returns None when `gpu_use_pct` is None
  - `compute_alert` returns orange alert when `gpu_use_pct` is between 0 and `offload_alert_pct`
  - `compute_alert` returns red alert when `gpu_use_pct` exceeds `offload_alert_pct`
  - `compute_alert` sets `expires_at` correctly based on `min_alert_display_s`
- pytest fixtures and plugins: pytest-asyncio, monkeypatch
- Coverage goals: must exercise all branches of the conditional logic and both alert color outcomes

## Module: src/nmon/views/__init__.py

Standard Python package-marker file. Owns no classes, functions, or
module-level constants — its role is to make the containing directory
importable as a package and (optionally) shorten import paths by
re-exporting selected symbols from sibling modules.

**Imports:** no intra-project imports beyond any re-exports. If re-exports
are kept, their canonical source is the sibling module section that
owns each symbol (see other `## Module: src/...` sections).

**Re-exports:** optional, determined at implementation time. May be empty.

### Testing strategy

Test file: none — a `__init__.py` with no logic has no behaviour to
assert beyond importability, which is covered implicitly by every
sibling module's test that imports from this package.


## Module: src/nmon/views/dashboard_view.py
Imports: GpuSnapshot from nmon.gpu_monitor; OllamaSnapshot from nmon.ollama_monitor; UserPrefs, Settings from nmon.config; HistoryStore from nmon.history; AlertState from nmon.alerts; Sparkline from nmon.widgets.sparkline

### DashboardView
```pseudocode
class DashboardView:
  def __init__(
    self,
    gpu_monitor: GpuMonitorProtocol,
    history_store: HistoryStore,
    prefs: UserPrefs,
    settings: Settings,
    alert_state: AlertState | None,
  ) -> None:
    1. Store all constructor arguments as instance attributes.
    2. Initialize internal state for rendering.

  def render(self) -> RenderableType:
    1. Create a rich.layout.Layout with a top alert bar and a main content area.
    2. If alert_state is not None, render the alert bar at the top.
    3. Build the main content area:
       a. Create a Column layout for GPU panels.
       b. For each GPU in gpu_monitor, render a panel with:
          i. Current temp, 24h max temp, 1h avg temp.
          ii. Memory used/total (MB and %).
          iii. Power draw/limit (W).
       c. If any GPU supports mem junction temp, render a separate panel with:
          i. Current mem junction temp, 24h max, 1h avg.
       d. If Ollama is detected, render an LLM panel with:
          i. Loaded model name and size.
          ii. GPU use % and CPU use %.
          iii. GPU offload indicator.
    4. Return the composed layout.
```

### Testing strategy
Test file: tests/test_dashboard_view.py
- External dependencies to mock: `GpuMonitorProtocol`, `HistoryStore`, `AlertState`, `httpx.AsyncClient`.
- Behaviors or edge cases to assert:
  - `render()` produces a valid `rich.layout.Layout` with expected structure.
  - GPU panels are rendered for each detected GPU.
  - Mem junction panel is shown only when at least one GPU supports it.
  - LLM panel is shown only when Ollama is detected.
  - Alert bar is rendered at the top when `alert_state` is not None.
  - Panel content reflects current and historical metrics from `history_store`.
- pytest fixtures and plugins to use: `pytest-asyncio`, `rich.console.Console(record=True)`, `tmp_path`.
- Coverage goal: must exercise all rendering paths including when Ollama is not detected, when mem junction is not supported, and when alert is active.

## Module: src/nmon/views/temp_view.py
Imports: GpuSnapshot from nmon.gpu_monitor; OllamaSnapshot from nmon.ollama_monitor; Settings, UserPrefs from nmon.config; HistoryStore from nmon.history; Sparkline from nmon.widgets.sparkline

### Purpose
The `temp_view.py` module renders the temperature monitoring view in the nmon terminal dashboard. It displays GPU core temperature and memory junction temperature over time, with configurable time ranges, threshold lines, and toggle controls for visualizing memory junction data.

### `def render_temp_view(
    gpu_samples: list[GpuSnapshot],
    ollama_sample: OllamaSnapshot | None,
    prefs: UserPrefs,
    history_store: HistoryStore,
    settings: Settings,
    now: float
) -> rich.layout.Layout`
1. Initialize a `rich.layout.Layout` with a single column.
2. Create a time range selector panel with buttons for 1h, 4h, 12h, 24h.
3. Determine the currently selected time range from `prefs.active_time_range_hours`.
4. Query `history_store.gpu_series(gpu_index, hours)` for each GPU to get temperature data.
5. Render a `Sparkline` chart for each GPU's core temperature.
6. If `prefs.show_mem_junction` is True, render a second series for memory junction temperature.
7. Add a horizontal threshold line at `prefs.temp_threshold_c` if enabled.
8. Return the constructed layout.

### `def update_temp_prefs(
    prefs: UserPrefs,
    key: str,
    settings: Settings
) -> UserPrefs`
1. If `key == "up"` or `key == "down"`, adjust `prefs.temp_threshold_c` by ±0.5°C.
2. If `key == "t"`, toggle `prefs.show_threshold_line`.
3. If `key == "m"`, toggle `prefs.show_mem_junction`.
4. Return updated `prefs`.

### Testing strategy
Test file: tests/test_temp_view.py
- External dependencies to mock: `history_store.gpu_series`, `rich.console.Console`, `time.time`.
- Assert that `render_temp_view` returns a layout with correct number of panels.
- Assert that time range buttons are rendered with correct labels and active state.
- Assert that threshold line is rendered when `show_threshold_line` is True.
- Assert that memory junction series is rendered when `show_mem_junction` is True.
- Assert that `update_temp_prefs` correctly modifies threshold and toggle flags.
- Assert that `render_temp_view` handles empty or missing GPU data gracefully.
- pytest fixtures: `tmp_path`, `monkeypatch`, `pytest-asyncio`.
- Coverage goal: 100% of lines in `temp_view.py` must be exercised.

## Module: src/nmon/views/power_view.py
Imports: GpuSnapshot from nmon.gpu_monitor; OllamaSnapshot from nmon.ollama_monitor; HistoryStore from nmon.history; UserPrefs, Settings from nmon.config; Sparkline from nmon.widgets.sparkline

### Purpose
The `power_view.py` module renders the power consumption dashboard view for the `nmon` terminal application. It displays power draw charts for each GPU over a selected time range, with guide lines at 0W and the power limit. The view is part of the keyboard-switchable dashboard and updates in real-time with polling data.

### Class: PowerView
```pseudocode
class PowerView:
    def __init__(
        self,
        history_store: HistoryStore,
        prefs: UserPrefs,
        settings: Settings,
        gpu_snapshots: list[GpuSnapshot],
        ollama_snapshot: OllamaSnapshot | None,
    ) -> None:
        1. Store the provided arguments as instance attributes.
        2. Initialize the time range selector to 1 hour.
        3. Set up a list of sparkline renderables for each GPU.

    def render(self) -> rich.layout.Layout:
        1. Create a layout with a time range selector panel at the top.
        2. For each GPU in gpu_snapshots:
            a. Extract power draw series from history_store for the selected time range.
            b. Determine the maximum power draw in the series for y-axis scaling.
            c. Create a Sparkline with title "GPU {gpu_index} Power Draw", series [("", power_draw_series)], y_min=0, y_max=max_power_draw, guide_lines=[0, power_limit_w].
            d. Add the Sparkline to the layout.
        3. Return the layout containing the time selector and GPU power charts.
```

### Testing strategy
Test file: tests/test_power_view.py
- External dependencies to mock: `HistoryStore`, `GpuSnapshot`, `OllamaSnapshot`, `UserPrefs`, `Settings`
- Behaviors or edge cases to assert:
  - `render()` produces a layout with correct number of GPU panels
  - Time range selector updates correctly when user presses 1/2/3/4
  - Sparkline charts show power draw series with correct y-axis scaling
  - Guide lines at 0W and power limit are displayed
  - Empty or invalid history data does not crash rendering
  - Layout structure matches expected Rich layout hierarchy
- pytest fixtures and plugins to use: `pytest-asyncio`, `rich.console.Console`
- Coverage goal: must exercise both the happy path AND the case where history data is missing or malformed

## Module: src/nmon/views/llm_view.py
Imports: OllamaSnapshot from nmon.ollama_monitor; HistoryStore from nmon.history; Settings, UserPrefs from nmon.config; AlertState from nmon.alerts; Sparkline from nmon.widgets.sparkline

### Purpose
The LLM view renders a combined chart of GPU and CPU usage percentages over time, showing how an Ollama server utilizes system resources. It is only displayed when Ollama is detected during startup.

### Function signatures
```pseudocode
def render_llm_view(
    ollama_snapshot: OllamaSnapshot,
    history_store: HistoryStore,
    settings: Settings,
    prefs: UserPrefs,
    now: float
) -> rich.layout.Layout
```

### Pseudocode logic
1. If `ollama_snapshot.reachable` is False, return a layout with a single panel displaying "Ollama offline".
2. Otherwise:
   - Fetch GPU usage series from `history_store` for the last `prefs.active_time_range_hours` hours.
   - Fetch CPU usage series from `history_store` for the last `prefs.active_time_range_hours` hours.
   - Create a `Sparkline` with:
     - Title: "LLM Server Usage"
     - Series: `[("GPU Use %", gpu_series), ("CPU Use %", cpu_series)]`
     - Y-axis range: 0 to 100
     - Guide lines: [0, 100]
     - Width: 80
     - Height: 10
   - Create a panel containing the sparkline.
   - Return a layout with one panel (the sparkline panel).

### Testing strategy
Test file: tests/test_llm_view.py
- Mock `HistoryStore` to return synthetic GPU and CPU usage series.
- Mock `OllamaSnapshot` with `reachable=True` and `reachable=False`.
- External dependencies to mock: `HistoryStore`, `OllamaSnapshot`.
- Behaviors to assert:
  - When `ollama_snapshot.reachable` is False, layout contains "Ollama offline" text.
  - When `ollama_snapshot.reachable` is True, layout contains a sparkline with two series.
  - Series data is correctly fetched from history store for the specified time range.
  - Guide lines at 0% and 100% are rendered.
  - Chart title is "LLM Server Usage".
- pytest fixtures and plugins: pytest-asyncio, monkeypatch.
- Coverage goal: must exercise both the reachable and unreachable branches.

## Module: src/nmon/widgets/__init__.py

Standard Python package-marker file. Owns no classes, functions, or
module-level constants — its role is to make the containing directory
importable as a package and (optionally) shorten import paths by
re-exporting selected symbols from sibling modules.

**Imports:** no intra-project imports beyond any re-exports. If re-exports
are kept, their canonical source is the sibling module section that
owns each symbol (see other `## Module: src/...` sections).

**Re-exports:** optional, determined at implementation time. May be empty.

### Testing strategy

Test file: none — a `__init__.py` with no logic has no behaviour to
assert beyond importability, which is covered implicitly by every
sibling module's test that imports from this package.


## Module: src/nmon/widgets/sparkline.py
Imports: (no intra-project imports required — Sparkline accepts pre-computed series data as arguments)

```pseudocode
class ThresholdLine:
    1. value: float
    2. label: str
    3. visible: bool

class Sparkline:
    1. title: str
    2. series: list[tuple[str, list[float]]]
    3. y_min: float
    4. y_max: float
    5. width: int
    6. height: int
    7. guide_lines: list[float] | None = None
    8. threshold: ThresholdLine | None = None

def __init__(self, title: str, series: list[tuple[str, list[float]]], y_min: float, y_max: float, width: int, height: int, guide_lines: list[float] | None = None, threshold: ThresholdLine | None = None) -> None:
    1. Initialize self.title = title
    2. Initialize self.series = series
    3. Initialize self.y_min = y_min
    4. Initialize self.y_max = y_max
    5. Initialize self.width = width
    6. Initialize self.height = height
    7. Initialize self.guide_lines = guide_lines
    8. Initialize self.threshold = threshold

def render(self) -> rich.panel.Panel:
    1. Create a rich.text.Text object for chart content
    2. For each row in height:
        a. Compute row value based on y_min, y_max, and row index
        b. For each column in width:
            i. Compute column value based on x position
            ii. Determine if this cell should be filled based on series data
            iii. Append appropriate Unicode block character to text
        c. Append newline to text
    3. If threshold is not None and threshold.visible:
        a. Compute row position for threshold line
        b. Draw threshold line with label
    4. If guide_lines is not None:
        a. For each guide_line in guide_lines:
            i. Compute row position for guide line
            ii. Draw guide line with label
    5. Create rich.panel.Panel with title=self.title and renderable=text
    6. Return panel
```

### Testing strategy
Test file: tests/test_sparkline.py
- External dependencies to mock: none
- Behaviors or edge cases to assert:
  - `render()` produces a valid Rich Panel with correct title
  - Series data is correctly mapped to Unicode block characters
  - Guide lines are drawn at correct vertical positions
  - Threshold line is rendered when visible
  - Empty series results in blank chart
  - Single-value series renders correctly
  - Multi-series chart shows distinct colors for each series
- pytest fixtures and plugins to use: pytest-asyncio, rich
- Must exercise both the happy path AND the edge cases with guide lines and threshold line rendering

## Module: src/nmon/widgets/alert_bar.py
Imports: AlertState from nmon.alerts; Settings from nmon.config

```pseudocode
class AlertBar:
    def __init__(self, alert_state: AlertState | None, settings: Settings):
        1. Store alert_state and settings as instance attributes.
        2. Initialize internal state tracking whether alert is currently visible.

    def __rich__(self) -> Panel:
        1. If alert_state is None or current time >= expires_at:
           a. Return a zero-height Panel (hidden).
           b. Mark internal visibility state as False.
        2. Else:
           a. Create a Panel with:
              i. Title "Alert"
              ii. Background color based on alert_state.color ("orange" or "red")
              iii. Content text from alert_state.message
           b. Mark internal visibility state as True.
        3. Return the Panel.

    def update(self, new_alert_state: AlertState | None, now: float) -> None:
        1. Update internal alert_state to new_alert_state.
        2. If new_alert_state is not None:
           a. Set internal visibility state to True.
        3. Else:
           a. Set internal visibility state to False.
```

### Testing strategy
Test file: tests/test_alert_bar.py
- External dependencies to mock: none
- Behaviors or edge cases to assert:
  - `__rich__()` returns a zero-height Panel when alert_state is None
  - `__rich__()` returns a Panel with red background when alert_state.color is "red"
  - `__rich__()` returns a Panel with orange background when alert_state.color is "orange"
  - `__rich__()` returns a zero-height Panel when current time >= alert_state.expires_at
  - `update()` correctly updates internal alert_state and visibility state
- pytest fixtures and plugins to use: pytest-asyncio, rich console recording
- Coverage goals: must exercise both the visible and hidden alert states

## Module: src/nmon/app.py
Imports: Settings, UserPrefs from nmon.config; HistoryStore from nmon.history; AlertState from nmon.alerts; DashboardView from nmon.views.dashboard_view; TempView from nmon.views.temp_view; PowerView from nmon.views.power_view; LlmView from nmon.views.llm_view; AlertBar from nmon.widgets.alert_bar; Sparkline from nmon.widgets.sparkline

```pseudocode
class NmonApp:
    def __init__(
        self,
        settings: Settings,
        gpu_monitor: GpuMonitorProtocol,
        ollama_monitor: OllamaMonitorProtocol,
        history_store: HistoryStore,
        alert_state: AlertState,
        prefs: UserPrefs,
    ) -> None:
        1. Initialize self.settings with settings.
        2. Initialize self.gpu_monitor with gpu_monitor.
        3. Initialize self.ollama_monitor with ollama_monitor.
        4. Initialize self.history_store with history_store.
        5. Initialize self.alert_state with alert_state.
        6. Initialize self.prefs with prefs.
        7. Initialize self.live with a new Live object.
        8. Initialize self.layout with a new Layout object.
        9. Initialize self.current_view_index to prefs.active_view.
        10. Initialize self.ollama_detected to False.
        11. Initialize self.views to a list of view instances.
        12. Initialize self.alert_bar to an AlertBar instance.
        13. Initialize self._running to False.

    async def start(self) -> None:
        1. Call self._setup_layout() to build the layout.
        2. Call self._probe_ollama() to detect Ollama presence.
        3. Call self.history_store.load_from_db() to pre-populate history.
        4. Start the main event loop in a background task.
        5. Start the live rendering loop.
        6. Set self._running to True.

    async def stop(self) -> None:
        1. Set self._running to False.
        2. Call self.history_store.flush_to_db() to persist history.
        3. Stop the live rendering loop.
        4. Cancel the background event loop task.

    async def _setup_layout(self) -> None:
        1. Create a new Layout object.
        2. Add a top panel for the alert bar.
        3. Add a main panel for the current view.
        4. Assign the layout to self.layout.

    async def _probe_ollama(self) -> None:
        1. Attempt to call self.ollama_monitor.probe().
        2. If successful, set self.ollama_detected to True.
        3. If failed, set self.ollama_detected to False and log warning.

    async def _poll_all(self) -> tuple[list[GpuSnapshot], OllamaSnapshot]:
        1. Poll GPU metrics asynchronously.
        2. Poll Ollama metrics asynchronously.
        3. Return a tuple of (gpu_snapshots, ollama_snapshot).

    async def _handle_event(self, event: str) -> None:
        1. If event is "q" or "Ctrl+Q", call self.stop().
        2. If event is "1", "2", "3", "4", switch to corresponding view.
        3. If event is "←" or "→", switch to previous/next view.
        4. If event is "+", increase poll interval by 0.5s (min 0.5s).
        5. If event is "-", decrease poll interval by 0.5s (min 0.5s).
        6. If event is "↑" or "↓", adjust temp threshold (Temp view only).
        7. If event is "t", toggle threshold line (Temp view only).
        8. If event is "m", toggle mem junction series (Temp view only).

    async def _render_current_view(self) -> None:
        1. Get the current view from self.views[self.current_view_index].
        2. Render the view with the current data.
        3. Update the layout with the rendered view.

    async def _event_loop(self) -> None:
        1. While self._running is True:
            2. Poll all metrics.
            3. Update history store with new snapshots.
            4. Compute alert state.
            5. Render current view.
            6. Wait for next poll interval.
```

### Testing strategy
Test file: tests/test_app.py
- External dependencies to mock: pynvml, httpx, sqlite3, rich.live.Live, keyboard input
- Behaviors or edge cases to assert:
  - NmonApp initializes with correct settings and monitors
  - App starts and stops cleanly with proper resource cleanup
  - Ollama detection works correctly and hides LLM view when not detected
  - View switching works with keyboard input
  - Poll interval adjustment updates settings and reflects in next poll
  - Temp threshold adjustment persists and affects rendering
  - Alert bar displays correctly based on alert state
  - History store flushes to DB on stop
  - Keyboard input handling ignores invalid keys gracefully
- pytest fixtures and plugins to use: pytest-asyncio, monkeypatch, tmp_path, capsys
- Must exercise both the happy path AND the Ollama-unreachable branch

## File: pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "nmon"
version = "0.1.0"
description = "Terminal dashboard for monitoring NVIDIA GPUs and Ollama LLM server"
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "rich>=13.7.0",
    "nvidia-ml-py>=12.535.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.0.0",
]

[project.scripts]
nmon = "nmon.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "--cov=src/nmon",
    "--cov-fail-under=100",
    "--cov-report=term-missing",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.hatch.build.targets.wheel]
packages = ["src/nmon"]
```

## File: .env.example

Environment variables for the `nmon` application, used to configure runtime behavior via `python-dotenv` and `pydantic-settings`.

```
NMON_OLLAMA_BASE_URL=http://192.168.1.126:11434
NMON_POLL_INTERVAL_S=2.0
NMON_HISTORY_HOURS=24
NMON_DB_PATH=nmon.db
NMON_PREFS_PATH=preferences.json
NMON_MIN_ALERT_DISPLAY_S=1.0
NMON_OFFLOAD_ALERT_PCT=5.0
```

## Data Pipeline

The data pipeline in `nmon` defines how information flows between subsystems, from raw hardware and API polling to in-memory storage, database persistence, and final rendering in the terminal UI. This section outlines the data flow architecture, including the interfaces between components, the mechanisms for data transfer, and how data is consumed by views and alerts.

### Data Flow Overview

1. **Polling Layer**: The `gpu_monitor.py` and `ollama_monitor.py` modules poll hardware and external APIs, producing `GpuSnapshot` and `OllamaSnapshot` objects respectively.
2. **History Store**: The `history.py` module receives snapshots from polling and stores them in an in-memory ring buffer. Periodically, it flushes data to SQLite for persistence.
3. **Alert Logic**: The `alerts.py` module consumes `OllamaSnapshot` data to compute alert states, which are then rendered by the `alert_bar.py` widget.
4. **View Rendering**: Each view (`dashboard_view.py`, `temp_view.py`, etc.) accesses historical data from `HistoryStore` to render charts and panels.
5. **User Preferences**: The `config.py` module loads and saves `UserPrefs` to/from `preferences.json`, which influence rendering behavior in views.

### Data Transfer Interfaces

#### `HistoryStore` Interface

`HistoryStore` is the central data hub — see `## Module: src/nmon/history.py` for the canonical class definition, method signatures, and pseudocode.

#### `AlertState` Computation

`compute_alert()` is the sole entry point for alert logic — see `## Module: src/nmon/alerts.py` for the canonical function signature and pseudocode.

### Data Flow Between Modules

1. **Polling → History Store**:
   - `gpu_monitor.poll()` returns `list[GpuSnapshot]`.
   - `history.add_gpu_samples()` receives this list and appends to in-memory buffer.
   - `ollama_monitor.poll()` returns `OllamaSnapshot`.
   - `history.add_ollama_sample()` receives this and appends to in-memory buffer.

2. **History Store → Views**:
   - Each view module calls `history.gpu_series()` or `history.ollama_series()` to get data for rendering.
   - `history.gpu_stat()` is used for dashboard panel values.

3. **Alert Logic → Alert Bar**:
   - `alerts.compute_alert()` is called with latest `OllamaSnapshot`.
   - Result is passed to `alert_bar.py` for rendering.

4. **User Preferences → Views**:
   - `config.UserPrefs` is loaded at startup and passed to view modules.
   - View modules use `prefs.temp_threshold_c`, `show_threshold_line`, etc., to configure rendering.

### Testing strategy

Test file: tests/test_history.py

- External dependencies to mock:
  - `sqlite3` (use in-memory DB)
  - `pynvml` (via `pytest-mock`)
  - `httpx.AsyncClient` (via `httpx.MockTransport`)
- 5 behaviors or edge cases to assert:
  1. `add_gpu_samples()` correctly appends and trims samples.
  2. `gpu_series()` filters samples by time and GPU index.
  3. `gpu_stat()` computes max, average, and current values correctly.
  4. `flush_to_db()` writes to SQLite and handles errors gracefully.
  5. `add_ollama_sample()` correctly appends and trims samples.
- pytest fixtures and plugins to use:
  - `tmp_path` for DB file
  - `pytest-asyncio`
  - `pytest-mock`
- Coverage goals:
  - Must exercise both happy path and error handling in `flush_to_db()`.




## Dependency Graph

Ordered implementation steps. Each step may begin only after all listed dependencies are complete.

| Step | Module / file | Depends on |
|---|---|---|
| 1 | `src/nmon/config.py` — `Settings`, `UserPrefs`, `load_settings`, `load_user_prefs`, `save_user_prefs` | — |
| 2 | `src/nmon/gpu_monitor.py` — `GpuSnapshot`, `GpuMonitorProtocol`, `poll` | step 1 |
| 3 | `src/nmon/ollama_monitor.py` — `OllamaSnapshot`, `OllamaMonitorProtocol`, `OllamaMonitor`, `probe_ollama`, `poll` | step 1 |
| 4 | `src/nmon/db.py` — `DbConnection`, DDL, `init_db`, `prune_old_data`, `flush_to_db` | steps 2, 3 |
| 5 | `src/nmon/alerts.py` — `AlertState`, `compute_alert` | steps 1, 3 |
| 6 | `src/nmon/widgets/sparkline.py` — `ThresholdLine`, `Sparkline` | — |
| 7 | `src/nmon/widgets/alert_bar.py` — `AlertBar` | step 5 |
| 8 | `src/nmon/history.py` — `HistoryStore` | steps 1, 2, 3, 4 |
| 9 | `src/nmon/views/dashboard_view.py` — `DashboardView` | steps 1, 2, 3, 5, 6, 7, 8 |
| 10 | `src/nmon/views/temp_view.py` — `render_temp_view`, `update_temp_prefs` | steps 1, 2, 6, 8 |
| 11 | `src/nmon/views/power_view.py` — `PowerView` | steps 1, 2, 6, 8 |
| 12 | `src/nmon/views/llm_view.py` — `render_llm_view` | steps 1, 3, 6, 8 |
| 13 | `src/nmon/app.py` — `NmonApp` | steps 1–12 |
| 14 | `src/nmon/main.py` — `main` | step 13 |
| 15 | `pyproject.toml`, `.env.example` | step 1 (for dependency list) |
| 16 | `tests/` — all test modules | steps 1–14 (each test file depends on its production module) |

---

## Design Decisions

1. **Configuration: `pydantic-settings` `BaseSettings` with `NMON_` prefix.**
   Alternatives: plain `os.environ` reads; `configparser`. Chosen because pydantic-settings provides typed fields, `.env` file support, and validation in one class, matching the mandatory tech stack. `os.environ` lacks typing and validation; `configparser` lacks `.env` support.

2. **User preferences: plain JSON file (`preferences.json`) at repo root.**
   Alternatives: SQLite row; in-memory only. Chosen because preferences are human-editable key/value pairs that survive process restarts without schema migration. SQLite would require a table for a handful of scalar fields; in-memory loses state on exit.

3. **History persistence: in-memory `deque` + SQLite flush every 60 s.**
   Alternatives: write-through on every poll; no persistence. Chosen because write-through at 2 s poll intervals would thrash SQLite; no persistence loses history on crash. 60 s flush balances performance with durability as specified in §3.3.

4. **Ollama API: `httpx.AsyncClient` with 3-second timeout per call.**
   Alternatives: `requests` (sync); `aiohttp`. Chosen because the mandatory tech stack requires `httpx` with `asyncio`; sync `requests` would block the render loop; `aiohttp` is not in the specified stack.

5. **`gpu_use_pct` derivation: `(gpu_layers / total_layers) * 100`.**
   Alternatives: use a direct NVML GPU utilization metric. Chosen because Ollama's `/api/ps` response exposes layer counts, not GPU utilization %; the formula is specified verbatim in §2.3. Direct NVML metrics would require pynvml calls outside gpu_monitor.py.

6. **Alert color thresholds: `≤ offload_alert_pct` → orange; `> offload_alert_pct` → red.**
   Alternatives: single threshold; three levels. Chosen to match §4.1 exactly: two discrete levels (orange = partial but low offload, red = exceeds threshold) with `offload_alert_pct` as the configurable boundary.

7. **`flush_to_db` parameter type: `DbConnection` (type alias for `sqlite3.Connection`).**
   Alternatives: pass `db_path: str` and open inside; use SQLAlchemy. Chosen because callers manage connection lifetime (allowing transaction batching), `DbConnection` alias makes the Planning Prompt signature match concrete, and SQLAlchemy is not in the mandatory stack.

8. **View abstraction: class-based (`DashboardView`, `PowerView`) vs. function-based (`TempView` via `render_temp_view`/`update_temp_prefs`, `LlmView` via `render_llm_view`) stored in a list indexed by `active_view`.**
   Alternatives: all class-based; all function-based; plugin registry. `DashboardView` and `PowerView` are class-based because they hold per-instance mutable state (time-range selection, sparkline instances). `TempView` and `LlmView` are function-based because their mutable state (`temp_threshold_c`, `show_threshold_line`, `show_mem_junction`, `active_time_range_hours`) is already owned by `UserPrefs` and persisted to disk — no additional instance state is needed, so a stateless function is the simpler choice. `NmonApp` wraps both styles behind a uniform render protocol so the dispatch loop treats them identically.

9. **`active_time_range_hours` added to `UserPrefs` (single shared time-range field for Temp, Power, and LLM views).**
   Alternatives: per-view time-range field in `UserPrefs`; time-range stored in class-based view state only. A single shared field minimises `UserPrefs` surface area. Per-view fields would allow independent ranges but the prompt specifies no such requirement. Storing it only in class state would lose the selection on restart; persisting it in `UserPrefs` is consistent with all other user-adjustable settings.




## Error Handling

This section defines the error-handling strategy for each subsystem of the `nmon` application, mapping specific failure scenarios to appropriate behaviors. The goal is to ensure robustness and graceful degradation while maintaining clear logging and user feedback.

### Subsystem: GPU Monitoring (`gpu_monitor.py`)

#### Error Scenarios and Behaviors

1. **`pynvml` initialization fails**
   - Log error to stderr with descriptive message.
   - Exit application with code 1.

2. **Per-GPU `pynvml` poll raises exception**
   - Skip that specific GPU for this poll cycle.
   - Log warning with GPU index and exception details.
   - Continue polling remaining GPUs.

3. **Memory junction temperature not supported**
   - Return `None` for `mem_junction_temp_c` field in `GpuSnapshot`.

See pseudocode in `## Module: src/nmon/gpu_monitor.py`.

### Subsystem: Ollama Monitoring (`ollama_monitor.py`)

#### Error Scenarios and Behaviors

1. **Ollama unreachable at startup**
   - Set `ollama_detected = False`.
   - Hide LLM view and panel from UI.

2. **Ollama unreachable mid-run**
   - Store `OllamaSnapshot(reachable=False)` in history.
   - Display "Ollama offline" in LLM panel.

3. **HTTP timeout or connection error**
   - Return `OllamaSnapshot(reachable=False, ...)` with default values.
   - Log warning with error type and URL.

4. **Invalid JSON response**
   - Log warning with response content.
   - Return `OllamaSnapshot(reachable=True, ...)` with `None` for derived fields.

See pseudocode in `## Module: src/nmon/ollama_monitor.py`.

### Subsystem: History Store (`history.py`)

#### Error Scenarios and Behaviors

1. **SQLite write error**
   - Log warning with error message.
   - Continue in-memory operation.
   - Retry flush on next scheduled cycle.

2. **Database connection failure**
   - Log warning.
   - Proceed with in-memory storage only.
   - Retry connection on next flush attempt.

3. **Invalid data during flush**
   - Log warning with data details.
   - Skip invalid row and continue processing.

See pseudocode in `## Module: src/nmon/history.py`.

### Subsystem: Alert Logic (`alerts.py`)

#### Error Scenarios and Behaviors

1. **Invalid `OllamaSnapshot` data**
   - Return `None` if `gpu_use_pct` is `None`.
   - Log warning if unexpected data types are encountered.

2. **Time calculation errors**
   - Use default values if `expires_at` cannot be computed.
   - Log warning with error details.

See pseudocode in `## Module: src/nmon/alerts.py`.

### Subsystem: Keyboard Input Handling (`app.py`)

#### Error Scenarios and Behaviors

1. **Keyboard read error**
   - Log warning with error details.
   - Continue rendering and polling.

2. **Invalid key press**
   - Ignore invalid key presses.
   - Log warning if debug mode is enabled.

See pseudocode in `## Module: src/nmon/app.py`.
