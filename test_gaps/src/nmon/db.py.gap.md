# src/nmon/db.py

## Overall
PARTIAL - Tests cover basic functionality but miss critical error handling and database connection scenarios.

## Untested Public Interface
- `init_db`: Missing tests for connection failures during table creation, missing table schema validation
- `prune_old_data`: No tests for connection failures during pruning, missing validation of history_hours parameter
- `flush_to_db`: No tests for connection failures during data insertion, missing validation of snapshot data types

## Untested Error Paths
- Condition: Database connection fails in `init_db` - no test verifies exception handling
- Condition: Database connection fails in `prune_old_data` - no test verifies warning logging and graceful return
- Condition: Database connection fails in `flush_to_db` - no test verifies warning logging and graceful return
- Condition: Invalid timestamp values in snapshots - no test verifies data integrity validation
- Condition: Empty snapshot lists - no test verifies behavior with empty GPU snapshot lists

## Fixture and Mock Quality
- `mock_db_connection`: Bypasses actual SQLite behavior including transaction handling, commit/rollback semantics, and connection lifecycle management that could hide bugs in real database operations

## Broken or Misleading Tests
- `test_init_db_creates_tables_if_not_exists`: Table schema in test doesn't match actual source (uses old column names)
- `test_prune_old_data_removes_old_rows`: Uses old table schema in INSERT statements that don't match actual source
- `test_flush_to_db_inserts_gpu_snapshots`: Uses old column names in INSERT statements that don't match actual source

## Priority Gaps
1. [HIGH] Test database connection failures in all three functions to ensure proper error handling and logging
2. [HIGH] Validate that `prune_old_data` correctly handles negative history_hours values
3. [MEDIUM] Test `flush_to_db` with empty GPU snapshot lists to verify graceful handling
4. [MEDIUM] Verify that `init_db` properly handles database corruption scenarios
5. [LOW] Test edge cases with timestamp values that might cause SQLite insertion errors
