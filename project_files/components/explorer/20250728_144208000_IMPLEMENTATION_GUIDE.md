# Enhanced Explorer Implementation Guide

**Date:** July 28, 2025  
**Component:** Enhanced Explorer Panel  
**Version:** 2.0.0  
**Status:** Production

## Introduction

This guide provides detailed implementation instructions for developers who need to extend, maintain, or integrate the Enhanced Explorer components into other parts of the application. It covers the implementation details of Phases 2 and 3, focusing on the context menu and drag & drop functionality.

## Implementation Phases

The Enhanced Explorer was implemented in multiple phases:

1. **Phase 1: Basic Explorer** - Core browsing functionality
2. **Phase 2: Context Menu** - Right-click menu operations
3. **Phase 3: Drag & Drop** - Intuitive file movement and copying
4. **Phase 4: Advanced Filtering** (Planned) - Improved search and filtering

This guide focuses on Phases 2 and 3.

## Phase 2: Context Menu Implementation

### Architecture

The context menu implementation follows a service-oriented architecture:

```
EnhancedFileView → ExplorerContextMenu → FileOperationsService → UndoRedoManager
```

### Core Components

#### 1. ExplorerContextMenu Class

This class manages the creation and configuration of context menus based on the selected items:

```python
class ExplorerContextMenu(QObject):
    """Context menu manager for the explorer view."""
    
    # Implementation notes:
    # - Uses composition with FileOperationsService
    # - Creates different menus based on selection type
    # - Emits signals for operations that need special handling
```

#### 2. FileOperationsService Class

This service provides a unified API for all file operations:

```python
class FileOperationsService(QObject):
    """Service for handling file operations in the Explorer."""
    
    # Implementation notes:
    # - Centralizes all file operations
    # - Provides proper error handling
    # - Emits signals for operation status
    # - Integrates with undo/redo system
```

#### 3. UndoRedoManager Class

This class manages operation history for undo/redo functionality:

```python
class UndoRedoManager(QObject):
    """Manager for undo and redo operations."""
    
    # Implementation notes:
    # - Stack-based implementation
    # - Tracks operations with their metadata
    # - Handles undo/redo logic for each operation type
```

### Implementation Steps

To implement context menu functionality:

1. **Set up services**:
   ```python
   file_operations = FileOperationsService()
   undo_redo = UndoRedoManager()
   ```

2. **Configure the enhanced file view**:
   ```python
   file_view = EnhancedFileView()
   file_view.setup_context_menu(file_operations, undo_redo)
   ```

3. **Connect to signals** for status updates:
   ```python
   file_operations.operationCompleted.connect(on_operation_completed)
   file_operations.operationFailed.connect(on_operation_failed)
   ```

### Extending Context Menu

To add a new context menu action:

1. **Identify the appropriate menu method** in `ExplorerContextMenu`:
   - `_create_file_menu()` for file-specific actions
   - `_create_directory_menu()` for directory-specific actions
   - `_create_mixed_menu()` for mixed selection actions
   - `_add_common_actions()` for actions that apply to all types

2. **Add the new action**:
   ```python
   def _create_file_menu(self, paths: List[str], menu: QMenu):
       # Existing code...
       
       # Add custom action
       custom_action = menu.addAction("My Custom Action")
       custom_action.triggered.connect(lambda: self._handle_custom_action(paths))
       
       # Continue with existing code...
   ```

3. **Implement the handler method**:
   ```python
   def _handle_custom_action(self, paths: List[str]):
       # Implement custom action logic
       for path in paths:
           # Do something with each path
           pass
   ```

## Phase 3: Drag & Drop Implementation

### Architecture

The drag and drop implementation extends the service-oriented architecture:

```
EnhancedFileView → DragDropService → FileOperationsService
```

### Core Components

#### 1. DragDropService Class

This service manages drag and drop operations:

```python
class DragDropService(QObject):
    """Service for handling drag and drop operations."""
    
    # Implementation notes:
    # - Manages drag start/end events
    # - Processes drop data
    # - Delegates to FileOperationsService for actual operations
```

#### 2. Enhanced Event Handlers

The `EnhancedFileView` class implements several event handlers:

```python
class EnhancedFileView(SimpleFileView):
    """Enhanced file view with context menu and drag & drop support."""
    
    # Implementation notes:
    # - Overrides mousePressEvent/mouseMoveEvent to detect drags
    # - Implements dragEnterEvent/dragMoveEvent/dropEvent for drops
    # - Uses DragDropService for operation processing
```

### Implementation Steps

To implement drag and drop functionality:

1. **Create and configure services**:
   ```python
   file_operations = FileOperationsService()
   drag_drop = DragDropService(file_operations)
   ```

2. **Set up the file view**:
   ```python
   file_view = EnhancedFileView()
   file_view.setDragEnabled(True)
   file_view.setAcceptDrops(True)
   file_view.setDropIndicatorShown(True)
   file_view.setDragDropMode(QTreeView.DragDrop)
   ```

3. **Connect to drag drop signals**:
   ```python
   drag_drop.drag_started.connect(on_drag_started)
   drag_drop.drop_received.connect(on_drop_received)
   drag_drop.drag_completed.connect(on_drag_completed)
   ```

### Event Flow

The drag and drop event flow follows this sequence:

1. **Mouse Press**: User clicks on a file/folder
   ```python
   def mousePressEvent(self, event):
       if event.button() == Qt.LeftButton:
           self.drag_start_position = event.pos()
       super().mousePressEvent(event)
   ```

2. **Mouse Move**: User drags with mouse button held down
   ```python
   def mouseMoveEvent(self, event):
       # Check if drag should start
       # If yes, collect selected paths
       self.drag_drop_service.start_drag(paths, event.pos(), self)
   ```

3. **Drag Enter**: Cursor enters a potential drop target
   ```python
   def dragEnterEvent(self, event):
       # Accept or reject the drag based on mime data
       if event.mimeData().hasUrls():
           event.acceptProposedAction()
   ```

4. **Drag Move**: Cursor moves over potential drop targets
   ```python
   def dragMoveEvent(self, event):
       # Validate drop target and provide visual feedback
       index = self.indexAt(event.pos())
       # Accept/reject based on target type
   ```

5. **Drop**: User releases mouse button to complete drag
   ```python
   def dropEvent(self, event):
       # Get target directory
       # Process the drop with service
       self.drag_drop_service.process_drop(event.mimeData(), path, event.proposedAction())
   ```

### Extending Drag & Drop

To customize drag and drop behavior:

1. **Extend MIME data handling** in `DragDropService.start_drag()`:
   ```python
   def start_drag(self, source_paths, start_pos, parent):
       # Existing code...
       
       # Add custom mime data
       mime_data.setData("application/x-custom-format", custom_data)
       
       # Continue with existing code...
   ```

2. **Customize drop processing** in `DragDropService.process_drop()`:
   ```python
   def process_drop(self, mime_data, target_dir, suggested_action):
       # Existing code...
       
       # Handle custom formats
       if mime_data.hasFormat("application/x-custom-format"):
           custom_data = mime_data.data("application/x-custom-format")
           return self._handle_custom_drop(custom_data, target_dir)
       
       # Continue with existing code...
   ```

## Integration Points

### Integrating with Other Panels

To integrate the Enhanced Explorer with other panels:

1. **Share services** between components:
   ```python
   # Create shared services
   file_operations = FileOperationsService()
   undo_redo = UndoRedoManager()
   
   # Pass to both explorer and another component
   explorer_panel.setup_services(file_operations, undo_redo)
   other_panel.setup_services(file_operations, undo_redo)
   ```

2. **Connect signals** between components:
   ```python
   # When explorer performs operations, notify other components
   explorer_panel.file_operations.operationCompleted.connect(
       other_panel.on_file_operation_completed)
   ```

### Integrating with Main Application

To integrate the Enhanced Explorer with the main application:

1. **Register the panel** with the panel manager:
   ```python
   panel_manager.register_panel(
       "explorer",
       EnhancedExplorerPanel,
       "Explorer",
       "explorer_active.svg",
       "explorer_inactive.svg"
   )
   ```

2. **Connect to application-level signals**:
   ```python
   app.file_opened.connect(explorer_panel.on_file_opened)
   explorer_panel.file_opened.connect(app.open_file)
   ```

## Testing

### Testing Context Menu

```python
def test_context_menu_creation():
    """Test that context menu is created correctly for file selection."""
    # Setup
    file_operations = FileOperationsService()
    undo_redo = UndoRedoManager()
    context_menu = ExplorerContextMenu(file_operations, undo_redo)
    
    # Test
    menu = context_menu.create_menu(["/path/to/file.txt"])
    
    # Verify
    assert menu is not None
    # Check for expected actions
    action_texts = [action.text() for action in menu.actions()]
    assert "Open" in action_texts
    assert "Copy" in action_texts
    # etc.
```

### Testing Drag & Drop

```python
def test_drag_drop_service():
    """Test that drag drop service processes drops correctly."""
    # Setup
    file_operations = FileOperationsService()
    drag_drop = DragDropService(file_operations)
    
    # Create mime data for testing
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("/path/to/source/file.txt")])
    
    # Test
    result = drag_drop.process_drop(
        mime_data,
        "/path/to/target/",
        Qt.CopyAction
    )
    
    # Verify
    assert result is True
    # Check that file was copied to target
    assert os.path.exists("/path/to/target/file.txt")
```

## Troubleshooting

### Common Issues

1. **Context Menu Not Showing**
   - Check that `setContextMenuPolicy(Qt.CustomContextMenu)` is set
   - Verify that `customContextMenuRequested` is connected to handler
   - Check that selected paths are valid

2. **Drag & Drop Not Working**
   - Verify that `setDragEnabled(True)` and `setAcceptDrops(True)` are set
   - Check that `mouseMoveEvent` calculates drag distance correctly
   - Ensure MIME data is properly formatted

3. **File Operations Failing**
   - Check error signals from FileOperationsService
   - Verify file permissions on source and target paths
   - Check for name conflicts and numbering service behavior

## Performance Optimization

For better performance when handling large file sets:

1. **Batch Processing**:
   ```python
   # Process items in batches for better responsiveness
   def process_large_selection(paths):
       batch_size = 100
       for i in range(0, len(paths), batch_size):
           batch = paths[i:i+batch_size]
           process_batch(batch)
           QApplication.processEvents()  # Keep UI responsive
   ```

2. **Delayed Operations**:
   ```python
   # For expensive operations, use a timer to avoid UI freezing
   def setup_delayed_operation():
       timer = QTimer()
       timer.setSingleShot(True)
       timer.timeout.connect(perform_expensive_operation)
       timer.start(100)  # Short delay to let UI update first
   ```

## Best Practices

1. **Service Composition**: Use composition over inheritance when extending functionality
2. **Clear Responsibility**: Each component should have a single responsibility
3. **Error Handling**: Always handle errors gracefully and inform the user
4. **Signal-Slot**: Use signals and slots for loose coupling between components
5. **Testing**: Write unit tests for all components, especially services

## Future Enhancement Ideas

1. **Background Operations**: Move long-running operations to background threads
2. **Progress UI**: Add progress dialogs for operations on large files/folders
3. **Custom Drag Visuals**: Implement custom drag pixmaps for better feedback
4. **Keyboard Navigation**: Enhance keyboard shortcuts for power users
5. **Extensible Actions**: Create a plugin system for custom context menu actions

## References

- [Qt Documentation: Drag and Drop](https://doc.qt.io/qt-6/dnd.html)
- [Qt Documentation: Model/View Programming](https://doc.qt.io/qt-6/model-view-programming.html)
- [Python Documentation: shutil](https://docs.python.org/3/library/shutil.html)
- [Explorer API Documentation](./EXPLORER_API_DOCUMENTATION.md)
- [Enhanced Explorer Technical Design](./ENHANCED_EXPLORER_TECHNICAL_DESIGN.md)
