# Module: `src/nmon/config.py`

## Role
Provides configuration loading and persistence for the nmon terminal monitoring application, handling both application settings and user preferences.

## Contract: `Settings`

### `__init__(params)`
- **Requires:** No parameters required; uses environment variable parsing via Pydantic
- **Establishes:** Instance with validated configuration fields; `env_prefix` set to "NMON_"
- **Raises:** `pydantic_settings.SettingsError` — if environment variable parsing fails

### `model_validate_env() -> Settings`
- **Requires:** Environment variables may be present but are not required
- **Guarantees:** Returns a fully initialized `Settings` object with validated fields
- **Raises:** `pydantic_settings.SettingsError` — if validation fails
- **Silent failure:** None
- **Thread safety:** unsafe

## Contract: `UserPrefs`

### `__init__(params)`
- **Requires:** All fields are optional with default values; no parameters required
- **Establishes:** Instance with default or provided preference values
- **Raises:** None

## Contract: `load_settings() -> Settings`
- **Requires:** Environment variables may be present but are not required
- **Guarantees:** Returns a validated `Settings` object with default or environment-provided values
- **Raises:** `pydantic_settings.SettingsError` — if validation fails
- **Silent failure:** None
- **Thread safety:** unsafe

## Contract: `load_user_prefs(prefs_path: Optional[str] = None) -> UserPrefs`
- **Requires:** `prefs_path` must be a valid string path or None
- **Guarantees:** Returns `UserPrefs` object with loaded or default values
- **Raises:** `json.JSONDecodeError` — if JSON file is malformed; `IOError` — if file cannot be read
- **Silent failure:** Returns default `UserPrefs()` if file does not exist or fails to load; logs warning
- **Thread safety:** unsafe

## Contract: `save_user_prefs(prefs: UserPrefs, prefs_path: Optional[str] = None) -> None`
- **Requires:** `prefs` must be a valid `UserPrefs` instance; `prefs_path` must be a valid string path or None
- **Guarantees:** Preferences are written to JSON file at specified path
- **Raises:** `IOError` — if file cannot be written
- **Silent failure:** Logs warning if file write fails; no exception raised
- **Thread safety:** unsafe

## Module Invariants
None

## Resource Lifecycle
- File handles opened for reading/writing preferences are automatically closed by Python's `with` statement
- No long-lived connections or threads held
- None
