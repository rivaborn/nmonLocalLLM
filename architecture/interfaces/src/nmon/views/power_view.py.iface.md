# Module: `src/nmon/views/power_view.py`

## Role
Renders the power consumption dashboard view for the nmon terminal application, displaying GPU power charts and optional Ollama process information.

## Contract: `PowerView`

### `__init__(history_store, prefs, settings, gpu_snapshots, ollama_snapshot)`
- **Requires:** `history_store` must be a valid `HistoryStore` instance; `prefs` must be a valid `UserPrefs` instance; `settings` must be a valid `Settings` instance; `gpu_snapshots` must be a `list` of `GpuSnapshot` objects; `ollama_snapshot` must be either an `OllamaSnapshot` instance or `None`
- **Establishes:** Instance attributes `history_store`, `prefs`, `settings`, `gpu_snapshots`, and `ollama_snapshot` are set; `active_time_range_hours` is initialized to `1.0`; `sparklines` is initialized as an empty `list`
- **Raises:** `TypeError` if any argument has incorrect type

### `render() -> Layout`
- **Requires:** Instance must be properly initialized with valid dependencies; `history_store` must be able to service `get_power_history` calls
- **Guarantees:** Returns a `rich.layout.Layout` object with three named sections: `header`, `content`, and `footer`
- **Raises:** `AttributeError` if `history_store` lacks `get_power_history` method; `TypeError` if `history_store.get_power_history` returns non-numeric data
- **Silent failure:** None
- **Thread safety:** unsafe

### `_render_gpu_charts() -> Layout`
- **Requires:** Instance must be properly initialized; `history_store` must be able to service `get_power_history` calls for each GPU ID in `gpu_snapshots`
- **Guarantees:** Returns a `rich.layout.Layout` containing sparkline charts for each GPU
- **Raises:** `AttributeError` if `history_store` lacks `get_power_history` method; `TypeError` if `history_store.get_power_history` returns non-numeric data
- **Silent failure:** None
- **Thread safety:** unsafe

### `_render_ollama_info() -> Panel`
- **Requires:** Instance must be properly initialized; `ollama_snapshot` must be a valid `OllamaSnapshot` instance if not `None`
- **Guarantees:** Returns a `rich.panel.Panel` containing a table with Ollama metrics
- **Raises:** `AttributeError` if `ollama_snapshot` lacks expected attributes
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
