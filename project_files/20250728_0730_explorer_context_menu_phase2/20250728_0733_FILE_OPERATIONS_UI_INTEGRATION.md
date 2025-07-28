# File Operations UI Integration

**Date**: July 28, 2025, 07:33  
**Component**: Explorer Context Menu - File Operations UI Integration  
**Status**: Technical Design  
**Priority**: High

## Overview

This document outlines how the Explorer Context Menu will integrate with the `FileOperationsService` implemented in Phase 1. It covers the connection between UI actions and service methods, error handling, progress indication, and user feedback.

## Architecture

The integration follows an MVC-like pattern:
- **View**: Context Menu UI (defined in CONTEXT_MENU_UI_DESIGN.md)
- **Controller**: Action Handlers (defined in this document)
- **Model**: FileOperationsService (implemented in Phase 1)

## Action Handlers

Each context menu action will be connected to a handler function that bridges the UI and service layers. These handlers will:

1. Extract necessary information from the UI state
2. Validate the operation
3. Call the appropriate service method
4. Handle errors and show feedback
5. Update UI state as needed

### Handler Implementation Pattern

```python
class FileOperationHandlers:
    def __init__(self, file_operations_service, undo_redo_manager, notification_service):
        self.file_operations_service = file_operations_service
        self.undo_redo_manager = undo_redo_manager
        self.notification_service = notification_service
        
    def handle_copy(self, selected_items):
        try:
            self.file_operations_service.copy(selected_items)
            self.notification_service.show_info(f"Copied {len(selected_items)} items to clipboard")
        except Exception as e:
            self.notification_service.show_error(f"Failed to copy items: {str(e)}")
            
    def handle_paste(self, destination):
        try:
            operation = self.file_operations_service.paste(destination)
            if operation.requires_confirmation:
                # Show confirmation dialog
                if not self._confirm_operation(operation):
                    return
            
            # For long operations, show progress
            if operation.is_long_running:
                self._run_with_progress(operation)
            else:
                operation.execute()
                
            self.notification_service.show_success(f"Pasted items to {destination}")
        except Exception as e:
            self.notification_service.show_error(f"Failed to paste items: {str(e)}")
```

## Progress Indication

For long-running operations, we will implement a progress dialog:

```python
def _run_with_progress(self, operation):
    progress_dialog = QProgressDialog("Processing...", "Cancel", 0, 100)
    progress_dialog.setWindowModality(Qt.WindowModal)
    
    # Connect operation progress signals
    operation.progress_updated.connect(progress_dialog.setValue)
    operation.status_updated.connect(progress_dialog.setLabelText)
    
    # Connect cancel button
    progress_dialog.canceled.connect(operation.cancel)
    
    # Start operation in background thread
    worker = OperationWorker(operation)
    worker.finished.connect(progress_dialog.close)
    worker.start()
    
    progress_dialog.exec_()
```

## Confirmation Dialogs

For potentially destructive operations, we will show confirmation dialogs:

```python
def _confirm_operation(self, operation):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(operation.confirmation_message)
    msg_box.setInformativeText(operation.confirmation_details)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    
    return msg_box.exec_() == QMessageBox.Yes
```

## Error Handling

We will implement a comprehensive error handling strategy:

1. **Service-level validation**: The FileOperationsService will validate operations before execution
2. **Pre-execution checks**: UI handlers will check for common errors before calling service methods
3. **Exception handling**: All service calls will be wrapped in try/except blocks
4. **User feedback**: Errors will be displayed to the user with clear messages
5. **Recovery options**: Where possible, we'll provide recovery options for failed operations

### Error Categories

| Error Category | Example | Handling Strategy |
|----------------|---------|-------------------|
| Permission errors | Cannot delete read-only file | Show error with option to retry as admin |
| Path errors | Destination doesn't exist | Show error with option to create path |
| Name conflicts | File already exists | Show conflict resolution dialog |
| I/O errors | Disk full | Show error with space information |
| Unexpected errors | Unknown exception | Show generic error with logging |

## Notification System

We will integrate with the application's notification system to provide feedback:

```python
def show_operation_result(operation_type, success, details):
    if success:
        self.notification_service.show_success(
            f"{operation_type} completed successfully", 
            details
        )
    else:
        self.notification_service.show_error(
            f"{operation_type} failed", 
            details
        )
```

## Undo/Redo Integration

Each operation will be recorded in the UndoRedoManager:

```python
def execute_with_undo(self, operation):
    result = operation.execute()
    
    if result.success:
        # Create undo record
        undo_operation = operation.create_undo_operation()
        self.undo_redo_manager.record_operation(
            operation_type=operation.type,
            undo_operation=undo_operation,
            redo_operation=operation
        )
        
    return result
```

## Selection State Management

The context menu needs to maintain awareness of the current selection:

```python
class SelectionStateManager:
    def __init__(self, explorer_tree_view):
        self.explorer_tree_view = explorer_tree_view
        
    def get_selected_items(self):
        return [
            self._item_from_index(index)
            for index in self.explorer_tree_view.selectedIndexes()
        ]
        
    def get_selected_paths(self):
        return [item.path for item in self.get_selected_items()]
        
    def is_multi_selection(self):
        return len(self.get_selected_items()) > 1
        
    def has_mixed_types(self):
        items = self.get_selected_items()
        if not items:
            return False
        
        first_is_dir = items[0].is_dir()
        return any(item.is_dir() != first_is_dir for item in items[1:])
```

## Testing Strategy

1. **Unit Tests**:
   - Test each handler with mock services
   - Test error handling with simulated failures
   - Test progress indication with long-running operation simulations

2. **Integration Tests**:
   - Test full operation flow from UI to service and back
   - Test with real file system operations (in a test directory)
   - Test undo/redo functionality

## Implementation Tasks

1. Create `FileOperationHandlers` class
2. Implement handlers for each menu action
3. Create progress dialog component
4. Create confirmation dialog components
5. Implement selection state manager
6. Connect handlers to context menu actions
7. Add unit and integration tests
8. Perform performance testing with large directories
