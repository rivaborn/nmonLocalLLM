"""
nmon package marker file.

This file makes the containing directory importable as a Python package and
optionally re-exports selected symbols from sibling modules to shorten import paths.
"""

# Package version
__version__ = "0.1.0"

# Package metadata
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import and expose key components from submodules
# This allows users to do:
# from nmon import GPU Monitor, LLM Monitor, etc.
try:
    # Import core monitoring components
    from .gpu.monitor import GPUMonitor
    from .llm.monitor import LLMMonitor
    from .storage.ring_buffer import RingBuffer
    from .ui.app import App
    from .ui.dashboard import Dashboard
    from .config import Config
    
    # Expose these for easier imports
    __all__ = [
        'GPUMonitor',
        'LLMMonitor', 
        'RingBuffer',
        'App',
        'Dashboard',
        'Config'
    ]
    
except ImportError as e:
    # If any imports fail, log the error but don't crash
    import logging
    logging.warning(f"Failed to import some nmon components: {e}")
    __all__ = []
