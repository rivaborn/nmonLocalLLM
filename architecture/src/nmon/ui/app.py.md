# src/nmon/ui/app.py

## Purpose
Implements the main Textual application class for nmon, managing the TUI lifecycle, UI components, and data flow between monitoring and display layers.

## Responsibilities
- Initialize and manage application lifecycle including monitoring components and UI widgets
- Handle conditional UI tab display based on Ollama presence detection
- Coordinate data flow between GPU/LLM monitors and UI components
- Manage polling intervals and update mechanisms for monitoring components
- Implement application shutdown procedures including monitor cleanup

## Key Types
- NmonApp (Class): Main application class coordinating all monitoring and UI components

## Key Functions
### __init__
- Purpose: Initialize application with configuration and set up monitoring components and UI widgets
- Calls: None visible

### on_mount
- Purpose: Start monitoring and initialize UI components when application is mounted
- Calls: gpu_monitor.start(), llm_monitor.detect(), llm_monitor.start()

### on_unmount
- Purpose: Clean up monitoring components and persist configuration on shutdown
- Calls: gpu_monitor.stop(), llm_monitor.stop()

### update_interval
- Purpose: Update polling intervals for all monitoring components
- Calls: None visible

### toggle_mem_junction
- Purpose: Toggle visibility of memory junction series in temperature tab
- Calls: None visible

### toggle_threshold_line
- Purpose: Toggle visibility of threshold line in temperature tab
- Calls: None visible

### adjust_threshold
- Purpose: Adjust temperature threshold with validation and persistence
- Calls: None visible

### _poll_all
- Purpose: Poll all monitoring components and update UI with latest data
- Calls: None visible

## Globals
None

## Dependencies
- textual.app.App
- textual.containers.Container
- textual.widgets.Static
- nmon.config.AppConfig
- nmon.gpu.protocol.GpuSample
- nmon.llm.protocol.LlmSample
- nmon.storage.ring_buffer.RingBuffer
- nmon
