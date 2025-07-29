# Core Services API Documentation

**Date:** July 28, 2025  
**Component:** Explorer Core Services  
**Version:** 2.0.0  
**Status:** Production

## Overview

This document provides API documentation for the core services that power the Enhanced Explorer components. These services provide the business logic and file system operations for the UI components, ensuring a clean separation of concerns.

## Service Architecture

```
┌──────────────────────────┐     ┌───────────────────────┐
│   UI Components          │     │   Core Services       │
│  ┌────────────────────┐  │     │  ┌─────────────────┐  │
│  │EnhancedExplorerPanel├─┼─────┼─►│FileOperationsService│
│  └────────────────────┘  │     │  └─────────────────┘  │
│  ┌────────────────────┐  │     │  ┌─────────────────┐  │
│  │EnhancedFileView    ├─┼─────┼─►│DragDropService   │  │
│  └────────────────────┘  │     │  └─────────────────┘  │
│  ┌────────────────────┐  │     │  ┌─────────────────┐  │
│  │ExplorerContextMenu ├─┼─────┼─►│UndoRedoManager   │  │
│  └────────────────────┘  │     │  └─────────────────┘  │
└──────────────────────────┘     └───────────────────────┘
```

## Core Services

### FileOperationsService

The `FileOperationsService` provides a unified API for all file system operations with proper error handling, event notifications, and undo/redo support.

#### Class Definition

```python
class FileOperationsService(QObject):
    """
    Service for handling file operations in the Explorer.
    
    This service provides a centralized way to perform file operations
    with proper error handling, undo/redo support, and event notifications.
    
    This service uses:
    - FileNumberingService to handle naming conflicts
    - UndoRedoManager to track operations for undo/redo capability
    - Qt clipboard for copy/paste operations
    """
    
    # Signals
    operationStarted = Signal(str, list)  # operation_type, paths
    operationCompleted = Signal(str, list, str)  # operation_type, source_paths, target_path
    operationFailed = Signal(str, list, str)  # operation_type, paths, error_message
    clipboardChanged = Signal()
```

#### Key Methods

##### Clipboard Operations

```python
def copy_to_clipboard(self, paths: List[str]) -> bool:
    """
    Copy the specified paths to the internal clipboard.
    
    Args:
        paths: List of file/directory paths to copy
        
    Returns:
        Success status
    """
    
def cut_to_clipboard(self, paths: List[str]) -> bool:
    """
    Cut the specified paths to the internal clipboard.
    
    Args:
        paths: List of file/directory paths to cut
        
    Returns:
        Success status
    """
    
def paste(self, target_dir: str) -> List[str]:
    """
    Paste items from the clipboard to the target directory.
    
    Args:
        target_dir: Target directory for paste operation
        
    Returns:
        List of new file/directory paths created
    """
```

##### File Operations

```python
def delete(self, paths: List[str], permanent: bool = False) -> bool:
    """
    Delete the specified paths.
    
    Args:
        paths: List of file/directory paths to delete
        permanent: If True, bypass the trash/recycle bin
        
    Returns:
        Success status
    """
    
def rename(self, path: str, new_name: str) -> str:
    """
    Rename a file or directory.
    
    Args:
        path: Path to the file/directory to rename
        new_name: New name (not full path)
        
    Returns:
        New path after rename
    """
    
def duplicate(self, paths: List[str]) -> List[str]:
    """
    Duplicate files or directories in the same location.
    
    Args:
        paths: List of file/directory paths to duplicate
        
    Returns:
        List of new file/directory paths created
    """
```

##### Creation Operations

```python
def new_file(self, parent_dir: str, name: str = "New File.txt") -> str:
    """
    Create a new empty file.
    
    Args:
        parent_dir: Directory to create the file in
        name: Name of the new file
        
    Returns:
        Path to the new file
    """
    
def new_folder(self, parent_dir: str, name: str = "New Folder") -> str:
    """
    Create a new empty folder.
    
    Args:
        parent_dir: Directory to create the folder in
        name: Name of the new folder
        
    Returns:
        Path to the new folder
    """
```

#### Usage Example

```python
# Create service
file_operations = FileOperationsService()

# Connect to signals
file_operations.operationCompleted.connect(on_operation_completed)
file_operations.operationFailed.connect(on_operation_failed)

# Perform operations
file_operations.copy_to_clipboard(["/path/to/file.txt"])
new_paths = file_operations.paste("/destination/")
```

### DragDropService

The `DragDropService` manages drag and drop operations for files and directories, coordinating with the `FileOperationsService` for the actual file operations.

#### Class Definition

```python
class DragDropService(QObject):
    """
    Service for handling drag and drop operations.
    
    This service works with FileOperationsService to provide
    drag and drop capabilities for file and directory items.
    """
    
    # Signals
    drag_started = Signal(list)  # List of paths being dragged
    drop_received = Signal(list, str)  # List of paths, target directory
    drag_completed = Signal(bool)  # Success status
```

#### Key Methods

```python
def set_file_operations_service(self, service: FileOperationsService):
    """
    Set the file operations service.
    
    Args:
        service: FileOperationsService instance
    """
    
def start_drag(self, source_paths: List[str], start_pos: QPoint, parent: QObject) -> QDrag:
    """
    Start a drag operation.
    
    Args:
        source_paths: List of file paths to drag
        start_pos: Starting position for the drag
        parent: Parent widget for the drag operation
        
    Returns:
        QDrag: The drag object
    """
    
def process_drop(self, mime_data: QMimeData, target_dir: str, 
                suggested_action: Qt.DropAction) -> bool:
    """
    Process a drop operation.
    
    Args:
        mime_data: The mime data from the drop
        target_dir: The target directory
        suggested_action: The suggested drop action
        
    Returns:
        bool: True if the drop was successful, False otherwise
    """
```

#### Internal Methods

```python
def _handle_copy_action(self, source_paths: List[str], target_dir: str) -> bool:
    """
    Handle a copy action.
    
    Args:
        source_paths: List of source file paths
        target_dir: Target directory
        
    Returns:
        bool: True if the operation was successful
    """
    
def _handle_move_action(self, source_paths: List[str], target_dir: str) -> bool:
    """
    Handle a move action.
    
    Args:
        source_paths: List of source file paths
        target_dir: Target directory
        
    Returns:
        bool: True if the operation was successful
    """
    
def _handle_link_action(self, source_paths: List[str], target_dir: str) -> bool:
    """
    Handle a link action.
    
    Args:
        source_paths: List of source file paths
        target_dir: Target directory
        
    Returns:
        bool: True if the operation was successful
    """
```

#### Usage Example

```python
# Create services
file_operations = FileOperationsService()
drag_drop = DragDropService(file_operations)

# Connect to signals
drag_drop.drag_started.connect(lambda paths: print(f"Dragging {len(paths)} items"))
drag_drop.drop_received.connect(lambda paths, target: 
    print(f"Dropped {len(paths)} items into {target}"))

# Initiate drag (typically called from a view component)
drag_drop.start_drag(["/path/to/file.txt"], mouse_position, parent_widget)
```

### UndoRedoManager

The `UndoRedoManager` provides a stack-based system for tracking operations that can be undone or redone.

#### Class Definition

```python
class UndoRedoManager(QObject):
    """
    Manager for undo and redo operations.
    
    Provides a stack-based system for tracking operations that can be
    undone or redone, with proper event notifications.
    """
    
    # Signals
    undoAvailable = Signal(bool)  # True if undo is available
    redoAvailable = Signal(bool)  # True if redo is available
    operationUndone = Signal(str)  # Operation type that was undone
    operationRedone = Signal(str)  # Operation type that was redone
```

#### Key Methods

```python
def push_operation(self, operation_type: str, data: Dict[str, Any]):
    """
    Add an operation to the undo stack.
    
    Args:
        operation_type: Type of operation (copy, move, delete, etc.)
        data: Operation data for undo/redo
    """
    
def undo(self) -> bool:
    """
    Undo the last operation.
    
    Returns:
        Success status
    """
    
def redo(self) -> bool:
    """
    Redo the last undone operation.
    
    Returns:
        Success status
    """
```

#### Query Methods

```python
def can_undo(self) -> bool:
    """
    Check if undo is available.
    
    Returns:
        True if undo is available
    """
    
def can_redo(self) -> bool:
    """
    Check if redo is available.
    
    Returns:
        True if redo is available
    """
    
def clear(self):
    """Clear all undo and redo stacks."""
```

#### Usage Example

```python
# Create manager
undo_redo = UndoRedoManager()

# Connect to UI elements
undo_button.setEnabled(False)
redo_button.setEnabled(False)
undo_redo.undoAvailable.connect(undo_button.setEnabled)
undo_redo.redoAvailable.connect(redo_button.setEnabled)

# Record operations
undo_redo.push_operation("copy", {
    "sources": ["/path/to/source.txt"],
    "target": "/path/to/destination/",
    "new_paths": ["/path/to/destination/source.txt"]
})

# Perform undo/redo
undo_button.clicked.connect(undo_redo.undo)
redo_button.clicked.connect(undo_redo.redo)
```

### FileNumberingService

The `FileNumberingService` provides automatic numbering for duplicate files, ensuring unique filenames when copying or creating new files.

#### Class Definition

```python
class FileNumberingService(QObject):
    """
    Service for handling file naming conflicts.
    
    This service provides automatic numbering for duplicate files,
    ensuring unique filenames when copying or creating new files.
    """
```

#### Key Methods

```python
def get_unique_name(self, path: str) -> str:
    """
    Get a unique name for a file or directory.
    
    Args:
        path: Original path that may have naming conflicts
        
    Returns:
        Unique path with number appended if needed
    """
```

#### Internal Methods

```python
def _generate_numbered_name(self, base_path: str, counter: int) -> str:
    """
    Generate a numbered filename.
    
    Args:
        base_path: Base path without numbering
        counter: Number to append
        
    Returns:
        Path with number appended
    """
```

#### Usage Example

```python
# Create service
numbering = FileNumberingService()

# Get unique names
original_path = "/path/to/document.txt"
if os.path.exists(original_path):
    unique_path = numbering.get_unique_name(original_path)
    # Result: "/path/to/document (1).txt" if document.txt exists
    # Result: "/path/to/document (2).txt" if both document.txt and document (1).txt exist
```

## Service Integration

### Integration with UI Components

```python
class EnhancedExplorerWidget(QWidget):
    def _create_services(self):
        """Create and initialize the required services."""
        # Create file numbering service
        self.file_numbering_service = FileNumberingService()
        
        # Create undo/redo manager
        self.undo_redo_manager = UndoRedoManager()
        
        # Create file operations service
        self.file_operations_service = FileOperationsService()
        
        # Create drag and drop service
        self.drag_drop_service = DragDropService(self.file_operations_service)
        
    def _setup_ui(self):
        """Set up the user interface."""
        # ... other UI setup code ...
        
        # Set up context menu
        self.file_view.setup_context_menu(
            self.file_operations_service,
            self.undo_redo_manager
        )
```

### Handling Service Events

```python
def _connect_signals(self):
    """Connect service signals to UI updates."""
    # File operations signals
    self.file_operations_service.operationStarted.connect(self._show_operation_status)
    self.file_operations_service.operationCompleted.connect(self._on_operation_completed)
    self.file_operations_service.operationFailed.connect(self._show_error_message)
    
    # Undo/redo signals
    self.undo_redo_manager.undoAvailable.connect(self.undo_action.setEnabled)
    self.undo_redo_manager.redoAvailable.connect(self.redo_action.setEnabled)
    
    # Drag and drop signals
    self.drag_drop_service.drag_started.connect(self._on_drag_started)
    self.drag_drop_service.drop_received.connect(self._on_drop_received)
```

## Error Handling

Each service implements comprehensive error handling:

```python
try:
    # Perform operation
    shutil.copy2(source_path, target_path)
    
    # Record for undo
    self.undo_redo_manager.push_operation("copy", {
        "sources": [source_path],
        "target": os.path.dirname(target_path),
        "new_paths": [target_path]
    })
    
    # Emit success signal
    self.operationCompleted.emit("copy", [source_path], target_path)
    return target_path
    
except PermissionError:
    self.operationFailed.emit("copy", [source_path], "Permission denied")
    logger.error(f"Permission denied copying {source_path} to {target_path}")
    return None
    
except FileNotFoundError:
    self.operationFailed.emit("copy", [source_path], "File not found")
    logger.error(f"File not found: {source_path}")
    return None
    
except Exception as e:
    self.operationFailed.emit("copy", [source_path], str(e))
    logger.error(f"Error copying {source_path}: {e}")
    return None
```

## Thread Safety

These services are designed to be used from the main UI thread:

```python
# For long-running operations, use a QThread with signals
class FileOperationThread(QThread):
    operation_completed = Signal(bool, str)
    
    def __init__(self, operation_func, *args, **kwargs):
        super().__init__()
        self.operation_func = operation_func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            result = self.operation_func(*self.args, **self.kwargs)
            self.operation_completed.emit(True, result)
        except Exception as e:
            self.operation_completed.emit(False, str(e))

# Usage example
def start_large_copy_operation(sources, target):
    thread = FileOperationThread(copy_large_files, sources, target)
    thread.operation_completed.connect(on_copy_completed)
    thread.start()
```

## Performance Considerations

For optimal performance when working with these services:

1. **Batch operations** whenever possible
2. **Use appropriate methods** for bulk operations
3. **Throttle UI updates** during large operations
4. **Consider threading** for operations on large files

## Extension Points

These services can be extended in the following ways:

### Adding New File Operations

```python
class ExtendedFileOperationsService(FileOperationsService):
    """Extended file operations with advanced features."""
    
    def compress_files(self, paths: List[str], archive_name: str) -> str:
        """Compress files into an archive."""
        try:
            # Implementation details...
            self.operationCompleted.emit("compress", paths, archive_name)
            return archive_name
        except Exception as e:
            self.operationFailed.emit("compress", paths, str(e))
            return None
```

### Custom Drag and Drop Behavior

```python
class EnhancedDragDropService(DragDropService):
    """Enhanced drag and drop with custom behaviors."""
    
    def start_drag(self, source_paths: List[str], start_pos: QPoint, parent: QObject) -> QDrag:
        """Start drag with custom preview image."""
        drag = super().start_drag(source_paths, start_pos, parent)
        
        # Create custom drag preview
        if len(source_paths) > 0:
            pixmap = self._create_drag_preview(source_paths)
            drag.setPixmap(pixmap)
            
        return drag
        
    def _create_drag_preview(self, paths: List[str]) -> QPixmap:
        """Create custom preview for dragged items."""
        # Implementation details...
```

## Future Enhancements

Planned enhancements for these services include:

1. **Background Operations**: Support for long-running operations in background threads
2. **Progress Reporting**: Detailed progress updates for operations
3. **Transaction Support**: Grouping multiple operations into atomic transactions
4. **Cloud Storage Support**: Integration with cloud storage providers
5. **Extended Metadata**: Support for file tagging and metadata operations

## References

- [Qt Documentation: Signal-Slot](https://doc.qt.io/qt-6/signalsandslots.html)
- [Qt Documentation: Drag and Drop](https://doc.qt.io/qt-6/dnd.html)
- [Python Documentation: shutil](https://docs.python.org/3/library/shutil.html)
- [Python Documentation: os.path](https://docs.python.org/3/library/os.path.html)
- [Explorer API Documentation](./EXPLORER_API_DOCUMENTATION.md)
