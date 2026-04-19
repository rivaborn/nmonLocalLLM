# Architecture Overview

## Repository Shape
- `src/nmon/` contains core application logic organized by concern: GPU monitoring, LLM monitoring, storage, UI, and configuration
- `src/nmon/gpu/` and `src/nmon/llm/` modules handle respective monitoring subsystems with data collection and protocol definitions
- `src/nmon/ui/` implements the Rich-based TUI with dashboard tabs and widgets
- `src/nmon/storage/` manages time-series data persistence using SQLite and ring buffers

## Major Subsystems

### GPU Monitoring
- Purpose: Collects GPU metrics via NVML and nvidia-smi, stores samples in a ring buffer
- Key files: `gpu/monitor.py`, `gpu/protocol.py`
- Dependencies: `storage/ring_buffer.py`, `config.py`

### LLM Monitoring
- Purpose: Collects LLM model statistics from Ollama API and stores samples in a ring buffer
- Key files: `llm/monitor.py`, `llm/protocol.py`
- Dependencies: `storage/ring_buffer.py`, `config.py`

### Storage
- Purpose: Provides time-series data persistence and retrieval using SQLite and ring buffers
- Key files: `storage/database.py`, `storage/ring_buffer.py`
- Dependencies: None

### UI
- Purpose: Renders live TUI dashboard with configurable widgets for GPU/LLM metrics
- Key files: `ui/app.py`, `ui/dashboard.py`, `ui/llm_tab.py`, `ui/power_tab.py`, `ui/temp_tab.py`
- Dependencies: `gpu/monitor.py`, `llm/monitor.py`, `storage/ring_buffer.py`

## Key Runtime Flows

### Initialization
- Load configuration from TOML/env vars via `config.py`
- Initialize GPU and LLM monitors with ring buffer storage
- Setup SQLite database for persistent storage
- Start asynchronous polling loops for data collection

### Main Loop / Per-Frame
- Update TUI with latest samples from ring buffers
- Render dashboard tabs with real-time GPU/LLM metrics
- Handle user input and UI events via Textual framework
- Periodically persist samples to SQLite database

### Shutdown
- Stop asynchronous polling loops
- Flush pending samples to database
- Clean up UI components and resources

## Notable Details
- Global state managed through singleton ring buffers and database connections
- Ownership boundaries: monitors own data collection, UI owns rendering, storage owns persistence
- Asynchronous polling pattern used for both GPU and LLM monitoring
- Time-window queries supported via ring buffer with fixed-size history
- Configurable widgets in TUI allow dynamic dashboard layout changes
