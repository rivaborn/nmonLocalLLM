from nmon.ollama_monitor import OllamaSnapshot
from nmon.history import HistoryStore
from nmon.config import Settings, UserPrefs
from nmon.alerts import AlertState
from nmon.widgets.sparkline import Sparkline
from rich.layout import Layout
from rich.panel import Panel


def render_llm_view(
    ollama_snapshot: OllamaSnapshot,
    history_store: HistoryStore,
    settings: Settings,
    prefs: UserPrefs,
    now: float
) -> Layout:
    # If Ollama is not reachable, return a layout with an offline message
    if not ollama_snapshot.reachable:
        layout = Layout()
        layout.split_row(
            Panel("Ollama offline")
        )
        return layout
    
    # Otherwise, fetch GPU and CPU usage series
    gpu_series = history_store.get_gpu_usage_series(
        start_time=now - prefs.active_time_range_hours * 3600
    )
    cpu_series = history_store.get_cpu_usage_series(
        start_time=now - prefs.active_time_range_hours * 3600
    )
    
    # Create the sparkline
    sparkline = Sparkline(
        title="LLM Server Usage",
        series=[("GPU Use %", gpu_series), ("CPU Use %", cpu_series)],
        y_range=(0, 100),
        guide_lines=[0, 100],
        width=80,
        height=10
    )
    
    # Create a panel containing the sparkline
    panel = Panel(sparkline)
    
    # Return a layout with one panel (the sparkline panel)
    layout = Layout()
    layout.split_row(panel)
    return layout
