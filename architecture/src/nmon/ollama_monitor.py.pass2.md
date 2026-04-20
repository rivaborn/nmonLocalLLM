# src/nmon/ollama_monitor.py - Enhanced Analysis

## Architectural Role
Provides Ollama inference server monitoring capabilities as part of the system's multi-source metrics collection pipeline. Acts as a protocol-conforming monitor that integrates with the main GPU monitoring workflow and contributes to the unified TUI dashboard.

## Cross-References
### Incoming
- `src/nmon/monitor.py` - Calls `poll()` method during periodic monitoring cycles
- `src/nmon/dashboard.py` - Consumes `OllamaSnapshot` data for display in widgets

### Outgoing
- `src/nmon/config.py` - Depends on `Settings` for Ollama base URL configuration
- `httpx.AsyncClient` - Makes async HTTP requests to Ollama API endpoints
- `src/nmon/monitor.py` - Called by main monitoring loop for Ollama data collection

## Design Patterns
- **Protocol-Implementation Pattern** - Uses `OllamaMonitorProtocol` interface to enable mockable testing and future extensibility
- **Stateful Polling Pattern** - Maintains `ollama_detected` flag to avoid repeated probing after initial discovery
- **Graceful Degradation Pattern** - Returns empty snapshots with `reachable=False` on network failures rather than crashing
