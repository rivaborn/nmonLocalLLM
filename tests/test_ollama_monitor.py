import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import the OllamaSnapshot dataclass
from src.nmon.ollama_monitor import OllamaSnapshot

def test_ollama_snapshot_creation():
    """Test that OllamaSnapshot can be created with all required fields"""
    snapshot = OllamaSnapshot(
        timestamp=1640995200.0,
        reachable=True,
        loaded_model="llama2:7b",
        model_size_bytes=123456789,
        gpu_use_pct=75.5,
        cpu_use_pct=30.2,
        gpu_layers=32,
        total_layers=40
    )
    
    assert snapshot.timestamp == 1640995200.0
    assert snapshot.reachable is True
    assert snapshot.loaded_model == "llama2:7b"
    assert snapshot.model_size_bytes == 123456789
    assert snapshot.gpu_use_pct == 75.5
    assert snapshot.cpu_use_pct == 30.2
    assert snapshot.gpu_layers == 32
    assert snapshot.total_layers == 40

def test_ollama_snapshot_optional_fields():
    """Test that OllamaSnapshot handles None values correctly"""
    snapshot = OllamaSnapshot(
        timestamp=1640995200.0,
        reachable=False,
        loaded_model=None,
        model_size_bytes=None,
        gpu_use_pct=None,
        cpu_use_pct=None,
        gpu_layers=None,
        total_layers=None
    )
    
    assert snapshot.timestamp == 1640995200.0
    assert snapshot.reachable is False
    assert snapshot.loaded_model is None
    assert snapshot.model_size_bytes is None
    assert snapshot.gpu_use_pct is None
    assert snapshot.cpu_use_pct is None
    assert snapshot.gpu_layers is None
    assert snapshot.total_layers is None

def test_ollama_snapshot_default_values():
    """Test that OllamaSnapshot can be created with default values"""
    snapshot = OllamaSnapshot(
        timestamp=1640995200.0,
        reachable=True,
        loaded_model="test-model",
        model_size_bytes=0,
        gpu_use_pct=0.0,
        cpu_use_pct=0.0,
        gpu_layers=0,
        total_layers=0
    )
    
    assert snapshot.timestamp == 1640995200.0
    assert snapshot.reachable is True
    assert snapshot.loaded_model == "test-model"
    assert snapshot.model_size_bytes == 0
    assert snapshot.gpu_use_pct == 0.0
    assert snapshot.cpu_use_pct == 0.0
    assert snapshot.gpu_layers == 0
    assert snapshot.total_layers == 0

def test_ollama_snapshot_field_types():
    """Test that OllamaSnapshot fields have correct types"""
    snapshot = OllamaSnapshot(
        timestamp=1640995200.0,
        reachable=True,
        loaded_model="test-model",
        model_size_bytes=1000,
        gpu_use_pct=50.0,
        cpu_use_pct=25.0,
        gpu_layers=10,
        total_layers=20
    )
    
    # Test timestamp (float)
    assert isinstance(snapshot.timestamp, float)
    
    # Test reachable (bool)
    assert isinstance(snapshot.reachable, bool)
    
    # Test loaded_model (str or None)
    assert isinstance(snapshot.loaded_model, str) or snapshot.loaded_model is None
    
    # Test model_size_bytes (int or None)
    assert isinstance(snapshot.model_size_bytes, int) or snapshot.model_size_bytes is None
    
    # Test gpu_use_pct (float or None)
    assert isinstance(snapshot.gpu_use_pct, float) or snapshot.gpu_use_pct is None
    
    # Test cpu_use_pct (float or None)
    assert isinstance(snapshot.cpu_use_pct, float) or snapshot.cpu_use_pct is None
    
    # Test gpu_layers (int or None)
    assert isinstance(snapshot.gpu_layers, int) or snapshot.gpu_layers is None
    
    # Test total_layers (int or None)
    assert isinstance(snapshot.total_layers, int) or snapshot.total_layers is None
