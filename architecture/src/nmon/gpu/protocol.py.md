# src/nmon/gpu/protocol.py

## Purpose
Defines data structures and protocol interface for GPU monitoring functionality.

## Responsibilities
- Define immutable GPU sample data structure with comprehensive metrics
- Specify required interface methods for GPU monitor implementations
- Provide type hints and protocol contract for GPU monitoring system

## Key Types
- GpuSample (Dataclass): Immutable container for single GPU metric snapshot
- GpuMonitorProtocol (Protocol): Interface contract for GPU monitoring implementations

## Key Functions
### None

## Globals
### None

## Dependencies
- dataclasses.dataclass: For creating immutable sample structure
- typing.Protocol: For defining interface contract
- typing.Optional: For nullable memory junction temperature
- typing.List: For collection return type
- typing |: For union type annotations (Python 3.10+)
