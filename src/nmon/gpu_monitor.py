from dataclasses import dataclass
from typing import List, Optional
import pynvml
import logging

@dataclass
class GpuSnapshot:
    gpu_index: int
    timestamp: float
    temperature_c: float
    mem_junction_temp_c: Optional[float]
    memory_used_mb: float
    memory_total_mb: float
    power_draw_w: float
    power_limit_w: float

class GpuMonitorProtocol:
    def poll(self) -> List[GpuSnapshot]:
        raise NotImplementedError

# Global variable to track if pynvml is initialized
_pynvml_initialized = False

def poll() -> List[GpuSnapshot]:
    global _pynvml_initialized
    
    try:
        if not _pynvml_initialized:
            pynvml.nvmlInit()
            _pynvml_initialized = True
    except Exception as e:
        logging.error(f"Failed to initialize pynvml: {e}")
        return []
    
    snapshots = []
    
    try:
        num_gpus = pynvml.nvmlDeviceGetCount()
    except Exception as e:
        logging.error(f"Failed to get GPU count: {e}")
        return []
    
    for gpu_index in range(num_gpus):
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        except Exception as e:
            logging.warning(f"Failed to get handle for GPU {gpu_index}: {e}")
            continue
        
        try:
            temperature_c = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        except Exception as e:
            logging.warning(f"Failed to get temperature for GPU {gpu_index}: {e}")
            temperature_c = 0.0
        
        try:
            mem_junction_temp_c = pynvml.nvmlDeviceGetMemoryBusTemperature(handle)
        except Exception:
            # Memory junction temperature not supported
            mem_junction_temp_c = None
        
        try:
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_used_mb = memory_info.used / (1024 * 1024)
            memory_total_mb = memory_info.total / (1024 * 1024)
        except Exception as e:
            logging.warning(f"Failed to get memory info for GPU {gpu_index}: {e}")
            continue
        
        try:
            power_draw_w = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
        except Exception as e:
            logging.warning(f"Failed to get power usage for GPU {gpu_index}: {e}")
            power_draw_w = 0.0
        
        try:
            power_limit_w = pynvml.nvmlDeviceGetPowerLimit(handle) / 1000.0
        except Exception as e:
            logging.warning(f"Failed to get power limit for GPU {gpu_index}: {e}")
            power_limit_w = 0.0
        
        # Create snapshot with collected data
        snapshot = GpuSnapshot(
            gpu_index=gpu_index,
            timestamp=0.0,  # Will be set by caller if needed
            temperature_c=temperature_c,
            mem_junction_temp_c=mem_junction_temp_c,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            power_draw_w=power_draw_w,
            power_limit_w=power_limit_w
        )
        
        snapshots.append(snapshot)
    
    return snapshots
