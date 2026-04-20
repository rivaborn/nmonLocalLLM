# src/nmon/views/dashboard_view.py - Enhanced Analysis

## Architectural Role
Manages the primary terminal user interface for nmon, orchestrating GPU and LLM metric display while coordinating with alert, configuration, and history subsystems. Serves as the main rendering entry point for the application's live monitoring dashboard.

## Cross-References
### Incoming
- `nmon/app.py` - Calls `render()` method during main application loop
- `nmon/views/main_view.py` - References `DashboardView` as primary view component

### Outgoing
- `nmon/gpu_monitor.py` - Calls `poll()` for current GPU metrics
- `nmon/history.py` - Calls `ollama_series()` for historical LLM data
- `nmon/widgets/alert_bar.py` - Instantiates `AlertBar` for alert display
- `nmon/widgets/sparkline.py` - Imports but not used in current implementation

## Design Patterns
- **Strategy Pattern** - Uses different panel creation methods (`_create_gpu_panel`, `_create_llm_panel`) for varying data types
- **Facade Pattern** - Provides unified `render()` interface that coordinates multiple subsystems
- **Conditional Rendering** - Implements dynamic layout adjustment based on data availability (memory junction temps, Ollama snapshots)
