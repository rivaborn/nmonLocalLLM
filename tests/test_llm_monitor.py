# Write tests for LlmMonitor in tests/test_llm_monitor.py
#
# Import the module under test from its production location
from nmon.llm.monitor import LlmMonitor
from nmon.llm.protocol import LlmSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from pytest_mock import MockerFixture

# Test file: tests/test_llm_monitor.py
# Module under test: src/nmon/llm/monitor.py
# Class: LlmMonitor
# Constants: TOTAL_LAYERS_ESTIMATE = 32

# Testing strategy:
# - External dependencies to mock: httpx.AsyncClient
# - Behaviors to assert:
#   - `_parse_response()` correctly maps all API fields to LlmSample
#   - `detect()` returns False on httpx.ConnectError
#   - `detect()` returns False on HTTP 5xx response
#   - `gpu_utilization_pct` is clamped to [0.0, 100.0]
#   - `_poll()` returns None on any HTTP exception
#   - `start()` and `stop()` manage task lifecycle correctly
# - pytest fixtures and plugins: pytest-asyncio, pytest-mock
# - Coverage goals: must exercise both happy path and error branches of `_poll()` and `detect()`

# Test cases:
# 1. Test `_parse_response()` with a full Ollama API response mapping all fields to `LlmSample` correctly.
# 2. Test `_parse_response()` with edge case values like zero size and verify clamping of utilization percentages.
# 3. Test `detect()` returns `False` when `httpx.ConnectError` is raised.
# 4. Test `detect()` returns `False` when HTTP 5xx response is received.
# 5. Test `detect()` returns `False` when `httpx.TimeoutException` is raised.
# 6. Test `detect()` returns `False` when `httpx.HTTPError` is raised.
# 7. Test `_poll()` returns `None` when `httpx.ConnectError` is raised.
# 8. Test `_poll()` returns `None` when HTTP 5xx response is received.
# 9. Test `gpu_utilization_pct` is clamped to `[0.0, 100.0]` in `LlmSample`.
# 10. Test `cpu_utilization_pct` is clamped to `[0.0, 100.0]` in `LlmSample`.

@pytest.mark.asyncio
async def test_detect_returns_false_on_connect_error(mocker: MockerFixture):
    """Test that detect() returns False when httpx.ConnectError is raised."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to raise ConnectError
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("Connection failed")
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor.detect()
    
    # Assert
    assert result is False
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/tags", timeout=3.0)

@pytest.mark.asyncio
async def test_detect_returns_false_on_http_5xx(mocker: MockerFixture):
    """Test that detect() returns False when a non-2xx HTTP status is returned."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to return a 500 status
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_response)
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor.detect()
    
    # Assert
    assert result is False
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/tags", timeout=3.0)

@pytest.mark.asyncio
async def test_detect_returns_false_on_timeout(mocker: MockerFixture):
    """Test that detect() returns False when httpx.TimeoutException is raised."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to raise TimeoutException
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Timeout")
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor.detect()
    
    # Assert
    assert result is False
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/tags", timeout=3.0)

@pytest.mark.asyncio
async def test_detect_returns_false_on_http_error(mocker: MockerFixture):
    """Test that detect() returns False when httpx.HTTPError is raised."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to raise HTTPError
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.HTTPError("HTTP Error")
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor.detect()
    
    # Assert
    assert result is False
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/tags", timeout=3.0)

@pytest.mark.asyncio
async def test_detect_returns_true_on_success(mocker: MockerFixture):
    """Test that detect() returns True when HTTP 200 is returned."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to return a 200 status
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor.detect()
    
    # Assert
    assert result is True
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/tags", timeout=3.0)

@pytest.mark.asyncio
async def test_poll_returns_none_on_connect_error(mocker: MockerFixture):
    """Test that _poll() returns None when httpx.ConnectError is raised."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to raise ConnectError
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("Connection failed")
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor._poll()
    
    # Assert
    assert result is None
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/ps", timeout=None)

@pytest.mark.asyncio
async def test_poll_returns_none_on_http_5xx(mocker: MockerFixture):
    """Test that _poll() returns None when a non-2xx HTTP status is returned."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock httpx.AsyncClient to return a 500 status
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_response)
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    
    # Act
    result = await monitor._poll()
    
    # Assert
    assert result is None
    mock_client.get.assert_called_once_with(f"{config.ollama_url}/api/ps", timeout=None)

@pytest.mark.asyncio
async def test_parse_response_maps_fields_correctly():
    """Test that _parse_response() correctly maps all API fields to LlmSample."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock data from Ollama /api/ps response
    response_data = {
        "models": [
            {
                "name": "llama3:8b",
                "size": 4200000000,  # 4.2 GB
                "size_vram": 3200000000,  # 3.2 GB
                "parameter_size": 8000000000,  # 8B parameters
            }
        ]
    }
    
    # Act
    result = monitor._parse_response(response_data)
    
    # Assert
    assert isinstance(result, LlmSample)
    assert result.model_name == "llama3:8b"
    assert result.model_size_bytes == 4200000000
    assert result.gpu_layers_offloaded == 25  # 32 * (3.2 / 4.2) ≈ 24.57 → 25
    assert result.gpu_utilization_pct == 77.5  # (25 / 32) * 100
    assert result.cpu_utilization_pct == 22.5  # 100 - 77.5
    assert result.total_layers == 32

@pytest.mark.asyncio
async def test_parse_response_handles_zero_size():
    """Test that _parse_response() handles zero size safely."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock data with zero size
    response_data = {
        "models": [
            {
                "name": "test:model",
                "size": 0,
                "size_vram": 0,
                "parameter_size": 0,
            }
        ]
    }
    
    # Act
    result = monitor._parse_response(response_data)
    
    # Assert
    assert isinstance(result, LlmSample)
    assert result.model_name == "test:model"
    assert result.model_size_bytes == 0
    assert result.gpu_layers_offloaded == 0
    assert result.gpu_utilization_pct == 0.0
    assert result.cpu_utilization_pct == 100.0  # 100 - 0

@pytest.mark.asyncio
async def test_parse_response_clamps_utilization():
    """Test that _parse_response() clamps utilization percentages to [0.0, 100.0]."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Mock data that would result in > 100% utilization
    response_data = {
        "models": [
            {
                "name": "test:model",
                "size": 1000000000,  # 1 GB
                "size_vram": 1500000000,  # 1.5 GB (more than size)
                "parameter_size": 1000000000,
            }
        ]
    }
    
    # Act
    result = monitor._parse_response(response_data)
    
    # Assert
    assert isinstance(result, LlmSample)
    assert result.gpu_utilization_pct == 100.0  # Clamped
    assert result.cpu_utilization_pct == 0.0  # 100 - 100

def test_start_and_stop_manage_task_lifecycle():
    """Test that start() and stop() manage task lifecycle correctly."""
    # Arrange
    config = AppConfig()
    buffer = RingBuffer(config)
    monitor = LlmMonitor(config, buffer)
    
    # Act & Assert
    assert monitor._running is False
    assert monitor._task is None
    
    # Start the monitor
    monitor.start()
    assert monitor._running is True
    assert monitor._task is not None
    
    # Stop the monitor
    monitor.stop()
    assert monitor._running is False
    assert monitor._task is None
