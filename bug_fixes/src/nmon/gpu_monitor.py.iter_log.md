# Iteration Log: src/nmon/gpu_monitor.py

Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.
Analysis: bugs, dataflow, contracts
Max iterations: 3
Started: 2026-04-20 01:23:30

## Iteration 1

**Severity:** HIGH:2  MED:5  LOW:1
**Best so far:** iter 1 (HIGH:2 MED:5)

## Bug Analysis

# src/nmon/gpu_monitor.py

## Findings

### Missing NVML resource cleanup [HIGH]
- **Where:** `poll()` function
- **Issue:** `pynvml.nvmlInit()` is called but `pynvml.nvmlShutdown()` is never invoked, leaving NVML handles and global state unreleased.
- **Impact:** Resource leak in long-running processes; repeated initialization attempts will fail or cause undefined behavior.
- **Fix:** Implement a cleanup function or context manager that calls `pynvml.nvmlShutdown()` and resets `_pynvml_initialized`.

### Race condition on global initialization flag [MEDIUM]
- **Where:** `_pynvml_initialized` global and `poll()`
- **Issue:** The global boolean is read and written without thread synchronization, and `nvmlInit()` is called conditionally based on it.
- **Impact:** Concurrent calls to `poll()` (typical in TUI polling loops) can trigger multiple `nvmlInit()` calls or cause inconsistent state, leading to `NVMLError_Unknown` or crashes.
- **Fix:** Protect the initialization check and `nvmlInit()` call with a `threading.Lock()`, or use a singleton/context manager pattern.

### Silent swallowing of process termination signals [LOW]
- **Where:** `poll()` exception handlers
- **Issue:** Broad `except Exception` clauses catch `KeyboardInterrupt` and `SystemExit`, preventing the monitor from responding to user termination requests.
- **Impact:** The application becomes unresponsive to Ctrl+C or programmatic shutdown, requiring force kill.
- **Fix:** Catch `Exception` specifically, or explicitly re-raise `KeyboardInterrupt` and `SystemExit` in the handlers.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/gpu_monitor.py`

## Findings

### Race condition on global NVML initialization flag [HIGH]
- **Where:** `poll()` function, `_pynvml_initialized` check and assignment
- **Issue:** The global `_pynvml_initialized` boolean is read and written without thread synchronization, allowing concurrent invocations of `poll()` to trigger multiple `nvmlInit()` calls or skip initialization incorrectly.
- **Impact:** Double initialization errors, undefined pynvml internal state, or runtime crashes in multi-threaded dashboard contexts.
- **Fix:** Guard the flag with a `threading.Lock` or use a thread-safe initialization pattern.

### Hardcoded zero timestamp injected into snapshot data stream [MEDIUM]
- **Where:** `GpuSnapshot` instantiation in `poll()`
- **Issue:** `timestamp=0.0` is hardcoded instead of capturing the actual sample time, passing invalid temporal data downstream.
- **Impact:** Downstream SQLite storage or Rich dashboard widgets will render or sort samples incorrectly, treating all samples as occurring at epoch zero.
- **Fix:** Replace `0.0` with `time.time()` or `time.perf_counter()` at the exact point of snapshot creation.

### Silent fallback to 0.0 masks sensor read failures [MEDIUM]
- **Where:** `power_draw_w` and `power_limit_w` assignment blocks
- **Issue:** Exceptions during power limit/draw reads are caught and silently replaced with `0.0`, discarding the failure context and injecting invalid zero values into the data stream.
- **Impact:** Dashboard displays zero power draw/limit instead of indicating a sensor error, leading to false operational assumptions and corrupted time-series data.
- **Fix:** Propagate the error, use a sentinel value like `float('nan')`, or explicitly mark the snapshot as incomplete rather than injecting zeros.

## Verdict
ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/gpu_monitor.py`

## Findings

### Race condition on global NVML initialization state [MEDIUM]
- **Where:** `poll()` function, lines 24-30
- **Issue:** The global `_pynvml_initialized` flag is read and written without synchronization, violating the implicit thread-safety contract for shared mutable state. Concurrent calls to `poll()` can both observe `False` and invoke `pynvml.nvmlInit()` simultaneously.
- **Impact:** Duplicate NVML context creation, undefined library state, or crashes in the underlying NVML driver when multiple threads initialize concurrently.
- **Fix:** Guard the initialization block with a `threading.Lock` or use `pynvml.nvmlInit()`'s built-in thread-safe initialization path, ensuring `_pynvml_initialized` is updated atomically.

### Silent failure return on NVML errors [MEDIUM]
- **Where:** `poll()` function, lines 31-34 and 38-40
- **Issue:** The function catches NVML errors and returns `[]` instead of raising an exception or signaling incompleteness, violating the postcondition that callers expect to distinguish between "no GPUs" and "failed to query GPUs".
- **Impact:** Downstream code interprets an empty list as a valid zero-GPU state rather than a monitoring failure, silently masking hardware or driver issues.
- **Fix:** Raise a custom `NmonError` or return a typed result object (e.g., `Result[List[GpuSnapshot], Exception]`) to explicitly signal query failure to callers.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 96 -> 104

## Iteration 2

**Severity:** HIGH:2  MED:4  LOW:0
**Best so far:** iter 2 (HIGH:2 MED:4)

## Bug Analysis

# src/nmon/gpu_monitor.py

## Findings

### Race condition between `poll()` and `shutdown()` [HIGH]
- **Where:** `shutdown()` and `poll()`
- **Issue:** `shutdown()` modifies `_pynvml_initialized` and calls `pynvml.nvmlShutdown()` without acquiring `_nvml_lock`, while `poll()` reads this flag and makes concurrent NVML calls.
- **Impact:** Concurrent execution can crash the process, corrupt the global NVML context, or raise `NVMLError_Uninitialized`/`NVMLError_InvalidArgument` during shutdown or subsequent polls.
- **Fix:** Acquire `_nvml_lock` in `shutdown()` before modifying state or calling `nvmlShutdown()`, and ensure `poll()` holds the lock during all NVML operations or uses a proper lifecycle manager.

### Missing lock scope around NVML calls in `poll()` [MEDIUM]
- **Where:** `poll()` ~lines 48-98
- **Issue:** `_nvml_lock` only protects the initialization check, but all subsequent NVML API calls (`nvmlDeviceGetCount`, `nvmlDeviceGetHandleByIndex`, etc.) are executed outside the lock.
- **Impact:** If `poll()` is called from multiple threads, they will race on the shared NVML context, causing unpredictable metrics, handle invalidation, or crashes.
- **Fix:** Wrap the entire polling loop in `with _nvml_lock:`, or refactor to use a thread-safe NVML session/context manager.

### Silent fallback to 0.0 for temperature [INFO]
- **Where:** `poll()` ~line 63
- **Issue:** If `nvmlDeviceGetTemperature` fails, `temperature_c` defaults to `0.0` instead of `None` or a sentinel.
- **Impact:** Downstream dashboards or calculations may interpret a sensor failure as a valid 0°C reading, masking hardware issues or causing incorrect trend analysis.
- **Fix:** Default to `None` or a documented sentinel value, and ensure downstream consumers handle missing data explicitly.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/gpu_monitor.py`

## Findings

### Race condition on NVML initialization flag [HIGH]
- **Where:** `shutdown()` and `poll()`
- **Issue:** `_pynvml_initialized` is read and written in `shutdown()` without holding `_nvml_lock`, while `poll()` guards it with the lock.
- **Impact:** Concurrent calls can cause double initialization, use-after-shutdown of NVML handles, or corrupted state leading to crashes or undefined behavior.
- **Fix:** Guard all reads and writes of `_pynvml_initialized` and `pynvml.nvmlShutdown()` with `_nvml_lock`.

### Silent temperature data corruption on error [MEDIUM]
- **Where:** `poll()` temperature fetch block
- **Issue:** Falls back to `temperature_c = 0.0` when `nvmlDeviceGetTemperature` fails, masking the error and injecting invalid zero values into the snapshot.
- **Impact:** Downstream SQLite storage and TUI render false zero temperatures, breaking monitoring accuracy and alerting logic.
- **Fix:** Use `None` or a documented sentinel value, or skip the snapshot entirely to match the memory info error handling.

### NaN propagation in power metrics without validation [MEDIUM]
- **Where:** `poll()` power draw/limit fetch blocks
- **Issue:** Assigns `float('nan')` on failure without checking NVML's `NVML_VALUE_NOT_AVAILABLE` constant or handling downstream compatibility.
- **Impact:** NaN values will corrupt SQLite inserts (depending on the driver) and break Rich TUI rendering or mathematical aggregations.
- **Fix:** Validate against NVML's not-available constant, use `None`, or clamp to a safe default before appending to the snapshot.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/gpu_monitor.py`

## Findings

### Thread-safety and state consistency violation in shutdown() [MEDIUM]
- **Where:** `shutdown()` function
- **Issue:** Modifies shared global state `_pynvml_initialized` and calls `pynvml.nvmlShutdown()` without acquiring `_nvml_lock`, violating the thread-safety contract implied by the module's locking strategy.
- **Impact:** Concurrent calls to `poll()` and `shutdown()` can race on `_pynvml_initialized`, potentially causing `poll()` to operate on a shut-down NVML context or `shutdown()` to fail during active polling.
- **Fix:** Acquire `_nvml_lock` in `shutdown()` before checking/modifying `_pynvml_initialized` and calling `nvmlShutdown()`.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 104 -> 105

## Iteration 3

**Severity:** HIGH:3  MED:4  LOW:1
**Best so far:** iter 2 (HIGH:2 MED:4)
**Non-improving streak:** 1 / 2

## Bug Analysis

# src/nmon/gpu_monitor.py

## Findings

### Type mismatch in `GpuSnapshot` fields [MEDIUM]
- **Where:** `GpuSnapshot` dataclass definition and `poll()` ~line 85
- **Issue:** `power_draw_w` and `power_limit_w` are annotated as `float`, but the code assigns `None` to them in the `except` blocks.
- **Impact:** Violates the type contract; downstream code or strict type checkers will fail when encountering `None`, and arithmetic operations on these fields will raise `TypeError` at runtime.
- **Fix:** Update the dataclass annotations to `Optional[float]` or provide safe numeric defaults (e.g., `0.0`) in the exception handlers.

### Silent data loss on memory info failure [HIGH]
- **Where:** `poll()` ~line 78
- **Issue:** When `nvmlDeviceGetMemoryInfo` fails, the code executes `continue`, skipping the snapshot creation for that GPU entirely.
- **Impact:** The GPU is silently dropped from the returned list, causing missing metrics in the dashboard and history without any user-facing warning. This breaks monitoring continuity.
- **Fix:** Remove the `continue` and assign fallback values (e.g., `memory_used_mb = 0.0`) so the snapshot is still created with partial data, or log a clear warning before skipping.

### Unhandled exception in `shutdown()` leaves state inconsistent [LOW]
- **Where:** `shutdown()` ~line 33
- **Issue:** `pynvml.nvmlShutdown()` is called without a try/except block. It can raise `NVMLError` if the driver is unloaded or if called multiple times.
- **Impact:** If an exception occurs, `_pynvml_initialized` remains `True`, leaving the module in an inconsistent state where subsequent `poll()` calls assume NVML is active but it is not.
- **Fix:** Wrap `pynvml.nvmlShutdown()` in a try/except block to catch `pynvml.NVMLError`, log the issue, and ensure `_pynvml_initialized` is safely reset or the error is propagated intentionally.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/gpu_monitor.py`

## Findings

### Race condition on NVML context [HIGH]
- **Where:** `poll()` and `shutdown()` functions
- **Issue:** `_nvml_lock` only guards initialization; NVML API calls in `poll()` execute outside the lock while `shutdown()` may concurrently call `nvmlShutdown()`.
- **Impact:** Concurrent shutdown during polling causes NVML calls to crash or return invalid/stale data, breaking the monitor's data pipeline.
- **Fix:** Extend the lock scope to cover all NVML calls in `poll()`, or implement a thread-safe shutdown sequence that blocks pending polls.

### Type mismatch on power fields [MEDIUM]
- **Where:** `poll()` function, `GpuSnapshot` instantiation
- **Issue:** `power_draw_w` and `power_limit_w` are typed as `float` in `GpuSnapshot` but assigned `None` when NVML calls fail, violating the data contract.
- **Impact:** Downstream storage or dashboard rendering expecting numeric values will fail or produce incorrect calculations.
- **Fix:** Update `GpuSnapshot` type hints to `Optional[float]` or use a numeric sentinel and validate before assignment.

### Invalid default for temperature data [MEDIUM]
- **Where:** `poll()` function, temperature fallback
- **Issue:** `temperature_c` defaults to `0.0` on NVML failure, which is physically impossible and corrupts time-series data.
- **Impact:** Dashboard and history views display invalid zero temperatures, skewing averages and triggering false alerts.
- **Fix:** Default to `None` or a valid sentinel, and filter/flag invalid samples before storage.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/gpu_monitor.py`

## Findings

### Dataclass invariant violation [HIGH]
- **Where:** `GpuSnapshot` dataclass definition and `poll()` function
- **Issue:** The dataclass contract specifies `power_draw_w` and `power_limit_w` as `float`, but `poll()` assigns `None` to these attributes when NVML calls fail.
- **Impact:** Downstream consumers relying on the type contract will encounter runtime `TypeError` or `AttributeError` when performing numeric operations, breaking the guaranteed object state.
- **Fix:** Update the dataclass field annotations to `Optional[float]` or provide numeric fallbacks (e.g., `0.0`) to maintain the invariant.

### Unhandled exception in shutdown cleanup path [MEDIUM]
- **Where:** `shutdown()` function
- **Issue:** `pynvml.nvmlShutdown()` is invoked without exception handling; if it raises, the function aborts without resetting `_pynvml_initialized`, leaving the module in a partially cleaned state.
- **Impact:** Callers expecting a safe, idempotent shutdown contract will face unhandled crashes, and subsequent `poll()` calls may fail or behave unpredictably due to inconsistent global state.
- **Fix:** Wrap the shutdown call in a try/except block that catches NVML-specific errors and safely resets the initialization flag to guarantee consistent state on all exit paths.

## Verdict

ISSUES FOUND

*Stopped: reached MaxIterations (3). Reverting to best version (iter 2, HIGH:2 MED:4).*

---

**Final status:** MAX_ITER
**Iterations run:** 3
**Best iteration:** 2 (HIGH:2 MED:4 LOW:0)
**Remaining (best):** HIGH:2  MED:4  LOW:0
**Fixed file:** `bug_fixes/src/nmon/gpu_monitor.py` (content from iteration 2)
**Written back to source:** no (review `bug_fixes/src/nmon/gpu_monitor.py` and copy manually)
