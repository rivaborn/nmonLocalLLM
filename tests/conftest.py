"""
Pytest fixtures for nmon tests.

This file defines shared fixtures used across all test modules in the tests/ directory.
Fixtures provide consistent test setup and mocking behavior for external dependencies.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

from nmon.config import Settings, UserPrefs
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.history import HistoryStore
from nmon.db import DbConnection

@pytest.fixture
def tmp_path():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def monkeypatch():
    """Provide monkeypatch fixture for modifying environment variables and global state."""
    # This fixture is provided by pytest automatically
    pass

@pytest.fixture
def mock_pynvml():
    """Mock the pynvml library for GPU monitoring tests."""
    with patch('nmon.gpu_monitor.pynvml') as mock_pynvml:
        yield mock_pynvml

@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for Ollama monitoring tests."""
    with patch('nmon.ollama_monitor.httpx.AsyncClient') as mock_client:
        yield mock_client

@pytest.fixture
def mock_db_connection():
    """Mock sqlite3.Connection for database tests."""
    with patch('nmon.db.sqlite3.connect') as mock_connect:
        mock_conn = MagicMock(spec=DbConnection)
        mock_connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture
def mock_settings():
    """Provide a default Settings instance for tests."""
    return Settings(
        ollama_base_url="http://192.168.1.126:11434",
        poll_interval_s=2.0,
        history_hours=24,
        db_path="nmon.db",
        prefs_path="preferences.json",
        min_alert_display_s=1.0,
        offload_alert_pct=5.0
    )

@pytest.fixture
def mock_user_prefs():
    """Provide a default UserPrefs instance for tests."""
    return UserPrefs(
        temp_threshold_c=95.0,
        show_threshold_line=True,
        show_mem_junction=True,
        active_view=0,
        active_time_range_hours=1.0
    )

@pytest.fixture
def mock_gpu_snapshot():
    """Provide a default GpuSnapshot instance for tests."""
    return GpuSnapshot(
        gpu_index=0,
        timestamp=1678886400.0,
        temperature_c=75.0,
        mem_junction_temp_c=80.0,
        memory_used_mb=4096.0,
        memory_total_mb=8192.0,
        power_draw_w=150.0,
        power_limit_w=250.0
    )

@pytest.fixture
def mock_ollama_snapshot():
    """Provide a default OllamaSnapshot instance for tests."""
    return OllamaSnapshot(
        timestamp=1678886400.0,
        reachable=True,
        loaded_model="llama3:8b",
        model_size_bytes=4000000000,
        gpu_use_pct=85.0,
        cpu_use_pct=15.0,
        gpu_layers=40,
        total_layers=48
    )

@pytest.fixture
def mock_history_store():
    """Provide a default HistoryStore instance for tests."""
    # This fixture would typically be implemented by creating a mock HistoryStore
    # that doesn't actually connect to a database, but for now we'll return a mock
    return MagicMock(spec=HistoryStore)
