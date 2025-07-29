# Enhanced Explorer Developer Quick Reference

## Component Quick Reference

### Core Components

| Component | Purpose | Key Methods |
|-----------|---------|------------|
| `EnhancedExplorerPanel` | Panel integration | `on_activate()`, `on_deactivate()` |
| `EnhancedExplorerWidget` | Main widget | `_create_services()`, `_setup_ui()` |
| `EnhancedFileView` | File display | `setup_context_menu()`, `_show_context_menu()` |
| `ExplorerContextMenu` | Context menu manager | `create_menu()`, `_create_file_menu()` |

### Services

| Service | Purpose | Key Methods |
|---------|---------|------------|
| `FileOperationsService` | File operations | `copy_to_clipboard()`, `paste()`, `delete()`, `rename()` |
| `UndoRedoManager` | Operation history | `push_operation()`, `undo()`, `redo()` |
| `DragDropService` | Drag and drop | `start_drag()`, `process_drop()` |
| `FileNumberingService` | Name conflict resolution | `get_unique_name()` |

## Key Signal Connections

### FileOperationsService Signals

```python
# Connect to operation signals
file_operations.operationStarted.connect(on_operation_started)
file_operations.operationCompleted.connect(on_operation_completed)
file_operations.operationFailed.connect(on_operation_failed)
file_operations.clipboardChanged.connect(on_clipboard_changed)

# Signal handlers
def on_operation_started(operation_type, paths):
    # Handle operation start (show progress UI, etc.)
    
def on_operation_completed(operation_type, source_paths, target_path):
    # Handle operation completion (refresh UI, show notification, etc.)
    
def on_operation_failed(operation_type, paths, error_message):
    # Handle operation failure (show error, log, etc.)
    
def on_clipboard_changed():
    # Update paste action availability
```

### UndoRedoManager Signals

```python
# Connect to undo/redo signals
undo_redo.undoAvailable.connect(on_undo_available)
undo_redo.redoAvailable.connect(on_redo_available)
undo_redo.operationUndone.connect(on_operation_undone)
undo_redo.operationRedone.connect(on_operation_redone)
```

### DragDropService Signals

```python
# Connect to drag/drop signals
drag_drop.drag_started.connect(on_drag_started)
drag_drop.drop_received.connect(on_drop_received)
drag_drop.drag_completed.connect(on_drag_completed)
```

## Common Code Snippets

### Initialize Explorer Widget

```python
# Create the explorer widget
explorer = EnhancedExplorerWidget()

# Connect to signals
explorer.file_view.file_activated.connect(on_file_activated)
explorer.file_view.directory_changed.connect(on_directory_changed)
```

### Perform File Operations

```python
# Get the file operations service
file_ops = explorer.file_operations_service

# Copy files
file_ops.copy_to_clipboard(["/path/to/file1.txt", "/path/to/file2.txt"])

# Cut files
file_ops.cut_to_clipboard(["/path/to/file3.txt"])

# Paste files to a directory
new_paths = file_ops.paste("/target/directory")

# Delete files
file_ops.delete(["/path/to/file4.txt"], permanent=False)

# Rename a file
new_path = file_ops.rename("/path/to/file.txt", "new_name.txt")

# Create new items
new_dir = file_ops.new_folder("/parent/dir", "New Folder")
new_file = file_ops.new_file("/parent/dir", "New File.txt")
```

### Work with Undo/Redo

```python
# Get the undo/redo manager
undo_redo = explorer.undo_redo_manager

# Check if undo/redo is available
can_undo = undo_redo.can_undo()
can_redo = undo_redo.can_redo()

# Perform undo/redo
if can_undo:
    undo_redo.undo()
    
if can_redo:
    undo_redo.redo()
```

### Custom Context Menu

```python
# Create a custom context menu handler
def my_custom_context_menu(menu, paths):
    # Add custom actions
    custom_action = menu.addAction("Custom Action")
    custom_action.triggered.connect(lambda: handle_custom_action(paths))
    
    # Add separator
    menu.addSeparator()
    
# Extend the context menu
original_create_menu = explorer.file_view.context_menu_manager.create_menu

def extended_create_menu(paths, parent=None):
    menu = original_create_menu(paths, parent)
    my_custom_context_menu(menu, paths)
    return menu
    
explorer.file_view.context_menu_manager.create_menu = extended_create_menu
```

### Handle Drag and Drop

```python
# Connect to drag/drop events
def on_drag_started(paths):
    print(f"Started dragging {len(paths)} items")
    
def on_drop_received(paths, target):
    print(f"Dropped {len(paths)} items to {target}")
    
drag_drop_service = explorer.file_view.drag_drop_service
drag_drop_service.drag_started.connect(on_drag_started)
drag_drop_service.drop_received.connect(on_drop_received)
```

## Testing Components

### Testing File Operations

```python
import unittest
from PySide6.QtWidgets import QApplication
from services.file_operations_service import FileOperationsService

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.service = FileOperationsService()
        
    def test_copy_paste(self):
        # Test copy/paste operations
        self.service.copy_to_clipboard(["/test/file.txt"])
        new_paths = self.service.paste("/destination")
        self.assertEqual(len(new_paths), 1)
        
    # Add more tests...
```

### Testing Drag and Drop

```python
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QMimeData, Qt
from services.drag_drop_service import DragDropService
from services.file_operations_service import FileOperationsService

class TestDragDrop(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.file_ops = FileOperationsService()
        self.drag_drop = DragDropService(self.file_ops)
        
    def test_process_drop(self):
        # Create mime data
        mime_data = QMimeData()
        mime_data.setText("/test/file.txt")
        
        # Process drop
        result = self.drag_drop.process_drop(
            mime_data, 
            "/destination", 
            Qt.DropAction.CopyAction
        )
        
        self.assertTrue(result)
        
    # Add more tests...
```

## Customization Points

### Custom File View

```python
from widgets.enhanced_file_view import EnhancedFileView

class MyCustomFileView(EnhancedFileView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Add custom initialization
        
    def _show_context_menu(self, position):
        # Override to customize context menu behavior
        super()._show_context_menu(position)
        
    # Override more methods as needed
```

### Custom FileOperationsService

```python
from services.file_operations_service import FileOperationsService

class MyCustomFileOperations(FileOperationsService):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Add custom initialization
        
    def delete(self, paths, permanent=False):
        # Override to customize delete behavior
        print(f"Custom delete implementation for {len(paths)} items")
        return super().delete(paths, permanent)
        
    # Override more methods as needed
```

## Best Practices

1. **Service Initialization**:
   - Create services early in the component lifecycle
   - Pass services to components that need them
   - Avoid creating multiple instances of the same service

2. **Signal Connections**:
   - Connect to signals after component initialization
   - Use descriptive slot method names
   - Disconnect signals when components are destroyed

3. **Error Handling**:
   - Connect to operationFailed signals
   - Log errors with appropriate severity
   - Show user-friendly error messages

4. **Resource Management**:
   - Ensure proper cleanup in destructors
   - Release file handles promptly
   - Use context managers where appropriate

5. **User Interface Updates**:
   - Update UI after operations complete
   - Use signals to keep UI responsive
   - Consider throttling updates during bulk operations

## Common Issues and Solutions

### Issue: Context Menu Not Appearing

**Possible Causes and Solutions:**
- Ensure `setContextMenuPolicy(Qt.CustomContextMenu)` is set
- Verify `customContextMenuRequested` signal is connected
- Check if menu creation returns a valid menu

### Issue: Drag and Drop Not Working

**Possible Causes and Solutions:**
- Ensure `setDragEnabled(True)` and `setAcceptDrops(True)` are set
- Override `mousePressEvent`, `mouseMoveEvent`, and `dropEvent`
- Check MIME data creation and handling

### Issue: File Operations Failing

**Possible Causes and Solutions:**
- Check file permissions
- Verify paths are valid
- Handle exceptions in service methods
- Check for naming conflicts
