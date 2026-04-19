# Module: `src/nmon/storage/database.py`

## Role
Implements SQLite database layer for persisting GPU and LLM monitoring samples, with WAL mode enabled and automatic cleanup of old data.

## Contract: Module-level functions

### `init_database(db_path: str) -> None`
- **Requires:** `db_path` must be a valid string path to a writable location
- **Establishes:** Database schema created with WAL mode enabled, tables for GPU samples, LLM samples, and app settings; old rows purged
- **Raises:** `sqlite3.OperationalError` — if database cannot be opened or initialized
- **Silent failure:** None
- **Thread safety:** unsafe

### `insert_gpu_sample(sample: GpuSample) -> None`
- **Requires:** `sample` must be a valid `GpuSample` instance with all fields populated
- **Guarantees:** Sample inserted into `gpu_samples` table; no return value
- **Raises:** `sqlite3.Error` — if write fails due to database issues
- **Silent failure:** None
- **Thread safety:** unsafe

### `insert_llm_sample(sample: LlmSample) -> None`
- **Requires:** `sample` must be a valid `LlmSample` instance with all fields populated
- **Guarantees:** Sample inserted into `llm_samples` table; no return value
- **Raises:** `sqlite3.Error` — if write fails due to database issues
- **Silent failure:** None
- **Thread safety:** unsafe

### `query_gpu_samples(window_s: int, gpu_index: Optional[int] = None) -> List[GpuSample]`
- **Requires:** `window_s` must be a non-negative integer representing seconds
- **Guarantees:** Returns list of `GpuSample` objects within time window; empty list if no results
- **Raises:** `sqlite3.Error` — if query fails due to database issues
- **Silent failure:** Returns empty list if query fails
- **Thread safety:** unsafe

### `query_llm_samples(window_s: int) -> List[LlmSample]`
- **Requires:** `window_s` must be a non-negative integer representing seconds
- **Guarantees:** Returns list of `LlmSample` objects within time window; empty list if no results
- **Raises:** `sqlite3.Error` — if query fails due to database issues
- **Silent failure:** Returns empty list if query fails
- **Thread safety:** unsafe

### `get_max_temperature(gpu_index: int, window_s: int) -> Optional[float]`
- **Requires:** `gpu_index` must be a non-negative integer; `window_s` must be a non-negative integer
- **Guarantees:** Returns maximum temperature value or None if no samples found
- **Raises:** `sqlite3.Error` — if query fails due to database issues
- **Silent failure:** Returns None if query fails
- **Thread safety:** unsafe

### `get_avg_temperature(gpu_index: int, window_s: int) -> Optional[float]`
- **Requires:** `gpu_index` must be a non-negative integer; `window_s` must be a non-negative integer
- **Guarantees:** Returns average temperature value or None if no samples found
- **
