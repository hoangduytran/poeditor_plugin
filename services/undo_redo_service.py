"""
Undo/Redo Service for tracking and managing file operations.

This service provides functionality to record file operations and
allow undoing and redoing them.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from lg import logger


@dataclass
class FileOperation:
    """
    Data class representing a file operation that can be undone/redone.
    
    Attributes:
        operation_type: Type of operation (copy, paste, move, rename, etc.)
        source_paths: List of source file paths involved in the operation
        target_path: Target path for the operation (if applicable)
        timestamp: When the operation occurred
        is_undoable: Whether the operation can be undone
        undo_data: Additional data needed for undoing the operation
    """
    operation_type: str
    source_paths: List[str]
    target_path: str
    timestamp: datetime
    is_undoable: bool = True
    undo_data: Optional[Dict[str, Any]] = None


class UndoRedoManager:
    """
    Manager for tracking and handling undo/redo operations.
    
    This manager maintains a stack of file operations and provides
    methods to undo and redo them.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the undo/redo manager.
        
        Args:
            max_history: Maximum number of operations to keep in history
        """
        self._undo_stack: List[FileOperation] = []
        self._redo_stack: List[FileOperation] = []
        self._max_history = max_history
        
    def record_operation(self, operation: FileOperation) -> None:
        """
        Record a new file operation for potential undoing.
        
        Args:
            operation: The file operation to record
        """
        # Only record if undoable
        if not operation.is_undoable:
            logger.debug(f"Operation {operation.operation_type} is not undoable, not recording")
            return
            
        # Add to undo stack
        self._undo_stack.append(operation)
        logger.debug(f"Recorded {operation.operation_type} operation for undo")
        
        # Clear redo stack since we've performed a new operation
        if self._redo_stack:
            logger.debug("Clearing redo stack due to new operation")
            self._redo_stack.clear()
            
        # Trim history if needed
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
            
    def undo(self) -> Optional[FileOperation]:
        """
        Undo the most recent operation.
        
        Returns:
            The operation that was undone, or None if no operation to undo
        """
        if not self._undo_stack:
            logger.debug("Nothing to undo")
            return None
            
        # Pop the most recent operation
        operation = self._undo_stack.pop()
        
        # Add to redo stack
        self._redo_stack.append(operation)
        
        logger.debug(f"Undoing {operation.operation_type} operation")
        return operation
        
    def redo(self) -> Optional[FileOperation]:
        """
        Redo the most recently undone operation.
        
        Returns:
            The operation that was redone, or None if no operation to redo
        """
        if not self._redo_stack:
            logger.debug("Nothing to redo")
            return None
            
        # Pop the most recent undone operation
        operation = self._redo_stack.pop()
        
        # Add back to undo stack
        self._undo_stack.append(operation)
        
        logger.debug(f"Redoing {operation.operation_type} operation")
        return operation
        
    def can_undo(self) -> bool:
        """Check if there are operations that can be undone."""
        return len(self._undo_stack) > 0
        
    def can_redo(self) -> bool:
        """Check if there are operations that can be redone."""
        return len(self._redo_stack) > 0
        
    def peek_undo(self) -> Optional[FileOperation]:
        """
        Peek at the most recent operation without popping it.
        
        Returns:
            The most recent operation, or None if no operation to undo
        """
        if not self._undo_stack:
            return None
        return self._undo_stack[-1]
        
    def peek_redo(self) -> Optional[FileOperation]:
        """
        Peek at the most recently undone operation without popping it.
        
        Returns:
            The most recently undone operation, or None if no operation to redo
        """
        if not self._redo_stack:
            return None
        return self._redo_stack[-1]
        
    def clear_history(self) -> None:
        """Clear all undo and redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        logger.debug("Cleared undo/redo history")
        
    def get_undo_history(self) -> List[FileOperation]:
        """
        Get a copy of the undo history.
        
        Returns:
            List of operations in the undo stack (oldest to newest)
        """
        return self._undo_stack.copy()
        
    def get_redo_history(self) -> List[FileOperation]:
        """
        Get a copy of the redo history.
        
        Returns:
            List of operations in the redo stack (oldest to newest)
        """
        return self._redo_stack.copy()
