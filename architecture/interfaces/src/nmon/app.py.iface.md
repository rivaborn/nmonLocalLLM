# Module: `src/nmon/app.py`

## Role
Orchestrates the terminal dashboard application for monitoring GPU and LLM metrics with a Rich-based TUI.

## Contract: `NmonApp`

### `__init__(params) -> None`
- **Requires:** All parameters must be non-None instances of their respective types: `Settings`, `GpuMonitorProtocol`, `OllamaMonitorProtocol`, `HistoryStore`, `AlertState`, `UserPrefs`
- **Establishes:** Initializes internal state including layout, live rendering context, and view management; sets `self._running = False`
- **Raises:** `TypeError` if any parameter is None or incorrect type

### `start() -> None`
- **Requires:** `self` must be initialized; all dependencies must be valid and ready
- **Guarantees:** Application enters running state; layout is set up; Ollama probing begins; live rendering starts
- **Raises:** `RuntimeError` if layout setup fails or live rendering fails to start
- **Silent failure:** None
- **Thread safety:** Unsafe - must be called from main thread

### `stop() -> None`
- **Requires:** Application must be running (`self._running = True`)
- **Guarantees:** Application stops; history flushed to database; live rendering stopped; background task canceled
- **Raises:** `sqlite3.OperationalError` if database connection fails during flush
- **Silent failure:** None
- **Thread safety:** Unsafe - must be called from main thread

### `_setup_layout() -> None`
- **Requires:** `self` must be initialized
- **Guarantees:** Layout is initialized with alert bar and main content areas
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `_probe_ollama() -> None`
- **Requires:** `self.ollama_monitor` must be a valid `OllamaMonitorProtocol` instance
- **Guarantees:** Sets `self.ollama_detected` to True/False based on Ollama availability
- **Raises:** None
- **Silent failure:** Swallows all exceptions during Ollama probing, defaults to `False`
- **Thread safety:** Unsafe

### `_poll_all() -> Tuple[List[GpuSnapshot], OllamaSnapshot]`
- **Requires:** `self.gpu_monitor` and `self.ollama_monitor` must be valid
- **Guarantees:** Returns tuple of GPU snapshots and Ollama snapshot; GPU polling is synchronous, Ollama polling is async
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `_handle_event(event: str) -> None`
- **Requires:** `event` must be a string representing a keyboard input
- **Guarantees:** Updates application state based on event; handles navigation, settings, and view switching
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `_render_current_view() -> None`
- **Requires:** `self.history_store` must contain valid samples; `self.current_view_index` must be valid (0-3)
- **Guarantees:** Updates layout with current view content
- **Raises:** None
- **Silent failure:** None
-
