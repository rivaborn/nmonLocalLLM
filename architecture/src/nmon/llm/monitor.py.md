# src/nmon/llm/monitor.py

## Purpose
Implements an asynchronous monitor for LLM model statistics using the Ollama API, collecting and storing samples in a ring buffer.

## Responsibilities
- Detect availability of Ollama API endpoint
- Poll Ollama API for model status and resource usage
- Parse API responses into structured LlmSample objects
- Manage async polling loop with start/stop controls
- Store collected samples in a shared ring buffer

## Key Types
- LlmMonitor (Class): Main monitor class managing async polling and data collection
- LlmSample (Class): Data structure representing parsed LLM model metrics

## Key Functions
### detect
- Purpose: Check if Ollama API is reachable and responding
- Calls: None

### start
- Purpose: Begin async polling loop
- Calls: None

### stop
- Purpose: Cancel active polling task
- Calls: None

### _poll
- Purpose: Fetch current model status from Ollama API
- Calls: None

### _parse_response
- Purpose: Convert raw API JSON into structured LlmSample
- Calls: None

### _poll_loop
- Purpose: Continuous polling loop that collects and stores samples
- Calls: _poll, buffer.append

## Globals
- TOTAL_LAYERS_ESTIMATE (int): Constant used for calculating layer offload ratios
- logger (logging.Logger): Module-level logger instance

## Dependencies
- asyncio, logging, typing.Optional
- httpx.ConnectError, httpx.HTTPError, httpx.TimeoutException
- nmon.config.AppConfig, nmon.config.ollama_url
- nmon.llm.protocol.LlmSample
- nmon.storage.ring_buffer.RingBuffer
