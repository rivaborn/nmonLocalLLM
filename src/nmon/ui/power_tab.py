from textual.widgets import Static, Plot
from textual.containers import Container
from textual import events
from nmon.gpu.protocol import GpuSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.config import AppConfig
from typing import Dict, List, Tuple
import time


class PowerTab(Static):
    """Textual Static widget that displays GPU power consumption over time."""
    
    def __init__(self, config: AppConfig, buffer: RingBuffer[GpuSample]):
        super().__init__()
        self.config = config
        self.buffer = buffer
        self.selected_time_range = 3600  # Default to 1 hour
        self.plots: Dict[str, Plot] = {}
        self.gpu_names: List[str] = []
        
    def compose(self):
        """Initialize the widget with time range selector and plot widgets."""
        # Create time range selector
        time_ranges = [
            ("1 h", 3600),
            ("4 h", 14400),
            ("12 h", 43200),
            ("24 h", 86400)
        ]
        
        # Create container for time range buttons
        time_selector_container = Container()
        
        # Create plot widgets for each GPU
        gpu_samples = self.buffer.peek(1)
        if gpu_samples:
            first_sample = gpu_samples[0]
            self.gpu_names = list(first_sample.power_draw_w.keys())
            
            for gpu_name in self.gpu_names:
                plot = Plot(
                    title=f"GPU {gpu_name} Power Consumption",
                    x_label="Time",
                    y_label="Power (W)",
                    x_bounds=(0, self.selected_time_range),
                    y_bounds=(0, 0)  # Will be updated with actual power limits
                )
                self.plots[gpu_name] = plot
                yield plot
        
        # Add time range selector buttons
        for label, duration in time_ranges:
            yield Static(label, id=f"time_range_{duration}")
    
    def _update_plots(self):
        """Update all plot widgets with data from the buffer."""
        if not self.gpu_names:
            return
            
        # Get samples for each GPU
        for gpu_name in self.gpu_names:
            samples = self.buffer.since(self.selected_time_range)
            
            # Extract power draw values for Y-axis
            y_values = []
            x_values = []
            
            # Get the power limit for this GPU
            power_limit = 0
            if samples:
                first_sample = samples[0]
                if gpu_name in first_sample.power_limit_w:
                    power_limit = first_sample.power_limit_w[gpu_name]
            
            # Update Y-axis bounds
            if self.plots.get(gpu_name):
                self.plots[gpu_name].y_bounds = (0, power_limit)
            
            # Process samples
            for sample in samples:
                if gpu_name in sample.power_draw_w:
                    y_values.append(sample.power_draw_w[gpu_name])
                    # Convert timestamp to elapsed time in seconds
                    elapsed_time = sample.timestamp - samples[0].timestamp
                    x_values.append(elapsed_time)
            
            # Update plot with new data
            if self.plots.get(gpu_name):
                self.plots[gpu_name].clear()
                if x_values and y_values:
                    self.plots[gpu_name].add_line(x_values, y_values, label=gpu_name)
        
        # Re-render all plot widgets
        for plot in self.plots.values():
            plot.refresh()
    
    def _format_time_label(self, seconds: int) -> str:
        """Convert seconds to hours, minutes, seconds format without zero-padding."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        # Format without zero-padding
        label_parts = []
        if hours > 0:
            label_parts.append(f"{hours}h")
        if minutes > 0 or hours > 0:
            label_parts.append(f"{minutes}m")
        if seconds > 0 or minutes > 0 or hours > 0:
            label_parts.append(f"{seconds}s")
            
        return " ".join(label_parts) if label_parts else "0s"
    
    def _on_time_range_change(self, duration: int):
        """Handle time range change event."""
        self.selected_time_range = duration
        self._update_plots()
    
    async def on_mount(self):
        """Called when the widget is mounted."""
        self._update_plots()
    
    async def on_click(self, event: events.Click):
        """Handle click events on time range buttons."""
        if event.control.id and event.control.id.startswith("time_range_"):
            duration = int(event.control.id.split("_")[-1])
            self._on_time_range_change(duration)
