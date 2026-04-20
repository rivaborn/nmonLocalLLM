# Module: `src/nmon/gpu_monitor.py`

## Role
Provides GPU monitoring functionality using NVML to collect hardware metrics and expose them through a standardized interface.

## Contract: `GpuSnapshot`

### `__init__(params)`
- **Requires:** All parameters must be of exact types: `gpu_index` (int), `timestamp` (float), `temperature_c` (float), `mem_junction_temp_c` (Optional[float]), `memory_used_mb` (float), `memory_total_mb` (float), `power_draw_w` (float), `power_limit_w` (float)
- **Establishes:** Object holds all provided values in corresponding fields; no invariants beyond field assignment
- **Raises:** None

## Contract: `GpuMonitorProtocol`

### `__init__(params)`
- **Requires:** None
- **Establishes:** None
- **Raises:** None

### `poll() -> List[GpuSnapshot]`
- **Requires:** None
- **Guarantees:** Returns a list of `GpuSnapshot` objects; empty list if no GPUs or initialization fails
- **Raises:** None
- **Silent failure:** Returns empty list if pynvml initialization fails or if any GPU operation fails; individual GPU data may be missing or zeroed
- **Thread safety:** Unsafe

## Contract: `poll() -> List[GpuSnapshot]`

### `poll() -> List[GpuSnapshot]`
- **Requires:** None
- **Guarantees:** Returns a list of `GpuSnapshot` objects; empty list if no GPUs or initialization fails
- **Raises:** None
- **Silent failure:** Returns empty list if pynvml initialization fails or if any GPU operation fails; individual GPU data may be missing or zeroed
- **Thread safety:** Unsafe

## Module Invariants
Module maintains a global flag `_pynvml_initialized` to track NVML initialization state; pynvml is initialized only once per session.

## Resource Lifecycle
NVML library is initialized once globally via `pynvml.nvmlInit()`; handles are acquired per GPU but not explicitly released; no explicit cleanup occurs.
