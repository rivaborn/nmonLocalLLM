# Module: `src/nmon/views/llm_view.py`

## Role
Provides a function to render an LLM system usage dashboard view using Rich layouts and sparklines.

## Contract: Module-level functions

### `render_llm_view(ollama_snapshot, history_store, settings, prefs, now) -> Layout`
- **Requires:** 
  - `ollama_snapshot` must be an `OllamaSnapshot` instance with a valid `reachable` attribute (bool)
  - `history_store` must be a `HistoryStore` instance with valid `get_gpu_usage_series` and `get_cpu_usage_series` methods
  - `settings` must be a `Settings` instance
  - `prefs` must be a `UserPrefs` instance with a valid `active_time_range_hours` attribute (float)
  - `now` must be a float representing Unix timestamp
- **Guarantees:** 
  - Returns a `rich.layout.Layout` instance
  - If `ollama_snapshot.reachable` is False, returns layout containing single panel with "Ollama offline" message
  - If `ollama_snapshot.reachable` is True, returns layout containing sparkline panel with GPU/CPU usage data
- **Raises:** 
  - `AttributeError` -- if `history_store` lacks `get_gpu_usage_series` or `get_cpu_usage_series` methods
  - `TypeError` -- if `prefs.active_time_range_hours` is not numeric
  - `sqlite3.OperationalError` -- if `history_store.get_*_usage_series` raises database error
- **Silent failure:** 
  - None
- **Thread safety:** 
  - unsafe

## Module Invariants
None

## Resource Lifecycle
None
