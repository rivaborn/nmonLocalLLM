# src/nmon/widgets/alert_bar.py

## Findings

### Missing expiration check in update method [MEDIUM]
- **Where:** `update()` method ~lines 54-62
- **Issue:** The `update()` method doesn't recheck if the new alert has already expired before setting `_visible = True`.
- **Impact:** An expired alert could be marked as visible, causing it to display incorrectly until the next render cycle.
- **Fix:** Add an expiration check in `update()` similar to what's done in `__rich__()`.

### Race condition in _visible state management [MEDIUM]
- **Where:** `__rich__()` and `update()` methods ~lines 26-38 and 54-62
- **Issue:** The `_visible` flag is set in both `__rich__()` and `update()` methods without synchronization, creating potential race conditions in multi-threaded usage.
- **Impact:** In a concurrent environment, the visibility state could become inconsistent with the actual alert state.
- **Fix:** Use a thread-safe approach for managing `_visible` state, or make the visibility logic purely derived from the alert state rather than maintained separately.

### Potential None access in color mapping [LOW]
- **Where:** `__rich__()` method ~line 33
- **Issue:** If `self.alert_state.color` is None, the `get()` method will return the default "red" value, but this could mask an underlying data inconsistency.
- **Impact:** Silently falls back to default color instead of flagging invalid alert data.
- **Fix:** Add validation or logging when `self.alert_state.color` is not in the expected set.

## Verdict

ISSUES FOUND
