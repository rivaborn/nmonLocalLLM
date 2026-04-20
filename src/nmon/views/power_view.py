"""
Module for rendering the power consumption dashboard view in the nmon terminal application.
"""

from typing import List
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.history import HistoryStore
from nmon.config import UserPrefs, Settings
from nmon.widgets.sparkline import Sparkline

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print

class PowerView:
    """
    Renders the power consumption dashboard view for the nmon terminal application.
    Displays power draw charts for each GPU over a selected time range.
    """

    def __init__(
        self,
        history_store: HistoryStore,
        prefs: UserPrefs,
        settings: Settings,
        gpu_snapshots: List[GpuSnapshot],
        ollama_snapshot: OllamaSnapshot | None,
    ) -> None:
        """
        Initialize the PowerView with required dependencies and data.

        Args:
            history_store: HistoryStore instance for accessing historical data.
            prefs: UserPrefs instance for configuration.
            settings: Settings instance for application settings.
            gpu_snapshots: List of current GPU snapshots.
            ollama_snapshot: Current Ollama snapshot or None if not detected.
        """
        # Store provided arguments as instance attributes
        self.history_store = history_store
        self.prefs = prefs
        self.settings = settings
        self.gpu_snapshots = gpu_snapshots
        self.ollama_snapshot = ollama_snapshot

        # Initialize the time range selector to 1 hour
        self.active_time_range_hours = 1.0

        # Set up a list of sparkline renderables for each GPU
        self.sparklines = []

    def render(self) -> Layout:
        """
        Render the power view layout with time range selector and GPU power charts.

        Returns:
            rich.layout.Layout: The composed layout for the power view.
        """
        # Create the main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="content", ratio=1),
            Layout(name="footer", size=1)
        )

        # Create header
        header = Panel(
            Text("Power Consumption Dashboard", style="bold blue"),
            border_style="blue"
        )
        layout["header"].update(header)

        # Create content area with sparklines
        content_layout = Layout()
        content_layout.split_row(
            Layout(name="gpu_charts", ratio=1),
            Layout(name="ollama_info", size=30)
        )

        # Add GPU sparklines
        gpu_charts = self._render_gpu_charts()
        content_layout["gpu_charts"].update(gpu_charts)

        # Add Ollama info if available
        if self.ollama_snapshot:
            ollama_info = self._render_ollama_info()
            content_layout["ollama_info"].update(ollama_info)
        else:
            # Create empty panel if no Ollama data
            empty_panel = Panel(
                Text("No Ollama data available", style="dim"),
                border_style="gray"
            )
            content_layout["ollama_info"].update(empty_panel)

        layout["content"].update(content_layout)

        # Create footer with time range selector
        footer = Panel(
            Text(f"Time range: {self.active_time_range_hours} hours", style="dim"),
            border_style="gray"
        )
        layout["footer"].update(footer)

        return layout

    def _render_gpu_charts(self) -> Layout:
        """
        Render sparklines for each GPU's power consumption.

        Returns:
            Layout: Layout containing GPU charts.
        """
        # Create a layout for GPU charts
        gpu_layout = Layout()
        gpu_layout.split_column()

        # Get historical power data for each GPU
        for i, snapshot in enumerate(self.gpu_snapshots):
            # Create sparkline for this GPU's power consumption
            power_data = self.history_store.get_power_history(
                snapshot.gpu_id, 
                hours=self.active_time_range_hours
            )
            
            # Create sparkline widget
            sparkline = Sparkline(
                data=power_data,
                title=f"GPU {snapshot.gpu_id} Power (W)",
                style="green"
            )
            
            # Create panel for this GPU chart
            panel = Panel(
                sparkline,
                title=f"GPU {snapshot.gpu_id}",
                border_style="blue"
            )
            
            gpu_layout.split_row(Layout(panel, ratio=1))

        return gpu_layout

    def _render_ollama_info(self) -> Panel:
        """
        Render information about the Ollama process.

        Returns:
            Panel: Panel containing Ollama information.
        """
        if not self.ollama_snapshot:
            return Panel(
                Text("No Ollama data available", style="dim"),
                border_style="gray"
            )

        table = Table(box=None)
        table.add_column("Metric", style="blue")
        table.add_column("Value", style="green")

        table.add_row("Model", self.ollama_snapshot.loaded_model or "Unknown")
        table.add_row("GPU Usage", f"{self.ollama_snapshot.gpu_use_pct:.1f}%")
        table.add_row("CPU Usage", f"{self.ollama_snapshot.cpu_use_pct:.1f}%")
        table.add_row("GPU Layers", str(self.ollama_snapshot.gpu_layers))
        table.add_row("Total Layers", str(self.ollama_snapshot.total_layers))
        table.add_row("Model Size", f"{self.ollama_snapshot.model_size_bytes / (1024**2):.1f} MB")

        return Panel(
            table,
            title="Ollama Process",
            border_style="magenta"
        )
