# src/nmon/ui/power_tab.py

## Purpose
Displays GPU power consumption over time in a Textual TUI widget with interactive time range selection.

## Responsibilities
- Render power consumption plots for each GPU in the system
- Handle time range selection changes to update displayed data
- Manage plot widget lifecycle and data updates
- Format time labels for display
- Process click events on time range buttons

## Key Types
- PowerTab (Class): Textual widget that displays GPU power consumption over time

## Key Functions
### _update_plots
- Purpose: Update all plot widgets with data from the buffer
- Calls: buffer.since(), plots.clear(), plots.add_line()

### _on_time_range_change
- Purpose: Handle time range change event
- Calls: _update_plots()

### on_mount
- Purpose: Called when the widget is mounted
- Calls: _update_plots()

### on_click
- Purpose: Handle click events on time range buttons
- Calls: _on_time_range_change()

## Globals
None

## Dependencies
- textual.widgets.Static, Plot, Container, events.Click
- nmon.gpu.protocol.GpuSample
- nmon.storage.ring_buffer.RingBuffer
- nmon.config.AppConfig
- typing.Dict, List, Tuple
- time
