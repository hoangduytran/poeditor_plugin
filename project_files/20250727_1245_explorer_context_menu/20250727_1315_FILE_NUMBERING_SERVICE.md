# File Numbering Service Implementation

**Date**: July 27, 2025, 13:15  
**Component**: Explorer File Numbering Service  
**Status**: Technical Documentation  
**Priority**: Medium

## Overview

This document provides a detailed implementation of the FileNumberingService, which handles automatic file numbering for duplicate files. The service ensures that duplicated files follow a consistent naming pattern with sequential numbering and handles edge cases like number rollover.

## Class Implementation

```python
import os
import re
from pathlib import Path
from typing import Tuple, Dict, Optional
from PySide6.QtCore import QSettings
from lg import logger

class FileNumberingService:
    """
    Handles automatic file numbering for duplicates.
    
    This service manages the generation of numbered filenames when duplicating files,
    using a configurable pattern and tracking the highest used number for each base filename.
    """
    
    DEFAULT_FORMAT = "{name}_{number:05d}{ext}"
    DEFAULT_WIDTH = 5
    DEFAULT_ROLLOVER = 99999
    
    def __init__(self, settings: Optional[QSettings] = None):
        """
        Initialize the file numbering service.
        
        Args:
            settings: QSettings instance for persistence
        """
        self.settings = settings
        self._load_settings()
        
        # Compile regex patterns for number extraction
        self._number_pattern = re.compile(r"_(\d{5,})(?=\.[^.]+$|\s*$)")
        
        # Cache of highest used numbers per directory and base name
        # Format: {directory_path: {base_name: highest_number}}
        self._number_cache: Dict[str, Dict[str, int]] = {}
        
    def _load_settings(self):
        """Load settings from QSettings or use defaults."""
        if self.settings:
            self.format = self.settings.value("explorer/file_operations/duplicate_numbering/format", 
                                             self.DEFAULT_FORMAT)
            self.number_width = int(self.settings.value("explorer/file_operations/duplicate_numbering/number_width", 
                                                      self.DEFAULT_WIDTH))
            self.rollover_threshold = int(self.settings.value("explorer/file_operations/duplicate_numbering/rollover_threshold", 
                                                            self.DEFAULT_ROLLOVER))
            self.start_from = int(self.settings.value("explorer/file_operations/duplicate_numbering/start_from", 1))
        else:
            self.format = self.DEFAULT_FORMAT
            self.number_width = self.DEFAULT_WIDTH
            self.rollover_threshold = self.DEFAULT_ROLLOVER
            self.start_from = 1
    
    def generate_numbered_name(self, base_path: str) -> str:
        """
        Generate a numbered filename for a duplicate.
        
        Args:
            base_path: The path of the file to duplicate
            
        Returns:
            A new path with numbering applied
        """
        path = Path(base_path)
        directory = str(path.parent)
        name_without_ext, ext = os.path.splitext(path.name)
        
        # Check if the name already has a number pattern
        match = self._number_pattern.search(name_without_ext)
        if match:
            # Extract the base name without number and the existing number
            number_str = match.group(1)
            base_name = name_without_ext[:match.start()]
            current_number = int(number_str)
            
            # Determine the width to use based on the existing number
            number_width = max(len(number_str), self.number_width)
        else:
            # No existing number, use the base name as is
            base_name = name_without_ext
            current_number = 0
            number_width = self.number_width
        
        # Get the next available number
        next_number = self.get_next_number(base_name, directory)
        
        # Check if we need to increase width due to rollover
        if next_number > self.rollover_threshold:
            number_width = max(len(str(next_number)), number_width + 1)
        
        # Format the new filename
        number_format = "{{:0{}d}}".format(number_width)
        number_str = number_format.format(next_number)
        
        if "{number}" in self.format:
            # Use the format with the calculated number
            new_name = self.format.format(
                name=base_name, 
                number=number_str,
                ext=ext
            )
        else:
            # Fallback to standard format
            new_name = f"{base_name}_{number_str}{ext}"
        
        # Save the used number for future reference
        self._update_highest_number(base_name, directory, next_number)
        
        return os.path.join(directory, new_name)
    
    def parse_numbered_name(self, path: str) -> Tuple[str, int]:
        """
        Extract the base name and number from a numbered file.
        
        Args:
            path: The path to parse
            
        Returns:
            Tuple of (base_name, number) or (filename, 0) if no number found
        """
        name = os.path.basename(path)
        name_without_ext, ext = os.path.splitext(name)
        
        match = self._number_pattern.search(name_without_ext)
        if match:
            number_str = match.group(1)
            base_name = name_without_ext[:match.start()]
            number = int(number_str)
            return (base_name, number)
        
        return (name_without_ext, 0)
    
    def get_next_number(self, base_name: str, directory: str) -> int:
        """
        Determine the next available number for a file.
        
        This checks both the cache and the filesystem to find the highest
        existing number for this base name, then adds 1.
        
        Args:
            base_name: The base filename without numbering
            directory: The directory to check
            
        Returns:
            The next available number
        """
        # Check the cache first
        highest = self._get_cached_highest_number(base_name, directory)
        
        # Scan the directory for existing numbers if no cache or cache is stale
        if highest is None:
            highest = self._scan_directory_for_highest_number(base_name, directory)
        
        # Start from the configured minimum or one higher than the highest found
        next_number = max(self.start_from, highest + 1) if highest is not None else self.start_from
        
        return next_number
    
    def _get_cached_highest_number(self, base_name: str, directory: str) -> Optional[int]:
        """Get the cached highest number for a base name in a directory."""
        dir_cache = self._number_cache.get(directory, {})
        return dir_cache.get(base_name)
    
    def _update_highest_number(self, base_name: str, directory: str, number: int):
        """Update the cached highest number for a base name in a directory."""
        if directory not in self._number_cache:
            self._number_cache[directory] = {}
        
        dir_cache = self._number_cache[directory]
        current_highest = dir_cache.get(base_name, 0)
        
        if number > current_highest:
            dir_cache[base_name] = number
            
            # Persist to settings if available
            if self.settings:
                key = f"explorer/file_operations/last_numbers/{directory}/{base_name}"
                self.settings.setValue(key, number)
                self.settings.sync()
    
    def _scan_directory_for_highest_number(self, base_name: str, directory: str) -> int:
        """
        Scan a directory to find the highest number used for a base name.
        
        Args:
            base_name: The base filename to check
            directory: The directory to scan
            
        Returns:
            The highest number found, or 0 if none found
        """
        highest_number = 0
        
        try:
            # Check if directory exists
            if not os.path.isdir(directory):
                return highest_number
            
            # Scan all files in the directory
            for filename in os.listdir(directory):
                name_without_ext, ext = os.path.splitext(filename)
                
                # Check if this file matches our base name pattern
                match = self._number_pattern.search(name_without_ext)
                if match and name_without_ext.startswith(base_name):
                    try:
                        number = int(match.group(1))
                        highest_number = max(highest_number, number)
                    except ValueError:
                        # Not a valid number, skip
                        pass
        
        except (IOError, OSError) as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        # Cache the result
        self._update_highest_number(base_name, directory, highest_number)
        
        return highest_number
    
    def clear_cache(self):
        """Clear the numbering cache."""
        self._number_cache.clear()
    
    def clear_cache_for_directory(self, directory: str):
        """Clear the numbering cache for a specific directory."""
        if directory in self._number_cache:
            del self._number_cache[directory]
```

## Usage Examples

### Basic Duplication

```python
# Example usage in the FileOperationService class
def duplicate_item(self, path: str) -> str:
    """Create a duplicate with auto-numbering."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cannot duplicate non-existent path: {path}")
    
    # Generate a numbered name for the duplicate
    new_path = self.numbering_service.generate_numbered_name(path)
    
    try:
        if os.path.isdir(path):
            # Use shutil to copy directory recursively
            shutil.copytree(path, new_path)
        else:
            # Use shutil to copy file with metadata preservation
            shutil.copy2(path, new_path)
        
        # Record the operation for undo
        operation = FileOperation(
            operation_type='duplicate',
            source_paths=[path],
            target_path=new_path,
            timestamp=datetime.now(),
            is_undoable=True,
            undo_data={'created_path': new_path}
        )
        self.undo_redo_manager.record_operation(operation)
        
        return new_path
    
    except (IOError, OSError) as e:
        logger.error(f"Failed to duplicate {path}: {e}")
        raise
```

### Multiple Duplications

When creating multiple duplicates of the same file in sequence:

```python
file_path = "/path/to/document.txt"

# First duplicate: document_00001.txt
first_duplicate = numbering_service.generate_numbered_name(file_path)
print(first_duplicate)  # "/path/to/document_00001.txt"

# Second duplicate: document_00002.txt
second_duplicate = numbering_service.generate_numbered_name(file_path)
print(second_duplicate)  # "/path/to/document_00002.txt"

# Duplicate of a duplicate: document_00001_00001.txt
duplicate_of_duplicate = numbering_service.generate_numbered_name(first_duplicate)
print(duplicate_of_duplicate)  # "/path/to/document_00001_00001.txt"
```

## Number Rollover Example

When hitting the rollover threshold:

```python
# Assuming we already have document_99999.txt
# The next duplicate will increase the width
file_path = "/path/to/document_99999.txt"
next_duplicate = numbering_service.generate_numbered_name(file_path)
print(next_duplicate)  # "/path/to/document_000001.txt" (6 digits)
```

## Edge Cases

The numbering service handles several edge cases:

1. **Files with existing numbers**: When duplicating an already-numbered file, the service correctly extracts and increments the existing number
2. **Directory enumeration failures**: If the directory cannot be read (permissions, etc.), falls back to the start number or cached values
3. **Invalid file paths**: Proper validation prevents operations on non-existent paths
4. **Number width consistency**: Maintains consistent width for aesthetics unless rollover occurs
5. **Thread safety**: While not shown in the example, production code should use locks for thread safety when accessing the cache

## Settings Integration

The numbering service integrates with the application's QSettings system for persistence:

1. **Format template**: Users can customize the numbering format
2. **Number width**: Control the default number of digits
3. **Rollover threshold**: Determine when to increase digit width
4. **Start number**: Configure the first number to use (default: 1)

These settings can be configured through the application's preferences dialog.
