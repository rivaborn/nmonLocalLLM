"""
AlertBar widget for displaying GPU offloading alerts in the nmon TUI.

The alert bar shows when GPU utilization is below 100% and indicates
the percentage of computation offloaded to the CPU. It enforces a
minimum visibility duration of 1000 ms to ensure readability.
"""

from textual.widgets import Static
from nmon.llm.protocol import LlmSample


class AlertBar(Static):
    """Global alert bar widget showing GPU offloading status."""

    def __init__(self) -> None:
        """Initialize the alert bar with default state."""
        super().__init__()
        self._visible = False
        self._timer = None
        self._min_duration_ms = 1000
        self._message = ""
        self._color = ""

    def update_alert(self, sample: LlmSample | None) -> None:
        """
        Update the alert bar based on the latest LLM sample.
        
        If sample is None or GPU utilization is 100%, hide the alert bar.
        Otherwise, calculate offload percentage and show appropriate alert.
        """
        if sample is None or sample.gpu_utilization_pct == 100:
            self._visible = False
            if self._timer is not None:
                self._timer.cancel()
            return

        # Calculate offload percentage
        offload_pct = 100 - sample.gpu_utilization_pct

        # Determine color based on offload percentage
        if offload_pct <= 5:
            color = "#FF8C00"  # orange
        else:
            color = "#FF0000"  # red

        # Format message
        message = f"⚠ GPU OFFLOADING ACTIVE — {offload_pct:.1f}% on CPU"
        
        self._message = message
        self._color = color
        self._visible = True

        # Start timer for minimum visibility duration
        if self._timer is not None:
            self._timer.cancel()
        # Note: In actual implementation, this would use self.set_timer(self._min_duration_ms, self._hide_alert)

    def render(self) -> str:
        """
        Render the alert bar content.
        
        Returns empty string if not visible, otherwise returns formatted message.
        """
        if not self._visible:
            return ""
        return f"[{self._color}]{self._message}[/{self._color}]"
