"""
Implement RingBuffer class in src/nmon/storage/ring_buffer.py

The RingBuffer is a time-series storage container that maintains a fixed-size
deque of samples, evicting oldest items when full. It supports thread-safe
operations and provides methods to query samples within time windows.

The RingBuffer is generic over type T, which must be a dataclass with a
timestamp field of type float. It is used to store GpuSample and LlmSample
objects from the respective monitoring modules.

Design Decisions:
- Use threading.Lock (not asyncio.Lock) because RingBuffer.append is called
  from asyncio polling loop but since/max_field/avg_field may be called from
  Textual's synchronous rendering callbacks; a threading.Lock is safe across
  both contexts.
- Compute maxlen as int(config.history_duration_s / config.poll_interval_s)
  rounded up to ensure sufficient capacity for the desired history window.
- All methods acquire the internal lock before accessing the deque to ensure
  thread-safety.
"""

from collections import deque
from threading import Lock
import time
from typing import TypeVar, Generic, List, Optional, Union

from nmon.config import AppConfig
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample

T = TypeVar('T')

class RingBuffer(Generic[T]):
    """
    A thread-safe time-series ring buffer for storing samples with timestamp.
    
    The buffer maintains a fixed-size deque of samples, automatically evicting
    the oldest samples when full. It supports querying samples within a time
    window and computing aggregate statistics (max, avg) over time windows.
    
    The buffer is initialized with AppConfig which determines the maximum
    history duration and polling interval. The buffer size is computed as:
    ceil(history_duration_s / poll_interval_s) to ensure sufficient capacity.
    """
    
    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the RingBuffer with configuration.
        
        Args:
            config: AppConfig instance containing history_duration_s and poll_interval_s
        """
        # Compute maximum length as ceil(history_duration_s / poll_interval_s)
        # Using int() with ceiling to round up
        import math
        maxlen = int(math.ceil(config.history_duration_s / config.poll_interval_s))
        
        # Initialize internal storage
        self._buffer = deque(maxlen=maxlen)
        
        # Initialize thread lock for thread-safety
        self._lock = Lock()
        
        # Store config for use in since() and other methods
        self._config = config

    def append(self, sample: T) -> None:
        """
        Append a sample to the buffer.
        
        This method is thread-safe and will acquire the internal lock before
        appending the sample.
        
        Args:
            sample: The sample to append (must have a timestamp field)
        """
        with self._lock:
            self._buffer.append(sample)

    def since(self, seconds: float) -> List[T]:
        """
        Get all samples within the specified time window.
        
        This method is thread-safe and will acquire the internal lock before
        filtering the samples.
        
        Args:
            seconds: The time window in seconds
            
        Returns:
            List of samples within the time window
        """
        with self._lock:
            threshold = time.time() - seconds
            return [sample for sample in self._buffer if sample.timestamp >= threshold]

    def latest(self) -> Optional[T]:
        """
        Get the most recent sample from the buffer.
        
        This method is thread-safe and will acquire the internal lock before
        accessing the buffer.
        
        Returns:
            The most recent sample or None if buffer is empty
        """
        with self._lock:
            if not self._buffer:
                return None
            return self._buffer[-1]

    def max_field(self, field: str, seconds: float) -> Optional[float]:
        """
        Compute the maximum value of a field within the specified time window.
        
        This method is thread-safe and will acquire the internal lock before
        filtering the samples.
        
        Args:
            field: The name of the field to compute maximum for
            seconds: The time window in seconds
            
        Returns:
            The maximum value of the field or None if no samples match the window
        """
        with self._lock:
            threshold = time.time() - seconds
            filtered_samples = [sample for sample in self._buffer if sample.timestamp >= threshold]
            
            if not filtered_samples:
                return None
                
            return max(getattr(sample, field) for sample in filtered_samples)

    def avg_field(self, field: str, seconds: float) -> Optional[float]:
        """
        Compute the average value of a field within the specified time window.
        
        This method is thread-safe and will acquire the internal lock before
        filtering the samples.
        
        Args:
            field: The name of the field to compute average for
            seconds: The time window in seconds
            
        Returns:
            The average value of the field or None if no samples match the window
        """
        with self._lock:
            threshold = time.time() - seconds
            filtered_samples = [sample for sample in self._buffer if sample.timestamp >= threshold]
            
            if not filtered_samples:
                return None
                
            total = sum(getattr(sample, field) for sample in filtered_samples)
            return total / len(filtered_samples)
