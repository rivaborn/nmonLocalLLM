import pytest
from unittest.mock import Mock, MagicMock
from rich.layout import Layout
from nmon.views.power_view import PowerView
from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import UserPrefs, Settings
from nmon.history import HistoryStore

def test_powerview_render():
    # Test normal rendering with valid GPU data
    mock_history = Mock(spec=HistoryStore)
    mock_prefs = Mock(spec=UserPrefs)
    mock_settings = Mock(spec=Settings)
    mock_gpu_snapshots = [
        GpuSnapshot(
            gpu_index=0,
            timestamp=1.0,
            temperature_c=75.0,
            mem_junction_temp_c=80.0,
            memory_used_mb=1000.0,
            memory_total_mb=2000.0,
            power_draw_w=150.0,
            power_limit_w=250.0
        )
    ]
    mock_ollama_snapshot = Mock(spec=OllamaSnapshot)

    # Create PowerView instance
    power_view = PowerView(
        history_store=mock_history,
        prefs=mock_prefs,
        settings=mock_settings,
        gpu_snapshots=mock_gpu_snapshots,
        ollama_snapshot=mock_ollama_snapshot
    )

    # Mock history data
    mock_history.gpu_series.return_value = [
        GpuSnapshot(
            gpu_index=0,
            timestamp=1.0,
            temperature_c=75.0,
            mem_junction_temp_c=80.0,
            memory_used_mb=1000.0,
            memory_total_mb=2000.0,
            power_draw_w=150.0,
            power_limit_w=250.0
        )
    ]

    # Call render
    layout = power_view.render()

    # Assert layout is returned
    assert isinstance(layout, Layout)

    # Assert that history.gpu_series was called
    mock_history.gpu_series.assert_called()

def test_powerview_render_empty_history():
    # Test rendering with empty history data
    mock_history = Mock(spec=HistoryStore)
    mock_prefs = Mock(spec=UserPrefs)
    mock_settings = Mock(spec=Settings)
    mock_gpu_snapshots = [
        GpuSnapshot(
            gpu_index=0,
            timestamp=1.0,
            temperature_c=75.0,
            mem_junction_temp_c=80.0,
            memory_used_mb=1000.0,
            memory_total_mb=2000.0,
            power_draw_w=150.0,
            power_limit_w=250.0
        )
    ]
    mock_ollama_snapshot = Mock(spec=OllamaSnapshot)

    # Create PowerView instance
    power_view = PowerView(
        history_store=mock_history,
        prefs=mock_prefs,
        settings=mock_settings,
        gpu_snapshots=mock_gpu_snapshots,
        ollama_snapshot=mock_ollama_snapshot
    )

    # Mock empty history data
    mock_history.gpu_series.return_value = []

    # Call render - should not crash
    layout = power_view.render()

    # Assert layout is returned
    assert isinstance(layout, Layout)

def test_powerview_render_missing_power_limit():
    # Test rendering with missing power limit data
    mock_history = Mock(spec=HistoryStore)
    mock_prefs = Mock(spec=UserPrefs)
    mock_settings = Mock(spec=Settings)
    mock_gpu_snapshots = [
        GpuSnapshot(
            gpu_index=0,
            timestamp=1.0,
            temperature_c=75.0,
            mem_junction_temp_c=80.0,
            memory_used_mb=1000.0,
            memory_total_mb=2000.0,
            power_draw_w=150.0,
            power_limit_w=None  # Missing power limit
        )
    ]
    mock_ollama_snapshot = Mock(spec=OllamaSnapshot)

    # Create PowerView instance
    power_view = PowerView(
        history_store=mock_history,
        prefs=mock_prefs,
        settings=mock_settings,
        gpu_snapshots=mock_gpu_snapshots,
        ollama_snapshot=mock_ollama_snapshot
    )

    # Mock history data
    mock_history.gpu_series.return_value = [
        GpuSnapshot(
            gpu_index=0,
            timestamp=1.0,
            temperature_c=75.0,
            mem_junction_temp_c=80.0,
            memory_used_mb=1000.0,
            memory_total_mb=2000.0,
            power_draw_w=150.0,
            power_limit_w=None
        )
    ]

    # Call render - should not crash
    layout = power_view.render()

    # Assert layout is returned
    assert isinstance(layout, Layout)
