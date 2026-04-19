"""
Test file for GpuMonitor class in src/nmon/gpu/monitor.py.

This file tests the GpuMonitor class behavior including:
- Initialization with AppConfig and RingBuffer
- Starting and stopping monitoring
- Polling logic with and without NVMLError exceptions
- Memory junction support detection
- Proper handling of device failures

External dependencies to mock:
- pynvml (nvmlInit, nvmlShutdown, nvmlDeviceGetHandleByIndex, nvmlDeviceGetName, nvmlDeviceGetTemperature, nvmlDeviceGetMemoryInfo, nvmlDeviceGetPowerUsage, nvmlDeviceGetPowerManagementLimit)
- asyncio (for task management)
- threading (for lock behavior)

Behaviors to assert:
1. _poll() returns a list of GpuSample objects when all devices are accessible
2. _poll() returns sentinel samples with None fields when a device raises NVMLError
3. _supports_mem_junction() returns False when nvmlDeviceGetMemoryInfo raises NVMLError_NotSupported
4. start() spawns a background task that calls _poll() periodically
5. stop() cancels the background task and calls nvmlShutdown()
6. GpuMonitor correctly initializes with a RingBuffer and AppConfig
7. _poll() does not raise when individual device calls fail, but logs warnings
8. GpuMonitor correctly handles multiple GPUs and their unique handles

Coverage goals: must exercise both the happy path AND the NVMLError branch for each device
"""

import asyncio
from unittest.mock import MagicMock, patch, call
import pytest
import pynvml
from pynvml import NVMLError, NVMLError_NotSupported

from nmon.gpu.monitor import GpuMonitor
from nmon.gpu.protocol import GpuSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer


@pytest.fixture
def mock_config():
    """Create a mock AppConfig instance."""
    config = MagicMock(spec=AppConfig)
    config.poll_interval_s = 2.0
    return config


@pytest.fixture
def mock_buffer():
    """Create a mock RingBuffer instance."""
    buffer = MagicMock(spec=RingBuffer)
    return buffer


@pytest.fixture
def mock_nvml():
    """Mock the entire pynvml module."""
    with patch('nmon.gpu.monitor.pynvml') as mock_pynvml:
        yield mock_pynvml


def test_gpu_monitor_initialization(mock_config, mock_buffer, mock_nvml):
    """Test that GpuMonitor initializes correctly with AppConfig and RingBuffer."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Verify initialization
    assert monitor.config == mock_config
    assert monitor.buffer == mock_buffer
    assert monitor.running is False
    assert monitor.task is None
    assert monitor.device_handles == ["mock_handle_0"]
    
    # Verify NVML was initialized
    mock_nvml.nvmlInit.assert_called_once()
    mock_nvml.nvmlDeviceGetHandleByIndex.assert_called_once_with(0)


def test_gpu_monitor_start_stop(mock_config, mock_buffer, mock_nvml):
    """Test that GpuMonitor start and stop methods work correctly."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Start the monitor
    monitor.start()
    
    # Verify it's running and task was created
    assert monitor.running is True
    assert monitor.task is not None
    
    # Stop the monitor
    monitor.stop()
    
    # Verify it's not running and task was cancelled
    assert monitor.running is False
    assert monitor.task is None
    mock_nvml.nvmlShutdown.assert_called_once()


def test_gpu_monitor_poll_success(mock_config, mock_buffer, mock_nvml):
    """Test that _poll returns correct GpuSample values when pynvml calls are mocked."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    # Mock successful device data retrieval
    mock_nvml.nvmlDeviceGetName.return_value = "GeForce RTX 3080"
    mock_nvml.nvmlDeviceGetTemperature.return_value = 75
    mock_nvml.nvmlDeviceGetMemoryInfo.return_value = MagicMock(total=8589934592, free=4294967296, used=4294967296)
    mock_nvml.nvmlDeviceGetPowerUsage.return_value = 250000
    mock_nvml.nvmlDeviceGetPowerManagementLimit.return_value = 300000
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Mock time.time to return a fixed timestamp
    with patch('time.time', return_value=1234567890.0):
        samples = monitor._poll()
    
    # Verify the sample was created correctly
    assert len(samples) == 1
    sample = samples[0]
    assert isinstance(sample, GpuSample)
    assert sample.timestamp == 1234567890.0
    assert sample.gpu_index == 0
    assert sample.temperature_gpu == 75.0
    assert sample.memory_used_mib == 4096.0  # 4294967296 bytes / (1024 * 1024)
    assert sample.memory_total_mib == 8192.0  # 8589934592 bytes / (1024 * 1024)
    assert sample.power_draw_w == 0.25  # 250000 microW / 1000000
    assert sample.power_limit_w == 0.3  # 300000 microW / 1000000


def test_gpu_monitor_poll_with_nvmLError(mock_config, mock_buffer, mock_nvml):
    """Test that _poll does not raise when a per-device NVMLError occurs; inserts sentinel sample."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    # Mock an NVMLError to be raised during device data retrieval
    mock_nvml.nvmlDeviceGetTemperature.side_effect = NVMLError(NVMLError_NotSupported)
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Mock time.time to return a fixed timestamp
    with patch('time.time', return_value=1234567890.0):
        samples = monitor._poll()
    
    # Verify a sentinel sample was created
    assert len(samples) == 1
    sample = samples[0]
    assert isinstance(sample, GpuSample)
    assert sample.timestamp == 1234567890.0
    assert sample.gpu_index == 0
    assert sample.temperature_gpu is None
    assert sample.temperature_mem_junction is None
    assert sample.memory_used_mib is None
    assert sample.memory_total_mib is None
    assert sample.power_draw_w is None
    assert sample.power_limit_w is None


def test_gpu_monitor_supports_mem_junction_success(mock_config, mock_buffer, mock_nvml):
    """Test that _supports_mem_junction returns True when nvmlDeviceGetMemoryInfo succeeds."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    # Mock successful device data retrieval
    mock_nvml.nvmlDeviceGetMemoryInfo.return_value = MagicMock(total=8589934592, free=4294967296, used=4294967296)
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Test the method
    result = monitor._supports_mem_junction("mock_handle_0")
    
    # Verify it returned True
    assert result is True


def test_gpu_monitor_supports_mem_junction_not_supported(mock_config, mock_buffer, mock_nvml):
    """Test that _supports_mem_junction returns False when nvmlDeviceGetMemoryInfo raises NVMLError_NotSupported."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    # Mock an NVMLError_NotSupported to be raised
    mock_nvml.nvmlDeviceGetMemoryInfo.side_effect = NVMLError(NVMLError_NotSupported)
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Test the method
    result = monitor._supports_mem_junction("mock_handle_0")
    
    # Verify it returned False
    assert result is False


def test_gpu_monitor_poll_loop(mock_config, mock_buffer, mock_nvml):
    """Test that _poll_loop calls _poll and appends to buffer."""
    # Mock the NVML initialization and device handle retrieval
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.return_value = "mock_handle_0"
    
    # Mock successful device data retrieval
    mock_nvml.nvmlDeviceGetName.return_value = "GeForce RTX 3080"
    mock_nvml.nvmlDeviceGetTemperature.return_value = 75
    mock_nvml.nvmlDeviceGetMemoryInfo.return_value = MagicMock(total=8589934592, free=4294967296, used=4294967296)
    mock_nvml.nvmlDeviceGetPowerUsage.return_value = 250000
    mock_nvml.nvmlDeviceGetPowerManagementLimit.return_value = 300000
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Mock time.time to return a fixed timestamp
    with patch('time.time', return_value=1234567890.0):
        # Mock the async sleep to avoid waiting
        with patch('asyncio.sleep') as mock_sleep:
            # Mock the _poll method to return a sample
            with patch.object(monitor, '_poll', return_value=[GpuSample(
                timestamp=1234567890.0,
                gpu_index=0,
                temperature_gpu=75.0,
                temperature_mem_junction=None,
                memory_used_mib=4096.0,
                memory_total_mib=8192.0,
                power_draw_w=0.25,
                power_limit_w=0.3
            )]):
                # Call _poll_loop once
                asyncio.run(monitor._poll_loop())
    
    # Verify that the buffer was appended to
    mock_buffer.append.assert_called_once()


def test_gpu_monitor_multiple_devices(mock_config, mock_buffer, mock_nvml):
    """Test that GpuMonitor correctly handles multiple GPUs and their unique handles."""
    # Mock the NVML initialization and device handle retrieval for multiple devices
    mock_nvml.nvmlInit.return_value = None
    mock_nvml.nvmlDeviceGetHandleByIndex.side_effect = ["mock_handle_0", "mock_handle_1"]
    
    monitor = GpuMonitor(mock_config, mock_buffer)
    
    # Verify device handles were populated
    assert monitor.device_handles == ["mock_handle_0", "mock_handle_1"]
    
    # Verify NVML was called for each device
    mock_nvml.nvmlDeviceGetHandleByIndex.assert_has_calls([call(0), call(1)])
