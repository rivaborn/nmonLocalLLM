# src/nmon/storage/ring_buffer.py - Enhanced Analysis

## Architectural Role
Implements a thread-safe time-series storage abstraction that serves as a foundational data structure for both GPU and LLM monitoring samples. Acts as a bridge between the asynchronous data collection loop and synchronous UI rendering by providing safe concurrent access to time-windowed sample queries.

## Cross-References
### Incoming
- `src/nmon/gpu/monitor.py` - calls `append()` and query methods for GPU samples
- `src/nmon/llm/monitor.py` - calls `append()` and query methods for LLM samples  
- `src/nmon/ui/dashboard.py` - calls `since()`, `max_field()`, `avg_field()` for rendering
- `src/nmon/ui/history.py` - calls `since()` and aggregate methods for historical views

### Outgoing
- `src/nmon/config.py` - consumes `AppConfig` for history duration and poll interval
- `src/nmon/gpu/protocol.py` - generic type constraint for `GpuSample`
- `src/nmon/llm/protocol.py` - generic type constraint for `LlmSample`
- `collections.deque`, `threading.Lock`, `time`, `math` - standard library dependencies

## Design Patterns
- **Generic Type Parameterization** - Uses `TypeVar[T]` to support both `GpuSample` and `LlmSample` types while maintaining type safety
- **Thread-Safe Decorator Pattern** - Wraps all public methods with `threading.Lock` to ensure safe concurrent access across asyncio and synchronous contexts
- **Time-Series Query Pattern** - Implements timestamp-based filtering and aggregation methods (`since`, `max_field`, `avg_field`) for common dashboard visualization needs
