# src/nmon/history.py

## Overall
PARTIAL - Tests cover basic functionality but miss critical error handling, database integration, and edge cases in history management.

## Untested Public Interface
- `HistoryStore.__init__`: No test covers the case where DB connection fails or query results are malformed
- `HistoryStore.add_gpu_samples`: No test covers the flush_to_db path when DB write fails
- `HistoryStore.gpu_stat`: No test covers the "current" stat type with empty series
- `HistoryStore.flush_to_db`: No test covers transaction rollback or partial insert failures

## Untested Error Paths
- Condition: Database connection failure during `__init__` - logging warning but continuing with empty data
- Condition: Database write failure in `add_gpu_samples` - logging warning but continuing
- Condition: Invalid `stat` parameter in `gpu_stat` - should raise ValueError but no test validates this
- Condition: Malformed DB query results in `__init__` - no error handling for missing columns or invalid data
- Condition: Transaction rollback in `flush_to_db` - no test covers partial success/failure scenarios

## Fixture and Mock Quality
- `mock_history_store`: Returns MagicMock without actual HistoryStore behavior, potentially hiding issues with real method signatures
- `mock_db_connection`: Mocks sqlite3.connect but doesn't verify actual DB operations or transaction behavior

## Broken or Misleading Tests
- `test_history_store_init`: Tests that `history.settings == settings` but `HistoryStore` stores `self._settings`, not `self.settings`
- `test_flush_to_db`: Mocks `src.nmon.db.flush_to_db` instead of the actual `HistoryStore.flush_to_db` method
- `test_add_gpu_samples`: Uses `settings.poll_interval` instead of `settings.poll_interval_s` in the code
- `test_add_ollama_sample`: Uses `settings.poll_interval` instead of `settings.poll_interval_s` in the code

## Priority Gaps
1. [HIGH] Test database connection failure in `__init__` - could silently continue with empty history
2. [HIGH] Test `gpu_stat` with invalid stat type - could raise untested ValueError
3. [HIGH] Test `flush_to_db` transaction rollback - could miss data consistency issues
4. [MEDIUM] Test malformed DB query results in `__init__` - could crash on missing columns
5. [MEDIUM] Test `add_gpu_samples` DB flush failure - could miss silent data loss
