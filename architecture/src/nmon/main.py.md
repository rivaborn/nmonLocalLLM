# src/nmon/main.py

## Purpose
Main entry point for the nmon application that initializes monitoring components and starts the TUI.

## Responsibilities
- Load application configuration from environment and persistent storage
- Initialize GPU and LLM monitoring components
- Handle Ollama detection and conditional LLM monitoring
- Start all monitoring processes and launch the Textual UI application

## Key Types
- AppConfig (Class): Configuration container for application settings
- GpuMonitor (Class): GPU metrics monitoring component
- LlmMonitor (Class): LLM metrics monitoring component
- RingBuffer (Class): Circular buffer for storing metric samples

## Key Functions
### run
- Purpose: Main application bootstrap function that initializes components and starts the UI
- Calls: load_from_env, load_persistent_settings, GpuMonitor.__init__, LlmMonitor.__init__, LlmMonitor.detect, GpuMonitor.start, LlmMonitor.start, NmonApp.__init__, NmonApp.run

## Globals
None

## Dependencies
- AppConfig from nmon.config
- GpuMonitor from nmon.gpu.monitor
- LlmMonitor from nmon.llm.monitor
- RingBuffer from nmon.storage.ring_buffer
- NmonApp from nmon.ui.app
- asyncio module
- load_from_env function
- load_persistent_settings function
