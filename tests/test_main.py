import asyncio
import os
import signal
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from nmon.app import NmonApp
from nmon.config import Settings, UserPrefs
from nmon.gpu_monitor import GpuMonitorProtocol
from nmon.history import HistoryStore
from nmon.main import main
from nmon.ollama_monitor import OllamaMonitorProtocol


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        poll_interval_s=1,
        ollama_base_url="http://localhost:11434",
        gpu_monitor_enabled=True,
        llm_monitor_enabled=True,
        power_monitor_enabled=True,
        temp_monitor_enabled=True,
        show_gpu=True,
        show_llm=True,
        show_power=True,
        show_temp=True,
        refresh_rate=1,
        log_level="INFO",
        app_name="nmon",
        db_path="/tmp/test.db",
        prefs_path="/tmp/test_prefs.json",
    )


@pytest.fixture
def mock_user_prefs():
    """Mock user preferences for testing."""
    return UserPrefs(
        gpu_threshold=80,
        temp_threshold=75,
        power_threshold=100,
        theme="dark",
        show_gpu=True,
        show_llm=True,
        show_power=True,
        show_temp=True,
    )


@pytest.fixture
def mock_history_store():
    """Mock history store for testing."""
    return MagicMock(spec=HistoryStore)


@pytest.fixture
def mock_gpu_monitor():
    """Mock GPU monitor for testing."""
    return MagicMock(spec=GpuMonitorProtocol)


@pytest.fixture
def mock_ollama_monitor():
    """Mock Ollama monitor for testing."""
    return MagicMock(spec=OllamaMonitorProtocol)


@pytest.fixture
def mock_app():
    """Mock NmonApp for testing."""
    return MagicMock(spec=NmonApp)


@pytest.fixture
def mock_pynvml():
    """Mock pynvml for testing."""
    with patch("nmon.gpu_monitor.pynvml") as mock:
        mock.init.return_value = None
        yield mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing."""
    with patch("nmon.ollama_monitor.AsyncClient") as mock:
        yield mock


@pytest.fixture
def mock_sqlite3_connection():
    """Mock sqlite3.Connection for testing."""
    with patch("nmon.db.sqlite3") as mock:
        yield mock


@pytest.fixture
def mock_rich_live():
    """Mock rich.live.Live for testing."""
    with patch("nmon.app.Live") as mock:
        yield mock


@pytest.fixture
def mock_load_settings(mocker: MockerFixture, mock_settings):
    """Mock load_settings function."""
    return mocker.patch("nmon.main.load_settings", return_value=mock_settings)


@pytest.fixture
def mock_load_user_prefs(mocker: MockerFixture, mock_user_prefs):
    """Mock load_user_prefs function."""
    return mocker.patch("nmon.main.load_user_prefs", return_value=mock_user_prefs)


@pytest.fixture
def mock_save_user_prefs(mocker: MockerFixture):
    """Mock save_user_prefs function."""
    return mocker.patch("nmon.main.save_user_prefs")


@pytest.fixture
def mock_init_db(mocker: MockerFixture):
    """Mock init_db function."""
    return mocker.patch("nmon.main.init_db")


@pytest.fixture
def mock_flush_to_db(mocker: MockerFixture):
    """Mock flush_to_db function."""
    return mocker.patch("nmon.main.flush_to_db")


@pytest.fixture
def mock_history_store_init(mocker: MockerFixture, mock_history_store):
    """Mock HistoryStore initialization."""
    return mocker.patch("nmon.main.HistoryStore", return_value=mock_history_store)


@pytest.fixture
def mock_gpu_monitor_init(mocker: MockerFixture, mock_gpu_monitor):
    """Mock GpuMonitorProtocol initialization."""
    return mocker.patch("nmon.main.GpuMonitorProtocol", return_value=mock_gpu_monitor)


@pytest.fixture
def mock_ollama_monitor_init(mocker: MockerFixture, mock_ollama_monitor):
    """Mock OllamaMonitorProtocol initialization."""
    return mocker.patch("nmon.main.OllamaMonitorProtocol", return_value=mock_ollama_monitor)


@pytest.fixture
def mock_app_init(mocker: MockerFixture, mock_app):
    """Mock NmonApp initialization."""
    return mocker.patch("nmon.main.NmonApp", return_value=mock_app)


@pytest.fixture
def mock_app_run(mocker: MockerFixture, mock_app):
    """Mock app.run() method."""
    return mocker.patch.object(mock_app, "run")


@pytest.fixture
def mock_app_shutdown(mocker: MockerFixture, mock_app):
    """Mock app.shutdown() method."""
    return mocker.patch.object(mock_app, "shutdown")


def test_main_happy_path(
    mock_load_settings,
    mock_load_user_prefs,
    mock_save_user_prefs,
    mock_init_db,
    mock_flush_to_db,
    mock_history_store_init,
    mock_gpu_monitor_init,
    mock_ollama_monitor_init,
    mock_app_init,
    mock_app_run,
    mock_pynvml,
    mock_settings,
    mock_user_prefs,
    mock_history_store,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mock_app,
):
    """Test main() function with happy path scenario."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_load_user_prefs.return_value = mock_user_prefs
    mock_app_run.return_value = None

    # Act
    main()

    # Assert
    mock_load_settings.assert_called_once()
    mock_load_user_prefs.assert_called_once()
    mock_history_store_init.assert_called_once_with(mock_settings)
    mock_gpu_monitor_init.assert_called_once_with(mock_settings.poll_interval_s)
    mock_ollama_monitor_init.assert_called_once_with(
        mock_settings.ollama_base_url, mock_settings.poll_interval_s
    )
    mock_app_init.assert_called_once_with(
        gpu_monitor=mock_gpu_monitor,
        ollama_monitor=mock_ollama_monitor,
        history_store=mock_history_store,
        settings=mock_settings,
        prefs=mock_user_prefs,
    )
    mock_app_run.assert_called_once()
    mock_save_user_prefs.assert_called_once()


def test_main_pynvml_init_failure(
    mock_load_settings,
    mock_pynvml,
    mock_settings,
):
    """Test main() function when pynvml init fails."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_pynvml.init.side_effect = Exception("NVML init failed")

    # Act & Assert
    with pytest.raises(SystemExit):
        main()


def test_main_sigterm_handling(
    mock_load_settings,
    mock_load_user_prefs,
    mock_save_user_prefs,
    mock_init_db,
    mock_flush_to_db,
    mock_history_store_init,
    mock_gpu_monitor_init,
    mock_ollama_monitor_init,
    mock_app_init,
    mock_app_run,
    mock_app_shutdown,
    mock_pynvml,
    mock_settings,
    mock_user_prefs,
    mock_history_store,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mock_app,
):
    """Test main() function handles SIGTERM gracefully."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_load_user_prefs.return_value = mock_user_prefs
    mock_app_run.side_effect = KeyboardInterrupt()

    # Act
    main()

    # Assert
    mock_app_shutdown.assert_called_once()
    mock_flush_to_db.assert_called_once()
    mock_save_user_prefs.assert_called_once()


def test_main_settings_validation(
    mock_load_settings,
    mock_settings,
):
    """Test main() function validates settings correctly."""
    # Arrange
    mock_load_settings.return_value = mock_settings

    # Act
    main()

    # Assert - This should not raise any exceptions
    mock_load_settings.assert_called_once()


def test_main_subsystem_initialization(
    mock_load_settings,
    mock_load_user_prefs,
    mock_history_store_init,
    mock_gpu_monitor_init,
    mock_ollama_monitor_init,
    mock_app_init,
    mock_pynvml,
    mock_settings,
    mock_user_prefs,
    mock_history_store,
    mock_gpu_monitor,
    mock_ollama_monitor,
    mock_app,
):
    """Test main() function initializes all subsystems correctly."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_load_user_prefs.return_value = mock_user_prefs

    # Act
    main()

    # Assert
    mock_history_store_init.assert_called_once_with(mock_settings)
    mock_gpu_monitor_init.assert_called_once_with(mock_settings.poll_interval_s)
    mock_ollama_monitor_init.assert_called_once_with(
        mock_settings.ollama_base_url, mock_settings.poll_interval_s
    )
    mock_app_init.assert_called_once_with(
        gpu_monitor=mock_gpu_monitor,
        ollama_monitor=mock_ollama_monitor,
        history_store=mock_history_store,
        settings=mock_settings,
        prefs=mock_user_prefs,
    )


def test_main_event_loop_start(
    mock_load_settings,
    mock_load_user_prefs,
    mock_app_run,
    mock_pynvml,
    mock_settings,
    mock_user_prefs,
):
    """Test main() function starts the NmonApp event loop."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_load_user_prefs.return_value = mock_user_prefs
    mock_app_run.return_value = None

    # Act
    main()

    # Assert
    mock_app_run.assert_called_once()


def test_main_preference_persistence(
    mock_load_settings,
    mock_load_user_prefs,
    mock_save_user_prefs,
    mock_pynvml,
    mock_settings,
    mock_user_prefs,
):
    """Test main() function persists user preferences on exit."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_load_user_prefs.return_value = mock_user_prefs
    mock_save_user_prefs.return_value = None

    # Act
    main()

    # Assert
    mock_save_user_prefs.assert_called_once()


def test_main_graceful_shutdown(
    mock_load_settings,
    mock_load_user_prefs,
    mock_flush_to_db,
    mock_app_shutdown,
    mock_pynvml,
    mock_settings,
    mock_user_prefs,
    mock_app,
):
    """Test main() function handles graceful shutdown."""
    # Arrange
    mock_load_settings.return_value = mock_settings
    mock_load_user_prefs.return_value = mock_user_prefs
    mock_app.run.side_effect = KeyboardInterrupt()

    # Act
    main()

    # Assert
    mock_app_shutdown.assert_called_once()
    mock_flush_to_db.assert_called_once()
