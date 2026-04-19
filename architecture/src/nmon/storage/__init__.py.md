# src/nmon/storage/__init__.py

## Purpose
This file serves as a package initializer for the storage module, providing a simplified import interface by re-exporting symbols from sibling modules.

## Responsibilities
- Initialize the storage package
- Re-export RingBuffer class from ring_buffer module
- Handle potential import errors gracefully
- Simplify import paths for storage components

## Key Types
- RingBuffer (Class): Circular buffer implementation for storing GPU metrics

## Key Functions
### None

## Globals
- None

## Dependencies
- .ring_buffer: RingBuffer class definition
- ImportError: Exception handling for missing module
- pass: Control flow for missing module handling
