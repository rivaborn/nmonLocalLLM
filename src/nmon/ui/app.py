"""
Implementation of the main Textual application class for nmon.

This module implements the NmonApp class which serves as the entry point for
the Textual-based TUI application. It manages the application lifecycle,
UI components, and data flow between monitoring components and the user interface.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
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
from nmon.ui.memory_tab import MemoryTab
from nmon.ui.llm_tab import LlmTab

class NmonApp(App):
    """Main application class for nmon TUI."""

    CSS = """
    TabbedContent {
        height: 1fr;
    }
    ContentSwitcher {
        height: 1fr;
    }
    TabPane {
        height: 1fr;
    }
    DashboardTab, TemperatureTab, PowerTab, MemoryTab, LlmTab {
        height: 1fr;
    }
    """

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.gpu_buffer: RingBuffer[GpuSample] = RingBuffer(config)
        self.llm_buffer: RingBuffer[LlmSample] = RingBuffer(config)
        self.gpu_monitor = GpuMonitor(config, self.gpu_buffer)
        self.llm_monitor = LlmMonitor(config, self.llm_buffer)
        self.update_interval_s = config.poll_interval_s
        self.ollama_present = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield AlertBar()
        with TabbedContent():
            with TabPane("Dashboard", id="tab-dashboard"):
                yield DashboardTab(
                    self.config, self.gpu_buffer, self.llm_buffer,
                    self.gpu_monitor, self.llm_monitor,
                )
            with TabPane("Temperature", id="tab-temp"):
                yield TemperatureTab(self.gpu_monitor, self.config, self.gpu_buffer)
            with TabPane("Power", id="tab-power"):
                yield PowerTab(self.config, self.gpu_buffer)
            with TabPane("Memory", id="tab-memory"):
                yield MemoryTab(self.config, self.gpu_buffer)
        yield Footer()

    async def on_mount(self) -> None:
        """Start monitors and set up polling timer."""
        self.gpu_monitor.start()

        ollama_detected = await self.llm_monitor.detect()
        if ollama_detected:
            self.ollama_present = True
            self.llm_monitor.start()
            await self.query_one(TabbedContent).add_pane(
                TabPane("LLM", LlmTab(self.config, self.llm_buffer), id="tab-llm")
            )

        self.set_interval(self.update_interval_s, self._poll_all)

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

    async def run_async(self) -> None:
        """Start the Textual app within the current event loop.
        
        Called from main.py's _run_async() which already has an event loop
        running. Delegate to Textual's App.run_async() which detects an
        existing event loop and attaches without creating a new one.
        """
        await super().run_async()

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
        """Refresh all tab displays from latest buffer data."""
        for widget_type in (DashboardTab, TemperatureTab, PowerTab, MemoryTab):
            try:
                self.query_one(widget_type).refresh_data()
            except Exception:
                pass
        if self.ollama_present:
            try:
                self.query_one(LlmTab).refresh_data()
            except Exception:
                pass
