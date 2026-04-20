import json
import logging
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
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
    class Config:
        env_prefix = "NMON_"
    
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
        return UserPrefs(**prefs_dict)
    except (json.JSONDecodeError, IOError) as e:
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
    except IOError as e:
        logger.warning(f"Failed to save user preferences to {prefs_path}: {e}")
