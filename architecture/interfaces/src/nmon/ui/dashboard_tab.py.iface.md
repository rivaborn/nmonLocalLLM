# Module: `src/nmon/ui/dashboard_tab.py`

## Role
Implements the dashboard UI tab for displaying GPU and LLM server metrics with Qt-based widgets.

## Contract: `DashboardTab`

### `__init__(parent=None)`
- **Requires:** `parent` is a valid Qt parent widget or None
- **Establishes:** UI layout with poll interval spinner, GPU grid, and Ollama section; initializes internal state
- **Raises:** `TypeError` if parent is not a QWidget subclass or None

### `update_data(data: DashboardData)`
- **Requires:** `data` contains valid `gpu_samples` list; `gpu_samples` contain valid `GpuSample` objects with valid numeric fields
- **Guarantees:** GPU cards are updated with latest sample data; Ollama section is updated or hidden based on `llm_sample`
- **Raises:** `AttributeError` if sample fields are missing; `ValueError` if sample data is invalid
- **Silent failure:** None
- **Thread safety:** unsafe

### `set_ollama_available(available: bool)`
- **Requires:** `available` is a boolean
- **Guarantees:** Ollama section visibility is set to `available` value
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

### `_on_poll_interval_changed(value: int)`
- **Requires:** `value` is an integer in range [1, 60]
- **Guarantees:** `poll_interval_changed` signal is emitted with `value`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

## Contract: `GpuCardWidget`

### `__init__(gpu_index: int)`
- **Requires:** `gpu_index` is a non-negative integer
- **Establishes:** UI layout with temperature, memory, power, and junction temperature labels; sets up frame styling
- **Raises:** `TypeError` if `gpu_index` is not an integer

### `update_sample(sample: GpuSample)`
- **Requires:** `sample` is a valid `GpuSample` with all numeric fields present
- **Guarantees:** All labels are updated with sample data; junction section visibility is set based on `junction_temp_c` presence
- **Raises:** `AttributeError` if sample fields are missing; `TypeError` if sample fields are not numeric
- **Silent failure:** None
- **Thread safety:** unsafe

## Contract: `OllamaSectionWidget`

### `__init__()`
- **Requires:** None
- **Establishes:** UI layout with model, GPU util, and CPU util labels
- **Raises:** None

### `update_sample(sample: LlmSample)`
- **Requires:** `sample` is a valid `LlmSample` with optional `model_name` field
- **Guarantees:** Labels are updated with sample data; color styling applied based on GPU utilization
- **Raises:** `AttributeError` if sample fields are missing; `TypeError` if sample fields are not numeric
- **Silent failure:** None
- **Thread safety:** unsafe

## Module Invariants
- All widget references are properly initialized before use
- UI elements are properly laid out with consistent spacing and margins
- GPU card widgets are indexed correctly in
