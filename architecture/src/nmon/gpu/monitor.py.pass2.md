# src/nmon/gpu/monitor.py - Enhanced Analysis

## Architectural Role
Manages GPU hardware metric collection via NVML in an asynchronous polling loop. Serves as the primary data source for the TUI dashboard and history view, feeding samples into a shared ring buffer for downstream processing.

## Cross-References
### Incoming
- `src/nmon/main.py` - Calls `start()` and `stop()` to control monitoring lifecycle
- `src/nmon/storage/database.py` - Receives samples via the shared ring buffer for persistence

### Outgoing
- `pynvml` - Direct NVML library calls for GPU device enumeration and metric collection
- `src/nmon/storage/ring_buffer.py` - Writes collected samples via `buffer.append()`
- `src/nmon/config.py` - Reads poll interval configuration

## Design Patterns
- **Observer Pattern** - The monitor observes GPU state changes through periodic polling, with samples pushed to subscribers (ring buffer)
- **Error Recovery Pattern** - Gracefully handles NVML exceptions by creating sentinel samples instead of crashing
- **Resource Management Pattern** - Properly initializes NVML in `__init__` and shuts down in `stop()` with cleanup tasks
