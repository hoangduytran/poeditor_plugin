# Unified Pagination Abstraction Design

## Overview

This document details the design of a unified pagination abstraction for the PO Editor application. The design aims to centralize pagination controls, avoid code duplication, and allow polymorphism across different components that require pagination functionality.

The core design principle is a clear separation between:
1. **Pagination Logic** - The core mechanism that handles page calculations and state
2. **Pagination UI** - The visual controls and widgets for user interaction
3. **Data Providers** - Components that supply the data to be paginated

## Current State Analysis

The application currently implements pagination in multiple locations with different approaches:

1. **TablePagerBase** (`subcmp/table_nav_widget.py`) - Abstract base class for table pagination
2. **PagedFileSystemModel** (`plugins/explorer/professional_explorer.py`) - Pagination for file system model
3. **SearchResultsPanel** (`plugins/explorer/professional_explorer.py`) - Self-contained panel with pagination
4. **IssueOnlyDialog** (`workspace/issue_only_dialog_paged.py`) - Dialog with pagination for issues
5. **BaseNavRecord** (`workspace/find_replace_types.py`) - Data class with pagination attributes

This leads to duplicated pagination logic and inconsistent user experiences across the application.

## Design Goals

1. **Separation of Concerns**
   - Decouple pagination logic from UI components
   - Separate data providers from pagination mechanisms

2. **Consistent User Experience**
   - Unified pagination controls with consistent behavior
   - Standard keyboard shortcuts across all paginated components

3. **Flexibility & Extensibility**
   - Support various data sources (models, lists, etc.)
   - Easy to implement in new components

4. **Reduced Code Duplication**
   - Centralized pagination calculations
   - Reusable UI components

5. **Polymorphism**
   - Common interface for all pagination implementations
   - Allow specialized behavior while maintaining the common contract

## Architecture

The pagination system will be built around three key components:

### 1. Core Pagination Models

#### `PaginationState` (Data Class)
Holds the current state of pagination with all necessary attributes:

```python
@dataclass
class PaginationState:
    """Immutable data class representing pagination state"""
    current_page: int = 0          # Current page index (0-based)
    page_size: int = 50            # Items per page
    total_items: int = 0           # Total number of items
    
    # Computed properties
    @property
    def total_pages(self) -> int:
        """Calculate total pages from items and page size"""
        if self.total_items <= 0:
            return 1
        return max(1, (self.total_items + self.page_size - 1) // self.page_size)
    
    @property
    def start_index(self) -> int:
        """Get start index for current page"""
        return self.current_page * self.page_size
    
    @property
    def end_index(self) -> int:
        """Get end index (exclusive) for current page"""
        return min(self.start_index + self.page_size, self.total_items)
    
    @property
    def is_first_page(self) -> bool:
        """Check if this is the first page"""
        return self.current_page == 0
    
    @property
    def is_last_page(self) -> bool:
        """Check if this is the last page"""
        return self.current_page >= self.total_pages - 1
    
    @property
    def visible_range(self) -> tuple[int, int]:
        """Get start and end indices (inclusive, exclusive) for the current page"""
        return (self.start_index, self.end_index)
    
    @property
    def has_items(self) -> bool:
        """Check if there are any items"""
        return self.total_items > 0
    
    @property
    def items_on_page(self) -> int:
        """Get number of items on the current page"""
        return self.end_index - self.start_index
```

#### `PaginationController` (Abstract Base Class)

Core component that handles pagination logic and state management:

```python
class PaginationController(QObject):
    """
    Abstract base class for pagination controllers.
    Handles core pagination logic separate from UI.
    """
    # Signals
    stateChanged = Signal(PaginationState)  # Emitted when pagination state changes
    
    def __init__(self, page_size: int = 50, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._state = PaginationState(page_size=page_size)
    
    @property
    def state(self) -> PaginationState:
        """Get the current pagination state (immutable)"""
        return self._state
    
    def set_page_size(self, size: int) -> None:
        """Set the number of items per page"""
        if size > 0 and size != self._state.page_size:
            prev_first_item = self._state.start_index
            new_state = PaginationState(
                current_page=prev_first_item // size,  # Maintain same first visible item
                page_size=size,
                total_items=self._state.total_items
            )
            self._update_state(new_state)
    
    def set_total_items(self, count: int) -> None:
        """Set the total number of items"""
        if count != self._state.total_items:
            new_state = PaginationState(
                current_page=min(self._state.current_page, max(0, (count - 1) // self._state.page_size)),
                page_size=self._state.page_size,
                total_items=max(0, count)
            )
            self._update_state(new_state)
    
    def go_to_page(self, page: int) -> bool:
        """Go to a specific page with bounds checking"""
        page = max(0, min(page, self._state.total_pages - 1))
        if page != self._state.current_page:
            new_state = PaginationState(
                current_page=page,
                page_size=self._state.page_size,
                total_items=self._state.total_items
            )
            self._update_state(new_state)
            return True
        return False
    
    def next_page(self) -> bool:
        """Go to the next page if possible"""
        return not self._state.is_last_page and self.go_to_page(self._state.current_page + 1)
    
    def previous_page(self) -> bool:
        """Go to the previous page if possible"""
        return not self._state.is_first_page and self.go_to_page(self._state.current_page - 1)
    
    def first_page(self) -> bool:
        """Go to the first page"""
        return not self._state.is_first_page and self.go_to_page(0)
    
    def last_page(self) -> bool:
        """Go to the last page"""
        return not self._state.is_last_page and self.go_to_page(self._state.total_pages - 1)
    
    def navigate_to_item(self, index: int) -> bool:
        """Navigate to the page containing the specified item"""
        if 0 <= index < self._state.total_items:
            target_page = index // self._state.page_size
            return self.go_to_page(target_page)
        return False
    
    def is_item_visible(self, index: int) -> bool:
        """Check if an item index is on the current page"""
        start, end = self._state.visible_range
        return start <= index < end
    
    def _update_state(self, new_state: PaginationState) -> None:
        """Update state and notify listeners"""
        if (new_state.current_page != self._state.current_page or
            new_state.page_size != self._state.page_size or
            new_state.total_items != self._state.total_items):
            self._state = new_state
            self.stateChanged.emit(new_state)
            self._on_state_changed(new_state)
    
    def _on_state_changed(self, state: PaginationState) -> None:
        """
        Called when state changes - must be implemented by subclasses
        to update the view or model
        """
        raise NotImplementedError("Subclasses must implement _on_state_changed")
```

### 2. Data Provider Interfaces

#### `PaginationDataProvider` (Abstract Interface)

```python
class PaginationDataProvider(ABC):
    """
    Abstract interface for data providers that support pagination.
    This interface allows the pagination controller to work with
    different data sources without knowing their implementation details.
    """
    
    @abstractmethod
    def get_total_count(self) -> int:
        """Get the total number of items available"""
        pass
    
    @abstractmethod
    def get_page_items(self, start_index: int, count: int) -> List[Any]:
        """
        Get a page of items.
        
        Args:
            start_index: The index of the first item to retrieve
            count: Maximum number of items to retrieve
            
        Returns:
            List of items for the requested page
        """
        pass
    
    @property
    def supports_random_access(self) -> bool:
        """
        Whether the data source supports efficient random access by index.
        If False, the pagination controller will avoid page jumping.
        """
        return True
```

### 3. UI Components

#### `PaginationWidget` (Base UI Component)

```python
class PaginationWidget(QWidget):
    """
    Reusable pagination UI widget with navigation buttons and display.
    Works with any PaginationController to provide a consistent UI.
    """
    # Signals
    pageRequested = Signal(int)          # Request to go to specific page
    pageSizeChangeRequested = Signal(int) # Request to change page size
    
    def __init__(self, 
                 controller: Optional[PaginationController] = None,
                 page_sizes: List[int] = [25, 50, 100, 250, 500],
                 show_page_size: bool = True,
                 show_goto: bool = True,
                 show_status: bool = True,
                 parent: Optional[QWidget] = None):
        """
        Initialize pagination widget.
        
        Args:
            controller: Optional controller to connect to
            page_sizes: List of page size options to show in dropdown
            show_page_size: Whether to show the page size selector
            show_goto: Whether to show the "Go to page" input
            show_status: Whether to show the status label
            parent: Parent widget
        """
        super().__init__(parent)
        self.controller = controller
        self._setup_ui(page_sizes, show_page_size, show_goto, show_status)
        
        if controller:
            self.connect_controller(controller)
    
    # UI setup and connection methods...
```

## Implementation Strategy

### Specialized Controllers

For each specific pagination use case, create a specialized controller:

1. **ModelViewController** - For QAbstractItemModel-based views (table, tree)
2. **FileSystemController** - For file system browsing
3. **ListViewController** - For list views and widgets
4. **SearchResultsController** - For search results
5. **DatabaseRecordController** - For database records

These would inherit from `PaginationController` and implement the `_on_state_changed` method appropriately.

### Data Provider Implementations

1. **ModelDataProvider** - Wraps a QAbstractItemModel
2. **ListDataProvider** - Wraps a Python list or QListModel
3. **SqliteDataProvider** - Executes SQL queries with LIMIT/OFFSET
4. **FileSystemDataProvider** - Lists files/folders with pagination

## Implementation Plan

### Phase 1: Core Framework

1. Create base classes:
   - `PaginationState` data class
   - `PaginationController` abstract base class
   - `PaginationDataProvider` interface
   - `PaginationWidget` UI component

2. Implement utility functions:
   - Page calculation helpers
   - State conversion utilities

### Phase 2: Basic Providers and Controllers

1. Implement common data providers:
   - `ListDataProvider`
   - `ModelDataProvider`

2. Implement specialized controllers:
   - `ListViewController`
   - `ModelViewController`

### Phase 3: UI Component Refinement

1. Enhance `PaginationWidget` with:
   - Consistent styling with theme support
   - Accessibility features
   - Keyboard navigation
   - Multiple layout options

2. Create specialized UI components:
   - Compact version for limited space
   - Full-featured version with all controls
   - Minimal version with just navigation buttons

### Phase 4: Application Integration

1. Refactor existing pagination implementations:
   - Start with the simplest component (e.g., `SearchResultsPanel`)
   - Proceed to more complex components one by one

2. Update the UI to use the new pagination widgets

3. Add unit tests for the pagination framework

## Detailed Component Designs

### Model-based Pagination Controller

```python
class ModelViewController(PaginationController):
    """
    Pagination controller for QAbstractItemModel-based views.
    Can work with TableView, TreeView, or any view that uses a model.
    """
    
    def __init__(self, view: QAbstractItemView, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.view = view
        self.model = view.model()
        self._proxy_model = None
        
        # Create proxy model for pagination if needed
        if not isinstance(self.model, QPaginationProxyModel):
            self._proxy_model = QPaginationProxyModel()
            self._proxy_model.setSourceModel(self.model)
            self.view.setModel(self._proxy_model)
            self.model = self._proxy_model
        
        # Connect to model changes
        self._connect_model_signals()
        
        # Initial state setup
        self.set_total_items(self.get_total_row_count())
    
    def _connect_model_signals(self):
        """Connect to model signals for updates"""
        if hasattr(self.model, 'modelReset'):
            self.model.modelReset.connect(self._on_model_changed)
        if hasattr(self.model, 'rowsInserted'):
            self.model.rowsInserted.connect(self._on_model_changed)
        if hasattr(self.model, 'rowsRemoved'):
            self.model.rowsRemoved.connect(self._on_model_changed)
    
    def get_total_row_count(self):
        """Get total number of rows in the model"""
        if self._proxy_model:
            # Count rows from source model
            return self._proxy_model.sourceModel().rowCount()
        return self.model.rowCount()
    
    def _on_state_changed(self, state: PaginationState):
        """Update the view based on new state"""
        if self._proxy_model:
            self._proxy_model.setPaginationState(state)
            self.view.reset()
        else:
            # For models that handle their own pagination
            if hasattr(self.model, 'setPaginationState'):
                self.model.setPaginationState(state)
    
    def _on_model_changed(self):
        """Handle model data changes"""
        total_items = self.get_total_row_count()
        if total_items != self.state.total_items:
            self.set_total_items(total_items)
```

### List-based Pagination Controller

```python
class ListViewController(PaginationController):
    """
    Pagination controller for Python lists or list-like objects.
    Can be used with QListWidget or custom list displays.
    """
    
    def __init__(self, 
                 data_provider: Union[List, PaginationDataProvider],
                 update_callback: Callable[[List, PaginationState], None],
                 parent: Optional[QObject] = None):
        """
        Initialize list pagination controller.
        
        Args:
            data_provider: List of items or a PaginationDataProvider
            update_callback: Function called with (visible_items, state) when pagination changes
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Setup data provider
        if isinstance(data_provider, PaginationDataProvider):
            self.data_provider = data_provider
        else:
            # Wrap list in a provider
            self.data_provider = ListDataProvider(data_provider)
        
        self.update_callback = update_callback
        
        # Initial state setup
        self.set_total_items(self.data_provider.get_total_count())
    
    def _on_state_changed(self, state: PaginationState):
        """Update display with new page of items"""
        start, count = state.start_index, state.page_size
        visible_items = self.data_provider.get_page_items(start, count)
        self.update_callback(visible_items, state)
    
    def refresh(self):
        """Refresh data from provider and update display"""
        self.set_total_items(self.data_provider.get_total_count())
        self._on_state_changed(self.state)
```

### Compact Pagination Widget

```python
class CompactPaginationWidget(QWidget):
    """
    Compact pagination widget for use in constrained spaces.
    Provides essential navigation without taking much space.
    """
    
    # Signals
    pageRequested = Signal(int)
    
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()
        
        if controller:
            self.connect_controller(controller)
    
    def _setup_ui(self):
        """Setup minimal UI with just prev/next buttons and page indicator"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Prev button
        self.prev_btn = QToolButton()
        self.prev_btn.setText("◀")
        self.prev_btn.setToolTip("Previous Page")
        self.prev_btn.clicked.connect(self._on_prev_clicked)
        layout.addWidget(self.prev_btn)
        
        # Page indicator
        self.page_label = QLabel("1/1")
        self.page_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.page_label)
        
        # Next button
        self.next_btn = QToolButton()
        self.next_btn.setText("▶")
        self.next_btn.setToolTip("Next Page")
        self.next_btn.clicked.connect(self._on_next_clicked)
        layout.addWidget(self.next_btn)
    
    # Connection and event handling methods...
```

## Example Usage

### Simple List Widget with Pagination

```python
# Create a data list
items = ["Item " + str(i) for i in range(1, 1001)]

# Create a list widget to display items
list_widget = QListWidget()

# Update function to apply pagination to list widget
def update_list_display(visible_items, state):
    list_widget.clear()
    for item in visible_items:
        list_widget.addItem(item)
    status_label.setText(f"Showing {state.start_index + 1}-{state.end_index} of {state.total_items}")

# Create pagination controller
pagination_controller = ListViewController(items, update_list_display)

# Create and connect pagination widget
pagination_widget = PaginationWidget(pagination_controller)

# Layout
layout = QVBoxLayout()
layout.addWidget(list_widget)
status_label = QLabel()
layout.addWidget(status_label)
layout.addWidget(pagination_widget)
```

### Table View with Pagination

```python
# Create model and view
table_model = QStandardItemModel()
table_view = QTableView()
table_view.setModel(table_model)

# Populate model with sample data
for row in range(500):
    items = [QStandardItem(f"Item {row},{col}") for col in range(5)]
    table_model.appendRow(items)

# Create pagination controller for the table
pagination_controller = ModelViewController(table_view)

# Create and connect pagination widget
pagination_widget = PaginationWidget(pagination_controller)

# Layout
layout = QVBoxLayout()
layout.addWidget(table_view)
layout.addWidget(pagination_widget)
```

## Benefits

1. **Consistency**: All paginated components follow the same patterns and behavior
2. **Maintainability**: Centralized pagination logic reduces code duplication
3. **Flexibility**: The architecture supports different data sources and UI requirements
4. **Separation of Concerns**: Logic, data, and UI are cleanly separated
5. **Extensibility**: Easy to add new specialized controllers or UI components

## Migration Strategy

### Step 1: Core Framework Implementation
Create the base classes and interfaces in a new module `common/pagination/`

### Step 2: First Component Migration
Start with the `SearchResultsPanel` class as a test case:
1. Create a `SearchResultsController` extending `PaginationController`
2. Create a `SearchResultsProvider` implementing `PaginationDataProvider`
3. Replace the pagination UI with `PaginationWidget`
4. Update the panel to use the controller for pagination logic

### Step 3: Iterative Component Migration
Apply the same pattern to each paginated component, one at a time:
1. `PagedFileSystemModel` in the explorer
2. `IssueOnlyDialog` for issues
3. Table views throughout the application

### Step 4: Testing and Refinement
Test each migrated component thoroughly to ensure consistent behavior

## Conclusion

This pagination abstraction design provides a robust, flexible framework for implementing pagination across the application. By separating pagination logic from UI components and data providers, we achieve clean separation of concerns while maintaining consistent behavior and appearance.

The polymorphic design allows for specialized implementations where needed, while the common interfaces ensure that components work together seamlessly. This approach will reduce code duplication, improve maintainability, and provide a more consistent user experience throughout the application.

## Component-Specific Upgrade Plans

This section provides detailed, concrete steps for upgrading each existing pagination component to use the new unified pagination system.

### 1. SearchResultsPanel Upgrade (`plugins/explorer/professional_explorer.py`)

**Current State**: Custom pagination with hardcoded controls and logic

**Priority**: High (Good starter component - relatively simple)

**Timeline**: 3-4 days

#### Step-by-Step Implementation:

1. **Create SearchResultsDataProvider**
   ```python
   # File: plugins/explorer/search_results_provider.py
   class SearchResultsDataProvider(PaginationDataProvider):
       """Data provider for search results"""
       
       def __init__(self):
           self.results = []
       
       def get_total_count(self) -> int:
           return len(self.results)
       
       def get_page_items(self, start_index: int, count: int) -> List[Any]:
           end_index = min(start_index + count, len(self.results))
           return self.results[start_index:end_index]
       
       def add_result(self, result):
           """Add a new search result"""
           self.results.append(result)
       
       def clear_results(self):
           """Clear all results"""
           self.results.clear()
   ```

2. **Create SearchResultsController**
   ```python
   # File: plugins/explorer/search_results_controller.py
   class SearchResultsController(PaginationController):
       """Controller for search results pagination"""
       
       def __init__(self, results_widget, data_provider, parent=None):
           super().__init__(page_size=20, parent=parent)  # Match current page size
           self.results_widget = results_widget
           self.data_provider = data_provider
           
       def _on_state_changed(self, state: PaginationState):
           """Update the results widget display"""
           # Clear current results
           self.results_widget.clear()
           
           # Get items for current page
           visible_items = self.data_provider.get_page_items(
               state.start_index, state.page_size)
           
           # Add items to UI
           for item in visible_items:
               self._add_result_to_ui(item)
       
       def _add_result_to_ui(self, result):
           """Add a single result to the UI"""
           # Move existing _add_result_to_ui logic here
           pass
   ```

3. **Refactor SearchResultsPanel**
   ```python
   # Changes to plugins/explorer/professional_explorer.py
   class SearchResultsPanel(QFrame):
       def __init__(self, parent=None):
           super().__init__(parent)
           # ...existing setup...
           
           # Replace old pagination variables with new system
           self.data_provider = SearchResultsDataProvider()
           self.pagination_controller = SearchResultsController(
               self.results_list, self.data_provider, self)
           
           # Create new pagination widget
           self.pagination_widget = PaginationWidget(
               self.pagination_controller,
               show_page_size=False,  # Keep current minimal design
               show_goto=False
           )
           
           self._setup_ui_with_new_pagination()
       
       def _setup_ui_with_new_pagination(self):
           # Remove old pagination controls
           # Replace with self.pagination_widget
           pass
       
       def add_result(self, result):
           """Simplified - delegate to data provider"""
           self.data_provider.add_result(result)
           
           # Update total count in controller
           self.pagination_controller.set_total_items(
               self.data_provider.get_total_count())
       
       def clear_results(self):
           """Simplified - delegate to data provider"""
           self.data_provider.clear_results()
           self.pagination_controller.set_total_items(0)
   ```

4. **Remove Old Code**
   - Delete `_update_display()`, `_update_pagination()` methods
   - Remove `current_page`, `page_size`, `total_pages` variables
   - Remove old navigation button event handlers

**Testing Checklist**:
- [ ] Search results display correctly on first page
- [ ] Navigation between pages works
- [ ] Adding new results updates pagination correctly
- [ ] Clearing results resets pagination
- [ ] Page size changes work (if enabled)

---

### 2. PagedFileSystemModel Upgrade (`plugins/explorer/professional_explorer.py`)

**Current State**: Custom QSortFilterProxyModel with pagination in `filterAcceptsRow`

**Priority**: High (Central component in file explorer)

**Timeline**: 5-7 days

#### Step-by-Step Implementation:

1. **Create FileSystemDataProvider**
   ```python
   # File: plugins/explorer/filesystem_data_provider.py
   class FileSystemDataProvider(PaginationDataProvider):
       """Data provider for file system items"""
       
       def __init__(self, source_model, filter_pattern="*"):
           self.source_model = source_model
           self.filter_pattern = filter_pattern
           self.root_path = ""
           self._cached_items = []
           self._cache_valid = False
       
       def set_root_path(self, path: str):
           """Set the root directory path"""
           self.root_path = path
           self._invalidate_cache()
       
       def set_filter_pattern(self, pattern: str):
           """Set file filter pattern"""
           self.filter_pattern = pattern
           self._invalidate_cache()
       
       def get_total_count(self) -> int:
           self._ensure_cache_valid()
           return len(self._cached_items)
       
       def get_page_items(self, start_index: int, count: int) -> List[Any]:
           self._ensure_cache_valid()
           end_index = min(start_index + count, len(self._cached_items))
           return self._cached_items[start_index:end_index]
       
       def _ensure_cache_valid(self):
           """Ensure the cached items list is up to date"""
           if not self._cache_valid:
               self._build_cache()
               self._cache_valid = True
       
       def _build_cache(self):
           """Build cache of filtered items"""
           self._cached_items = []
           root_index = self.source_model.index(self.root_path)
           
           for row in range(self.source_model.rowCount(root_index)):
               index = self.source_model.index(row, 0, root_index)
               if self._item_matches_filter(index):
                   self._cached_items.append(row)  # Store source row indices
       
       def _item_matches_filter(self, index):
           """Check if item matches current filter"""
           # Always show directories
           if self.source_model.isDir(index):
               return True
           
           # Apply file pattern filter
           if self.filter_pattern and self.filter_pattern != "*":
               filename = self.source_model.fileName(index)
               return fnmatch.fnmatch(filename.lower(), self.filter_pattern.lower())
           
           return True
       
       def _invalidate_cache(self):
           """Mark cache as invalid"""
           self._cache_valid = False
   ```

2. **Create FileSystemController**
   ```python
   # File: plugins/explorer/filesystem_controller.py
   class FileSystemController(PaginationController):
       """Controller for file system pagination"""
       
       def __init__(self, proxy_model, data_provider, parent=None):
           super().__init__(page_size=200, parent=parent)  # Match current default
           self.proxy_model = proxy_model
           self.data_provider = data_provider
           
           # Set up the proxy model to use our pagination logic
           self.proxy_model.pagination_controller = self
           
       def _on_state_changed(self, state: PaginationState):
           """Update the proxy model filtering"""
           # Trigger proxy model to re-filter with new pagination state
           self.proxy_model.invalidateFilter()
       
       def set_root_path(self, path: str):
           """Set root path and update pagination"""
           self.data_provider.set_root_path(path)
           self.set_total_items(self.data_provider.get_total_count())
       
       def set_filter_pattern(self, pattern: str):
           """Set filter pattern and reset to first page"""
           self.data_provider.set_filter_pattern(pattern)
           self.set_total_items(self.data_provider.get_total_count())
           self.go_to_page(0)  # Reset to first page on filter change
   ```

3. **Refactor PagedFileSystemModel**
   ```python
   # Changes to plugins/explorer/professional_explorer.py
   class PagedFileSystemModel(QSortFilterProxyModel):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.source_model = QFileSystemModel()
           self.setSourceModel(self.source_model)
           
           # Replace old pagination variables with new system
           self.data_provider = FileSystemDataProvider(self.source_model)
           self.pagination_controller = FileSystemController(
               self, self.data_provider, parent)
           
           # Remove old pagination variables
           # self.items_per_page, self.current_page, etc.
       
       def filterAcceptsRow(self, source_row: int, source_parent):
           """Simplified filter that delegates to pagination controller"""
           source_index = self.source_model.index(source_row, 0, source_parent)
           if not source_index.isValid():
               return False
           
           # Always show directories
           if self.source_model.isDir(source_index):
               return True
           
           # Get visible items for current page from data provider
           if hasattr(self, 'pagination_controller'):
               state = self.pagination_controller.state
               visible_items = self.data_provider.get_page_items(
                   state.start_index, state.page_size)
               return source_row in visible_items
           
           return True
       
       def set_root_path(self, path: str):
           """Delegate to controller"""
           result = self.source_model.setRootPath(path)
           if hasattr(self, 'pagination_controller'):
               self.pagination_controller.set_root_path(path)
           return self.mapFromSource(result)
       
       def set_filter_pattern(self, pattern: str):
           """Delegate to controller"""
           if hasattr(self, 'pagination_controller'):
               self.pagination_controller.set_filter_pattern(pattern)
       
       # Remove old pagination methods
       # def set_items_per_page, def set_page, def next_page, etc.
   ```

4. **Update ProfessionalExplorer**
   ```python
   # Changes to ProfessionalExplorer class
   def _setup_paging_controls(self):
       """Replace old paging controls with new pagination widget"""
       # Create pagination widget connected to file model controller
       self.pagination_widget = PaginationWidget(
           self.file_model.pagination_controller,
           page_sizes=[50, 100, 200, 500, 1000],
           show_page_size=True,
           show_goto=False,
           show_status=True
       )
       
       # Remove old paging control code
   ```

**Testing Checklist**:
- [ ] File listing displays correctly
- [ ] Pagination navigation works
- [ ] File filtering works with pagination
- [ ] Directory navigation resets pagination
- [ ] Page size changes work correctly
- [ ] Performance is acceptable for large directories

---

### 3. IssueOnlyDialog Upgrade (`workspace/issue_only_dialog_paged.py`)

**Current State**: Custom pagination with database-style controls

**Priority**: Medium (Specialized component, less frequently used)

**Timeline**: 4-5 days

#### Step-by-Step Implementation:

1. **Create IssueDataProvider**
   ```python
   # File: workspace/issue_data_provider.py
   class IssueDataProvider(PaginationDataProvider):
       """Data provider for issue records"""
       
       def __init__(self):
           self.issue_records = []
           self.issue_indices = []  # Original indices in main table
       
       def load_issues(self, main_model):
           """Load issue records from the main model"""
           self.issue_records = []
           self.issue_indices = []
           
           # Extract records with issues
           for row in range(main_model.rowCount()):
               record = main_model.get_record(row)
               if self._has_issues(record):
                   self.issue_records.append(record)
                   self.issue_indices.append(row)
       
       def get_total_count(self) -> int:
           return len(self.issue_records)
       
       def get_page_items(self, start_index: int, count: int) -> List[Any]:
           end_index = min(start_index + count, len(self.issue_records))
           return self.issue_records[start_index:end_index]
       
       def get_original_index(self, issue_index: int) -> int:
           """Get original index in main table for an issue record"""
           if 0 <= issue_index < len(self.issue_indices):
               return self.issue_indices[issue_index]
           return -1
       
       def _has_issues(self, record):
           """Check if record has issues"""
           # Implement issue detection logic
           pass
   ```

2. **Create IssueDialogController**
   ```python
   # File: workspace/issue_dialog_controller.py
   class IssueDialogController(PaginationController):
       """Controller for issue dialog pagination"""
       
       def __init__(self, table_model, data_provider, parent=None):
           # Use existing default page size from dialog
           super().__init__(page_size=50, parent=parent)
           self.table_model = table_model
           self.data_provider = data_provider
       
       def _on_state_changed(self, state: PaginationState):
           """Update table model with current page data"""
           # Get visible issues for current page
           visible_issues = self.data_provider.get_page_items(
               state.start_index, state.page_size)
           
           # Update table model
           self.table_model.beginResetModel()
           self.table_model.visible_records = visible_issues
           self.table_model.endResetModel()
       
       def load_issues(self, main_model):
           """Load issues and set up pagination"""
           self.data_provider.load_issues(main_model)
           self.set_total_items(self.data_provider.get_total_count())
   ```

3. **Refactor IssueOnlyDialog**
   ```python
   # Changes to workspace/issue_only_dialog_paged.py
   class IssueOnlyDialog(QDialog):
       def __init__(self, parent=None):
           super().__init__(parent)
           # ...existing initialization...
           
           # Replace old pagination state with new system
           self.data_provider = IssueDataProvider()
           self.pagination_controller = IssueDialogController(
               self.table_model, self.data_provider, self)
           
           # Create new pagination widget
           self.pagination_widget = PaginationWidget(
               self.pagination_controller,
               page_sizes=DEFAULT_PAGE_SIZES,
               show_page_size=True,
               show_goto=True,
               show_status=True
           )
           
           self._create_widgets_with_new_pagination()
       
       def _create_widgets_with_new_pagination(self):
           """Update widget creation to use new pagination"""
           # Remove old pagination controls
           # Use self.pagination_widget instead
           
           # Remove these old widgets:
           # self.first_page_button, self.prev_page_button, etc.
           # self.page_size_combo, self.goto_page_spin, etc.
           
           pass
       
       def _load_issue_records(self):
           """Simplified issue loading"""
           # Delegate to controller
           self.pagination_controller.load_issues(main_window.get_current_model())
       
       # Remove old pagination methods:
       # def _update_pagination_controls, def _on_page_size_changed, etc.
   ```

4. **Update Layout**
   ```python
   def _setup_layout(self):
       """Update layout to use new pagination widget"""
       # ...existing layout code...
       
       # Replace old pagination layout with:
       layout.addWidget(self.pagination_widget)
       
       # Remove old pagination control layout code
   ```

**Testing Checklist**:
- [ ] Issue records load and display correctly
- [ ] Pagination navigation works
- [ ] Page size changes work
- [ ] "Go to Record" functionality still works
- [ ] Find/replace within issues still works
- [ ] Performance is acceptable

---

### 4. TablePagerBase Upgrade (`subcmp/table_nav_widget.py`)

**Current State**: Abstract base class used by various table components

**Priority**: High (Affects multiple components)

**Timeline**: 3-4 days (plus testing time for dependent components)

#### Step-by-Step Implementation:

1. **Create TableDataProvider**
   ```python
   # File: subcmp/table_data_provider.py
   class TableDataProvider(PaginationDataProvider):
       """Data provider for table models"""
       
       def __init__(self, model):
           self.model = model
           self._connect_model_signals()
       
       def _connect_model_signals(self):
           """Connect to model change signals"""
           if self.model:
               try:
                   self.model.modelReset.connect(self._on_model_changed)
                   self.model.rowsInserted.connect(self._on_model_changed)
                   self.model.rowsRemoved.connect(self._on_model_changed)
               except AttributeError:
                   pass
       
       def get_total_count(self) -> int:
           return self.model.rowCount() if self.model else 0
       
       def get_page_items(self, start_index: int, count: int) -> List[Any]:
           """For table models, return row indices rather than actual data"""
           end_index = min(start_index + count, self.get_total_count())
           return list(range(start_index, end_index))
       
       def _on_model_changed(self):
           """Handle model changes"""
           # Emit signal that can be connected to controller
           pass
   ```

2. **Create New TablePaginator**
   ```python
   # File: subcmp/table_paginator.py
   class TablePaginator(PaginationController):
       """New table paginator using unified system"""
       
       def __init__(self, table, model, page_size=100, parent=None):
           super().__init__(page_size=page_size, parent=parent)
           self.table = table
           self.model = model
           self.data_provider = TableDataProvider(model)
           
           # Set initial total
           self.set_total_items(self.data_provider.get_total_count())
           
           # Connect to model changes
           self._connect_model_signals()
       
       def _connect_model_signals(self):
           """Connect to model signals for auto-updates"""
           if self.model:
               try:
                   self.model.modelReset.connect(self._on_model_reset)
                   self.model.rowsInserted.connect(self._on_model_reset)
                   self.model.rowsRemoved.connect(self._on_model_reset)
               except AttributeError:
                   pass
       
       def _on_model_reset(self, *args):
           """Handle model reset"""
           self.set_total_items(self.data_provider.get_total_count())
       
       def _on_state_changed(self, state: PaginationState):
           """Update table view to show only current page rows"""
           if not self.table:
               return
           
           total_rows = self.data_provider.get_total_count()
           start_idx, end_idx = state.visible_range
           
           # Hide/show rows based on current page
           for row in range(total_rows):
               should_show = start_idx <= row < end_idx
               self.table.setRowHidden(row, not should_show)
       
       # Backward compatibility methods
       def go_first(self):
           return self.first_page()
       
       def go_last(self):
           return self.last_page()
       
       def go_prev(self):
           return self.previous_page()
       
       def go_next(self):
           return self.next_page()
       
       def get_page_indices(self):
           return self.state.visible_range
       
       def refresh(self):
           self._on_model_reset()
   ```

3. **Update TablePagerBase for Backward Compatibility**
   ```python
   # Changes to subcmp/table_nav_widget.py
   class TablePagerBase(QObject):
       """
       Updated TablePagerBase that wraps the new TablePaginator
       Maintains backward compatibility while using new system
       """
       # Keep existing signals for compatibility
       pageChanged = Signal(int, int)
       pageSizeChanged = Signal(int)
       
       def __init__(self, table, table_model, page_size=100, parent=None):
           super().__init__(parent)
           
           # Create new paginator
           self.paginator = TablePaginator(table, table_model, page_size, parent)
           
           # Connect new signals to old signals for compatibility
           self.paginator.stateChanged.connect(self._on_state_changed)
           
           # Backward compatibility properties
           self.table = table
           self.model = table_model
           self.page_size = page_size
           
       def _on_state_changed(self, state):
           """Convert new state to old signals"""
           self.current_page = state.current_page
           self.total_pages = state.total_pages
           self.total_rows = state.total_items
           
           # Emit old-style signals
           self.pageChanged.emit(state.current_page, state.total_pages)
       
       # Delegate all methods to new paginator
       def set_page_size(self, size):
           self.paginator.set_page_size(size)
           self.page_size = size
           self.pageSizeChanged.emit(size)
       
       def go_to_page(self, page):
           return self.paginator.go_to_page(page)
       
       def go_first(self):
           return self.paginator.first_page()
       
       def go_last(self):
           return self.paginator.last_page()
       
       def go_prev(self):
           return self.paginator.previous_page()
       
       def go_next(self):
           return self.paginator.next_page()
       
       def get_page_info(self):
           state = self.paginator.state
           return (state.current_page, state.total_pages, 
                   state.page_size, state.total_items)
       
       def get_page_indices(self):
           return self.paginator.state.visible_range
       
       def refresh(self):
           self.paginator._on_model_reset()
       
       def ensure_row_visible(self, row):
           return self.paginator.navigate_to_item(row)
       
       # Abstract method - now optional
       def update_table_view(self):
           """No longer needed - handled by paginator"""
           pass
   ```

**Testing Checklist**:
- [ ] All existing table components still work
- [ ] Pagination behavior is identical to before
- [ ] Performance is not degraded
- [ ] Backward compatibility is maintained
- [ ] New pagination widgets can be used

---

### 5. Translation History Components

**Current State**: Various history dialogs and views with pagination

**Priority**: Medium

**Timeline**: 3-4 days

#### Step-by-Step Implementation:

1. **Create DatabasePaginator Base Class**
   ```python
   # File: common/pagination/database_paginator.py
   class DatabasePaginator(BasePaginator):
       """
       Specialized paginator for database-backed data sources.
       Provides efficient SQL query pagination using LIMIT/OFFSET.
       """
       
       def __init__(self, database_connection, base_query, page_size=50, parent=None):
           super().__init__(page_size, PaginationMode.DATABASE, parent)
           self.db_connection = database_connection
           self.base_query = base_query
           self.sort_column = None
           self.sort_order = 'ASC'
           self.where_conditions = []
           
       def set_sort(self, column, ascending=True):
           """Set sorting for database queries"""
           self.sort_column = column
           self.sort_order = 'ASC' if ascending else 'DESC'
           self._refresh_total_count()
           self._update_view()
           
       def add_filter(self, condition):
           """Add WHERE condition to queries"""
           self.where_conditions.append(condition)
           self._refresh_total_count()
           self.go_to_page(0)  # Reset to first page
           
       def _build_count_query(self):
           """Build query to count total records"""
           query = f"SELECT COUNT(*) FROM ({self.base_query})"
           if self.where_conditions:
               query += " WHERE " + " AND ".join(self.where_conditions)
           return query
           
       def _build_page_query(self):
           """Build query for current page"""
           query = self.base_query
           if self.where_conditions:
               query += " WHERE " + " AND ".join(self.where_conditions)
           if self.sort_column:
               query += f" ORDER BY {self.sort_column} {self.sort_order}"
           query += f" LIMIT {self.page_size} OFFSET {self.current_page * self.page_size}"
           return query
           
       def _refresh_total_count(self):
           """Update total count from database"""
           count_query = self._build_count_query()
           cursor = self.db_connection.execute(count_query)
           total = cursor.fetchone()[0]
           self.set_total_items(total)
           
       def get_page_data(self):
           """Execute query and return data for current page"""
           page_query = self._build_page_query()
           cursor = self.db_connection.execute(page_query)
           return cursor.fetchall()
   ```

2. **Create HistoryDataProvider**
   ```python
   # File: pref/tran_history/history_data_provider.py
   class HistoryDataProvider(PaginationDataProvider):
       """
       Data provider for translation history with dual mode support.
       Handles both database view and search result view modes.
       """
       
       def __init__(self, translation_db):
           self.translation_db = translation_db
           self.mode = PagingMode.DatabaseView
           self.search_results = []
           self.current_filters = []
           self.sort_column = 0
           self.sort_ascending = True
           
       def set_mode(self, mode: PagingMode):
           """Switch between database and search result modes"""
           self.mode = mode
           
       def set_search_results(self, results):
           """Set search results for search mode"""
           self.search_results = results
           
       def get_total_count(self) -> int:
           if self.mode == PagingMode.DatabaseView:
               return self.translation_db.get_total_record_count(self.current_filters)
           else:
               return len(self.search_results)
               
       def get_page_items(self, start_index: int, count: int) -> List[Any]:
           if self.mode == PagingMode.DatabaseView:
               return self.translation_db.get_records_page(
                   start_index, count, self.current_filters, 
                   self.sort_column, self.sort_ascending)
           else:
               end_index = min(start_index + count, len(self.search_results))
               return self.search_results[start_index:end_index]
               
       def set_filters(self, filters):
           """Set database filters"""
           self.current_filters = filters
           
       def set_sort(self, column, ascending=True):
           """Set sort order"""
           self.sort_column = column
           self.sort_ascending = ascending
   ```

3. **Create HistoryController**
   ```python
   # File: pref/tran_history/history_controller.py
   class HistoryController(BasePaginator):
       """
       Controller for translation history dialog pagination.
       Manages dual modes and complex state synchronization.
       """
       
       def __init__(self, history_dialog, data_provider, page_size=22, parent=None):
           super().__init__(page_size, PaginationMode.DATABASE, parent)
           self.history_dialog = history_dialog
           self.data_provider = data_provider
           self.current_mode = PagingMode.DatabaseView
           
           # Separate page state for each mode
           self.database_page = 0
           self.search_page = 0
           
       def switch_mode(self, mode: PagingMode):
           """Switch between database and search modes"""
           # Save current page for current mode
           if self.current_mode == PagingMode.DatabaseView:
               self.database_page = self.current_page
           else:
               self.search_page = self.current_page
               
           # Switch to new mode
           self.current_mode = mode
           self.data_provider.set_mode(mode)
           
           # Restore page for new mode and update total
           self.set_total_items(self.data_provider.get_total_count())
           
           target_page = self.database_page if mode == PagingMode.DatabaseView else self.search_page
           self.go_to_page(target_page)
           
       def set_search_results(self, results):
           """Set search results and switch to search mode"""
           self.data_provider.set_search_results(results)
           self.switch_mode(PagingMode.SearchView)
           
       def _on_state_changed(self, state: PaginationState):
           """Update the history dialog display"""
           # Get page data from provider
           page_data = self.data_provider.get_page_items(
               state.start_index, state.page_size)
           
           # Update dialog table
           self.history_dialog.update_table_display(page_data, state)
           
           # Update mode-specific UI elements
           if self.current_mode == PagingMode.DatabaseView:
               self.database_page = state.current_page
           else:
               self.search_page = state.current_page
   ```

4. **Refactor TranslationHistoryDialog**
   ```python
   # Major changes to pref/tran_history/translation_db_gui.py
   class TranslationHistoryDialog(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           
           # Replace old pagination state with new system
           self.data_provider = HistoryDataProvider(self.db)
           self.pagination_controller = HistoryController(
               self, self.data_provider, parent=self)
           
           # Connect to settings for page size
           settings = QSettings("POEditor", "Settings")
           page_size = int(settings.value("history_table_page_size", 22))
           self.pagination_controller.set_page_size(page_size)
           
           # Create pagination widget
           self.pagination_widget = PaginationWidget(
               self.pagination_controller,
               page_sizes=[10, 22, 50, 100, 250],
               show_page_size=True,
               show_goto=True,
               show_status=True
           )
           
           self._setup_ui_with_new_pagination()
           
       def _setup_ui_with_new_pagination(self):
           """Update UI to use new pagination system"""
           # Remove old pagination controls and replace with pagination_widget
           # Update layout to include new controls
           pass
           
       def update_table_display(self, page_data, state: PaginationState):
           """Update table with new page data"""
           # Clear current table
           self.table_model.beginResetModel()
           
           # Update model with page data
           self.table_model.records = page_data
           
           # Update model and refresh display
           self.table_model.endResetModel()
           
           # Update status display
           self._update_status_display(state)
           
       def switch_to_search_mode(self, search_results):
           """Switch to search result pagination mode"""
           self.pagination_controller.set_search_results(search_results)
           
       def switch_to_database_mode(self):
           """Switch to database pagination mode"""
           self.pagination_controller.switch_mode(PagingMode.DatabaseView)
           
       # Remove old pagination methods:
       # def _update_paging_controls, def _on_page_changed, etc.
   ```

**Testing Checklist**:
- [ ] Database pagination performance with large datasets
- [ ] Mode switching preserves page state
- [ ] Search result pagination works correctly
- [ ] Settings integration functions properly
- [ ] Sorting works with pagination
- [ ] Find/replace integration preserved
- [ ] Memory usage is acceptable

---

### 7. Paged Search Navigation Bar Upgrade (`pref/tran_history/paged_search_nav_bar.py`)

**Current State**: Custom pagination for search result navigation

**Priority**: Medium (Supporting component for translation history)

**Timeline**: 3-4 days

#### Step-by-Step Implementation:

1. **Create SearchNavDataProvider**
   ```python
   # File: pref/tran_history/search_nav_data_provider.py
   class SearchNavDataProvider(PaginationDataProvider):
       """Data provider for search navigation bar"""
       
       def __init__(self):
           self.found_indices = []
           self.found_row_ids = []
           self.current_highlight = -1
           
       def set_search_results(self, indices, row_ids):
           """Set search results"""
           self.found_indices = indices
           self.found_row_ids = row_ids
           
       def get_total_count(self) -> int:
           return len(self.found_indices)
           
       def get_page_items(self, start_index: int, count: int) -> List[Any]:
           end_index = min(start_index + count, len(self.found_indices))
           return [(self.found_indices[i], self.found_row_ids[i]) 
                   for i in range(start_index, end_index)]
                   
       def set_highlight(self, index):
           """Set currently highlighted item"""
           self.current_highlight = index
   ```

2. **Update PagedSearchNavBar**
   ```python
   # Changes to pref/tran_history/paged_search_nav_bar.py
   class PagedSearchNavBar(QDockWidget):
       def __init__(self, title="Search Results", parent=None):
           super().__init__(title, parent)
           
           # Replace old pagination with new system
           self.data_provider = SearchNavDataProvider()
           self.pagination_controller = CollectionPaginator(
               items=[], 
               page_size=50,  # Keep existing PAGE_SIZE
               update_callback=self._update_list_display,
               parent=self
           )
           
           self._setup_ui_with_new_pagination()
           
       def _update_list_display(self, visible_items, state):
           """Update list widget with visible items"""
           self.list_widget.clear()
           
           for index, (found_index, row_id) in enumerate(visible_items):
               item = QListWidgetItem(f"Row {found_index}: {row_id}")
               item.setData(Qt.UserRole, (found_index, row_id))
               self.list_widget.addItem(item)
           
           # Update highlight if needed
           self._update_highlight_display()
           
       def set_search_results(self, indices, row_ids):
           """Set new search results"""
           self.data_provider.set_search_results(indices, row_ids)
           self.pagination_controller.set_items(
               list(zip(indices, row_ids)))
   ```

### 8. Main Window Table Integration

**Current State**: Uses TablePagerBase (will be updated automatically)

**Priority**: Critical (Core application functionality)

**Timeline**: 2-3 days (verification and integration testing)

#### Implementation Notes:
- Main table should automatically benefit from TablePagerBase upgrade
- Verify settings integration with `EditorSettingsWidget`
- Test performance with large PO files
- Ensure find/replace operations work correctly with pagination
- Verify navigation features work with new pagination

### 9. Settings Integration Upgrade (`pref/settings/editor_settings_widget.py`)

**Current State**: Provides settings for pagination parameters

**Priority**: Medium (Supporting component)

**Timeline**: 2-3 days

#### Step-by-Step Implementation:

1. **Create Settings Bridge**
   ```python
   # File: common/pagination/settings_bridge.py
   class PaginationSettingsBridge(QObject):
       """
       Bridge between QSettings and pagination components.
       Provides unified settings management for all pagination.
       """
       
       settingsChanged = Signal(str, dict)  # component_id, settings_dict
       
       def __init__(self):
           super().__init__()
           self.settings = QSettings("POEditor", "Settings")
           self.registered_components = {}
           
       def register_component(self, component_id, paginator, default_settings):
           """Register a paginated component"""
           self.registered_components[component_id] = {
               'paginator': paginator,
               'defaults': default_settings
           }
           
           # Load and apply settings
           self._load_component_settings(component_id)
           
       def _load_component_settings(self, component_id):
           """Load settings for a component"""
           component = self.registered_components[component_id]
           paginator = component['paginator']
           defaults = component['defaults']
           
           # Load page size
           page_size = int(self.settings.value(
               f"{component_id}_page_size", 
               defaults.get('page_size', 50)))
           paginator.set_page_size(page_size)
           
       def update_component_setting(self, component_id, setting_name, value):
           """Update a setting for a component"""
           setting_key = f"{component_id}_{setting_name}"
           self.settings.setValue(setting_key, value)
           
           # Apply to component
           if component_id in self.registered_components:
               paginator = self.registered_components[component_id]['paginator']
               if setting_name == 'page_size':
                   paginator.set_page_size(value)
                   
           # Emit change signal
           self.settingsChanged.emit(component_id, {setting_name: value})
   ```

2. **Update EditorSettingsWidget**
   ```python
   # Changes to pref/settings/editor_settings_widget.py
   class EditorSettingsWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           
           # Create settings bridge
           self.pagination_settings = PaginationSettingsBridge()
           
           # Setup UI (keep existing)
           self._setup_ui()
           
           # Connect to bridge instead of direct QSettings
           self.main_table_page_size.valueChanged.connect(
               lambda v: self.pagination_settings.update_component_setting(
                   "main_table", "page_size", v))
           self.history_table_page_size.valueChanged.connect(
               lambda v: self.pagination_settings.update_component_setting(
                   "history_table", "page_size", v))
   ```

## Enhanced Architecture Considerations

### Database Optimization

For database-backed pagination, several optimizations are crucial:

1. **Index Strategy**
   ```sql
   -- Add indexes for common pagination scenarios
   CREATE INDEX idx_translation_history_timestamp ON translation_history(timestamp DESC);
   CREATE INDEX idx_translation_history_msgid ON translation_history(msgid);
   CREATE INDEX idx_composite_sort ON translation_history(timestamp DESC, msgid);
   ```

2. **Query Optimization**
   ```python
   # Use prepared statements for repeated pagination queries
   class OptimizedDatabasePaginator(DatabasePaginator):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self._prepared_statements = {}
           
       def _get_prepared_statement(self, query_type):
           """Get or create prepared statement"""
           if query_type not in self._prepared_statements:
               self._prepared_statements[query_type] = self.db_connection.prepare(
                   self._build_query_template(query_type))
           return self._prepared_statements[query_type]
   ```

### Memory Management

For large datasets, implement smart memory management:

```python
class MemoryEfficientPaginator(BasePaginator):
    """
    Paginator with memory management for large datasets.
    Implements LRU cache for page data and automatic garbage collection.
    """
    
    def __init__(self, *args, cache_size=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_cache = {}
        self.cache_size = cache_size
        self.access_order = []
        
    def _cache_page_data(self, page, data):
        """Cache page data with LRU eviction"""
        if len(self.page_cache) >= self.cache_size:
            # Evict least recently used page
            lru_page = self.access_order.pop(0)
            del self.page_cache[lru_page]
            
        self.page_cache[page] = data
        self.access_order.append(page)
        
    def get_cached_page_data(self, page):
        """Get page data from cache"""
        if page in self.page_cache:
            # Move to end (most recently used)
            self.access_order.remove(page)
            self.access_order.append(page)
            return self.page_cache[page]
        return None
```

This enhanced component-specific upgrade plan now covers all pagination components in the application, including the preferences system and database components that were initially missed. The plan provides comprehensive implementation details, risk assessment, and optimization strategies for a complete pagination system overhaul.
