from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Static
from nmon.gpu.protocol import GpuSample, GpuMonitorProtocol
from nmon.storage.ring_buffer import RingBuffer
from nmon.config import AppConfig, save_persistent_settings
from nmon.ui.chart import Chart

TIME_RANGES = [("1h", 3600), ("4h", 14400), ("12h", 43200), ("24h", 86400)]


class TemperatureTab(Widget):
    """GPU temperature history charts."""

    DEFAULT_CSS = """
    TemperatureTab { height: 1fr; }
    TemperatureTab #temp-controls { height: auto; margin-bottom: 1; }
    TemperatureTab #temp-controls Button { margin-right: 1; }
    TemperatureTab Chart { margin-bottom: 1; }
    """

    def __init__(
        self,
        gpu_monitor: GpuMonitorProtocol,
        config: AppConfig,
        buffer: RingBuffer[GpuSample],
    ) -> None:
        self.gpu_monitor = gpu_monitor
        self.config = config
        self.buffer = buffer
        self._time_range_s = 3600
        self._show_mem_junction = config.mem_junction_visible
        self._threshold_visible = config.temp_threshold_visible
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal(id="temp-controls"):
            for label, _ in TIME_RANGES:
                yield Button(label, id=f"tr-{label}")
            yield Button("Threshold", id="btn-threshold")
            yield Button("Mem Junc", id="btn-memjunc")
            yield Button("↑", id="btn-thresh-up")
            yield Button("↓", id="btn-thresh-down")
        yield Static("—", id="temp-title")
        yield Static("Core: —", id="temp-core-label")
        yield Chart(min_color="green", max_color="red", unit="°C", id="chart-core")
        yield Static("Mem junction: —", id="temp-mem-label")
        yield Chart(min_color="cyan", max_color="orange", unit="°C", id="chart-mem")
        yield Static("", id="temp-threshold-label")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id and btn_id.startswith("tr-"):
            label = btn_id[3:]
            for lbl, secs in TIME_RANGES:
                if lbl == label:
                    self._time_range_s = secs
                    self.refresh_data()
        elif btn_id == "btn-threshold":
            self._threshold_visible = not self._threshold_visible
            self.config.temp_threshold_visible = self._threshold_visible
            save_persistent_settings(self.config)
            self.refresh_data()
        elif btn_id == "btn-memjunc":
            self._show_mem_junction = not self._show_mem_junction
            self.refresh_data()
        elif btn_id == "btn-thresh-up":
            self.config.temp_threshold_c = min(200.0, self.config.temp_threshold_c + 0.5)
            save_persistent_settings(self.config)
            self.refresh_data()
        elif btn_id == "btn-thresh-down":
            self.config.temp_threshold_c = max(0.0, self.config.temp_threshold_c - 0.5)
            save_persistent_settings(self.config)
            self.refresh_data()

    def refresh_data(self) -> None:
        samples = self.buffer.since(self._time_range_s)
        latest = self.buffer.latest()

        label = (latest.gpu_name or f"GPU {latest.gpu_index}") if latest else "—"
        self.query_one("#temp-title", Static).update(f"{label} — Temperature")

        if latest:
            self.query_one("#temp-core-label", Static).update(
                f"Core: {latest.temperature_gpu:.1f}°C"
            )
        core_temps = [s.temperature_gpu for s in samples]
        self.query_one("#chart-core", Chart).update_data(core_temps)

        has_mem = latest is not None and latest.temperature_mem_junction is not None
        show_mem = has_mem and self._show_mem_junction
        self.query_one("#temp-mem-label", Static).display = show_mem
        self.query_one("#chart-mem", Chart).display = show_mem

        if show_mem and latest:
            self.query_one("#temp-mem-label", Static).update(
                f"Mem junction: {latest.temperature_mem_junction:.1f}°C"
            )
            mem_temps = [
                s.temperature_mem_junction
                for s in samples
                if s.temperature_mem_junction is not None
            ]
            self.query_one("#chart-mem", Chart).update_data(mem_temps)

        thresh = self.query_one("#temp-threshold-label", Static)
        thresh.update(
            f"Threshold: {self.config.temp_threshold_c:.1f}°C"
            if self._threshold_visible else ""
        )
