# Module: `src/nmon/db.py`

## Role
Database interface for storing and managing GPU and Ollama metrics collected by the nmon system.

## Contract: Module-level functions

### `init_db(db_path: str) -> None`
- **Requires:** `db_path` must be a valid string path to a writable location; the process must have file system permissions to create and modify database files at that location
- **Establishes:** Database tables `gpu_metrics` and `ollama_metrics` exist with specified schema; connection is properly closed
- **Raises:** Any `Exception` — if database connection fails or schema creation fails due to permission or disk issues

### `prune_old_data(db_path: str, history_hours: int) -> None`
- **Requires:** `db_path` must be a valid string path to an existing database file; `history_hours` must be a non-negative integer
- **Establishes:** Records older than `history_hours` are deleted from both `gpu_metrics` and `ollama_metrics` tables; connection is properly closed
- **Raises:** None — failures are logged and silently ignored
- **Silent failure:** If database connection fails or SQL execution fails, the function returns without raising an exception
- **Thread safety:** unsafe

### `flush_to_db(db_path: str, gpu_snapshots: List[GpuSnapshot], ollama_snapshot: Optional[OllamaSnapshot]) -> None`
- **Requires:** `db_path` must be a valid string path to an existing database file; `gpu_snapshots` must be a list of `GpuSnapshot` objects with valid data; `ollama_snapshot` may be `None`
- **Establishes:** All GPU and Ollama snapshot data is inserted into respective database tables; connection is properly closed
- **Raises:** None — failures are logged and silently ignored
- **Silent failure:** If database connection fails or SQL execution fails, the function returns without raising an exception
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
Database connections are opened and explicitly closed in all functions using a `try/finally` block to ensure proper cleanup. No persistent connections or background threads are maintained.
