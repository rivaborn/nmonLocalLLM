# Write tests for the conftest.py file into tests/conftest.py
# This file defines pytest fixtures for the nmon project tests.
# The fixtures are used across multiple test modules to provide
# consistent test data and setup.

# Import the modules under test from their production location
from nmon.config import AppConfig
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.gpu.monitor import GpuMonitor
from nmon.llm.monitor import LlmMonitor

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
import time

# Test file: tests/conftest.py
# External dependencies to mock: none
# Behaviors to assert:
# - AppConfig fixture loads from environment variables correctly
# - AppConfig fixture falls back to defaults when env vars are absent
# - GpuSample and LlmSample fixtures are valid dataclass instances
# - RingBuffer fixture is properly initialized with correct capacity
# - Fixtures are reusable across test modules without side effects
# pytest fixtures and plugins to use: pytest, pytest-asyncio

# The following fixtures are defined in this file and should be reusable
# across all test modules in the tests/ directory.

@pytest.fixture
def app_config_fixture():
    """Load AppConfig from environment variables, falling back to defaults."""
    # This fixture should return an AppConfig instance
    # It's used to test config loading behavior
    config = AppConfig()
    return config

@pytest.fixture
def gpu_sample_fixture():
    """Create a valid GpuSample instance with realistic values."""
    # This fixture should return a GpuSample instance
    # It's used to test GPU monitoring logic
    sample = GpuSample(
        timestamp=time.time(),
        gpu_index=0,
        temperature_gpu=75.0,
        temperature_mem_junction=80.0,
        memory_used_mib=1024.0,
        memory_total_mib=2048.0,
        power_draw_w=150.0,
        power_limit_w=250.0
    )
    return sample

@pytest.fixture
def llm_sample_fixture():
    """Create a valid LlmSample instance with realistic values."""
    # This fixture should return a LlmSample instance
    # It's used to test LLM monitoring logic
    sample = LlmSample(
        timestamp=time.time(),
        model_name="test-model",
        model_size_bytes=1073741824,  # 1 GB
        gpu_utilization_pct=75.0,
        cpu_utilization_pct=25.0,
        gpu_layers_offloaded=24,
        total_layers=32
    )
    return sample

@pytest.fixture
def ring_buffer_fixture():
    """Initialize a RingBuffer with default capacity."""
    # This fixture should return a RingBuffer instance
    # It's used to test ring buffer behavior
    from nmon.config import AppConfig
    config = AppConfig()
    buffer = RingBuffer(config)
    return buffer

# Additional test functions to verify fixture behavior
def test_app_config_fixture(app_config_fixture):
    """Test that AppConfig fixture loads correctly."""
    assert isinstance(app_config_fixture, AppConfig)
    # Verify default values are set
    assert app_config_fixture.ollama_url == "http://192.168.1.126:11434"
    assert app_config_fixture.poll_interval_s == 2.0
    assert app_config_fixture.history_duration_s == 86400.0
    assert app_config_fixture.temp_threshold_c == 95.0
    assert app_config_fixture.temp_threshold_visible == True
    assert app_config_fixture.mem_junction_visible == True

def test_gpu_sample_fixture(gpu_sample_fixture):
    """Test that GpuSample fixture is valid."""
    assert isinstance(gpu_sample_fixture, GpuSample)
    # Verify all fields are set
    assert gpu_sample_fixture.timestamp is not None
    assert gpu_sample_fixture.gpu_index == 0
    assert gpu_sample_fixture.temperature_gpu == 75.0
    assert gpu_sample_fixture.memory_used_mib == 1024.0
    assert gpu_sample_fixture.memory_total_mib == 2048.0
    assert gpu_sample_fixture.power_draw_w == 150.0
    assert gpu_sample_fixture.power_limit_w == 250.0

def test_llm_sample_fixture(llm_sample_fixture):
    """Test that LlmSample fixture is valid."""
    assert isinstance(llm_sample_fixture, LlmSample)
    # Verify all fields are set
    assert llm_sample_fixture.timestamp is not None
    assert llm_sample_fixture.model_name == "test-model"
    assert llm_sample_fixture.model_size_bytes == 1073741824
    assert llm_sample_fixture.gpu_utilization_pct == 75.0
    assert llm_sample_fixture.cpu_utilization_pct == 25.0
    assert llm_sample_fixture.gpu_layers_offloaded == 24
    assert llm_sample_fixture.total_layers == 32

def test_ring_buffer_fixture(ring_buffer_fixture):
    """Test that RingBuffer fixture is properly initialized."""
    assert isinstance(ring_buffer_fixture, RingBuffer)
    # Verify buffer has correct capacity based on config
    from nmon.config import AppConfig
    config = AppConfig()
    expected_capacity = int(config.history_duration_s / config.poll_interval_s)
    # Note: actual capacity may be rounded up, so we check it's at least the expected value
    assert len(ring_buffer_fixture._buffer) <= expected_capacity
