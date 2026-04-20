"""
Module for rendering the temperature monitoring view in the nmon terminal dashboard.
"""

from typing import List
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import Settings, UserPrefs
from nmon.history import HistoryStore
from nmon.widgets.sparkline import Sparkline, ThresholdLine

def render_temp_view(
    gpu_samples: List[GpuSnapshot],
    ollama_sample: OllamaSnapshot | None,
    prefs: UserPrefs,
    history_store: HistoryStore,
    settings: Settings,
    now: float
) -> Layout:
    """
    Render the temperature monitoring view.
    
    Args:
        gpu_samples: List of recent GPU snapshots.
        ollama_sample: Latest Ollama snapshot or None.
        prefs: User preferences.
        history_store: History store for retrieving historical data.
        settings: Application settings.
        now: Current timestamp.
        
    Returns:
        Rich Layout object containing the temperature view.
    """
    # Initialize a rich.layout.Layout with a single column
    layout = Layout()
    layout.split_column()
    
    # Create a time range selector panel with buttons for 1h, 4h, 12h, 24h
    time_range_panel = Panel(
        Text("1h 4h 12h 24h", style="bold"),
        title="Time Range",
        border_style="blue"
    )
    
    # Add the time range selector to the layout
    layout[0] = time_range_panel
    
    # Create panels for each GPU
    for i, gpu_sample in enumerate(gpu_samples):
        # Get temperature data from history store
        gpu_index = gpu_sample.gpu_index
        core_temps = history_store.gpu_series(gpu_index, prefs.active_time_range_hours)
        
        # Create sparkline for core temperature
        sparkline = Sparkline(
            core_temps,
            title=f"GPU {gpu_index} Core Temp"
        )
        
        # Add memory junction temperature if enabled
        if prefs.show_mem_junction:
            mem_temps = history_store.gpu_mem_series(gpu_index, prefs.active_time_range_hours)
            sparkline.add_series(mem_temps, title="Memory Junction")
        
        # Add threshold line if enabled
        if prefs.show_threshold_line and prefs.temp_threshold_c is not None:
            threshold_line = ThresholdLine(prefs.temp_threshold_c)
            sparkline.add_threshold(threshold_line)
        
        # Create panel for this GPU
        panel = Panel(
            sparkline,
            title=f"GPU {gpu_index}",
            border_style="green"
        )
        
        # Add panel to layout
        layout.split_row()
        layout[1] = panel
    
    return layout

def update_temp_prefs(
    prefs: UserPrefs,
    key: str,
    settings: Settings
) -> UserPrefs:
    """
    Update temperature view preferences based on user input.
    
    Args:
        prefs: Current user preferences.
        key: Keyboard input key.
        settings: Application settings.
        
    Returns:
        Updated user preferences.
    """
    # Adjust temperature threshold
    if key == "up":
        prefs.temp_threshold_c = (prefs.temp_threshold_c or 0) + 0.5
    elif key == "down":
        prefs.temp_threshold_c = (prefs.temp_threshold_c or 0) - 0.5
    elif key == "t":
        prefs.show_threshold_line = not prefs.show_threshold_line
    elif key == "m":
        prefs.show_mem_junction = not prefs.show_mem_junction
    
    return prefs
