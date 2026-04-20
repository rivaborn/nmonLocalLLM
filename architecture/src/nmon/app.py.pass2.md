# src/nmon/app.py - Enhanced Analysis

## Architectural Role
NmonApp serves as the central orchestrator of the terminal monitoring application, managing the UI lifecycle, coordinating data flow between monitoring components and views, and handling user interaction events. It acts as the primary controller that ties together GPU monitoring, Ollama monitoring, history storage, alerting, and UI rendering.

## Cross-References
### Incoming
- `src/nmon/main.py` calls `NmonApp.start()` and `NmonApp.stop()` to begin and end application execution
- `src/nmon/views/` modules call `NmonApp._render_current_view()` to update UI components
- `src/nmon/history.py` interacts with `NmonApp.history_store` for data persistence

### Outgoing
- Calls `src/nmon/history.py` for data storage and retrieval operations
- Calls `src/nmon/gpu_monitor.py` and `src/nmon/ollama_monitor.py` for metric polling
- Calls `src/nmon/alerts.py` for alert computation and state management
- Calls `src/nmon/views/` modules for UI rendering and view-specific logic
- Calls `src/nmon/widgets/` modules for UI component rendering

## Design Patterns
- **Observer Pattern**: The app observes changes in monitoring data and updates UI accordingly through the history store
- **State Machine**: Application maintains running state and transitions between active and stopped states
- **Command Pattern**: Keyboard events are handled as commands that modify application state or trigger actions
