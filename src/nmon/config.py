"""
Implement AppConfig dataclass and configuration loading functions in src/nmon/config.py.

The AppConfig class holds all application settings with sensible defaults.
Functions load configuration from environment variables and persistent JSON storage.
The persistent settings only save temp_threshold_c and temp_threshold_visible
as other settings are either derived from environment variables or runtime-only.

Imports:
- os for environment variable access
- json for persistent settings
- platformdirs for user config directory
- dataclass decorator for AppConfig
- typing TYPE_CHECKING for conditional imports

Classes:
- AppConfig: Dataclass holding all application configuration settings

Functions:
- load_from_env(): Load AppConfig from environment variables with defaults
- load_persistent_settings(): Load persisted settings from JSON file
- save_persistent_settings(): Save temp_threshold_c and temp_threshold_visible to JSON file
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional
import os
import json
from platformdirs import user_config_dir

if TYPE_CHECKING:
    from .storage.ring_buffer import RingBuffer
    from .gpu.protocol import GpuSample
    from .llm.protocol import LlmSample
    import httpx

@dataclass
class AppConfig:
    """Application configuration settings."""
    ollama_url: str = "http://192.168.1.126:11434"
    poll_interval_s: float = 2.0
    history_duration_s: float = 86400.0
    temp_threshold_c: float = 95.0
    temp_threshold_visible: bool = True
    mem_junction_visible: bool = True

    # http_client factory - will be set after dataclass construction
    # type: ignore -- set dynamically in main.py
    http_client: "Optional[Callable]" = None  # type: ignore[assignment]

def load_from_env() -> AppConfig:
    """
    Load AppConfig from environment variables with defaults from .env.example.
    
    Returns:
        AppConfig: Configuration instance with values from environment or defaults.
    """
    # Parse ollama_url as str
    ollama_url = os.getenv("OLLAMA_URL", "http://192.168.1.126:11434")
    # Set http_client factory on the config after construction
    # (done in main.py after importing httpx)
    
    # Parse poll_interval_s as float
    poll_interval_s = float(os.getenv("POLL_INTERVAL_S", "2.0"))
    
    # Parse history_duration_s as float
    history_duration_s = float(os.getenv("HISTORY_DURATION_S", "86400.0"))
    
    # Parse temp_threshold_c as float
    temp_threshold_c = float(os.getenv("TEMP_THRESHOLD_C", "95.0"))
    
    # Parse temp_threshold_visible as bool
    temp_threshold_visible = os.getenv("TEMP_THRESHOLD_VISIBLE", "true").lower() == "true"
    
    # Parse mem_junction_visible as bool
    mem_junction_visible = os.getenv("MEM_JUNCTION_VISIBLE", "true").lower() == "true"
    
    return AppConfig(
        ollama_url=ollama_url,
        poll_interval_s=poll_interval_s,
        history_duration_s=history_duration_s,
        temp_threshold_c=temp_threshold_c,
        temp_threshold_visible=temp_threshold_visible,
        mem_junction_visible=mem_junction_visible
    )

def load_persistent_settings() -> AppConfig:
    """
    Load persisted AppConfig from JSON file in user config directory.
    
    Returns:
        AppConfig: Configuration instance with loaded values or defaults.
    """
    config_dir = user_config_dir("nmon")
    config_file = os.path.join(config_dir, "settings.json")
    
    # If file does not exist, return default AppConfig
    if not os.path.exists(config_file):
        return AppConfig()
    
    try:
        with open(config_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        # If JSON decode fails or I/O error, log error and return default AppConfig
        return AppConfig()
    
    # Parse temp_threshold_c and temp_threshold_visible from JSON
    temp_threshold_c = float(data.get("temp_threshold_c", 95.0))
    temp_threshold_visible = bool(data.get("temp_threshold_visible", True))
    
    return AppConfig(
        temp_threshold_c=temp_threshold_c,
        temp_threshold_visible=temp_threshold_visible,
        mem_junction_visible=True  # Default value, not persisted
    )

def save_persistent_settings(config: AppConfig) -> None:
    """
    Save temp_threshold_c and temp_threshold_visible to JSON file in user config directory.
    
    Args:
        config: AppConfig instance to save.
    """
    config_dir = user_config_dir("nmon")
    config_file = os.path.join(config_dir, "settings.json")
    
    try:
        # Ensure directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Open file for writing
        with open(config_file, "w") as f:
            # Serialize temp_threshold_c and temp_threshold_visible to JSON
            json.dump({
                "temp_threshold_c": config.temp_threshold_c,
                "temp_threshold_visible": config.temp_threshold_visible
            }, f)
    except IOError:
        # Handle any I/O errors by logging and ignoring
        pass
