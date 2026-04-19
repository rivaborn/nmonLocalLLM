# Module: `src/nmon/llm/protocol.py`

## Role
Defines data structures and protocols for monitoring LLM server resource utilization.

## Contract: `LlmSample`

### `__init__(timestamp: float, model_name: str, model_size_bytes: int, gpu_utilization_pct: float, cpu_utilization_pct: float, gpu_layers_offloaded: int, total_layers: int)`
- **Requires:** `timestamp` must be a positive float; `model_name` must be a non-empty string; `model_size_bytes` must be non-negative int; `gpu_utilization_pct` and `cpu_utilization_pct` must be floats in range [0, 100]; `gpu_layers_offloaded` and `total_layers` must be non-negative ints
- **Establishes:** All fields are set to provided values; object is immutable due to `__slots__ = True`
- **Raises:** `TypeError` if any argument has incorrect type

## Contract: `LlmMonitorProtocol`

### `detect() -> bool`
- **Requires:** No external state requirements
- **Guarantees:** Returns `True` if Ollama server is reachable, `False` otherwise
- **Raises:** `Exception` -- any exception during network detection (network error, timeout, etc.)
- **Silent failure:** None
- **Thread safety:** unsafe

### `start() -> None`
- **Requires:** Monitor must not be running
- **Guarantees:** Monitor loop is started
- **Raises:** `RuntimeError` -- if monitor is already running
- **Silent failure:** None
- **Thread safety:** unsafe

### `stop() -> None`
- **Requires:** Monitor must be running
- **Guarantees:** Monitor loop is stopped
- **Raises:** `RuntimeError` -- if monitor is not running
- **Silent failure:** None
- **Thread safety:** unsafe

### `_poll() -> LlmSample | None`
- **Requires:** Monitor must be running
- **Guarantees:** Returns `LlmSample` with current data or `None` if polling failed
- **Raises:** `Exception` -- any exception during polling (network error, timeout, etc.)
- **Silent failure:** Returns `None` if polling fails
- **Thread safety:** unsafe

### `_parse_response(data: dict) -> LlmSample`
- **Requires:** `data` must be a dict containing required keys with correct types
- **Guarantees:** Returns `LlmSample` with parsed data
- **Raises:** `KeyError` -- if required keys missing from `data`; `TypeError` -- if values have incorrect types
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
