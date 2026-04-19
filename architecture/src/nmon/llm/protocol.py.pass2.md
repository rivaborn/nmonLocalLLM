# src/nmon/llm/protocol.py - Enhanced Analysis

## Architectural Role
Defines the contract and data schema for LLM monitoring functionality, enabling pluggable monitoring implementations while maintaining consistency with GPU monitoring patterns. Serves as the interface layer between LLM-specific data collection and the system's unified monitoring architecture.

## Cross-References
### Incoming
- `src/nmon/llm/monitor.py` - Implements LlmMonitorProtocol and uses LlmSample
- `src/nmon/main.py` - References LlmMonitorProtocol for dynamic monitoring setup

### Outgoing
- `src/nmon/storage/ring_buffer.py` - Consumes LlmSample for storage
- `src/nmon/config.py` - Uses LlmSample for configuration validation

## Design Patterns
- **Protocol-based Interface Design** - Uses typing.Protocol to define LLM monitoring contract, enabling flexible implementations while maintaining type safety
- **Dataclass for Immutable Data Structures** - LlmSample uses dataclass with `__slots__` for efficient memory usage and clear schema definition
- **Separation of Concerns** - Clear distinction between monitoring protocol (interface), data representation (LlmSample), and parsing logic (parse_response)
