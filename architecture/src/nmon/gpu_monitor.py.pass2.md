# src/nmon/gpu_monitor.py - Enhanced Analysis

## Architectural Role
Provides core GPU metric collection functionality for the monitoring system. Serves as the primary data source for all GPU-related telemetry, bridging hardware-level NVML calls with the application's monitoring and display layers.

## Cross-References
### Incoming
- `src/nmon/monitor.py` - Calls `poll()` to fetch current GPU metrics for display and storage
- `src/nmon/cli.py` - References `GpuMonitorProtocol` for type hints in CLI monitoring flows

### Outgoing
- `pynvml` - Direct NVML API calls for GPU hardware metrics
- `logging` - Error reporting for NVML operation failures

## Design Patterns
- **Singleton-like Initialization**: Global state management prevents redundant NVML initialization, optimizing performance across repeated polling cycles
- **Graceful Degradation**: Fallback values and exception handling ensure monitoring continues even when individual GPU metrics are unavailable
- **Protocol-Based Abstraction**: `GpuMonitorProtocol` enables potential future implementations (mock, file-based) while maintaining consistent interface contract
