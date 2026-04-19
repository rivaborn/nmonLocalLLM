# src/nmon/ui/__init__.py

## Purpose
This file serves as a package marker and re-export hub for the nmon UI components, making them conveniently accessible to users of the nmon.ui package.

## Responsibilities
- Provides package-level import functionality for UI modules
- Acts as a central re-export point for UI components
- Handles optional imports with graceful fallbacks for unimplemented modules
- Maintains package structure for the UI subpackage

## Key Types
- App (Class): Main application class for the TUI interface
- Dashboard (Class): Primary dashboard view component
- TempTab (Class): Temperature monitoring tab
- PowerTab (Class): Power consumption monitoring tab
- LLMTab (Class): LLM-related monitoring tab
- AlertBar (Class): Alert notification component

## Key Functions
### None

## Globals
### None

## Dependencies
- .app module
- .dashboard module
- .temp_tab module
- .power_tab module
- .llm_tab module
- .alert_bar module
