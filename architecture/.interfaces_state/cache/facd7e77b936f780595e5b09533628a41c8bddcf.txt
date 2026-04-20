# Module: `src/nmon/widgets/alert_bar.py`

## Role
Provides a Rich-based terminal widget for displaying active GPU alerts with color-coded styling.

## Contract: `AlertBar`

### `__init__(alert_state: AlertState | None, settings: Settings)`
- **Requires:** `settings` must be a valid `Settings` instance with alert duration configuration; `alert_state` may be `None`
- **Establishes:** `self.alert_state` set to provided value; `self.settings` set to provided settings; `self._visible` initialized to `False`
- **Raises:** `AttributeError` if `settings` lacks required alert configuration attributes

### `__rich__() -> Panel`
- **Requires:** `self.alert_state` and `self.settings` must be properly initialized
- **Guarantees:** Returns a `Panel` instance; if no active alert, returns zero-height panel with `height=0`
- **Raises:** `KeyError` if `self.alert_state.color` is not in `color_map` (but this is handled by `.get()` with default)
- **Silent failure:** None
- **Thread safety:** unsafe

### `update(new_alert_state: AlertState | None, now: float) -> None`
- **Requires:** `new_alert_state` may be `None`; `now` must be a valid timestamp (float)
- **Guarantees:** Updates `self.alert_state` and `self._visible` state appropriately
- **Raises:** `AttributeError` if `new_alert_state` is not `None` and lacks required attributes
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
