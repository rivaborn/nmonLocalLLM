# src/nmon/config.py

## Purpose
Defines application configuration management including environment variable loading, persistent settings storage, and default value handling.

## Responsibilities
- Load application settings from environment variables with sensible defaults
- Persist temperature threshold settings to JSON configuration file
- Load previously saved configuration from user's config directory
- Merge environment and persistent settings with proper precedence

## Key Types
- AppConfig (Dataclass): Holds all application configuration parameters with default values

## Key Functions
### load_from_env
- Purpose: Parse environment variables into AppConfig instance with defaults
- Calls: None

### load_persistent_settings
- Purpose: Load saved configuration from JSON file in user directory
- Calls: os.path.exists, json.load, os.makedirs

### save_persistent_settings
- Purpose: Save temperature threshold settings to JSON configuration file
- Calls: os.makedirs, json.dump

## Globals
None

## Dependencies
- os: Environment variable access, file operations
- json: Configuration serialization/deserialization
- platformdirs: User configuration directory path resolution
- dataclasses.dataclass: AppConfig class definition
- typing.TYPE_CHECKING: Conditional imports for type hints only
