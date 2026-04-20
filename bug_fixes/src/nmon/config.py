import json
import logging
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, ConfigDict
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class UserPrefs:
    """User-adjustable preferences for the application."""
    refresh_rate: int = 1000
    theme: str = "dark"
    show_gpu: bool = True
    show_temp: bool = True
    show_power: bool = True
    show_llm: bool = True

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = ConfigDict(env_prefix="NMON_")
    
    # Define configuration fields with default values
    app_name: str = "nmon"
    log_level: str = "INFO"
    db_path: str = "./nmon.db"
    prefs_path: str = "./preferences.json"
    gpu_monitor_enabled: bool = True
    temp_monitor_enabled: bool = True
    power_monitor_enabled: bool = True
    llm_monitor_enabled: bool = True

def load_settings() -> Settings:
    """Load application settings from environment variables."""
    return Settings.model_validate_env()

def load_user_prefs(prefs_path: Optional[str] = None) -> UserPrefs:
    """Load user preferences from JSON file or return default preferences."""
    if prefs_path is None:
        prefs_path = Settings().prefs_path
    
    path = Path(prefs_path)
    
    if not path.exists():
        return UserPrefs()
    
    try:
        with open(path, 'r') as f:
            prefs_dict = json.load(f)
        valid_keys = {k for k in prefs_dict if k in UserPrefs.__dataclass_fields__}
        filtered_prefs = {}
        for k in valid_keys:
            val = prefs_dict[k]
            if k == "refresh_rate":
                filtered_prefs[k] = int(val) if val is not None else 1000
            elif k in ("show_gpu", "show_temp", "show_power", "show_llm"):
                filtered_prefs[k] = val if isinstance(val, bool) else str(val).lower() in ("true", "1", "yes") if val is not None else True
            else:
                filtered_prefs[k] = str(val) if val is not None else "dark"
        return UserPrefs(**filtered_prefs)
    except (json.JSONDecodeError, IOError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load user preferences from {prefs_path}: {e}")
        return UserPrefs()

def save_user_prefs(prefs: UserPrefs, prefs_path: Optional[str] = None) -> None:
    """Save user preferences to JSON file."""
    if prefs_path is None:
        prefs_path = Settings().prefs_path
    
    path = Path(prefs_path)
    
    try:
        with open(path, 'w') as f:
            json.dump(prefs.__dict__, f, indent=2)
    except (IOError, TypeError) as e:
        logger.warning(f"Failed to save user preferences to {prefs_path}: {e}")
        raise