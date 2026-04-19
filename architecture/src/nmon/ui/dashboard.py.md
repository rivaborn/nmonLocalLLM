# src/nmon/ui/dashboard.py

## Purpose
Implements the main dashboard UI tab for displaying GPU and LLM system metrics in a NiceGUI-based TUI.

## Responsibilities
- Render GPU and LLM monitoring data in a structured card-based UI
- Build and update dynamic dashboard sections with real-time metrics
- Manage UI element lifecycle for GPU and LLM data displays
- Handle data fetching and display logic for system monitoring

## Key Types
- DashboardTab (Class): Main UI component for system monitoring dashboard

## Key Functions
### __init__
- Purpose: Initialize dashboard tab with monitoring buffers and protocols
- Calls: None

### _build_initial_content
- Purpose: Create initial UI structure with containers for GPU and LLM data
- Calls: None

### _build_gpu_sections
- Purpose: Generate GPU metric cards with temperature, memory, and power data
- Calls: gpu_buffer.get_all(), ui.card(), ui.label(), ui.row()

### _build_llm_section
- Purpose: Create LLM server monitoring card with utilization and offloading metrics
- Calls: llm_buffer.get_latest(), ui.card(), ui.label(), ui.row()

### _update_display
- Purpose: Refresh all dashboard sections with latest monitoring data
- Calls: _build_gpu_sections(), _build_llm_section()

## Globals
None

## Dependencies
- nicegui.ui, nicegui.elements.Vertical
- nmon.gpu.protocol.GpuSample, nmon.llm.protocol.LlmSample
- nmon.config.AppConfig
- nmon.storage.ring_buffer.RingBuffer
- nmon.gpu.protocol.GpuMonitorProtocol, nmon.llm.protocol.LlmMonitorProtocol
