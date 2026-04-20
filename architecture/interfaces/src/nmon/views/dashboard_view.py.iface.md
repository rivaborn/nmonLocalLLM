# Module: `src/nmon/views/dashboard_view.py`

## Role
Provides the main terminal dashboard view for nmon, rendering GPU metrics, memory junction temperatures, and Ollama LLM usage.

## Contract: `DashboardView`

### `__init__(gpu_monitor, history_store, prefs, settings, alert_state)`
- **Requires:** `gpu_monitor` must be a valid GpuMonitorProtocol instance; `history_store` must be a valid HistoryStore instance; `prefs` must be a valid UserPrefs instance; `settings` must be a valid Settings instance; `alert_state` must be either an AlertState instance or None
- **Establishes:** All instance attributes are set to provided parameters; no resources are acquired during initialization
- **Raises:** `TypeError` if any parameter is of incorrect type

### `render() -> Layout`
- **Requires:** `self.gpu_monitor` must be a valid GpuMonitorProtocol instance; `self.history_store` must be a valid HistoryStore instance; `self.prefs` must be a valid UserPrefs instance; `self.settings` must be a valid Settings instance
- **Guarantees:** Returns a rich.layout.Layout instance with properly structured dashboard layout; alert bar is rendered if alert_state is not None; GPU panels are created for each snapshot; LLM panel is shown only if reachable Ollama snapshot exists
- **Raises:** `AttributeError` if any required instance attribute is missing; `ValueError` if GPU monitor returns invalid data; `KeyError` if layout access fails
- **Silent failure:** None
- **Thread safety:** unsafe

### `_create_gpu_panel(snapshot) -> Panel`
- **Requires:** `snapshot` must be a valid GpuSnapshot instance with all required fields populated
- **Guarantees:** Returns a rich.panel.Panel instance with properly formatted GPU metrics table; temperature, memory, and power values are correctly formatted
- **Raises:** `AttributeError` if snapshot fields are missing; `TypeError` if snapshot fields are of incorrect type
- **Silent failure:** None
- **Thread safety:** unsafe

### `_create_llm_panel(snapshot) -> Panel`
- **Requires:** `snapshot` must be a valid OllamaSnapshot instance with all required fields populated
- **Guarantees:** Returns a rich.panel.Panel instance with properly formatted LLM metrics table; model name, size, usage percentages, and offload status are correctly formatted
- **Raises:** `AttributeError` if snapshot fields are missing; `TypeError` if snapshot fields are of incorrect type
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
