# src/nmon/app.py

## Findings

### Unhandled Exception in Ollama Probe [HIGH]
- **Where:** `_probe_ollama()` ~line 74
- **Issue:** The `probe()` method call is wrapped in a bare `except:` clause that silently catches all exceptions and sets `self.ollama_detected = False`.
- **Impact:** If `probe()` raises an unexpected exception (e.g., network timeout, permission error), the application will incorrectly assume Ollama is not available, potentially disabling features or showing incorrect UI state.
- **Fix:** Catch specific exceptions that are expected from `probe()` rather than using a bare `except:` clause.

### Resource Leak in Stop Method [HIGH]
- **Where:** `stop()` ~line 44
- **Issue:** The database connection is opened but not properly managed with a context manager, and there's no error handling for the flush operation.
- **Impact:** If `flush_to_db()` fails or `db.close()` raises an exception, the database connection may not be properly closed, leading to resource leaks or inconsistent state.
- **Fix:** Use a context manager (`with sqlite3.connect(...)`) for the database connection and handle potential exceptions during flush.

### Missing Task Cancellation in Stop Method [MEDIUM]
- **Where:** `stop()` ~line 44
- **Issue:** The background task created in `start()` is not cancelled when stopping the application.
- **Impact:** The event loop task continues running even after `stop()` is called, potentially causing memory leaks or unexpected behavior.
- **Fix:** Store the task reference and cancel it in `stop()` using `task.cancel()`.

### Potential None Dereference in Poll All [LOW]
- **Where:** `_poll_all()` ~line 87
- **Issue:** The `poll()` method on `self.gpu_monitor` returns `List[GpuSnapshot]` but there's no validation that it's not `None`.
- **Impact:** If `poll()` returns `None`, subsequent code may fail with a `TypeError` when trying to iterate over it.
- **Fix:** Add a check to ensure `gpu_snapshots` is not `None` before using it.

### Race Condition in View Switching [LOW]
- **Where:** `_handle_event()` ~line 60
- **Issue:** The view index is updated without synchronization, and the view rendering logic assumes the current view index is valid.
- **Impact:** In a multi-threaded environment, concurrent access to `current_view_index` could lead to inconsistent view rendering.
- **Fix:** Add thread synchronization (e.g., using a lock) when updating `current_view_index`.

## Verdict

ISSUES FOUND
