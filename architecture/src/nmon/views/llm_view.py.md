# src/nmon/views/llm_view.py

## Purpose
Provides a TUI view for displaying LLM server resource usage metrics using sparklines. Handles offline state and integrates with history data.

## Responsibilities
- Render LLM usage dashboard with GPU/CPU sparklines
- Handle offline Ollama state with informative message
- Fetch historical usage data for visualization
- Create Rich layout structure for display

## Key Types
- OllamaSnapshot (Class): Represents Ollama server connection state
- HistoryStore (Class): Manages historical metric storage and retrieval
- Settings (Class): Application configuration settings
- UserPrefs (Class): User-specific display preferences
- Sparkline (Class): Rich widget for time-series visualization
- Layout (Class): Rich layout container for TUI structure
- Panel (Class): Rich panel container for display elements

## Key Functions
### render_llm_view
- Purpose: Generate TUI layout showing LLM resource usage or offline message
- Calls: history_store.get_gpu_usage_series, history_store.get_cpu_usage_series, Sparkline.__init__

## Globals
None

## Dependencies
- nmon.ollama_monitor.OllamaSnapshot
- nmon.history.HistoryStore
- nmon.config.Settings
- nmon.config.UserPrefs
- nmon.alerts.AlertState
- nmon.widgets.sparkline.Sparkline
- rich.layout.Layout
- rich.panel.Panel
