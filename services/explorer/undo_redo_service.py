"""
Undo/Redo Service for tracking and reversing file operations

This service provides a framework for recording file operations and
implementing undo/redo functionality across the application.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from collections import deque

from lg import logger


@dataclass
class FileOperation:
    """
    Data class representing a file operation for undo/redo tracking.

    Attributes:
        operation_type: The type of operation (copy, move, delete, etc)
        source_paths: List of source file paths
        target_path: Target path for operation
        timestamp: When the operation was performed
        is_undoable: Whether this operation can be undone
        undo_data: Additional data required for undoing the operation
    """
    operation_type: str
    source_paths: List[str]
    target_path: str
    timestamp: datetime
    is_undoable: bool = True
    undo_data: Optional[Dict[str, Any]] = None


class UndoRedoManager:
    """
    Manager for tracking file operations and implementing undo/redo functionality.

    This class maintains stacks of operations for undo and redo, with methods
    to record operations and traverse the history.
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize the undo/redo manager.

        Args:
            max_history: Maximum number of operations to keep in history
        """
        self._undo_stack = deque(maxlen=max_history)
        self._redo_stack = deque(maxlen=max_history)
        self._current_group_id = None
        self._is_operation_in_progress = False

    def record_operation(self, operation: FileOperation) -> None:
        """
        Record an operation in the undo history.

        Args:
            operation: The file operation to record
        """
        if not operation.is_undoable:
            # Don't record non-undoable operations
            return

        # Clear redo stack when a new operation is performed
        self._redo_stack.clear()

        # Add to undo stack
        self._undo_stack.append(operation)
        logger.debug(f"Recorded operation: {operation.operation_type}")

    def begin_operation_group(self) -> str:
        """
        Begin a group of operations that should be undone/redone together.

        Returns:
            Group ID string
        """
        self._current_group_id = f"group_{int(time.time())}_{id(self)}"
        return self._current_group_id

    def end_operation_group(self) -> None:
        """End the current operation group."""
        self._current_group_id = None

    def undo(self) -> Optional[FileOperation]:
        """
        Undo the last operation.

        Returns:
            The operation that was undone, or None if no operations to undo
        """
        if not self._undo_stack:
            return None

        # Move operation from undo to redo stack
        operation = self._undo_stack.pop()
        self._redo_stack.append(operation)

        logger.debug(f"Undoing operation: {operation.operation_type}")
        return operation

    def redo(self) -> Optional[FileOperation]:
        """
        Redo the last undone operation.

        Returns:
            The operation that was redone, or None if no operations to redo
        """
        if not self._redo_stack:
            return None

        # Move operation from redo to undo stack
        operation = self._redo_stack.pop()
        self._undo_stack.append(operation)

        logger.debug(f"Redoing operation: {operation.operation_type}")
        return operation

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def peek_undo(self) -> Optional[FileOperation]:
        """
        Look at the next operation to be undone without undoing it.

        Returns:
            The operation that would be undone next, or None if no operations
        """
        if not self._undo_stack:
            return None
        return self._undo_stack[-1]

    def peek_redo(self) -> Optional[FileOperation]:
        """
        Look at the next operation to be redone without redoing it.

        Returns:
            The operation that would be redone next, or None if no operations
        """
        if not self._redo_stack:
            return None
        return self._redo_stack[-1]

    def get_undo_history(self) -> List[FileOperation]:
        """
        Get the current undo history.

        Returns:
            List of operations in the undo stack (newest last)
        """
        return list(self._undo_stack)

    def get_redo_history(self) -> List[FileOperation]:
        """
        Get the current redo history.

        Returns:
            List of operations in the redo stack (newest last)
        """
        return list(self._redo_stack)

    def clear_history(self) -> None:
        """Clear all undo and redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        logger.debug("Undo/redo history cleared")

    def set_operation_in_progress(self, in_progress: bool) -> None:
        """
        Set whether an operation is currently in progress.

        Args:
            in_progress: Whether an operation is in progress
        """
        self._is_operation_in_progress = in_progress

    def is_operation_in_progress(self) -> bool:
        """
        Check if an operation is currently in progress.

        Returns:
            True if an operation is in progress, False otherwise
        """
        return self._is_operation_in_progress
