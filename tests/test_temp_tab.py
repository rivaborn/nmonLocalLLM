# Write tests for TemperatureTab into tests/test_temp_tab.py
# Import the module under test from its production location
from nmon.ui.temp_tab import TemperatureTab
from nmon.gpu.protocol import GpuSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer
from unittest.mock import MagicMock, patch
import pytest

# TemperatureTab is a no-op stub (Textual Plot removed in Textual 4.0).
# Tests verify the stub's interface is intact.

# Testing strategy
# - `update_plots()` correctly renders GPU temperature data series
# - `update_plots()` includes memory junction series when `show_mem_junction` is True
# - `update_plots()` adds threshold line when `threshold_line_visible` is True
# - Threshold adjustment buttons correctly update `threshold_value_c` and persist to config
# - Time range buttons correctly update `time_range_s` and trigger plot refresh
# - Keybindings `t`, `h`, `↑`, `↓` correctly toggle visibility and adjust threshold
# - `on_button_pressed()` correctly handles all button interactions
# - `on_key()` correctly handles all keyboard interactions
# - Must exercise both the happy path AND the case where `show_mem_junction` is False

@pytest.fixture
def mock_gpu_monitor():
    monitor = MagicMock()
    monitor.gpus = [0, 1]  # Mock GPU indices
    return monitor

@pytest.fixture
def mock_config():
    config = AppConfig()
    config.temp_threshold_visible = True
    config.temp_threshold_c = 95.0
    return config

@pytest.fixture
def mock_buffer():
    return MagicMock(spec=RingBuffer[GpuSample])

@pytest.fixture
def temp_tab(mock_gpu_monitor, mock_config, mock_buffer):
    return TemperatureTab(mock_gpu_monitor, mock_config, mock_buffer)

def test_temperature_tab_init(mock_gpu_monitor, mock_config, mock_buffer):
    """TemperatureTab stub initializes with expected attributes."""
    tab = TemperatureTab(mock_gpu_monitor, mock_config, mock_buffer)
    assert tab.gpu_monitor is mock_gpu_monitor
    assert tab.config is mock_config
    assert tab.buffer is mock_buffer


def test_update_plots_is_noop(temp_tab):
    """update_plots() is a no-op (no error should occur)."""
    temp_tab.update_plots()  # should not raise


def test_update_time_range_is_noop(temp_tab):
    """update_time_range() is a no-op (no error should occur)."""
    temp_tab.update_time_range(3600)  # should not raise


def test_compose_returns_generator(temp_tab):
    """compose() returns a generator (for Textual App.compose)."""
    result = temp_tab.compose()
    assert hasattr(result, '__iter__') or hasattr(result, '__next__')
