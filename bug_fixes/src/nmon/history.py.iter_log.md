# Iteration Log: src/nmon/history.py

Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.
Analysis: bugs, dataflow, contracts
Max iterations: 3
Started: 2026-04-20 02:05:24

## Iteration 1

**Severity:** HIGH:3  MED:4  LOW:2
**Best so far:** iter 1 (HIGH:3 MED:4)

## Bug Analysis

# src/nmon/history.py

## Findings

### Untracked Flush State / Data Duplication [HIGH]
- **Where:** `flush_to_db()`
- **Issue:** Inserts all in-memory snapshots on every call without clearing them or tracking persisted state, causing duplicate DB rows and memory bloat.
- **Impact:** Database grows unbounded with duplicates; memory usage increases until trim removes them, but DB retains duplicates.
- **Fix:** Clear `self._gpu_snapshots` and `self._ollama_snapshots` after successful flush, or track a `last_flushed_index` to only insert new samples.

### Nested Context Manager / Transaction Boundary Conflict [MEDIUM]
- **Where:** `add_gpu_samples()` calling `flush_to_db()`
- **Issue:** `add_gpu_samples` opens a `DbConnection` context, then passes `db` to `flush_to_db`, which wraps it again with `with db:`. This nests transaction boundaries incorrectly.
- **Impact:** May cause double commit/rollback, transaction state corruption, or `RuntimeError` depending on `DbConnection` implementation.
- **Fix:** Remove `with db:` from `flush_to_db` and rely on the caller's context, or pass a flag to skip context management.

### ZeroDivisionError in Max Size Calculation [LOW]
- **Where:** `add_gpu_samples()` and `add_ollama_sample()`
- **Issue:** `max_size` divides by `self._settings.poll_interval_s` without checking for zero or negative values.
- **Impact:** Crashes with `ZeroDivisionError` if poll interval is misconfigured to 0.
- **Fix:** Add a guard `if self._settings.poll_interval_s <= 0: return` or use `max(1, ...)` or validate in `Settings`.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/history.py`

## Findings

### Ollama snapshots never persisted to database [HIGH]
- **Where:** `add_ollama_sample`
- **Issue:** The method appends samples to the in-memory deque but never invokes `flush_to_db`, unlike the GPU sample path.
- **Impact:** All Ollama history is lost on process restart or crash, breaking data continuity and dashboard accuracy.
- **Fix:** Mirror the max-size trimming and conditional `flush_to_db` call from `add_gpu_samples` into `add_ollama_sample`.

### Unbounded duplicate inserts on every flush [HIGH]
- **Where:** `flush_to_db`
- **Issue:** The method iterates over the entire deque contents on every call without tracking which rows were already written, relying on `INSERT OR IGNORE` which does nothing without a unique constraint.
- **Impact:** Database grows unbounded with duplicate records, corrupting history queries and wasting storage.
- **Fix:** Track a `last_flushed_timestamp` or enforce a unique constraint on `(gpu_index, ts)`, and only insert new snapshots since the last flush.

### Flush failures silently swallowed [MEDIUM]
- **Where:** `add_gpu_samples` and `flush_to_db`
- **Issue:** `flush_to_db` catches `Exception` and logs a warning, but `add_gpu_samples` ignores the operation's success state and continues normally.
- **Impact:** Application state assumes data is persisted when it is not, leading to silent data loss and inconsistent dashboard history.
- **Fix:** Return a boolean or raise a specific exception from `flush_to_db`, and handle the failure in `add_gpu_samples` (e.g., retry or mark data as pending).

### Unvalidated DB row types passed to snapshots [LOW]
- **Where:** `__init__`
- **Issue:** Raw values from `db.execute(...).fetchall()` are passed directly to `GpuSnapshot` and `OllamaSnapshot` constructors without type checking or coercion.
- **Impact:** If the database schema changes or returns unexpected types (e.g., strings instead of floats), snapshot initialization may fail or store corrupted data.
- **Fix:** Explicitly cast or validate row values before constructing snapshot objects, or rely on ORM/type hints with validation.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/history.py`

## Findings

### Missing Precondition for Poll Interval [MEDIUM]
- **Where:** `add_gpu_samples` and `add_ollama_sample`
- **Issue:** Calculates `max_size` by dividing by `self._settings.poll_interval_s` without validating it is non-zero and positive.
- **Impact:** Triggers a `ZeroDivisionError` at runtime if the configuration is invalid, crashing the monitoring loop.
- **Fix:** Validate `poll_interval_s > 0` before division or enforce a safe minimum threshold.

### Silent Contract Break in Database Flush [MEDIUM]
- **Where:** `flush_to_db` method
- **Issue:** Catches all exceptions and logs a warning, but returns `None` instead of signaling failure or re-raising.
- **Impact:** Callers expect persistence to either succeed or raise an error; silent swallowing breaks this contract and masks data loss.
- **Fix:** Remove the bare `except Exception` block or return a success/failure status to honor the persistence contract.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 163 -> 180

## Iteration 2

**Severity:** HIGH:4  MED:1  LOW:3
**Best so far:** iter 1 (HIGH:3 MED:4)
**Non-improving streak:** 1 / 2

## Bug Analysis

# src/nmon/history.py

## Findings

### Cross-Deque Data Loss in `flush_to_db` [HIGH]
- **Where:** `flush_to_db()` ~line 158
- **Issue:** Unconditionally calls `self._gpu_snapshots.clear()` and `self._ollama_snapshots.clear()` regardless of which method triggered the flush.
- **Impact:** Calling `add_ollama_sample()` triggers a flush that silently wipes pending GPU snapshots (and vice versa), causing irreversible data loss.
- **Fix:** Only clear the deque corresponding to the active metric type, or pass a flag to `flush_to_db` to specify which data to clear.

### Flush Triggered on Zero `max_size` [LOW]
- **Where:** `add_gpu_samples()` / `add_ollama_sample()` ~line 78 / ~line 108
- **Issue:** If `poll_interval_s` exceeds `history_hours * 3600`, `max_size` evaluates to `0`. The condition `len(...) >= 0.8 * max_size` becomes `len(...) >= 0`, which is always true.
- **Impact:** Triggers a database flush on every single sample addition, causing severe performance degradation and unnecessary I/O.
- **Fix:** Add a guard clause: `if max_size > 0 and len(self._gpu_snapshots) >= 0.8 * max_size:`.

### Silent Row Dropping via `INSERT OR IGNORE` [INFO]
- **Where:** `flush_to_db()` ~line 138
- **Issue:** Relies on `INSERT OR IGNORE` to handle duplicates without verifying that unique constraints actually exist on the target columns.
- **Impact:** If the database schema lacks the expected unique indexes, rows will be silently dropped or inserted as duplicates, corrupting history accuracy.
- **Fix:** Verify unique constraints exist in the schema, or use explicit `ON CONFLICT` handling with known constraint names.

## Verdict
ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/history.py`

## Findings

### Cross-deque data loss on flush [HIGH]
- **Where:** `flush_to_db` (lines 168-169)
- **Issue:** Unconditionally clears both `_gpu_snapshots` and `_ollama_snapshots` regardless of which metric triggered the flush.
- **Impact:** Silent loss of unflushed samples for the other metric type whenever a flush is triggered.
- **Fix:** Clear only the deque corresponding to the flushed metric, or defer clearing until after a successful DB commit.

### Ignored flush failure return value [HIGH]
- **Where:** `add_gpu_samples` and `add_ollama_sample` (lines 78, 108)
- **Issue:** Calls `flush_to_db` but ignores its boolean return value (`if not self.flush_to_db(db): pass`), while deques are already cleared inside `flush_to_db`.
- **Impact:** Fails to propagate partial failure; results in permanent silent data loss if the DB write fails.
- **Fix:** Check the return value, handle failure (e.g., rollback clearing or retry), and remove the `pass` statement.

### Unvalidated DB row deserialization [LOW]
- **Where:** `__init__` (lines 28-48)
- **Issue:** Constructs snapshot objects directly from `row` indices without validating column count or type compatibility.
- **Impact:** Could raise `IndexError` or store malformed data if the SQLite schema changes or returns unexpected types.
- **Fix:** Validate `len(row)` and explicitly cast/verify types during deserialization.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/history.py`

## Findings

### Transaction not committed in `flush_to_db` [HIGH]
- **Where:** `flush_to_db` method
- **Issue:** Returns `True` on success but never calls `db.commit()`, violating the persistence contract implied by the method name and return value.
- **Impact:** Caller assumes data is durably saved, but it is silently rolled back or lost when the context manager exits.
- **Fix:** Explicitly call `db.commit()` before returning `True`, or document that `DbConnection` auto-commits.

### Bounded history contract bypassed in sample adders [MEDIUM]
- **Where:** `add_gpu_samples` and `add_ollama_sample` methods
- **Issue:** Early return when `poll_interval_s <= 0` skips the trimming logic, violating the implicit contract that internal deques are strictly bounded by `max_size`.
- **Impact:** Memory grows unbounded if poll interval is misconfigured, breaking the store's memory safety contract.
- **Fix:** Remove the early return or apply trimming independently of `poll_interval_s`, handling division safely.

### Silent field validation in `gpu_stat` [LOW]
- **Where:** `gpu_stat` method
- **Issue:** Uses `getattr(s, field, None)` which silently filters out invalid fields instead of validating them upfront or raising a clear error.
- **Impact:** Caller receives `None` or partial statistics without knowing the field was invalid, silently altering the expected result contract.
- **Fix:** Validate `field` against known snapshot attributes or raise `ValueError`/`AttributeError` for unknown fields.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 180 -> 185

## Iteration 3

**Severity:** HIGH:1  MED:4  LOW:2
**Best so far:** iter 3 (HIGH:1 MED:4)

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/history.py`

## Findings

### Zero max_size causes silent data loss [MEDIUM]
- **Where:** add_gpu_samples / add_ollama_sample
- **Issue:** When `history_hours * 3600 / poll_interval_s` evaluates to less than 1, `max_size` becomes 0, and the `while len > max_size` loop immediately drains the entire deque.
- **Impact:** All in-memory history is discarded, breaking dashboard and stat calculations.
- **Fix:** Enforce a minimum `max_size` of 1 or skip trimming when `max_size` is 0.

### INSERT OR IGNORE silently drops conflicting rows [MEDIUM]
- **Where:** flush_to_db
- **Issue:** Uses `INSERT OR IGNORE` without verifying table constraints; if a unique constraint exists on timestamp or GPU index, conflicting rows are silently discarded.
- **Impact:** Unreported data loss in the SQLite database, causing incomplete history.
- **Fix:** Use `INSERT` with explicit conflict resolution or verify schema constraints before flushing.

### Unhandled AttributeError in gpu_stat [LOW]
- **Where:** gpu_stat
- **Issue:** `getattr(s, field)` is called without a try/except; if `field` is not a valid attribute on `GpuSnapshot`, it raises an unhandled exception.
- **Impact:** Crash during dashboard stat rendering when invalid field names are passed.
- **Fix:** Validate `field` against known attributes or wrap in try/except with safe fallback.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/history.py`

## Findings

### Missing `samples` validation in `add_gpu_samples`/`add_ollama_sample` [MEDIUM]
- **Where:** `add_gpu_samples` and `add_ollama_sample` methods
- **Issue:** Functions call `extend()` on the `samples` parameter without validating it is not `None`, violating the implicit precondition that parameters are valid iterables.
- **Impact:** Caller passing `None` triggers an unhandled `TypeError`, crashing the monitoring loop.
- **Fix:** Add `if samples is None: return` or validate type at the start of each method.

### Missing `field` validation in `gpu_stat` [MEDIUM]
- **Where:** `gpu_stat` method
- **Issue:** `field` is passed directly to `getattr()` without verifying it matches a valid `GpuSnapshot` attribute, breaking the precondition that `field` must be a valid attribute name.
- **Impact:** Passing an invalid string raises an unhandled `AttributeError` instead of a documented `ValueError` or graceful fallback.
- **Fix:** Validate `field` against a whitelist of valid snapshot attributes before calling `getattr`.

### Invariant break via `max_size = 0` causing data drain [HIGH]
- **Where:** `add_gpu_samples` and `add_ollama_sample` methods
- **Issue:** When `poll_interval_s <= 0`, `max_size` becomes 0. The subsequent `while len(...) > max_size` loop drains the entire deque, violating the retention invariant for historical data.
- **Impact:** All newly added samples are immediately discarded, breaking history continuity and causing silent data loss across calls.
- **Fix:** Enforce `poll_interval_s > 0` as a precondition in `__init__` or clamp `max_size` to a minimum of 1 before trimming.

### Unvalidated `db_path` in `__init__` [LOW]
- **Where:** `__init__` method
- **Issue:** `settings.db_path` is passed directly to `DbConnection` without `None` or type validation.
- **Impact:** If `db_path` is `None`, `DbConnection` initialization or subsequent queries will fail with a low-level error, bypassing the graceful `logging.warning` fallback.
- **Fix:** Validate `settings.db_path` exists and is a string before instantiating `DbConnection`.

## Verdict

ISSUES FOUND

*Stopped: reached MaxIterations (3). Reverting to best version (iter 3, HIGH:1 MED:4).*

---

**Final status:** MAX_ITER
**Iterations run:** 3
**Best iteration:** 3 (HIGH:1 MED:4 LOW:2)
**Remaining (best):** HIGH:1  MED:4  LOW:2
**Fixed file:** `bug_fixes/src/nmon/history.py` (content from iteration 3)
**Written back to source:** no (review `bug_fixes/src/nmon/history.py` and copy manually)
