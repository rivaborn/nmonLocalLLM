# src/nmon/views/dashboard_view.py

## Findings

### Missing error handling in GPU polling [HIGH]
- **Where:** `render()` ~line 74, `self.gpu_monitor.poll()`
- **Issue:** The code calls `self.gpu_monitor.poll()` without any error handling for potential exceptions during GPU data collection.
- **Impact:** If GPU monitoring fails (e.g., NVML error), the entire dashboard rendering will crash instead of gracefully handling the failure.
- **Fix:** Wrap the `self.gpu_monitor.poll()` call in a try-except block to catch and log exceptions, then proceed with empty or default data.

### Potential None dereference in memory calculation [MEDIUM]
- **Where:** `_create_gpu_panel()` ~line 53, `mem_percent = (mem_used_mb / mem_total_mb) * 100`
- **Issue:** The code divides by `mem_total_mb` without checking if it's zero, which could cause a ZeroDivisionError.
- **Impact:** Runtime crash when GPU memory total is reported as zero, which can happen during certain GPU states or driver issues.
- **Fix:** Add explicit check for `mem_total_mb == 0` before division and handle this edge case appropriately.

### Unhandled exception in LLM panel creation [HIGH]
- **Where:** `render()` ~line 88, `ollama_snapshots[-1].reachable`
- **Issue:** The code assumes `ollama_snapshots` is not None and has at least one element before accessing `[-1]`.
- **Impact:** If `ollama_series()` returns None or empty list, accessing `[-1]` will raise IndexError, crashing the dashboard.
- **Fix:** Add proper None/empty list checks before accessing `ollama_snapshots[-1]`.

### Missing validation of snapshot data [MEDIUM]
- **Where:** `_create_llm_panel()` ~line 104, `snapshot.gpu_layers == snapshot.total_layers`
- **Issue:** The code assumes `snapshot.gpu_layers` and `snapshot.total_layers` are valid integers and that `total_layers` is not zero.
- **Impact:** Division by zero or incorrect comparison if layer counts are invalid or None.
- **Fix:** Add validation checks for layer count values before performing comparisons or calculations.

## Verdict

ISSUES FOUND
