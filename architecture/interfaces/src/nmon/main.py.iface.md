# Module: `src/nmon/main.py`

## Role
Bootstraps the nmon terminal monitoring application by loading configuration, initializing monitoring components, and launching the Rich-based TUI.

## Contract: Module-level functions

### `run() -> None`
- **Requires:** Environment variables `OLLAMA_URL`, `POLL_INTERVAL_S`, `HISTORY_DURATION_S` must be set; valid numeric values for poll interval and history duration; NVML-compatible GPU system; SQLite database accessible for `RingBuffer`
- **Guarantees:** Application initializes with configured GPU and LLM monitoring; UI starts with appropriate tab visibility; `GpuMonitor` polling begins; `LlmMonitor` polling begins only if Ollama is detected
- **Raises:** `TypeError` — if `load_from_env()` or `load_persistent_settings()` return invalid types; `ValueError` — if config values are invalid (e.g., negative durations); `sqlite3.OperationalError` — if `RingBuffer` fails to initialize database; `asyncio.RunTimeError` — if `asyncio.run()` fails to execute `llm_monitor.detect()`
- **Silent failure:** `llm_monitor.detect()` returns `False` silently on any failure (network, timeout, HTTP error); `GpuMonitor` or `LlmMonitor` may silently fail to update samples if NVML or Ollama calls fail; no exception raised but UI may show stale data
- **Thread safety:** unsafe — `run()` is not thread-safe due to global state changes and potential race conditions in monitor initialization

## Module Invariants
- `GpuMonitor` and `LlmMonitor` are initialized with valid `AppConfig` and `RingBuffer` instances
- `RingBuffer` is initialized with valid `history_duration_s` and `poll_interval_s` from `AppConfig`
- `NmonApp` is initialized with a valid `AppConfig` and configured monitors
- `llm_monitor.detect()` is called exactly once during startup

## Resource Lifecycle
- `RingBuffer` acquires SQLite database connection during initialization and releases it on garbage collection or explicit shutdown
- `GpuMonitor` initializes NVML via `nvmlInit()` and shuts it down via `nvmlShutdown()` on `stop()` or app exit
- `LlmMonitor` establishes HTTP connection to Ollama during `detect()` and closes it after detection
- `NmonApp` manages UI lifecycle and handles cleanup on exit
- All resources are released on application exit via `on_unmount` or `stop()` methods
