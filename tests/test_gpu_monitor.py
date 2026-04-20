import pytest
from unittest.mock import patch, MagicMock
from nmon.gpu_monitor import poll, GpuSnapshot

def test_poll_returns_empty_list_when_pynvml_init_fails(monkeypatch):
    # Mock pynvml.init to raise an exception
    monkeypatch.setattr("pynvml.nvmlInit", side_effect=Exception("Init failed"))
    # Call poll and assert it returns empty list
    result = poll()
    assert result == []

def test_poll_skips_gpu_and_logs_warning_when_handle_retrieval_fails(monkeypatch, caplog):
    # Mock pynvml functions
    mock_nvmlDeviceGetHandleByIndex = MagicMock(side_effect=Exception("Handle failed"))
    mock_nvmlDeviceGetCount = MagicMock(return_value=2)
    monkeypatch.setattr("pynvml.nvmlDeviceGetHandleByIndex", mock_nvmlDeviceGetHandleByIndex)
    monkeypatch.setattr("pynvml.nvmlDeviceGetCount", mock_nvmlDeviceGetCount)
    monkeypatch.setattr("pynvml.nvmlInit", MagicMock())
    # Mock other required functions to return dummy data for valid GPU
    mock_get_temperature = MagicMock(return_value=60.0)
    mock_get_memory_info = MagicMock(return_value=MagicMock(free=1000000, total=2000000))
    mock_get_power_usage = MagicMock(return_value=100.0)
    mock_get_power_limit = MagicMock(return_value=250.0)
    monkeypatch.setattr("pynvml.nvmlDeviceGetTemperature", mock_get_temperature)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryInfo", mock_get_memory_info)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerUsage", mock_get_power_usage)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerLimit", mock_get_power_limit)
    # Call poll and assert it skips the first GPU and logs warning
    result = poll()
    # Should have one GpuSnapshot for the valid GPU
    assert len(result) == 1
    assert result[0].gpu_index == 1  # Second GPU (index 1) should be processed
    # Check that warning was logged for first GPU
    assert "Warning" in caplog.text
    assert "Handle failed" in caplog.text

def test_poll_handles_missing_memory_junction_temp(monkeypatch, caplog):
    # Mock pynvml functions
    mock_nvmlDeviceGetHandleByIndex = MagicMock(return_value=MagicMock())
    mock_nvmlDeviceGetCount = MagicMock(return_value=1)
    monkeypatch.setattr("pynvml.nvmlDeviceGetHandleByIndex", mock_nvmlDeviceGetHandleByIndex)
    monkeypatch.setattr("pynvml.nvmlDeviceGetCount", mock_nvmlDeviceGetCount)
    monkeypatch.setattr("pynvml.nvmlInit", MagicMock())
    # Mock functions to return dummy data
    mock_get_temperature = MagicMock(return_value=60.0)
    mock_get_memory_info = MagicMock(return_value=MagicMock(free=1000000, total=2000000))
    mock_get_power_usage = MagicMock(return_value=100.0)
    mock_get_power_limit = MagicMock(return_value=250.0)
    # Mock memory junction temp to raise exception (simulating unsupported)
    mock_get_memory_bus_temperature = MagicMock(side_effect=Exception("Not supported"))
    monkeypatch.setattr("pynvml.nvmlDeviceGetTemperature", mock_get_temperature)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryInfo", mock_get_memory_info)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerUsage", mock_get_power_usage)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerLimit", mock_get_power_limit)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryBusTemperature", mock_get_memory_bus_temperature)
    # Call poll and assert it returns valid GpuSnapshot with None for mem_junction_temp_c
    result = poll()
    assert len(result) == 1
    snapshot = result[0]
    assert snapshot.gpu_index == 0
    assert snapshot.temperature_c == 60.0
    assert snapshot.mem_junction_temp_c is None
    assert snapshot.memory_used_mb == 1000000
    assert snapshot.memory_total_mb == 2000000
    assert snapshot.power_draw_w == 100.0
    assert snapshot.power_limit_w == 250.0

def test_poll_returns_valid_gpu_snapshot_data(monkeypatch):
    # Mock pynvml functions
    mock_nvmlDeviceGetHandleByIndex = MagicMock(return_value=MagicMock())
    mock_nvmlDeviceGetCount = MagicMock(return_value=1)
    monkeypatch.setattr("pynvml.nvmlDeviceGetHandleByIndex", mock_nvmlDeviceGetHandleByIndex)
    monkeypatch.setattr("pynvml.nvmlDeviceGetCount", mock_nvmlDeviceGetCount)
    monkeypatch.setattr("pynvml.nvmlInit", MagicMock())
    # Mock functions to return dummy data
    mock_get_temperature = MagicMock(return_value=60.0)
    mock_get_memory_bus_temperature = MagicMock(return_value=50.0)
    mock_get_memory_info = MagicMock(return_value=MagicMock(free=1000000, total=2000000))
    mock_get_power_usage = MagicMock(return_value=100.0)
    mock_get_power_limit = MagicMock(return_value=250.0)
    monkeypatch.setattr("pynvml.nvmlDeviceGetTemperature", mock_get_temperature)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryBusTemperature", mock_get_memory_bus_temperature)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryInfo", mock_get_memory_info)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerUsage", mock_get_power_usage)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerLimit", mock_get_power_limit)
    # Call poll and assert it returns valid GpuSnapshot
    result = poll()
    assert len(result) == 1
    snapshot = result[0]
    assert isinstance(snapshot, GpuSnapshot)
    assert snapshot.gpu_index == 0
    assert snapshot.temperature_c == 60.0
    assert snapshot.mem_junction_temp_c == 50.0
    assert snapshot.memory_used_mb == 1000000
    assert snapshot.memory_total_mb == 2000000
    assert snapshot.power_draw_w == 100.0
    assert snapshot.power_limit_w == 250.0

def test_poll_raises_no_exceptions_when_gpu_metrics_are_accessible(monkeypatch):
    # Mock pynvml functions
    mock_nvmlDeviceGetHandleByIndex = MagicMock(return_value=MagicMock())
    mock_nvmlDeviceGetCount = MagicMock(return_value=1)
    monkeypatch.setattr("pynvml.nvmlDeviceGetHandleByIndex", mock_nvmlDeviceGetHandleByIndex)
    monkeypatch.setattr("pynvml.nvmlDeviceGetCount", mock_nvmlDeviceGetCount)
    monkeypatch.setattr("pynvml.nvmlInit", MagicMock())
    # Mock functions to return dummy data
    mock_get_temperature = MagicMock(return_value=60.0)
    mock_get_memory_bus_temperature = MagicMock(return_value=50.0)
    mock_get_memory_info = MagicMock(return_value=MagicMock(free=1000000, total=2000000))
    mock_get_power_usage = MagicMock(return_value=100.0)
    mock_get_power_limit = MagicMock(return_value=250.0)
    monkeypatch.setattr("pynvml.nvmlDeviceGetTemperature", mock_get_temperature)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryBusTemperature", mock_get_memory_bus_temperature)
    monkeypatch.setattr("pynvml.nvmlDeviceGetMemoryInfo", mock_get_memory_info)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerUsage", mock_get_power_usage)
    monkeypatch.setattr("pynvml.nvmlDeviceGetPowerLimit", mock_get_power_limit)
    # Call poll and assert it does not raise any exceptions
    try:
        result = poll()
        assert len(result) == 1
    except Exception as e:
        pytest.fail(f"poll() raised an exception unexpectedly: {e}")
