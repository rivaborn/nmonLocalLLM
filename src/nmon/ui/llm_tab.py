from typing import List, Tuple
from datetime import datetime, timedelta

from nmon.llm.protocol import LlmSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.config import AppConfig

from textual.containers import Static
from textual.widgets import Plot, Button
from textual.app import ComposeResult, on_mount
from textual.widgets import ButtonPressed
from textual.app import KeyEvent

class LlmTab(Static):
    """LLM Server tab widget showing GPU/CPU utilization over time."""

    def __init__(self, config: AppConfig, buffer: RingBuffer[LlmSample]) -> None:
        super().__init__(id="llm-tab")
        self.config = config
        self.buffer = buffer
        
        # Create Plot widget for GPU/CPU utilization
        self.plot = Plot(
            title="LLM Utilization",
            x_label="Time",
            y_label="Utilization (%)",
        )
        
        # Set up time-range selector buttons
        self.time_ranges = [
            ("1 h", 3600),
            ("4 h", 14400),
            ("12 h", 43200),
            ("24 h", 86400),
        ]
        self.selected_range = self.time_ranges[0][1]  # Default to 1 hour
        
        # Initialize chart data structures
        self.gpu_series = []
        self.cpu_series = []
        
        # Create time-range buttons
        self.time_buttons = [
            Button(label, id=f"time-{label.lower().replace(' ', '-')}")
            for label, _ in self.time_ranges
        ]
        
        # Set initial button to selected range
        self.time_buttons[0].classes = "selected"

    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        yield from self.time_buttons
        yield self.plot

    @on_mount
    def on_mount(self) -> None:
        """Set up the widget when mounted."""
        # Register for config changes to update chart bounds
        self.config.subscribe(self._on_config_change)
        
        # Start periodic chart update timer
        self.set_interval(self.config.poll_interval_s, self.update_chart)
        
        # Trigger initial chart update
        self.update_chart()

    def update_chart(self) -> None:
        """Update the chart with new data."""
        # Get samples from buffer for selected time range
        now = datetime.now()
        start_time = now - timedelta(seconds=self.selected_range)
        
        samples = self.buffer.since(start_time)
        
        # Extract GPU utilization and CPU utilization series
        gpu_utilization = []
        cpu_utilization = []
        
        for sample in samples:
            # Calculate offload ratio as size_vram / size
            offload_ratio = 0.0
            if sample.size > 0:
                offload_ratio = sample.size_vram / sample.size
            
            # Calculate GPU and CPU utilization from offload ratio
            gpu_utilization_pct = min(100.0, max(0.0, offload_ratio * 100.0))
            cpu_utilization_pct = min(100.0, max(0.0, (1.0 - offload_ratio) * 100.0))
            
            gpu_utilization.append((sample.timestamp, gpu_utilization_pct))
            cpu_utilization.append((sample.timestamp, cpu_utilization_pct))
        
        # Update Plot widget with new data series
        self.gpu_series = gpu_utilization
        self.cpu_series = cpu_utilization
        
        # Set Y-axis bounds to [0, 100]
        self.plot.y_range = (0, 100)
        
        # Set X-axis labels to elapsed time with no zero-padding
        self.plot.x_range = (0, self.selected_range)
        
        # Update the plot with new data
        self.plot.clear()
        if gpu_utilization:
            self.plot.add_series(
                gpu_utilization,
                name="GPU Utilization",
                color="blue"
            )
        if cpu_utilization:
            self.plot.add_series(
                cpu_utilization,
                name="CPU Utilization",
                color="green"
            )

    def on_button_pressed(self, event: ButtonPressed) -> None:
        """Handle time-range button presses."""
        if event.button.id and event.button.id.startswith("time-"):
            # Update selected range
            label = event.button.label
            for btn_label, seconds in self.time_ranges:
                if btn_label == label:
                    self.selected_range = seconds
                    break
            
            # Update button selection
            for i, button in enumerate(self.time_buttons):
                if button.label == label:
                    button.classes = "selected"
                else:
                    button.classes = ""
            
            # Trigger chart update with new range
            self.update_chart()

    def _on_config_change(self) -> None:
        """Handle configuration changes."""
        # Re-start the timer with new interval
        self.set_interval(self.config.poll_interval_s, self.update_chart)
