# src/nmon/ui/alert_bar.py

## Purpose
Provides a TUI widget to display GPU offloading alerts when GPU utilization drops below 100%. Shows percentage of computation offloaded to CPU with color-coded warnings.

## Responsibilities
- Monitor GPU utilization and calculate offload percentage
- Display color-coded alerts in TUI with minimum visibility duration
- Manage alert visibility state and timer logic
- Format and render alert messages with appropriate styling
- Handle edge cases where GPU is fully utilized

## Key Types
- AlertBar (Class): TUI widget that displays GPU offloading status alerts

## Key Functions
### update_alert
- Purpose: Processes LLM samples to determine if GPU offloading alert should be shown
- Calls: None visible

### render
- Purpose: Returns formatted alert message when visible, empty string otherwise
- Calls: None visible

## Globals
None

## Dependencies
- textual.widgets.Static
- nmon.llm.protocol.LlmSample
