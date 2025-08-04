"""
File filter functionality for the explorer.
"""

import re
from pathlib import Path
from PySide6.QtCore import QObject, Signal

import os
import fnmatch
from typing import List
from lg import logger


class FileFilter:
    """
    Pure file filtering logic - no Qt dependencies.

    Uses the exact same proven logic from test_filter_direct.py that works correctly.
    """

    def __init__(self, pattern: str = "", include_hidden: bool = False):
        """
        Initialize file filter.

        Args:
            pattern: Filter pattern (e.g., "*.txt", "doc", "*.py")
            include_hidden: Whether to include hidden files (starting with .)
        """
        self.pattern = pattern.strip()
        self.include_hidden = include_hidden
        self.is_glob = '*' in self.pattern or '?' in self.pattern or '[' in self.pattern

        logger.debug(f"FileFilter created: pattern='{self.pattern}', include_hidden={self.include_hidden}, is_glob={self.is_glob}")

    def matches(self, filename: str, is_directory: bool = False) -> bool:
        """
        Test if a filename matches this filter.

        Args:
            filename: The filename to test (just the name, not full path)
            is_directory: Whether this is a directory

        Returns:
            True if the file matches the filter criteria
        """
        # Hidden file check first
        if not self.include_hidden and filename.startswith('.') and filename not in ['.', '..']:
            return False

        # Empty pattern = show all (except hidden if not included)
        if not self.pattern:
            return True

        # Support multiple patterns separated by semicolon
        patterns = [p.strip() for p in self.pattern.split(';') if p.strip()]

        for pattern in patterns:
            is_pattern_glob = '*' in pattern or '?' in pattern or '[' in pattern

            if is_pattern_glob:
                # Use glob pattern matching (case insensitive)
                if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                    return True
            else:
                # Use substring matching (case insensitive)
                if pattern.lower() in filename.lower():
                    return True

        return False

    def is_empty(self) -> bool:
        """Check if this is an empty filter (shows everything)."""
        return not self.pattern

    def __str__(self) -> str:
        """String representation for debugging."""
        return f"FileFilter(pattern='{self.pattern}', include_hidden={self.include_hidden})"

    def __repr__(self) -> str:
        """Official string representation."""
        return self.__str__()


def create_file_filter(pattern: str, include_hidden: bool = False) -> FileFilter:
    """
    Convenience function to create a FileFilter.

    Args:
        pattern: Filter pattern
        include_hidden: Whether to include hidden files

    Returns:
        Configured FileFilter instance
    """
    return FileFilter(pattern, include_hidden)


# Export the main class and convenience function
__all__ = ['FileFilter', 'create_file_filter']
