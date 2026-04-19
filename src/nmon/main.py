"""
Implement the main entry point for the nmon application.

This module contains the `run()` function which serves as the application's
bootstrap logic. It loads configuration, initializes monitoring components,
and starts the Textual UI application.

Imports:
    AppConfig from nmon.config
    GpuMonitor from nmon.gpu.monitor
    LlmMonitor from nmon.llm.monitor
    RingBuffer from nmon.storage.ring_buffer
    App from nmon.ui.app

Function signatures:
    def run() -> None

Design Decisions:
    1. Use `GET /api/tags` for the Ollama availability probe because it is a
       lightweight endpoint that returns 200 when the server is reachable and
       requires no query parameters; it is not used for runtime data.
    2. `detect()` is `async` and never raises because `main.py` calls it in the
       app mount path with `await` and must not need a try/except wrapper;
       all exception handling is internal to `detect()`, which returns `False`
       on any failure.
    3. LLM tab suppressed (not hidden) when Ollama is absent because suppression
       avoids rendering a tab whose data source does not exist, preventing
       empty-state UI bugs; no retry after startup because periodic retries
       would require a separate background task and add complexity without
       user benefit (user can restart the app if they start Ollama later).
    4. `nvmlInit()` called in `GpuMonitor.__init__`, `nvmlShutdown()` called in
       `stop()` because the resource-manager pattern ensures NVML is
       initialised exactly once per monitor lifetime and is always released,
       even if the app exits abnormally via `on_unmount`.
"""

import asyncio
from nmon.config import AppConfig, load_from_env, load_persistent_settings
from nmon.gpu.monitor import GpuMonitor
from nmon.llm.monitor import LlmMonitor
from nmon.storage.ring_buffer import RingBuffer
from nmon.ui.app import NmonApp

def run() -> None:
    """
    Entry point for the nmon application.
    
    1. Load AppConfig from environment and persistence layer.
    2. Initialize RingBuffer with history_duration_s and poll_interval_s from AppConfig.
    3. Create GpuMonitor instance with AppConfig and RingBuffer.
    4. Create LlmMonitor instance with AppConfig and RingBuffer.
    5. Attempt LlmMonitor.detect() asynchronously.
    6. If detect() returns True, mark Ollama as present and start LlmMonitor polling.
    7. If detect() returns False, mark Ollama as absent and suppress LLM tab.
    8. Start GpuMonitor polling.
    9. Initialize and run App with configured monitors and tabs.
    10. Handle Ctrl+Q keybinding to exit cleanly.
    """
    # Load configuration from environment and persistent settings
    env_config = load_from_env()
    persistent_config = load_persistent_settings()
    config = AppConfig(
        ollama_url=env_config.ollama_url,
        poll_interval_s=env_config.poll_interval_s,
        history_duration_s=env_config.history_duration_s,
        temp_threshold_c=persistent_config.temp_threshold_c,
        temp_threshold_visible=persistent_config.temp_threshold_visible,
        mem_junction_visible=env_config.mem_junction_visible,
    )
    
    # Initialize ring buffer with history duration and poll interval
    buffer = RingBuffer(config)
    
    # Create monitor instances
    gpu_monitor = GpuMonitor(config, buffer)
    llm_monitor = LlmMonitor(config, buffer)
    
    # Attempt to detect Ollama presence
    ollama_present = asyncio.run(llm_monitor.detect())
    
    # Start GPU monitoring
    gpu_monitor.start()
    
    # Start LLM monitoring if Ollama is present
    if ollama_present:
        llm_monitor.start()
    
    # Initialize and run the app
    app = NmonApp(config)
    app.run()
