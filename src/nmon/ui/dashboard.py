from textual.widgets import Static
from textual.widget import Widget
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer
from nmon.gpu.protocol import GpuMonitorProtocol
from nmon.llm.protocol import LlmMonitorProtocol


class DashboardTab(Widget):
    """Dashboard tab — summary of GPU and LLM metrics."""

    def __init__(
        self,
        config: AppConfig,
        gpu_buffer: RingBuffer[GpuSample],
        llm_buffer: RingBuffer[LlmSample],
        gpu_monitor: GpuMonitorProtocol,
        llm_monitor: LlmMonitorProtocol,
    ) -> None:
        self.config = config
        self.gpu_buffer = gpu_buffer
        self.llm_buffer = llm_buffer
        self.gpu_monitor = gpu_monitor
        self.llm_monitor = llm_monitor
        super().__init__()

    def compose(self):
        yield Static("Waiting for GPU data…", id="gpu-summary")
        yield Static("", id="llm-summary")

    def refresh_data(self) -> None:
        gpu = self.gpu_buffer.latest()
        if gpu is not None:
            mem_pct = (
                gpu.memory_used_mib / gpu.memory_total_mib * 100
                if gpu.memory_total_mib > 0 else 0.0
            )
            self.query_one("#gpu-summary", Static).update(
                f"{gpu.gpu_name or f'GPU {gpu.gpu_index}'}\n"
                f"  Temp:   {gpu.temperature_gpu:.1f}°C\n"
                f"  Power:  {gpu.power_draw_w:.1f} W / {gpu.power_limit_w:.1f} W\n"
                f"  VRAM:   {gpu.memory_used_mib:.0f} / {gpu.memory_total_mib:.0f} MiB  ({mem_pct:.1f}%)"
            )

        llm = self.llm_buffer.latest()
        if llm is not None:
            self.query_one("#llm-summary", Static).update(
                f"\nLLM: {llm.model_name}\n"
                f"  GPU: {llm.gpu_utilization_pct:.1f}%   CPU: {llm.cpu_utilization_pct:.1f}%\n"
                f"  Layers on GPU: {llm.gpu_layers_offloaded} / {llm.total_layers}"
            )
