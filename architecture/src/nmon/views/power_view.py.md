# src/nmon/views/power_view.py

## Purpose
Renders the power consumption dashboard view in the nmon terminal application, displaying GPU power charts and optional Ollama process information.

## Responsibilities
- Render power consumption charts using sparkline widgets for each GPU
- Display Ollama process information when available
- Manage time range selection for historical data visualization
- Compose rich layout with header, content area, and footer
- Integrate historical power data from HistoryStore

## Key Types
- PowerView (Class): Main view controller for power dashboard rendering

## Key Functions
### render
- Purpose: Compose and return the complete power view layout with all components
- Calls: _render_gpu_charts, _render_ollama_info

### _render_gpu_charts
- Purpose: Generate sparkline charts for each GPU's power consumption history
- Calls: history_store.get_power_history

### _render_ollama_info
- Purpose: Create panel displaying Ollama process metrics in a formatted table
- Calls: None

## Globals
None

## Dependencies
- nmon.gpu_monitor.GpuSnapshot
- nmon.ollama_monitor.OllamaSnapshot
- nmon.history.HistoryStore
- nmon.config.UserPrefs
- nmon.config.Settings
- nmon.widgets.sparkline.Sparkline
- rich.layout.Layout
- rich.panel.Panel
- rich.table.Table
- rich.text.Text
- rich.print
