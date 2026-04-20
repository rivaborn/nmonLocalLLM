# src/nmon/views/dashboard_view.py

## Purpose
Displays a terminal dashboard showing GPU metrics, memory junction temperatures (if supported), and Ollama LLM usage. Renders a Rich-based layout with configurable widgets.

## Responsibilities
- Manage dashboard layout structure with alert bar and GPU/LLM panels
- Poll GPU monitor for current metrics and render GPU panels
- Fetch and display Ollama LLM usage when available
- Handle conditional rendering of memory junction temperature data
- Coordinate with history store for Ollama snapshot data

## Key Types
- DashboardView (Class): Main dashboard view controller managing layout and rendering

## Key Functions
### render
- Purpose: Build and return the complete dashboard layout with GPU and LLM panels
- Calls: _create_gpu_panel, _create_llm_panel, gpu_monitor.poll, history_store.ollama_series

### _create_gpu_panel
- Purpose: Generate a Rich Panel displaying individual GPU metrics
- Calls: None

### _create_llm_panel
- Purpose: Generate a Rich Panel displaying Ollama LLM usage metrics
- Calls: None

## Globals
None

## Dependencies
- GpuSnapshot, OllamaSnapshot from nmon.gpu_monitor and nmon.ollama_monitor
- UserPrefs, Settings from nmon.config
- HistoryStore from nmon.history
- AlertState from nmon.alerts
- Sparkline from nmon.widgets.sparkline
- Layout, Panel, Text, Columns, Table, ROUNDED from rich
- AlertBar from nmon.widgets.alert_bar
- time from python standard library
