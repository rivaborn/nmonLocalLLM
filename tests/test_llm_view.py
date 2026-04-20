from datetime import datetime
from typing import List

from rich.layout import Layout
from rich.table import Table
from rich.text import Text

from src.nmon.config import Settings, UserPrefs
from src.nmon.history import HistoryStore
from src.nmon.ollama_monitor import OllamaSnapshot


def render_llm_view(
    ollama_snapshot: OllamaSnapshot,
    history_store: HistoryStore,
    settings: Settings,
    prefs: UserPrefs,
    now: float
) -> Layout:
    """
    Render the LLM monitoring view layout.
    
    Args:
        ollama_snapshot: Current Ollama snapshot data
        history_store: History store for retrieving historical data
        settings: Application settings
        prefs: User preferences
        now: Current timestamp
        
    Returns:
        Rich Layout object representing the LLM view
    """
    # Create main layout
    layout = Layout()
    layout.size = 20  # Set height for the layout
    
    # Create a table for LLM information
    llm_table = Table(
        title="LLM Status",
        show_header=True,
        header_style="bold blue",
        border_style="blue"
    )
    
    # Add columns to the table
    llm_table.add_column("Metric", style="cyan", no_wrap=True)
    llm_table.add_column("Value", style="white")
    llm_table.add_column("Status", style="yellow")
    
    # Add rows with LLM data
    if ollama_snapshot.loaded_model:
        llm_table.add_row(
            "Model",
            ollama_snapshot.loaded_model,
            "Loaded"
        )
    else:
        llm_table.add_row(
            "Model",
            "None",
            "Not Loaded"
        )
    
    llm_table.add_row(
        "CPU Usage",
        f"{ollama_snapshot.cpu_use_pct:.1f}%",
        "Normal" if ollama_snapshot.cpu_use_pct < 80 else "High"
    )
    
    llm_table.add_row(
        "GPU Usage",
        f"{ollama_snapshot.gpu_use_pct:.1f}%",
        "Normal" if ollama_snapshot.gpu_use_pct < 80 else "High"
    )
    
    llm_table.add_row(
        "GPU Layers",
        str(ollama_snapshot.gpu_layers),
        "Normal" if ollama_snapshot.gpu_layers < 10 else "High"
    )
    
    llm_table.add_row(
        "Model Size",
        f"{ollama_snapshot.model_size_bytes / (1024**2):.1f} MB",
        "Normal"
    )
    
    llm_table.add_row(
        "Total Layers",
        str(ollama_snapshot.total_layers),
        "Normal"
    )
    
    # Create a layout section for the table
    layout.split_column(
        Layout(llm_table, size=15),
        Layout("LLM View", size=5)
    )
    
    return layout
