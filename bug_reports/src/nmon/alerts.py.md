# src/nmon/alerts.py

## Findings

### Missing null check for gpu_layers [MEDIUM]
- **Where:** `compute_alert()` ~line 27
- **Issue:** The code accesses `snapshot.gpu_layers` without checking if it's None before comparing it to None.
- **Impact:** If `gpu_layers` is None, the condition `snapshot.gpu_layers is not None` will be False, but the code path may still attempt to use `gpu_layers` in a comparison or operation.
- **Fix:** The current logic is actually correct as written, but the comment and logic should be clarified to ensure that `gpu_layers` is only used when not None.

### Incorrect alert condition logic [HIGH]
- **Where:** `compute_alert()` ~line 26-27
- **Issue:** The alert condition requires `snapshot.gpu_use_pct < 100` AND `snapshot.gpu_layers is not None`, but the alert message and logic don't properly account for the case where `gpu_layers` is None but `gpu_use_pct` is below 100.
- **Impact:** The alert may not be triggered when it should be, or may be triggered incorrectly when GPU layers are not being used.
- **Fix:** The condition should be restructured to ensure that alerts are properly triggered when GPU offload is below 100% and GPU layers are being used, or when GPU layers are None but GPU use is below 100%.

### Potential race condition in alert expiration [LOW]
- **Where:** `compute_alert()` ~line 34
- **Issue:** The `expires_at` timestamp is computed using `now` which is passed in, but if `now` is not consistently updated, the alert expiration may be inaccurate.
- **Impact:** Alerts may not expire at the correct time, leading to display issues.
- **Fix:** Ensure that `now` is always the current timestamp when computing alert expiration, or make the expiration logic more robust.

## Verdict

ISSUES FOUND
