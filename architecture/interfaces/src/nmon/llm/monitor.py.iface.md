# Module: `src/nmon/llm/monitor.py`

## Role
Asynchronous monitor for LLM model metrics using Ollama API, collecting samples into a ring buffer.

## Contract: `LlmMonitor`

### `__init__(config: AppConfig, buffer: RingBuffer[LlmSample]) -> None`
- **Requires:** `config` must be a valid `AppConfig` instance with a working `http_client()` method; `buffer` must be a valid `RingBuffer[LlmSample]` instance
- **Establishes:** Initializes internal state with `config`, `buffer`, `_running=False`, and `_task=None`
- **Raises:** `TypeError` — if `config` is not `AppConfig` or `buffer` is not `RingBuffer[LlmSample]`

### `detect() -> bool`
- **Requires:** `config.http_client()` must be callable and return a valid async HTTP client
- **Guarantees:** Returns `True` if Ollama API `/api/tags` returns HTTP 200; `False` otherwise
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `start() -> None`
- **Requires:** Monitor must not already be running (`_running` must be `False`)
- **Guarantees:** Sets `_running=True` and starts background polling task via `asyncio.create_task`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `stop() -> None`
- **Requires:** Monitor must be running (`_running` must be `True`)
- **Guarantees:** Sets `_running=False` and cancels background task if running
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `_poll() -> Optional[LlmSample]`
- **Requires:** `config.http_client()` must be callable and return a valid async HTTP client
- **Guarantees:** Returns `LlmSample` if API call succeeds and data is valid; `None` otherwise
- **Raises:** None
- **Silent failure:** Returns `None` if API returns non-200 status or JSON parsing fails
- **Thread safety:** Unsafe

### `_parse_response(data: dict) -> LlmSample`
- **Requires:** `data` must contain a `"models"` key with a list of at least one model dict; model dict must contain `"name"`, `"size"`, `"size_vram"`, `"parameter_size"` keys
- **Guarantees:** Returns a valid `LlmSample` with calculated GPU/CPU utilization percentages clamped to [0.0, 100.0]
- **Raises:** `KeyError` — if any required key is missing from `data["models"][0]`
- **Silent failure:** None
- **Thread safety:** Unsafe

### `_poll_loop() -> None`
- **Requires:** Monitor must be running (`_running` must be `True`)
- **Guarantees:** Continuously polls Ollama API and appends valid samples to buffer until stopped
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

## Module Invariants
- `self._running` is always `True` only when
