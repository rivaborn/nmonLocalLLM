# Module: `src/nmon/ui/power_tab.py`

## Role
Textual widget that displays GPU power consumption over time with interactive time range selection.

## Contract: `PowerTab`

### `__init__(config: AppConfig, buffer: RingBuffer[GpuSample])`
- **Requires:** `config` must be a valid `AppConfig` instance; `buffer` must be a `RingBuffer[GpuSample]` with valid samples
- **Establishes:** Initializes widget with default 1-hour time range, empty plots dict, and empty GPU names list
- **Raises:** `TypeError` if `config` is not `AppConfig` or `buffer` is not `RingBuffer[GpuSample]`

### `compose() -> None`
- **Requires:** `self.buffer` must contain at least one `GpuSample` with valid `power_draw_w` keys
- **Guarantees:** Returns generator yielding `Plot` widgets for each GPU and time range buttons; `self.gpu_names` populated with GPU identifiers from first sample
- **Raises:** `KeyError` if `power_draw_w` keys are missing from first sample; `AttributeError` if `self.buffer.peek(1)` fails
- **Silent failure:** None
- **Thread safety:** unsafe

### `_update_plots() -> None`
- **Requires:** `self.gpu_names` must be populated; `self.buffer` must be a valid `RingBuffer[GpuSample]`
- **Guarantees:** Updates all plot widgets with current data from buffer; sets appropriate Y-axis bounds based on power limits
- **Raises:** `KeyError` if GPU name not found in sample data; `AttributeError` if buffer access fails
- **Silent failure:** None
- **Thread safety:** unsafe

### `_format_time_label(seconds: int) -> str`
- **Requires:** `seconds` must be a non-negative integer
- **Guarantees:** Returns formatted time string in "Xh Xm Xs" format without zero-padding; handles edge case of 0 seconds
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

### `_on_time_range_change(duration: int) -> None`
- **Requires:** `duration` must be a positive integer representing seconds
- **Guarantees:** Updates `self.selected_time_range` and triggers plot update
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

### `on_mount() -> None`
- **Requires:** Widget must be properly initialized with valid buffer and config
- **Guarantees:** Triggers initial plot update when widget is mounted
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

### `on_click(event: events.Click) -> None`
- **Requires:** `event.control.id` must be properly formatted as "time_range_X" where X is integer seconds
- **Guarantees:** Handles time range button clicks and updates display
- **Raises:** `ValueError` if `event.control.id` parsing fails; `KeyError` if time range not found
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
- `self.selected_time_range` is always a positive integer representing seconds
- `self.plots`
