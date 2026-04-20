# src/nmon/main.py

## Findings

### Missing error handling for prefs file read
- **Where:** `main()` ~line 22
- **Issue:** The code opens and reads the prefs file without handling potential IO errors like FileNotFoundError or PermissionError.
- **Impact:** If the prefs file is missing or inaccessible, the application crashes with an unhandled exception instead of failing gracefully.
- **Fix:** Wrap the file read operation in a try-except block to handle IO exceptions.

### Potential resource leak in signal handler
- **Where:** `signal_handler()` ~line 28
- **Issue:** The signal handler calls `sys.exit(0)` directly without ensuring proper cleanup of all resources.
- **Impact:** If `gpu_monitor.stop()` or `ollama_monitor.stop()` raise exceptions, the application may not terminate cleanly, potentially leaving GPU handles or network connections open.
- **Fix:** Wrap the cleanup operations in a try-except block and ensure `sys.exit()` is called only after all cleanup is complete or has failed gracefully.

### Exception swallowing in main try-except block
- **Where:** `main()` ~line 37
- **Issue:** The broad `except Exception as e:` clause catches all exceptions and only re-raises specific ones related to pynvml.
- **Impact:** Other unexpected exceptions during app execution will be silently ignored or improperly handled, potentially masking bugs in the application logic.
- **Fix:** Log the caught exception before re-raising, or implement more specific exception handling to prevent silent failures.

## Verdict

ISSUES FOUND
