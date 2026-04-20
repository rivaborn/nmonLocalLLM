import sys
import signal
import time
from typing import NoReturn

from nmon.app import NmonApp
from nmon.config import Settings, UserPrefs
from nmon.history import HistoryStore
from nmon.gpu_monitor import GpuMonitorProtocol
from nmon.ollama_monitor import OllamaMonitorProtocol

def main() -> NoReturn:
    # Load settings from environment
    settings = Settings.model_validate_env()
    
    # Initialize HistoryStore
    history_store = HistoryStore(settings)
    
    # Initialize monitors
    gpu_monitor = GpuMonitorProtocol(settings.poll_interval_s)
    ollama_monitor = OllamaMonitorProtocol(settings.ollama_base_url, settings.poll_interval_s)
    
    # Load user preferences
    with open(settings.prefs_path, "r") as f:
        prefs = UserPrefs.model_validate_json(f.read())
    
    # Create NmonApp instance
    app = NmonApp(
        gpu_monitor=gpu_monitor,
        ollama_monitor=ollama_monitor,
        history_store=history_store,
        settings=settings,
        prefs=prefs
    )
    
    def signal_handler(sig, frame):
        print('Shutting down gracefully...')
        # Stop monitors
        gpu_monitor.stop()
        ollama_monitor.stop()
        # Flush history to DB
        history_store.flush()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the app
        app.run()
    except Exception as e:
        # Handle pynvml init failure
        if "pynvml" in str(e).lower():
            raise SystemExit(1)
        raise

if __name__ == '__main__':
    main()
