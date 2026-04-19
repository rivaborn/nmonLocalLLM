# src/nmon/storage/ring_buffer.py

## Purpose
Implements a thread-safe ring buffer for time-series sample storage with time-window query capabilities. Used to maintain fixed-size histories of GPU and LLM monitoring samples.

## Responsibilities
- Store time-series samples in a fixed-size deque with automatic eviction
- Provide thread-safe access methods for sample retrieval and aggregation
- Support time-window filtering and statistical computations (max, avg) on samples
- Maintain configurable history duration based on polling interval
- Handle sample timestamp-based queries and filtering

## Key Types
- RingBuffer (Class): Generic thread-safe container for time-series samples with timestamp field

## Key Functions
### __init__
- Purpose: Initialize ring buffer with configured maximum length and thread lock
- Calls: math.ceil, int

### append
- Purpose: Thread-safe addition of samples to buffer
- Calls: None

### since
- Purpose: Retrieve samples within specified time window
- Calls: time.time

### latest
- Purpose: Get most recent sample from buffer
- Calls: None

### max_field
- Purpose: Compute maximum value of specified field within time window
- Calls: time.time, getattr, max

### avg_field
- Purpose: Compute average value of specified field within time window
- Calls: time.time, getattr, sum

## Globals
- T (TypeVar): Generic type parameter for ring buffer samples
- None

## Dependencies
- collections.deque, threading.Lock, time, typing.TypeVar, typing.Generic, typing.List, typing.Optional
- nmon.config.AppConfig
- nmon.gpu.protocol.GpuSample
- nmon.llm.protocol.LlmSample
