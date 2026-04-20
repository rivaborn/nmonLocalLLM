# src/nmon/views/__init__.py - Enhanced Analysis

## Architectural Role
This file serves as the view module facade, exposing the core dashboard and metric-specific views (temperature, power, LLM) to the main application controller. It coordinates the TUI rendering components and provides the interface through which the main loop invokes different visualization modes.

## Cross-References
### Incoming
- `src/nmon/__init__.py` calls `render_temp_view` and `update_temp_prefs` 
- `src/nmon/__init__.py` imports and uses `DashboardView` and `PowerView`

### Outgoing
- Imports `DashboardView` from `nmon.views.dashboard_view`
- Imports `render_temp_view` and `update_temp_prefs` from `nmon.views.temp_view`
- Imports `PowerView` from `nmon.views.power_view`
- Imports `render_llm_view` from `nmon.views.llm_view`

## Design Patterns
- **Facade Pattern**: Provides unified interface to complex view subsystems
- **Module Organization Pattern**: Groups related view components under single import namespace
- **Separation of Concerns**: Each view module handles distinct GPU metric visualization logic
