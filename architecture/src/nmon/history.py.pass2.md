# src/nmon/history.py - Enhanced Analysis

## Architectural Role
Manages historical metric persistence and retrieval for both GPU and Ollama systems. Acts as the bridge between live monitoring data and long-term storage, enabling time-series analysis and dashboard history views.

## Cross-References
### Incoming
- `src/nmon/dashboard.py` - calls `gpu_series`, `ollama_series`, `gpu_stat` for history data
- `src/nmon/gpu_monitor.py` - calls `add_gpu_samples` to store new GPU metrics
- `src/nmon/ollama_monitor.py` - calls `add_ollama_sample` to store new Ollama metrics

### Outgoing
- `src/nmon/db.py` - calls `DbConnection` for database operations
- `src/nmon/config.py` - reads `history_hours`, `poll_interval_s`, `db_path` settings
- `src/nmon/gpu_monitor.py` - creates `GpuSnapshot` objects for storage
- `src/nmon/ollama_monitor.py` - creates `OllamaSnapshot` objects for storage

## Design Patterns
- **Caching with Size Limits** - Uses `deque` with automatic trimming to implement memory-efficient time-series cache
- **Lazy Persistence** - Flushes to database only when approaching capacity, balancing performance with data durability
- **Query Abstraction** - Provides high-level statistical queries (`gpu_stat`) that abstract underlying time-series filtering logic
