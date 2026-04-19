# Module: `src/nmon/ui/llm_tab.py`

## Role
Provides a Textual widget for displaying LLM server GPU/CPU utilization metrics in a time-series chart with configurable time ranges.

## Contract: `LlmTab`

### `__init__(config: AppConfig, buffer: RingBuffer[LlmSample]) -> None`
- **Requires:** `config` must be a valid `AppConfig` instance with `poll_interval_s` attribute; `buffer` must be a valid `RingBuffer[LlmSample]` instance
- **Establishes:** Initializes widget with ID "llm-tab", sets up time-range buttons, creates empty chart data structures, and configures default 1-hour time range
- **Raises:** `AttributeError` — if `config` lacks `poll_interval_s` attribute or `buffer` lacks `since` method

### `compose() -> ComposeResult`
- **Requires:** None
- **Guarantees:** Returns a `ComposeResult` yielding time-range buttons and plot widget
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe

### `on_mount() -> None`
- **Requires:** Widget must be mounted in Textual app context
- **Guarantees:** Registers config change handler and starts periodic chart update timer
- **Raises:** `AttributeError` — if `config` lacks `subscribe` method or `set_interval` fails
- **Silent failure:** None
- **Thread safety:** Requires external lock (Textual app context)

### `update_chart() -> None`
- **Requires:** `self.buffer` must support `since()` method returning iterable of `LlmSample` with `timestamp`, `size`, and `size_vram` attributes
- **Guarantees:** Updates internal chart data series and Plot widget with current samples within selected time range
- **Raises:** `AttributeError` — if `LlmSample` lacks required attributes (`timestamp`, `size`, `size_vram`)
- **Silent failure:** None
- **Thread safety:** Safe

### `on_button_pressed(event: ButtonPressed) -> None`
- **Requires:** `event.button.id` must start with "time-" prefix; `self.time_ranges` must contain matching label
- **Guarantees:** Updates selected time range, changes button selection classes, and triggers chart update
- **Raises:** `AttributeError` — if `event.button` lacks `id` or `label` attributes
- **Silent failure:** None
- **Thread safety:** Safe

### `_on_config_change() -> None`
- **Requires:** `self.config` must support `subscribe()` and `poll_interval_s` attribute
- **Guarantees:** Restarts periodic timer with new interval
- **Raises:** `AttributeError` — if `config` lacks required methods or attributes
- **Silent failure:** None
- **Thread safety:** Requires external lock (Textual app context)

## Module Invariants
- `self.time_ranges` always contains exactly 4 tuples of (label: str, seconds: int)
- `self.selected_range` always corresponds to a value in `self.time_ranges`
- `self.plot` is always initialized with title "LLM Utilization" and axis labels
- Chart data series (`gpu_series`, `cpu_series`) are always updated together
