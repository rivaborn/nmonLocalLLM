"""
Implementation of NmonApp class for orchestrating the terminal dashboard application.
This class manages the application lifecycle, UI layout, event handling, and data flow
between monitoring components and views.
"""

from typing import List, Tuple, Optional
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from nmon.config import Settings, UserPrefs
from nmon.gpu_monitor import GpuMonitorProtocol, GpuSnapshot
from nmon.ollama_monitor import OllamaMonitorProtocol, OllamaSnapshot
from nmon.history import HistoryStore
from nmon.alerts import AlertState, compute_alert
from nmon.views.dashboard_view import DashboardView
from nmon.views.temp_view import render_temp_view, update_temp_prefs
from nmon.views.power_view import PowerView
from nmon.views.llm_view import render_llm_view
from nmon.widgets.alert_bar import AlertBar
from nmon.widgets.sparkline import Sparkline
import time
import asyncio
import readchar

class NmonApp:
    def __init__(
        self,
        settings: Settings,
        gpu_monitor: GpuMonitorProtocol,
        ollama_monitor: OllamaMonitorProtocol,
        history_store: HistoryStore,
        alert_state: AlertState,
        prefs: UserPrefs,
    ) -> None:
        """
        Initialize the NmonApp with all required components.
        
        Args:
            settings: Application settings from environment
            gpu_monitor: GPU monitoring protocol implementation
            ollama_monitor: Ollama monitoring protocol implementation
            history_store: History store for persisting metrics
            alert_state: Current alert state
            prefs: User preferences for rendering behavior
        """
        self.settings = settings
        self.gpu_monitor = gpu_monitor
        self.ollama_monitor = ollama_monitor
        self.history_store = history_store
        self.alert_state = alert_state
        self.prefs = prefs
        self.live = Live()
        self.layout = Layout()
        self.current_view_index = prefs.active_view
        self.ollama_detected = False
        self.views = []
        self.alert_bar = AlertBar(alert_state, settings)
        self._running = False
        self._live_started = False

    async def start(self) -> None:
        """
        Start the application by setting up layout, probing Ollama, loading history,
        and starting the event loop and live rendering.
        """
        await self._setup_layout()
        await self._probe_ollama()
        # HistoryStore.__init__ already loaded history from DB; no separate call needed.
        if not self._live_started:
            self.live.start()
            self._live_started = True
        self.event_task = asyncio.create_task(self._event_loop())
        self._running = True

    async def stop(self) -> None:
        """
        Stop the application by setting running flag to False, flushing history,
        stopping live rendering, and canceling the background task.
        """
        self._running = False
        if hasattr(self, 'event_task'):
            self.event_task.cancel()
            try:
                await self.event_task
            except asyncio.CancelledError:
                pass
        if self._live_started:
            self.live.stop()
            self._live_started = False
        # Flush history to database synchronously by opening a connection
        import sqlite3
        db = sqlite3.connect(self.settings.db_path)
        try:
            self.history_store.flush_to_db(db)
        finally:
            db.close()

    async def _setup_layout(self) -> None:
        """
        Set up the initial layout with alert bar and main content area.
        """
        self.layout = Layout()
        self.layout.split_row(
            Layout(name="alert_bar", size=1),
            Layout(name="main_content")
        )

    async def _probe_ollama(self) -> None:
        """
        Probe Ollama to detect if it's available and set the detection flag.
        """
        try:
            # Assuming OllamaMonitor has a probe method
            # This is a placeholder - actual implementation depends on OllamaMonitorProtocol
            self.ollama_detected = await self.ollama_monitor.probe()
        except Exception:
            self.ollama_detected = False

    async def _poll_all(self) -> Tuple[List[GpuSnapshot], Optional[OllamaSnapshot]]:
        """
        Poll all metrics from GPU and Ollama monitors concurrently.
        
        Returns:
            Tuple of (gpu_snapshots, ollama_snapshot)
        """
        gpu_snapshots = []
        ollama_snapshot = None
        try:
            gpu_snapshots = await asyncio.to_thread(self.gpu_monitor.poll)
        except Exception:
            pass
        try:
            ollama_snapshot = await self.ollama_monitor.poll()
        except Exception:
            pass
        return gpu_snapshots, ollama_snapshot

    async def _handle_event(self, event: str) -> None:
        """
        Handle keyboard events for navigation, settings adjustment, and view switching.
        
        Args:
            event: Keyboard event string
        """
        if event == "q" or event == "Ctrl+Q":
            await self.stop()
        elif event in ["1", "2", "3", "4"]:
            self.current_view_index = int(event) - 1
        elif event == readchar.KEY_LEFT:
            self.current_view_index = (self.current_view_index - 1) % 4
        elif event == readchar.KEY_RIGHT:
            self.current_view_index = (self.current_view_index + 1) % 4
        elif event == "+":
            self.settings.poll_interval_s = max(0.5, self.settings.poll_interval_s + 0.5)
        elif event == "-":
            self.settings.poll_interval_s = max(0.5, self.settings.poll_interval_s - 0.5)
        elif event in [readchar.KEY_UP, readchar.KEY_DOWN]:
            if self.current_view_index == 1:  # Temp view
                update_temp_prefs(self.prefs, event, self.settings)
        elif event == "t":
            if self.current_view_index == 1:  # Temp view
                self.prefs.show_threshold_line = not self.prefs.show_threshold_line
        elif event == "m":
            if self.current_view_index == 1:  # Temp view
                self.prefs.show_mem_junction = not self.prefs.show_mem_junction

    async def _render_current_view(self) -> None:
        """
        Render the current view based on the active view index.
        """
        # Get the current data from history store
        gpu_samples = self.history_store.get_gpu_samples()
        ollama_sample = self.history_store.get_ollama_sample()
        
        # Render based on current view index
        if self.current_view_index == 0:
            # Dashboard view
            dashboard_view = DashboardView(
                gpu_samples=gpu_samples,
                ollama_sample=ollama_sample,
                settings=self.settings,
                prefs=self.prefs,
                alert_state=self.alert_state
            )
            self.layout["main_content"].update(dashboard_view.render())
        elif self.current_view_index == 1:
            # Temperature view
            temp_view = render_temp_view(
                gpu_samples=gpu_samples,
                prefs=self.prefs,
                settings=self.settings
            )
            self.layout["main_content"].update(temp_view)
        elif self.current_view_index == 2:
            # Power view
            power_view = PowerView(
                gpu_samples=gpu_samples,
                settings=self.settings,
                prefs=self.prefs
            )
            self.layout["main_content"].update(power_view.render())
        elif self.current_view_index == 3:
            # LLM view
            llm_view = render_llm_view(
                ollama_sample=ollama_sample,
                settings=self.settings,
                prefs=self.prefs
            )
            self.layout["main_content"].update(llm_view)
        self.live.refresh()

    async def _event_loop(self) -> None:
        """
        Main event loop that polls metrics, updates history, computes alerts,
        and renders the UI with appropriate delays.
        """
        while self._running:
            # Poll all metrics
            gpu_snapshots, ollama_snapshot = await self._poll_all()
            
            # Update history store
            self.history_store.add_gpu_samples(gpu_snapshots)
            if ollama_snapshot is not None:
                self.history_store.add_ollama_sample(ollama_snapshot)
                
            # Compute alert state
            if ollama_snapshot is not None:
                now = time.time()
                self.alert_state.update(compute_alert(ollama_snapshot, self.settings, now))
            
            # Update alert bar
            self.alert_bar.update(self.alert_state, time.time())
            
            # Render current view
            await self._render_current_view()
            
            # Wait for next poll interval
            await asyncio.sleep(self.settings.poll_interval_s)
            event = await asyncio.to_thread(readchar.readkey)
            await self._handle_event(event)