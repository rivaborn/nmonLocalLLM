import asyncio
import logging
import time
from typing import List, Optional

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message=".*pynvml.*")
import pynvml

from nmon.config import AppConfig
from nmon.gpu.protocol import GpuSample
from nmon.storage.ring_buffer import RingBuffer

logger = logging.getLogger(__name__)


class GpuMonitor:
    def __init__(self, config: AppConfig, buffer: RingBuffer[GpuSample]) -> None:
        """Initialize GPU monitor with config and buffer."""
        self.config = config
        self.buffer = buffer
        
        # Initialize NVML library
        pynvml.nvmlInit()
        
        # Internal state
        self.task: Optional[asyncio.Task] = None
        self.running = False
        
        # Device handles
        self.device_handles: List[pynvml.c_nvmlDevice_t] = []
        
        # Populate device handles
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            self.device_handles.append(handle)

    def start(self) -> None:
        """Start the GPU monitoring loop."""
        if self.running:
            return
            
        self.running = True
        self.task = asyncio.create_task(self._poll_loop())

    def stop(self) -> None:
        """Stop the GPU monitoring loop."""
        if not self.running:
            return
            
        self.running = False
        
        if self.task:
            self.task.cancel()
            
        pynvml.nvmlShutdown()

    async def _poll_loop(self) -> None:
        """Background polling loop."""
        while self.running:
            samples = self._poll()
            for sample in samples:
                self.buffer.append(sample)
            await asyncio.sleep(self.config.poll_interval_s)

    def _poll(self) -> List[GpuSample]:
        """Poll GPU data for all devices."""
        samples = []
        
        for i, handle in enumerate(self.device_handles):
            try:
                # Get device name (bytes in older pynvml, str in newer)
                raw_name = pynvml.nvmlDeviceGetName(handle)
                name = raw_name.decode() if isinstance(raw_name, bytes) else raw_name

                # Get temperature
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                # Get memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Get power info
                power = pynvml.nvmlDeviceGetPowerUsage(handle)
                
                # Get power limit
                power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle)
                
                # Check if memory junction temperature is supported
                mem_junction_supported = self._supports_mem_junction(handle)
                mem_junction_temp = None
                
                # NVML_TEMPERATURE_MEMORY may not exist in older nvidia-ml-py versions
                mem_temp_constant = getattr(pynvml, 'NVML_TEMPERATURE_MEMORY', None)
                if mem_junction_supported and mem_temp_constant is not None:
                    mem_junction_temp = pynvml.nvmlDeviceGetTemperature(handle, mem_temp_constant)
                
                # Create sample
                sample = GpuSample(
                    timestamp=time.time(),
                    gpu_index=i,
                    gpu_name=name,
                    temperature_gpu=float(temp),
                    temperature_mem_junction=float(mem_junction_temp) if mem_junction_temp is not None else None,
                    memory_used_mib=float(mem_info.used) // (1024 * 1024),
                    memory_total_mib=float(mem_info.total) // (1024 * 1024),
                    power_draw_w=float(power) / 1000.0,
                    power_limit_w=float(power_limit) / 1000.0,
                )
                samples.append(sample)
                
            except pynvml.NVMLError as e:
                logger.warning(f"Error collecting data from GPU {i}: {e}")
                # Create sentinel sample with None/NaN fields
                sample = GpuSample(
                    timestamp=time.time(),
                    gpu_index=i,
                    gpu_name="",
                    temperature_gpu=float("nan"),
                    temperature_mem_junction=None,
                    memory_used_mib=float("nan"),
                    memory_total_mib=float("nan"),
                    power_draw_w=float("nan"),
                    power_limit_w=float("nan"),
                )
                samples.append(sample)
            except Exception as e:
                logger.warning(f"Unexpected error collecting data from GPU {i}: {e}")
                # Create sentinel sample with None/NaN fields
                sample = GpuSample(
                    timestamp=time.time(),
                    gpu_index=i,
                    gpu_name="",
                    temperature_gpu=float("nan"),
                    temperature_mem_junction=None,
                    memory_used_mib=float("nan"),
                    memory_total_mib=float("nan"),
                    power_draw_w=float("nan"),
                    power_limit_w=float("nan"),
                )
                samples.append(sample)
                
        return samples

    def _supports_mem_junction(self, handle: object) -> bool:
        """Check if memory junction temperature is supported for the device."""
        try:
            pynvml.nvmlDeviceGetMemoryInfo(handle)
            return True
        except pynvml.NVMLError_NotSupported:
            return False
        except pynvml.NVMLError as e:
            logger.warning(f"Error checking memory junction support for GPU: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error checking memory junction support for GPU: {e}")
            return False
