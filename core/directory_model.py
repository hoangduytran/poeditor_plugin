"""
Directory Model

Simple directory reader - no Qt model complexity.
Provides synchronous file system access with clean separation of concerns.
"""

import os
import stat
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from lg import logger


@dataclass
class FileInfo:
    """Information about a file or directory."""
    name: str
    path: str
    is_directory: bool
    size: int
    modified: datetime
    is_hidden: bool = False
    
    def __post_init__(self):
        """Calculate derived properties."""
        self.is_hidden = self.name.startswith('.')


class DirectoryModel:
    """Simple directory model for synchronous file access."""
    
    def __init__(self, path: str, include_hidden: bool = False):
        """
        Initialize directory model.
        
        Args:
            path: Directory path to read
            include_hidden: Whether to include hidden files (default: False)
        """
        self.path = path
        self.include_hidden = include_hidden
        self._files = []
        self._loaded = False
        
        logger.debug(f"DirectoryModel created for {path}, include_hidden={include_hidden}")
    
    def load(self) -> List[FileInfo]:
        """Load directory contents synchronously."""
        if self._loaded:
            return self._files
            
        try:
            if not os.path.exists(self.path):
                logger.warning(f"Directory does not exist: {self.path}")
                return []
                
            if not os.path.isdir(self.path):
                logger.warning(f"Path is not a directory: {self.path}")
                return []
            
            entries = os.listdir(self.path)
            self._files = []
            
            for name in entries:
                # Skip hidden files unless explicitly included
                if not self.include_hidden and name.startswith('.') and name not in ['.', '..']:
                    continue
                    
                full_path = os.path.join(self.path, name)
                try:
                    file_info = self._create_file_info(name, full_path)
                    if file_info:
                        self._files.append(file_info)
                except OSError as e:
                    logger.warning(f"Cannot access {full_path}: {e}")
                    continue
                    
            self._loaded = True
            logger.info(f"Loaded {len(self._files)} files from {self.path}")
            return self._files
            
        except OSError as e:
            logger.error(f"Cannot read directory {self.path}: {e}")
            return []
    
    def _create_file_info(self, name: str, full_path: str) -> Optional[FileInfo]:
        """Create FileInfo for a file or directory."""
        try:
            stat_result = os.stat(full_path)
            
            return FileInfo(
                name=name,
                path=full_path,
                is_directory=stat.S_ISDIR(stat_result.st_mode),
                size=stat_result.st_size if not stat.S_ISDIR(stat_result.st_mode) else 0,
                modified=datetime.fromtimestamp(stat_result.st_mtime),
                is_hidden=name.startswith('.') and name not in ['.', '..']
            )
        except OSError as e:
            logger.warning(f"Cannot stat {full_path}: {e}")
            return None
    
    def filter(self, file_filter) -> List[FileInfo]:
        """Apply filter and return matching files."""
        all_files = self.load()
        
        if not file_filter or file_filter.is_empty():
            # No filter - return all files respecting hidden file setting  
            if file_filter and not file_filter.include_hidden:
                return [f for f in all_files if not f.is_hidden]
            return all_files
        
        filtered_files = []
        for file_info in all_files:
            # Always include directories for navigation
            if file_info.is_directory:
                # But still respect hidden file setting
                if file_filter.include_hidden or not file_info.is_hidden:
                    filtered_files.append(file_info)
            else:
                # For files, apply the filter
                if file_filter.matches(file_info.name, file_info.is_directory):
                    filtered_files.append(file_info)
        
        logger.info(f"Filtered {len(all_files)} files to {len(filtered_files)} matches")
        return filtered_files
    
    def refresh(self):
        """Force reload of directory contents."""
        self._loaded = False
        self._files = []
        logger.debug(f"DirectoryModel refreshed for {self.path}")
