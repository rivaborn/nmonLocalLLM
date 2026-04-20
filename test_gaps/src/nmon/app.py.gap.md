# src/nmon/app.py

## Overall
PARTIAL - Tests cover basic initialization, start/stop, and event handling but miss critical error paths and view rendering logic.

## Untested Public Interface
- `NmonApp.start`: No test covers the actual `_event_loop` task lifecycle or Live rendering behavior
- `NmonApp.stop`: No test verifies the exact database connection flow or task cancellation behavior
- `NmonApp._render_current_view`: No test covers the actual view rendering logic for all four view types
- `NmonApp._event_loop`: No test validates the complete event loop execution with real data flow

## Untested Error Paths
- Condition: `_probe_ollama` method doesn't test specific exception types that could occur during Ollama probing
- Condition: `stop` method doesn't test database connection failures or flush_to_db exceptions
- Condition: `_poll_all` method doesn't test GPU or Ollama monitor failures during polling
- Condition: `_handle_event` doesn't test invalid view index navigation or boundary conditions
- Condition: `_event_loop` doesn't test alert computation failures or rendering exceptions

## Fixture and Mock Quality
- `mock_history_store`: Uses MagicMock without verifying actual HistoryStore interface compliance
- `mock_ollama_monitor.probe`: Mocks return value but doesn't test different probe outcomes
- `mock_gpu_monitor.poll`: Mocks return value but doesn't test different polling scenarios

## Broken or Misleading Tests
- `test_nmon_app_render_current_view`: Tests mock view rendering but doesn't verify actual view construction logic
- `test_nmon_app_event_loop`: Uses `asyncio.sleep(0)` which bypasses real timing behavior and doesn't validate actual polling intervals

## Priority Gaps
1. [HIGH] Test `_probe_ollama` with specific exception types to ensure robust error handling
2. [HIGH] Test `stop` method with database connection failures to prevent data loss
3. [HIGH] Test `_poll_all` with monitor polling failures to ensure graceful degradation
4. [MEDIUM] Test all four view rendering paths in `_render_current_view` with real data
5. [MEDIUM] Test `_event_loop` with actual alert computation and rendering to validate complete data flow
