# Module: `src/nmon/ui/alert_bar.py`

## Role
Provides a TUI widget for displaying GPU offloading alerts in the nmon system.

## Contract: `AlertBar`

### `__init__()`
- **Requires:** None
- **Establishes:** Initializes internal state with `_visible = False`, `_timer = None`, `_min_duration_ms = 1000`, `_message = ""`, `_color = ""`
- **Raises:** None

### `update_alert(sample: LlmSample | None) -> None`
- **Requires:** `sample` parameter may be `None` or an `LlmSample` instance with valid `gpu_utilization_pct` attribute
- **Guarantees:** Sets internal state to reflect alert visibility, message, and color; ensures `_visible` is `False` when `sample` is `None` or `gpu_utilization_pct == 100`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

### `render() -> str`
- **Requires:** None
- **Guarantees:** Returns empty string when not visible; otherwise returns color-formatted message string
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
