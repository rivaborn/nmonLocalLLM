# Iteration Log: src/nmon/db.py

Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.
Analysis: bugs, dataflow, contracts
Max iterations: 3
Started: 2026-04-20 00:33:59

## Iteration 1

**Severity:** HIGH:2  MED:1  LOW:1
**Best so far:** iter 1 (HIGH:2 MED:1)

## Bug Analysis

# src/nmon/db.py

## Findings

### Silent exception swallowing causes data loss [HIGH]
- **Where:** `prune_old_data()` and `flush_to_db()`
- **Issue:** Both functions catch `Exception`, log a warning, and silently `return` instead of propagating the error.
- **Impact:** If the database becomes locked, full, or corrupt, metrics are silently dropped without the caller knowing, leading to permanent data loss in the monitoring history.
- **Fix:** Remove the bare `except` blocks or re-raise the exception after logging so the caller can handle persistence failures appropriately.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/db.py`

## Findings

### Silent Error Swallowing in Mutation Functions [HIGH]
- **Where:** `prune_old_data` and `flush_to_db`
- **Issue:** Both functions catch `Exception`, log a warning, and return silently, discarding the original traceback and failing to notify the caller that the database operation failed.
- **Impact:** The scheduler or TUI will assume data was successfully pruned or flushed, leading to silent metric loss or stale dashboard data with no runtime feedback.
- **Fix:** Re-raise the exception after logging, or return a boolean/status indicator so the caller can handle partial failures.

### Unvalidated `history_hours` Parameter [LOW]
- **Where:** `prune_old_data`
- **Issue:** `history_hours` is used directly in arithmetic without checking for negative or zero values, allowing invalid cutoff calculations.
- **Impact:** Negative values push the cutoff timestamp into the future, preventing any deletion; zero values delete all historical data.
- **Fix:** Add a guard clause `if history_hours <= 0: return` or raise `ValueError` to enforce valid ranges.

## Verdict
ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/db.py`

## Findings

### Silent failure on DB errors violates postcondition [MEDIUM]
- **Where:** `prune_old_data` and `flush_to_db`
- **Issue:** Both functions catch `Exception`, log a warning, and silently return `None` on failure, violating the postcondition that persistence operations either succeed or explicitly signal failure.
- **Impact:** Callers assume data was pruned or flushed successfully, leading to silent data loss or stale dashboard metrics without any error handling downstream.
- **Fix:** Remove the bare `except Exception` block or re-raise the exception after logging to ensure callers are notified of failed persistence operations.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 107 -> 101

## Iteration 2

**Severity:** HIGH:0  MED:4  LOW:1
**Best so far:** iter 2 (HIGH:0 MED:4)

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/db.py`

## Findings

### Coupled transaction for independent metrics [MEDIUM]
- **Where:** `flush_to_db`
- **Issue:** GPU and Ollama inserts share a single transaction; if the optional Ollama insert fails, all GPU data is rolled back.
- **Impact:** Silent loss of GPU metrics when Ollama data is malformed or unavailable, breaking expected persistence flow.
- **Fix:** Validate Ollama data before GPU insertion, or commit GPU metrics separately before attempting Ollama insertion.

### Missing validation for history_hours [MEDIUM]
- **Where:** `prune_old_data`
- **Issue:** No validation for negative or zero `history_hours` values before calculating the cutoff timestamp.
- **Impact:** Negative values result in a future cutoff (deletes nothing); zero values delete all historical data unexpectedly.
- **Fix:** Add `if history_hours <= 0: raise ValueError(...)` or clamp to a minimum positive threshold.

### Unvalidated snapshot attributes at module boundary [LOW]
- **Where:** `flush_to_db`
- **Issue:** Direct attribute access on `GpuSnapshot` and `OllamaSnapshot` objects without verifying structure or handling missing fields.
- **Impact:** `AttributeError` at runtime if caller passes a dict, partial object, or mismatched snapshot type.
- **Fix:** Use `getattr(snap, 'field', default)` or validate snapshot schema/type before insertion.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/db.py`

## Findings

### Missing precondition validation for gpu_snapshots [MEDIUM]
- **Where:** `flush_to_db`
- **Issue:** The function signature promises `gpu_snapshots: List[GpuSnapshot]` but performs no runtime check to ensure it is not `None`, directly iterating over it.
- **Impact:** Callers passing `None` will trigger an unhandled `TypeError` at the loop start instead of a clear `ValueError` or graceful no-op, breaking expected error handling contracts.
- **Fix:** Add `if gpu_snapshots is None: raise ValueError("gpu_snapshots must be a list, not None")` at the function entry.

### Non-atomic flush postcondition gap [MEDIUM]
- **Where:** `flush_to_db`
- **Issue:** The function accumulates inserts in a loop and only calls `conn.commit()` at the end. If an exception occurs mid-loop, the transaction is abandoned and the connection closed in `finally` without an explicit `rollback`.
- **Impact:** Downstream callers expecting an all-or-nothing flush contract may observe partial state loss or inconsistent DB state without being explicitly warned, as the implicit rollback on close is not guaranteed by the public API contract.
- **Fix:** Wrap the loop in a `try...except` block that calls `conn.rollback()` before re-raising, or use `with conn:` context manager to enforce transaction boundaries.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 101 -> 113

## Iteration 3

**Severity:** HIGH:1  MED:2  LOW:0
**Best so far:** iter 2 (HIGH:0 MED:4)
**Non-improving streak:** 1 / 2

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/db.py`

## Findings

### Non-atomic transaction across metric inserts [HIGH]
- **Where:** `flush_to_db`
- **Issue:** GPU metrics are committed separately from Ollama metrics; if the Ollama insert fails, GPU data is already persisted, causing partial data corruption.
- **Impact:** Inconsistent database state where GPU metrics exist without corresponding Ollama metrics for the same sample cycle, breaking data integrity and breaking downstream aggregation queries.
- **Fix:** Remove the intermediate `conn.commit()` after the GPU loop and place a single `conn.commit()` after both inserts succeed, ensuring atomicity.

### Unvalidated snapshot attributes passed to SQL [MEDIUM]
- **Where:** `flush_to_db` loop and Ollama insert block
- **Issue:** `gpu_snapshots` and `ollama_snapshot` are used directly without validating that required attributes exist or are numeric, relying entirely on upstream module contracts.
- **Impact:** Runtime `AttributeError` or `TypeError` during insertion if the monitor returns malformed snapshots, potentially dropping samples silently or crashing the flush process.
- **Fix:** Add explicit attribute/type checks or use `getattr` with safe defaults, and validate numeric ranges before passing to `cursor.execute`.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/db.py`

## Findings

### Transactional Integrity Violation in `flush_to_db` [MEDIUM]
- **Where:** `flush_to_db` function
- **Issue:** The function commits GPU metrics and Ollama metrics in separate `conn.commit()` calls. If the GPU insert succeeds and commits, but the Ollama insert fails, the function raises an exception while leaving the database in a partially flushed state.
- **Impact:** Callers expecting an atomic flush operation will observe inconsistent data (GPU metrics persisted without corresponding Ollama metrics) despite receiving an error, violating the implicit all-or-nothing contract of a "flush" method.
- **Fix:** Defer all `conn.commit()` calls until after both inserts succeed, or wrap the entire operation in a single transaction with a rollback on any failure.

## Verdict

ISSUES FOUND

*Stopped: reached MaxIterations (3). Reverting to best version (iter 2, HIGH:0 MED:4).*

---

**Final status:** MAX_ITER
**Iterations run:** 3
**Best iteration:** 2 (HIGH:0 MED:4 LOW:1)
**Remaining (best):** HIGH:0  MED:4  LOW:1
**Fixed file:** `bug_fixes/src/nmon/db.py` (content from iteration 2)
**Written back to source:** no (review `bug_fixes/src/nmon/db.py` and copy manually)
