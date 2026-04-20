# src/nmon/alerts.py

## Purpose
Manages alert state computation and rendering for the nmon terminal dashboard based on Ollama snapshot data. Determines when and how to display GPU offload alerts.

## Responsibilities
- Compute alert states based on Ollama snapshot data and application settings
- Determine alert visibility, message content, and color coding
- Handle alert expiration timing
- Return structured alert data for dashboard display

## Key Types
- AlertState (Dataclass): Represents current alert state with active status, message, color, and expiration time

## Key Functions
### compute_alert
- Purpose: Computes current alert state based on Ollama snapshot, settings, and timestamp
- Calls: None

## Globals
None

## Dependencies
- dataclasses.dataclass
- typing.Optional
- nmon.ollama_monitor.OllamaSnapshot
- nmon.config.Settings
