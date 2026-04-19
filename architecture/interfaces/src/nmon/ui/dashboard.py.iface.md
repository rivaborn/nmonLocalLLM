# Module: `src/nmon/ui/dashboard.py`

## Role
Provides a NiceGUI-based dashboard UI tab for displaying real-time GPU and LLM monitoring data.

## Contract: `DashboardTab`

### `__init__(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)`
- **Requires:** `config` must be an `AppConfig` instance; `gpu_buffer` and `llm_buffer` must be `RingBuffer` instances with `GpuSample` and `LlmSample` types respectively; `gpu_monitor` must be a `GpuMonitorProtocol` instance; `llm_monitor` must be an `LlmMonitorProtocol` instance or `None`
- **Establishes:** Initializes internal state with provided parameters; creates UI container elements; sets up initial UI structure with GPU container and optional LLM container
- **Raises:** `TypeError` if any parameter has incorrect type

### `_build_initial_content()`
- **Requires:** None
- **Guarantees:** Creates initial UI structure with GPU container and optional LLM container; does not modify external state
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `_build_gpu_sections() -> None`
- **Requires:** `self.gpu_buffer` must be a valid `RingBuffer[GpuSample]` with accessible `get_all()` method
- **Guarantees:** Updates `self.gpu_sections` with new GPU section elements; clears previous sections before rebuilding; adds placeholder message if no samples available
- **Raises:** None
- **Silent failure:** If `self.gpu_buffer.get_all()` returns invalid data, may produce incorrect display values; if UI element deletion fails, sections may not be properly cleared
- **Thread safety:** Unsafe

### `_build_llm_section() -> None`
- **Requires:** `self.llm_buffer` must be a valid `RingBuffer[LlmSample]` with accessible `get_latest()` method; `self.llm_monitor` must be truthy
- **Guarantees:** Updates `self.llm_section` with new LLM section element; displays LLM metrics if data is available
- **Raises:** None
- **Silent failure:** If `self.llm_buffer.get_latest()` returns invalid data, may produce incorrect display values; if UI element creation fails, section may not be created
- **Thread safety:** Unsafe

### `_update_display() -> None`
- **Requires:** None
- **Guarantees:** Triggers rebuild of GPU and LLM sections with fresh data; handles exceptions gracefully by printing to console
- **Raises:** None
- **Silent failure:** If any internal `_build_*` methods fail, the error is caught and printed but not re-raised; UI may not update properly if exceptions occur during section rebuilding
- **Thread safety:** Unsafe

## Module Invariants
None

## Resource Lifecycle
UI elements are created during initialization and managed by NiceGUI's lifecycle. No explicit resource cleanup is performed in the class.
