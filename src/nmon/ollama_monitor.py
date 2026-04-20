from dataclasses import dataclass
from typing import Optional
import httpx
from nmon.config import Settings


@dataclass
class OllamaSnapshot:
    timestamp: float
    reachable: bool
    loaded_model: Optional[str] = None
    model_size_bytes: Optional[int] = None
    gpu_use_pct: Optional[float] = None
    cpu_use_pct: Optional[float] = None
    gpu_layers: Optional[int] = None
    total_layers: Optional[int] = None


class OllamaMonitorProtocol:
    async def poll(self, client: httpx.AsyncClient) -> OllamaSnapshot:
        raise NotImplementedError


class OllamaMonitor(OllamaMonitorProtocol):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ollama_detected = False
        self.ollama_client = None

    @staticmethod
    async def probe_ollama(client: httpx.AsyncClient, base_url: str) -> bool:
        try:
            response = await client.get(f"{base_url}/api/tags", timeout=3.0)
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def poll(self, client: httpx.AsyncClient) -> OllamaSnapshot:
        if not self.ollama_detected:
            # First check if Ollama is reachable
            self.ollama_detected = await self.probe_ollama(client, self.settings.ollama_base_url)
            
        if not self.ollama_detected:
            return OllamaSnapshot(
                timestamp=0.0,
                reachable=False,
                loaded_model=None,
                model_size_bytes=None,
                gpu_use_pct=None,
                cpu_use_pct=None,
                gpu_layers=None,
                total_layers=None
            )

        try:
            response = await client.get(f"{self.settings.ollama_base_url}/api/ps", timeout=3.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract model information
            model_info = data.get("models", [{}])[0] if data.get("models") else {}
            loaded_model = model_info.get("name")
            model_size_bytes = model_info.get("size")
            gpu_layers = model_info.get("gpu_layers")
            total_layers = model_info.get("total_layers")
            
            # Calculate GPU and CPU usage percentages
            gpu_use_pct = None
            cpu_use_pct = None
            
            if gpu_layers is not None and total_layers is not None and total_layers > 0:
                gpu_use_pct = (gpu_layers / total_layers) * 100
                cpu_use_pct = 100.0 - gpu_use_pct
            
            return OllamaSnapshot(
                timestamp=0.0,
                reachable=True,
                loaded_model=loaded_model,
                model_size_bytes=model_size_bytes,
                gpu_use_pct=gpu_use_pct,
                cpu_use_pct=cpu_use_pct,
                gpu_layers=gpu_layers,
                total_layers=total_layers
            )
            
        except (httpx.TimeoutException, httpx.RequestError):
            return OllamaSnapshot(
                timestamp=0.0,
                reachable=False,
                loaded_model=None,
                model_size_bytes=None,
                gpu_use_pct=None,
                cpu_use_pct=None,
                gpu_layers=None,
                total_layers=None
            )
