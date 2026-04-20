# src/nmon/config.py

## Purpose
Handles application configuration loading and saving, including settings from environment variables and user preferences from JSON.

## Responsibilities
- Load application settings from environment variables using Pydantic
- Manage user preferences via JSON file I/O
- Provide default values for configuration fields
- Handle errors during preference file loading/saving
- Support optional custom preference file paths

## Key Types
- UserPrefs (Dataclass): Stores user-adjustable display preferences
- Settings (BaseSettings): Application configuration from environment variables

## Key Functions
### load_settings
- Purpose: Load application settings from environment variables using Pydantic validation
- Calls: Settings.model_validate_env()

### load_user_prefs
- Purpose: Load user preferences from JSON file or return defaults
- Calls: json.load(), Path.exists(), logger.warning()

### save_user_prefs
- Purpose: Save user preferences to a JSON file
- Calls: json.dump(), Path(), logger.warning()

## Globals
- logger (Logger): Module-level logger instance for configuration operations

## Dependencies
- json, logging, pathlib.Path, typing.Optional
- pydantic_settings.BaseSettings, dataclasses.dataclass
- json.JSONDecodeError, IOError (from try/except blocks)
