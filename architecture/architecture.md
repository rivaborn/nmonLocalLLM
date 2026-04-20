# Architecture Overview

## Repository Shape
- `src/nmon/` contains all application modules organized by functionality
- `src/nmon/views/` holds UI rendering components for different dashboard sections
- `src/nmon/widgets/` contains reusable Rich-based UI elements
- `src/nmon/` root includes main entry points and core system components

## Major Subsystems

### Monitoring
- Purpose: Collects real-time GPU and Ollama metrics using NVML and nvidia-smi
- Key files: `gpu_monitor.py`, `ollama_monitor.py`
- Dependencies: `db.py` for data storage

### Data Management
- Purpose: Stores and retrieves GPU/Ollama metrics in SQLite database
- Key files: `db.py`, `history.py`
- Dependencies: `gpu_monitor.py`, `ollama_monitor.py`

### User Interface
- Purpose: Renders live TUI dashboards with configurable widgets using Rich
- Key files: `app.py`, `dashboard_view.py`, `llm_view.py`, `power_view.py`, `temp_view.py`
- Dependencies: `alerts.py`, `db.py`

### Configuration & Alerts
- Purpose: Manages application settings and GPU alert state computation
- Key files: `config.py`, `alerts.py`
- Dependencies: `app.py`, `gpu_monitor.py`

## Key Runtime Flows

### Initialization
- Main entry point (`main.py`) initializes components including config loading, database setup, and monitor instantiation
- UI application (`app.py`) is created with configured views and widgets
- Monitoring components (`gpu_monitor.py`, `ollama_monitor.py`) start collecting data

### Main Loop / Per-Frame
- Application event loop processes user input and updates UI
- Monitoring components periodically collect new samples
- Data is flushed to database (`db.py`) and rendered in dashboard views
- Alert state is computed and displayed in alert bar widget

### Shutdown
- Signal handlers in `main.py` trigger graceful shutdown
- Pending database writes are flushed
- Monitoring threads are terminated
- UI is cleanly closed

## Notable Details
- Global state managed through application lifecycle in `app.py`
- Data flow follows a pattern of collection → storage → rendering
- Views are decoupled from data sources via `db.py` interface
- Rich-based widgets provide reusable UI components for different metric types
- Configuration is loaded from environment variables and JSON preferences
