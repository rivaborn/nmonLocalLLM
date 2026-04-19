# Module: `src/nmon/ui/temp_tab.py`

## Role
Implements a Textual UI tab for displaying GPU temperature data over time with interactive controls.

## Contract: `TemperatureTab`

### `__init__(gpu_monitor, config, buffer)`
- **Requires:** `gpu_monitor` must implement `GpuMonitorProtocol` with accessible `gpus` attribute; `config` must be `AppConfig` instance with `temp_threshold_visible` and `temp_threshold_c` attributes; `buffer` must be `RingBuffer[GpuSample]` instance
- **Establishes:** Initializes all internal state including plot widgets, time range buttons, and control buttons; sets initial time range to 3600 seconds; initializes visibility flags from config
- **Raises:** `AttributeError` if `gpu_monitor` lacks `gpus` attribute, `TypeError` if `buffer` is not `RingBuffer[GpuSample]`

### `compose() -> ComposeResult`
- **Requires:** None
- **Guarantees:** Returns a `ComposeResult` containing time range buttons, GPU plots, and control buttons in specified order
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `on_button_pressed(event) -> None`
- **Requires:** `event.button` must be one of the initialized control buttons (`threshold_toggle_button`, `mem_junction_toggle_button`, `threshold_adjust_up`, `threshold_adjust_down`)
- **Guarantees:** Updates internal state and config persistence when threshold toggle or adjustment buttons are pressed; calls `update_plots()` after processing
- **Raises:** `AttributeError` if config persistence methods fail, `TypeError` if config attributes are not writable
- **Silent failure:** None
- **Thread safety:** Unsafe

### `on_key(event) -> None`
- **Requires:** `event.key` must be one of "t", "h", "up", "down" for keyboard control
- **Guarantees:** Updates internal state and config persistence when keyboard shortcuts are pressed; calls `update_plots()` after processing
- **Raises:** `AttributeError` if config persistence methods fail, `TypeError` if config attributes are not writable
- **Silent failure:** None
- **Thread safety:** Unsafe

### `update_plots() -> None`
- **Requires:** `self.buffer` must be a valid `RingBuffer[GpuSample]` with `since()` method; `self.gpu_monitor.gpus` must be iterable with length matching `len(self.gpu_plots)`
- **Guarantees:** Updates all plot widgets with current GPU temperature data; clears plots when no data available; adds threshold line when visible
- **Raises:** `AttributeError` if buffer `since()` method fails, `TypeError` if sample data types are invalid
- **Silent failure:** None
- **Thread safety:** Unsafe

### `update_time_range(seconds) -> None`
- **Requires:** `seconds` must be numeric type
- **Guarantees:** Clamps `seconds` to range [3600, 86400]; updates `self.time_range_s` and calls `update_plots()`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

## Module Invariants
- `self.gpu_plots` list length equals `len(self
