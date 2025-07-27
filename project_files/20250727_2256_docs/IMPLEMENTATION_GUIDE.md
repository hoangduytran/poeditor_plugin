# Core Services Implementation Guide

**Date**: July 27, 2025  
**Status**: Technical Implementation  
**Component**: File Operations Core Services

## Implementation Overview

This document provides detailed implementation guidance for the core services introduced in the Explorer Context Menu feature. It covers integration patterns, code examples, and best practices for working with these services.

## 1. Setting Up the Services

### Required Imports

```python
from core.plugin_manager import PluginManager
from services.file_numbering_service import FileNumberingService
from services.undo_redo_service import UndoRedoManager, FileOperation
from services.file_operations_service import FileOperationsService, OperationType
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from PySide6.QtCore import QObject, Signal, Slot, QUrl
```

### Initializing the Services

```python
# Initialize services
file_numbering_service = FileNumberingService()
undo_redo_manager = UndoRedoManager(max_history=100)
file_operations_service = FileOperationsService()

# Alternatively, retrieve from a plugin manager
plugin_manager = PluginManager.instance()
file_operations_service = plugin_manager.get_service("file_operations")
```

## 2. Handling File Operations

### Copy and Paste Workflow

```python
# Copy files to clipboard
paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
if file_operations_service.copy_to_clipboard(paths):
    print("Files copied to clipboard")
else:
    print("Failed to copy files to clipboard")
    
# Later, paste files to a target directory
if file_operations_service.can_paste("/path/to/destination"):
    new_paths = file_operations_service.paste("/path/to/destination")
    print(f"Files pasted to: {', '.join(new_paths)}")
else:
    print("Cannot paste here")
```

### Moving Files

```python
# Move files
source_paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
target_dir = "/path/to/new/location"
try:
    new_paths = file_operations_service.move_items(source_paths, target_dir)
    print(f"Files moved to: {', '.join(new_paths)}")
except Exception as e:
    print(f"Failed to move files: {str(e)}")
```

### Deleting Files

```python
# Delete files (to trash by default)
paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
try:
    if file_operations_service.delete_items(paths):
        print("Files deleted")
    else:
        print("Failed to delete files")
        
    # For permanent deletion
    file_operations_service.delete_items(paths, skip_trash=True)
except Exception as e:
    print(f"Failed to delete files: {str(e)}")
```

### Creating New Files and Folders

```python
# Create a new file
parent_dir = "/path/to/parent"
try:
    new_file_path = file_operations_service.create_new_file(parent_dir, "New Document.txt")
    print(f"New file created: {new_file_path}")
except Exception as e:
    print(f"Failed to create file: {str(e)}")
    
# Create a new folder
try:
    new_folder_path = file_operations_service.create_new_folder(parent_dir, "New Project")
    print(f"New folder created: {new_folder_path}")
except Exception as e:
    print(f"Failed to create folder: {str(e)}")
```

### Renaming Files

```python
# Rename a file
original_path = "/path/to/original.txt"
new_name = "renamed.txt"
try:
    new_path = file_operations_service.rename_item(original_path, new_name)
    print(f"File renamed to: {new_path}")
except Exception as e:
    print(f"Failed to rename file: {str(e)}")
```

### Duplicating Files

```python
# Duplicate a file
path = "/path/to/original.txt"
try:
    duplicate_path = file_operations_service.duplicate_item(path)
    print(f"File duplicated to: {duplicate_path}")
except Exception as e:
    print(f"Failed to duplicate file: {str(e)}")
```

## 3. Managing Undo and Redo

### Connecting to Undo/Redo UI Controls

```python
# Update UI controls based on undo/redo availability
def update_undo_redo_buttons():
    undo_button.setEnabled(file_operations_service.can_undo())
    redo_button.setEnabled(file_operations_service.can_redo())

# Connect to undo/redo events
file_operations_service.operationCompleted.connect(lambda *args: update_undo_redo_buttons())
file_operations_service.operationFailed.connect(lambda *args: update_undo_redo_buttons())

# Connect buttons to actions
undo_button.clicked.connect(file_operations_service.undo)
redo_button.clicked.connect(file_operations_service.redo)
```

### Manual Undo/Redo Management

```python
# Manually record an operation
operation = FileOperation(
    operation_type=OperationType.RENAME.value,
    source_paths=["/path/to/old_name.txt"],
    target_path="/path/to/new_name.txt",
    timestamp=datetime.now(),
    is_undoable=True,
    undo_data={
        "old_name": "old_name.txt",
        "new_name": "new_name.txt",
        "parent_dir": "/path/to/"
    }
)
undo_redo_manager.record_operation(operation)

# Perform undo/redo
if undo_redo_manager.can_undo():
    operation = undo_redo_manager.undo()
    if operation:
        print(f"Undoing {operation.operation_type}: {operation.source_paths} → {operation.target_path}")
        # Perform the actual undo action
        
if undo_redo_manager.can_redo():
    operation = undo_redo_manager.redo()
    if operation:
        print(f"Redoing {operation.operation_type}: {operation.source_paths} → {operation.target_path}")
        # Perform the actual redo action
```

## 4. Advanced File Numbering

### Custom Numbering Patterns

```python
# Generate a numbered name with custom pattern
path = "/path/to/document.txt"

# Default pattern (parentheses)
numbered_name = file_numbering_service.generate_numbered_name(path)
print(numbered_name)  # "/path/to/document (1).txt"

# Underscore pattern
numbered_name = file_numbering_service.generate_numbered_name(path, preferred_pattern="underscore")
print(numbered_name)  # "/path/to/document_1.txt"
```

### Finding Next Available Number

```python
# Find next available number in a sequence
directory = "/path/to/directory"
base_name = "report"

next_num = file_numbering_service.get_next_available_number(directory, base_name)
print(f"Next available number: {next_num}")

# Create a file with this number
new_name = f"{base_name} ({next_num}).txt"
new_path = os.path.join(directory, new_name)
```

### Extracting Pattern Components

```python
# Extract pattern components from a path
path = "/path/to/document (3).txt"
base_name, separator, number, extension = file_numbering_service.extract_pattern(path)

print(f"Base: {base_name}")      # "document"
print(f"Separator: {separator}")  # " ("
print(f"Number: {number}")        # 3
print(f"Extension: {extension}")  # ").txt"

# Rebuild with a different number
new_path = f"/path/to/{base_name}{separator}{number+1}{extension}"
print(new_path)  # "/path/to/document (4).txt"
```

## 5. Integration Examples

### Creating a Context Menu for File Operations

```python
from PySide6.QtWidgets import QMenu, QAction, QMessageBox
from PySide6.QtCore import Qt

class ExplorerContextMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_operations_service = FileOperationsService()
        
        # Selected paths in explorer
        self.selected_paths = []
        
        # Setup actions
        self.setup_actions()
        
    def setup_actions(self):
        # Copy action
        self.copy_action = QAction("Copy", self)
        self.copy_action.triggered.connect(self.on_copy)
        self.addAction(self.copy_action)
        
        # Cut action
        self.cut_action = QAction("Cut", self)
        self.cut_action.triggered.connect(self.on_cut)
        self.addAction(self.cut_action)
        
        # Paste action
        self.paste_action = QAction("Paste", self)
        self.paste_action.triggered.connect(self.on_paste)
        self.addAction(self.paste_action)
        
        self.addSeparator()
        
        # Delete action
        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(self.on_delete)
        self.addAction(self.delete_action)
        
        # Rename action
        self.rename_action = QAction("Rename", self)
        self.rename_action.triggered.connect(self.on_rename)
        self.addAction(self.rename_action)
        
        # Duplicate action
        self.duplicate_action = QAction("Duplicate", self)
        self.duplicate_action.triggered.connect(self.on_duplicate)
        self.addAction(self.duplicate_action)
        
    def show_for_paths(self, paths, pos, target_dir=None):
        self.selected_paths = paths
        self.target_dir = target_dir
        
        # Update paste action based on clipboard contents
        can_paste = self.file_operations_service.can_paste(target_dir) if target_dir else False
        self.paste_action.setEnabled(can_paste)
        
        # Disable rename if multiple items selected
        self.rename_action.setEnabled(len(paths) == 1)
        
        # Show the menu
        self.exec_(pos)
        
    def on_copy(self):
        if self.selected_paths:
            self.file_operations_service.copy_to_clipboard(self.selected_paths)
            
    def on_cut(self):
        if self.selected_paths:
            self.file_operations_service.cut_to_clipboard(self.selected_paths)
            
    def on_paste(self):
        if self.target_dir:
            try:
                self.file_operations_service.paste(self.target_dir)
            except Exception as e:
                QMessageBox.warning(self, "Paste Failed", f"Failed to paste files: {str(e)}")
                
    def on_delete(self):
        if self.selected_paths:
            try:
                self.file_operations_service.delete_items(self.selected_paths)
            except Exception as e:
                QMessageBox.warning(self, "Delete Failed", f"Failed to delete files: {str(e)}")
                
    def on_rename(self):
        if len(self.selected_paths) == 1:
            # Show rename dialog (implementation not shown)
            new_name = self.show_rename_dialog(self.selected_paths[0])
            if new_name:
                try:
                    self.file_operations_service.rename_item(self.selected_paths[0], new_name)
                except Exception as e:
                    QMessageBox.warning(self, "Rename Failed", f"Failed to rename file: {str(e)}")
                    
    def on_duplicate(self):
        if len(self.selected_paths) == 1:
            try:
                self.file_operations_service.duplicate_item(self.selected_paths[0])
            except Exception as e:
                QMessageBox.warning(self, "Duplicate Failed", f"Failed to duplicate file: {str(e)}")
                
    def show_rename_dialog(self, path):
        # Implementation of rename dialog
        # Return new name or None if canceled
        pass
```

### Integrating with a File Explorer View

```python
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import Qt

class ExplorerView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_operations_service = FileOperationsService()
        
        # Connect to signals
        self.file_operations_service.operationCompleted.connect(self.on_operation_completed)
        self.file_operations_service.operationFailed.connect(self.on_operation_failed)
        
        # Setup context menu
        self.context_menu = ExplorerContextMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, pos):
        # Get selected paths
        selected_paths = self.get_selected_paths()
        
        # Get target directory (for paste operation)
        target_dir = self.get_directory_at_position(pos)
        
        # Show context menu
        self.context_menu.show_for_paths(selected_paths, self.mapToGlobal(pos), target_dir)
        
    def get_selected_paths(self):
        # Implementation to get selected paths from model
        # Returns a list of absolute paths
        pass
        
    def get_directory_at_position(self, pos):
        # Implementation to get directory path at position
        # Returns absolute path or None
        pass
        
    def on_operation_completed(self, op_type, sources, target):
        # Refresh view after operation
        self.model().refresh()
        
        # Show status message
        self.window().statusBar().showMessage(f"{op_type.capitalize()} operation completed", 3000)
        
    def on_operation_failed(self, op_type, sources, error):
        # Show error message
        self.window().statusBar().showMessage(f"{op_type.capitalize()} operation failed: {error}", 5000)
        
    def keyPressEvent(self, event):
        # Handle keyboard shortcuts
        if event.matches(QKeySequence.Copy):
            selected_paths = self.get_selected_paths()
            if selected_paths:
                self.file_operations_service.copy_to_clipboard(selected_paths)
                event.accept()
                return
        elif event.matches(QKeySequence.Cut):
            selected_paths = self.get_selected_paths()
            if selected_paths:
                self.file_operations_service.cut_to_clipboard(selected_paths)
                event.accept()
                return
        elif event.matches(QKeySequence.Paste):
            target_dir = self.get_current_directory()
            if target_dir and self.file_operations_service.can_paste(target_dir):
                self.file_operations_service.paste(target_dir)
                event.accept()
                return
        elif event.key() == Qt.Key_Delete:
            selected_paths = self.get_selected_paths()
            if selected_paths:
                self.file_operations_service.delete_items(selected_paths)
                event.accept()
                return
                
        # Call base implementation for unhandled keys
        super().keyPressEvent(event)
        
    def get_current_directory(self):
        # Implementation to get current directory path
        # Returns absolute path or None
        pass
```

### Handling Progress and Notifications

```python
from PySide6.QtWidgets import QProgressDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer

class FileOperationsHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_operations_service = FileOperationsService()
        
        # Connect to signals
        self.file_operations_service.operationStarted.connect(self.on_operation_started)
        self.file_operations_service.operationCompleted.connect(self.on_operation_completed)
        self.file_operations_service.operationFailed.connect(self.on_operation_failed)
        
        # Progress dialog
        self.progress_dialog = None
        
    def on_operation_started(self, op_type, sources):
        # Show progress dialog for longer operations
        if op_type in ["copy", "move", "delete"] and len(sources) > 5:
            self.progress_dialog = QProgressDialog(
                f"{op_type.capitalize()} in progress...",
                "Cancel",
                0,
                0,
                self.parent()
            )
            self.progress_dialog.setWindowTitle(f"{op_type.capitalize()} Files")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setCancelButton(None)  # No cancel for now
            self.progress_dialog.show()
            
    def on_operation_completed(self, op_type, sources, target):
        # Close progress dialog if shown
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
            
        # Show notification for significant operations
        if op_type in ["copy", "move", "delete"] and len(sources) > 1:
            self.show_notification(
                f"{op_type.capitalize()} Completed",
                f"{len(sources)} items {op_type}d successfully."
            )
            
    def on_operation_failed(self, op_type, sources, error):
        # Close progress dialog if shown
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
            
        # Show error message
        QMessageBox.warning(
            self.parent(),
            f"{op_type.capitalize()} Failed",
            f"Failed to {op_type} {len(sources)} item(s).\n\nError: {error}"
        )
        
    def show_notification(self, title, message):
        # Implementation of notification system
        # Could use system notifications or in-app toast
        pass
```

## 6. Best Practices

### Error Handling

Always wrap file operations in try-except blocks to catch potential errors:

```python
try:
    result = file_operations_service.some_operation(...)
    # Handle success
except Exception as e:
    # Handle error
    print(f"Operation failed: {str(e)}")
```

### Resource Management

Ensure resources are properly released after operations:

```python
try:
    # Perform operations
    pass
finally:
    # Clean up resources if needed
    file_operations_service.clear_clipboard()  # If appropriate
```

### UI Responsiveness

For potentially long-running operations, use signals and slots for asynchronous handling:

```python
# In your UI class
def __init__(self):
    # Connect to operation signals
    file_operations_service.operationStarted.connect(self.show_progress)
    file_operations_service.operationCompleted.connect(self.hide_progress)
    file_operations_service.operationFailed.connect(self.hide_progress)
    
def show_progress(self, op_type, sources):
    # Show progress indicator
    self.statusBar().showMessage(f"{op_type.capitalize()} in progress...")
    
def hide_progress(self, *args):
    # Hide progress indicator
    self.statusBar().clearMessage()
```

### Clipboard Management

Be mindful of clipboard usage to prevent resource leaks:

```python
# Clear clipboard when no longer needed
def on_application_close(self):
    file_operations_service.clear_clipboard()
```

## 7. Testing the Services

### Unit Testing FileNumberingService

```python
import unittest
import os
import tempfile
from services.file_numbering_service import FileNumberingService

class TestFileNumberingService(unittest.TestCase):
    def setUp(self):
        self.service = FileNumberingService()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_extract_pattern(self):
        # Test various pattern formats
        base, sep, num, ext = self.service.extract_pattern("/path/to/file (1).txt")
        self.assertEqual(base, "file")
        self.assertEqual(sep, " (")
        self.assertEqual(num, 1)
        self.assertEqual(ext, ").txt")
        
        base, sep, num, ext = self.service.extract_pattern("/path/to/file_1.txt")
        self.assertEqual(base, "file")
        self.assertEqual(sep, "_")
        self.assertEqual(num, 1)
        self.assertEqual(ext, ".txt")
        
    def test_generate_numbered_name(self):
        # Create test files
        with open(os.path.join(self.temp_dir, "file.txt"), "w") as f:
            f.write("test")
            
        # Test generation of numbered name
        new_name = self.service.generate_numbered_name(os.path.join(self.temp_dir, "file.txt"))
        self.assertEqual(os.path.basename(new_name), "file (1).txt")
        
        # Create the new file
        with open(new_name, "w") as f:
            f.write("test")
            
        # Generate another name
        another_name = self.service.generate_numbered_name(os.path.join(self.temp_dir, "file.txt"))
        self.assertEqual(os.path.basename(another_name), "file (2).txt")
        
    def test_get_next_available_number(self):
        # Create test files
        for i in range(1, 4):
            with open(os.path.join(self.temp_dir, f"file ({i}).txt"), "w") as f:
                f.write("test")
                
        # Test finding next number
        next_num = self.service.get_next_available_number(self.temp_dir, "file", "parentheses")
        self.assertEqual(next_num, 4)
```

### Integration Testing with All Services

```python
import unittest
import os
import tempfile
import shutil
from services.file_numbering_service import FileNumberingService
from services.undo_redo_service import UndoRedoManager
from services.file_operations_service import FileOperationsService

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.target_dir = os.path.join(self.temp_dir, "target")
        
        # Create directories
        os.mkdir(self.source_dir)
        os.mkdir(self.target_dir)
        
        # Create test files
        self.test_files = []
        for i in range(3):
            path = os.path.join(self.source_dir, f"test_file_{i}.txt")
            with open(path, "w") as f:
                f.write(f"Test content {i}")
            self.test_files.append(path)
            
        # Initialize services
        self.file_operations_service = FileOperationsService()
        
    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)
        
    def test_copy_paste_undo_redo(self):
        # Copy files to clipboard
        self.file_operations_service.copy_to_clipboard(self.test_files)
        
        # Paste to target directory
        new_paths = self.file_operations_service.paste(self.target_dir)
        self.assertEqual(len(new_paths), len(self.test_files))
        
        # Verify files were copied
        for path in new_paths:
            self.assertTrue(os.path.exists(path))
            
        # Undo the paste operation
        self.assertTrue(self.file_operations_service.can_undo())
        self.file_operations_service.undo()
        
        # Verify files were removed
        for path in new_paths:
            self.assertFalse(os.path.exists(path))
            
        # Redo the paste operation
        self.assertTrue(self.file_operations_service.can_redo())
        self.file_operations_service.redo()
        
        # Verify files were recreated
        for path in new_paths:
            self.assertTrue(os.path.exists(path))
            
    def test_rename_undo_redo(self):
        # Rename a file
        original_path = self.test_files[0]
        original_name = os.path.basename(original_path)
        new_name = "renamed_file.txt"
        
        new_path = self.file_operations_service.rename_item(original_path, new_name)
        self.assertTrue(os.path.exists(new_path))
        self.assertFalse(os.path.exists(original_path))
        
        # Undo the rename
        self.file_operations_service.undo()
        self.assertTrue(os.path.exists(original_path))
        self.assertFalse(os.path.exists(new_path))
        
        # Redo the rename
        self.file_operations_service.redo()
        self.assertTrue(os.path.exists(new_path))
        self.assertFalse(os.path.exists(original_path))
```

## 8. Common Issues and Solutions

### Issue: File Access Errors

**Problem**: Operations fail due to file access permissions or locks.

**Solution**: 
1. Check file permissions before operations
2. Add retry logic for temporary locks
3. Handle specific exceptions with clear error messages

```python
def safe_operation(func, *args, **kwargs):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            return func(*args, **kwargs)
        except PermissionError:
            return None, "Permission denied. Check file permissions."
        except OSError as e:
            if "being used by another process" in str(e):
                retry_count += 1
                time.sleep(0.5)  # Wait before retry
            else:
                return None, f"Operation failed: {str(e)}"
    
    return None, "File is locked by another process."
```

### Issue: Undo/Redo Stack Overflow

**Problem**: Memory usage increases with large operation history.

**Solution**:
1. Limit history size (UndoRedoManager already has max_history parameter)
2. Merge similar consecutive operations
3. Periodically clear history for very large operations

```python
# Set a reasonable history limit
undo_redo_manager = UndoRedoManager(max_history=50)

# Periodically clear history for large operations
def handle_large_operation(paths):
    if len(paths) > 100:
        # Clear history before operation to prevent memory issues
        undo_redo_manager.clear_history()
        # Inform user that this operation is too large for undo
        QMessageBox.information(None, "Large Operation", 
                               "This operation involves too many files to support undo/redo.")
```

### Issue: Naming Conflicts

**Problem**: Generated file names may still conflict in certain edge cases.

**Solution**:
1. Add timestamp to generated names as fallback
2. Implement conflict resolution dialog for user decision
3. Add more robust pattern detection

```python
def resolve_name_conflict(path):
    # Try standard numbering first
    numbered_name = file_numbering_service.generate_numbered_name(path)
    
    # If it still exists (edge case), add timestamp
    if os.path.exists(numbered_name):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        base_name, extension = os.path.splitext(path)
        return f"{base_name}_{timestamp}{extension}"
        
    return numbered_name
```

## 9. Performance Considerations

### Batch Operations

For better performance with multiple files, batch operations where possible:

```python
# Instead of copying files one by one
for path in paths:
    file_operations_service.copy_to_clipboard([path])
    file_operations_service.paste(target_dir)
    
# Copy all files at once
file_operations_service.copy_to_clipboard(paths)
file_operations_service.paste(target_dir)
```

### Large File Handling

When working with large files, consider progress reporting:

```python
def on_operation_started(self, op_type, sources):
    total_size = sum(os.path.getsize(path) for path in sources if os.path.exists(path))
    
    # Show progress for large operations
    if total_size > 10 * 1024 * 1024:  # 10 MB
        self.progress_dialog = QProgressDialog(
            f"{op_type.capitalize()} large files...",
            "Cancel",
            0,
            100,
            self.parent()
        )
        self.progress_dialog.show()
```

## 10. Security Considerations

### Safe File Deletion

Always use safe deletion methods:

```python
# Use send2trash for safer deletion
import send2trash

def safe_delete(path):
    try:
        send2trash.send2trash(path)
        return True
    except Exception as e:
        print(f"Failed to safely delete {path}: {str(e)}")
        # Ask user if they want to permanently delete
        # ...
        return False
```

### Path Traversal Prevention

Validate paths to prevent path traversal:

```python
def is_safe_path(base_path, path):
    # Resolve to absolute paths
    base_path = os.path.abspath(base_path)
    path = os.path.abspath(path)
    
    # Check if path is within base_path
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, path])
    
# Usage
target_dir = "/path/to/target"
for path in paths:
    if not is_safe_path(target_dir, path):
        raise SecurityError(f"Invalid path: {path}")
```
