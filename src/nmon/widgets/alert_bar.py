"""
Module for the alert bar widget that displays active alerts in the terminal UI.
"""

from rich.panel import Panel
from nmon.alerts import AlertState
from nmon.config import Settings

class AlertBar:
    """
    A widget that renders an alert bar at the top of the dashboard view.
    
    The alert bar is visible only when there is an active alert that has not yet expired.
    It displays the alert message with a color-coded background based on the alert level.
    """
    
    def __init__(self, alert_state: AlertState | None, settings: Settings):
        """
        Initialize the AlertBar with an optional alert state and settings.
        
        Args:
            alert_state: The current alert state, or None if no alert is active.
            settings: Application settings for alert display duration.
        """
        self.alert_state = alert_state
        self.settings = settings
        self._visible = False

    def __rich__(self) -> Panel:
        """
        Render the alert bar as a Rich Panel.
        
        Returns:
            A Rich Panel containing the alert message or a zero-height panel if no alert is active.
        """
        # If no alert state or alert has expired, return a zero-height panel (hidden)
        if self.alert_state is None:
            self._visible = False
            return Panel("", height=0)
        
        # Check if alert has expired
        import time
        now = time.time()
        if now >= self.alert_state.expires_at:
            self._visible = False
            return Panel("", height=0)
        
        # Determine background color based on alert level
        color_map = {
            "red": "red",
            "orange": "orange3"
        }
        bg_color = color_map.get(self.alert_state.color, "red")
        
        # Create and return the panel with alert message
        panel = Panel(
            self.alert_state.message,
            title="Alert",
            style=f"black on {bg_color}"
        )
        self._visible = True
        return panel

    def update(self, new_alert_state: AlertState | None, now: float) -> None:
        """
        Update the alert bar with a new alert state.
        
        Args:
            new_alert_state: The new alert state, or None if no alert is active.
            now: Current timestamp for expiration check.
        """
        self.alert_state = new_alert_state
        if new_alert_state is not None:
            self._visible = True
        else:
            self._visible = False
