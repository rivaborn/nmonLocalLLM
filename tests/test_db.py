import sqlite3
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

from nmon.db import init_db, prune_old_data, flush_to_db
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot


@pytest.fixture
def mock_db_connection():
    """Mock sqlite3 connection"""
    with patch('nmon.db.sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_time():
    """Mock time.time()"""
    with patch('nmon.db.time.time') as mock_time:
        yield mock_time


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path"""
    return tmp_path / "test.db"


def test_init_db_creates_tables_if_not_exists(mock_db_connection, test_db_path):
    """Test that init_db creates tables if they don't exist"""
    init_db(str(test_db_path))
    
    # Verify that the connection was called with the correct path
    mock_db_connection.execute.assert_any_call(
        "CREATE TABLE IF NOT EXISTS gpu_metrics (timestamp REAL, gpu_id INTEGER, memory_used REAL, memory_total REAL, utilization_gpu REAL, utilization_memory REAL)"
    )
    mock_db_connection.execute.assert_any_call(
        "CREATE TABLE IF NOT EXISTS ollama_metrics (timestamp REAL, model TEXT, gpu_layers INTEGER, total_layers INTEGER, gpu_use_pct REAL, cpu_use_pct REAL, model_size_bytes INTEGER, loaded_model TEXT)"
    )
    mock_db_connection.commit.assert_called_once()


def test_init_db_handles_existing_tables(mock_db_connection, test_db_path):
    """Test that init_db does not fail if tables already exist"""
    # Mock the execute method to raise an exception (simulating existing tables)
    mock_db_connection.execute.side_effect = sqlite3.OperationalError("table already exists")
    
    # This should not raise an exception
    init_db(str(test_db_path))
    
    # Verify that commit was still called
    mock_db_connection.commit.assert_called_once()


def test_prune_old_data_removes_old_rows(mock_db_connection, test_db_path, mock_time):
    """Test that prune_old_data removes rows older than history_hours"""
    # Set up mock time to return a specific value
    current_time = 1640995200  # 2022-01-01 00:00:00 UTC
    mock_time.return_value = current_time
    
    # Create a test database with some data
    init_db(str(test_db_path))
    
    # Insert some test data - some old, some new
    old_timestamp = current_time - 3600 * 25  # 25 hours ago (older than 24h)
    new_timestamp = current_time - 3600 * 5   # 5 hours ago (newer than 24h)
    
    # Insert old data
    mock_db_connection.execute("INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)", 
                              (old_timestamp, 0, 1000.0, 8000.0, 50.0, 60.0))
    mock_db_connection.execute("INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)", 
                              (old_timestamp, 1, 2000.0, 8000.0, 40.0, 50.0))
    
    # Insert new data
    mock_db_connection.execute("INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)", 
                              (new_timestamp, 0, 1500.0, 8000.0, 55.0, 65.0))
    
    # Call prune_old_data with history_hours = 24
    prune_old_data(str(test_db_path), 24)
    
    # Verify that old rows were deleted and new rows remain
    mock_db_connection.execute.assert_any_call(
        "DELETE FROM gpu_metrics WHERE timestamp < ?",
        (current_time - 3600 * 24,)
    )
    mock_db_connection.commit.assert_called_once()


def test_prune_old_data_preserves_new_rows(mock_db_connection, test_db_path, mock_time):
    """Test that prune_old_data preserves rows newer than history_hours"""
    # Set up mock time to return a specific value
    current_time = 1640995200  # 2022-01-01 00:00:00 UTC
    mock_time.return_value = current_time
    
    # Create a test database with some data
    init_db(str(test_db_path))
    
    # Insert some test data - some old, some new
    old_timestamp = current_time - 3600 * 25  # 25 hours ago (older than 24h)
    new_timestamp = current_time - 3600 * 5   # 5 hours ago (newer than 24h)
    
    # Insert old data
    mock_db_connection.execute("INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)", 
                              (old_timestamp, 0, 1000.0, 8000.0, 50.0, 60.0))
    
    # Insert new data
    mock_db_connection.execute("INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)", 
                              (new_timestamp, 0, 1500.0, 8000.0, 55.0, 65.0))
    
    # Call prune_old_data with history_hours = 24
    prune_old_data(str(test_db_path), 24)
    
    # Verify that the new row is still there
    # We can't directly check the data, but we can verify the DELETE query was called correctly
    mock_db_connection.execute.assert_any_call(
        "DELETE FROM gpu_metrics WHERE timestamp < ?",
        (current_time - 3600 * 24,)
    )


def test_flush_to_db_inserts_gpu_snapshots(mock_db_connection, test_db_path):
    """Test that flush_to_db inserts all GPU snapshots into gpu_metrics"""
    # Create test data
    gpu_snapshots = [
        GpuSnapshot(
            timestamp=1640995200,
            gpu_id=0,
            memory_used=1000.0,
            memory_total=8000.0,
            utilization_gpu=50.0,
            utilization_memory=60.0
        ),
        GpuSnapshot(
            timestamp=1640995200,
            gpu_id=1,
            memory_used=2000.0,
            memory_total=8000.0,
            utilization_gpu=40.0,
            utilization_memory=50.0
        )
    ]
    
    # Call flush_to_db
    flush_to_db(str(test_db_path), gpu_snapshots, None)
    
    # Verify that execute was called twice for the GPU snapshots
    assert mock_db_connection.execute.call_count == 2
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)",
        (1640995200, 0, 1000.0, 8000.0, 50.0, 60.0)
    )
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)",
        (1640995200, 1, 2000.0, 8000.0, 40.0, 50.0)
    )
    mock_db_connection.commit.assert_called_once()


def test_flush_to_db_inserts_ollama_snapshot(mock_db_connection, test_db_path):
    """Test that flush_to_db inserts Ollama snapshot into ollama_metrics if not None"""
    # Create test data
    gpu_snapshots = []
    ollama_snapshot = OllamaSnapshot(
        timestamp=1640995200,
        model="test-model",
        gpu_layers=5,
        total_layers=10,
        gpu_use_pct=75.0,
        cpu_use_pct=30.0,
        model_size_bytes=1024,
        loaded_model="test-model"
    )
    
    # Call flush_to_db
    flush_to_db(str(test_db_path), gpu_snapshots, ollama_snapshot)
    
    # Verify that execute was called once for the Ollama snapshot
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO ollama_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (1640995200, "test-model", 5, 10, 75.0, 30.0, 1024, "test-model")
    )
    mock_db_connection.commit.assert_called_once()


def test_flush_to_db_handles_none_ollama_snapshot(mock_db_connection, test_db_path):
    """Test that flush_to_db handles None Ollama snapshot gracefully"""
    # Create test data
    gpu_snapshots = [
        GpuSnapshot(
            timestamp=1640995200,
            gpu_id=0,
            memory_used=1000.0,
            memory_total=8000.0,
            utilization_gpu=50.0,
            utilization_memory=60.0
        )
    ]
    
    # Call flush_to_db with None ollama_snapshot
    flush_to_db(str(test_db_path), gpu_snapshots, None)
    
    # Verify that only GPU data was inserted
    assert mock_db_connection.execute.call_count == 1
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)",
        (1640995200, 0, 1000.0, 8000.0, 50.0, 60.0)
    )
    mock_db_connection.commit.assert_called_once()


def test_flush_to_db_handles_database_errors(mock_db_connection, test_db_path):
    """Test that flush_to_db handles database connection errors gracefully"""
    # Create test data
    gpu_snapshots = [
        GpuSnapshot(
            timestamp=1640995200,
            gpu_id=0,
            memory_used=1000.0,
            memory_total=8000.0,
            utilization_gpu=50.0,
            utilization_memory=60.0
        )
    ]
    
    # Mock execute to raise an exception
    mock_db_connection.execute.side_effect = sqlite3.Error("Database error")
    
    # This should not raise an exception
    flush_to_db(str(test_db_path), gpu_snapshots, None)
    
    # Verify that commit was still called (even if it failed)
    mock_db_connection.commit.assert_called_once()


def test_flush_to_db_inserts_both_gpu_and_ollama_data(mock_db_connection, test_db_path):
    """Test that flush_to_db inserts both GPU and Ollama data when both are provided"""
    # Create test data
    gpu_snapshots = [
        GpuSnapshot(
            timestamp=1640995200,
            gpu_id=0,
            memory_used=1000.0,
            memory_total=8000.0,
            utilization_gpu=50.0,
            utilization_memory=60.0
        )
    ]
    
    ollama_snapshot = OllamaSnapshot(
        timestamp=1640995200,
        model="test-model",
        gpu_layers=5,
        total_layers=10,
        gpu_use_pct=75.0,
        cpu_use_pct=30.0,
        model_size_bytes=1024,
        loaded_model="test-model"
    )
    
    # Call flush_to_db
    flush_to_db(str(test_db_path), gpu_snapshots, ollama_snapshot)
    
    # Verify that both GPU and Ollama data were inserted
    assert mock_db_connection.execute.call_count == 2
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO gpu_metrics VALUES (?, ?, ?, ?, ?, ?)",
        (1640995200, 0, 1000.0, 8000.0, 50.0, 60.0)
    )
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO ollama_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (1640995200, "test-model", 5, 10, 75.0, 30.0, 1024, "test-model")
    )
    mock_db_connection.commit.assert_called_once()
