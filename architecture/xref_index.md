# Cross-Reference Index

Auto-generated from per-file architecture docs.

## Function Definition Map

| Function | Defined In |
|----------|-----------|
| `__all__` | `Module: `src/nmon/__init__.py`` |
| `__all__` | `Interface Contracts: nmon` |
| `__init__` | `src/nmon/ui/dashboard.py` |
| `__init__` | `Module: `src/nmon/llm/__init__.py`` |
| `__init__` | `src/nmon/ui/app.py` |
| `__init__` | `src/nmon/gpu/monitor.py` |
| `__init__` | `src/nmon/storage/ring_buffer.py` |
| `__init__` | `Module: `src/nmon/ui/__init__.py`` |
| `__init__` | `src/nmon/ui/temp_tab.py` |
| `__init__()` | `Module: `src/nmon/ui/alert_bar.py`` |
| `__init__()` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `__init__(argv: list[str]) -> None` | `Module: `src/nmon/ui/app.py`` |
| `__init__(config)` | `Module: `src/nmon/storage/ring_buffer.py`` |
| `__init__(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor) -> None` | `Module: `src/nmon/ui/dashboard.py`` |
| `__init__(config: AppConfig, buffer: RingBuffer[GpuSample]) -> None` | `Module: src/nmon/gpu/monitor.py` |
| `__init__(config: AppConfig, buffer: RingBuffer[LlmSample])` | `Module: src/nmon/llm/monitor.py` |
| `__init__(gpu_buffer, config)` | `Module: `src/nmon/ui/power_tab.py`` |
| `__init__(gpu_index: int)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `__init__(gpu_monitor, config, buffer) -> None` | `Module: `src/nmon/ui/temp_tab.py`` |
| `__init__(index: int, name: str, has_junction_temp: bool)` | `Module: src/nmon/gpu/monitor.py` |
| `__init__(params)` | `Module: `src/nmon/ui/llm_tab.py`` |
| `__init__(params)` | `Module: `src/nmon/gpu/__init__.py`` |
| `__init__(params)` | `Module: `src/nmon/gpu/protocol.py`` |
| `__init__(params)` | `Interface Contracts: nmon` |
| `__init__(params)` | `Module: `src/nmon/config.py`` |
| `__init__(params)` | `Module: `src/nmon/storage/__init__.py`` |
| `__init__(params)` | `Module: `src/nmon/ui/llm_tab.py`` |
| `__init__(parent=None)` | `Module: `src/nmon/ui/widgets/alert_bar.py`` |
| `__init__(parent=None)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `__init__(timestamp: float, gpu_index: int, gpu_name: str, temperature_c: Optional[float], memory_used_mb: Optional[float], memory_total_mb: Optional[float], power_draw_w: Optional[float], junction_temp_c: Optional[float])` | `Module: src/nmon/gpu/monitor.py` |
| `__init__(timestamp: float, model_name: str, model_size_bytes: int, gpu_utilization_pct: float, cpu_utilization_pct: float, gpu_layers_offloaded: int, total_layers: int)` | `Module: `src/nmon/llm/protocol.py`` |
| `__iter__() -> Iterator[GPUSample]` | `Module: `src/nmon/storage/__init__.py`` |
| `__len__() -> int` | `Module: `src/nmon/storage/__init__.py`` |
| `__post_init__(params)` | `Interface Contracts: nmon` |
| `__post_init__(params)` | `Module: `src/nmon/config.py`` |
| `_build_gpu_sections` | `src/nmon/ui/dashboard.py` |
| `_build_initial_content` | `src/nmon/ui/dashboard.py` |
| `_build_llm_section` | `src/nmon/ui/dashboard.py` |
| `_build_power_plot(samples, power_limit_w, time_range_seconds) -> Plot` | `Module: `src/nmon/ui/power_tab.py`` |
| `_create_main_window() -> None` | `Module: `src/nmon/ui/app.py`` |
| `_format_time_label(timestamp) -> str` | `Module: `src/nmon/ui/power_tab.py`` |
| `_get_power_limit_for_gpu(gpu_index, config) ->` | `Module: `src/nmon/ui/power_tab.py`` |
| `_increase_temp_threshold() -> None` | `Module: `src/nmon/ui/app.py`` |
| `_latest_gpu_samples(buffer) -> List[GpuSample]` | `Module: `src/nmon/ui/dashboard.py`` |
| `_on_config_change` | `src/nmon/ui/llm_tab.py` |
| `_on_hide_timeout() -> None` | `Module: `src/nmon/ui/widgets/alert_bar.py`` |
| `_on_poll_interval_changed(value: int)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `_on_time_range_change` | `src/nmon/ui/power_tab.py` |
| `_on_window_close(event) -> None` | `Module: `src/nmon/ui/app.py`` |
| `_parse_response` | `src/nmon/llm/protocol.py` |
| `_parse_response` | `src/nmon/llm/monitor.py` |
| `_parse_response(data: dict) -> LlmSample` | `Module: `src/nmon/llm/protocol.py`` |
| `_parse_response(data: Dict[str, Any]) -> Optional[LlmSample]` | `Module: src/nmon/llm/monitor.py` |
| `_poll` | `src/nmon/gpu/monitor.py` |
| `_poll` | `src/nmon/llm/protocol.py` |
| `_poll` | `src/nmon/llm/monitor.py` |
| `_poll() -> LlmSample | None` | `Module: `src/nmon/llm/protocol.py`` |
| `_poll() -> Optional[LlmSample]` | `Module: src/nmon/llm/monitor.py` |
| `_poll_all` | `src/nmon/ui/app.py` |
| `_poll_loop` | `src/nmon/gpu/monitor.py` |
| `_poll_loop` | `src/nmon/llm/monitor.py` |
| `_poll_loop() -> None` | `Module: src/nmon/llm/monitor.py` |
| `_refresh_chart() -> None` | `Module: `src/nmon/ui/llm_tab.py`` |
| `_save_config() -> None` | `Module: `src/nmon/ui/temp_tab.py`` |
| `_setup_keyboard_shortcuts() -> None` | `Module: `src/nmon/ui/app.py`` |
| `_setup_logging() -> None` | `Module: `src/nmon/ui/app.py`` |
| `_shutdown() -> None` | `Module: `src/nmon/ui/app.py`` |
| `_supports_mem_junction` | `src/nmon/gpu/monitor.py` |
| `_update_display` | `src/nmon/ui/dashboard.py` |
| `_update_plots` | `src/nmon/ui/power_tab.py` |
| `_update_style() -> None` | `Module: `src/nmon/ui/widgets/alert_bar.py`` |
| `adjust_threshold` | `src/nmon/ui/app.py` |
| `append` | `src/nmon/storage/ring_buffer.py` |
| `append(item)` | `Module: `src/nmon/storage/__init__.py`` |
| `append(sample)` | `Module: `src/nmon/storage/ring_buffer.py`` |
| `avg_field` | `src/nmon/storage/ring_buffer.py` |
| `avg_field(field, seconds)` | `Module: `src/nmon/storage/ring_buffer.py`` |
| `collect_gpu_samples(gpu_descriptors: List[GpuDescriptor]) -> List[GpuSample]` | `Module: src/nmon/gpu/monitor.py` |
| `compose` | `src/nmon/ui/temp_tab.py` |
| `compose() -> ComposeResult` | `Module: `src/nmon/ui/llm_tab.py`` |
| `compose() -> ComposeResult` | `Module: `src/nmon/ui/temp_tab.py`` |
| `compose() -> ComposeResult` | `Module: `src/nmon/ui/dashboard.py`` |
| `compose() -> ComposeResult` | `Module: `src/nmon/ui/power_tab.py`` |
| `detect` | `src/nmon/llm/monitor.py` |
| `detect` | `src/nmon/llm/protocol.py` |
| `detect() -> bool` | `Module: `src/nmon/llm/protocol.py`` |
| `detect() -> bool` | `Module: src/nmon/llm/monitor.py` |
| `enumerate_gpus() -> List[GpuDescriptor]` | `Module: src/nmon/gpu/monitor.py` |
| `get_avg_temperature(gpu_index: int, window_s: int) -> Optional[float]` | `Module: `src/nmon/storage/database.py`` |
| `get_max_temperature(gpu_index: int, window_s: int) -> Optional[float]` | `Module: `src/nmon/storage/database.py`` |
| `init_database(db_path: str) -> None` | `Module: `src/nmon/storage/database.py`` |
| `init_nvml() -> None` | `Module: src/nmon/gpu/monitor.py` |
| `insert_gpu_sample(sample: GpuSample) -> None` | `Module: `src/nmon/storage/database.py`` |
| `insert_llm_sample(sample: LlmSample) -> None` | `Module: `src/nmon/storage/database.py`` |
| `latest` | `src/nmon/storage/ring_buffer.py` |
| `latest()` | `Module: `src/nmon/storage/ring_buffer.py`` |
| `load_from_env` | `src/nmon/config.py` |
| `load_from_env() -> AppConfig` | `Module: `src/nmon/config.py`` |
| `load_persistent_settings` | `src/nmon/config.py` |
| `load_persistent_settings() -> AppConfig` | `Module: `src/nmon/config.py`` |
| `max_field` | `src/nmon/storage/ring_buffer.py` |
| `max_field(field, seconds)` | `Module: `src/nmon/storage/ring_buffer.py`` |
| `None` | `src/nmon/__init__.py` |
| `None` | `src/nmon/ui/__init__.py` |
| `None` | `src/nmon/storage/__init__.py` |
| `None` | `src/nmon/gpu/protocol.py` |
| `on_button_pressed` | `src/nmon/ui/llm_tab.py` |
| `on_button_pressed` | `src/nmon/ui/temp_tab.py` |
| `on_button_pressed(event) -> None` | `Module: `src/nmon/ui/power_tab.py`` |
| `on_button_pressed(event) -> None` | `Module: `src/nmon/ui/temp_tab.py`` |
| `on_button_pressed(event: Button.Pressed) -> None` | `Module: `src/nmon/ui/llm_tab.py`` |
| `on_click` | `src/nmon/ui/power_tab.py` |
| `on_key` | `src/nmon/ui/temp_tab.py` |
| `on_key(event) -> None` | `Module: `src/nmon/ui/temp_tab.py`` |
| `on_mount` | `src/nmon/ui/app.py` |
| `on_mount` | `src/nmon/ui/power_tab.py` |
| `on_mount() -> None` | `Module: `src/nmon/ui/llm_tab.py`` |
| `on_mount() -> None` | `Module: `src/nmon/ui/power_tab.py`` |
| `on_unmount` | `src/nmon/ui/app.py` |
| `poll() -> List[GpuSample]` | `Module: `src/nmon/gpu/protocol.py`` |
| `query_gpu_samples(window_s: int, gpu_index: Optional[int] = None) -> List[GpuSample]` | `Module: `src/nmon/storage/database.py`` |
| `query_llm_samples(window_s: int) -> List[LlmSample]` | `Module: `src/nmon/storage/database.py`` |
| `render` | `src/nmon/ui/alert_bar.py` |
| `render() -> str` | `Module: `src/nmon/ui/alert_bar.py`` |
| `run` | `src/nmon/main.py` |
| `run() -> None` | `Module: `src/nmon/main.py`` |
| `safe_nvml_call(call_func, args, default=None) -> Any` | `Module: src/nmon/gpu/monitor.py` |
| `save_persistent_settings` | `src/nmon/config.py` |
| `save_persistent_settings(config: AppConfig) -> None` | `Module: `src/nmon/config.py`` |
| `set_offload(pct: float) -> None` | `Module: `src/nmon/ui/widgets/alert_bar.py`` |
| `set_ollama_available(available: bool)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `set_ollama_present(present: bool) -> None` | `Module: `src/nmon/ui/dashboard.py`` |
| `set_time_range(seconds) -> None` | `Module: `src/nmon/ui/power_tab.py`` |
| `since` | `src/nmon/storage/ring_buffer.py` |
| `since(seconds)` | `Module: `src/nmon/storage/ring_buffer.py`` |
| `src/nmon/__init__.py` | `Interface Contracts: nmon` |
| `src/nmon/config.py` | `Interface Contracts: nmon` |
| `src/nmon/config.py -> src/nmon/main.py` | `Data Flow: nmon` |
| `src/nmon/gpu/monitor.py -> src/nmon/storage/database.py` | `Data Flow: nmon` |
| `src/nmon/llm/monitor.py -> src/nmon/storage/database.py` | `Data Flow: nmon` |
| `src/nmon/main.py -> src/nmon/gpu/monitor.py` | `Data Flow: nmon` |
| `src/nmon/storage/database.py -> src/nmon/ui/dashboard.py` | `Data Flow: nmon` |
| `src/nmon/ui/dashboard.py -> src/nmon/ui/dashboard_tab.py` | `Data Flow: nmon` |
| `src/nmon/ui/dashboard_tab.py -> src/nmon/ui/app.py` | `Data Flow: nmon` |
| `Stage 1: Configuration Loading (src/nmon/config.py)` | `Data Flow: nmon` |
| `Stage 2: Data Collection (src/nmon/gpu/monitor.py, src/nmon/llm/monitor.py)` | `Data Flow: nmon` |
| `Stage 3: Data Persistence (src/nmon/storage/database.py)` | `Data Flow: nmon` |
| `Stage 4: UI Rendering (src/nmon/ui/dashboard.py, src/nmon/ui/dashboard_tab.py)` | `Data Flow: nmon` |
| `start` | `src/nmon/llm/monitor.py` |
| `start` | `src/nmon/gpu/monitor.py` |
| `start` | `src/nmon/llm/protocol.py` |
| `start() -> None` | `Module: src/nmon/llm/monitor.py` |
| `start() -> None` | `Module: `src/nmon/llm/protocol.py`` |
| `start() -> None` | `Module: `src/nmon/gpu/protocol.py`` |
| `stop` | `src/nmon/llm/protocol.py` |
| `stop` | `src/nmon/gpu/monitor.py` |
| `stop` | `src/nmon/llm/monitor.py` |
| `stop() -> None` | `Module: `src/nmon/llm/protocol.py`` |
| `stop() -> None` | `Module: src/nmon/llm/monitor.py` |
| `stop() -> None` | `Module: `src/nmon/gpu/protocol.py`` |
| `toggle_mem_junction` | `src/nmon/ui/app.py` |
| `toggle_threshold_line` | `src/nmon/ui/app.py` |
| `update() -> None` | `Module: `src/nmon/ui/dashboard.py`` |
| `update_alert` | `src/nmon/ui/alert_bar.py` |
| `update_alert(sample: LlmSample | None) -> None` | `Module: `src/nmon/ui/alert_bar.py`` |
| `update_chart` | `src/nmon/ui/llm_tab.py` |
| `update_data(data: DashboardData)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `update_interval` | `src/nmon/ui/app.py` |
| `update_plots` | `src/nmon/ui/temp_tab.py` |
| `update_plots() -> None` | `Module: `src/nmon/ui/power_tab.py`` |
| `update_plots() -> None` | `Module: `src/nmon/ui/temp_tab.py`` |
| `update_sample(sample: GpuSample)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `update_sample(sample: LlmSample)` | `Module: `src/nmon/ui/dashboard_tab.py`` |
| `update_time_range` | `src/nmon/ui/temp_tab.py` |
| `update_time_range(seconds) -> None` | `Module: `src/nmon/ui/temp_tab.py`` |

## Call Graph - Most Connected Functions

Functions sorted by number of outgoing calls.

| Caller | File | Callees (count) |
|--------|------|-----------------|
| `update_time_range(seconds) -> None` | `Module: `src/nmon/ui/temp_tab.py`` | 1: seconds |
| `on_button_pressed(event: Button.Pressed) -> None` | `Module: `src/nmon/ui/llm_tab.py`` | 1: _time_range_s |

## Most Called Functions

| Function | Called By (count) | Callers |
|----------|-------------------|---------|
| `seconds` | 1 | update_time_range(seconds) -> None |
| `_time_range_s` | 1 | on_button_pressed(event: Button.Pressed) -> None |

## Subsystem Interfaces

Functions exported by each top-level directory.

### (root)

- `__all__`
- `__init__(params)`
- `__post_init__(params)`
- `src/nmon/__init__.py`
- `src/nmon/config.py`
- `src/nmon/config.py -> src/nmon/main.py`
- `src/nmon/gpu/monitor.py -> src/nmon/storage/database.py`
- `src/nmon/llm/monitor.py -> src/nmon/storage/database.py`
- `src/nmon/main.py -> src/nmon/gpu/monitor.py`
- `src/nmon/storage/database.py -> src/nmon/ui/dashboard.py`
- `src/nmon/ui/dashboard.py -> src/nmon/ui/dashboard_tab.py`
- `src/nmon/ui/dashboard_tab.py -> src/nmon/ui/app.py`
- `Stage 1: Configuration Loading (src/nmon/config.py)`
- `Stage 2: Data Collection (src/nmon/gpu/monitor.py, src/nmon/llm/monitor.py)`
- `Stage 3: Data Persistence (src/nmon/storage/database.py)`
- `Stage 4: UI Rendering (src/nmon/ui/dashboard.py, src/nmon/ui/dashboard_tab.py)`

### Module: `src

- `__all__`
- `__init__`
- `__init__`
- `__init__()`
- `__init__()`
- `__init__(argv: list[str]) -> None`
- `__init__(config)`
- `__init__(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor) -> None`
- `__init__(gpu_buffer, config)`
- `__init__(gpu_index: int)`
- `__init__(gpu_monitor, config, buffer) -> None`
- `__init__(params)`
- `__init__(params)`
- `__init__(params)`
- `__init__(params)`
- `__init__(params)`
- `__init__(params)`
- `__init__(parent=None)`
- `__init__(parent=None)`
- `__init__(timestamp: float, model_name: str, model_size_bytes: int, gpu_utilization_pct: float, cpu_utilization_pct: float, gpu_layers_offloaded: int, total_layers: int)`
- `__iter__() -> Iterator[GPUSample]`
- `__len__() -> int`
- `__post_init__(params)`
- `_build_power_plot(samples, power_limit_w, time_range_seconds) -> Plot`
- `_create_main_window() -> None`
- `_format_time_label(timestamp) -> str`
- `_get_power_limit_for_gpu(gpu_index, config) ->`
- `_increase_temp_threshold() -> None`
- `_latest_gpu_samples(buffer) -> List[GpuSample]`
- `_on_hide_timeout() -> None`
- `_on_poll_interval_changed(value: int)`
- `_on_window_close(event) -> None`
- `_parse_response(data: dict) -> LlmSample`
- `_poll() -> LlmSample | None`
- `_refresh_chart() -> None`
- `_save_config() -> None`
- `_setup_keyboard_shortcuts() -> None`
- `_setup_logging() -> None`
- `_shutdown() -> None`
- `_update_style() -> None`
- `append(item)`
- `append(sample)`
- `avg_field(field, seconds)`
- `compose() -> ComposeResult`
- `compose() -> ComposeResult`
- `compose() -> ComposeResult`
- `compose() -> ComposeResult`
- `detect() -> bool`
- `get_avg_temperature(gpu_index: int, window_s: int) -> Optional[float]`
- `get_max_temperature(gpu_index: int, window_s: int) -> Optional[float]`
- `init_database(db_path: str) -> None`
- `insert_gpu_sample(sample: GpuSample) -> None`
- `insert_llm_sample(sample: LlmSample) -> None`
- `latest()`
- `load_from_env() -> AppConfig`
- `load_persistent_settings() -> AppConfig`
- `max_field(field, seconds)`
- `on_button_pressed(event) -> None`
- `on_button_pressed(event) -> None`
- `on_button_pressed(event: Button.Pressed) -> None`
- `on_key(event) -> None`
- `on_mount() -> None`
- `on_mount() -> None`
- `poll() -> List[GpuSample]`
- `query_gpu_samples(window_s: int, gpu_index: Optional[int] = None) -> List[GpuSample]`
- `query_llm_samples(window_s: int) -> List[LlmSample]`
- `render() -> str`
- `run() -> None`
- `save_persistent_settings(config: AppConfig) -> None`
- `set_offload(pct: float) -> None`
- `set_ollama_available(available: bool)`
- `set_ollama_present(present: bool) -> None`
- `set_time_range(seconds) -> None`
- `since(seconds)`
- `start() -> None`
- `start() -> None`
- `stop() -> None`
- `stop() -> None`
- `update() -> None`
- `update_alert(sample: LlmSample | None) -> None`
- `update_data(data: DashboardData)`
- `update_plots() -> None`
- `update_plots() -> None`
- `update_sample(sample: GpuSample)`
- `update_sample(sample: LlmSample)`
- `update_time_range(seconds) -> None`

### Module: src

- `__init__(config: AppConfig, buffer: RingBuffer[GpuSample]) -> None`
- `__init__(config: AppConfig, buffer: RingBuffer[LlmSample])`
- `__init__(index: int, name: str, has_junction_temp: bool)`
- `__init__(timestamp: float, gpu_index: int, gpu_name: str, temperature_c: Optional[float], memory_used_mb: Optional[float], memory_total_mb: Optional[float], power_draw_w: Optional[float], junction_temp_c: Optional[float])`
- `_parse_response(data: Dict[str, Any]) -> Optional[LlmSample]`
- `_poll() -> Optional[LlmSample]`
- `_poll_loop() -> None`
- `collect_gpu_samples(gpu_descriptors: List[GpuDescriptor]) -> List[GpuSample]`
- `detect() -> bool`
- `enumerate_gpus() -> List[GpuDescriptor]`
- `init_nvml() -> None`
- `safe_nvml_call(call_func, args, default=None) -> Any`
- `start() -> None`
- `stop() -> None`

### src

- `__init__`
- `__init__`
- `__init__`
- `__init__`
- `__init__`
- `_build_gpu_sections`
- `_build_initial_content`
- `_build_llm_section`
- `_on_config_change`
- `_on_time_range_change`
- `_parse_response`
- `_parse_response`
- `_poll`
- `_poll`
- `_poll`
- `_poll_all`
- `_poll_loop`
- `_poll_loop`
- `_supports_mem_junction`
- `_update_display`
- `_update_plots`
- `adjust_threshold`
- `append`
- `avg_field`
- `compose`
- `detect`
- `detect`
- `latest`
- `load_from_env`
- `load_persistent_settings`
- `max_field`
- `None`
- `None`
- `None`
- `None`
- `on_button_pressed`
- `on_button_pressed`
- `on_click`
- `on_key`
- `on_mount`
- `on_mount`
- `on_unmount`
- `render`
- `run`
- `save_persistent_settings`
- `since`
- `start`
- `start`
- `start`
- `stop`
- `stop`
- `stop`
- `toggle_mem_junction`
- `toggle_threshold_line`
- `update_alert`
- `update_chart`
- `update_interval`
- `update_plots`
- `update_time_range`


