# Module: `src/nmon/ui/app.py`

## Role
Main Textual application class that orchestrates GPU and LLM monitoring, UI components, and data flow for the nmon terminal system monitor.

## Contract: `NmonApp`

### `__init__(config: AppConfig) -> None`
- **Requires:** `config` must be a valid `AppConfig` instance with `poll_interval_s`, `history_duration_s` attributes; `AppConfig` must be properly initialized
- **Establishes:** All internal components (`gpu_buffer`, `llm_buffer`, `gpu_monitor`, `llm_monitor`, UI widgets) are initialized; `tabs` list contains dashboard, temperature, and power tabs; `update_interval_s` is set to `config.poll_interval_s`
- **Raises:** `TypeError` if `config` is not of type `AppConfig`

### `on_mount() -> None`
- **Requires:** `self.gpu_monitor` and `self.llm_monitor` must be properly initialized; `self.config` must be valid
- **Guarantees:** GPU monitoring starts; if Ollama detected, LLM monitoring starts and LLM tab is added to UI; all UI components are composed
- **Raises:** `Exception` if monitor detection or startup fails (silent failure possible)
- **Silent failure:** Monitor detection or startup failures may be silently ignored; UI composition may fail silently if not properly handled
- **Thread safety:** Unsafe - relies on async event handling

### `on_unmount() -> None`
- **Requires:** `self.gpu_monitor` and `self.llm_monitor` must be initialized; `self.ollama_present` flag must be valid
- **Guarantees:** All monitoring is stopped; configuration persistence logic is called (implementation not shown)
- **Raises:** `Exception` if monitor stopping fails (silent failure possible)
- **Silent failure:** Monitor stopping failures may be silently ignored; config persistence may silently fail
- **Thread safety:** Unsafe

### `update_interval(interval_s: float) -> None`
- **Requires:** `interval_s` must be a `float` in range [0.5, 60.0]
- **Guarantees:** Internal `update_interval_s` is updated; monitor intervals are updated (implementation not shown)
- **Raises:** `ValueError` if `interval_s` is outside range [0.5, 60.0]
- **Silent failure:** Monitor interval updates may silently fail (implementation not shown)
- **Thread safety:** Unsafe

### `toggle_mem_junction() -> None`
- **Requires:** `self.temp_tab` must be initialized
- **Guarantees:** Memory junction visibility toggled in TempTab (implementation not shown)
- **Raises:** `Exception` if UI update fails (silent failure possible)
- **Silent failure:** UI update failures may be silently ignored
- **Thread safety:** Unsafe

### `toggle_threshold_line() -> None`
- **Requires:** `self.temp_tab` must be initialized
- **Guarantees:** Threshold line visibility toggled in TempTab (implementation not shown)
- **Raises:** `Exception` if UI update fails (silent failure possible)
- **Silent failure:** UI update failures may be silently ignored
- **Thread safety:** Unsafe

### `adjust_threshold(delta_c: float) -> None`
