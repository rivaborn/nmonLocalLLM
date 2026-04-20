# Iteration Log: src/nmon/app.py

Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.
Analysis: bugs, dataflow, contracts
Max iterations: 3
Started: 2026-04-19 22:54:14

## Iteration 1

**Severity:** HIGH:3  MED:7  LOW:0
**Best so far:** iter 1 (HIGH:3 MED:7)

## Bug Analysis

# src/nmon/app.py

## Findings

### Missing Event Handler Invocation [HIGH]
- **Where:** `_event_loop()`
- **Issue:** `_handle_event()` is defined but never called within the event loop, so keyboard input is completely ignored.
- **Impact:** Users cannot navigate views, adjust settings, or quit the application via keyboard.
- **Fix:** Read input inside the loop and call `await self._handle_event(event)` after each poll cycle.

### Lost Background Task Reference [MEDIUM]
- **Where:** `start()` / `stop()`
- **Issue:** `event_task` is created via `asyncio.create_task()` but not stored as an instance variable, making it impossible to cancel in `stop()`.
- **Impact:** The background event loop continues running after `stop()` is called, causing resource leaks or unhandled async errors.
- **Fix:** Store the task as `self.event_task = asyncio.create_task(...)` and call `self.event_task.cancel()` in `stop()`.

### State Object Reassignment Desync [MEDIUM]
- **Where:** `_event_loop()` and `_handle_event()`
- **Issue:** `self.alert_state` and `self.prefs` are reassigned to new objects instead of mutating existing ones.
- **Impact:** `AlertBar` and other components initialized with the original references will not see updates, causing stale UI data.
- **Fix:** Mutate existing objects in-place (e.g., `self.alert_state.update(...)`) or ensure all components read from `self.alert_state`/`self.prefs` dynamically.

### Unhandled Poll Exceptions [MEDIUM]
- **Where:** `_poll_all()`
- **Issue:** `self.gpu_monitor.poll()` and `self.ollama_monitor.poll()` are called without error handling.
- **Impact:** If a monitor fails (e.g., GPU disconnected or Ollama unreachable), the entire event loop crashes, stopping the dashboard.
- **Fix:** Wrap poll calls in `try/except` blocks, log errors, and return default/empty snapshots to keep the UI alive.

## Verdict
ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/app.py`

## Findings

### Shared AlertState Reference Broken [HIGH]
- **Where:** `_event_loop`
- **Issue:** `self.alert_state` is reassigned to a new object returned by `compute_alert`, severing the reference to the original `AlertState` instance injected at initialization.
- **Impact:** `AlertBar` (initialized with the original instance) will display stale alert data while the app logic uses the new instance, causing silent state divergence and potential alert data loss.
- **Fix:** Mutate the existing `self.alert_state` object in place or pass it to `compute_alert` for in-place updates instead of reassigning the instance variable.

### Shared UserPrefs Reference Broken [MEDIUM]
- **Where:** `_handle_event`
- **Issue:** `self.prefs` is reassigned to a new object returned by `update_temp_prefs`, breaking the link to the original `UserPrefs` instance passed at init.
- **Impact:** Other components or background tasks holding a reference to the original `prefs` will read stale configuration, leading to misaligned rendering or ignored user settings.
- **Fix:** Update fields on the existing `self.prefs` object directly or ensure all components consistently use the updated reference.

### Synchronous GPU Poll Blocks Async Data Flow [MEDIUM]
- **Where:** `_poll_all`
- **Issue:** `self.gpu_monitor.poll()` is called synchronously within an async method, blocking the event loop during data collection.
- **Impact:** Blocks downstream data ingestion, alert computation, and UI rendering, causing cascading latency that can drop samples or freeze the TUI during heavy GPU polling.
- **Fix:** Run `self.gpu_monitor.poll()` in a thread pool executor (`asyncio.to_thread`) to keep the event loop non-blocking and maintain steady data flow.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/app.py`

## Findings

### Background Task Not Cancelled on Stop [HIGH]
- **Where:** `NmonApp.stop` method
- **Issue:** The `event_task` created in `start()` is never stored or cancelled in `stop()`, violating the lifecycle contract that promises to halt background processing.
- **Impact:** The event loop continues running after `stop()` is called, potentially accessing stopped resources (like `self.live`) or causing unhandled async exceptions.
- **Fix:** Store the task reference in `start()` and call `task.cancel()` followed by `await task` in `stop()`.

### Alert State Reference Reassignment [MEDIUM]
- **Where:** `NmonApp._event_loop` method
- **Issue:** `self.alert_state = compute_alert(...)` reassigns the instance attribute instead of mutating the original `AlertState` object passed to `__init__`.
- **Impact:** External code holding a reference to the original `alert_state` will not see updated alerts, breaking the shared-state contract.
- **Fix:** Mutate the existing `alert_state` object in-place or ensure `compute_alert` updates it directly.

### Unchecked Live Rendering Lifecycle [MEDIUM]
- **Where:** `NmonApp.start` and `NmonApp.stop` methods
- **Issue:** `self.live.start()` is called unconditionally in `start()`, and `self.live.stop()` in `stop()`, without verifying the current state of the `Live` context manager.
- **Impact:** Calling `start()` multiple times or calling `stop()` without a prior successful `start()` can raise `RuntimeError` or leave the TUI in a corrupted state.
- **Fix:** Guard `self.live.start()` with a state check or use a context manager, and ensure `stop()` only calls `self.live.stop()` if `start()` succeeded.

## Verdict
ISSUES FOUND

**Fix applied.** Lines: 223 -> 238

## Iteration 2

**Severity:** HIGH:5  MED:5  LOW:2
**Best so far:** iter 1 (HIGH:3 MED:7)
**Non-improving streak:** 1 / 2

## Bug Analysis

# src/nmon/app.py

## Findings

### Blocking I/O in Async Event Loop [HIGH]
- **Where:** `_event_loop()` ~line 185
- **Issue:** `readchar.readkey()` is a synchronous, blocking call that halts the entire asyncio event loop until a key is pressed.
- **Impact:** The UI freezes completely between keypresses; `asyncio.sleep` and background tasks cannot run concurrently as intended.
- **Fix:** Wrap in `await asyncio.to_thread(readchar.readkey)` or switch to a non-blocking async keyboard library.

### Missing Live UI Refresh [HIGH]
- **Where:** `_render_current_view()` ~line 150-175
- **Issue:** The code mutates `self.layout` in place but never calls `self.live.update()` or `self.live.refresh()` to notify Rich's `Live` renderer.
- **Impact:** The dashboard will not redraw on screen; users will see a static or blank screen despite logic executing.
- **Fix:** Call `self.live.update(self.layout)` or `self.live.refresh()` after updating the layout.

### Silent Exception Swallowing in Polling [MEDIUM]
- **Where:** `_poll_all()` ~line 95-105
- **Issue:** Broad `except Exception: pass` clauses silently discard GPU/Ollama monitor failures, returning empty lists or `None`.
- **Impact:** Real hardware or service errors are hidden, making debugging impossible and potentially causing downstream `None`/empty data crashes.
- **Fix:** Log the exception at least, or re-raise after setting a fallback, and validate return types before use.

### Broken Arrow Key Navigation Strings [MEDIUM]
- **Where:** `_handle_event()` ~line 115-117
- **Issue:** String literals `â†` and `â†’` appear to be mojibake (UTF-8 arrows). `readchar` returns raw terminal input bytes/chars, which rarely match these exact strings.
- **Impact:** Left/Right navigation will never trigger, leaving the user stuck on the initial view.
- **Fix:** Use `readchar`'s built-in constants (e.g., `readchar.KEY_LEFT`) or compare against raw escape sequences (`\x1b[D`).

### Potential DB Data Loss on Crash [LOW]
- **Where:** `stop()` ~line 75-80
- **Issue:** `sqlite3.connect()` is called synchronously in an async function, and `flush_to_db` is assumed to handle commits.
- **Impact:** If `flush_to_db` doesn't explicitly commit, or if the process crashes before `db.close()`, recent metrics are lost.
- **Fix:** Ensure `flush_to_db` calls `db.commit()`, or use `aiosqlite` for async DB operations.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/app.py`

## Findings

### Silent Exception Swallowing in Polling [HIGH]
- **Where:** `_poll_all`
- **Issue:** Catches all exceptions from `gpu_monitor.poll()` and `ollama_monitor.poll()` and returns empty list or `None`, silently discarding the original error context.
- **Impact:** Downstream components receive invalid/empty data without knowing a failure occurred, leading to silent data loss or incorrect alert states.
- **Fix:** Propagate exceptions or return a failure status tuple, and check for success before updating history or alerts.

### Unvalidated `None` Snapshot Passed to Alert & History Modules [MEDIUM]
- **Where:** `_event_loop`
- **Issue:** `ollama_snapshot` can be `None` from `_poll_all`, but is passed directly to `self.history_store.add_ollama_sample()` and `compute_alert()` without null checks.
- **Impact:** Type mismatch or `AttributeError` if downstream expects a valid `OllamaSnapshot`, or stale alert state if `compute_alert` mishandles `None`.
- **Fix:** Validate `ollama_snapshot is not None` before passing to history and alert computation, or handle `None` explicitly.

### Blocking I/O in Async Loop Causes Stale Data Updates [MEDIUM]
- **Where:** `_event_loop`
- **Issue:** `readchar.readkey()` is a synchronous blocking call executed after `asyncio.sleep()`, halting the event loop until a key is pressed.
- **Impact:** UI rendering and metric polling are frozen during key reads, causing stale dashboard data and missed poll intervals.
- **Fix:** Run `readchar.readkey()` in a thread executor via `asyncio.to_thread()` or use an async-compatible input library.

### Unvalidated History Sample Passed to View Renderer [LOW]
- **Where:** `_render_current_view`
- **Issue:** `self.history_store.get_ollama_sample()` may return `None` if no data exists, but is passed directly to `render_llm_view` without validation.
- **Impact:** View renderer may crash or render blank/incorrect UI if it assumes a valid snapshot object is always provided.
- **Fix:** Provide a default empty snapshot or check for `None` before rendering.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/app.py`

## Findings

### None Returned Where Non-None Guaranteed [HIGH]
- **Where:** `NmonApp._poll_all`
- **Issue:** The method signature and docstring promise `OllamaSnapshot` but returns `None` when polling fails, violating the postcondition.
- **Impact:** Downstream callers like `add_ollama_sample` and `compute_alert` receive `None` and may raise `AttributeError` or process invalid state.
- **Fix:** Update the return type to `Optional[OllamaSnapshot]` and either propagate the exception or ensure a valid snapshot is always constructed.

### Silent Contract Break via Exception Swallowing [MEDIUM]
- **Where:** `NmonApp._poll_all`
- **Issue:** Catches and discards all exceptions from GPU and Ollama monitors, silently returning empty/default data instead of signaling failure.
- **Impact:** The dashboard displays stale or missing metrics without any error indication, breaking the implicit contract of a monitoring poller.
- **Fix:** Log the exception, return a failure sentinel, or re-raise to allow the caller to handle the polling failure appropriately.

### Async Non-Blocking Contract Violation [HIGH]
- **Where:** `NmonApp._event_loop`
- **Issue:** Calls synchronous blocking `readchar.readkey()` directly inside an `async def`, violating the event loop's non-blocking contract.
- **Impact:** Blocks the entire application event loop, causing UI freezes, missed render cycles, and unresponsive dashboard.
- **Fix:** Run `readchar.readkey()` via `asyncio.to_thread()` or switch to an async-compatible terminal input library.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 238 -> 241

## Iteration 3

**Severity:** HIGH:1  MED:9  LOW:2
**Best so far:** iter 3 (HIGH:1 MED:9)

## Bug Analysis

# src/nmon/app.py

## Findings

### Silent metric polling failures [HIGH]
- **Where:** `_poll_all()` ~line 98-106
- **Issue:** Broad `except Exception: pass` clauses swallow all errors from `gpu_monitor.poll()` and `ollama_monitor.poll()`.
- **Impact:** If a monitor crashes or raises an error, the app continues silently with empty/None data, masking hardware or service failures without alerting the user.
- **Fix:** Catch specific exceptions, log them, or propagate them so the dashboard can indicate a connection loss.

### Invalid key comparison for Ctrl+Q [MEDIUM]
- **Where:** `_handle_event()` ~line 118
- **Issue:** `readchar.readkey()` returns raw escape sequences (e.g., `\x11`), not the literal string `"Ctrl+Q"`. The condition will never match.
- **Impact:** The quit shortcut fails; users must press 'q' or force-kill the process.
- **Fix:** Compare against `readchar.KEY_CTRL_Q` or the raw escape sequence `\x11` instead of the string `"Ctrl+Q"`.

### Blocking input delays shutdown and poll timing [MEDIUM]
- **Where:** `_event_loop()` ~line 168-170
- **Issue:** `asyncio.sleep()` is called before `asyncio.to_thread(readchar.readkey)`. The loop sleeps for the full interval, then blocks indefinitely waiting for a key. `stop()` sets `_running = False`, but the loop only checks it after the blocking read returns.
- **Impact:** UI feels unresponsive; effective poll interval becomes `interval + time_to_press_key`; graceful shutdown hangs until a key is pressed.
- **Fix:** Read input first with a timeout (`asyncio.wait_for`), then sleep. Check `self._running` before initiating blocking reads.

### Missing explicit DB commit on shutdown [MEDIUM]
- **Where:** `stop()` ~line 78-82
- **Issue:** `sqlite3.connect()` defaults to deferred transactions in Python 3.10/3.11. The code relies on `flush_to_db` to commit, but if it doesn't, data is lost.
- **Impact:** History metrics may be silently dropped on exit if the underlying store doesn't explicitly commit.
- **Fix:** Explicitly call `db.commit()` before `db.close()`, or wrap the connection in a context manager that handles commits/rollbacks.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/app.py`

## Findings

### Unchecked GPU monitor return type [MEDIUM]
- **Where:** `_poll_all`
- **Issue:** `self.gpu_monitor.poll()` is assigned directly to `gpu_snapshots` without verifying it returns a list. If it returns `None` or another iterable, `add_gpu_samples` will ingest invalid data.
- **Impact:** Silent data corruption in the history store or unhandled `TypeError` during metric ingestion.
- **Fix:** Validate the return type or explicitly fallback to `[]` only when `poll()` raises an exception, not when it returns a falsy value.

### Unvalidated Ollama snapshot passed to views [MEDIUM]
- **Where:** `_render_current_view`
- **Issue:** `ollama_sample` (which can be `None` from `_poll_all` or `get_ollama_sample()`) is passed directly to `DashboardView` and `render_llm_view` without `None` guards or type validation.
- **Impact:** Views will crash with `AttributeError` or render blank/incorrect data when Ollama is unavailable or history is empty.
- **Fix:** Default `ollama_sample` to an empty dict or safe sentinel, or add explicit `None` checks before passing to view constructors.

### Raw `readchar` input passed without type validation [MEDIUM]
- **Where:** `_event_loop` and `_handle_event`
- **Issue:** `readchar.readkey()` output is passed directly to `_handle_event`, which assumes a string. `readchar` can return bytes or raise platform-specific exceptions on certain inputs.
- **Impact:** `TypeError` during string comparisons or silent event drops when non-string types are received.
- **Fix:** Decode bytes to string if necessary, wrap `readchar.readkey()` in a try/except, and validate the event type before routing.

### Direct mutation of settings without validation [LOW]
- **Where:** `_handle_event`
- **Issue:** `self.settings.poll_interval_s` is mutated directly via `max(0.5, ...)`. If `Settings` uses a frozen dataclass or Pydantic model, this bypasses validation and may raise delayed errors.
- **Impact:** Inconsistent configuration state or runtime validation failures when the settings object is accessed elsewhere.
- **Fix:** Use a dedicated setter method or Pydantic/dataclass validator to ensure type and range constraints are enforced.

## Verdict
ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/app.py`

## Findings

### Live Object Lifecycle Leak [MEDIUM]
- **Where:** `NmonApp.start()`
- **Issue:** If `_setup_layout()` or `_probe_ollama()` raises after `self.live.start()`, the `Live` object remains in a started state without a corresponding `stop()` call, violating the start/stop contract.
- **Impact:** Downstream cleanup fails, Rich TUI hangs or leaks terminal resources, and subsequent `start()` calls may raise `Live` state errors.
- **Fix:** Wrap `self.live.start()` in a try/finally block or use `self.live` as a context manager to guarantee `stop()` is called on any failure path.

### Missing Precondition Validation on Settings [MEDIUM]
- **Where:** `NmonApp._handle_event()`
- **Issue:** Directly mutates `self.settings.poll_interval_s` without verifying the attribute exists or is a numeric type, assuming a specific settings contract.
- **Impact:** Raises `AttributeError` or `TypeError` if the injected `settings` object lacks the attribute or uses an immutable config type, breaking the event handling contract.
- **Fix:** Validate attribute presence and type before mutation, or use `getattr` with a fallback and explicit type checking.

### Unprotected Shared State Access [MEDIUM]
- **Where:** `NmonApp.stop()` vs `NmonApp._event_loop()` / `start()`
- **Issue:** `self._live_started` and `self.live` are read/written across the async event loop and potential external `stop()` calls without synchronization.
- **Impact:** Race conditions can cause double `start()`/`stop()` calls or inconsistent UI state, violating the expected single-threaded async lifecycle contract.
- **Fix:** Guard all accesses to `_live_started` and `live` with an `asyncio.Lock` or ensure `stop()` is only invoked from the same event loop thread.

### Rich Live API Contract Mismatch [LOW]
- **Where:** `NmonApp._render_current_view()`
- **Issue:** Calls `self.live.refresh()`, but Rich's `Live` contract expects `update()` or context manager exit to trigger screen redraws; `refresh()` may not exist or behave as intended.
- **Impact:** UI may fail to update silently or raise `AttributeError`, breaking the rendering contract.
- **Fix:** Replace `self.live.refresh()` with `self.live.update()` or rely on the context manager's automatic refresh on exit.

## Verdict

ISSUES FOUND

*Stopped: reached MaxIterations (3). Reverting to best version (iter 3, HIGH:1 MED:9).*

---

**Final status:** MAX_ITER
**Iterations run:** 3
**Best iteration:** 3 (HIGH:1 MED:9 LOW:2)
**Remaining (best):** HIGH:1  MED:9  LOW:2
**Fixed file:** `bug_fixes/src/nmon/app.py` (content from iteration 3)
**Written back to source:** no (review `bug_fixes/src/nmon/app.py` and copy manually)
