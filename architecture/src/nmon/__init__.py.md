# src/nmon/__init__.py

## Purpose
Exports core modules and components for the nmon system, making them available for import by other parts of the application.

## Responsibilities
- Aggregate and expose key system components for external use
- Provide unified access to monitoring data structures and views
- Enable modular organization of the nmon application

## Key Types
- Settings (Class): Configuration settings container
- UserPrefs (Class): User preference storage
- GpuSnapshot (Class): GPU metrics data structure
- OllamaSnapshot (Class): Ollama metrics data structure
- AlertState (Class): Alert state management
- HistoryStore (Class): Historical data storage
- DashboardView (Class): Main dashboard rendering interface
- PowerView (Class): Power consumption visualization
- Sparkline (Class): Sparkline widget for data visualization
- AlertBar (Class): Alert notification display widget

## Key Functions
### render_temp_view
- Purpose: Renders temperature monitoring view
- Calls: Not visible in this file

### update_temp_prefs
- Purpose: Updates temperature view preferences
- Calls: Not visible in this file

### render_llm_view
- Purpose: Renders LLM monitoring view
- Calls: Not visible in this file

## Globals
None

## Dependencies
- nmon.config
- nmon.gpu_monitor
- nmon.ollama_monitor
- nmon.alerts
- nmon.history
- nmon.views.dashboard
