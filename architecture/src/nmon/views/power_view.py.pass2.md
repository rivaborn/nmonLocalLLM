# src/nmon/views/power_view.py - Enhanced Analysis

## Architectural Role
PowerView serves as a specialized dashboard renderer for GPU power consumption metrics, integrating historical data visualization with optional Ollama process monitoring. It acts as a view controller in the MVC pattern, orchestrating the presentation layer for power-related telemetry.

## Cross-References
### Incoming
- Called by main application loop in `src/nmon/app.py` during view switching
- Accessed by `src/nmon/controller.py` for view rendering delegation

### Outgoing
- Calls `HistoryStore.get_power_history()` for data retrieval
- Depends on `Sparkline` widget from `src/nmon/widgets/sparkline.py`
- Integrates with `OllamaSnapshot` from `src/nmon/ollama_monitor.py`

## Design Patterns
- **View Controller Pattern**: Separates presentation logic from data sources, managing UI composition
- **Composite Pattern**: Uses rich Layout objects to compose nested UI components
- **Adapter Pattern**: Transforms historical power data into sparkline-compatible format for visualization
