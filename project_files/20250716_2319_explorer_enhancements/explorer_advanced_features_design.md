# Explorer Advanced Features Design

**Date**: July 16, 2025  
**Component**: Explorer Panel  
**Feature**: Advanced Column Management, Sorting, and Search  

## Overview

This design document outlines the implementation of advanced Explorer features including:
- Dynamic column management (add/remove columns)
- Multi-column sorting capabilities
- Enhanced file search with glob patterns, case sensitivity, and regex support

## Architecture Components

### 1. Column Management System

#### 1.1 Available Columns
```python
class ExplorerColumn(Enum):
    NAME = "name"
    SIZE = "size" 
    MODIFIED = "modified"
    TYPE = "type"
    PERMISSIONS = "permissions"
    CREATED = "created"
    ACCESSED = "accessed"
    OWNER = "owner"
    EXTENSION = "extension"
    PATH = "path"
```

#### 1.2 Column Configuration
```python
@dataclass
class ColumnConfig:
    column: ExplorerColumn
    visible: bool = True
    width: int = 150
    sortable: bool = True
    resizable: bool = True
    order: int = 0  # Display order
```

#### 1.3 Column Manager
```python
class ExplorerColumnManager:
    def __init__(self):
        self.columns: Dict[ExplorerColumn, ColumnConfig] = {}
        self.visible_columns: List[ExplorerColumn] = []
        
    def add_column(self, column: ExplorerColumn, config: ColumnConfig)
    def remove_column(self, column: ExplorerColumn)
    def reorder_columns(self, new_order: List[ExplorerColumn])
    def get_visible_columns(self) -> List[ExplorerColumn]
    def save_configuration(self)
    def load_configuration(self)
```

### 2. Sorting System

#### 2.1 Sort Configuration
```python
@dataclass
class SortConfig:
    column: ExplorerColumn
    direction: SortDirection  # ASC, DESC
    priority: int = 0  # For multi-column sorting
    
class SortDirection(Enum):
    ASC = "ascending"
    DESC = "descending"
```

#### 2.2 Sort Manager
```python
class ExplorerSortManager:
    def __init__(self):
        self.sort_configs: List[SortConfig] = []
        
    def add_sort(self, column: ExplorerColumn, direction: SortDirection)
    def remove_sort(self, column: ExplorerColumn)
    def clear_sorts(self)
    def apply_sort(self, items: List[FileItem]) -> List[FileItem]
    def get_sort_indicator(self, column: ExplorerColumn) -> str
```

### 3. Advanced Search System

#### 3.1 Search Configuration
```python
@dataclass
class SearchConfig:
    pattern: str = ""
    case_sensitive: bool = False
    whole_word: bool = False
    use_regex: bool = False
    use_glob: bool = True
    search_in_content: bool = False
    file_types: List[str] = None  # Filter by extensions
    size_range: Tuple[int, int] = None  # Min, max file size
    date_range: Tuple[datetime, datetime] = None
```

#### 3.2 Search Engine
```python
class ExplorerSearchEngine:
    def __init__(self):
        self.config = SearchConfig()
        self.search_history: List[str] = []
        
    def search(self, pattern: str, config: SearchConfig = None) -> List[FileItem]
    def search_glob(self, pattern: str, items: List[FileItem]) -> List[FileItem]
    def search_regex(self, pattern: str, items: List[FileItem]) -> List[FileItem]
    def search_simple(self, pattern: str, items: List[FileItem]) -> List[FileItem]
    def filter_by_type(self, items: List[FileItem], extensions: List[str]) -> List[FileItem]
    def filter_by_size(self, items: List[FileItem], size_range: Tuple[int, int]) -> List[FileItem]
```

## UI Components

### 1. Column Management UI

#### 1.1 Column Selector Dialog
```python
class ColumnSelectorDialog(QDialog):
    """Dialog for selecting which columns to display"""
    
    def __init__(self, parent, column_manager: ExplorerColumnManager):
        super().__init__(parent)
        self.column_manager = column_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Checkbox list of available columns
        # Drag-and-drop reordering
        # Column width settings
        # Preview area
```

#### 1.2 Column Header Context Menu
```python
class ExplorerHeaderContextMenu(QMenu):
    """Right-click context menu on column headers"""
    
    def __init__(self, parent, column: ExplorerColumn):
        super().__init__(parent)
        self.add_action("Sort Ascending", lambda: self.sort_ascending(column))
        self.add_action("Sort Descending", lambda: self.sort_descending(column))
        self.addSeparator()
        self.add_action("Hide Column", lambda: self.hide_column(column))
        self.add_action("Column Settings...", self.show_column_settings)
        self.addSeparator()
        self.add_action("Reset Columns", self.reset_columns)
```

### 2. Enhanced Search Widget

#### 2.1 Advanced Search Bar
```python
class AdvancedSearchWidget(QWidget):
    """Enhanced search widget with advanced options"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.search_engine = ExplorerSearchEngine()
        self.setup_ui()
        
    def setup_ui(self):
        # Search input field with history dropdown
        # Toggle buttons for: Case, Whole Word, Regex, Glob
        # Advanced options button
        # Clear/Reset button
        # Search results count
```

#### 2.2 Search Options Panel
```python
class SearchOptionsPanel(QWidget):
    """Collapsible panel with advanced search options"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # File type filters (checkboxes)
        # Size range slider
        # Date range picker
        # Search in content checkbox
        # Save/Load search presets
```

### 3. Enhanced Tree View

#### 3.1 Multi-Column Tree View
```python
class ExplorerTreeView(QTreeView):
    """Enhanced tree view with column management and sorting"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.column_manager = ExplorerColumnManager()
        self.sort_manager = ExplorerSortManager()
        self.setup_columns()
        self.setup_sorting()
        
    def setup_columns(self):
        # Configure header
        # Set up column delegates
        # Enable column resizing/reordering
        
    def setup_sorting(self):
        # Enable multi-column sorting
        # Custom sort indicators
        # Sort persistence
```

## Data Models

### 1. Enhanced File Model
```python
class ExplorerFileModel(QAbstractItemModel):
    """Enhanced file system model with column and search support"""
    
    def __init__(self):
        super().__init__()
        self.column_manager = ExplorerColumnManager()
        self.search_engine = ExplorerSearchEngine()
        self.sort_manager = ExplorerSortManager()
        self.filtered_items: List[FileItem] = []
        
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.column_manager.get_visible_columns())
        
    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        # Return column headers with sort indicators
        
    def data(self, index: QModelIndex, role: int):
        # Return data based on visible columns
        
    def sort(self, column: int, order: Qt.SortOrder):
        # Multi-column sorting support
        
    def apply_search_filter(self, config: SearchConfig):
        # Apply search filter and refresh view
```

### 2. File Item Data Structure
```python
@dataclass
class FileItem:
    name: str
    path: Path
    size: int
    modified: datetime
    created: datetime
    accessed: datetime
    type: str  # file, directory, symlink
    extension: str
    permissions: str
    owner: str
    is_hidden: bool = False
    is_symlink: bool = False
    
    def get_column_value(self, column: ExplorerColumn) -> Any:
        """Get value for specific column"""
        return getattr(self, column.value, "")
```

## Integration Points

### 1. Panel Integration
```python
# In panels/explorer_panel.py
class ExplorerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_view = ExplorerTreeView(self)
        self.search_widget = AdvancedSearchWidget(self)
        self.column_manager = ExplorerColumnManager()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        # Layout with search widget and tree view
        # Toolbar with column management button
        
    def setup_connections(self):
        # Connect search signals
        # Connect column management signals
        # Connect sorting signals
```

### 2. State Persistence
```python
# Integration with services/panel_state_service.py
class ExplorerStateManager:
    def save_state(self) -> dict:
        return {
            'columns': self.column_manager.get_configuration(),
            'sort': self.sort_manager.get_configuration(),
            'search': self.search_engine.config.__dict__,
            'view_settings': self.get_view_settings()
        }
        
    def restore_state(self, state: dict):
        self.column_manager.load_configuration(state.get('columns', {}))
        self.sort_manager.load_configuration(state.get('sort', {}))
        # Restore other settings
```

## Implementation Plan

### Phase 1: Column Management (Week 1)
1. Implement `ExplorerColumn` enum and `ColumnConfig` dataclass
2. Create `ExplorerColumnManager` class
3. Update `ExplorerFileModel` to support dynamic columns
4. Create `ColumnSelectorDialog` UI
5. Add column header context menu
6. Implement column persistence

### Phase 2: Sorting System (Week 2)
1. Implement `SortConfig` and `ExplorerSortManager`
2. Add multi-column sorting to file model
3. Create sort indicators in headers
4. Add keyboard shortcuts for sorting
5. Implement sort persistence

### Phase 3: Advanced Search (Week 3)
1. Create `SearchConfig` and `ExplorerSearchEngine`
2. Implement glob pattern matching
3. Add regex search support
4. Create `AdvancedSearchWidget` UI
5. Add search options panel
6. Implement search history

### Phase 4: Integration & Polish (Week 4)
1. Integrate all components in `ExplorerPanel`
2. Add comprehensive error handling
3. Implement state persistence
4. Add keyboard shortcuts and accessibility
5. Performance optimization
6. Testing and documentation

## Testing Strategy

### Unit Tests
- Column management operations
- Sorting algorithms with various data types
- Search pattern matching (glob, regex, simple)
- State persistence and restoration

### Integration Tests
- UI component interactions
- Search and sort combinations
- Column visibility changes during active search
- State persistence across application restarts

### Performance Tests
- Large directory handling (10k+ files)
- Search performance with different pattern types
- Sorting performance with multiple columns
- Memory usage during extended usage

## Configuration Files

### Default Column Configuration
```json
{
  "default_columns": [
    {"column": "name", "visible": true, "width": 250, "order": 0},
    {"column": "size", "visible": true, "width": 100, "order": 1},
    {"column": "modified", "visible": true, "width": 150, "order": 2},
    {"column": "type", "visible": false, "width": 100, "order": 3}
  ],
  "search_defaults": {
    "case_sensitive": false,
    "whole_word": false,
    "use_regex": false,
    "use_glob": true
  }
}
```

## Future Enhancements

1. **Custom Column Types**: Allow plugins to register custom columns
2. **Advanced Filters**: Date range, file size, file type filters
3. **Saved Searches**: Save and recall frequently used search patterns
4. **Search Scopes**: Limit search to specific directories
5. **Thumbnail Column**: Show file thumbnails for images
6. **Git Integration**: Show git status as a column
7. **Tag System**: Add custom tags to files and search by tags

## Dependencies

- **PySide6**: Core UI framework
- **pathlib**: File system operations
- **re**: Regular expression support
- **fnmatch**: Glob pattern matching
- **json**: Configuration persistence
- **datetime**: Date/time handling

## Notes

- All column configurations will be saved in user preferences
- Search history will be limited to last 50 searches
- Performance will be optimized for directories with up to 10,000 files
- Sorting will use stable sort algorithms to maintain secondary order
- Regular expression patterns will be validated before execution
- Glob patterns will follow standard shell glob syntax
