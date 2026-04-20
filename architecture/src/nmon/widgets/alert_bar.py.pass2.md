# src/nmon/widgets/alert_bar.py - Enhanced Analysis

## Architectural Role
This widget serves as a terminal UI component that provides real-time visual feedback for GPU system alerts. It integrates with the dashboard's rendering system through Rich's widget protocol and coordinates with the alert subsystem for state management.

## Cross-References
### Incoming
- Dashboard renderer calls `__rich__` method for UI display
- Alert manager updates state via `update` method
- Main application loop polls for alert changes

### Outgoing
- Depends on `AlertState` from alerts module for alert data
- References `Settings` for alert duration configuration
- Uses `rich.panel.Panel` for rendering
- Imports `time` module for expiration checks

## Design Patterns
- **Observer Pattern**: The widget observes alert state changes through update() method calls
- **State Management**: Uses explicit visibility flags and expiration timestamps to manage UI state
- **Decorator Pattern**: Implements `__rich__` method to integrate with Rich's rendering system
