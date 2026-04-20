"""
DashboardView for nmon terminal dashboard.
Displays GPU metrics, memory junction temperatures (if supported), and Ollama LLM usage.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nmon.gpu_monitor import GpuSnapshot
    from nmon.ollama_monitor import OllamaSnapshot
    from nmon.config import UserPrefs, Settings
    from nmon.history import HistoryStore
    from nmon.alerts import AlertState
    from rich.layout import Layout
    from rich.console import RenderableType

from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import UserPrefs, Settings
from nmon.history import HistoryStore
from nmon.alerts import AlertState
from nmon.widgets.sparkline import Sparkline
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.table import Table
from rich.box import ROUNDED
from rich import print
import time


class DashboardView:
    """
    Main dashboard view for nmon terminal application.
    Displays GPU metrics, memory junction temperatures (if supported), and Ollama LLM usage.
    """

    def __init__(
        self,
        gpu_monitor,
        history_store: HistoryStore,
        prefs: UserPrefs,
        settings: Settings,
        alert_state: AlertState | None,
    ) -> None:
        """
        Initialize the dashboard view with required dependencies.
        
        Args:
            gpu_monitor: GpuMonitorProtocol instance for polling GPU data
            history_store: HistoryStore for accessing historical metrics
            prefs: UserPrefs for rendering configuration
            settings: Settings for application configuration
            alert_state: Current alert state or None
        """
        self.gpu_monitor = gpu_monitor
        self.history_store = history_store
        self.prefs = prefs
        self.settings = settings
        self.alert_state = alert_state

    def render(self) -> Layout:
        """
        Render the dashboard view layout.
        
        Returns:
            rich.layout.Layout containing the dashboard structure
        """
        # Create main layout with alert bar at top
        layout = Layout()
        layout.split_row(
            Layout(name="alert_bar", size=1),
            Layout(name="main_content")
        )
        
        # Render alert bar if alert_state is not None.
        # Create an AlertBar(self.alert_state, self.settings) instance and assign
        # it as the renderable for the "alert_bar" layout slot.
        # The AlertBar.__rich__ method returns a zero-height Panel when no alert
        # is active, so it is safe to always assign it.
        if self.alert_state is not None:
            from nmon.widgets.alert_bar import AlertBar
            layout["alert_bar"].renderable = AlertBar(self.alert_state, self.settings)
        
        # Create main content area
        main_content = Layout()
        main_content.split_column(
            Layout(name="gpu_panels"),
            Layout(name="llm_panel", size=10)
        )
        
        # Get all GPU snapshots from monitor
        gpu_snapshots = self.gpu_monitor.poll()
        
        # Build GPU panels
        gpu_panels = []
        has_mem_junction = False
        
        for snapshot in gpu_snapshots:
            # Check if any GPU supports memory junction temperature
            if snapshot.mem_junction_temp_c is not None:
                has_mem_junction = True
            
            # Create panel for this GPU
            panel = self._create_gpu_panel(snapshot)
            gpu_panels.append(panel)
        
        # Add GPU panels to layout
        main_content["gpu_panels"].renderable = Columns(gpu_panels, equal=True)
        
        # Add LLM panel if Ollama is detected.
        # Call self.history_store.ollama_series(self.prefs.active_time_range_hours)
        # to get recent Ollama snapshots. If the most recent snapshot has
        # reachable=True, render a Panel showing loaded_model name and size,
        # gpu_use_pct, cpu_use_pct, and gpu offload indicator, then assign it
        # to the "llm_panel" layout slot. If no reachable snapshot, hide the slot.
        ollama_snapshots = self.history_store.ollama_series(self.prefs.active_time_range_hours)
        if ollama_snapshots and ollama_snapshots[-1].reachable:
            llm_panel = self._create_llm_panel(ollama_snapshots[-1])
            main_content["llm_panel"].renderable = llm_panel
        else:
            # Hide the llm_panel slot if no reachable snapshot
            main_content["llm_panel"].size = 0
        
        layout["main_content"] = main_content
        return layout

    def _create_gpu_panel(self, snapshot: GpuSnapshot) -> Panel:
        """
        Create a panel for a single GPU showing its metrics.
        
        Args:
            snapshot: GpuSnapshot containing GPU metrics
            
        Returns:
            rich.panel.Panel with GPU metrics
        """
        # Create table for GPU metrics
        table = Table(box=ROUNDED, show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="cyan")
        
        # Add current temperature
        table.add_row("Temp", f"{snapshot.temperature_c:.1f}°C")
        
        # Add memory usage
        mem_used_mb = snapshot.memory_used_mb
        mem_total_mb = snapshot.memory_total_mb
        mem_percent = (mem_used_mb / mem_total_mb) * 100 if mem_total_mb > 0 else 0
        table.add_row("Memory", f"{mem_used_mb:.0f}MB / {mem_total_mb:.0f}MB ({mem_percent:.0f}%)")
        
        # Add power consumption
        power_draw_w = snapshot.power_draw_w
        power_limit_w = snapshot.power_limit_w
        table.add_row("Power", f"{power_draw_w:.1f}W / {power_limit_w:.1f}W")
        
        # Add mem junction temp if available
        if snapshot.mem_junction_temp_c is not None:
            table.add_row("Mem Junction", f"{snapshot.mem_junction_temp_c:.1f}°C")
        
        return Panel(table, title=f"GPU {snapshot.gpu_index}")

    def _create_llm_panel(self, snapshot: OllamaSnapshot) -> Panel:
        """
        Create a panel for displaying Ollama LLM usage metrics.
        
        Args:
            snapshot: OllamaSnapshot containing LLM metrics
            
        Returns:
            rich.panel.Panel with LLM metrics
        """
        # Create table for LLM metrics
        table = Table(box=ROUNDED, show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="cyan")
        
        # Add loaded model name
        table.add_row("Model", snapshot.loaded_model)
        
        # Add model size
        model_size_mb = snapshot.model_size_bytes / (1024 * 1024)
        table.add_row("Size", f"{model_size_mb:.1f} MB")
        
        # Add GPU usage
        table.add_row("GPU Use", f"{snapshot.gpu_use_pct:.1f}%")
        
        # Add CPU usage
        table.add_row("CPU Use", f"{snapshot.cpu_use_pct:.1f}%")
        
        # Add GPU offload indicator
        if snapshot.gpu_layers == snapshot.total_layers:
            offload_status = "Full"
        elif snapshot.gpu_layers > 0:
            offload_status = f"Partial ({snapshot.gpu_layers}/{snapshot.total_layers})"
        else:
            offload_status = "None"
        table.add_row("GPU Offload", offload_status)
        
        return Panel(table, title="Ollama LLM")
