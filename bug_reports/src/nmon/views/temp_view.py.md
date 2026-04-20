# src/nmon/views/temp_view.py

## Findings

### Missing error handling for history store queries [MEDIUM]
- **Where:** `history_store.gpu_series()` and `history_store.gpu_mem_series()` calls ~lines 40-45
- **Issue:** The code assumes history queries will succeed and return valid data without checking for exceptions or invalid return values.
- **Impact:** If database queries fail or return unexpected data types, the application may crash or display incorrect information.
- **Fix:** Add proper exception handling around history store queries and validate returned data before passing to Sparkline constructor.

### Potential None dereference in threshold line [MEDIUM]
- **Where:** `sparkline.add_threshold(threshold_line)` ~line 49
- **Issue:** The code creates a ThresholdLine with `prefs.temp_threshold_c` but doesn't validate that this value is a number before passing it to ThresholdLine constructor.
- **Impact:** If `temp_threshold_c` is None or an invalid type, ThresholdLine constructor may fail or behave unexpectedly.
- **Fix:** Validate that `prefs.temp_threshold_c` is a numeric type before creating ThresholdLine instance.

### Inconsistent layout handling for GPU panels [MEDIUM]
- **Where:** Layout management ~lines 51-55
- **Issue:** The code calls `layout.split_row()` before adding each GPU panel but doesn't ensure the layout has sufficient space or properly manage the layout structure.
- **Impact:** May cause layout rendering issues or incorrect panel placement in the TUI.
- **Fix:** Review layout structure and ensure proper row/column management for GPU panels.

## Verdict

ISSUES FOUND
