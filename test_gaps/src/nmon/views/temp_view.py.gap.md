# src/nmon/views/temp_view.py

## Overall
PARTIAL - Tests cover basic functionality but miss critical error handling and preference update scenarios.

## Untested Public Interface
- `render_temp_view`: Missing tests for Ollama snapshot handling and edge cases with GPU data
- `update_temp_prefs`: No tests for key="0" through key="9" numeric input handling, missing tests for None threshold cases

## Untested Error Paths
- Condition: `history_store.gpu_series()` raises exception during temperature data retrieval
- Condition: `history_store.gpu_mem_series()` raises exception when memory junction data is requested
- Condition: `prefs.temp_threshold_c` is None and key="up" or key="down" is pressed
- Condition: `prefs.temp_threshold_c` is not None but arithmetic operations fail

## Fixture and Mock Quality
- `mock_history_store`: Returns fixed data instead of simulating real-time data series behavior
- `mock_user_prefs`: Uses Mock instead of actual UserPrefs instance, bypasses validation
- `mock_settings`: Uses Mock instead of actual Settings instance, bypasses validation

## Broken or Misleading Tests
- `test_update_temp_prefs_modifies_threshold_and_flags`: Tests call with incorrect parameters (90, True, False) instead of actual key strings like "up", "down", "t", "m"
- `test_render_temp_view_handles_empty_gpu_data`: Mocks history_store but doesn't test actual empty data handling in Sparkline
- `test_render_temp_view_handles_missing_gpu_data`: Tests exception handling but doesn't verify actual exception propagation

## Priority Gaps
1. [HIGH] Test `update_temp_prefs` with key="up"/"down" when `temp_threshold_c` is None
2. [HIGH] Test `render_temp_view` with empty GPU samples list
3. [MEDIUM] Test `render_temp_view` with `history_store.gpu_series()` raising exception
4. [MEDIUM] Test `render_temp_view` with `history_store.gpu_mem_series()` raising exception
5. [LOW] Test `update_temp_prefs` with numeric key inputs (0-9)
