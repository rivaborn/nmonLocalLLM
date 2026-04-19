# src/nmon/__init__.py

## Purpose
This file serves as the package marker and re-exports key components from submodules to provide convenient import paths for users of the nmon system.

## Responsibilities
- Exposes core monitoring and UI components for simplified imports
- Manages package version and metadata
- Handles import errors gracefully with logging
- Provides a consistent public API through `__all__`
- Enables direct imports like `from nmon import GPUMonitor, App`

## Key Types
- GPUMonitor (Class): GPU monitoring component
- LLMMonitor (Class): LLM monitoring component  
- RingBuffer (Class): Storage buffer for samples
- App (Class): Main application controller
- Dashboard (Class): UI dashboard component
- Config (Class): Configuration management

## Key Functions
### None

## Globals
- __version__ (str): Package version identifier
- __author__ (str): Package author name
- __email__ (str): Package author email
- __all__ (list): Exported component names

## Dependencies
- .gpu.monitor.GPUMonitor
- .llm.monitor.LLMMonitor
- .storage.ring_buffer.RingBuffer
- .ui.app.App
- .ui.dashboard.Dashboard
- .config.Config
- logging module
