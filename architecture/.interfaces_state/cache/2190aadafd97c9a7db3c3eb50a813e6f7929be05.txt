# Module: `src/nmon/views/temp_view.py`

## Role
Provides functions to render temperature monitoring views and update related user preferences in the nmon terminal dashboard.

## Contract: Module-level functions

### `render_temp_view(gpu_samples, ollama_sample, prefs, history_store, settings, now) -> Layout`
- **Requires:** `gpu_samples` must be a non-empty list of `GpuSnapshot` objects; `prefs` must be a valid `UserPrefs` instance with `active_time_range_hours` set; `history_store` must be a valid `HistoryStore` instance; `settings` must be a valid `Settings` instance; `now` must be a numeric timestamp.
- **Guarantees:** Returns a `rich.layout.Layout` object with a time range selector and panels for each GPU's temperature data.
- **Raises:** `AttributeError` — if `history_store` does not have `gpu_series` or `gpu_mem_series` methods; `TypeError` — if `prefs.active_time_range_hours` is not numeric.
- **Silent failure:** None
- **Thread safety:** unsafe

### `update_temp_prefs(prefs, key, settings) -> UserPrefs`
- **Requires:** `prefs` must be a valid `UserPrefs` instance; `key` must be a string representing a keyboard input; `settings` must be a valid `Settings` instance.
- **Guarantees:** Returns an updated `UserPrefs` instance with modified temperature-related preferences.
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
