# src/nmon/views/temp_view.py

## Purpose
Provides functions to render and update the temperature monitoring view in the nmon terminal dashboard, displaying GPU core and memory temperatures over time.

## Responsibilities
- Render temperature view with sparklines for GPU core and memory temperatures
- Handle user input to adjust temperature threshold and toggle display options
- Integrate historical temperature data from the history store
- Create Rich layout structure for the temperature dashboard

## Key Types
- GpuSnapshot (Class): Represents a snapshot of GPU metrics
- OllamaSnapshot (Class): Represents a snapshot of Ollama metrics
- UserPrefs (Class): Stores user preferences for display options
- HistoryStore (Class): Provides access to historical GPU data
- Settings (Class): Application configuration settings
- Sparkline (Class): Renders temperature data as sparkline charts
- ThresholdLine (Class): Represents threshold line for temperature charts

## Key Functions

### render_temp_view
- Purpose: Creates and returns a Rich Layout object displaying GPU temperature data
- Calls: history_store.gpu_series, history_store.gpu_mem_series, Sparkline.__init__, ThresholdLine.__init__

### update_temp_prefs
- Purpose: Updates user preferences for temperature view based on keyboard input
- Calls: None

## Globals
None

## Dependencies
- rich.layout.Layout, rich.panel.Panel, rich.text.Text, rich.console.Console
- nmon.gpu_monitor.GpuSnapshot, nmon.ollama_monitor.OllamaSnapshot
- nmon.config.Settings, nmon.config.UserPrefs
- nmon.history.HistoryStore
- nmon.widgets.sparkline.Sparkline, nmon.widgets.sparkline.ThresholdLine
