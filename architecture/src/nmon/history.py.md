# src/nmon/history.py

## Purpose
Manages historical GPU and Ollama metrics storage, retrieval, and persistence in SQLite database.

## Responsibilities
- Load historical metrics from SQLite on initialization
- Store new GPU and Ollama samples in memory with size limits
- Provide time-series queries for GPU and Ollama metrics
- Flush samples to SQLite database periodically
- Trim excess samples based on configured history duration

## Key Types
- HistoryStore (Class): Main class managing historical metric storage and retrieval

## Key Functions
### __init__
- Purpose: Initialize history store and load existing data from database
- Calls: DbConnection, GpuSnapshot, OllamaSnapshot

### add_gpu_samples
- Purpose: Add new GPU samples and manage storage limits
- Calls: DbConnection, flush_to_db

### add_ollama_sample
- Purpose: Add new Ollama sample and manage storage limits
- Calls: None

### gpu_series
- Purpose: Retrieve GPU samples for a specific GPU within time range
- Calls: time.time

### ollama_series
- Purpose: Retrieve Ollama samples within time range
- Calls: time.time

### gpu_stat
- Purpose: Calculate statistics (max, avg, current) for GPU metrics
- Calls: gpu_series, getattr

### flush_to_db
- Purpose: Persist all samples to SQLite database
- Calls: DbConnection, time.time

## Globals
None

## Dependencies
- collections.deque
- typing.Literal
- time
- logging
- nmon.gpu_monitor.GpuSnapshot
- nmon.ollama_monitor.OllamaSnapshot
- nmon.config.Settings
- nmon.db.DbConnection
