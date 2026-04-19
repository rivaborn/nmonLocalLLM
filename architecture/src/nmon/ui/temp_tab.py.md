# src/nmon/ui/temp_tab.py

## Purpose
Displays GPU temperature data over time in a Textual TUI with interactive controls for time range, threshold visibility, and temperature metrics.

## Responsibilities
- Manage UI elements for temperature visualization including plots and control buttons
- Handle user interactions for time range selection and threshold adjustments
- Update GPU temperature plots with current data from ring buffer
- Synchronize configuration changes to persistent storage
- Process keyboard and button events for user controls

## Key Types
- TemperatureTab (Class): Main UI component for temperature monitoring

## Key Functions
### __init__
- Purpose: Initialize temperature tab with GPU monitor, config, and buffer
- Calls: None

### compose
- Purpose: Generate UI element layout for the temperature tab
- Calls: None

### on_button_pressed
- Purpose: Handle button press events for toggling visibility and adjusting threshold
- Calls: update_plots, config.save_persistent_settings

### on_key
- Purpose: Handle keyboard shortcuts for toggling visibility and adjusting threshold
- Calls: update_plots, config.save_persistent_settings

### update_plots
- Purpose: Refresh GPU temperature plots with current data and settings
- Calls: buffer.since, plot.clear, plot.add_series, plot.add_line

### update_time_range
- Purpose: Update time range for data display and refresh plots
- Calls: update_plots

## Globals
None

## Dependencies
- textual.app.ComposeResult
- textual.containers.Container
- textual.widgets.Button
- textual.widgets.Plot
- nmon.gpu.protocol.GpuMonitorProtocol
- nmon.storage.ring_buffer.RingBuffer
- nmon.config.AppConfig
