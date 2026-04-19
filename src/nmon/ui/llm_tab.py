from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Static
from nmon.llm.protocol import LlmSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.config import AppConfig
from nmon.ui.chart import Chart

TIME_RANGES = [("1h", 3600), ("4h", 14400), ("12h", 43200), ("24h", 86400)]


class LlmTab(Widget):
    """LLM server GPU/CPU utilization history charts."""

    DEFAULT_CSS = """
    LlmTab { height: 1fr; }
    LlmTab #llm-controls { height: auto; margin-bottom: 1; }
    LlmTab #llm-controls Button { margin-right: 1; }
    LlmTab Chart { margin-bottom: 1; }
    """

    def __init__(self, config: AppConfig, buffer: RingBuffer[LlmSample]) -> None:
        self.config = config
        self.buffer = buffer
        self._time_range_s = 3600
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal(id="llm-controls"):
            for label, _ in TIME_RANGES:
                yield Button(label, id=f"tr-{label}")
        yield Static("—", id="llm-title")
        yield Static("GPU utilization: —", id="llm-gpu-label")
        yield Chart(min_color="green", max_color="red", unit="%", id="chart-gpu")
        yield Static("CPU utilization: —", id="llm-cpu-label")
        yield Chart(min_color="blue", max_color="orange", unit="%", id="chart-cpu")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id and btn_id.startswith("tr-"):
            label = btn_id[3:]
            for lbl, secs in TIME_RANGES:
                if lbl == label:
                    self._time_range_s = secs
                    self.refresh_data()

    def refresh_data(self) -> None:
        samples = self.buffer.since(self._time_range_s)
        latest = self.buffer.latest()

        if latest:
            self.query_one("#llm-title", Static).update(
                f"{latest.model_name}  —  {latest.gpu_layers_offloaded}/{latest.total_layers} layers on GPU"
            )
            self.query_one("#llm-gpu-label", Static).update(
                f"GPU utilization: {latest.gpu_utilization_pct:.1f}%"
            )
            self.query_one("#llm-cpu-label", Static).update(
                f"CPU utilization: {latest.cpu_utilization_pct:.1f}%"
            )

        self.query_one("#chart-gpu", Chart).update_data(
            [s.gpu_utilization_pct for s in samples]
        )
        self.query_one("#chart-cpu", Chart).update_data(
            [s.cpu_utilization_pct for s in samples]
        )
