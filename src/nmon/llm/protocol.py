"""
Protocol and dataclass definitions for LLM monitoring.

This module defines the data structures and interfaces used for
monitoring LLM server resource utilization.
"""

from dataclasses import dataclass
from typing import Protocol

@dataclass
class LlmSample:
    """Represents a single sample of LLM server resource utilization."""
    __slots__ = True
    timestamp: float
    model_name: str
    model_size_bytes: int
    gpu_utilization_pct: float
    cpu_utilization_pct: float
    gpu_layers_offloaded: int
    total_layers: int

class LlmMonitorProtocol(Protocol):
    """Protocol defining the interface for LLM monitoring."""
    
    async def detect(self) -> bool:
        """Detect if Ollama server is available.
        
        Returns:
            True if Ollama server is reachable, False otherwise.
        """
    
    def start(self) -> None:
        """Start the LLM monitoring loop."""
    
    def stop(self) -> None:
        """Stop the LLM monitoring loop."""
    
    async def _poll(self) -> LlmSample | None:
        """Poll for current LLM resource utilization.
        
        Returns:
            LlmSample with current utilization data, or None if polling failed.
        """
    
    def _parse_response(self, data: dict) -> LlmSample:
        """Parse Ollama API response into LlmSample.
        
        Args:
            data: Raw JSON response from Ollama API.
            
        Returns:
            LlmSample with parsed data.
        """
