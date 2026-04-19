from dataclasses import dataclass
from typing import Protocol, Optional, List

@dataclass(frozen=True)
class GpuSample:
    timestamp: float
    gpu_index: int
    gpu_name: str
    temperature_gpu: float
    temperature_mem_junction: float | None
    memory_used_mib: float
    memory_total_mib: float
    power_draw_w: float
    power_limit_w: float

class GpuMonitorProtocol(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def _poll(self) -> List[GpuSample]: ...
    def _supports_mem_junction(self, handle) -> bool: ...
