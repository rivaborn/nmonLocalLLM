# Module: `src/nmon/gpu/protocol.py`

## Role
Defines the interface contract for GPU monitoring components, specifying the expected methods and data structures for GPU metric collection.

## Contract: `GpuSample`

### `__init__(params)`
- **Requires:** All parameters must be of exact specified types: `timestamp: float`, `gpu_index: int`, `temperature_gpu: float`, `temperature_mem_junction: float | None`, `memory_used_mib: float`, `memory_total_mib: float`, `power_draw_w: float`, `power_limit_w: float`
- **Establishes:** Immutable dataclass instance with frozen fields; all fields are set to provided values
- **Raises:** `TypeError` — if any parameter is of incorrect type

## Contract: `GpuMonitorProtocol`

### `start() -> None`
- **Requires:** None
- **Guarantees:** None
- **Raises:** `RuntimeError` — if monitor is already started
- **Silent failure:** None
- **Thread safety:** unsafe

### `stop() -> None`
- **Requires:** None
- **Guarantees:** None
- **Raises:** `RuntimeError` — if monitor is not started
- **Silent failure:** None
- **Thread safety:** unsafe

### `_poll() -> List[GpuSample]`
- **Requires:** Monitor must be in started state
- **Guarantees:** Returns list of GPU samples; each sample contains valid numeric values
- **Raises:** `RuntimeError` — if monitor is not started
- **Silent failure:** None
- **Thread safety:** unsafe

### `_supports_mem_junction(handle) -> bool`
- **Requires:** `handle` must be a valid NVML device handle
- **Guarantees:** Returns boolean indicating memory junction temperature support
- **Raises:** `TypeError` — if `handle` is not of expected type
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
