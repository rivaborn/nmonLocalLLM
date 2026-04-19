# Module: `src/nmon/gpu/monitor.py`

## Role
GPU monitor that collects hardware metrics from NVIDIA GPUs via NVML and stores samples in a ring buffer.

## Contract: `GpuMonitor`

### `__init__(config: AppConfig, buffer: RingBuffer[GpuSample]) -> None`
- **Requires:** `config` must be a valid `AppConfig` instance with `poll_interval_s` attribute; `buffer` must be a valid `RingBuffer[GpuSample]` instance; NVML library must be available and accessible
- **Establishes:** `self.config` and `self.buffer` are set to provided values; NVML library is initialized via `pynvml.nvmlInit()`; `self.device_handles` is populated with valid device handles from `pynvml.nvmlDeviceGetHandleByIndex()` for each available GPU
- **Raises:** `pynvml.NVMLError` — if NVML initialization or device enumeration fails

### `start() -> None`
- **Requires:** `self` must be initialized; no concurrent calls to `start()` or `stop()` should be in progress
- **Guarantees:** `self.running` is set to `True`; `self.task` is set to a running asyncio task that polls GPU data
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external synchronization if called concurrently with `stop()`

### `stop() -> None`
- **Requires:** `self` must be initialized; no concurrent calls to `start()` or `stop()` should be in progress
- **Guarantees:** `self.running` is set to `False`; `self.task` is cancelled if it exists; NVML library is shut down via `pynvml.nvmlShutdown()`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external synchronization if called concurrently with `start()`

### `_poll_loop() -> None`
- **Requires:** `self.running` must be `True`; `self.buffer` must be a valid `RingBuffer[GpuSample]` instance
- **Guarantees:** Polls GPU data at intervals defined by `self.config.poll_interval_s`; samples are appended to `self.buffer`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Internal lock; safe to call from asyncio context

### `_poll() -> List[GpuSample]`
- **Requires:** `self.device_handles` must contain valid device handles; NVML functions must be callable
- **Guarantees:** Returns a list of `GpuSample` objects; if a device fails, a sentinel `GpuSample` with `None` fields is returned for that device
- **Raises:** `pynvml.NVMLError` — if NVML functions fail during data collection
- **Silent failure:** If a device fails, a sentinel `GpuSample` is returned with `None` fields; no exception is raised for individual device failures
- **Thread safety:** Safe to call from asyncio context

### `_supports_mem_junction(handle) -> bool`
- **Requires:** `handle` must be a valid `pynvml.c_nvmlDevice_t` instance
- **Guarantees:** Returns `True` if
