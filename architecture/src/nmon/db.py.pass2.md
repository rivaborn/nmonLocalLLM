# src/nmon/db.py - Enhanced Analysis

## Architectural Role
Manages persistent storage layer for system metrics, serving as the data persistence boundary between real-time monitoring and historical analysis. Provides the foundation for both live dashboard rendering and historical data retrieval.

## Cross-References
### Incoming
- `src/nmon/main.py` calls `init_db` during startup
- `src/nmon/main.py` calls `flush_to_db` during data collection cycles
- `src/nmon/main.py` calls `prune_old_data` during cleanup operations

### Outgoing
- `src/nmon/gpu_monitor.py` imports `GpuSnapshot` type
- `src/nmon/ollama_monitor.py` imports `OllamaSnapshot` type
- Direct SQLite database operations with no external dependencies

## Design Patterns
- **Data Access Object (DAO)**: Encapsulates all database operations behind a clean interface
- **Connection Management**: Uses try/finally blocks to ensure proper resource cleanup
- **Separation of Concerns**: Clearly separates schema initialization, data pruning, and data insertion logic
