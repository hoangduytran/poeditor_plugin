# Explorer Components API Documentation

**Date:** July 28, 2025  
**Component:** Enhanced Explorer Panel  
**Version:** 2.0.0  
**Status:** Production

## Overview

This document provides comprehensive API documentation for the Enhanced Explorer components implemented in Phases 2 and 3, including Context Menu and Drag & Drop functionality. These components enable file management operations through an intuitive user interface.

## Component Hierarchy

```
EnhancedExplorerPanel
└── EnhancedExplorerWidget
    ├── SimpleSearchBar
    ├── EnhancedFileView
    │   └── ExplorerContextMenu
    └── Services
        ├── FileOperationsService
        ├── UndoRedoManager
        ├── FileNumberingService
        └── DragDropService
```

## Core Components

### EnhancedExplorerPanel

A panel component that integrates the enhanced explorer functionality into the application's panel system.

```python
class EnhancedExplorerPanel(PanelInterface):
    """
    Enhanced Explorer panel with context menu and drag & drop support.
    
    This panel extends the standard Explorer panel with:
    1. Context menu functionality for file operations
    2. Drag & drop capabilities for intuitive file management
    3. Integration with file operations services
    """
    
    # Signals
    file_opened = Signal(str)  # Emitted when a file is opened
    location_changed = Signal(str)  # Emitted when directory changes
    
    def __init__(self, parent: Optional[PanelInterface] = None):
        """
        Initialize the enhanced explorer panel.
        
        Args:
            parent: Optional parent panel
        """
        
    def on_activate(self):
        """Called when the panel is activated."""
        
    def on_deactivate(self):
        """Called when the panel is deactivated."""
```

### EnhancedExplorerWidget

Widget component providing enhanced file browsing capabilities with context menu and drag & drop support.

```python
class EnhancedExplorerWidget(QWidget):
    """
    Enhanced explorer widget with context menu support.
    
    Features:
    - All features of SimpleExplorerWidget
    - Context menu support with file operations
    - Drag & drop file transfer capabilities
    - Integration with undo/redo system
    """
    
    def __init__(self, parent=None):
        """
        Initialize the enhanced explorer widget.
        
        Args:
            parent: Optional parent widget
        """
    
    def _create_services(self):
        """Create and initialize the required services."""
        
    def _setup_ui(self):
        """Set up the user interface."""
        
    def _connect_signals(self):
        """Connect signals to slots."""
        
    def _load_initial_state(self):
        """Load the initial state of the explorer."""
        
    def _on_up_button_clicked(self):
        """Handle up button clicks to navigate to parent directory."""
        
    def _on_search_text_changed(self, text: str):
        """Handle search text changes."""
        
    def _on_file_activated(self, path: str):
        """Handle file activation events."""
        
    def _on_directory_changed(self, path: str):
        """Handle directory changed events."""
```

### EnhancedFileView

Extended file view component with context menu and drag & drop support.

```python
class EnhancedFileView(SimpleFileView):
    """
    Enhanced file view with context menu and drag & drop support.
    
    This class extends SimpleFileView to add context menu support,
    drag & drop capabilities, and integration with file operations.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the enhanced file view.
        
        Args:
            parent: Optional parent widget
        """
        
    def setup_context_menu(self, file_operations_service: FileOperationsService, 
                          undo_redo_manager: UndoRedoManager):
        """
        Set up the context menu manager.
        
        Args:
            file_operations_service: Service for file operations
            undo_redo_manager: Manager for undo/redo operations
        """
    
    def _show_context_menu(self, position: QPoint):
        """
        Show context menu at the specified position.
        
        Args:
            position: Position where the context menu should appear
        """
        
    def _show_properties(self, paths):
        """
        Show properties dialog for the given paths.
        
        Args:
            paths: List of paths to show properties for
        """
        
    def _show_open_with(self, paths):
        """
        Show 'Open With' dialog for the given paths.
        
        Args:
            paths: List of paths to show 'Open With' dialog for
        """
        
    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events for drag and drop.
        
        Args:
            event: Mouse event information
        """
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handle mouse move events to initiate drag operations.
        
        Args:
            event: Mouse event information
        """
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter events.
        
        Args:
            event: Drag enter event information
        """
        
    def dragMoveEvent(self, event: QDragMoveEvent):
        """
        Handle drag move events.
        
        Args:
            event: Drag move event information
        """
        
    def dropEvent(self, event: QDropEvent):
        """
        Handle drop events.
        
        Args:
            event: Drop event information
        """
        
    def _get_selected_paths(self) -> list:
        """
        Get the file paths of the selected items.
        
        Returns:
            List of selected file paths
        """
        
    def rootPath(self) -> str:
        """
        Get the current root path of the view.
        
        Returns:
            Current root directory path
        """
```

### ExplorerContextMenu

Provides context menu functionality for file management operations.

```python
class ExplorerContextMenu(QObject):
    """
    Context menu manager for the explorer view.
    
    Provides context menu functionality based on the selected items
    and integrates with the file operations service.
    """
    
    # Signals
    show_properties = Signal(list)  # List of paths
    show_open_with = Signal(list)  # List of paths
    
    def __init__(self, file_operations_service: FileOperationsService,
                undo_redo_manager: UndoRedoManager, parent=None):
        """
        Initialize the context menu manager.
        
        Args:
            file_operations_service: Service for file operations
            undo_redo_manager: Manager for undo/redo operations
            parent: Optional parent object
        """
        
    def create_menu(self, paths: List[str], parent: QWidget = None) -> QMenu:
        """
        Create a context menu for the specified paths.
        
        Args:
            paths: List of paths to create a menu for
            parent: Parent widget for the menu
            
        Returns:
            Configured QMenu instance
        """
        
    def _create_file_menu(self, paths: List[str], menu: QMenu):
        """
        Create menu items for file operations.
        
        Args:
            paths: List of paths
            menu: Menu to add items to
        """
        
    def _create_directory_menu(self, paths: List[str], menu: QMenu):
        """
        Create menu items for directory operations.
        
        Args:
            paths: List of paths
            menu: Menu to add items to
        """
        
    def _create_mixed_menu(self, paths: List[str], menu: QMenu):
        """
        Create menu items for mixed selection (files and directories).
        
        Args:
            paths: List of paths
            menu: Menu to add items to
        """
        
    def _add_common_actions(self, paths: List[str], menu: QMenu):
        """
        Add common actions to the menu.
        
        Args:
            paths: List of paths
            menu: Menu to add items to
        """
```

## Services

### FileOperationsService

Service for performing file system operations with undo/redo support.

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
    
    def __init__(self, parent=None):
        """Initialize the file operations service."""
        
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

### DragDropService

Service for handling drag and drop operations for file transfers.

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
    
    def __init__(self, file_operations_service: Optional[FileOperationsService] = None):
        """
        Initialize the DragDropService.
        
        Args:
            file_operations_service: Service for file operations
        """
        
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

### UndoRedoManager

Manages undo and redo operations for file system changes.

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
    
    def __init__(self, max_stack_size: int = 50, parent=None):
        """
        Initialize the UndoRedoManager.
        
        Args:
            max_stack_size: Maximum number of operations to track
            parent: Optional parent object
        """
        
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

### FileNumberingService

Service for handling file naming conflicts by automatically appending numbers.

```python
class FileNumberingService(QObject):
    """
    Service for handling file naming conflicts.
    
    This service provides automatic numbering for duplicate files,
    ensuring unique filenames when copying or creating new files.
    """
    
    def __init__(self, parent=None):
        """Initialize the file numbering service."""
        
    def get_unique_name(self, path: str) -> str:
        """
        Get a unique name for a file or directory.
        
        Args:
            path: Original path that may have naming conflicts
            
        Returns:
            Unique path with number appended if needed
        """
        
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

## Usage Examples

### Context Menu Example

```python
# Create services
file_operations = FileOperationsService()
undo_redo = UndoRedoManager()

# Set up the file view with context menu
file_view = EnhancedFileView()
file_view.setup_context_menu(file_operations, undo_redo)

# Connect to operation signals
file_operations.operationCompleted.connect(lambda op_type, sources, target: 
    print(f"Operation {op_type} completed"))
```

### Drag and Drop Example

```python
# Create services
file_operations = FileOperationsService()
drag_drop = DragDropService(file_operations)

# Connect to drag and drop signals
drag_drop.drag_started.connect(lambda paths: print(f"Dragging {len(paths)} items"))
drag_drop.drop_received.connect(lambda paths, target: 
    print(f"Dropped {len(paths)} items into {target}"))
```

### File Operations Example

```python
# Create the service
file_operations = FileOperationsService()

# Copy files
file_operations.copy_to_clipboard(["/path/to/file.txt"])
new_paths = file_operations.paste("/destination/")

# Create new folder and file
new_folder = file_operations.new_folder("/parent/directory", "My Folder")
new_file = file_operations.new_file(new_folder, "Notes.txt")

# Delete files
file_operations.delete([new_file], permanent=False)
```

## Error Handling

All services include comprehensive error handling:

1. **Graceful Failures**: Operations fail gracefully with descriptive error messages.
2. **Signal Notifications**: Error signals provide details about failed operations.
3. **Logging**: Detailed logging of operations and errors via the logging system.

## Thread Safety

These components are designed to be used from the main UI thread:
- File operations are performed synchronously
- Signals can be connected to handle UI updates after operations complete
- Long-running operations should be wrapped in background tasks if needed

## Performance Considerations

1. **Batch Operations**: File operations support batch processing for better performance.
2. **Lazy Loading**: File system information is loaded on-demand.
3. **Efficient Selection**: The selection model efficiently handles large numbers of items.
4. **Optimized Transfers**: File transfers use efficient copy/move operations where possible.

## Future Enhancements

1. **Background Operations**: Long-running operations in background threads with progress UI
2. **Cloud Storage Integration**: Support for cloud storage providers
3. **Thumbnail Generation**: Preview thumbnails for images and documents
4. **Custom Drag Visuals**: Enhanced drag feedback with thumbnails and item counts
