# Module: `src/nmon/config.py`

## Role
Provides configuration loading and persistence functionality for the nmon system, managing application settings from environment variables and persistent storage.

## Contract: `AppConfig`

### `__init__(params)`
- **Requires:** No parameters required; all fields have default values
- **Establishes:** All fields initialized with specified default values; `ollama_url` is string, numeric fields are float, boolean fields are bool
- **Raises:** None

### `__post_init__(params)`
- **Requires:** No parameters required
- **Establishes:** No additional invariants beyond field initialization
- **Raises:** None

## Contract: `load_from_env() -> AppConfig`

### `load_from_env() -> AppConfig`
- **Requires:** Environment variables may contain string representations of numeric/boolean values
- **Guarantees:** Returns AppConfig instance with all fields populated; defaults used when environment variables missing
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** unsafe

## Contract: `load_persistent_settings() -> AppConfig`

### `load_persistent_settings() -> AppConfig`
- **Requires:** `platformdirs.user_config_dir` function must be available and functional
- **Guarantees:** Returns AppConfig instance with persisted values or defaults; `mem_junction_visible` always set to `True` (not persisted)
- **Raises:** None
- **Silent failure:** If JSON file cannot be read or parsed, returns default AppConfig without error reporting
- **Thread safety:** unsafe

## Contract: `save_persistent_settings(config: AppConfig) -> None`

### `save_persistent_settings(config: AppConfig) -> None`
- **Requires:** `config` parameter must be an AppConfig instance with valid field values
- **Guarantees:** Configuration values are written to JSON file in user config directory
- **Raises:** None
- **Silent failure:** If I/O error occurs during file write, operation silently fails and no error is reported
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
- Creates directory using `os.makedirs` if it doesn't exist
- Opens and closes JSON files for reading and writing
- No long-lived resources or explicit cleanup required
- Directory creation and file I/O operations are handled per-call
