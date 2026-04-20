# src/nmon/main.py - Enhanced Analysis

## Architectural Role
Serves as the primary entry point and application coordinator, orchestrating the startup, runtime, and graceful shutdown of the nmon monitoring system. Acts as the central hub that wires together all major subsystems: configuration, monitoring, storage, and UI.

## Cross-References
### Incoming
- `nmon.app.NmonApp.run()` - Application lifecycle management
- `nmon.config.Settings.model_validate_env()` - Configuration loading
- `nmon.history.HistoryStore.__init__()` - Database initialization
- `nmon.gpu_monitor.GpuMonitorProtocol.__init__()` - GPU monitoring setup
- `nmon.ollama_monitor.OllamaMonitorProtocol.__init__()` - Ollama monitoring setup

### Outgoing
- `nmon.app.NmonApp` - Main application controller
- `nmon.config.Settings` - Configuration management
- `nmon.history.HistoryStore` - Data persistence
- `nmon.gpu_monitor.GpuMonitorProtocol` - GPU metrics collection
- `nmon.ollama_monitor.OllamaMonitorProtocol` - Ollama metrics collection

## Design Patterns
- **Dependency Injection**: Components are instantiated and passed to NmonApp, enabling loose coupling and testability
- **Signal Handler Pattern**: Graceful shutdown handling via SIGINT/SIGTERM signals with cleanup routines
- **Factory Pattern**: Component instantiation with configuration-driven parameters
