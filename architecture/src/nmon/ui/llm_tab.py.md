# src/nmon/ui/llm_tab.py

## Purpose
Implements a Textual widget for displaying LLM server GPU/CPU utilization over time in a TUI dashboard.

## Responsibilities
- Render GPU/CPU utilization chart using Plot widget
- Handle time-range selection for chart data
- Update chart data periodically from ring buffer
- Respond to configuration changes and button presses

## Key Types
- LlmTab (Class): Main widget for LLM utilization visualization

## Key Functions
### update_chart
- Purpose: Fetches samples and updates the Plot widget with GPU/CPU utilization data
- Calls: buffer.since, plot.clear, plot.add_series

### on_button_pressed
- Purpose: Handles time-range button selection and updates chart
- Calls: update_chart

### _on_config_change
- Purpose: Re-starts update timer when config changes
- Calls: set_interval

## Globals
None

## Dependencies
- nmon.llm.protocol.LlmSample
- nmon.storage.ring_buffer.RingBuffer
- nmon.config.AppConfig
- textual.containers.Static
- textual.widgets.Plot
- textual.widgets.Button
- textual.app.ComposeResult
- textual.app.on_mount
- textual.widgets.ButtonPressed
- textual.app.KeyEvent
