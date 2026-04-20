# src/nmon/views/__init__.py

## Overall
NONE — no dedicated test file exists for this module.

## Must Test (Highest Risk First)
1. [HIGH] `DashboardView`: test view initialization, rendering logic, and widget updates
2. [HIGH] `render_temp_view`: verify temperature view rendering with different prefs and data
3. [HIGH] `update_temp_prefs`: test preference updates and validation logic
4. [HIGH] `PowerView`: validate power view rendering and data display
5. [HIGH] `render_llm_view`: test LLM view rendering with mock Ollama data
6. [MEDIUM] `DashboardView.__init__`: ensure proper widget setup and layout
7. [MEDIUM] `PowerView.__init__`: verify power view initialization and data binding
8. [MEDIUM] `render_temp_view`: test with edge cases like empty data or invalid prefs
9. [MEDIUM] `update_temp_prefs`: validate threshold updates and UI state changes
10. [LOW] `render_llm_view`: test view rendering with various model states and error conditions

## Mock Strategy
- `nmon.views.dashboard_view.DashboardView`: mock `rich.console.Console` and widget rendering
- `nmon.views.temp_view.render_temp_view`: mock `rich.console.Console` and `nmon.gpu_monitor.GpuSnapshot` data
- `nmon.views.temp_view.update_temp_prefs`: mock `nmon.config.UserPrefs` and preference persistence
- `nmon.views.power_view.PowerView`: mock `rich.console.Console` and power data sources
- `nmon.views.llm_view.render_llm_view`: mock `rich.console.Console` and `nmon.ollama_monitor.OllamaSnapshot` data
