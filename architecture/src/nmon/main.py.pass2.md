# src/nmon/main.py - Enhanced Analysis

## Architectural Role
Serves as the application's bootstrap coordinator, orchestrating component initialization and startup sequence. Acts as the central coordination point that wires together configuration, monitoring components, and the UI layer.

## Cross-References
### Incoming
- `NmonApp.__init__` calls `run()` to initialize monitoring state
- `NmonApp.on_mount` triggers monitoring startup via `run()`'s side effects

### Outgoing
- `GpuMonitor.__init__` and `LlmMonitor.__init__` 
- `RingBuffer.__init__`
- `NmonApp.__init__` and `NmonApp.run`
- `asyncio.run()` for async Ollama detection

## Design Patterns
- **Resource Manager Pattern**: NVML initialization/shutdown in monitor lifecycle
- **Conditional Component Activation**: LLM monitoring starts only when Ollama is detected
- **Bootstrapping Pattern**: Centralized initialization sequence with dependency injection
