import pytest
from collections import deque
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import the classes we need to test
from src.nmon.config import Settings
from src.nmon.history import HistoryStore
from src.nmon.gpu_monitor import GpuSnapshot
from src.nmon.ollama_monitor import OllamaSnapshot

def test_history_store_init():
    """Test HistoryStore initialization"""
    # Create mock settings
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    # Create HistoryStore instance
    history = HistoryStore(settings)
    
    # Verify initialization
    assert hasattr(history, 'gpu_snapshots')
    assert hasattr(history, 'ollama_snapshots')
    assert history.settings == settings

def test_add_gpu_samples():
    """Test adding GPU samples to history"""
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    history = HistoryStore(settings)
    
    # Create test samples
    samples = [
        GpuSnapshot(
            timestamp=datetime.now(),
            gpu_index=0,
            memory_used=100,
            memory_total=200,
            utilization=50,
            temperature=60,
            power=100
        )
    ]
    
    # Add samples
    history.add_gpu_samples(samples)
    
    # Verify samples were added
    assert len(history.gpu_snapshots) == 1

def test_add_ollama_sample():
    """Test adding Ollama samples to history"""
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    history = HistoryStore(settings)
    
    # Create test sample
    sample = OllamaSnapshot(
        timestamp=datetime.now(),
        model="test_model",
        gpu_use_pct=75,
        cpu_use_pct=50,
        gpu_layers=10,
        total_layers=20,
        model_size_bytes=1024
    )
    
    # Add sample
    history.add_ollama_sample(sample)
    
    # Verify sample was added
    assert len(history.ollama_snapshots) == 1

def test_gpu_series():
    """Test retrieving GPU series data"""
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    history = HistoryStore(settings)
    
    # Add test samples
    now = datetime.now()
    samples = [
        GpuSnapshot(
            timestamp=now,
            gpu_index=0,
            memory_used=100,
            memory_total=200,
            utilization=50,
            temperature=60,
            power=100
        ),
        GpuSnapshot(
            timestamp=now - timedelta(hours=1),
            gpu_index=0,
            memory_used=150,
            memory_total=200,
            utilization=75,
            temperature=70,
            power=150
        )
    ]
    
    history.add_gpu_samples(samples)
    
    # Retrieve series
    series = history.gpu_series(0, 2)
    
    # Verify results
    assert len(series) == 2

def test_ollama_series():
    """Test retrieving Ollama series data"""
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    history = HistoryStore(settings)
    
    # Add test samples
    now = datetime.now()
    samples = [
        OllamaSnapshot(
            timestamp=now,
            model="test_model",
            gpu_use_pct=75,
            cpu_use_pct=50,
            gpu_layers=10,
            total_layers=20,
            model_size_bytes=1024
        ),
        OllamaSnapshot(
            timestamp=now - timedelta(hours=1),
            model="test_model",
            gpu_use_pct=80,
            cpu_use_pct=55,
            gpu_layers=12,
            total_layers=20,
            model_size_bytes=1024
        )
    ]
    
    history.add_ollama_sample(samples[0])
    history.add_ollama_sample(samples[1])
    
    # Retrieve series
    series = history.ollama_series(2)
    
    # Verify results
    assert len(series) == 2

def test_gpu_stat():
    """Test GPU statistics calculation"""
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    history = HistoryStore(settings)
    
    # Add test samples
    now = datetime.now()
    samples = [
        GpuSnapshot(
            timestamp=now,
            gpu_index=0,
            memory_used=100,
            memory_total=200,
            utilization=50,
            temperature=60,
            power=100
        ),
        GpuSnapshot(
            timestamp=now - timedelta(hours=1),
            gpu_index=0,
            memory_used=150,
            memory_total=200,
            utilization=75,
            temperature=70,
            power=150
        )
    ]
    
    history.add_gpu_samples(samples)
    
    # Test max utilization
    max_util = history.gpu_stat(0, "utilization", 2, "max")
    assert max_util == 75.0
    
    # Test average utilization
    avg_util = history.gpu_stat(0, "utilization", 2, "avg")
    assert avg_util == 62.5

def test_flush_to_db():
    """Test flushing data to database"""
    settings = Mock(spec=Settings)
    settings.history_hours = 24
    settings.poll_interval = 5
    
    history = HistoryStore(settings)
    
    # Mock database connection
    db = Mock()
    
    # Mock the flush_to_db function from db module
    with patch('src.nmon.db.flush_to_db') as mock_flush:
        history.flush_to_db(db)
        
        # Verify flush was called
        mock_flush.assert_called_once_with(db, history.gpu_snapshots, history.ollama_snapshots)
