"""
Alert state management for nmon terminal dashboard.

This module handles the computation and rendering of alert states based on
Ollama snapshot data. Alerts are displayed in the top bar of the dashboard
when GPU offload is below a configured threshold.
"""

from dataclasses import dataclass
from typing import Optional

from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import Settings


@dataclass
class AlertState:
    """
    Represents the current alert state for display in the dashboard.
    
    Attributes:
        active: Whether the alert is currently visible.
        message: Text to display in the alert bar.
        color: Color of the alert ("orange" or "red").
        expires_at: Unix timestamp when the alert should expire.
    """
    active: bool
    message: str
    color: str          # "orange" | "red"
    expires_at: float   # time.time() + min_display_seconds


def compute_alert(snapshot: OllamaSnapshot, settings: Settings, now: float) -> Optional[AlertState]:
    """
    Compute the current alert state based on Ollama snapshot data.
    
    An alert is triggered when:
    - Ollama is reachable (snapshot.reachable is True)
    - GPU use percentage is available (snapshot.gpu_use_pct is not None)
    - GPU offload is below 100% but layers are being used
    
    The alert color is determined by the GPU use percentage relative to
    settings.offload_alert_pct:
    - If gpu_use_pct > offload_alert_pct, color is "red"
    - Otherwise, color is "orange"
    
    Args:
        snapshot: Latest Ollama snapshot data.
        settings: Application settings including alert thresholds.
        now: Current timestamp (time.time()).
        
    Returns:
        AlertState instance if alert should be active, None otherwise.
    """
    # If Ollama is unreachable or GPU use is not available, no alert
    if not snapshot.reachable or snapshot.gpu_use_pct is None:
        return None
        
    # Only alert if GPU offload is below 100% but layers are being used
    if snapshot.gpu_use_pct < 100 and snapshot.gpu_layers is not None:
        # Set alert message
        message = "GPU offload below 100%"
        
        # Determine alert color based on threshold
        if snapshot.gpu_use_pct > settings.offload_alert_pct:
            color = "red"
        else:
            color = "orange"
            
        # Set expiration time
        expires_at = now + settings.min_alert_display_s
        
        return AlertState(
            active=True,
            message=message,
            color=color,
            expires_at=expires_at
        )
        
    # No alert conditions met
    return None
