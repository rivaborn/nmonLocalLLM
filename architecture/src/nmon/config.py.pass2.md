# src/nmon/config.py - Enhanced Analysis

## Architectural Role
Manages application configuration lifecycle, bridging environment-based settings with user preferences. Acts as a central configuration hub that supports both runtime customization and persistent user state management.

## Cross-References
### Incoming
- `src/nmon/main.py` (loads settings and prefs at startup)
- `src/nmon/ui/dashboard.py` (accesses user prefs for display configuration)
- `src/nmon/cli.py` (reads settings for command-line argument parsing)

### Outgoing
- `src/nmon/db.py` (uses `db_path` setting for SQLite database location)
- `src/nmon/gpu/monitor.py` (reads monitor enable flags from settings)
- `src/nmon/ui/render.py` (consumes user prefs for TUI layout decisions)

## Design Patterns
- **Configuration-Dataclass Pattern**: Uses Pydantic BaseSettings for structured environment loading and dataclass for user preferences, separating concerns between system and user configuration.
- **Fail-Safe Defaults Pattern**: Gracefully handles missing or corrupted preference files by returning default values, ensuring application stability.
- **Lazy Loading Pattern**: Preferences are only loaded when explicitly requested, deferring I/O operations until needed.
