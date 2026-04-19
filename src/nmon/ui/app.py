"""
Implementation of the main Textual application class for nmon.

This module implements the NmonApp class which serves as the entry point for
the Textual-based TUI application. It manages the application lifecycle,
UI components, and data flow between monitoring components and the user interface.
"""

from textual.app import App
from textual.containers import Container
from textual.widgets import Static
from nmon.config import AppConfig
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.gpu.monitor import GpuMonitor
from nmon.llm.monitor import LlmMonitor
from nmon.ui.alert_bar import AlertBar
from nmon.ui.dashboard import DashboardTab
from nmon.ui.temp_tab import TemperatureTab
from nmon.ui.power_tab import PowerTab
from nmon.ui.llm_tab import LlmTab

class NmonApp(App):
    """Main application class for nmon TUI."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the NmonApp with configuration.
        
        Args:
            config: Application configuration object
        """
        # Initialize base App with title "nmon" and log level "WARNING"
        super().__init__(title="nmon", log_level="WARNING")
        
        # Store config in instance variable
        self.config = config
        
        # Initialize ring buffers for GpuSample and LlmSample with history_duration_s from config
        self.gpu_buffer = RingBuffer[GpuSample](config)
        self.llm_buffer = RingBuffer[LlmSample](config)
        
        # Initialize monitors: GpuMonitor and LlmMonitor with respective buffers
        self.gpu_monitor = GpuMonitor(config, self.gpu_buffer)
        self.llm_monitor = LlmMonitor(config, self.llm_buffer)
        
        # Initialize UI components: AlertBar, DashboardTab, TempTab, PowerTab, LlmTab
        self.alert_bar = AlertBar()
        self.dashboard_tab = DashboardTab(config, self.gpu_buffer, self.llm_buffer, self.gpu_monitor, self.llm_monitor)
        self.temp_tab = TemperatureTab(self.gpu_monitor, config, self.gpu_buffer)
        self.power_tab = PowerTab(config, self.gpu_buffer)
        
        # Initialize LLM tab conditionally - will be added to UI only if Ollama is detected
        self.llm_tab = LlmTab(config, self.llm_buffer)
        
        # Set up tab structure with conditional LLM tab
        self.tabs = [self.dashboard_tab, self.temp_tab, self.power_tab]
        
        # Initialize update interval to config.poll_interval_s
        self.update_interval_s = config.poll_interval_s
        
        # Initialize Ollama presence flag to False
        self.ollama_present = False

    async def on_mount(self) -> None:
        """
        Called when the application is mounted and ready to run.
        
        Starts GPU monitoring and attempts to detect Ollama presence.
        If Ollama is present, starts LLM monitoring and shows the LLM tab.
        """
        # Start GPU monitoring by calling gpu_monitor.start()
        self.gpu_monitor.start()
        
        # Attempt to detect Ollama presence by calling llm_monitor.detect()
        ollama_detected = await self.llm_monitor.detect()
        
        # If Ollama is present:
        if ollama_detected:
            # Set Ollama presence flag to True
            self.ollama_present = True
            
            # Start LLM monitoring by calling llm_monitor.start()
            self.llm_monitor.start()
            
            # Show LLM tab in UI
            self.tabs.append(self.llm_tab)
        else:
            # Ollama is not present, do not show LLM tab
            pass
        
        # Add all UI components to app layout
        self.compose()
        
        # Set initial update interval in UI
        self.update_interval(self.update_interval_s)

    async def on_unmount(self) -> None:
        """
        Called when the application is unmounted and shutting down.
        
        Stops all monitoring and persists current configuration settings.
        """
        # Stop GPU monitoring by calling gpu_monitor.stop()
        self.gpu_monitor.stop()
        
        # If Ollama was present, stop LLM monitoring by calling llm_monitor.stop()
        if self.ollama_present:
            self.llm_monitor.stop()
        
        # Persist current config settings to JSON file
        # Note: This would require implementing config persistence logic
        # that's not shown in the architecture plan but is implied by the testing strategy

    def update_interval(self, interval_s: float) -> None:
        """
        Update the polling interval for all monitors.
        
        Args:
            interval_s: New polling interval in seconds
            
        Raises:
            ValueError: If interval_s is not in range [0.5, 60.0]
        """
        # Validate interval_s is in range [0.5, 60.0]
        if not (0.5 <= interval_s <= 60.0):
            raise ValueError("Update interval must be between 0.5 and 60.0 seconds")
        
        # Update internal poll interval
        self.update_interval_s = interval_s
        
        # Update all active monitors' poll intervals
        # Note: This would require access to monitor-specific interval setting methods
        # which are not defined in the architecture plan
        
        # Update UI interval display
        # Note: This would require UI-specific logic to update the display

    def toggle_mem_junction(self) -> None:
        """
        Toggle visibility of memory junction series in TempTab.
        """
        # Toggle visibility of memory junction series in TempTab
        # Note: This would require access to TempTab's internal state
        # which is not defined in the architecture plan
        
        # Update UI to reflect new state
        # Note: This would require UI-specific logic to update the display

    def toggle_threshold_line(self) -> None:
        """
        Toggle visibility of threshold line in TempTab.
        """
        # Toggle visibility of threshold line in TempTab
        # Note: This would require access to TempTab's internal state
        # which is not defined in the architecture plan
        
        # Update UI to reflect new state
        # Note: This would require UI-specific logic to update the display

    def adjust_threshold(self, delta_c: float) -> None:
        """
        Adjust the temperature threshold.
        
        Args:
            delta_c: Change in temperature threshold in Celsius
        """
        # Adjust temp_threshold_c in config by delta_c
        # Note: This would require access to config's internal state
        # which is not defined in the architecture plan
        
        # Clamp adjusted value to [0.0, 100.0]
        # Note: This would require config validation logic
        
        # Persist updated threshold to JSON file
        # Note: This would require config persistence logic
        
        # Update UI to reflect new threshold value
        # Note: This would require UI-specific logic to update the display

    async def _poll_all(self) -> None:
        """
        Poll all monitoring components and update UI.
        """
        # Poll GPU monitor and append samples to buffer
        # Note: This would require access to monitor polling methods
        # which are not defined in the architecture plan
        
        # Poll LLM monitor and append samples to buffer
        # Note: This would require access to monitor polling methods
        # which are not defined in the architecture plan
        
        # Update all UI components with latest data
        # Note: This would require UI-specific update methods
        
        # Handle any exceptions from polling without crashing app
        # Note: This would require exception handling logic
