# src/nmon/alerts.py - Enhanced Analysis

## Architectural Role
Handles alert state computation for the terminal dashboard, acting as a bridge between Ollama monitoring data and UI display logic. Part of the dashboard's real-time feedback system.

## Cross-References
### Incoming
- `src/nmon/dashboard.py` - Calls `compute_alert` during dashboard refresh cycles
- `src/nmon/ollama_monitor.py` - Receives alert state computation results for alert bar rendering

### Outgoing
- `src/nmon/ollama_monitor.py` - Depends on `OllamaSnapshot` data structure
- `src/nmon/config.py` - Depends on `Settings` for alert threshold configuration

## Design Patterns
- **State Management Pattern**: Uses `AlertState` dataclass to encapsulate alert state, enabling clean separation of alert computation from display logic
- **Conditional Logic Pattern**: Implements clear decision trees for alert activation based on multiple boolean conditions and threshold comparisons
- **Time-based Expiration Pattern**: Incorporates timestamp-based alert lifetime management for temporary UI feedback
