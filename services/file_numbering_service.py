"""
File Numbering Service for handling automatic numbering of duplicate files.

This service provides functionality to detect and generate properly numbered
file and directory names when duplicates are created.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple

from lg import logger


class FileNumberingService:
    """
    Service for automatically generating numbered file names when duplicates are created.
    
    This service handles detection of existing numbering patterns and 
    generation of the next appropriate number in the sequence.
    """
    
    def __init__(self):
        """Initialize the file numbering service."""
        # Common numbering patterns used in file systems
        self.patterns = [
            r"(.*) \((\d+)\)(\..*)?$",  # "file (1).txt", "folder (2)"
            r"(.*)_(\d+)(\..*)?$",       # "file_1.txt", "folder_2"
            r"(.*)-(\d+)(\..*)?$",       # "file-1.txt", "folder-2"
        ]
        
    def extract_pattern(self, path: str) -> Tuple[str, str, int, str]:
        """
        Extract numbering pattern from a file or directory name.
        
        Args:
            path: The file or directory path to analyze
            
        Returns:
            Tuple containing (base_name, separator, number, extension)
            where:
                base_name: The name without the number
                separator: The separator used (" (", "_", or "-")
                number: The extracted number, or 0 if none found
                extension: The file extension, if any
        """
        file_name = os.path.basename(path)
        
        for pattern in self.patterns:
            match = re.match(pattern, file_name)
            if match:
                base_name = match.group(1)
                number = int(match.group(2))
                extension = match.group(3) if len(match.groups()) > 2 and match.group(3) else ""
                
                # Determine separator based on pattern
                if pattern.startswith(r"(.*) \("):
                    separator = " ("
                    extension = ")" + extension
                elif "_" in pattern:
                    separator = "_"
                elif "-" in pattern:
                    separator = "-"
                
                return base_name, separator, number, extension
                
        # No pattern match, return original name with default pattern
        file_name_parts = os.path.splitext(file_name)
        base_name = file_name_parts[0]
        extension = file_name_parts[1] if len(file_name_parts) > 1 else ""
        
        return base_name, " (", 0, ")" + extension
    
    def generate_numbered_name(self, path: str, preferred_pattern: Optional[str] = None) -> str:
        """
        Generate a numbered version of the path that doesn't exist yet.
        
        Args:
            path: The original file or directory path
            preferred_pattern: Optional pattern to use for numbering
                               (" ()", "_", or "-")
            
        Returns:
            A new path with numbering that doesn't conflict with existing files
        """
        if not os.path.exists(path):
            return path
            
        dir_path = os.path.dirname(path)
        original_name = os.path.basename(path)
        
        # Extract existing pattern if any
        base_name, separator, number, extension = self.extract_pattern(path)
        
        # Override with preferred pattern if specified
        if preferred_pattern:
            if preferred_pattern == " ()":
                separator = " ("
                extension = ")" + extension.lstrip(")")
            else:
                separator = preferred_pattern
                # Remove closing parenthesis if switching from " ()" pattern
                if extension.startswith(")"):
                    extension = extension[1:]
        
        # Start searching from the current number + 1 or 1 if no number found
        start_number = max(number, 0) + 1
        
        # Generate candidate names until we find one that doesn't exist
        candidate_path = ""
        for i in range(start_number, 10000):  # Reasonable upper limit
            if separator == " (":
                new_name = f"{base_name}{separator}{i}{extension}"
            else:
                new_name = f"{base_name}{separator}{i}{extension}"
                
            candidate_path = os.path.join(dir_path, new_name)
            if not os.path.exists(candidate_path):
                logger.debug(f"Generated numbered name: {new_name} for {original_name}")
                return candidate_path
                
        # If we somehow reach here, return with a timestamp to ensure uniqueness
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if separator == " (":
            new_name = f"{base_name}{separator}{timestamp}{extension}"
        else:
            new_name = f"{base_name}{separator}{timestamp}{extension}"
            
        candidate_path = os.path.join(dir_path, new_name)
        logger.debug(f"Generated timestamp name: {new_name} for {original_name}")
        return candidate_path
    
    def detect_existing_numbering(self, directory: str, base_name: str) -> dict:
        """
        Detect existing numbered files in a directory with the given base name.
        
        Args:
            directory: The directory to scan
            base_name: The base name to look for
            
        Returns:
            Dictionary mapping pattern types to lists of detected numbers
        """
        if not os.path.isdir(directory):
            return {}
            
        result = {
            "parentheses": [],  # For " (N)" pattern
            "underscore": [],   # For "_N" pattern
            "dash": []          # For "-N" pattern
        }
        
        try:
            for entry in os.scandir(directory):
                name = entry.name
                
                # Check for parentheses pattern
                match = re.match(rf"{re.escape(base_name)} \((\d+)\).*", name)
                if match:
                    result["parentheses"].append(int(match.group(1)))
                    continue
                    
                # Check for underscore pattern
                match = re.match(rf"{re.escape(base_name)}_(\d+).*", name)
                if match:
                    result["underscore"].append(int(match.group(1)))
                    continue
                    
                # Check for dash pattern
                match = re.match(rf"{re.escape(base_name)}-(\d+).*", name)
                if match:
                    result["dash"].append(int(match.group(1)))
                    
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            
        return result
    
    def get_next_available_number(self, directory: str, base_name: str, 
                                 pattern_type: str = "parentheses") -> int:
        """
        Get the next available number for a given base name and pattern.
        
        Args:
            directory: The directory to scan
            base_name: The base name to look for
            pattern_type: The pattern type ("parentheses", "underscore", or "dash")
            
        Returns:
            The next available number (starting from 1)
        """
        existing_numbers = self.detect_existing_numbering(directory, base_name)
        
        if pattern_type not in existing_numbers or not existing_numbers[pattern_type]:
            return 1
            
        # Find the maximum existing number and add 1
        return max(existing_numbers[pattern_type]) + 1
