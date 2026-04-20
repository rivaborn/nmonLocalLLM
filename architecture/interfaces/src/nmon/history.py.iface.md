# Module: `src/nmon/history.py`

## Role
Manages historical GPU and Ollama metrics storage, retrieval, and persistence via SQLite.

## Contract: `HistoryStore`

### `__init__(settings: Settings) -> None`
- **Requires:** `settings.db_path` must be a valid path string; `settings.history_hours` and `settings.poll_interval_s` must be positive numbers; SQLite database at `settings.db_path` must be accessible or creatable.
- **Establishes:** `_gpu_snapshots` and `_ollama_snapshots` are initialized as empty deques; data from DB is loaded into deques if available.
- **Raises:** `None` — no exceptions are raised during construction, though logging may occur on DB load failure.

### `add_gpu_samples(samples: list[GpuSnapshot]) -> None`
- **Requires:** `samples` must be a list of `GpuSnapshot` objects; `self._settings` must be initialized with valid `history_hours` and `poll_interval_s`.
- **Guarantees:** Samples are added to internal deque and trimmed to maximum size based on history duration and poll interval.
- **Raises:** `None` — no exceptions raised; DB flush failures are logged but do not interrupt execution.
- **Silent failure:** If DB flush fails, samples are still added and trimmed, but not persisted to disk.
- **Thread safety:** unsafe — not thread-safe; concurrent access may corrupt internal state.

### `add_ollama_sample(sample: OllamaSnapshot) -> None`
- **Requires:** `sample` must be an `OllamaSnapshot` object; `self._settings` must be initialized with valid `history_hours` and `poll_interval_s`.
- **Guarantees:** Sample is added to internal deque and trimmed to maximum size based on history duration and poll interval.
- **Raises:** `None` — no exceptions raised.
- **Silent failure:** None.
- **Thread safety:** unsafe — not thread-safe.

### `gpu_series(gpu_index: int, hours: float) -> list[GpuSnapshot]`
- **Requires:** `gpu_index` must be an integer; `hours` must be a non-negative float.
- **Guarantees:** Returns a list of `GpuSnapshot` objects matching the GPU index and time range.
- **Raises:** `None` — no exceptions raised.
- **Silent failure:** None.
- **Thread safety:** safe — read-only operation.

### `ollama_series(hours: float) -> list[OllamaSnapshot]`
- **Requires:** `hours` must be a non-negative float.
- **Guarantees:** Returns a list of `OllamaSnapshot` objects within the specified time range.
- **Raises:** `None` — no exceptions raised.
- **Silent failure:** None.
- **Thread safety:** safe — read-only operation.

### `gpu_stat(gpu_index: int, field: str, hours: float, stat: Literal["max","avg","current"]) -> float | None`
- **Requires:** `gpu_index` must be an integer; `field` must be a valid attribute name of `GpuSnapshot`; `hours` must be non-negative; `stat` must be one of `"max"`, `"avg"`, or `"current"`.
- **Guarantees:** Returns a float
