import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from nmon.app import NmonApp
from nmon.config import Settings, UserPrefs
from nmon.db import init_db
from nmon.gpu_monitor import GpuSnapshot, GpuMonitorProtocol
from nmon.history import HistoryStore
from nmon.ollama_monitor import OllamaMonitorProtocol, OllamaSnapshot
from nmon.alerts import AlertState


@pytest.fixture
def mock_settings():
    return Settings(
        ollama_base_url="http://127.0.0.1:11434",
        poll_interval_s=2.0,
        history_hours=24,
        db_path=":memory:",
        prefs_path="preferences.json",
        min_alert_display_s=1.0,
        offload_alert_pct=5.0,
    )


@pytest.fixture
def mock_gpu_monitor():
    return MagicMock(spec=GpuMonitorProtocol)


@pytest.fixture
def mock_ollama_monitor():
    return MagicMock(spec=OllamaMonitorProtocol)


@pytest.fixture
def mock_history_store():
    return MagicMock(spec=HistoryStore)


@pytest.fixture
def mock_alert_state():
    return MagicMock(spec=AlertState)


@pytest.fixture
def mock_prefs():
    return UserPrefs()


@pytest.fixture
def nmon_app(
    mock_settings,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mock_history_store,
    mock_alert_state,
    mock_prefs,
):
    return NmonApp(
        settings=mock_settings,
        gpu_monitor=mock_gpu_monitor,
        ollama_monitor=mock_ollama_monitor,
        history_store=mock_history_store,
        alert_state=mock_alert_state,
        prefs=mock_prefs,
    )


@pytest.mark.asyncio
async def test_nmon_app_init(
    mock_settings,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mock_history_store,
    mock_alert_state,
    mock_prefs,
):
    app = NmonApp(
        settings=mock_settings,
        gpu_monitor=mock_gpu_monitor,
        ollama_monitor=mock_ollama_monitor,
        history_store=mock_history_store,
        alert_state=mock_alert_state,
        prefs=mock_prefs,
    )
    
    assert app.settings == mock_settings
    assert app.gpu_monitor == mock_gpu_monitor
    assert app.ollama_monitor == mock_ollama_monitor
    assert app.history_store == mock_history_store
    assert app.alert_state == mock_alert_state
    assert app.prefs == mock_prefs
    assert app._running is False
    assert app.ollama_detected is False


@pytest.mark.asyncio
async def test_nmon_app_start(
    nmon_app,
    mock_history_store,
    mock_ollama_monitor,
    mocker: MockerFixture,
):
    # Mock the async methods
    mocker.patch.object(nmon_app, '_setup_layout', new_callable=AsyncMock)
    mocker.patch.object(nmon_app, '_probe_ollama', new_callable=AsyncMock)
    mocker.patch.object(nmon_app.history_store, 'load_from_db', new_callable=AsyncMock)
    mocker.patch.object(nmon_app, '_event_loop', new_callable=AsyncMock)
    
    # Mock Live to avoid actual rendering
    with patch('nmon.app.Live') as mock_live:
        mock_live_instance = MagicMock()
        mock_live.return_value = mock_live_instance
        
        await nmon_app.start()
        
        # Assert that the methods were called
        nmon_app._setup_layout.assert_awaited_once()
        nmon_app._probe_ollama.assert_awaited_once()
        nmon_app.history_store.load_from_db.assert_awaited_once()
        nmon_app._event_loop.assert_awaited_once()
        assert nmon_app._running is True


@pytest.mark.asyncio
async def test_nmon_app_stop(
    nmon_app,
    mock_history_store,
    mocker: MockerFixture,
):
    # Mock the async methods
    mocker.patch.object(nmon_app, '_event_loop', new_callable=AsyncMock)
    
    # Mock Live to avoid actual rendering
    with patch('nmon.app.Live') as mock_live:
        mock_live_instance = MagicMock()
        mock_live.return_value = mock_live_instance
        
        # Mock sqlite3.connect for database access
        with patch('sqlite3.connect') as mock_connect:
            mock_db = MagicMock()
            mock_connect.return_value = mock_db
            
            # Set _running to True to simulate running app
            nmon_app._running = True
            
            await nmon_app.stop()
            
            # Assert that flush_to_db was called (synchronous, not async)
            nmon_app.history_store.flush_to_db.assert_called_once()
            assert nmon_app._running is False


@pytest.mark.asyncio
async def test_nmon_app_probe_ollama_success(
    nmon_app,
    mock_ollama_monitor,
    mocker: MockerFixture,
):
    # Mock the probe method to return True
    mock_ollama_monitor.probe.return_value = True
    
    await nmon_app._probe_ollama()
    
    assert nmon_app.ollama_detected is True


@pytest.mark.asyncio
async def test_nmon_app_probe_ollama_failure(
    nmon_app,
    mock_ollama_monitor,
    mocker: MockerFixture,
):
    # Mock the probe method to raise an exception
    mock_ollama_monitor.probe.side_effect = Exception("Ollama not reachable")
    
    await nmon_app._probe_ollama()
    
    assert nmon_app.ollama_detected is False


@pytest.mark.asyncio
async def test_nmon_app_poll_all(
    nmon_app,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mocker: MockerFixture,
):
    # Mock the poll methods
    mock_gpu_snapshots = [GpuSnapshot(
        gpu_index=0,
        timestamp=1.0,
        temperature_c=70.0,
        mem_junction_temp_c=80.0,
        memory_used_mb=1000.0,
        memory_total_mb=2000.0,
        power_draw_w=50.0,
        power_limit_w=150.0,
    )]
    mock_ollama_snapshot = OllamaSnapshot(
        timestamp=1.0,
        reachable=True,
        loaded_model="test-model",
        model_size_bytes=1000000,
        gpu_use_pct=80.0,
        cpu_use_pct=20.0,
        gpu_layers=10,
        total_layers=10,
    )
    
    mock_gpu_monitor.poll.return_value = mock_gpu_snapshots
    mock_ollama_monitor.poll.return_value = mock_ollama_snapshot
    
    gpu_snapshots, ollama_snapshot = await nmon_app._poll_all()
    
    assert gpu_snapshots == mock_gpu_snapshots
    assert ollama_snapshot == mock_ollama_snapshot


@pytest.mark.asyncio
async def test_nmon_app_handle_event_stop(
    nmon_app,
    mocker: MockerFixture,
):
    # Mock the stop method
    mocker.patch.object(nmon_app, 'stop', new_callable=AsyncMock)
    
    await nmon_app._handle_event("q")
    
    nmon_app.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_nmon_app_handle_event_view_switch(
    nmon_app,
):
    # Test switching to view 1
    await nmon_app._handle_event("2")
    
    assert nmon_app.current_view_index == 1


@pytest.mark.asyncio
async def test_nmon_app_handle_event_poll_interval_adjust(
    nmon_app,
):
    # Test increasing poll interval
    await nmon_app._handle_event("+")
    
    assert nmon_app.settings.poll_interval_s == 2.5


@pytest.mark.asyncio
async def test_nmon_app_handle_event_invalid_key(
    nmon_app,
):
    # Test handling an invalid key - should not raise an exception
    try:
        await nmon_app._handle_event("invalid_key")
        assert True  # Should not raise an exception
    except Exception:
        assert False  # Should not reach here


@pytest.mark.asyncio
async def test_nmon_app_render_current_view(
    nmon_app,
    mocker: MockerFixture,
):
    # Mock the render method of views
    mock_view = MagicMock()
    nmon_app.views = [mock_view]
    
    await nmon_app._render_current_view()
    
    # Should have called render on the current view
    mock_view.render.assert_called_once()


@pytest.mark.asyncio
async def test_nmon_app_event_loop(
    nmon_app,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mock_history_store,
    mock_alert_state,
    mocker: MockerFixture,
):
    # Mock the async methods
    mocker.patch.object(nmon_app, '_poll_all', new_callable=AsyncMock)
    mocker.patch.object(nmon_app.history_store, 'add_gpu_samples', new_callable=AsyncMock)
    mocker.patch.object(nmon_app.history_store, 'add_ollama_sample', new_callable=AsyncMock)
    mocker.patch.object(nmon_app, 'compute_alert', new_callable=AsyncMock)
    mocker.patch.object(nmon_app, '_render_current_view', new_callable=AsyncMock)
    
    # Mock the poll_all return values
    mock_gpu_snapshots = [GpuSnapshot(
        gpu_index=0,
        timestamp=1.0,
        temperature_c=70.0,
        mem_junction_temp_c=80.0,
        memory_used_mb=1000.0,
        memory_total_mb=2000.0,
        power_draw_w=50.0,
        power_limit_w=150.0,
    )]
    mock_ollama_snapshot = OllamaSnapshot(
        timestamp=1.0,
        reachable=True,
        loaded_model="test-model",
        model_size_bytes=1000000,
        gpu_use_pct=80.0,
        cpu_use_pct=20.0,
        gpu_layers=10,
        total_layers=10,
    )
    
    nmon_app._poll_all.return_value = (mock_gpu_snapshots, mock_ollama_snapshot)
    nmon_app._running = True
    
    # Run for a few iterations
    with patch('asyncio.sleep') as mock_sleep:
        mock_sleep.return_value = asyncio.sleep(0)
        
        # Run for 2 iterations
        task = asyncio.create_task(nmon_app._event_loop())
        await asyncio.sleep(0.01)
        nmon_app._running = False
        await task
        
        # Assert that the methods were called
        nmon_app._poll_all.assert_awaited()
        nmon_app.history_store.add_gpu_samples.assert_awaited()
        nmon_app.history_store.add_ollama_sample.assert_awaited()
        nmon_app._render_current_view.assert_awaited()
