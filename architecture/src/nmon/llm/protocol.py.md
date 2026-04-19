# src/nmon/llm/protocol.py

## Purpose
Defines data structures and protocol interface for monitoring LLM server resource utilization, specifically for Ollama servers.

## Responsibilities
- Define LLM monitoring data schema via LlmSample dataclass
- Specify required interface methods for LLM monitoring via LlmMonitorProtocol
- Provide parsing logic for Ollama API responses into structured data
- Support asynchronous detection and polling of LLM server metrics

## Key Types
- LlmSample (Dataclass): Represents a single snapshot of LLM server resource usage
- LlmMonitorProtocol (Protocol): Defines the interface for LLM monitoring implementations

## Key Functions
### detect
- Purpose: Asynchronously check if Ollama server is reachable
- Calls: None visible

### start
- Purpose: Begin the LLM monitoring loop
- Calls: None visible

### stop
- Purpose: Terminate the LLM monitoring loop
- Calls: None visible

### _poll
- Purpose: Fetch current LLM resource utilization data from server
- Calls: None visible

### _parse_response
- Purpose: Convert raw Ollama API JSON response into structured LlmSample
- Calls: None visible

## Globals
None

## Dependencies
- dataclasses.dataclass
- typing.Protocol
- LlmSample (defined in same module)
- LlmMonitorProtocol (defined in same module)
