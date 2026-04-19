import json
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
from pytest_mock import MockerFixture

from nmon.config import AppConfig, load_from_env, load_persistent_settings, save_persistent_settings


def test_load_from_env_uses_defaults_when_env_vars_absent(monkeypatch):
    """Test that load_from_env() falls back to defaults when env vars are absent."""
    # Clear all relevant env vars
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    monkeypatch.delenv("POLL_INTERVAL_S", raising=False)
    monkeypatch.delenv("HISTORY_DURATION_S", raising=False)
    monkeypatch.delenv("TEMP_THRESHOLD_C", raising=False)
    monkeypatch.delenv("TEMP_THRESHOLD_VISIBLE", raising=False)
    monkeypatch.delenv("MEM_JUNCTION_VISIBLE", raising=False)

    config = load_from_env()
    assert config.ollama_url == "http://192.168.1.126:11434"
    assert config.poll_interval_s == 2.0
    assert config.history_duration_s == 86400.0
    assert config.temp_threshold_c == 95.0
    assert config.temp_threshold_visible is True
    assert config.mem_junction_visible is True


def test_load_from_env_parses_all_env_vars(monkeypatch):
    """Test that load_from_env() correctly parses all environment variables."""
    monkeypatch.setenv("OLLAMA_URL", "http://localhost:11434")
    monkeypatch.setenv("POLL_INTERVAL_S", "1.5")
    monkeypatch.setenv("HISTORY_DURATION_S", "43200.0")
    monkeypatch.setenv("TEMP_THRESHOLD_C", "90.0")
    monkeypatch.setenv("TEMP_THRESHOLD_VISIBLE", "false")
    monkeypatch.setenv("MEM_JUNCTION_VISIBLE", "false")

    config = load_from_env()
    assert config.ollama_url == "http://localhost:11434"
    assert config.poll_interval_s == 1.5
    assert config.history_duration_s == 43200.0
    assert config.temp_threshold_c == 90.0
    assert config.temp_threshold_visible is False
    assert config.mem_junction_visible is False


def test_load_persistent_settings_returns_default_when_file_does_not_exist(monkeypatch, tmp_path):
    """Test that load_persistent_settings() returns default config when file does not exist."""
    # Mock platformdirs to return a tmp directory
    config_dir = tmp_path / "nmon"
    config_dir.mkdir()
    monkeypatch.setattr("platformdirs.user_config_dir", lambda appname: str(config_dir))

    # Ensure settings.json does not exist
    settings_file = config_dir / "settings.json"
    assert not settings_file.exists()

    config = load_persistent_settings()
    # Should return default AppConfig
    assert config.temp_threshold_c == 95.0
    assert config.temp_threshold_visible is True


def test_load_persistent_settings_falls_back_to_defaults_when_json_corrupted(monkeypatch, tmp_path):
    """Test that load_persistent_settings() falls back to defaults when JSON is corrupted."""
    # Mock platformdirs to return a tmp directory
    config_dir = tmp_path / "nmon"
    config_dir.mkdir()
    monkeypatch.setattr("platformdirs.user_config_dir", lambda appname: str(config_dir))

    # Create a corrupted JSON file
    settings_file = config_dir / "settings.json"
    settings_file.write_text("this is not valid json")

    config = load_persistent_settings()
    # Should fall back to defaults
    assert config.temp_threshold_c == 95.0
    assert config.temp_threshold_visible is True


def test_save_persistent_settings_only_saves_threshold_fields(monkeypatch, tmp_path):
    """Test that save_persistent_settings() persists only temp_threshold_c and temp_threshold_visible."""
    # Mock platformdirs to return a tmp directory
    config_dir = tmp_path / "nmon"
    config_dir.mkdir()
    monkeypatch.setattr("platformdirs.user_config_dir", lambda appname: str(config_dir))

    # Create a config with non-default values for other fields
    config = AppConfig(
        ollama_url="http://localhost:11434",
        poll_interval_s=1.5,
        history_duration_s=43200.0,
        temp_threshold_c=90.0,
        temp_threshold_visible=False,
        mem_junction_visible=False
    )

    save_persistent_settings(config)

    # Check that only the threshold fields were saved
    settings_file = config_dir / "settings.json"
    assert settings_file.exists()
    with open(settings_file, "r") as f:
        saved_data = json.load(f)
    assert saved_data["temp_threshold_c"] == 90.0
    assert saved_data["temp_threshold_visible"] is False
    # Other fields should not be in the saved file
    assert "ollama_url" not in saved_data
    assert "poll_interval_s" not in saved_data
    assert "history_duration_s" not in saved_data
    assert "mem_junction_visible" not in saved_data


def test_save_persistent_settings_handles_io_errors(monkeypatch, tmp_path, mocker: MockerFixture):
    """Test that save_persistent_settings() does not raise on I/O errors."""
    # Mock platformdirs to return a tmp directory
    config_dir = tmp_path / "nmon"
    config_dir.mkdir()
    monkeypatch.setattr("platformdirs.user_config_dir", lambda appname: str(config_dir))

    # Mock open to raise an exception
    mocker.patch("builtins.open", side_effect=IOError("Disk full"))

    # This should not raise
    config = AppConfig(temp_threshold_c=90.0, temp_threshold_visible=False)
    save_persistent_settings(config)
