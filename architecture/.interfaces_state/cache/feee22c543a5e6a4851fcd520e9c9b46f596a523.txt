# Module: `src/nmon/ollama_monitor.py`

## Role
Provides monitoring capabilities for Ollama inference server, collecting model load status and resource utilization metrics.

## Contract: `OllamaSnapshot`

### `__init__(timestamp: float, reachable: bool, loaded_model: Optional[str], model_size_bytes: Optional[int], gpu_use_pct: Optional[float], cpu_use_pct: Optional[float], gpu_layers: Optional[int], total_layers: Optional[int])`
- **Requires:** `timestamp` must be a valid float; `reachable` must be a bool; all other fields must be either valid types or None
- **Establishes:** All fields are stored as provided; object is immutable due to `@dataclass`
- **Raises:** None

## Contract: `OllamaMonitorProtocol`

### `poll(client: httpx.AsyncClient) -> OllamaSnapshot`
- **Requires:** `client` must be a valid `httpx.AsyncClient` instance
- **Guarantees:** Returns an `OllamaSnapshot` object with populated fields based on Ollama API response
- **Raises:** `NotImplementedError` -- method is abstract and must be overridden
- **Silent failure:** None
- **Thread safety:** unsafe

## Contract: `OllamaMonitor`

### `__init__(settings: Settings) -> None`
- **Requires:** `settings` must be a valid `Settings` instance with `ollama_base_url` attribute
- **Establishes:** Initializes internal state with `settings`, sets `ollama_detected` to False, and `ollama_client` to None
- **Raises:** None

### `probe_ollama(client: httpx.AsyncClient, base_url: str) -> bool`
- **Requires:** `client` must be a valid `httpx.AsyncClient` instance; `base_url` must be a string
- **Guarantees:** Returns True if Ollama API is reachable and responds with 2xx status; False otherwise
- **Raises:** None
- **Silent failure:** Returns False on any exception (including network errors, HTTP errors, JSON parsing errors)
- **Thread safety:** unsafe

### `poll(client: httpx.AsyncClient) -> OllamaSnapshot`
- **Requires:** `client` must be a valid `httpx.AsyncClient` instance
- **Guarantees:** Returns an `OllamaSnapshot` with populated fields if Ollama is reachable; otherwise returns snapshot with `reachable=False`
- **Raises:** None
- **Silent failure:** 
  - Returns default snapshot with `reachable=False` if Ollama is unreachable or API returns invalid JSON
  - Returns `None` for all numeric fields if model information is missing from API response
  - May silently fail to calculate GPU/CPU percentages if `gpu_layers` or `total_layers` are invalid
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
None
