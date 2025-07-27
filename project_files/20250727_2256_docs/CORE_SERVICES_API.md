# Core Services API Documentation

**Date**: July 27, 2025  
**Status**: Technical Documentation  
**Component**: File Operations Core Services

## Overview

This document provides a comprehensive reference for the core services implemented as part of the Explorer Context Menu feature. These services form the foundation for file operations with support for undo/redo functionality and automatic file numbering.

## Service Architecture

The services are organized in a layered architecture:

```
┌─────────────────────────────────┐
│     FileOperationsService       │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│       UndoRedoManager           │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│      FileNumberingService       │
└─────────────────────────────────┘
```

## 1. FileNumberingService

A service for automatically generating numbered file names when duplicates are created.

### Key Classes and Methods

#### `FileNumberingService`

```python
class FileNumberingService:
    def __init__(self)
    def extract_pattern(path: str) -> Tuple[str, str, int, str]
    def generate_numbered_name(path: str, preferred_pattern: Optional[str] = None) -> str
    def detect_existing_numbering(directory: str, base_name: str) -> dict
    def get_next_available_number(directory: str, base_name: str, pattern_type: str = "parentheses") -> int
```

### Usage Examples

```python
# Create a service instance
numbering_service = FileNumberingService()

# Generate a numbered name for a file that already exists
new_path = numbering_service.generate_numbered_name("/path/to/document.txt")
# Result: "/path/to/document (1).txt"

# Extract numbering pattern from an existing file
base_name, separator, number, extension = numbering_service.extract_pattern("/path/to/document (3).txt")
# Result: ("document", " (", 3, ").txt")

# Find the next available number in a directory
next_num = numbering_service.get_next_available_number("/path/to", "document", "parentheses")
# Result: 4 (if document (3).txt exists)
```

## 2. UndoRedoManager

A service for tracking file operations and providing undo/redo functionality.

### Key Classes and Methods

#### `FileOperation` (dataclass)

```python
@dataclass
class FileOperation:
    operation_type: str
    source_paths: List[str]
    target_path: str
    timestamp: datetime
    is_undoable: bool
    undo_data: Optional[Dict[str, Any]] = None
```

#### `UndoRedoManager`

```python
class UndoRedoManager:
    def __init__(self, max_history: int = 100)
    def record_operation(self, operation: FileOperation) -> None
    def undo(self) -> Optional[FileOperation]
    def redo(self) -> Optional[FileOperation]
    def peek_undo(self) -> Optional[FileOperation]
    def peek_redo(self) -> Optional[FileOperation]
    def can_undo(self) -> bool
    def can_redo(self) -> bool
    def clear_history(self) -> None
    def get_undo_history(self) -> List[FileOperation]
    def get_redo_history(self) -> List[FileOperation]
```

### Usage Examples

```python
# Create a manager instance
undo_redo_manager = UndoRedoManager()

# Record a file operation
operation = FileOperation(
    operation_type="copy",
    source_paths=["/path/to/source.txt"],
    target_path="/path/to/destination/",
    timestamp=datetime.now(),
    is_undoable=True,
    undo_data={"created_paths": ["/path/to/destination/source.txt"]}
)
undo_redo_manager.record_operation(operation)

# Check if undo is available
if undo_redo_manager.can_undo():
    # Undo the last operation
    undone_op = undo_redo_manager.undo()
    
    # Later, redo the operation if needed
    if undo_redo_manager.can_redo():
        redo_op = undo_redo_manager.redo()
```

## 3. FileOperationsService

A service for performing file operations with undo/redo support and clipboard management.

### Key Classes and Methods

#### `OperationType` (Enum)

```python
class OperationType(Enum):
    COPY = "copy"
    CUT = "cut"
    PASTE = "paste"
    DELETE = "delete"
    RENAME = "rename"
    DUPLICATE = "duplicate"
    NEW_FILE = "new_file"
    NEW_FOLDER = "new_folder"
    MOVE = "move"
```

#### `FileOperationsService`

```python
class FileOperationsService(QObject):
    # Signals
    operationStarted = Signal(str, list)
    operationCompleted = Signal(str, list, str)
    operationFailed = Signal(str, list, str)
    clipboardChanged = Signal()
    
    def __init__(self, parent=None)
    
    # Clipboard operations
    def copy_to_clipboard(self, paths: List[str]) -> bool
    def cut_to_clipboard(self, paths: List[str]) -> bool
    def get_clipboard_contents(self) -> Tuple[Optional[str], List[str]]
    def can_paste(self, target_dir: str) -> bool
    def paste(self, target_dir: str) -> List[str]
    
    # File operations
    def delete_items(self, paths: List[str], skip_trash: bool = False) -> bool
    def rename_item(self, path: str, new_name: str) -> str
    def duplicate_item(self, path: str) -> str
    def create_new_file(self, parent_dir: str, name: str = "New File.txt") -> str
    def create_new_folder(self, parent_dir: str, name: str = "New Folder") -> str
    def move_items(self, paths: List[str], target_dir: str) -> List[str]
    
    # Undo/Redo operations
    def undo(self) -> bool
    def redo(self) -> bool
    def can_undo(self) -> bool
    def can_redo(self) -> bool
    
    # Helpers
    def is_operation_in_progress(self) -> bool
    def clear_clipboard(self)
```

### Usage Examples

```python
# Create a service instance
file_ops = FileOperationsService()

# Connect to signals
file_ops.operationCompleted.connect(lambda op_type, sources, target: print(f"Operation {op_type} completed"))
file_ops.operationFailed.connect(lambda op_type, sources, error: print(f"Operation {op_type} failed: {error}"))

# Copy files to clipboard
file_ops.copy_to_clipboard(["/path/to/file1.txt", "/path/to/file2.txt"])

# Paste files to a target directory
new_paths = file_ops.paste("/path/to/destination/")

# Create a new folder
new_folder = file_ops.create_new_folder("/path/to/parent", "My Folder")

# Rename a file
new_path = file_ops.rename_item("/path/to/old.txt", "new.txt")

# Delete files (to trash by default)
file_ops.delete_items(["/path/to/unwanted.txt"])

# Undo the last operation
if file_ops.can_undo():
    file_ops.undo()
    
# Redo the undone operation
if file_ops.can_redo():
    file_ops.redo()
```

## Service Integration

These services work together to provide a complete file operations system:

1. **FileNumberingService** is used by FileOperationsService to handle naming conflicts
2. **UndoRedoManager** tracks operations performed by FileOperationsService
3. **FileOperationsService** uses both to provide robust file operations with undo/redo

### Example Integration Flow

1. User initiates a duplicate operation on file.txt
2. FileOperationsService calls FileNumberingService to generate a name (file (1).txt)
3. FileOperationsService performs the duplication
4. FileOperationsService creates a FileOperation record with undo data
5. FileOperationsService sends the record to UndoRedoManager
6. FileOperationsService emits operationCompleted signal

### Error Handling

All services include comprehensive error handling:

- **FileNumberingService**: Falls back to timestamp-based naming if conflicts persist
- **UndoRedoManager**: Validates operations before adding to history
- **FileOperationsService**: Catches exceptions and emits operationFailed signals

## Best Practices

### Working with FileOperationsService

1. **Always check return values**: Operations return success indicators
2. **Connect to signals**: For UI updates and error handling
3. **Use undo/redo properly**: Check can_undo()/can_redo() before calling undo()/redo()

### Working with UndoRedoManager

1. **Provide complete undo_data**: Include all information needed to reverse operations
2. **Set is_undoable correctly**: Not all operations should be undoable

### Working with FileNumberingService

1. **Handle preferences**: Use preferred_pattern for consistent naming
2. **Extract patterns carefully**: The extract_pattern method returns components that can be manipulated

## Thread Safety

These services are not thread-safe by default. When using them in a multi-threaded environment:

1. Call FileOperationsService methods from the main thread
2. Use signals/slots for asynchronous operations
3. Use locks if direct access from worker threads is necessary
