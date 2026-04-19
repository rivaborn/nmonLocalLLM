# Module: `src/nmon/__init__.py`

## Role
Package marker file that makes the directory importable and re-exports key monitoring components for convenient access.

## Contract: Module-level functions

### `__init__(params)` or constructor equivalent
- **Requires:** None
- **Establishes:** Exports public API components (GPUMonitor, LLMMonitor, RingBuffer, App, Dashboard, Config) in `__all__` list
- **Raises:** None

### `__all__`
- **Requires:** None
- **Guarantees:** List of strings containing names of public API components
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe

## Module Invariants
None

## Resource Lifecycle
None

## Notes
This file is a package marker that imports and re-exports components from submodules. It handles import failures gracefully by logging warnings but does not raise exceptions. The actual implementation of the monitored components resides in their respective submodules.
