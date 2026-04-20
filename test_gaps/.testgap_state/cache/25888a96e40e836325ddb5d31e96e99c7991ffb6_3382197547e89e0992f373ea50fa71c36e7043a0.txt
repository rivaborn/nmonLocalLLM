# src/nmon/views/dashboard_view.py

## Overall
PARTIAL - Tests cover basic structure and happy path rendering but miss critical error conditions and edge cases in GPU monitoring and alert handling.

## Untested Public Interface
- `DashboardView.__init__`: No test verifies proper initialization with None alert_state or validates parameter types
- `DashboardView._create_gpu_panel`: No test covers edge cases like zero memory total or None snapshot values
- `DashboardView._create_llm_panel`: No test covers None or invalid OllamaSnapshot data scenarios

## Untested Error Paths
- Condition: GPU monitor returns empty list from poll() - no test covers empty GPU data handling
- Condition: History store returns empty lists from gpu_series() or ollama_series() - no test covers missing historical data scenarios
- Condition: AlertState is None but render() tries to access its attributes - no test covers this defensive branch
- Condition: Memory calculation division by zero when memory_total_mb = 0 - no test covers this edge case in _create_gpu_panel

## Fixture and Mock Quality
- `mock_history_store`: Uses MagicMock without verifying specific method calls, could miss incorrect usage patterns
- `mock_gpu_monitor`: Mocks poll() but doesn't verify the actual polling behavior or error conditions

## Broken or Misleading Tests
- `test_dashboard_view_render_structure`: Uses mock_gpu_snapshot in both gpu_series and ollama_series calls but doesn't validate that these are actually used for rendering
- `test_dashboard_view_panel_content_reflects_metrics`: Doesn't actually verify that panel content matches the mocked snapshot data

## Priority Gaps
1. [HIGH] Test empty GPU list from monitor - could cause crash in render() method
2. [HIGH] Test division by zero in memory percentage calculation - could silently produce wrong values
3. [MEDIUM] Test None alert_state handling - could cause AttributeError in alert bar rendering
4. [MEDIUM] Test empty history store responses - could cause rendering failures
5. [LOW] Test _create_gpu_panel with zero memory total - edge case for memory percentage calculation
