import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pydantic import ValidationError

from nmon.config import Settings, UserPrefs, load_settings, load_user_prefs, save_user_prefs


def test_load_settings_valid_env(tmp_path):
    # Arrange
    env_file = tmp_path / ".env"
    env_file.write_text("NMON_OLLAMA_BASE_URL=http://localhost:11434\nNMON_POLL_INTERVAL_S=5.0\n")
    
    with patch("nmon.config.dotenv.find_dotenv", return_value=str(env_file)):
        # Act
        settings = load_settings()
        
        # Assert
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.poll_interval_s == 5.0
        assert settings.history_hours == 24  # default
        assert settings.db_path == "nmon.db"  # default
        assert settings.prefs_path == "preferences.json"  # default
        assert settings.min_alert_display_s == 1.0  # default
        assert settings.offload_alert_pct == 5.0  # default


def test_load_settings_invalid_env_raises_validation_error(tmp_path):
    # Arrange
    env_file = tmp_path / ".env"
    env_file.write_text("NMON_POLL_INTERVAL_S=invalid\n")
    
    with patch("nmon.config.dotenv.find_dotenv", return_value=str(env_file)):
        # Act & Assert
        with pytest.raises(ValidationError):
            load_settings()


def test_load_user_prefs_file_does_not_exist_returns_defaults(tmp_path):
    # Arrange
    prefs_path = tmp_path / "preferences.json"
    # prefs_path does not exist
    
    # Act
    prefs = load_user_prefs(prefs_path)
    
    # Assert
    assert prefs.temp_threshold_c == 95.0  # default
    assert prefs.show_threshold_line == True  # default
    assert prefs.show_mem_junction == True  # default
    assert prefs.active_view == 0  # default
    assert prefs.active_time_range_hours == 1.0  # default


def test_load_user_prefs_file_exists_deserializes_correctly(tmp_path):
    # Arrange
    prefs_path = tmp_path / "preferences.json"
    prefs_data = {
        "temp_threshold_c": 90.0,
        "show_threshold_line": False,
        "show_mem_junction": False,
        "active_view": 1,
        "active_time_range_hours": 2.0
    }
    prefs_path.write_text(json.dumps(prefs_data))
    
    # Act
    prefs = load_user_prefs(prefs_path)
    
    # Assert
    assert prefs.temp_threshold_c == 90.0
    assert prefs.show_threshold_line == False
    assert prefs.show_mem_junction == False
    assert prefs.active_view == 1
    assert prefs.active_time_range_hours == 2.0


def test_save_user_prefs_writes_valid_json(tmp_path):
    # Arrange
    prefs_path = tmp_path / "preferences.json"
    prefs = UserPrefs(
        temp_threshold_c=90.0,
        show_threshold_line=False,
        show_mem_junction=False,
        active_view=1,
        active_time_range_hours=2.0
    )
    
    # Act
    save_user_prefs(prefs, prefs_path)
    
    # Assert
    assert prefs_path.exists()
    with open(prefs_path, "r") as f:
        data = json.load(f)
    assert data["temp_threshold_c"] == 90.0
    assert data["show_threshold_line"] == False
    assert data["show_mem_junction"] == False
    assert data["active_view"] == 1
    assert data["active_time_range_hours"] == 2.0


def test_save_user_prefs_handles_write_errors_gracefully(tmp_path, caplog):
    # Arrange
    prefs_path = tmp_path / "preferences.json"
    prefs = UserPrefs()
    
    # Mock open to raise an exception
    with patch("builtins.open", side_effect=IOError("Disk full")):
        # Act
        save_user_prefs(prefs, prefs_path)
        
        # Assert
        assert "Warning" in caplog.text
        assert "Disk full" in caplog.text
