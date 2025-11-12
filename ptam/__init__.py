"""
Plain Text Archive Merger (.ptam)

A Python library for creating and extracting human-readable, non-compressed archives.
"""

from .core import archive, extract

__all__ = ['archive', 'extract']
__version__ = '0.1.0'
