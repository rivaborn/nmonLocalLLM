# Module: `src/nmon/main.py`

## Role
Main entry point for the nmon terminal system/GPU monitor that initializes components, handles signals, and runs the application loop.

## Contract: Module-level functions

### `main() -> NoReturn`
- **Requires:** Environment must contain valid configuration variables for `Settings`; `settings.prefs_path` must be a readable JSON file; `pynvml` must be importable and functional; `GpuMonitorProtocol` and `OllamaMonitorProtocol` must be properly initialized with valid parameters
- **Guarantees:** Application will run until interrupted by SIGINT or SIGTERM; all monitors will be stopped and history flushed on shutdown; system will exit with code 0 on clean shutdown or code 1 on pynvml initialization failure
- **Raises:** `SystemExit(1)` -- when `pynvml` initialization fails (detected by error message containing "pynvml")
- **Raises:** `Exception` -- any other unhandled exception during app execution
- **Silent failure:** None
- **Thread safety:** Unsafe - modifies global signal handlers and assumes single-threaded execution

## Module Invariants
- All monitors are stopped and history is flushed before application exit
- Signal handlers are registered for SIGINT and SIGTERM
- Configuration is validated before use
- User preferences are loaded from a valid JSON file

## Resource Lifecycle
- `HistoryStore` connection opened during initialization and flushed on shutdown
- `GpuMonitorProtocol` and `OllamaMonitorProtocol` handles opened during initialization and stopped on shutdown
- Signal handlers registered at startup and remain active until process termination
- File handle for preferences opened during initialization and closed automatically by context manager
