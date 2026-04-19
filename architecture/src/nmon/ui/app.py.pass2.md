# src/nmon/ui/app.py - Enhanced Analysis

## Architectural Role
Serves as the central coordinator and entry point for the nmon TUI application, orchestrating GPU and LLM monitoring components with the rich text-based UI. Manages application lifecycle, conditional UI tab rendering, and data flow between monitoring layers and display widgets.

## Cross-References
### Incoming
- `src/nmon/__main__.py` calls `NmonApp.__init__()` and `App.run()`
- `src/nmon/ui/dashboard_tab.py` interacts with app state via `self.app` reference
- Keyboard shortcut handlers in `src/nmon/ui/app.py` call `adjust_threshold`, `toggle_mem_junction`, `toggle_threshold_line`

### Outgoing
- Calls `GpuMonitor.start()`, `GpuMonitor.stop()`, `LlmMonitor.start()`, `LlmMonitor.stop()`
- Instantiates and manages `DashboardTab`, `TemperatureTab`, `PowerTab`, `LlmTab` UI components
- Depends on `RingBuffer` for data storage and `AppConfig` for configuration

## Design Patterns
- **Observer Pattern**: UI components observe monitor data through ring buffers and update automatically
- **Conditional Composition**: UI tabs are dynamically added/removed based on runtime conditions (Ollama detection)
- **State Machine**: Application transitions through mounted/unmounted states with corresponding cleanup/startup logic
