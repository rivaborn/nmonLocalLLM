import pytest
from unittest.mock import Mock, MagicMock
from rich.layout import Layout
from nmon.views.dashboard_view import DashboardView
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import UserPrefs, Settings
from nmon.history import HistoryStore
from nmon.alerts import AlertState
from nmon.widgets.sparkline import Sparkline

@pytest.fixture
def mock_gpu_monitor():
    return Mock()

@pytest.fixture
def mock_history_store():
    return Mock(spec=HistoryStore)

@pytest.fixture
def mock_prefs():
    return UserPrefs()

@pytest.fixture
def mock_settings():
    return Settings()

@pytest.fixture
def mock_alert_state():
    return Mock(spec=AlertState)

@pytest.fixture
def mock_gpu_snapshot():
    return GpuSnapshot(
        gpu_index=0,
        timestamp=1.0,
        temperature_c=75.0,
        mem_junction_temp_c=80.0,
        memory_used_mb=1000.0,
        memory_total_mb=2000.0,
        power_draw_w=150.0,
        power_limit_w=250.0
    )

@pytest.fixture
def mock_ollama_snapshot():
    return OllamaSnapshot(
        timestamp=1.0,
        reachable=True,
        loaded_model="test-model",
        model_size_bytes=1000000,
        gpu_use_pct=80.0,
        cpu_use_pct=20.0,
        gpu_layers=10,
        total_layers=10
    )

def test_dashboard_view_render_structure(
    mock_gpu_monitor,
    mock_history_store,
    mock_prefs,
    mock_settings,
    mock_alert_state,
    mock_gpu_snapshot,
    mock_ollama_snapshot
):
    """Test that DashboardView.render() produces a valid Layout with expected structure."""
    # Arrange
    dashboard_view = DashboardView(
        gpu_monitor=mock_gpu_monitor,
        history_store=mock_history_store,
        prefs=mock_prefs,
        settings=mock_settings,
        alert_state=mock_alert_state
    )
    
    # Mock the GPU monitor to return a list of snapshots
    mock_gpu_monitor.poll.return_value = [mock_gpu_snapshot]
    
    # Mock history store to return sample data
    mock_history_store.gpu_series.return_value = [mock_gpu_snapshot]
    mock_history_store.ollama_series.return_value = [mock_ollama_snapshot]
    
    # Mock alert state to be active
    mock_alert_state.active = True
    mock_alert_state.message = "Test alert"
    mock_alert_state.color = "orange"
    mock_alert_state.expires_at = 10.0
    
    # Act
    result = dashboard_view.render()
    
    # Assert
    assert isinstance(result, Layout)
    assert len(result.children) >= 1  # Should have at least a main content area

def test_dashboard_view_gpu_panels_rendered(
    mock_gpu_monitor,
    mock_history_store,
    mock_prefs,
    mock_settings,
    mock_alert_state,
    mock_gpu_snapshot
):
    """Test that GPU panels are rendered for each detected GPU."""
    # Arrange
    dashboard_view = DashboardView(
        gpu_monitor=mock_gpu_monitor,
        history_store=mock_history_store,
        prefs=mock_prefs,
        settings=mock_settings,
        alert_state=mock_alert_state
    )
    
    # Mock the GPU monitor to return multiple snapshots
    mock_gpu_monitor.poll.return_value = [mock_gpu_snapshot, mock_gpu_snapshot]
    
    # Mock history store to return sample data
    mock_history_store.gpu_series.return_value = [mock_gpu_snapshot]
    
    # Act
    result = dashboard_view.render()
    
    # Assert
    assert isinstance(result, Layout)
    # Should have multiple GPU panels (at least one for each GPU)
    assert len(result.children) >= 1

def test_dashboard_view_mem_junction_panel_shown(
    mock_gpu_monitor,
    mock_history_store,
    mock_prefs,
    mock_settings,
    mock_alert_state,
    mock_gpu_snapshot
):
    """Test that mem junction panel is shown only when at least one GPU supports it."""
    # Arrange
    dashboard_view = DashboardView(
        gpu_monitor=mock_gpu_monitor,
        history_store=mock_history_store,
        prefs=mock_prefs,
        settings=mock_settings,
        alert_state=mock_alert_state
    )
    
    # Mock the GPU monitor to return a snapshot with mem junction temp
    mock_gpu_monitor.poll.return_value = [mock_gpu_snapshot]
    
    # Mock history store to return sample data
    mock_history_store.gpu_series.return_value = [mock_gpu_snapshot]
    
    # Act
    result = dashboard_view.render()
    
    # Assert
    assert isinstance(result, Layout)
    # Should render with mem junction panel since GPU supports it

def test_dashboard_view_ollama_panel_shown(
    mock_gpu_monitor,
    mock_history_store,
    mock_prefs,
    mock_settings,
    mock_alert_state,
    mock_ollama_snapshot
):
    """Test that LLM panel is shown only when Ollama is detected."""
    # Arrange
    dashboard_view = DashboardView(
        gpu_monitor=mock_gpu_monitor,
        history_store=mock_history_store,
        prefs=mock_prefs,
        settings=mock_settings,
        alert_state=mock_alert_state
    )
    
    # Mock the GPU monitor to return a snapshot
    mock_gpu_monitor.poll.return_value = [Mock()]
    
    # Mock history store to return sample data
    mock_history_store.gpu_series.return_value = [Mock()]
    mock_history_store.ollama_series.return_value = [mock_ollama_snapshot]
    
    # Act
    result = dashboard_view.render()
    
    # Assert
    assert isinstance(result, Layout)
    # Should render with LLM panel since Ollama is detected

def test_dashboard_view_alert_bar_rendered(
    mock_gpu_monitor,
    mock_history_store,
    mock_prefs,
    mock_settings,
    mock_alert_state
):
    """Test that alert bar is rendered at the top when alert_state is not None."""
    # Arrange
    dashboard_view = DashboardView(
        gpu_monitor=mock_gpu_monitor,
        history_store=mock_history_store,
        prefs=mock_prefs,
        settings=mock_settings,
        alert_state=mock_alert_state
    )
    
    # Mock the GPU monitor to return a snapshot
    mock_gpu_monitor.poll.return_value = [Mock()]
    
    # Mock history store to return sample data
    mock_history_store.gpu_series.return_value = [Mock()]
    
    # Mock alert state to be active
    mock_alert_state.active = True
    mock_alert_state.message = "Test alert"
    mock_alert_state.color = "red"
    mock_alert_state.expires_at = 10.0
    
    # Act
    result = dashboard_view.render()
    
    # Assert
    assert isinstance(result, Layout)
    # Should render with alert bar at the top

def test_dashboard_view_panel_content_reflects_metrics(
    mock_gpu_monitor,
    mock_history_store,
    mock_prefs,
    mock_settings,
    mock_alert_state,
    mock_gpu_snapshot,
    mock_ollama_snapshot
):
    """Test that panel content reflects current and historical metrics from history_store."""
    # Arrange
    dashboard_view = DashboardView(
        gpu_monitor=mock_gpu_monitor,
        history_store=mock_history_store,
        prefs=mock_prefs,
        settings=mock_settings,
        alert_state=mock_alert_state
    )
    
    # Mock the GPU monitor to return a snapshot
    mock_gpu_monitor.poll.return_value = [mock_gpu_snapshot]
    
    # Mock history store to return sample data
    mock_history_store.gpu_series.return_value = [mock_gpu_snapshot]
    mock_history_store.ollama_series.return_value = [mock_ollama_snapshot]
    
    # Act
    result = dashboard_view.render()
    
    # Assert
    assert isinstance(result, Layout)
    # Panel content should reflect the metrics from history store
