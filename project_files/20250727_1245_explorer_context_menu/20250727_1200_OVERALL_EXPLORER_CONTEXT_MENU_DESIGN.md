# Explorer Context Menu and File Operations Design

**Date**: July 27, 2025  
**Component**: Explorer Context Menu and File Operations  
**Status**: Design Phase  
**Priority**: High

## 1. Overview

This document outlines the design for an enhanced Explorer component with comprehensive file and directory operations accessible through a right-click context menu and drag-and-drop functionality. The design follows the VS Code-like architecture established in the project rules and integrates with the existing plugin framework.

## 2. Core Features

### 2.1 Context Menu Operations
- File/directory copy, paste, delete, and move operations
- New file creation with template selection
- New directory creation
- Smart file duplication with automatic numbering
- Rename operations with validation
- Open with external application

### 2.2 Drag and Drop Support
- Internal drag and drop (within the Explorer)
- External drag and drop (from Finder/File Explorer)
- Copy vs. Move operation selection (via modifier keys)
- Visual feedback during drag operations

### 2.3 Undo/Redo Framework
- Operation history tracking
- Undo/Redo for all file system operations
- Persistent operation history
- Safety mechanisms for destructive operations

## 3. User Interface Design

### 3.1 Context Menu Layout

```
┌──────────────────────────────┐
│ Open                         │
│ Open With...                 │
├──────────────────────────────┤
│ Cut                          │
│ Copy                         │
│ Paste                        │
│ Duplicate                    │
├──────────────────────────────┤
│ New File...                  │ ──┐
│ New Folder                   │   │
├──────────────────────────────┤   │    ┌─────────────────────────┐
│ Delete                       │   └──> │ [Text Field]            │
│ Rename                       │        ├─────────────────────────┤
├──────────────────────────────┤        │ Common Extensions:      │
│ Copy Path                    │        │ ◉ .py                   │
│ Copy Relative Path           │        │ ○ .md                   │
├──────────────────────────────┤        │ ○ .json                 │
│ Refresh Explorer             │        │ ○ .xml                  │
└──────────────────────────────┘        │ ○ .txt                  │
                                        │ ○ .html                 │
                                        │ ○ .css                  │
                                        │ ○ .js                   │
                                        │ ○ (Custom)              │
                                        ├─────────────────────────┤
                                        │ [Cancel] [Create]       │
                                        └─────────────────────────┘
```

### 3.2 Drag and Drop Indicators

- **Copy Operation**: Plus icon overlay on dragged item
- **Move Operation**: Arrow icon overlay on dragged item
- **Drop Target**: Highlighted folder/area with subtle animation
- **Invalid Drop**: Red "no" icon indicator
- **Operation Progress**: Mini progress indicator during lengthy operations

### 3.3 Undo/Redo UI Elements

- Status bar notification after each operation with undo link
- Keyboard shortcuts: Ctrl+Z (Undo), Ctrl+Shift+Z/Ctrl+Y (Redo)
- Edit menu integration for Undo/Redo operations
- Operation details in tooltip

## 4. Technical Architecture

### 4.1 Component Structure

```
explorer/
├── file_operations/
│   ├── __init__.py
│   ├── copy_paste_manager.py      # Clipboard operations
│   ├── drag_drop_handler.py       # D&D implementation
│   ├── file_creator.py            # New file/directory creation
│   ├── file_system_operations.py  # Core file operations
│   ├── numbering_service.py       # Duplicate file numbering
│   └── undo_redo_manager.py       # Operation history tracking
├── ui/
│   ├── __init__.py
│   ├── context_menu_provider.py   # Context menu builder
│   ├── drag_drop_ui.py           # Visual feedback components
│   ├── file_creation_dialog.py    # New file dialog
│   └── operation_progress_ui.py   # Progress indicators
└── models/
    ├── __init__.py
    ├── file_operation_model.py    # Operation data model
    ├── operation_history.py       # Undo/redo stack model
    └── extension_registry.py      # File extension definitions
```

### 4.2 Key Classes

```python
class FileOperationService:
    """Core service managing all file system operations."""
    
    def copy_items(self, paths: List[str], cut: bool = False) -> bool:
        """Copy files/directories to internal clipboard."""
        pass
        
    def paste_items(self, target_dir: str) -> List[FileOperationResult]:
        """Paste previously copied items to target directory."""
        pass
    
    def create_file(self, parent_dir: str, name: str, template: str = None) -> str:
        """Create a new file in the specified directory."""
        pass
    
    def create_directory(self, parent_dir: str, name: str) -> str:
        """Create a new directory."""
        pass
    
    def delete_items(self, paths: List[str], permanent: bool = False) -> bool:
        """Delete files/directories (to trash or permanently)."""
        pass
    
    def rename_item(self, path: str, new_name: str) -> str:
        """Rename a file or directory."""
        pass
    
    def duplicate_item(self, path: str) -> str:
        """Create a duplicate with auto-numbering."""
        pass


class DragDropManager:
    """Manages drag and drop operations."""
    
    def start_drag(self, paths: List[str], source_widget) -> None:
        """Initialize a drag operation."""
        pass
    
    def handle_drop(self, paths: List[str], target_path: str, action: DropAction) -> List[FileOperationResult]:
        """Process dropped items."""
        pass
    
    def is_valid_drop_target(self, path: str, dragged_paths: List[str]) -> bool:
        """Check if a drop location is valid for the dragged items."""
        pass


class FileNumberingService:
    """Handles automatic file numbering for duplicates."""
    
    def generate_numbered_name(self, base_path: str) -> str:
        """Generate a numbered filename for a duplicate."""
        pass
    
    def parse_numbered_name(self, path: str) -> Tuple[str, int]:
        """Extract the base name and number from a numbered file."""
        pass
    
    def get_next_number(self, base_name: str, directory: str) -> int:
        """Determine the next available number for a file."""
        pass


class UndoRedoManager:
    """Manages the undo/redo stack and operation history."""
    
    def record_operation(self, operation: FileOperation) -> None:
        """Add an operation to the history stack."""
        pass
    
    def can_undo(self) -> bool:
        """Check if an undo operation is available."""
        pass
    
    def can_redo(self) -> bool:
        """Check if a redo operation is available."""
        pass
    
    def undo(self) -> FileOperationResult:
        """Undo the last operation."""
        pass
    
    def redo(self) -> FileOperationResult:
        """Redo the previously undone operation."""
        pass
    
    def get_operation_history(self, limit: int = 10) -> List[FileOperation]:
        """Get recent operations from the history."""
        pass
```

### 4.3 Data Models

```python
class FileOperation:
    """Model representing a file system operation."""
    
    operation_type: Literal['copy', 'move', 'delete', 'create', 'rename']
    source_paths: List[str]
    target_path: Optional[str]
    timestamp: datetime
    is_undoable: bool
    undo_data: Dict[str, Any]
    
    def get_description(self) -> str:
        """Get a human-readable description of the operation."""
        pass


class FileOperationResult:
    """Result of a file operation."""
    
    success: bool
    operation: FileOperation
    result_paths: List[str]
    errors: List[str]
    warnings: List[str]
```

### 4.4 Settings Schema

```yaml
explorer:
  file_operations:
    confirm_delete: bool  # Show confirmation dialog for deletions
    permanent_delete_key: str  # Key modifier for permanent delete (default: "shift")
    preserve_timestamps: bool  # Preserve timestamps on copy operations
    max_operation_history: int  # Number of operations to keep in history
    duplicate_numbering:
      format: str  # Format for numbered duplicates (default: "{name}_{number:05d}{ext}")
      start_from: int  # Starting number for duplicates (default: 1)
      number_width: int  # Width of the number part (default: 5)
      rollover_threshold: int  # When to increase width (default: 99999)
    new_file_templates:
      enabled: bool  # Enable file templates
      custom_templates: dict  # User-defined templates
```

## 5. Automatic File Numbering

### 5.1 Numbering Format

- **Default Pattern**: `{filename}_{number:05d}{extension}`
  - Example: `document_00001.txt`
- **Number Range**: 00001-99999
- **Number Width Increase**: When limit reached, width increases to 000001-999999
- **Persistence**: Last used number stored in QSettings per directory

### 5.2 Numbering Algorithm

1. Extract base name and extension from original file
2. Check for existing numbered variants in the directory
3. Determine the next available number
4. If max number reached (99999), increase width to 6 digits
5. Generate the new filename using the pattern
6. Store the highest used number in settings

## 6. Undo/Redo Implementation

### 6.1 Operation Tracking

Each file operation records:
- Operation type (copy, move, delete, create, rename)
- Source and target paths
- Timestamp
- Additional metadata needed for undo
- Original file contents hash (for verification)

### 6.2 Undoable Operations

| Operation | Undo Action | Data Required |
|-----------|-------------|---------------|
| Copy      | Delete copied files | List of created files |
| Move      | Move back to original location | Original paths, target paths |
| Delete    | Restore from backup | Backup paths, original paths |
| Create    | Delete created files | Created file paths |
| Rename    | Restore original name | Original path, new path |
| Duplicate | Delete duplicated files | Created file paths |

### 6.3 Safety Mechanisms

- File hash verification before undo/redo
- Backup creation before destructive operations
- Read-only file detection and handling
- Transaction-like approach for multi-file operations
- Graceful failure with detailed error reporting

## 7. Drag and Drop Implementation

### 7.1 Supported Operations

- Drag files within Explorer (move or copy)
- Drag files from Explorer to external applications
- Drag files from external sources into Explorer
- Multi-file selection drag and drop
- Directory drag and drop

### 7.2 Modifier Keys

| Modifier | Action |
|----------|--------|
| None     | Move within same volume, Copy across volumes |
| Ctrl/Cmd | Force Copy operation |
| Alt      | Force Move operation |
| Shift    | Create shortcut/link (where supported) |

### 7.3 Drop Target Detection

- Directory highlighting when valid target
- Visual feedback for invalid targets
- Auto-scroll during drag near edges
- Expand/collapse folders during hover

## 8. New File Creation Dialog

### 8.1 Common Extensions Registry

Default extension categories:
- **Code**: .py, .js, .html, .css, .xml, .json
- **Documents**: .txt, .md, .csv
- **Images**: .png, .jpg, .svg
- **Data**: .yaml, .toml, .ini
- **Custom**: User-defined extensions

### 8.2 Dialog Features

- Extension selection with radio buttons
- Custom extension input field
- File name validation (illegal characters, existing files)
- Template selection for supported types
- Preview pane for selected template
- Recently used extensions list

## 9. Error Handling and Edge Cases

### 9.1 Error Scenarios

- Permission denied errors
- Disk space limitations
- File in use by another process
- Name collisions
- Broken links/references
- Long paths (exceeding OS limits)
- Special file types (symlinks, devices)

### 9.2 Conflict Resolution

- **Naming Conflicts**: Auto-rename with numbering or prompt user
- **Merge Folders**: Options to merge, replace, or cancel
- **Permissions**: Elevate privileges or show detailed error
- **File in Use**: Retry, skip, or abort options

## 10. Integration Points

### 10.1 Plugin System Integration

```python
class ExplorerContextMenuProvider(PluginBase):
    """Plugin for providing explorer context menu entries."""
    
    def get_context_menu_items(self, paths: List[str], is_folder: bool) -> List[ContextMenuItem]:
        """Get context menu items for the selected path(s)."""
        pass
    
    def handle_menu_action(self, action_id: str, paths: List[str]) -> bool:
        """Handle a selected menu action."""
        pass
```

### 10.2 Event System

```python
# Explorer events that can be observed by other components
explorer_events = {
    'file_created': Signal(str),  # path
    'file_deleted': Signal(List[str]),  # paths
    'file_moved': Signal(str, str),  # source_path, target_path
    'file_copied': Signal(str, str),  # source_path, target_path
    'file_renamed': Signal(str, str),  # old_path, new_path
    'operation_undone': Signal(FileOperation),  # undone operation
    'operation_redone': Signal(FileOperation),  # redone operation
}
```

### 10.3 Command Integration

```python
# Explorer commands that can be triggered from other components
explorer_commands = {
    'copy_selected': Command(),
    'paste_to_selected': Command(),
    'delete_selected': Command(),
    'rename_selected': Command(),
    'create_new_file': Command(str),  # parent_path
    'create_new_folder': Command(str),  # parent_path
    'undo_last_operation': Command(),
    'redo_last_operation': Command(),
    'refresh_view': Command(),
}
```

## 11. Implementation Plan

### Phase 1: Core Infrastructure
- File operation service implementation
- Undo/redo manager framework
- Basic context menu functionality
- Settings integration

### Phase 2: Advanced Features
- Drag and drop implementation
- New file dialog with templates
- File numbering service
- Conflict resolution system

### Phase 3: Polish and Edge Cases
- Error handling improvements
- Performance optimization for large directories
- Animation and visual feedback refinements
- Accessibility enhancements

## 12. Suggested Enhancements

### 12.1 Batch Operations
- Multi-file rename with patterns
- Batch processing operations
- Operation queuing for large transfers

### 12.2 Extended Functionality
- File comparison tool integration
- Search within selection
- File tagging and categorization
- Archive operations (zip/unzip)
- File preview in tooltip

### 12.3 UI Enhancements
- Operation progress in status bar
- Customizable context menu items
- Keyboard shortcut overlay
- File icons based on type/extension
- List/Grid/Tree view options

## 13. Testing Strategy

### 13.1 Unit Tests
- Test each file operation in isolation
- Verify numbering logic
- Test undo/redo stack behavior
- Validation testing

### 13.2 Integration Tests
- Test UI components with mock file system
- Verify drag and drop behavior
- Test context menu construction

### 13.3 System Tests
- End-to-end tests of complete operations
- Performance testing with large directories
- Edge case handling

## 14. Conclusion

This enhanced Explorer component will provide a full-featured file management experience within the application, matching the capabilities of native file managers while integrating seamlessly with the application's UI and architecture. The comprehensive context menu, drag-and-drop support, and undo/redo functionality will significantly improve user workflow when managing project files.

The implementation follows the project's architectural patterns and provides extensive plugin hooks for future extensions. The attention to edge cases and error handling ensures a robust experience even in complex file system environments.
