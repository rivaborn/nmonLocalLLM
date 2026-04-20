# Module: `src/nmon/views/__init__.py`

## Role
Exports public view components and rendering functions for the nmon terminal user interface.

## Contract: Module-level functions

### `render_temp_view(config, gpu_data, temp_prefs)`
- **Requires:** `config` must be a dict with valid nmon configuration keys; `gpu_data` must be a list[GPUSample] with at least one sample; `temp_prefs` must be a dict with valid temperature preference keys
- **Guarantees:** Returns a Rich-compatible renderable object representing the temperature view
- **Raises:** `KeyError` -- if `config` or `temp_prefs` lacks required keys
- **Silent failure:** None
- **Thread safety:** unsafe

### `update_temp_prefs(config, temp_prefs)`
- **Requires:** `config` must be a dict with valid nmon configuration keys; `temp_prefs` must be a dict with valid temperature preference keys
- **Guarantees:** Returns updated `temp_prefs` dict with validated values
- **Raises:** `TypeError` -- if `config` or `temp_prefs` contains invalid types
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
