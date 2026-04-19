# Module: `src/nmon/ui/__init__.py`

## Role
Package initializer that provides re-exports for nmon UI components, handling optional module imports with graceful fallbacks.

## Contract: Module-level functions

### `__init__(params)`
- **Requires:** None
- **Establishes:** Imports and re-exports UI components from sibling modules if available; no-op if modules not implemented
- **Raises:** None

### `App`
- **Requires:** None
- **Guarantees:** Re-export of App class from `.app` module if available
- **Raises:** ImportError -- if `.app` module cannot be imported (but silently fails due to try/except)
- **Silent failure:** App class not available if `.app` module is not implemented or importable
- **Thread safety:** unsafe

### `Dashboard`
- **Requires:** None
- **Guarantees:** Re-export of Dashboard class from `.dashboard` module if available
- **Raises:** ImportError -- if `.dashboard` module cannot be imported (but silently fails due to try/except)
- **Silent failure:** Dashboard class not available if `.dashboard` module is not implemented or importable
- **Thread safety:** unsafe

### `TempTab`
- **Requires:** None
- **Guarantees:** Re-export of TempTab class from `.temp_tab` module if available
- **Raises:** ImportError -- if `.temp_tab` module cannot be imported (but silently fails due to try/except)
- **Silent failure:** TempTab class not available if `.temp_tab` module is not implemented or importable
- **Thread safety:** unsafe

### `PowerTab`
- **Requires:** None
- **Guarantees:** Re-export of PowerTab class from `.power_tab` module if available
- **Raises:** ImportError -- if `.power_tab` module cannot be imported (but silently fails due to try/except)
- **Silent failure:** PowerTab class not available if `.power_tab` module is not implemented or importable
- **Thread safety:** unsafe

### `LLMTab`
- **Requires:** None
- **Guarantees:** Re-export of LLMTab class from `.llm_tab` module if available
- **Raises:** ImportError -- if `.llm_tab` module cannot be imported (but silently fails due to try/except)
- **Silent failure:** LLMTab class not available if `.llm_tab` module is not implemented or importable
- **Thread safety:** unsafe

### `AlertBar`
- **Requires:** None
- **Guarantees:** Re-export of AlertBar class from `.alert_bar` module if available
- **Raises:** ImportError -- if `.alert_bar` module cannot be imported (but silently fails due to try/except)
- **Silent failure:** AlertBar class not available if `.alert_bar` module is not implemented or importable
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
