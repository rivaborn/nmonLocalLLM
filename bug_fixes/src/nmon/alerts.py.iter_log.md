# Iteration Log: src/nmon/alerts.py

Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.
Analysis: bugs, dataflow, contracts
Max iterations: 3
Started: 2026-04-19 22:32:26

## Iteration 1

**Severity:** HIGH:1  MED:1  LOW:0
**Best so far:** iter 1 (HIGH:1 MED:1)

## Bug Analysis

# src/nmon/alerts.py

## Findings

### Missing validation for settings attributes [HIGH]
- **Where:** `compute_alert()` ~lines 68-69
- **Issue:** `settings.offload_alert_pct` and `settings.min_alert_display_s` are accessed and used in comparisons/arithmetic without checking for `None` or invalid types.
- **Impact:** Raises `TypeError` at runtime if the TOML config omits or misconfigures these fields, crashing the dashboard render loop.
- **Fix:** Add explicit validation or provide safe defaults/fallbacks before use.

### Inverted alert color logic [MEDIUM]
- **Where:** `compute_alert()` ~lines 65-67
- **Issue:** The code assigns `"red"` when `gpu_use_pct > offload_alert_pct`. If `gpu_use_pct` tracks offload percentage, higher values indicate better performance, so exceeding the threshold should trigger a positive/neutral color, not a warning.
- **Impact:** Alerts display incorrectly (red for good offload, orange for poor offload), misleading the user.
- **Fix:** Invert the comparison or swap the color assignments to match the metric's semantics.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/alerts.py`

## Findings

None.

## Verdict

CLEAN

---

## Contract Analysis

# Contract Analysis: `src/nmon/alerts.py`

## Findings

None.

## Verdict

CLEAN

**Fix applied.** Lines: 81 -> 89

## Iteration 2

**Severity:** HIGH:0  MED:3  LOW:1
**Best so far:** iter 2 (HIGH:0 MED:3)

## Bug Analysis

# src/nmon/alerts.py

## Findings

### Inverted alert color logic [MEDIUM]
- **Where:** `compute_alert()` ~line 68
- **Issue:** The condition `if snapshot.gpu_use_pct > offload_alert_pct:` assigns `"orange"` to `color`, but the docstring and inline comments explicitly state it should be `"red"` when usage exceeds the threshold. The logic is inverted.
- **Impact:** Alerts will display the wrong severity color (orange instead of red) when GPU usage is above the configured threshold, misleading the user about the alert's urgency.
- **Fix:** Swap the color assignments in the `if/else` block so that `gpu_use_pct > offload_alert_pct` results in `"red"` and the `else` branch results in `"orange"`.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/alerts.py`

## Findings

### Inverted Alert Color Mapping [MEDIUM]
- **Where:** `compute_alert`, lines 68-71
- **Issue:** The conditional assignment for `color` is inverted relative to the documented intent and standard severity conventions; when `gpu_use_pct` exceeds the threshold, it assigns "orange" instead of "red".
- **Impact:** The dashboard renders incorrect severity colors, causing users to misinterpret alert urgency and breaking the expected data contract between this module and the TUI renderer.
- **Fix:** Swap the color assignments in the `if/else` block so that `> threshold` maps to "red" and `<= threshold` maps to "orange".

### Unvalidated Negative Display Duration [LOW]
- **Where:** `compute_alert`, lines 60-63
- **Issue:** `min_alert_display_s` is only validated for `None` and numeric type, but negative values are permitted through to the `expires_at` calculation.
- **Impact:** A negative duration causes `expires_at` to fall in the past, potentially triggering immediate alert expiration or causing the TUI to skip rendering the alert entirely.
- **Fix:** Clamp the value to a non-negative range (e.g., `max(0.0, min_alert_display_s)`) before using it in arithmetic.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/alerts.py`

## Findings

### Inverted Alert Color Logic vs Documented Contract [MEDIUM]
- **Where:** `compute_alert` function, lines 48-52
- **Issue:** The implementation assigns `"orange"` when `gpu_use_pct > offload_alert_pct`, directly contradicting the docstring which promises `"red"` in that case.
- **Impact:** Downstream dashboard rendering will display inverted severity colors, misleading users about the actual GPU offload threshold breach.
- **Fix:** Swap the color assignments in the conditional block to align with the documented threshold behavior, or update the docstring to reflect the actual implementation.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 89 -> 89

## Iteration 3

**Severity:** HIGH:0  MED:2  LOW:0
**Best so far:** iter 3 (HIGH:0 MED:2)

## Bug Analysis

# src/nmon/alerts.py

## Findings

### Inverted threshold comparison for alert color [MEDIUM]
- **Where:** `compute_alert()` ~line 68
- **Issue:** The condition `snapshot.gpu_use_pct > offload_alert_pct` assigns "red" when the metric is *above* the threshold, but the alert is explicitly for "GPU offload below 100%". Lower offload should be worse, not better.
- **Impact:** Alerts will incorrectly show "red" (critical) when offload is actually healthy (above threshold), and "orange" (warning) when offload is critically low.
- **Fix:** Change `>` to `<` so that falling below the configured threshold triggers the worse color state.

### Missing type validation for snapshot metrics [INFO]
- **Where:** `compute_alert()` ~line 53
- **Issue:** `snapshot.gpu_use_pct` is compared to `100` and used in arithmetic without verifying it is numeric. If the upstream `OllamaSnapshot` provides a string or other type, this will raise a `TypeError`.
- **Impact:** Unhandled crash in the alert computation path if malformed or untyped snapshot data is passed.
- **Fix:** Add `isinstance(snapshot.gpu_use_pct, (int, float))` validation or enforce numeric typing in the `OllamaSnapshot` dataclass.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/alerts.py`

## Findings

### Unvalidated scale and type on `gpu_use_pct` [MEDIUM]
- **Where:** `compute_alert`, lines 58-60
- **Issue:** `snapshot.gpu_use_pct` is used directly in threshold comparisons without type validation or scale normalization, implicitly assuming a 0-100 numeric range.
- **Impact:** If the upstream `OllamaSnapshot` module provides utilization as a 0.0-1.0 normalized float, the comparison `> offload_alert_pct` (default 90) will silently evaluate incorrectly, causing alerts to never trigger or always show the wrong color; a non-numeric type will raise a TypeError at runtime.
- **Fix:** Add explicit type validation (`isinstance(snapshot.gpu_use_pct, (int, float))`) and normalize the value to a 0-100 scale before any threshold comparison.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/alerts.py`

## Findings

None.

## Verdict

CLEAN

*Stopped: reached MaxIterations (3). Reverting to best version (iter 3, HIGH:0 MED:2).*

---

**Final status:** MAX_ITER
**Iterations run:** 3
**Best iteration:** 3 (HIGH:0 MED:2 LOW:0)
**Remaining (best):** HIGH:0  MED:2  LOW:0
**Fixed file:** `bug_fixes/src/nmon/alerts.py` (content from iteration 3)
**Written back to source:** no (review `bug_fixes/src/nmon/alerts.py` and copy manually)
