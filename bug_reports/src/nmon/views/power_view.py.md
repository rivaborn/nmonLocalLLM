# src/nmon/views/power_view.py

## Findings

### Missing error handling in GPU power data retrieval [HIGH]
- **Where:** `_render_gpu_charts()` ~lines 85-90
- **Issue:** The `get_power_history()` call can fail silently if the database connection is broken or query fails.
- **Impact:** GPU charts may display empty or stale data without any error indication to user.
- **Fix:** Wrap `get_power_history()` call in try/except and handle database errors appropriately.

### Potential None dereference in Ollama info rendering [MEDIUM]
- **Where:** `_render_ollama_info()` ~lines 117-122
- **Issue:** `self.ollama_snapshot.loaded_model` could be None but is used directly in f-string without null check.
- **Impact:** Runtime error if `loaded_model` is None and not handled gracefully.
- **Fix:** Add null check or provide default value for `loaded_model` in f-string.

### Inconsistent data handling in sparkline creation [LOW]
- **Where:** `_render_gpu_charts()` ~lines 85-95
- **Issue:** The code assumes `get_power_history()` always returns valid data, but may return empty list or None.
- **Impact:** Sparkline widget may receive invalid data causing rendering issues or crashes.
- **Fix:** Validate `power_data` before passing to Sparkline constructor.

## Verdict

ISSUES FOUND
