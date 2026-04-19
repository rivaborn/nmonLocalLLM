# Module: `src/nmon/ui/widgets/alert_bar.py`

## Role
Implements a PyQt6-based alert bar widget that displays GPU offload status with color-coded warnings and automatic hide functionality.

## Contract: `AlertBar`

### `__init__(parent=None)`
- **Requires:** `parent` parameter must be a valid PyQt6 QWidget or None
- **Establishes:** Widget initialized with empty offload percentage, single-shot hide timer, and basic UI layout; widget is hidden initially
- **Raises:** `TypeError` — if parent is not a QWidget or None

### `set_offload(pct: float) -> None`
- **Requires:** `pct` must be a float in range [0.0, 100.0]
- **Guarantees:** Widget state updated to reflect new offload percentage; timer started or stopped appropriately; widget visibility managed
- **Raises:** `TypeError` — if `pct` is not a float
- **Silent failure:** None
- **Thread safety:** unsafe

### `_update_style() -> None`
- **Requires:** `self._offload_pct` must be a valid float in range [0.0, 100.0]
- **Guarantees:** Label text and style updated according to offload percentage thresholds
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

### `_on_hide_timeout() -> None`
- **Requires:** `self._offload_pct` must be a valid float in range [0.0, 100.0]
- **Guarantees:** Widget hidden only if offload percentage is still 0.0
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
- Widget is always in a valid state between method calls
- Timer is properly managed (single-shot, started/stopped appropriately)
- UI components are properly initialized and connected
- Label text and styling are consistent with offload percentage thresholds

## Resource Lifecycle
- QTimer object created and managed by widget lifecycle
- QLabel and QHBoxLayout components created during initialization
- No external resources require explicit cleanup beyond Qt's automatic garbage collection
