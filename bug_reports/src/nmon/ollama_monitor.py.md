# src/nmon/ollama_monitor.py

## Findings

### Missing Error Handling for JSON Parsing
- **Where:** `poll()` method ~lines 50-52
- **Issue:** The code calls `response.json()` without checking if the response contains valid JSON, which can raise a `json.JSONDecodeError`.
- **Impact:** Unhandled exception that crashes the monitoring loop when Ollama returns malformed JSON.
- **Fix:** Wrap `response.json()` in a try-except block to handle `json.JSONDecodeError` gracefully.

### Potential Division by Zero in GPU Usage Calculation
- **Where:** `poll()` method ~lines 57-60
- **Issue:** The code calculates `gpu_use_pct = (gpu_layers / total_layers) * 100` without checking if `total_layers` is zero.
- **Impact:** Division by zero error when `total_layers` is 0, causing a crash.
- **Fix:** Add a check `if total_layers == 0:` before the division to prevent division by zero.

### Inconsistent Timestamp Usage
- **Where:** `poll()` method ~lines 44, 67
- **Issue:** The `timestamp` field in `OllamaSnapshot` is set to `0.0` in both success and error cases, instead of using actual timestamps.
- **Impact:** Loss of temporal information for monitoring data points.
- **Fix:** Use `time.time()` or similar to populate the timestamp field in all cases.

### Resource Leak in HTTP Client Usage
- **Where:** `probe_ollama()` method ~lines 27-32
- **Issue:** The method accepts an `httpx.AsyncClient` but doesn't ensure it's properly closed or managed, potentially leading to resource leaks.
- **Impact:** HTTP client resources may not be released properly in long-running applications.
- **Fix:** Either require the caller to manage the client lifecycle or use a context manager for client creation.

## Verdict

ISSUES FOUND
