# Module: `src/nmon/__init__.py`

## Role
Exports public interfaces for the nmon system, including configuration, GPU monitoring, history storage, views, and UI widgets.

## Contract: Module-level functions

### `__init__`
- **Requires:** All imported modules (`config`, `gpu_monitor`, `ollama_monitor`, `alerts`, `history`, `views`, `widgets`) must be correctly installed and importable
- **Establishes:** All public classes and functions from submodules are available at module level
- **Raises:** `ImportError` — if any submodule fails to import

## Module Invariants
None

## Resource Lifecycle
None
