# src/nmon/alerts.py

## Overall
POOR - Tests cover the AlertState dataclass but completely miss the core `compute_alert` function logic and all conditional branches.

## Untested Public Interface
- `compute_alert`: The main function that determines alert state is entirely untested. This function contains the core business logic for when alerts should be triggered and how they should be colored.

## Untested Error Paths
- Condition: `compute_alert` function does not test the case where `snapshot.reachable` is False - should return None
- Condition: `compute_alert` function does not test the case where `snapshot.gpu_use_pct` is None - should return None  
- Condition: `compute_alert` function does not test the case where `snapshot.gpu_use_pct >= 100` - should return None
- Condition: `compute_alert` function does not test the case where `snapshot.gpu_layers is None` - should return None
- Condition: `compute_alert` function does not test the case where `snapshot.gpu_use_pct > settings.offload_alert_pct` - should return "red" color

## Fixture and Mock Quality
- `mock_ollama_snapshot`: The fixture provides default values but doesn't test edge cases like None values that would trigger different code paths in compute_alert
- `mock_settings`: The fixture provides default values but doesn't test boundary conditions around offload_alert_pct

## Broken or Misleading Tests
None.

## Priority Gaps
1. [HIGH] Test `compute_alert` function with `snapshot.reachable = False` - should return None
2. [HIGH] Test `compute_alert` function with `snapshot.gpu_use_pct is None` - should return None
3. [HIGH] Test `compute_alert` function with `snapshot.gpu_use_pct >= 100` - should return None
4. [HIGH] Test `compute_alert` function with `snapshot.gpu_layers is None` - should return None
5. [MEDIUM] Test `compute_alert` function with `snapshot.gpu_use_pct > settings.offload_alert_pct` - should return "red" color
