from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Static
from nmon.gpu.protocol import GpuSample
from nmon.storage.ring_buffer import RingBuffer
from nmon.config import AppConfig
from nmon.ui.chart import Chart

TIME_RANGES = [("1h", 3600), ("4h", 14400), ("12h", 43200), ("24h", 86400)]


class MemoryTab(Widget):
    """GPU VRAM usage history chart."""

    DEFAULT_CSS = """
    MemoryTab { height: 1fr; }
    MemoryTab #mem-controls { height: auto; margin-bottom: 1; }
    MemoryTab #mem-controls Button { margin-right: 1; }
    """

    def __init__(self, config: AppConfig, buffer: RingBuffer[GpuSample]) -> None:
        self.config = config
        self.buffer = buffer
        self._time_range_s = 3600
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal(id="mem-controls"):
            for label, _ in TIME_RANGES:
                yield Button(label, id=f"tr-{label}")
        yield Static("—", id="mem-title")
        yield Static("VRAM: —", id="mem-label")
        yield Chart(min_color="green", max_color="red", unit="MiB", id="chart-mem")

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

        label = (latest.gpu_name or f"GPU {latest.gpu_index}") if latest else "—"
        self.query_one("#mem-title", Static).update(f"{label} — VRAM")

        if latest:
            pct = (
                latest.memory_used_mib / latest.memory_total_mib * 100
                if latest.memory_total_mib > 0 else 0.0
            )
            self.query_one("#mem-label", Static).update(
                f"VRAM: {latest.memory_used_mib:.0f} / {latest.memory_total_mib:.0f} MiB  ({pct:.1f}%)"
            )

        self.query_one("#chart-mem", Chart).update_data(
            [s.memory_used_mib for s in samples]
        )
