# src/nmon/db.py

## Findings

### Missing error handling for database connection failure [HIGH]
- **Where:** `init_db()` ~lines 15-16, `prune_old_data()` ~lines 27-28, `flush_to_db()` ~lines 40-41
- **Issue:** Database connection failures are caught but not properly handled - the function may proceed with a None connection.
- **Impact:** If `sqlite3.connect()` fails, subsequent cursor operations will raise AttributeError, crashing the application.
- **Fix:** Check if `conn` is None after `sqlite3.connect()` and raise an appropriate exception.

### Inconsistent exception handling in flush_to_db [MEDIUM]
- **Where:** `flush_to_db()` ~lines 48-50
- **Issue:** The function catches all exceptions but only logs a warning and returns silently, potentially losing data.
- **Impact:** If database write fails, the data is lost without any recovery mechanism or user notification.
- **Fix:** Re-raise the exception or implement a retry mechanism with proper error reporting.

### Potential resource leak in prune_old_data [MEDIUM]
- **Where:** `prune_old_data()` ~lines 27-37
- **Issue:** If `conn.commit()` fails, the connection may not be closed properly in the finally block.
- **Impact:** Database connection may remain open, leading to resource exhaustion over time.
- **Fix:** Ensure connection is closed even if commit fails by moving the close operation to a more robust location or using context managers.

## Verdict

ISSUES FOUND
