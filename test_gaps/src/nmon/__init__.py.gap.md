# src/nmon/__init__.py

## Overall
NONE — no dedicated test file exists for this module.

## Must Test (Highest Risk First)
1. [HIGH] `Settings`: validate config parsing and default values for all fields
2. [HIGH] `UserPrefs`: test preference loading and validation of threshold settings
3. [HIGH] `GpuSnapshot`: verify GPU data structure initialization and field access
4. [HIGH] `OllamaSnapshot`: test Ollama data structure initialization and field access
5. [HIGH] `AlertState`: validate alert state management and threshold comparisons
6. [HIGH] `HistoryStore`: test database connection and query behavior
7. [MEDIUM] `DashboardView`: verify view rendering logic and widget layout
8. [MEDIUM] `render_temp_view`: test temperature view rendering with different prefs
9. [MEDIUM] `PowerView`: validate power metrics display and formatting
10. [LOW] `Sparkline`: test sparkline widget rendering and data point handling

## Mock Strategy
- `Settings`: mock config file reading and environment variable parsing
- `UserPrefs`: mock JSON file loading and validation
- `GpuSnapshot`: mock NVML GPU data retrieval
- `OllamaSnapshot`: mock Ollama API responses
- `AlertState`: mock threshold comparisons and alert timing
- `HistoryStore`: mock SQLite database operations
- `DashboardView`: mock Rich console rendering
- `render_temp_view`: mock preference loading and view updates
- `PowerView`: mock power metrics display
- `Sparkline`: mock data point rendering and scaling
