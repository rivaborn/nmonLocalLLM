# Module: `src/nmon/alerts.py`

## Role
Provides alert state management for the nmon terminal dashboard, computing and rendering alert states based on Ollama snapshot data.

## Contract: `AlertState`

### `__init__(params)`
- **Requires:** `active: bool`, `message: str`, `color: str` (must be "orange" or "red"), `expires_at: float` (valid Unix timestamp)
- **Establishes:** All fields are set to provided values; object is immutable due to `@dataclass`
- **Raises:** None

### `__post_init__(params)`
- **Requires:** `color: str` must be one of "orange" or "red"
- **Establishes:** `color` field validated to be "orange" or "red"
- **Raises:** `ValueError` if `color` is not "orange" or "red"

## Contract: `compute_alert(snapshot, settings, now) -> Optional[AlertState]`
- **Requires:** `snapshot: OllamaSnapshot` must be a valid instance with `reachable` and `gpu_use_pct` fields; `settings: Settings` must be a valid instance with `offload_alert_pct` and `min_alert_display_s` fields; `now: float` must be a valid Unix timestamp
- **Guarantees:** Returns `AlertState` with `active=True` if alert conditions are met, otherwise returns `None`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe

## Module Invariants
None

## Resource Lifecycle
None
