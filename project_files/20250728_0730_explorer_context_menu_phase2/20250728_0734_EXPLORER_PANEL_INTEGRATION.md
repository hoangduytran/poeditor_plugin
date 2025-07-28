# Explorer Panel Integration

**Date**: July 28, 2025, 07:34  
**Component**: Explorer Context Menu - Explorer Panel Integration  
**Status**: Technical Design  
**Priority**: High

## Overview

This document outlines how the Explorer Context Menu will be integrated with the existing Explorer panel. It covers the attachment of the context menu to the tree view, handling of selection events, and coordination with other Explorer panel features.

## Integration Points

The Explorer panel integration involves several key components:

1. **Tree View Context Menu**: Attaching the context menu to the Explorer tree view
2. **Selection Handling**: Tracking and interpreting user selections
3. **Item Type Detection**: Determining the types of selected items
4. **Event Coordination**: Coordinating with other Explorer panel events

## Tree View Context Menu Integration

### Attachment Method

The context menu will be attached to the tree view using Qt's context menu event system:

```python
class ExplorerTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Create context menu manager
        self.context_menu_manager = ContextMenuManager(
            file_operations_service=self.file_operations_service,
            undo_redo_manager=self.undo_redo_manager,
            notification_service=self.notification_service
        )
        
    def _show_context_menu(self, position):
        # Get the item under the cursor
        index = self.indexAt(position)
        
        # If clicking on empty area, deselect and show folder menu
        if not index.isValid():
            self.clearSelection()
            # Get the current directory
            current_dir = self.model().rootPath()
            menu = self.context_menu_manager.create_folder_menu(current_dir)
        else:
            # Ensure the item under cursor is selected
            if not self.selectionModel().isSelected(index):
                self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
                
            # Get all selected items
            selected_items = self._get_selected_items()
            menu = self.context_menu_manager.create_menu(selected_items)
        
        # Show the menu at the requested position
        menu.exec_(self.viewport().mapToGlobal(position))
```

### Menu Types

The context menu will adapt based on the selection:

1. **File Menu**: When one or more files are selected
2. **Folder Menu**: When one or more folders are selected
3. **Mixed Menu**: When both files and folders are selected
4. **Background Menu**: When clicking on empty space (shows folder operations for current directory)

## Selection Handling

### Selection Tracking

We'll implement a selection tracking mechanism to maintain the current selection state:

```python
class SelectionTracker:
    def __init__(self, tree_view):
        self.tree_view = tree_view
        self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self._current_selection = []
        
    def _on_selection_changed(self, selected, deselected):
        self._current_selection = self._get_selected_items()
        
    def _get_selected_items(self):
        model = self.tree_view.model()
        return [
            {
                'path': model.filePath(index),
                'is_dir': model.isDir(index),
                'name': model.fileName(index),
                'index': index
            }
            for index in self.tree_view.selectionModel().selectedIndexes()
        ]
        
    def get_selected_items(self):
        return self._current_selection
        
    def get_selected_paths(self):
        return [item['path'] for item in self._current_selection]
        
    def has_selection(self):
        return len(self._current_selection) > 0
        
    def is_single_selection(self):
        return len(self._current_selection) == 1
        
    def is_multi_selection(self):
        return len(self._current_selection) > 1
        
    def has_only_files(self):
        return all(not item['is_dir'] for item in self._current_selection)
        
    def has_only_folders(self):
        return all(item['is_dir'] for item in self._current_selection)
        
    def has_mixed_types(self):
        has_file = any(not item['is_dir'] for item in self._current_selection)
        has_folder = any(item['is_dir'] for item in self._current_selection)
        return has_file and has_folder
```

### Right-click Selection Behavior

When right-clicking on an item:

1. If the item is already part of the current selection, maintain the selection
2. If the item is not part of the current selection, clear the selection and select only the clicked item
3. If right-clicking on empty space, clear the selection

## Item Type Detection

### File Type Analysis

To provide context-appropriate menu items, we'll implement file type detection:

```python
class FileTypeDetector:
    def __init__(self):
        self._mime_database = QMimeDatabase()
        
    def get_file_type(self, path):
        mime_type = self._mime_database.mimeTypeForFile(path)
        return {
            'mime_type': mime_type.name(),
            'category': self._get_category(mime_type),
            'icon': QIcon.fromTheme(mime_type.iconName())
        }
        
    def _get_category(self, mime_type):
        if mime_type.name().startswith('text/'):
            return 'text'
        elif mime_type.name().startswith('image/'):
            return 'image'
        elif mime_type.name().startswith('audio/'):
            return 'audio'
        elif mime_type.name().startswith('video/'):
            return 'video'
        # Add more categories as needed
        else:
            return 'other'
```

### Type-Based Menu Customization

The context menu will adapt based on the detected file types:

```python
def customize_menu_for_file_types(menu, selected_items):
    file_type_detector = FileTypeDetector()
    
    # Get file types for all selected items
    file_types = [file_type_detector.get_file_type(item['path']) 
                 for item in selected_items]
                 
    # If all items are the same type, add type-specific actions
    if all(ft['category'] == file_types[0]['category'] for ft in file_types):
        category = file_types[0]['category']
        
        if category == 'image':
            menu.addAction(QIcon("icons/view_image.svg"), "Preview Image")
            
        elif category == 'text':
            menu.addAction(QIcon("icons/edit_text.svg"), "Edit")
            
        # Add more type-specific actions as needed
```

## Event Coordination

### Handling Double-Click Events

We need to ensure the context menu actions are consistent with double-click behavior:

```python
class ExplorerTreeView(QTreeView):
    def __init__(self, parent=None):
        # ... existing initialization ...
        self.doubleClicked.connect(self._on_double_click)
        
    def _on_double_click(self, index):
        path = self.model().filePath(index)
        if self.model().isDir(index):
            # Open folder
            self._open_folder(path)
        else:
            # Open file (same as "Open" in context menu)
            self._open_file(path)
            
    def _open_file(self, path):
        # This should use the same implementation as the "Open" context menu action
        self.file_operations_service.open_file(path)
```

### Drag and Drop Coordination

The context menu operations should be consistent with drag and drop behavior:

```python
def setup_drag_drop_handlers(self):
    # Set drag and drop flags
    self.setDragEnabled(True)
    self.setAcceptDrops(True)
    self.setDropIndicatorShown(True)
    
    # Use the same operations service for both context menu and drag-drop
    self.setDragDropMode(QAbstractItemView.DragDrop)
    
    # Connect drop event to the file operations service
    self.model().setDropAction(Qt.MoveAction)  # Default action
```

## UI Feedback

### Operation Status Feedback

The Explorer panel should update to reflect operation status:

```python
def connect_operation_signals(self):
    # Connect to file operation service signals
    self.file_operations_service.operation_started.connect(self._on_operation_started)
    self.file_operations_service.operation_completed.connect(self._on_operation_completed)
    self.file_operations_service.operation_failed.connect(self._on_operation_failed)
    
def _on_operation_started(self, operation_type, targets):
    # Show operation in status bar
    self.main_window.statusBar().showMessage(f"{operation_type} in progress...")
    
    # Disable affected items in the view during operation
    self._set_items_enabled(targets, False)
    
def _on_operation_completed(self, operation_type, targets):
    # Clear status and show success message
    self.main_window.statusBar().clearMessage()
    self.main_window.statusBar().showMessage(f"{operation_type} completed", 3000)
    
    # Update the view
    self._refresh_affected_paths(targets)
    
def _on_operation_failed(self, operation_type, targets, error):
    # Clear status and show error
    self.main_window.statusBar().clearMessage()
    self.main_window.statusBar().showMessage(f"{operation_type} failed: {error}", 5000)
    
    # Re-enable affected items
    self._set_items_enabled(targets, True)
```

## Testing Strategy

1. **Unit Tests**:
   - Test selection tracking with various selection scenarios
   - Test file type detection with different file types
   - Test menu generation for different selection types

2. **Integration Tests**:
   - Test context menu appearance in the Explorer panel
   - Test coordination between double-click and context menu actions
   - Test coordination between drag-drop and context menu operations

3. **UI Tests**:
   - Test right-click behavior on various items and empty space
   - Test selection behavior when right-clicking
   - Test keyboard context menu key behavior

## Implementation Tasks

1. Create `SelectionTracker` class
2. Implement `FileTypeDetector` class
3. Extend `ExplorerTreeView` to support context menu
4. Connect context menu to file operations
5. Implement coordination with other Explorer features
6. Add unit and integration tests
