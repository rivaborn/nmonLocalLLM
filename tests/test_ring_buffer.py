import time
import threading
from collections import deque
from typing import TypeVar, List, Optional, Any

# Import the necessary classes from the existing codebase
from src.nmon.config import AppConfig
from src.nmon.gpu.protocol import GpuSample
from src.nmon.llm.protocol import LlmSample

T = TypeVar('T')

class RingBuffer:
    def __init__(self, config: AppConfig) -> None:
        # 1. Compute `maxlen` as `int(config.history_duration_s / config.poll_interval_s)` rounded up
        maxlen = int(config.history_duration_s / config.poll_interval_s)
        if config.history_duration_s % config.poll_interval_s != 0:
            maxlen += 1
            
        # 2. Initialize internal `collections.deque(maxlen=maxlen)` storage
        self._storage = deque(maxlen=maxlen)
        
        # 3. Initialize `threading.Lock()` for thread-safety
        self._lock = threading.Lock()
        
        # 4. Store `config` for use in `since()` and other methods
        self._config = config

    def append(self, sample: T) -> None:
        # 1. Acquire internal `threading.Lock()`
        with self._lock:
            # 2. Append `sample` to internal `deque`
            self._storage.append(sample)
            # 3. Release `threading.Lock()` (automatically handled by 'with' statement)

    def since(self, seconds: float) -> List[T]:
        # 1. Acquire internal `threading.Lock()`
        with self._lock:
            # 2. Compute `threshold` as `time.time() - seconds`
            threshold = time.time() - seconds
            
            # 3. Filter internal `deque` to samples with `sample.timestamp >= threshold`
            filtered = [sample for sample in self._storage if sample.timestamp >= threshold]
            
            # 4. Return filtered list
            # 5. Release `threading.Lock()` (automatically handled by 'with' statement)
            return filtered

    def latest(self) -> Optional[T]:
        # 1. Acquire internal `threading.Lock()`
        with self._lock:
            # 2. If internal `deque` is empty, return `None`
            if not self._storage:
                return None
                
            # 3. Return last element of internal `deque`
            # 4. Release `threading.Lock()` (automatically handled by 'with' statement)
            return self._storage[-1]

    def max_field(self, field: str, seconds: float) -> Optional[float]:
        # 1. Acquire internal `threading.Lock()`
        with self._lock:
            # 2. Compute `threshold` as `time.time() - seconds`
            threshold = time.time() - seconds
            
            # 3. Filter internal `deque` to samples with `sample.timestamp >= threshold`
            filtered = [sample for sample in self._storage if sample.timestamp >= threshold]
            
            # 4. If filtered list is empty, return `None`
            if not filtered:
                return None
                
            # 5. Compute `max` of `getattr(sample, field)` for all samples in filtered list
            # 6. Return computed `max`
            # 7. Release `threading.Lock()` (automatically handled by 'with' statement)
            return max(getattr(sample, field) for sample in filtered)

    def avg_field(self, field: str, seconds: float) -> Optional[float]:
        # 1. Acquire internal `threading.Lock()`
        with self._lock:
            # 2. Compute `threshold` as `time.time() - seconds`
            threshold = time.time() - seconds
            
            # 3. Filter internal `deque` to samples with `sample.timestamp >= threshold`
            filtered = [sample for sample in self._storage if sample.timestamp >= threshold]
            
            # 4. If filtered list is empty, return `None`
            if not filtered:
                return None
                
            # 5. Compute `sum` of `getattr(sample, field)` for all samples in filtered list
            # 6. Compute `avg` as `sum / len(filtered_list)`
            # 7. Return computed `avg`
            # 8. Release `threading.Lock()` (automatically handled by 'with' statement)
            total = sum(getattr(sample, field) for sample in filtered)
            return total / len(filtered)
