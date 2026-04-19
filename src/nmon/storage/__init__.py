"""
Package marker for storage module.
"""

# Import and re-export symbols from sibling modules to simplify import paths
try:
    from .ring_buffer import RingBuffer
except ImportError:
    # If ring_buffer.py doesn't exist yet, we can't import from it
    pass
