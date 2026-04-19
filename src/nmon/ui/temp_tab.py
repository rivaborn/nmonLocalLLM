from typing import List

from nmon.gpu.protocol import GpuSample, GpuMonitorProtocol
from nmon.storage.ring_buffer import RingBuffer
from nmon.config import AppConfig

from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Plot


class TemperatureTab:
    """A Textual Screen that displays GPU temperature data over time."""

    def __init__(
        self, 
        gpu_monitor: GpuMonitorProtocol, 
        config: AppConfig, 
        buffer: RingBuffer[GpuSample]
    ) -> None:
        self.gpu_monitor = gpu_monitor
        self.config = config
        self.buffer = buffer
        
        # Initialize time range to 1 hour
        self.time_range_s = 3600
        
        # Initialize visibility flags
        self.show_mem_junction = True
        self.threshold_line_visible = config.temp_threshold_visible
        self.threshold_value_c = config.temp_threshold_c
        
        # Initialize plot widgets - one per GPU
        self.gpu_plots: List[Plot] = [
            Plot() for _ in gpu_monitor.gpus
        ]
        
        # Initialize time range buttons
        self.time_range_buttons = [
            Button("1h", id="time_1h"),
            Button("6h", id="time_6h"),
            Button("12h", id="time_12h"),
            Button("1d", id="time_1d"),
        ]
        
        # Initialize control buttons
        self.threshold_toggle_button = Button("Toggle Threshold")
        self.mem_junction_toggle_button = Button("Toggle Mem Junction")
        self.threshold_adjust_up = Button("↑")
        self.threshold_adjust_down = Button("↓")

    def compose(self) -> ComposeResult:
        """Compose the UI elements for the temperature tab."""
        # Yield time range buttons container
        yield Container(*self.time_range_buttons)
        
        # Yield GPU plots container
        yield Container(*self.gpu_plots)
        
        # Yield control buttons
        yield self.threshold_toggle_button
        yield self.mem_junction_toggle_button
        yield self.threshold_adjust_up
        yield self.threshold_adjust_down

    def on_button_pressed(self, event: events.ButtonPressed) -> None:
        """Handle button press events."""
        if event.button == self.threshold_toggle_button:
            # Toggle threshold line visibility
            self.threshold_line_visible = not self.threshold_line_visible
            # Update config
            self.config.temp_threshold_visible = self.threshold_line_visible
            # Persist config to JSON
            self.config.save_persistent_settings()
            
        elif event.button == self.mem_junction_toggle_button:
            # Toggle memory junction visibility
            self.show_mem_junction = not self.show_mem_junction
            # Update plots
            self.update_plots()
            
        elif event.button == self.threshold_adjust_up:
            # Increment threshold value
            self.threshold_value_c += 0.5
            # Clamp to valid range
            self.threshold_value_c = max(0.0, min(200.0, self.threshold_value_c))
            # Update config
            self.config.temp_threshold_c = self.threshold_value_c
            # Persist config to JSON
            self.config.save_persistent_settings()
            
        elif event.button == self.threshold_adjust_down:
            # Decrement threshold value
            self.threshold_value_c -= 0.5
            # Clamp to valid range
            self.threshold_value_c = max(0.0, min(200.0, self.threshold_value_c))
            # Update config
            self.config.temp_threshold_c = self.threshold_value_c
            # Persist config to JSON
            self.config.save_persistent_settings()
            
        # Update all plots with new threshold value
        self.update_plots()

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard events."""
        if event.key == "t":
            # Toggle memory junction visibility
            self.show_mem_junction = not self.show_mem_junction
            # Update plots
            self.update_plots()
            
        elif event.key == "h":
            # Toggle threshold line visibility
            self.threshold_line_visible = not self.threshold_line_visible
            # Update config
            self.config.temp_threshold_visible = self.threshold_line_visible
            # Persist config to JSON
            self.config.save_persistent_settings()
            
        elif event.key == "up":
            # Increment threshold value
            self.threshold_value_c += 0.5
            # Clamp to valid range
            self.threshold_value_c = max(0.0, min(200.0, self.threshold_value_c))
            # Update config
            self.config.temp_threshold_c = self.threshold_value_c
            # Persist config to JSON
            self.config.save_persistent_settings()
            
        elif event.key == "down":
            # Decrement threshold value
            self.threshold_value_c -= 0.5
            # Clamp to valid range
            self.threshold_value_c = max(0.0, min(200.0, self.threshold_value_c))
            # Update config
            self.config.temp_threshold_c = self.threshold_value_c
            # Persist config to JSON
            self.config.save_persistent_settings()
            
        # Update all plots with new threshold value
        self.update_plots()

    def update_plots(self) -> None:
        """Update all GPU temperature plots with current data."""
        # Get samples from buffer for the specified time range
        samples = self.buffer.since(self.time_range_s)
        
        # Update each plot
        for gpu_index, plot in enumerate(self.gpu_plots):
            # Filter samples for this GPU
            gpu_samples = [
                sample for sample in samples 
                if sample.gpu_index == gpu_index
            ]
            
            # Extract temperature data
            if not gpu_samples:
                # No data to plot
                plot.clear()
                continue
                
            # Extract time and temperature values
            x_values = [sample.timestamp for sample in gpu_samples]
            y_values_gpu = [sample.temperature_gpu for sample in gpu_samples]
            
            # Create data series for GPU temperature
            series_gpu = list(zip(x_values, y_values_gpu))
            
            # Add memory junction temperature if enabled
            if self.show_mem_junction:
                y_values_mem = [sample.temperature_mem_junction for sample in gpu_samples]
                series_mem = list(zip(x_values, y_values_mem))
                
                # Update plot with both series
                plot.clear()
                plot.add_series(series_gpu, name="GPU Temp")
                plot.add_series(series_mem, name="Mem Temp")
            else:
                # Update plot with only GPU temperature
                plot.clear()
                plot.add_series(series_gpu, name="GPU Temp")
            
            # Add threshold line if visible
            if self.threshold_line_visible:
                plot.add_line(
                    x_values[0], 
                    self.threshold_value_c, 
                    x_values[-1], 
                    self.threshold_value_c,
                    name="Threshold"
                )

    def update_time_range(self, seconds: float) -> None:
        """Update the time range for data display."""
        # Clamp seconds to valid range [3600, 86400]
        seconds = max(3600, min(86400, seconds))
        
        # Update time range
        self.time_range_s = seconds
        
        # Update all plots with new time range
        self.update_plots()
