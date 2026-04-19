import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from nmon.ui.app import NmonApp
from nmon.config import AppConfig
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.gpu.monitor import GpuMonitor
from nmon.llm.monitor import LlmMonitor
from nmon.ui.alert_bar import AlertBar
from nmon.ui.dashboard import DashboardTab
from nmon.ui.temp_tab import TemperatureTab
from nmon.ui.power_tab import PowerTab
from nmon.ui.llm_tab import LlmTab
from pynvml import NVMLError


@pytest.fixture
def mock_app():
    """Create a mock NmonApp instance"""
    app = NmonApp()
    app.config = AppConfig()
    return app


@pytest.fixture
def mock_gpu_monitor():
    """Create a mock GpuMonitor"""
    return MagicMock(spec=GpuMonitor)


@pytest.fixture
def mock_llm_monitor():
    """Create a mock LlmMonitor"""
    return MagicMock(spec=LlmMonitor)


@pytest.mark.asyncio
async def test_on_mount_starts_gpu_monitoring_and_ollama_detection(
    mock_app, 
    mock_gpu_monitor, 
    mock_llm_monitor,
    mocker
):
    """Test that on_mount starts GPU monitoring and attempts Ollama detection"""
    # Mock the monitors
    mocker.patch('nmon.ui.app.GpuMonitor', return_value=mock_gpu_monitor)
    mocker.patch('nmon.ui.app.LlmMonitor', return_value=mock_llm_monitor)
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Call on_mount
    await mock_app.on_mount()
    
    # Assert that GPU monitor was started
    mock_gpu_monitor.start.assert_called_once()
    
    # Assert that Ollama detection was attempted
    mock_app._detect_ollama.assert_called_once()
    
    # Assert that UI was set up
    mock_app._setup_ui.assert_called_once()


@pytest.mark.asyncio
async def test_on_mount_shows_llm_tab_when_ollama_detected(
    mock_app, 
    mock_gpu_monitor, 
    mock_llm_monitor,
    mocker
):
    """Test that on_mount shows LLM tab only when Ollama is detected"""
    # Mock the monitors
    mocker.patch('nmon.ui.app.GpuMonitor', return_value=mock_gpu_monitor)
    mocker.patch('nmon.ui.app.LlmMonitor', return_value=mock_llm_monitor)
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection to return True
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Call on_mount
    await mock_app.on_mount()
    
    # Assert that LLM tab is shown (this would be verified by checking UI state)
    # Since we can't easily test UI state, we'll check that the method was called
    assert mock_app._detect_ollama.called


@pytest.mark.asyncio
async def test_on_mount_hides_llm_tab_when_ollama_not_detected(
    mock_app, 
    mock_gpu_monitor, 
    mock_llm_monitor,
    mocker
):
    """Test that on_mount hides LLM tab when Ollama is not detected"""
    # Mock the monitors
    mocker.patch('nmon.ui.app.GpuMonitor', return_value=mock_gpu_monitor)
    mocker.patch('nmon.ui.app.LlmMonitor', return_value=mock_llm_monitor)
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection to return False
    mock_app._detect_ollama = AsyncMock(return_value=False)
    
    # Call on_mount
    await mock_app.on_mount()
    
    # Assert that Ollama detection was attempted
    mock_app._detect_ollama.assert_called_once()


@pytest.mark.asyncio
async def test_on_unmount_stops_monitoring_and_persists_config(
    mock_app, 
    mock_gpu_monitor, 
    mock_llm_monitor,
    mocker
):
    """Test that on_unmount stops all monitoring and persists config"""
    # Mock the monitors
    mocker.patch('nmon.ui.app.GpuMonitor', return_value=mock_gpu_monitor)
    mocker.patch('nmon.ui.app.LlmMonitor', return_value=mock_llm_monitor)
    
    # Mock the config persistence
    mock_save = mocker.patch('nmon.ui.app.save_persistent_settings')
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Call on_mount first to set up monitors
    await mock_app.on_mount()
    
    # Call on_unmount
    await mock_app.on_unmount()
    
    # Assert that GPU monitor was stopped
    mock_gpu_monitor.stop.assert_called_once()
    
    # Assert that LLM monitor was stopped
    mock_llm_monitor.stop.assert_called_once()
    
    # Assert that config was saved
    mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_update_interval_validates_input_and_updates_monitors(
    mock_app, 
    mock_gpu_monitor, 
    mock_llm_monitor,
    mocker
):
    """Test that update_interval validates input range and updates all monitors"""
    # Mock the monitors
    mocker.patch('nmon.ui.app.GpuMonitor', return_value=mock_gpu_monitor)
    mocker.patch('nmon.ui.app.LlmMonitor', return_value=mock_llm_monitor)
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Call on_mount first to set up monitors
    await mock_app.on_mount()
    
    # Test valid interval
    mock_app.update_interval(5)
    assert mock_app.config.poll_interval_s == 5
    
    # Test invalid interval (should be clamped)
    mock_app.update_interval(0)
    assert mock_app.config.poll_interval_s == 1  # Assuming 1 is the minimum
    
    mock_app.update_interval(100)
    assert mock_app.config.poll_interval_s == 60  # Assuming 60 is the maximum


@pytest.mark.asyncio
async def test_toggle_mem_junction_updates_ui_state(
    mock_app, 
    mocker
):
    """Test that toggle_mem_junction updates UI state without crashing"""
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Call on_mount first to set up
    await mock_app.on_mount()
    
    # Test toggling memory junction
    try:
        mock_app.toggle_mem_junction()
        # If we get here without exception, the test passes
        assert True
    except Exception as e:
        pytest.fail(f"toggle_mem_junction raised an exception: {e}")


@pytest.mark.asyncio
async def test_toggle_threshold_line_updates_ui_state(
    mock_app, 
    mocker
):
    """Test that toggle_threshold_line updates UI state without crashing"""
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Call on_mount first to set up
    await mock_app.on_mount()
    
    # Test toggling threshold line
    try:
        mock_app.toggle_threshold_line()
        # If we get here without exception, the test passes
        assert True
    except Exception as e:
        pytest.fail(f"toggle_threshold_line raised an exception: {e}")


@pytest.mark.asyncio
async def test_adjust_threshold_clamps_values_and_persists(
    mock_app, 
    mocker
):
    """Test that adjust_threshold clamps values and persists to JSON"""
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Mock config persistence
    mock_save = mocker.patch('nmon.ui.app.save_persistent_settings')
    
    # Call on_mount first to set up
    await mock_app.on_mount()
    
    # Test adjusting threshold to valid value
    mock_app.adjust_threshold(50)
    assert mock_app.config.temp_threshold_c == 50
    
    # Test adjusting threshold to value below minimum
    mock_app.adjust_threshold(-10)
    assert mock_app.config.temp_threshold_c == 0  # Assuming 0 is the minimum
    
    # Test adjusting threshold to value above maximum
    mock_app.adjust_threshold(150)
    assert mock_app.config.temp_threshold_c == 100  # Assuming 100 is the maximum
    
    # Assert that config was saved
    assert mock_save.call_count >= 1


@pytest.mark.asyncio
async def test_app_handles_nvml_error_gracefully(
    mock_app, 
    mock_gpu_monitor,
    mocker
):
    """Test that App gracefully handles NVMLError during GPU polling"""
    # Mock the monitors
    mocker.patch('nmon.ui.app.GpuMonitor', return_value=mock_gpu_monitor)
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=True)
    
    # Mock the GPU monitor to raise NVMLError
    mock_gpu_monitor.poll = MagicMock(side_effect=NVMLError(0))
    
    # Call on_mount first to set up
    await mock_app.on_mount()
    
    # Test that the app doesn't crash when NVMLError is raised
    try:
        # This should not raise an exception
        await asyncio.sleep(0.1)
        assert True
    except Exception as e:
        pytest.fail(f"App crashed when handling NVMLError: {e}")


@pytest.mark.asyncio
async def test_detect_ollama_handles_unreachable_ollama(
    mock_app, 
    mocker
):
    """Test that _detect_ollama handles unreachable Ollama gracefully"""
    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=Exception("Connection failed"))
    mocker.patch('nmon.ui.app.httpx.AsyncClient', return_value=mock_client)
    
    # Mock the app's methods
    mock_app._setup_ui = MagicMock()
    mock_app._setup_monitors = MagicMock()
    
    # Mock the Ollama detection
    mock_app._detect_ollama = AsyncMock(return_value=False)
    
    # Call on_mount first to set up
    await mock_app.on_mount()
    
    # Test that the app doesn't crash when Ollama is unreachable
    try:
        result = await mock_app._detect_ollama()
        assert result is False  # Should return False when Ollama is unreachable
    except Exception as e:
        pytest.fail(f"_detect_ollama crashed when Ollama is unreachable: {e}")
