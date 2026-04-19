# src/nmon/gpu/monitor.py

## Purpose
Manages GPU monitoring using NVML to collect hardware metrics and store them in a ring buffer. Runs an asynchronous polling loop to continuously sample GPU data.

## Responsibilities
- Initialize NVML and enumerate GPU devices
- Start/stop asynchronous monitoring loop
- Poll GPU metrics (temperature, memory, power) for all devices
- Handle NVML exceptions and create sentinel samples on errors
- Store collected samples in a shared ring buffer

## Key Types
- GpuMonitor (Class): Main monitoring class that manages GPU device polling and data collection

## Key Functions
### __init__
- Purpose: Initialize GPU monitor with configuration and buffer, setup NVML and device handles
- Calls: pynvml.nvmlInit(), pynvml.nvmlDeviceGetCount(), pynvml.nvmlDeviceGetHandleByIndex()

### start
- Purpose: Begin the GPU monitoring loop in an asyncio task
- Calls: asyncio.create_task()

### stop
- Purpose: Terminate the monitoring loop and shutdown NVML
- Calls: asyncio.Task.cancel(), pynvml.nvmlShutdown()

### _poll_loop
- Purpose: Run background polling loop that collects samples at configured intervals
- Calls: self._poll(), asyncio.sleep()

### _poll
- Purpose: Collect GPU metrics from all devices and handle exceptions
- Calls: pynvml.nvmlDeviceGetName(), pynvml.nvmlDeviceGetTemperature(), pynvml.nvmlDeviceGetMemoryInfo(), pynvml.nvmlDeviceGetPowerUsage(), pynvml.nvmlDeviceGetPowerManagementLimit(), self._supports_mem_junction()

### _supports_mem_junction
- Purpose: Check if memory junction temperature is supported for a GPU device
- Calls: pynvml.nvmlDeviceGetMemoryInfo()

## Globals
- logger (Logger): Module
