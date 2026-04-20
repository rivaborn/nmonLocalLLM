# src/nmon/main.py

## Purpose
Main entry point for the nmon system monitor application. Initializes components and handles application lifecycle including signal handling for graceful shutdown.

## Responsibilities
- Load application settings from environment
- Initialize GPU and Ollama monitors with configuration
- Manage application lifecycle and signal handlers
- Coordinate startup and shutdown of monitoring components
- Handle pynvml initialization failures

## Key Types
- NmonApp (Class): Main application controller
- Settings (Class): Configuration settings model
- UserPrefs (Class): User preference model
- HistoryStore (Class): Database storage for metrics
- GpuMonitorProtocol (Class): GPU monitoring interface
- OllamaMonitorProtocol (Class): Ollama monitoring interface

## Key Functions
### main
- Purpose: Entry point that initializes all components and starts the application
- Calls: Settings.model_validate_env, HistoryStore.__init__, GpuMonitorProtocol.__init__, OllamaMonitorProtocol.__init__, UserPrefs.model_validate_json, NmonApp.__init__, signal.signal, app.run, gpu_monitor.stop, ollama_monitor.stop, history_store.flush

## Globals
- None

## Dependencies
- signal, time, sys, typing.NoReturn
- nmon.app.NmonApp
- nmon.config.Settings, nmon.config.UserPrefs
- nmon.history.HistoryStore
- nmon.gpu_monitor.GpuMonitorProtocol
- nmon.ollama_monitor.OllamaMonitorProtocol
