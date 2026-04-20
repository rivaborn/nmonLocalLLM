# src/nmon/app.py

## Purpose
Manages the terminal dashboard application lifecycle, UI rendering, event handling, and data flow between monitoring components and views.

## Responsibilities
- Initialize and orchestrate application components including monitors, history store, and UI
- Handle keyboard events for navigation, settings adjustment, and view switching
- Poll GPU and Ollama metrics concurrently and update history store
- Render dynamic views based on current selection and application state
- Manage application start/stop lifecycle with proper cleanup

## Key Types
- NmonApp (Class): Main application controller managing all components and UI flow

## Key Functions
### start
- Purpose: Initialize layout, probe Ollama, start event loop and live rendering
- Calls: _setup_layout, _probe_ollama

### stop
- Purpose: Clean shutdown by flushing history, stopping live rendering, and canceling background task
- Calls: None

### _poll_all
- Purpose: Concurrently poll GPU and Ollama metrics
- Calls: gpu_monitor.poll, ollama_monitor.poll

### _handle_event
- Purpose: Process keyboard events for application control and view navigation
- Calls: None

### _render_current_view
- Purpose: Render the active view with current data
- Calls: DashboardView.render, render_temp_view, PowerView.render, render_llm_view

### _event_loop
- Purpose: Main polling loop that updates metrics, history, alerts, and UI
- Calls: _poll_all, history_store.add_gpu_samples, history_store.add_ollama_sample, compute_alert, _render_current_view

## Globals
None

## Dependencies
- rich.live.Live, rich.layout.Layout, rich.panel.Panel
- nmon.config.Settings, UserPrefs
- nmon.gpu_monitor.GpuMonitorProtocol, GpuSnapshot
- nmon.ollama_monitor.OllamaMonitorProtocol, OllamaSnapshot
- nmon.history.HistoryStore
- nmon.alerts.AlertState, compute_alert
- nmon.views.dashboard_view.DashboardView
- nmon.views.temp_view.render_temp_view, update_temp_prefs
- nmon.views.power_view.PowerView
- nmon.views.llm_view.render_llm_view
- nmon.widgets.alert_bar.AlertBar
- nmon.widgets.sparkline.Sparkline
- time, asyncio
- sqlite3
