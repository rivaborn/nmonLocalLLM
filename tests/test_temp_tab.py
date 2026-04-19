# Write tests for TemperatureTab into tests/test_temp_tab.py
# Import the module under test from its production location
from nmon.ui.temp_tab import TemperatureTab
from nmon.gpu.protocol import GpuSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import asyncio
from textual.widgets import Plot, Button
from textual.containers import Container
from textual.widgets import Label

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

@pytest.mark.asyncio
async def test_update_plots_happy_path(temp_tab, mock_buffer):
    # Mock the buffer.since method to return sample data
    sample1 = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=80.0,
        temperature_mem_junction=70.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=50.0,
        power_limit_w=150.0
    )
    sample2 = GpuSample(
        timestamp=2.0,
        gpu_index=1,
        temperature_gpu=85.0,
        temperature_mem_junction=75.0,
        memory_used_mib=1200.0,
        memory_total_mib=2000.0,
        power_draw_w=60.0,
        power_limit_w=150.0
    )
    mock_buffer.since.return_value = [sample1, sample2]
    
    # Call update_plots
    temp_tab.update_plots()
    
    # Verify that update_plots was called
    assert len(temp_tab.gpu_plots) == 2  # Should have 2 plots for 2 GPUs

@pytest.mark.asyncio
async def test_update_plots_no_mem_junction(temp_tab, mock_buffer):
    # Set show_mem_junction to False
    temp_tab.show_mem_junction = False
    
    # Mock the buffer.since method to return sample data
    sample1 = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=80.0,
        temperature_mem_junction=70.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=50.0,
        power_limit_w=150.0
    )
    mock_buffer.since.return_value = [sample1]
    
    # Call update_plots
    temp_tab.update_plots()
    
    # Verify that update_plots was called
    assert len(temp_tab.gpu_plots) == 1  # Should have 1 plot for 1 GPU

def test_threshold_adjustment_buttons(temp_tab, mock_config):
    # Mock config persistence
    with patch('nmon.ui.temp_tab.config') as mock_config_module:
        mock_config_module.save_persistent_settings = MagicMock()
        
        # Simulate pressing threshold_adjust_up button
        temp_tab.threshold_adjust_up = MagicMock()
        temp_tab.threshold_adjust_up.id = "threshold_adjust_up"
        temp_tab.on_button_pressed(type('obj', (object,), {'button': temp_tab.threshold_adjust_up})())
        
        # Verify threshold value was updated
        assert temp_tab.threshold_value_c == 95.5
        
        # Verify config was saved
        mock_config_module.save_persistent_settings.assert_called_once()

def test_time_range_buttons(temp_tab):
    # Mock time range button
    button = MagicMock()
    button.id = "time_range_3600"
    
    # Simulate pressing time range button
    temp_tab.on_button_pressed(type('obj', (object,), {'button': button})())
    
    # Verify time range was updated
    assert temp_tab.time_range_s == 3600

def test_keybindings(temp_tab, mock_config):
    # Mock config persistence
    with patch('nmon.ui.temp_tab.config') as mock_config_module:
        mock_config_module.save_persistent_settings = MagicMock()
        
        # Simulate pressing 'h' key
        temp_tab.on_key(type('obj', (object,), {'key': 'h'})())
        
        # Verify threshold visibility was toggled
        assert temp_tab.threshold_line_visible == False
        
        # Verify config was saved
        mock_config_module.save_persistent_settings.assert_called_once()

def test_button_pressed_all_cases(temp_tab):
    # Test all button interactions
    temp_tab.threshold_toggle_button = MagicMock()
    temp_tab.threshold_toggle_button.id = "threshold_toggle_button"
    
    temp_tab.mem_junction_toggle_button = MagicMock()
    temp_tab.mem_junction_toggle_button.id = "mem_junction_toggle_button"
    
    temp_tab.threshold_adjust_up = MagicMock()
    temp_tab.threshold_adjust_up.id = "threshold_adjust_up"
    
    temp_tab.threshold_adjust_down = MagicMock()
    temp_tab.threshold_adjust_down.id = "threshold_adjust_down"
    
    # Test threshold toggle
    temp_tab.on_button_pressed(type('obj', (object,), {'button': temp_tab.threshold_toggle_button})())
    
    # Test mem junction toggle
    temp_tab.on_button_pressed(type('obj', (object,), {'button': temp_tab.mem_junction_toggle_button})())
    
    # Test threshold adjust up
    temp_tab.on_button_pressed(type('obj', (object,), {'button': temp_tab.threshold_adjust_up})())
    
    # Test threshold adjust down
    temp_tab.on_button_pressed(type('obj', (object,), {'button': temp_tab.threshold_adjust_down})())
    
    # Verify all buttons were processed
    assert temp_tab.threshold_line_visible == False
    assert temp_tab.show_mem_junction == False
    assert temp_tab.threshold_value_c == 95.5

def test_keybindings_all_cases(temp_tab):
    # Test all key interactions
    temp_tab.on_key(type('obj', (object,), {'key': 't'})())
    temp_tab.on_key(type('obj', (object,), {'key': 'h'})())
    temp_tab.on_key(type('obj', (object,), {'key': 'up'})())
    temp_tab.on_key(type('obj', (object,), {'key': 'down'})())
    
    # Verify all keys were processed
    assert temp_tab.show_mem_junction == False
    assert temp_tab.threshold_line_visible == False
    assert temp_tab.threshold_value_c == 96.0
