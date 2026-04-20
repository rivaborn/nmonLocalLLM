# src/nmon/gpu_monitor.py

## Purpose
Provides GPU monitoring functionality using NVML to collect hardware metrics like temperature, memory usage, and power consumption.

## Responsibilities
- Initialize and manage NVML GPU driver interactions
- Collect real-time GPU metrics including temperature, memory, and power data
- Handle NVML exceptions and provide fallback values
- Return structured GPU snapshot data for monitoring

## Key Types
- GpuSnapshot (Dataclass): Represents a single point-in-time snapshot of GPU metrics
- GpuMonitorProtocol (Protocol): Defines interface for GPU monitoring implementations

## Key Functions
### poll
- Purpose: Collects current GPU metrics from all available GPUs using NVML
- Calls: pynvml.nvmlInit, pynvml.nvmlDeviceGetCount, pynvml.nvmlDeviceGetHandleByIndex, pynvml.nvmlDeviceGetTemperature, pynvml.nvmlDeviceGetMemoryBusTemperature, pynvml.nvmlDeviceGetMemoryInfo, pynvml.nvmlDeviceGetPowerUsage, pynvml.nvmlDeviceGetPowerLimit

## Globals
- _pynvml_initialized (bool): Tracks whether NVML has been initialized to prevent redundant initialization

## Dependencies
- pynvml: NVML library for GPU monitoring
- dataclasses: For GpuSnapshot data structure
- typing: Type hints for List and Optional
- logging: Error logging for NVML operations
