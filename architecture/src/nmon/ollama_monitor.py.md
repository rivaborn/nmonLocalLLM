# src/nmon/ollama_monitor.py

## Purpose
Provides monitoring capabilities for Ollama inference server, collecting model load status and resource utilization metrics.

## Responsibilities
- Detect and verify connectivity to Ollama server endpoint
- Fetch running model information and resource usage from Ollama API
- Convert Ollama resource data into standardized snapshot format
- Handle network errors and unreachable server states
- Maintain connection state tracking for Ollama server

## Key Types
- OllamaSnapshot (Dataclass): Container for Ollama monitoring metrics and status
- OllamaMonitorProtocol (Protocol): Interface defining Ollama monitoring contract
- OllamaMonitor (Class): Concrete implementation of Ollama monitoring logic

## Key Functions
### probe_ollama
- Purpose: Test connectivity to Ollama server endpoint
- Calls: None

### poll
- Purpose: Fetch current Ollama model status and resource utilization
- Calls: probe_ollama, httpx.AsyncClient.get

## Globals
None

## Dependencies
- httpx.AsyncClient
- nmon.config.Settings
- dataclasses.dataclass
- typing.Optional
