# src/nmon/widgets/alert_bar.py

## Purpose
Displays active GPU alerts in a color-coded Rich panel at the top of the terminal UI dashboard. Shows alert messages with expiration handling and dynamic visibility.

## Responsibilities
- Render alert messages as Rich Panel widgets with color coding
- Manage alert visibility based on expiration timestamps
- Update alert state and visibility status
- Handle None alert states and expired alerts gracefully
- Integrate with application settings for alert duration

## Key Types
- AlertBar (Class): Main widget class managing alert display and visibility

## Key Functions
### __rich__
- Purpose: Renders the alert bar as a Rich Panel widget with appropriate styling
- Calls: time.time()

### update
- Purpose: Updates the alert state and manages visibility flags
- Calls: None

## Globals
None

## Dependencies
- rich.panel.Panel
- nmon.alerts.AlertState
- nmon.config.Settings
- time (module)
