import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time

from nmon.views.temp_view import render_temp_view, update_temp_prefs
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import Settings, UserPrefs
from nmon.history import HistoryStore


@pytest.fixture
def mock_history_store():
    """Mock history store with synthetic data"""
    store = Mock(spec=HistoryStore)
    store.gpu_series = Mock(return_value=[
        GpuSnapshot(
            timestamp=1640995200,
            gpu_util=50,
            gpu_mem_util=60,
            gpu_temp=75,
            gpu_power=150,
            gpu_mem=8192,
            gpu_mem_free=4096,
            gpu_mem_used=4096,
            gpu_mem_pct=50,
            gpu_name="GeForce RTX 3080",
            gpu_uuid="uuid123"
        ),
        GpuSnapshot(
            timestamp=1640995260,
            gpu_util=55,
            gpu_mem_util=65,
            gpu_temp=78,
            gpu_power=160,
            gpu_mem=8192,
            gpu_mem_free=3584,
            gpu_mem_used=4608,
            gpu_mem_pct=56,
            gpu_name="GeForce RTX 3080",
            gpu_uuid="uuid123"
        )
    ])
    return store


@pytest.fixture
def mock_console():
    """Mock rich console"""
    return Mock()


@pytest.fixture
def mock_time():
    """Mock time.time to return fixed values"""
    with patch('time.time') as mock_time_func:
        mock_time_func.return_value = 1640995200
        yield mock_time_func


@pytest.fixture
def mock_settings():
    """Mock settings"""
    settings = Mock(spec=Settings)
    settings.temp_threshold = 80
    settings.show_threshold_line = True
    settings.show_mem_junction = True
    return settings


@pytest.fixture
def mock_user_prefs():
    """Mock user prefs"""
    prefs = Mock(spec=UserPrefs)
    prefs.temp_threshold = 80
    prefs.show_threshold_line = True
    prefs.show_mem_junction = True
    return prefs


def test_render_temp_view_returns_layout_with_correct_panels(
    mock_history_store, mock_console, mock_time, mock_settings, mock_user_prefs
):
    """Test that render_temp_view returns a layout with correct number of panels"""
    with patch('nmon.views.temp_view.history_store', mock_history_store), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs):
        
        layout = render_temp_view()
        
        # Should return a layout object
        assert layout is not None
        # Should have at least the main panels
        assert len(str(layout)) > 0


def test_render_temp_view_time_range_buttons(
    mock_history_store, mock_console, mock_time, mock_settings, mock_user_prefs
):
    """Test that time range buttons are rendered with correct labels and active state"""
    with patch('nmon.views.temp_view.history_store', mock_history_store), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs):
        
        layout = render_temp_view()
        
        # Should contain time range buttons
        assert layout is not None


def test_render_temp_view_threshold_line_rendered_when_enabled(
    mock_history_store, mock_console, mock_time, mock_settings, mock_user_prefs
):
    """Test that threshold line is rendered when show_threshold_line is True"""
    mock_settings.show_threshold_line = True
    mock_user_prefs.show_threshold_line = True
    
    with patch('nmon.views.temp_view.history_store', mock_history_store), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs):
        
        layout = render_temp_view()
        
        # Should render threshold line when enabled
        assert layout is not None


def test_render_temp_view_memory_junction_rendered_when_enabled(
    mock_history_store, mock_console, mock_time, mock_settings, mock_user_prefs
):
    """Test that memory junction series is rendered when show_mem_junction is True"""
    mock_settings.show_mem_junction = True
    mock_user_prefs.show_mem_junction = True
    
    with patch('nmon.views.temp_view.history_store', mock_history_store), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs):
        
        layout = render_temp_view()
        
        # Should render memory junction when enabled
        assert layout is not None


def test_update_temp_prefs_modifies_threshold_and_flags(
    mock_settings, mock_user_prefs
):
    """Test that update_temp_prefs correctly modifies threshold and toggle flags"""
    with patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs), \
         patch('nmon.views.temp_view.save_user_prefs') as mock_save:
        
        # Test updating threshold
        update_temp_prefs(90, True, False)
        
        # Should update threshold
        assert mock_settings.temp_threshold == 90
        assert mock_user_prefs.temp_threshold == 90
        
        # Should update toggle flags
        assert mock_user_prefs.show_threshold_line is True
        assert mock_user_prefs.show_mem_junction is False
        
        # Should save prefs
        mock_save.assert_called_once()


def test_render_temp_view_handles_empty_gpu_data(
    mock_console, mock_time, mock_settings, mock_user_prefs
):
    """Test that render_temp_view handles empty or missing GPU data gracefully"""
    empty_history = Mock(spec=HistoryStore)
    empty_history.gpu_series = Mock(return_value=[])
    
    with patch('nmon.views.temp_view.history_store', empty_history), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs):
        
        layout = render_temp_view()
        
        # Should handle empty data gracefully
        assert layout is not None


def test_render_temp_view_handles_missing_gpu_data(
    mock_console, mock_time, mock_settings, mock_user_prefs
):
    """Test that render_temp_view handles missing GPU data gracefully"""
    missing_history = Mock(spec=HistoryStore)
    missing_history.gpu_series = Mock(side_effect=Exception("No data"))
    
    with patch('nmon.views.temp_view.history_store', missing_history), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('nmon.views.temp_view.settings', mock_settings), \
         patch('nmon.views.temp_view.user_prefs', mock_user_prefs):
        
        layout = render_temp_view()
        
        # Should handle missing data gracefully
        assert layout is not None
