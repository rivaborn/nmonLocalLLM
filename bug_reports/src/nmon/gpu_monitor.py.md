# src/nmon/gpu_monitor.py

## Findings

### Missing pynvml handle cleanup on error paths
- **Where:** `poll()` function, lines 42-44
- **Issue:** GPU handles are acquired via `nvmlDeviceGetHandleByIndex()` but not explicitly released, and the function may return early due to exceptions.
- **Impact:** Potential resource leak of GPU handles if exceptions occur during handle acquisition or subsequent operations.
- **Fix:** Use context managers or explicitly call `pynvml.nvmlDeviceGetHandleByIndex()` within a try/finally block to ensure proper cleanup.

### Inconsistent exception handling for memory junction temperature
- **Where:** `poll()` function, lines 50-53
- **Issue:** The `mem_junction_temp_c` is set to `None` when `nvmlDeviceGetMemoryBusTemperature()` fails, but this is not logged or handled consistently with other optional metrics.
- **Impact:** Silent failure for memory junction temperature data, which could mask hardware compatibility issues.
- **Fix:** Log the failure to get memory junction temperature for debugging purposes.

### Potential race condition in global initialization
- **Where:** `poll()` function, lines 12-17
- **Issue:** The global `_pynvml_initialized` flag is not protected by a lock, making it vulnerable to race conditions in multi-threaded environments.
- **Impact:** Concurrent calls to `poll()` might attempt to initialize pynvml multiple times or in an inconsistent state.
- **Fix:** Use a threading lock around the initialization check and assignment.

### Unhandled exception in memory info retrieval
- **Where:** `poll()` function, lines 47-52
- **Issue:** If `nvmlDeviceGetMemoryInfo()` fails, the function continues with `continue` but doesn't log the error or attempt recovery.
- **Impact:** Silent data loss for memory metrics, potentially leading to incorrect monitoring behavior.
- **Fix:** Log the error and consider setting default values for memory metrics instead of skipping the GPU entirely.

### Incorrect power limit handling
- **Where:** `poll()` function, lines 64-67
- **Issue:** Power limit is divided by 1000.0, but `nvmlDeviceGetPowerLimit()` returns milliwatts, so the division is incorrect.
- **Impact:** Power limit values are incorrectly scaled, leading to inaccurate power consumption reporting.
- **Fix:** Remove the division by 1000.0 since `nvmlDeviceGetPowerLimit()` already returns watts.

## Verdict

ISSUES FOUND
