# src/nmon/gpu/protocol.py - Enhanced Analysis

## Architectural Role
Defines the contract and data structure for GPU monitoring components, enabling polymorphic behavior across different monitoring implementations while providing a consistent interface for data consumption throughout the system.

## Cross-References
### Incoming
- `src/nmon/gpu/monitor.py` implements this protocol
- `src/nmon/main.py` consumes GPU samples through this interface
- `src/nmon/storage/ring_buffer.py` stores samples conforming to this structure

### Outgoing
- `src/nmon/gpu/monitor.py` implements this protocol
- `src/nmon/llm/protocol.py` references similar patterns for consistency

## Design Patterns
- **Protocol-based Design**: Uses `typing.Protocol` to define interface contracts, enabling flexible implementation while maintaining type safety
- **Immutable Data Transfer**: `GpuSample` uses `dataclass(frozen=True)` for immutable value objects, preventing accidental mutation during data flow
- **Separation of Concerns**: Clear distinction between data structure definition (`GpuSample`) and behavioral contract (`GpuMonitorProtocol`)
