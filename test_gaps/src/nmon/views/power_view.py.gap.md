# src/nmon/views/power_view.py

## Overall
PARTIAL - Tests cover basic rendering scenarios but miss critical error conditions and edge cases in data handling.

## Untested Public Interface
- `PowerView.__init__`: Constructor logic for handling None ollama_snapshot and different time range scenarios not tested
- `PowerView._render_gpu_charts`: Method that processes historical power data and creates sparklines lacks tests for empty data, single vs multiple GPUs, and various data structures
- `PowerView._render_ollama_info`: Method that formats Ollama data into a table has no tests for None values or edge cases in snapshot data

## Untested Error Paths
- Condition: `history_store.get_power_history()` could raise exceptions when querying invalid GPU IDs or time ranges - no tests verify error handling
- Condition: Empty `gpu_snapshots` list could cause index errors in `_render_gpu_charts` - no tests cover this scenario
- Condition: `power_draw_w` or `power_limit_w` being None in historical data could cause rendering issues - only partially tested
- Condition: `ollama_snapshot` with None values in fields like `loaded_model` or `gpu_use_pct` - no tests verify graceful handling

## Fixture and Mock Quality
- `mock_history_store`: Uses MagicMock without verifying actual method signatures or behavior, could miss interface mismatches
- `mock_gpu_snapshot`: Default fixture doesn't test edge cases like negative power values or extreme temperature readings
- `mock_ollama_snapshot`: Default fixture doesn't test None values in optional fields that could be None in real data

## Broken or Misleading Tests
- `test_powerview_render_missing_power_limit`: Tests with None power_limit_w but doesn't verify actual power draw handling in sparklines
- `test_powerview_render_empty_history`: Tests empty history but doesn't verify that empty sparklines render correctly
- `test_powerview_render`: Tests basic functionality but doesn't validate actual layout structure or content

## Priority Gaps
1. [HIGH] Test handling of empty GPU snapshot lists in `_render_gpu_charts` - could cause IndexError in production
2. [HIGH] Test exception handling when `history_store.get_power_history()` fails - could crash dashboard
3. [MEDIUM] Test `_render_ollama_info` with None values in Ollama snapshot fields - could cause rendering errors
4. [MEDIUM] Test `_render_gpu_charts` with empty power history data - sparkline rendering behavior not verified
5. [LOW] Test constructor with None ollama_snapshot - edge case not covered by existing tests
