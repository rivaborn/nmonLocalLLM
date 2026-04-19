# Module: src/nmon/storage/__init__.py

## Role
Exports storage-related classes and utilities for nmon's GPU monitoring system.

## Contract: Module-level functions

### `__init__`
- **Requires:** `ring_buffer.py` must be importable or absent from the filesystem
- **Establishes:** `RingBuffer` class is available in module namespace if `ring_buffer.py` exists
- **Raises:** `ImportError` if `ring_buffer.py` exists but cannot be imported due to syntax or runtime errors

## Module Invariants
None

## Resource Lifecycle
None

## Notes
This module is a simple package marker that conditionally imports and re-exports `RingBuffer` from `ring_buffer.py`. It does not manage any resources or maintain state. The conditional import with bare `except ImportError` means that if `ring_buffer.py` is missing or broken, the module will silently fail to expose `RingBuffer` but will not raise an exception during import. This could lead to runtime errors if code assumes `RingBuffer` is available.
