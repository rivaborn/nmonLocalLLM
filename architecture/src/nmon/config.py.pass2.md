# src/nmon/config.py - Enhanced Analysis

## Architectural Role
Handles application configuration lifecycle from environment loading to persistent storage. Serves as the central configuration coordinator that merges runtime settings with user preferences, providing a unified interface for all subsystems to access application parameters.

## Cross-References
### Incoming
- `src/nmon/main.py` - Calls `load_from_env()` and `load_persistent_settings()` during startup
- `src/nmon/ui/dashboard.py` - References `AppConfig` for threshold visibility settings
- `src/nmon/storage/ring_buffer.py` - Accesses `poll_interval_s` for sampling control

### Outgoing
- `os` - File system operations and environment variable access
- `json` - Configuration serialization and persistence
- `platformdirs` - Cross-platform user configuration directory resolution
- `src/nmon/storage/ring_buffer.py` - Indirect dependency via `poll_interval_s` usage

## Design Patterns
- **Configuration Merge Pattern** - Combines environment and persistent settings with clear precedence, enabling flexible deployment scenarios
- **Fail-Safe Persistence Pattern** - Gracefully handles I/O errors during config save/load, ensuring application stability
- **Dataclass-Driven Configuration** - Uses Python dataclasses for type safety and clear configuration schema definition
