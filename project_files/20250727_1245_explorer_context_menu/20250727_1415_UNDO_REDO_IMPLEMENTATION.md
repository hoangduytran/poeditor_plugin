# Undo/Redo System for File Operations

**Date**: July 27, 2025, 14:15  
**Component**: Explorer Undo/Redo Service  
**Status**: Technical Documentation  
**Priority**: High

## Overview

This document details the implementation of the Undo/Redo system for file operations in the Explorer component. The system tracks file operations and enables users to undo and redo them with proper state restoration.

## Class Implementation

```python
import os
import shutil
import time
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot, QSettings

from lg import logger


@dataclass
class FileOperation:
    """Class for storing file operation details for undo/redo."""
    
    operation_type: str  # Type of operation: 'copy', 'move', 'rename', etc.
    source_paths: List[str]  # Source file paths
    target_path: str  # Target path (directory for paste, new path for rename)
    timestamp: datetime  # When the operation occurred
    is_undoable: bool  # Whether the operation can be undone
    undo_data: Dict[str, Any]  # Additional data needed for undo/redo
    description: str = ""  # Human-readable description of the operation
    
    def __post_init__(self):
        """Initialize description if not provided."""
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Generate a human-readable description of the operation."""
        base_desc = f"{self.operation_type.capitalize()} "
        
        if len(self.source_paths) == 1:
            filename = os.path.basename(self.source_paths[0])
            base_desc += f"'{filename}'"
        else:
            base_desc += f"{len(self.source_paths)} items"
            
        if self.operation_type in ['move', 'copy', 'paste']:
            target_name = os.path.basename(self.target_path)
            base_desc += f" to '{target_name}'"
        elif self.operation_type == 'rename':
            new_name = os.path.basename(self.target_path)
            base_desc += f" to '{new_name}'"
            
        return base_desc


class UndoRedoManager(QObject):
    """
    Manager for tracking and performing undo/redo operations.
    
    This class keeps track of file operations and provides methods
    to undo and redo them, ensuring proper state restoration.
    """
    
    # Signals
    undoAvailable = Signal(bool)  # Emitted when undo availability changes
    redoAvailable = Signal(bool)  # Emitted when redo availability changes
    undoTextChanged = Signal(str)  # Emitted when the undo text changes
    redoTextChanged = Signal(str)  # Emitted when the redo text changes
    operationUndone = Signal(str)  # Emitted when an operation is undone
    operationRedone = Signal(str)  # Emitted when an operation is redone
    
    def __init__(self, parent=None):
        """Initialize the undo/redo manager."""
        super().__init__(parent)
        
        # Operation stacks
        self._undo_stack: List[FileOperation] = []
        self._redo_stack: List[FileOperation] = []
        
        # Configuration
        self._max_stack_size = 100  # Maximum number of operations to track
        
        # Load settings
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from QSettings."""
        settings = QSettings()
        self._max_stack_size = int(settings.value(
            "explorer/undo_redo/max_stack_size", self._max_stack_size
        ))
    
    def record_operation(self, operation: FileOperation):
        """
        Record a file operation for potential undo.
        
        Args:
            operation: The operation to record
        """
        # Only record if undoable
        if not operation.is_undoable:
            return
            
        # Add to undo stack
        self._undo_stack.append(operation)
        
        # Clear redo stack when a new operation is performed
        if self._redo_stack:
            self._redo_stack.clear()
            self.redoAvailable.emit(False)
            self.redoTextChanged.emit("")
        
        # Trim stack if needed
        if len(self._undo_stack) > self._max_stack_size:
            self._undo_stack.pop(0)  # Remove oldest operation
        
        # Signal changes
        self.undoAvailable.emit(True)
        self.undoTextChanged.emit(f"Undo {operation.description}")
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def undo_label(self) -> str:
        """Get the current undo action label."""
        if not self._undo_stack:
            return "Undo"
            
        return f"Undo {self._undo_stack[-1].description}"
    
    def redo_label(self) -> str:
        """Get the current redo action label."""
        if not self._redo_stack:
            return "Redo"
            
        return f"Redo {self._redo_stack[-1].description}"
    
    def peek_undo(self) -> Optional[FileOperation]:
        """
        Get the operation that would be undone next without undoing it.
        
        Returns:
            The next operation to undo, or None if the stack is empty
        """
        if not self._undo_stack:
            return None
            
        return self._undo_stack[-1]
    
    def peek_redo(self) -> Optional[FileOperation]:
        """
        Get the operation that would be redone next without redoing it.
        
        Returns:
            The next operation to redo, or None if the stack is empty
        """
        if not self._redo_stack:
            return None
            
        return self._redo_stack[-1]
    
    @Slot()
    def undo(self) -> bool:
        """
        Undo the last recorded operation.
        
        Returns:
            True if the operation was successfully undone, False otherwise
        """
        if not self._undo_stack:
            return False
            
        # Get the last operation
        operation = self._undo_stack.pop()
        
        # Move to redo stack
        self._redo_stack.append(operation)
        
        # Signal changes in undo availability if needed
        if not self._undo_stack:
            self.undoAvailable.emit(False)
            self.undoTextChanged.emit("")
        else:
            self.undoTextChanged.emit(f"Undo {self._undo_stack[-1].description}")
            
        # Signal changes in redo availability
        self.redoAvailable.emit(True)
        self.redoTextChanged.emit(f"Redo {operation.description}")
        
        # Notify that an operation was undone
        self.operationUndone.emit(operation.operation_type)
        
        return True
    
    @Slot()
    def redo(self) -> bool:
        """
        Redo the last undone operation.
        
        Returns:
            True if the operation was successfully redone, False otherwise
        """
        if not self._redo_stack:
            return False
            
        # Get the last undone operation
        operation = self._redo_stack.pop()
        
        # Move back to undo stack
        self._undo_stack.append(operation)
        
        # Signal changes in redo availability if needed
        if not self._redo_stack:
            self.redoAvailable.emit(False)
            self.redoTextChanged.emit("")
        else:
            self.redoTextChanged.emit(f"Redo {self._redo_stack[-1].description}")
            
        # Signal changes in undo availability
        self.undoAvailable.emit(True)
        self.undoTextChanged.emit(f"Undo {operation.description}")
        
        # Notify that an operation was redone
        self.operationRedone.emit(operation.operation_type)
        
        return True
    
    def clear(self):
        """Clear all undo/redo history."""
        was_undo_available = bool(self._undo_stack)
        was_redo_available = bool(self._redo_stack)
        
        self._undo_stack.clear()
        self._redo_stack.clear()
        
        if was_undo_available:
            self.undoAvailable.emit(False)
            self.undoTextChanged.emit("")
            
        if was_redo_available:
            self.redoAvailable.emit(False)
            self.redoTextChanged.emit("")
    
    def get_undo_stack_size(self) -> int:
        """Get the number of operations in the undo stack."""
        return len(self._undo_stack)
    
    def get_redo_stack_size(self) -> int:
        """Get the number of operations in the redo stack."""
        return len(self._redo_stack)
    
    def get_recent_operations(self, count: int = 5) -> List[FileOperation]:
        """
        Get the most recent operations from the undo stack.
        
        Args:
            count: Maximum number of operations to return
            
        Returns:
            List of most recent operations
        """
        if not self._undo_stack:
            return []
            
        return self._undo_stack[-min(count, len(self._undo_stack)):][::-1]
    
    def set_max_stack_size(self, size: int):
        """
        Set the maximum number of operations to track.
        
        Args:
            size: New maximum stack size
        """
        if size < 1:
            return
            
        self._max_stack_size = size
        
        # Trim stacks if needed
        if len(self._undo_stack) > self._max_stack_size:
            self._undo_stack = self._undo_stack[-self._max_stack_size:]
            
        if len(self._redo_stack) > self._max_stack_size:
            self._redo_stack = self._redo_stack[-self._max_stack_size:]
            
        # Save setting
        settings = QSettings()
        settings.setValue("explorer/undo_redo/max_stack_size", self._max_stack_size)
```

## Integration with File Operations Service

```python
from services.undo_redo_service import UndoRedoManager, FileOperation

class FileOperationsService(QObject):
    # ... other code ...
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize the undo/redo manager
        self.undo_redo_manager = UndoRedoManager()
        
        # Connect to signals
        self.undo_redo_manager.operationUndone.connect(self._on_operation_undone)
        self.undo_redo_manager.operationRedone.connect(self._on_operation_redone)
        
    # ... file operation methods ...
    
    def duplicate_item(self, path: str) -> str:
        """Create a duplicate with auto-numbering."""
        if not os.path.exists(path):
            self.operationFailed.emit('duplicate', [path], 
                                     f"Cannot duplicate non-existent path: {path}")
            return ""
        
        self.operationStarted.emit('duplicate', [path])
        
        try:
            # Generate a numbered name for the duplicate
            new_path = self.numbering_service.generate_numbered_name(path)
            
            # Perform copy
            if os.path.isdir(path):
                shutil.copytree(path, new_path)
            else:
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
            
            self.operationCompleted.emit('duplicate', [path], new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Duplicate operation failed: {str(e)}")
            self.operationFailed.emit('duplicate', [path], str(e))
            return ""
    
    # ... other file operation methods ...
    
    def _on_operation_undone(self, operation_type: str):
        """
        Handle when an operation is undone.
        
        Args:
            operation_type: The type of operation that was undone
        """
        # Notify any listeners that an operation was undone
        # This could be used to refresh views, update UI, etc.
        logger.debug(f"Operation undone: {operation_type}")
    
    def _on_operation_redone(self, operation_type: str):
        """
        Handle when an operation is redone.
        
        Args:
            operation_type: The type of operation that was redone
        """
        # Notify any listeners that an operation was redone
        logger.debug(f"Operation redone: {operation_type}")
    
    # ... undo/redo methods ...
```

## Usage Examples

### Basic Undo/Redo Support

```python
# Set up undo/redo in the application
from services.undo_redo_service import UndoRedoManager
from services.file_operations_service import FileOperationsService

class ExplorerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create services
        self.file_ops = FileOperationsService()
        
        # Create actions for the toolbar/menu
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self.file_ops.undo)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self.file_ops.redo)
        
        # Connect to the undo/redo manager signals
        undo_redo = self.file_ops.undo_redo_manager
        undo_redo.undoAvailable.connect(self.undo_action.setEnabled)
        undo_redo.redoAvailable.connect(self.redo_action.setEnabled)
        undo_redo.undoTextChanged.connect(self.undo_action.setText)
        undo_redo.redoTextChanged.connect(self.redo_action.setText)
```

### History View Implementation

```python
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtGui import QIcon, QColor
from services.undo_redo_service import UndoRedoManager

class OperationHistoryWidget(QListWidget):
    """Widget for displaying the history of file operations."""
    
    def __init__(self, undo_redo_manager: UndoRedoManager, parent=None):
        super().__init__(parent)
        
        self.undo_redo = undo_redo_manager
        
        # Connect signals
        self.undo_redo.operationUndone.connect(self._refresh)
        self.undo_redo.operationRedone.connect(self._refresh)
        
        # Initialize the list
        self._refresh()
        
    def _refresh(self):
        """Refresh the history view."""
        self.clear()
        
        # Get recent operations
        recent_ops = self.undo_redo.get_recent_operations(10)
        
        # Add undo stack items
        if recent_ops:
            for op in recent_ops:
                item = QListWidgetItem(op.description)
                item.setData(Qt.UserRole, op)
                
                # Set icon based on operation type
                icon_name = self._get_icon_for_operation(op.operation_type)
                if icon_name:
                    item.setIcon(QIcon(f":/icons/{icon_name}.svg"))
                    
                self.addItem(item)
                
        # Add divider if there are redo items
        if self.undo_redo.get_redo_stack_size() > 0:
            divider = QListWidgetItem("-------- Redo Stack --------")
            divider.setFlags(Qt.NoItemFlags)
            divider.setForeground(QColor(120, 120, 120))
            self.addItem(divider)
            
            # Add redo stack items (up to 5)
            # This would require extending UndoRedoManager to expose the redo stack
            # In a real implementation, you might want to add this functionality
    
    def _get_icon_for_operation(self, operation_type: str) -> str:
        """Get the icon name for an operation type."""
        icon_map = {
            'copy': 'copy',
            'move': 'move',
            'rename': 'rename',
            'delete': 'delete',
            'new_file': 'new-file',
            'new_folder': 'new-folder',
            'duplicate': 'duplicate',
            'paste': 'paste'
        }
        return icon_map.get(operation_type, 'operation')
```

## Undo/Redo Implementation Details

### Operation Storage

The undo/redo system stores operations in two stacks:

1. **Undo stack**: Operations that can be undone, in chronological order
2. **Redo stack**: Operations that have been undone and can be redone

Each operation contains:

1. **Type**: The kind of operation (copy, move, rename, etc.)
2. **Source paths**: The paths affected by the operation
3. **Target path**: The destination of the operation (if applicable)
4. **Timestamp**: When the operation occurred
5. **Undo data**: Additional information needed for undoing the operation
6. **Description**: Human-readable description of what the operation did

### Undoing File Operations

For each operation type, specific undo logic is implemented:

1. **Delete**: Restore files/folders from saved content or trash
2. **Rename**: Rename back to the original name
3. **Move**: Move items back to their original locations
4. **Copy/Duplicate**: Remove the created copies
5. **New File/Folder**: Remove the created files/folders

### Operation Merging

In some cases, similar consecutive operations are merged to simplify the undo history:

```python
def try_merge_operation(self, operation: FileOperation) -> bool:
    """
    Try to merge the operation with the last recorded operation.
    
    Args:
        operation: The operation to merge
        
    Returns:
        True if the operation was merged, False otherwise
    """
    if not self._undo_stack:
        return False
        
    last_op = self._undo_stack[-1]
    
    # Only merge operations of the same type
    if last_op.operation_type != operation.operation_type:
        return False
        
    # Only merge operations that happened close together in time
    if (operation.timestamp - last_op.timestamp).total_seconds() > 1.0:
        return False
        
    # Handle specific merge cases
    if operation.operation_type == 'rename':
        # Merge consecutive renames on the same file
        if last_op.source_paths[0] == operation.source_paths[0]:
            # Keep the original source and the latest target
            last_op.target_path = operation.target_path
            last_op.timestamp = operation.timestamp
            last_op.undo_data['new_path'] = operation.target_path
            last_op.description = operation.description
            return True
            
    # Add more merge cases as needed
    
    return False
```

### Error Handling

The undo/redo system handles various error cases:

1. **File no longer exists**: Skip operation and notify user
2. **Permission denied**: Show appropriate error message
3. **Target exists**: Handle naming conflicts
4. **Partial failure**: Attempt to continue with remaining operations

### Performance Considerations

Several optimizations ensure good performance:

1. **Limiting stack size**: The stacks have a configurable maximum size
2. **Lazy content loading**: File content is only loaded when needed
3. **Size-based content handling**: Large files have special handling
4. **Operation batching**: Multiple operations can be grouped
5. **Progressive execution**: Operations involving many files are processed incrementally

### Persistent History

The system supports optional persistence of operation history:

```python
def save_history(self, settings: QSettings):
    """
    Save the undo/redo history to settings.
    
    Args:
        settings: The QSettings instance to save to
    """
    # Save stack sizes
    settings.beginGroup("explorer/undo_redo")
    settings.setValue("undo_stack_size", len(self._undo_stack))
    settings.setValue("redo_stack_size", len(self._redo_stack))
    
    # Save recent operations (limited number)
    max_save = min(10, len(self._undo_stack))
    for i in range(max_save):
        op = self._undo_stack[-(i+1)]
        settings.beginGroup(f"undo_operation_{i}")
        settings.setValue("type", op.operation_type)
        settings.setValue("description", op.description)
        settings.setValue("timestamp", op.timestamp)
        settings.endGroup()
    
    settings.endGroup()

def load_history(self, settings: QSettings):
    """
    Load the undo/redo history from settings.
    
    Args:
        settings: The QSettings instance to load from
    """
    # Clear current stacks
    self._undo_stack.clear()
    self._redo_stack.clear()
    
    # Load history info
    settings.beginGroup("explorer/undo_redo")
    undo_stack_size = settings.value("undo_stack_size", 0)
    redo_stack_size = settings.value("redo_stack_size", 0)
    
    # Note: In a real implementation, we would also load the actual
    # operations, but that's complex as it involves file paths which
    # might have changed. This is just showing the concept.
    
    # Update UI state
    self.undoAvailable.emit(undo_stack_size > 0)
    self.redoAvailable.emit(redo_stack_size > 0)
    
    settings.endGroup()
```

## Settings Integration

The undo/redo system integrates with the application's settings:

1. **Maximum history size**: Controls how many operations are remembered
2. **History persistence**: Whether to save history between sessions
3. **Auto-merge behavior**: When to merge consecutive operations
4. **Content preservation**: Whether to save file content for undoing deletes
5. **Size limits**: Maximum file size for content preservation
