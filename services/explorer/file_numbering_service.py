"""
File Numbering Service for handling file name conflicts

This service provides functionality to detect and resolve file naming conflicts
by automatically generating numbered versions of file names.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple

from lg import logger


class FileNumberingService:
    """
    Service for handling automatic sequential file naming for duplicates.
    
    This service provides methods to detect naming patterns and generate
    numbered versions of file names to avoid conflicts when copying,
    creating, or moving files.
    """
    
    def __init__(self):
        """Initialize the file numbering service."""
        # Common patterns for numbered files
        self._patterns = [
            # Pattern: "name (1).ext", "name (2).ext"
            r"^(.+?)(\s\((\d+)\))(\.[^.]*)?$",
            # Pattern: "name 1.ext", "name 2.ext"
            r"^(.+?)(\s(\d+))(\.[^.]*)?$",
            # Pattern: "name_1.ext", "name_2.ext"
            r"^(.+?)(_(\d+))(\.[^.]*)?$",
            # Pattern: "name-1.ext", "name-2.ext"
            r"^(.+?)([-](\d+))(\.[^.]*)?$",
        ]
    
    def extract_pattern(self, file_path: str) -> Optional[Tuple[str, str, int, str]]:
        """
        Extract naming pattern from a file path.
        
        Args:
            file_path: Path to analyze
            
        Returns:
            Tuple of (base_name, separator, number, extension) or None if no pattern found
        """
        filename = os.path.basename(file_path)
        
        for pattern in self._patterns:
            match = re.match(pattern, filename)
            if match:
                base_name = match.group(1)
                separator = match.group(2).replace(match.group(3), '')
                number = int(match.group(3))
                extension = match.group(4) if match.group(4) else ""
                return (base_name, separator, number, extension)
        
        # No pattern match, might be the first file
        root, ext = os.path.splitext(filename)
        return (root, " (", 0, ext)
    
    def generate_numbered_name(self, file_path: str) -> str:
        """
        Generate a new file path with an incremented number to avoid conflicts.
        
        Args:
            file_path: Original file path
            
        Returns:
            New file path with a number appended/incremented
        """
        if not os.path.exists(file_path):
            return file_path
            
        directory = os.path.dirname(file_path)
        pattern_info = self.extract_pattern(file_path)
        
        if not pattern_info:
            # Fallback pattern if none detected
            root, ext = os.path.splitext(os.path.basename(file_path))
            new_path = os.path.join(directory, f"{root} (1){ext}")
            if not os.path.exists(new_path):
                return new_path
            pattern_info = (root, " (", 1, ext)
            
        base_name, separator, number, extension = pattern_info
        
        # Find the next available number
        counter = number + 1
        while True:
            if separator == " (":
                new_name = f"{base_name} ({counter}){extension}"
            else:
                new_name = f"{base_name}{separator}{counter}{extension}"
                
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            
            counter += 1
            # Safety check to prevent infinite loops
            if counter > 999:
                logger.warning(f"Numbered filename exceeded 999 tries for {file_path}")
                # Fallback with timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{base_name}_{timestamp}{extension}"
                return os.path.join(directory, new_name)
    
    def detect_common_pattern(self, files: list) -> Optional[Tuple[str, str, str]]:
        """
        Detect the most common numbering pattern in a list of files.
        
        Args:
            files: List of file paths to analyze
            
        Returns:
            Tuple of (pattern_type, base_name, extension) or None if no pattern found
        """
        pattern_counts = {}
        
        for file_path in files:
            pattern_info = self.extract_pattern(file_path)
            if pattern_info:
                base_name, separator, number, extension = pattern_info
                
                # Categorize separator type
                if separator == " (":
                    pattern_type = "parenthesis"
                elif separator == " ":
                    pattern_type = "space"
                elif separator == "_":
                    pattern_type = "underscore"
                elif separator == "-":
                    pattern_type = "dash"
                else:
                    pattern_type = "other"
                
                key = (pattern_type, base_name, extension)
                pattern_counts[key] = pattern_counts.get(key, 0) + 1
        
        # Find most common pattern
        if pattern_counts:
            return max(pattern_counts.items(), key=lambda x: x[1])[0]
        
        return None
    
    def generate_next_name_in_sequence(self, directory: str, base_pattern: Tuple[str, str, str]) -> str:
        """
        Generate the next name in a sequence based on detected pattern.
        
        Args:
            directory: Directory path
            base_pattern: Pattern tuple from detect_common_pattern
            
        Returns:
            New file path for next item in the sequence
        """
        pattern_type, base_name, extension = base_pattern
        
        # Find highest number in the sequence
        highest_num = 0
        for item in os.listdir(directory):
            pattern_info = self.extract_pattern(os.path.join(directory, item))
            if pattern_info:
                item_base, _, item_num, item_ext = pattern_info
                if item_base == base_name and item_ext == extension:
                    highest_num = max(highest_num, item_num)
        
        # Create next name in sequence
        next_num = highest_num + 1
        
        if pattern_type == "parenthesis":
            new_name = f"{base_name} ({next_num}){extension}"
        elif pattern_type == "space":
            new_name = f"{base_name} {next_num}{extension}"
        elif pattern_type == "underscore":
            new_name = f"{base_name}_{next_num}{extension}"
        elif pattern_type == "dash":
            new_name = f"{base_name}-{next_num}{extension}"
        else:
            new_name = f"{base_name} ({next_num}){extension}"
            
        return os.path.join(directory, new_name)
