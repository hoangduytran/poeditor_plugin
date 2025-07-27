"""
File System Models for representing file system items in the application.
"""

import os
from enum import Enum
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

from PySide6.QtCore import QObject


class ItemType(Enum):
    """Enumeration of file system item types."""
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    UNKNOWN = "unknown"


@dataclass
class FileSystemItem:
    """
    Data class representing a file system item (file, directory, or symlink).
    
    Attributes:
        path: Absolute path to the item
        name: Name of the item (basename)
        item_type: Type of the item (file, directory, symlink, or unknown)
        size: Size of the item in bytes (for files)
        modified_time: Last modification time
        created_time: Creation time
        is_hidden: Whether the item is hidden
        parent_path: Path to the parent directory
    """
    path: str
    name: str
    item_type: ItemType
    size: int = 0
    modified_time: Optional[datetime] = None
    created_time: Optional[datetime] = None
    is_hidden: bool = False
    parent_path: Optional[str] = None
    
    @classmethod
    def from_path(cls, path: str) -> 'FileSystemItem':
        """
        Create a FileSystemItem from a file system path.
        
        Args:
            path: Path to the file system item
            
        Returns:
            A new FileSystemItem instance
        """
        name = os.path.basename(path)
        parent_path = os.path.dirname(path)
        
        # Determine item type
        if os.path.islink(path):
            item_type = ItemType.SYMLINK
        elif os.path.isdir(path):
            item_type = ItemType.DIRECTORY
        elif os.path.isfile(path):
            item_type = ItemType.FILE
        else:
            item_type = ItemType.UNKNOWN
            
        # Get file stats
        try:
            stat_info = os.stat(path)
            size = stat_info.st_size if item_type == ItemType.FILE else 0
            modified_time = datetime.fromtimestamp(stat_info.st_mtime)
            created_time = datetime.fromtimestamp(stat_info.st_ctime)
        except (FileNotFoundError, PermissionError):
            size = 0
            modified_time = None
            created_time = None
            
        # Check if hidden (platform-specific)
        is_hidden = name.startswith('.') or (
            hasattr(os, 'name') and os.name == 'nt' and 
            bool(stat_info.st_file_attributes & 0x2) 
            if 'st_file_attributes' in dir(stat_info) else False
        )
            
        return cls(
            path=path,
            name=name,
            item_type=item_type,
            size=size,
            modified_time=modified_time,
            created_time=created_time,
            is_hidden=is_hidden,
            parent_path=parent_path
        )
