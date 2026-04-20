# src/nmon/db.py

## Purpose
Manages database operations for storing GPU and Ollama metrics collected by the nmon system. Provides functions for initializing the database schema, pruning old data, and flushing collected snapshots to persistent storage.

## Responsibilities
- Initialize SQLite database with required tables for GPU and Ollama metrics
- Remove outdated metric data based on configurable history duration
- Insert collected GPU and Ollama snapshots into the database
- Handle database connection management and error logging

## Key Types
- DbConnection (Alias): sqlite3.Connection type alias for database connections

## Key Functions
### init_db
- Purpose: Creates necessary database tables for GPU and Ollama metrics if they don't exist
- Calls: sqlite3.connect, cursor.execute

### prune_old_data
- Purpose: Deletes metric records older than specified history duration
- Calls: sqlite3.connect, cursor.execute

### flush_to_db
- Purpose: Inserts collected GPU and Ollama snapshots into their respective database tables
- Calls: sqlite3.connect, cursor.execute

## Globals
None

## Dependencies
- sqlite3: Database interface
- time: For timestamp calculations
- logging: Error logging
- typing: Type hints (List, Optional)
- nmon.gpu_monitor.GpuSnapshot: GPU metric data structure
- nmon.ollama_monitor.OllamaSnapshot: Ollama metric data structure
