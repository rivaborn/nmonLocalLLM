import asyncio
import logging
import time
from typing import Optional

from httpx import ConnectError, HTTPError, TimeoutException

from nmon.config import AppConfig
from nmon.llm.protocol import LlmSample
from nmon.storage.ring_buffer import RingBuffer

logger = logging.getLogger(__name__)

TOTAL_LAYERS_ESTIMATE = 32


class LlmMonitor:
    def __init__(self, config: AppConfig, buffer: RingBuffer[LlmSample]) -> None:
        self.config = config
        self.buffer = buffer
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def detect(self) -> bool:
        try:
            async with self.config.http_client() as client:
                response = await client.get(f"{self.config.ollama_url}/api/tags", timeout=3.0)
                if response.status_code == 200:
                    return True
                else:
                    logger.warning(f"Ollama API returned status {response.status_code}")
                    return False
        except (ConnectError, TimeoutException, HTTPError) as e:
            logger.warning(f"Failed to connect to Ollama API: {e}")
            return False

    def start(self) -> None:
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())

    def stop(self) -> None:
        if not self._running:
            return
            
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    async def _poll(self) -> Optional[LlmSample]:
        try:
            async with self.config.http_client() as client:
                response = await client.get(f"{self.config.ollama_url}/api/ps")
                if response.status_code != 200:
                    logger.warning(f"Ollama API returned status {response.status_code}")
                    return None
                
                data = response.json()
                return self._parse_response(data)  # may be None if no model loaded
        except (ConnectError, TimeoutException, HTTPError) as e:
            logger.warning(f"Failed to poll Ollama API: {e}")
            return None

    def _parse_response(self, data: dict) -> LlmSample | None:
        models = data.get("models", [])
        if not models:
            return None
        model = models[0]

        name = model["name"]
        size = model["size"]
        size_vram = model["size_vram"]

        offload_ratio = size_vram / size if size != 0 else 0.0
        gpu_layers_offloaded = round(offload_ratio * TOTAL_LAYERS_ESTIMATE)
        gpu_utilization_pct = max(0.0, min(100.0, (gpu_layers_offloaded / TOTAL_LAYERS_ESTIMATE) * 100))
        cpu_utilization_pct = 100.0 - gpu_utilization_pct

        return LlmSample(
            timestamp=time.time(),
            model_name=name,
            model_size_bytes=size,
            gpu_utilization_pct=gpu_utilization_pct,
            cpu_utilization_pct=cpu_utilization_pct,
            gpu_layers_offloaded=gpu_layers_offloaded,
            total_layers=TOTAL_LAYERS_ESTIMATE,
        )

    async def _poll_loop(self) -> None:
        while self._running:
            sample = await self._poll()
            if sample:
                self.buffer.append(sample)
            await asyncio.sleep(self.config.poll_interval_s)
