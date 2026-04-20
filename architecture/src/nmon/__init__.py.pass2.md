# src/nmon/__init__.py - Enhanced Analysis

## Architectural Role
Serves as the system's module aggregation point, exposing core monitoring components and views to enable cohesive integration across the TUI application. Acts as a central coordination layer for data flow between GPU monitoring, history storage, and UI rendering components.

## Cross-References
### Incoming
- `src/nmon/views/dashboard_view.py` (imports `DashboardView`)
- `src/nmon/views/temp_view.py` (imports `render_temp_view`, `update_temp_prefs`)
- `src/nmon/views/power_view.py` (imports `PowerView`)
- `src/nmon/views/llm_view.py` (imports `render_llm_view`)
- `src/nmon/widgets/sparkline.py` (imports `Sparkline`)
- `src/nmon/widgets/alert_bar.py` (imports `AlertBar`)

### Outgoing
- `nmon.config` (imports `Settings`, `UserPrefs`)
- `nmon.gpu_monitor` (imports `GpuSnapshot`)
- `nmon.ollama_monitor` (imports `OllamaSnapshot`)
- `nmon.alerts` (imports `AlertState`)
- `nmon.history` (imports `HistoryStore`)
- `nmon.views.dashboard_view` (imports `DashboardView`)
- `nmon.views.temp_view` (imports `render_temp_view`, `update_temp_prefs`)
- `nmon.views.power_view` (imports `PowerView`)
- `nmon.views.llm_view` (imports `render_llm_view`)
- `nmon.widgets.sparkline` (imports `Sparkline`)
- `nmon.widgets.alert_bar` (imports `AlertBar`)

## Design Patterns
- **Facade Pattern**: Provides simplified unified interface to complex subsystems
- **Module Aggregation**: Centralizes imports to reduce dependency management overhead
- **Export-Import Coordination**: Enables loose coupling between components while maintaining clear dependencies
