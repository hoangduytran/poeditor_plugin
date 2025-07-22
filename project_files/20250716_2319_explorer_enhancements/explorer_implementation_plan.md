# Explorer Advanced Features Implementation Plan

**Date**: July 16, 2025  
**Component**: Explorer Panel  
**Related Design**: explorer_advanced_features_design.md  

## Implementation Priority

### High Priority (Must Have)
1. **Column Management**: Add/remove basic columns (name, size, modified, type)
2. **Basic Sorting**: Single column sorting with visual indicators
3. **Glob Search**: File search using glob patterns with case sensitivity option

### Medium Priority (Should Have)
1. **Multi-column Sorting**: Secondary and tertiary sort columns
2. **Advanced Search**: Regex support and whole word matching
3. **Column Persistence**: Save/restore column configurations
4. **Search History**: Remember recent searches

### Low Priority (Nice to Have)
1. **Extended Columns**: Permissions, owner, created date, accessed date
2. **Advanced Filters**: File type, size range, date range filters
3. **Search Presets**: Save/load search configurations
4. **Performance Optimization**: Lazy loading for large directories

## File Structure Changes

### New Files to Create
```
panels/
├── explorer_column_manager.py      # Column management logic
├── explorer_search_engine.py       # Advanced search functionality
├── explorer_sort_manager.py        # Multi-column sorting logic
└── dialogs/
    ├── __init__.py
    ├── column_selector_dialog.py   # Column selection UI
    └── search_options_dialog.py    # Advanced search options UI

widgets/
├── advanced_search_widget.py       # Enhanced search input widget
└── sortable_header_view.py         # Custom header with sort indicators

models/
└── explorer_file_model.py          # Enhanced file system model

tests/
└── panels/
    └── test_cases/
        ├── test_explorer_columns.py
        ├── test_explorer_search.py
        └── test_explorer_sorting.py
```

### Files to Modify
```
panels/
├── explorer_panel.py               # Main integration point
└── explorer_settings.py            # Add new configuration options

services/
├── config_service.py               # Add explorer configuration
└── panel_state_service.py          # Add explorer state persistence

core/
└── main_app_window.py              # Register new dialogs if needed
```

## Implementation Steps

### Step 1: Core Data Structures (Day 1)
1. Create `ExplorerColumn` enum
2. Create `ColumnConfig` and `SortConfig` dataclasses
3. Create `FileItem` dataclass
4. Add basic configuration loading/saving

### Step 2: Column Management (Days 2-3)
1. Implement `ExplorerColumnManager`
2. Create `ColumnSelectorDialog`
3. Add column header context menu
4. Integrate with existing explorer panel

### Step 3: Enhanced File Model (Days 4-5)
1. Create `ExplorerFileModel` based on `QAbstractItemModel`
2. Implement dynamic column support
3. Add data retrieval for all column types
4. Test with existing explorer panel

### Step 4: Sorting System (Days 6-7)
1. Implement `ExplorerSortManager`
2. Add sorting logic to file model
3. Create custom header view with sort indicators
4. Add multi-column sorting support

### Step 5: Search Engine (Days 8-9)
1. Create `ExplorerSearchEngine`
2. Implement glob pattern matching
3. Add case sensitivity and whole word options
4. Create search filter integration

### Step 6: Advanced Search UI (Days 10-11)
1. Create `AdvancedSearchWidget`
2. Add search options toggles
3. Implement search history dropdown
4. Create advanced search options dialog

### Step 7: Integration & Testing (Days 12-14)
1. Integrate all components in `ExplorerPanel`
2. Add state persistence
3. Write comprehensive tests
4. Performance testing and optimization
5. Documentation updates

## Code Quality Guidelines

### Naming Conventions
- Class names: `ExplorerColumnManager`, `AdvancedSearchWidget`
- File names: `explorer_column_manager.py`, `advanced_search_widget.py`
- Method names: `add_column()`, `apply_search_filter()`
- Constants: `DEFAULT_COLUMN_WIDTH`, `MAX_SEARCH_HISTORY`

### Error Handling
```python
# Use logging from lg.py
from lg import logger

try:
    result = self.search_engine.search(pattern, config)
except Exception as e:
    logger.error(f"Search failed for pattern '{pattern}': {e}")
    return []
```

### Type Hints
```python
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

def search(self, pattern: str, config: Optional[SearchConfig] = None) -> List[FileItem]:
    """Search for files matching the given pattern."""
```

### Documentation
```python
class ExplorerColumnManager:
    """Manages column configuration for the explorer panel.
    
    This class handles adding, removing, and reordering columns in the
    explorer file list. It also manages column width, visibility, and
    persistence of column configurations.
    
    Attributes:
        columns: Dictionary mapping column types to their configurations
        visible_columns: List of currently visible columns in display order
    """
```

## Configuration Schema

### Column Configuration
```python
@dataclass
class ColumnConfig:
    """Configuration for a single explorer column."""
    column: ExplorerColumn
    visible: bool = True
    width: int = 150
    sortable: bool = True
    resizable: bool = True
    order: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ColumnConfig':
        """Create from dictionary."""
        return cls(**data)
```

### Search Configuration
```python
@dataclass
class SearchConfig:
    """Configuration for explorer search functionality."""
    pattern: str = ""
    case_sensitive: bool = False
    whole_word: bool = False
    use_regex: bool = False
    use_glob: bool = True
    search_in_content: bool = False
    file_types: List[str] = field(default_factory=list)
    exclude_hidden: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
```

## Testing Strategy

### Unit Tests
```python
# tests/panels/test_cases/test_explorer_columns.py
class TestExplorerColumnManager:
    def test_add_column(self):
        """Test adding a new column."""
        
    def test_remove_column(self):
        """Test removing an existing column."""
        
    def test_reorder_columns(self):
        """Test changing column order."""
        
    def test_save_load_configuration(self):
        """Test persistence of column configuration."""
```

### Integration Tests
```python
# tests/panels/test_cases/test_explorer_integration.py
class TestExplorerIntegration:
    def test_search_and_sort_combination(self):
        """Test searching and sorting together."""
        
    def test_column_changes_during_search(self):
        """Test column visibility changes during active search."""
        
    def test_state_persistence(self):
        """Test saving and restoring explorer state."""
```

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: Load file details only when column becomes visible
2. **Caching**: Cache file metadata to avoid repeated stat calls
3. **Incremental Search**: Update search results as user types (debounced)
4. **Virtual Scrolling**: For very large directories (10k+ files)
5. **Background Threading**: File system operations in background threads

### Memory Management
```python
class FileItemCache:
    """Cache for file metadata to improve performance."""
    
    def __init__(self, max_size: int = 10000):
        self.cache: Dict[Path, FileItem] = {}
        self.max_size = max_size
        self.access_order: List[Path] = []
    
    def get_or_create(self, path: Path) -> FileItem:
        """Get cached item or create new one."""
        if path in self.cache:
            self._update_access(path)
            return self.cache[path]
        
        item = self._create_file_item(path)
        self._add_to_cache(path, item)
        return item
```

## Accessibility Features

### Keyboard Navigation
- `Ctrl+F`: Focus search widget
- `Ctrl+Shift+F`: Open advanced search dialog
- `F3`: Find next search result
- `Shift+F3`: Find previous search result
- `Alt+Click Header`: Add to multi-column sort
- `Ctrl+Alt+C`: Open column selector dialog

### Screen Reader Support
- Proper ARIA labels for search options
- Descriptive column headers
- Sort direction announcements
- Search result count announcements

### Visual Indicators
- Clear sort direction arrows
- Search match highlighting
- Column resize cursors
- Focus indicators for keyboard navigation

## Backwards Compatibility

### Migration Strategy
1. **Configuration Migration**: Convert existing simple column settings
2. **Default Fallbacks**: Provide sensible defaults for new features
3. **Graceful Degradation**: Basic functionality if advanced features fail
4. **Version Detection**: Check configuration version and migrate accordingly

## Security Considerations

### Input Validation
```python
def validate_search_pattern(pattern: str, use_regex: bool) -> tuple[bool, str]:
    """Validate search pattern for security and syntax."""
    if use_regex:
        try:
            re.compile(pattern)
        except re.error as e:
            return False, f"Invalid regex: {e}"
    
    # Check for potentially dangerous patterns
    if len(pattern) > 1000:
        return False, "Pattern too long"
    
    return True, ""
```

### File System Safety
- Limit directory traversal depth
- Validate file paths to prevent directory traversal attacks
- Handle permission errors gracefully
- Limit memory usage for large directories

This implementation plan provides a comprehensive roadmap for implementing the advanced Explorer features while maintaining code quality, performance, and security standards.
