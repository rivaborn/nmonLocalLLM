# src/nmon/views/llm_view.py - Enhanced Analysis

## Architectural Role
This file implements a specialized TUI view for monitoring LLM server resource usage, integrating with the broader monitoring system's history and configuration subsystems. It serves as a bridge between raw metric data and user-facing visualizations.

## Cross-References
### Incoming
- `src/nmon/app.py` - Called during view switching in main application loop
- `src/nmon/views/dashboard.py` - Potentially referenced for view composition

### Outgoing
- `src/nmon/history.py` - Calls `get_gpu_usage_series` and `get_cpu_usage_series`
- `src/nmon/ollama_monitor.py` - Reads `ollama_snapshot.reachable` flag
- `src/nmon/widgets/sparkline.py` - Instantiates Sparkline widget
- `src/nmon/config.py` - Reads `prefs.active_time_range_hours` setting

## Design Patterns
- **State Machine Pattern** - Handles offline/online states with conditional rendering
- **Facade Pattern** - Abstracts complex history data fetching and visualization logic
- **Strategy Pattern** - Adapts to different data sources (GPU/CPU) through unified sparkline interface
