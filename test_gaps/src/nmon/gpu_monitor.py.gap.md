# src/nmon/gpu_monitor.py

## Overall
PARTIAL - Tests cover basic functionality and some error paths, but miss critical initialization and multi-GPU scenarios.

## Untested Public Interface
- `GpuSnapshot`: Dataclass constructor not directly tested, relies on implicit validation
- `GpuMonitorProtocol`: Abstract base class with no concrete implementations tested

## Untested Error Paths
- Condition: GPU count retrieval failure when pynvml init succeeds
- Condition: Memory info retrieval failure with valid GPU handle
- Condition: Power usage retrieval failure with valid GPU handle
- Condition: Power limit retrieval failure with valid GPU handle
- Condition: Temperature retrieval failure with valid GPU handle

## Fixture and Mock Quality
- `mock_pynvml`: Only patches specific functions, doesn't mock pynvml module state or global variables
- `mock_gpu_snapshot`: Doesn't test edge cases like zero memory values or negative temperatures

## Broken or Misleading Tests
- `test_poll_raises_no_exceptions_when_gpu_metrics_are_accessible`: Tests that no exceptions are raised but doesn't validate actual data correctness

## Priority Gaps
1. [HIGH] Test GPU count retrieval failure after successful pynvml init - could cause silent data loss
2. [HIGH] Test multiple GPUs with mixed success/failure scenarios - critical for production monitoring
3. [MEDIUM] Test memory info failure with valid GPU handle - could skip valid GPU data
4. [MEDIUM] Test power usage and limit failures with valid GPU handle - could report zero values incorrectly
5. [LOW] Test temperature failure with valid GPU handle - could report 0.0 instead of proper fallback
