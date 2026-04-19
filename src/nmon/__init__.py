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

# Import and expose key components from submodules.
# These imports are deliberately NOT at module level because they trigger
# expensive side-effects (NVML init, etc.) during package import. Instead,
# users should import from the submodule directly:
#   from nmon.gpu.monitor import GPUMonitor
#   from nmon.llm.monitor import LLMMonitor
# Lazy accessors below enable `from nmon import GPUMonitor` only when asked.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gpu.monitor import GPUMonitor
    from .llm.monitor import LLMMonitor
    from .storage.ring_buffer import RingBuffer
    from .config import Config

    __all__ = [
        'GPUMonitor',
        'LLMMonitor', 
        'RingBuffer',
        'Config'
    ]
