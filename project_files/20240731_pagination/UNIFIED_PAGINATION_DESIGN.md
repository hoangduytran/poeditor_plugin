# Unified Pagination System Design

**Date:** July 13, 2025  
**Author:** Development Team

## 1. Executive Summary

This document outlines the design and implementation plan for a unified pagination system across the POEditor application. The goal is to centralize pagination controls, avoid code duplication, and enable polymorphism through a clean separation of concerns between the pagination logic and UI components.

## 2. Current State Analysis

The application currently implements pagination in several distinct components:

1. **TablePagerBase** (`subcmp/table_nav_widget.py`): 
   - An existing abstract class for table pagination
   - Already provides navigation methods and page size management
   - Requires subclasses to implement `update_table_view()`

2. **PagedFileSystemModel** (`plugins/explorer/professional_explorer.py`):
   - Custom implementation for file system model pagination
   - Contains methods for page navigation and size configuration
   - Implements filtering through `filterAcceptsRow()`

3. **SearchResultsPanel** (`plugins/explorer/professional_explorer.py`):
   - Self-contained panel with its own pagination controls
   - Maintains internal page state and navigation logic

4. **IssueOnlyDialog** (`workspace/issue_only_dialog_paged.py`):
   - Dialog with pagination for issue records
   - Implements custom pagination UI controls

5. **BaseNavRecord** (`workspace/find_replace_types.py`):
   - Data class with pagination attributes for records

This fragmented approach leads to duplicated code, inconsistent user experience, and increased maintenance complexity.

## 3. Design Principles

Our design follows these core principles:

1. **Separation of Concerns**: 
   - Clear separation between pagination logic and UI representation
   - Abstract interfaces defining pagination behavior

2. **Polymorphism**: 
   - Common interface for all pagination implementations
   - Support for specialized behavior through inheritance

3. **Reusability**: 
   - Standardized components that can be used across the application
   - Configurable options to adapt to different contexts

4. **Maintainability**: 
   - Centralized logic for common pagination calculations
   - Reduced code duplication

5. **User Experience**: 
   - Consistent pagination controls throughout the application
   - Standardized behavior for a cohesive feel

## 4. Architecture Overview

The architecture consists of three distinct layers:

### 4.1. Data Layer

The foundation of the pagination system, managing the state and calculations.

```
IPaginator (Abstract Interface)
    ├── Core pagination state (current_page, page_size, etc.)
    ├── Navigation methods (next_page, prev_page, etc.)
    └── Abstract methods (e.g., _update_view)
```

### 4.2. Implementation Layer

Concrete implementations of the pagination interface for different data sources.

```
IPaginator
    ├── ModelPaginator (for QAbstractItemModel-based data)
    │   ├── TablePaginator (for table views)
    │   └── TreePaginator (for tree views)
    ├── ProxyModelPaginator (for filter proxy models)
    │   └── FileSystemPaginator (specialized for file system)
    ├── CollectionPaginator (for lists and arrays)
    │   └── SearchResultsPaginator (for search results)
    └── DatabasePaginator (for database queries)
```

### 4.3. Presentation Layer

UI components that visualize and interact with pagination state.

```
IPaginationWidget (Abstract UI Interface)
    ├── StandardPaginationBar (Common pagination controls)
    │   ├── CompactPaginationBar (Minimal controls)
    │   └── EnhancedPaginationBar (Full-featured controls)
    └── CustomPaginationWidgets
        ├── PagedNavScrollbar (Visual scrollbar with pages)
        └── MiniPaginationBar (Minimal indicator dots)
```

## 5. Detailed Design

### 5.1. Core Interface (IPaginator)

The `IPaginator` interface defines the core contract for all pagination implementations:

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal

class PaginationMode(Enum):
    """Different pagination modes across the application"""
    DATABASE = "database"
    SEARCH_RESULTS = "search"
    FILE_SYSTEM = "files"
    HISTORY = "history"
    TABLE = "table"
    CUSTOM = "custom"

@dataclass
class PageInfo:
    """Information about the current pagination state"""
    current_page: int = 0
    total_pages: int = 1
    page_size: int = 50
    total_items: int = 0
    start_index: int = 0
    end_index: int = 0
    
    @property
    def is_first_page(self) -> bool:
        return self.current_page == 0
    
    @property
    def is_last_page(self) -> bool:
        return self.current_page >= self.total_pages - 1


class IPaginator(QObject, ABC):
    """
    Abstract interface for pagination across the application.
    Provides common pagination functionality that specialized implementations must support.
    """
    # Signals
    pageChanged = Signal(int, int)  # (current_page, total_pages)
    pageSizeChanged = Signal(int)   # new page size
    
    def __init__(self, 
                 page_size: int = 50, 
                 mode: PaginationMode = PaginationMode.CUSTOM,
                 parent: Optional[QObject] = None):
        """Initialize the paginator with basic settings"""
        super().__init__(parent)
        self.page_size = page_size
        self.current_page = 0
        self.total_items = 0
        self.total_pages = 1
        self.mode = mode
    
    @abstractmethod
    def set_page_size(self, size: int) -> None:
        """Set the number of items per page"""
        pass
    
    @abstractmethod
    def go_to_page(self, page: int) -> bool:
        """Go to a specific page with bounds checking"""
        pass
    
    @abstractmethod
    def next_page(self) -> bool:
        """Go to the next page if possible"""
        pass
    
    @abstractmethod
    def prev_page(self) -> bool:
        """Go to the previous page if possible"""
        pass
    
    @abstractmethod
    def first_page(self) -> bool:
        """Go to the first page"""
        pass
    
    @abstractmethod
    def last_page(self) -> bool:
        """Go to the last page"""
        pass
    
    @abstractmethod
    def set_total_items(self, count: int) -> None:
        """Set the total number of items and recalculate pages"""
        pass
    
    @abstractmethod
    def get_page_info(self) -> PageInfo:
        """Get current pagination state"""
        pass
    
    @abstractmethod
    def get_visible_range(self) -> tuple[int, int]:
        """Get the start and end indices for the current page"""
        pass
    
    @abstractmethod
    def is_item_visible(self, index: int) -> bool:
        """Check if an item index is on the current page"""
        pass
    
    @abstractmethod
    def navigate_to_item(self, index: int) -> bool:
        """Navigate to the page containing the specified item"""
        pass
    
    @abstractmethod
    def _recalculate_pages(self) -> None:
        """Recalculate total pages based on item count and page size"""
        pass
    
    @abstractmethod
    def _update_view(self) -> None:
        """Update the view to show the current page - must be implemented by subclasses"""
        pass
```

### 5.2. Base Implementation (BasePaginator)

The `BasePaginator` provides a standard implementation of the interface:

```python
class BasePaginator(IPaginator):
    """
    Base implementation of the IPaginator interface.
    Provides standard pagination functionality that more specialized paginators can inherit.
    """
    
    def set_page_size(self, size: int) -> None:
        """Set the number of items per page"""
        if size > 0 and size != self.page_size:
            self.page_size = size
            self._recalculate_pages()
            self.pageSizeChanged.emit(size)
            self._update_view()
    
    def go_to_page(self, page: int) -> bool:
        """Go to a specific page with bounds checking"""
        page = max(0, min(page, self.total_pages - 1))
        if page != self.current_page:
            self.current_page = page
            self.pageChanged.emit(self.current_page, self.total_pages)
            self._update_view()
            return True
        return False
    
    def next_page(self) -> bool:
        """Go to the next page if possible"""
        return self.go_to_page(self.current_page + 1)
    
    def prev_page(self) -> bool:
        """Go to the previous page if possible"""
        return self.go_to_page(self.current_page - 1)
    
    def first_page(self) -> bool:
        """Go to the first page"""
        return self.go_to_page(0)
    
    def last_page(self) -> bool:
        """Go to the last page"""
        return self.go_to_page(self.total_pages - 1)
    
    def set_total_items(self, count: int) -> None:
        """Set the total number of items and recalculate pages"""
        self.total_items = max(0, count)
        self._recalculate_pages()
        
    def get_page_info(self) -> PageInfo:
        """Get current pagination state"""
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, self.total_items)
        
        return PageInfo(
            current_page=self.current_page,
            total_pages=self.total_pages,
            page_size=self.page_size,
            total_items=self.total_items,
            start_index=start_idx,
            end_index=end_idx
        )
    
    def get_visible_range(self) -> tuple[int, int]:
        """Get the start and end indices for the current page"""
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, self.total_items)
        return start_idx, end_idx
    
    def is_item_visible(self, index: int) -> bool:
        """Check if an item index is on the current page"""
        start_idx, end_idx = self.get_visible_range()
        return start_idx <= index < end_idx
    
    def navigate_to_item(self, index: int) -> bool:
        """Navigate to the page containing the specified item"""
        if 0 <= index < self.total_items:
            target_page = index // self.page_size
            return self.go_to_page(target_page)
        return False
    
    def _recalculate_pages(self) -> None:
        """Recalculate total pages based on item count and page size"""
        if self.total_items <= 0:
            self.total_pages = 1
        else:
            self.total_pages = (self.total_items + self.page_size - 1) // self.page_size
            
        # Ensure current page is within bounds
        if self.current_page >= self.total_pages:
            self.current_page = max(0, self.total_pages - 1)
            self.pageChanged.emit(self.current_page, self.total_pages)
    
    def _update_view(self) -> None:
        """
        Update the view to show the current page - must be implemented by subclasses.
        This base implementation does nothing.
        """
        pass  # Must be implemented by subclasses
```

### 5.3. Specialized Implementations

#### 5.3.1. ModelPaginator

For QAbstractItemModel-based views:

```python
class ModelPaginator(BasePaginator):
    """
    Paginator for QAbstractItemModel-based views.
    Works with QTableView, QTreeView, etc.
    """
    
    def __init__(self, 
                 model, 
                 view, 
                 page_size: int = 50,
                 parent: Optional[QObject] = None):
        """Initialize with model and view"""
        super().__init__(page_size, PaginationMode.TABLE, parent)
        self.model = model
        self.view = view
        self.total_items = self.model.rowCount() if self.model else 0
        self._recalculate_pages()
        
        # Connect to model signals for auto-updates
        if self.model:
            try:
                self.model.modelReset.connect(self._on_model_reset)
            except AttributeError:
                pass
            try:
                self.model.rowsInserted.connect(self._on_model_reset)
            except AttributeError:
                pass
            try:
                self.model.rowsRemoved.connect(self._on_model_reset)
            except AttributeError:
                pass
    
    def _on_model_reset(self, *args):
        """Handle model reset by updating pagination"""
        self.total_items = self.model.rowCount() if self.model else 0
        self._recalculate_pages()
        self._update_view()
    
    def _update_view(self) -> None:
        """Update the view to show only current page rows"""
        if not self.model or not self.view:
            return
            
        start, end = self.get_visible_range()
        
        # Hide all rows first
        for row in range(self.total_items):
            self.view.setRowHidden(row, row < start or row >= end)
```

#### 5.3.2. ProxyModelPaginator

For QSortFilterProxyModel-based pagination:

```python
class ProxyModelPaginator(BasePaginator):
    """
    Paginator that works with QSortFilterProxyModel by implementing custom filtering.
    Typically used when the filter needs to include pagination logic.
    """
    
    def __init__(self, 
                 proxy_model,
                 page_size: int = 50,
                 parent: Optional[QObject] = None):
        """Initialize with a proxy model"""
        super().__init__(page_size, PaginationMode.TABLE, parent)
        self.proxy_model = proxy_model
        
        # If the proxy model has an invalidateFilter method, we'll connect our update
        if hasattr(self.proxy_model, 'invalidateFilter'):
            self._update_view = self._invalidate_filter
    
    def _invalidate_filter(self):
        """Invalidate the filter to trigger refiltering with new page"""
        self.proxy_model.invalidateFilter()
    
    def _update_view(self) -> None:
        """Default implementation for proxy models without invalidateFilter"""
        if hasattr(self.proxy_model, 'invalidateFilter'):
            self.proxy_model.invalidateFilter()
        
    def setup_filter_function(self, filter_function):
        """
        Setup a custom filter function that will incorporate pagination logic
        The function should take (source_row, source_parent, paginator) as arguments
        """
        def filtered_accepts_row(source_row, source_parent):
            return filter_function(source_row, source_parent, self)
            
        # Attach to the proxy model's filterAcceptsRow if it allows
        if hasattr(self.proxy_model, 'setFilterFunction'):
            self.proxy_model.setFilterFunction(filtered_accepts_row)
```

#### 5.3.3. CollectionPaginator

For list/array-based data:

```python
class CollectionPaginator(BasePaginator):
    """
    Paginator for Python collections (lists, tuples, etc.)
    Provides methods to get the visible items for the current page.
    """
    
    def __init__(self, 
                 items=None, 
                 page_size: int = 50,
                 update_callback=None,
                 parent: Optional[QObject] = None):
        """Initialize with collection items"""
        super().__init__(page_size, PaginationMode.CUSTOM, parent)
        self.items = items or []
        self.total_items = len(self.items)
        self.update_callback = update_callback
        self._recalculate_pages()
    
    def set_items(self, items):
        """Set or replace the items collection"""
        self.items = items or []
        self.total_items = len(self.items)
        self._recalculate_pages()
        self._update_view()
        
    def get_visible_items(self):
        """Get only the items visible on the current page"""
        start, end = self.get_visible_range()
        return self.items[start:end]
        
    def add_item(self, item):
        """Add an item to the collection"""
        self.items.append(item)
        self.total_items += 1
        self._recalculate_pages()
        
        # Only update view if the new item should be visible on current page
        if self.is_item_visible(self.total_items - 1):
            self._update_view()
    
    def _update_view(self) -> None:
        """Call the update callback if provided"""
        if self.update_callback:
            visible_items = self.get_visible_items()
            self.update_callback(visible_items, self.get_page_info())
```

### 5.4. UI Components

#### 5.4.1. IPaginationWidget Interface

```python
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

class IPaginationWidget(QWidget, ABC):
    """
    Abstract interface for pagination UI widgets.
    Defines the contract for UI components that control pagination.
    """
    # Signals
    pageRequested = Signal(int)       # Request to go to specific page
    pageSizeChanged = Signal(int)     # Page size changed
    firstPageRequested = Signal()     # Request to go to first page
    lastPageRequested = Signal()      # Request to go to last page
    nextPageRequested = Signal()      # Request to go to next page
    prevPageRequested = Signal()      # Request to go to previous page
    
    @abstractmethod
    def update_state(self, current_page: int, total_pages: int, page_size: int = None):
        """Update the UI to reflect current pagination state"""
        pass
    
    @abstractmethod
    def connect_paginator(self, paginator):
        """Connect this widget to a paginator"""
        pass
```

#### 5.4.2. Standard Pagination Controls

```python
class StandardPaginationControls(IPaginationWidget):
    """
    Standard pagination control widget with navigation buttons, page display, and size selector.
    Provides a consistent pagination UI that can be used throughout the application.
    """
    
    def __init__(self, 
                 page_sizes: List[int] = [25, 50, 100, 250, 500],
                 show_page_size: bool = True,
                 show_goto: bool = True,
                 parent: Optional[QWidget] = None):
        """Initialize pagination controls"""
        super().__init__(parent)
        self.paginator = None
        self._setup_ui(page_sizes, show_page_size, show_goto)
        
    def _setup_ui(self, page_sizes, show_page_size, show_goto):
        """Setup pagination UI controls"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons
        self.first_button = QToolButton()
        self.first_button.setText("<<")
        self.first_button.setToolTip("First Page")
        
        self.prev_button = QToolButton()
        self.prev_button.setText("<")
        self.prev_button.setToolTip("Previous Page")
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumWidth(100)
        
        self.next_button = QToolButton()
        self.next_button.setText(">")
        self.next_button.setToolTip("Next Page")
        
        self.last_button = QToolButton()
        self.last_button.setText(">>")
        self.last_button.setToolTip("Last Page")
        
        # Add navigation controls
        main_layout.addWidget(self.first_button)
        main_layout.addWidget(self.prev_button)
        main_layout.addWidget(self.page_label)
        main_layout.addWidget(self.next_button)
        main_layout.addWidget(self.last_button)
        
        # Page size selector (optional)
        if show_page_size:
            main_layout.addStretch()
            
            self.page_size_label = QLabel("Items per page:")
            main_layout.addWidget(self.page_size_label)
            
            self.page_size_combo = QComboBox()
            for size in page_sizes:
                self.page_size_combo.addItem(str(size), size)
            main_layout.addWidget(self.page_size_combo)
        else:
            self.page_size_combo = None
            
        # Go to page input (optional)
        if show_goto:
            main_layout.addStretch()
            
            self.goto_label = QLabel("Go to page:")
            main_layout.addWidget(self.goto_label)
            
            self.goto_spin = QSpinBox()
            self.goto_spin.setMinimum(1)
            self.goto_spin.setMaximum(1)
            self.goto_spin.setValue(1)
            main_layout.addWidget(self.goto_spin)
        else:
            self.goto_spin = None
            
        # Connect button signals
        self.first_button.clicked.connect(self._on_first_clicked)
        self.prev_button.clicked.connect(self._on_prev_clicked)
        self.next_button.clicked.connect(self._on_next_clicked)
        self.last_button.clicked.connect(self._on_last_clicked)
        
        if self.page_size_combo:
            self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)
            
        if self.goto_spin:
            self.goto_spin.editingFinished.connect(self._on_goto_page)
    
    def update_state(self, current_page: int, total_pages: int, page_size: int = None):
        """Update UI to reflect current pagination state"""
        # Update page label
        self.page_label.setText(f"Page {current_page + 1} of {max(1, total_pages)}")
        
        # Update button states
        self.first_button.setEnabled(current_page > 0)
        self.prev_button.setEnabled(current_page > 0)
        self.next_button.setEnabled(current_page < total_pages - 1)
        self.last_button.setEnabled(current_page < total_pages - 1)
        
        # Update goto spinner if we have one
        if self.goto_spin:
            self.goto_spin.setMaximum(max(1, total_pages))
            self.goto_spin.setValue(current_page + 1)  # UI shows 1-based
        
        # Update page size if provided
        if page_size is not None and self.page_size_combo:
            for i in range(self.page_size_combo.count()):
                if self.page_size_combo.itemData(i) == page_size:
                    self.page_size_combo.setCurrentIndex(i)
                    break
    
    def connect_paginator(self, paginator):
        """Connect to a paginator instance"""
        self.paginator = paginator
        
        # Connect paginator signals to update our UI
        paginator.pageChanged.connect(lambda curr, total: self.update_state(curr, total))
        paginator.pageSizeChanged.connect(lambda size: self.update_state(paginator.current_page, 
                                                                       paginator.total_pages, size))
        
        # Connect our signals to the paginator
        self.pageRequested.connect(paginator.go_to_page)
        self.pageSizeChanged.connect(paginator.set_page_size)
        self.firstPageRequested.connect(paginator.first_page)
        self.lastPageRequested.connect(paginator.last_page)
        self.nextPageRequested.connect(paginator.next_page)
        self.prevPageRequested.connect(paginator.prev_page)
        
        # Initialize our UI with current paginator state
        page_info = paginator.get_page_info()
        self.update_state(page_info.current_page, page_info.total_pages, page_info.page_size)
    
    # Event handlers
    def _on_first_clicked(self):
        self.firstPageRequested.emit()
        
    def _on_prev_clicked(self):
        self.prevPageRequested.emit()
        
    def _on_next_clicked(self):
        self.nextPageRequested.emit()
        
    def _on_last_clicked(self):
        self.lastPageRequested.emit()
        
    def _on_page_size_changed(self, index):
        if index >= 0 and self.page_size_combo:
            size = self.page_size_combo.itemData(index)
            self.pageSizeChanged.emit(size)
        
    def _on_goto_page(self):
        if self.goto_spin:
            # Convert from 1-based UI to 0-based internal
            page = self.goto_spin.value() - 1
            self.pageRequested.emit(page)
```

#### 5.4.3. Compact Pagination Controls

```python
class CompactPaginationControls(IPaginationWidget):
    """
    Compact pagination controls with minimal UI footprint.
    Designed for use in space-constrained interfaces.
    """
    
    def __init__(self, parent=None):
        """Initialize compact controls"""
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup minimal UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self.prev_btn = QToolButton()
        self.prev_btn.setText("◀")
        self.prev_btn.setFixedSize(24, 24)
        
        self.page_label = QLabel("1/1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setFixedWidth(40)
        
        self.next_btn = QToolButton()
        self.next_btn.setText("▶")
        self.next_btn.setFixedSize(24, 24)
        
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_btn)
        
        # Connect signals
        self.prev_btn.clicked.connect(lambda: self.prevPageRequested.emit())
        self.next_btn.clicked.connect(lambda: self.nextPageRequested.emit())
    
    def update_state(self, current_page: int, total_pages: int, page_size: int = None):
        """Update UI state"""
        self.page_label.setText(f"{current_page + 1}/{max(1, total_pages)}")
        self.prev_btn.setEnabled(current_page > 0)
        self.next_btn.setEnabled(current_page < total_pages - 1)
    
    def connect_paginator(self, paginator):
        """Connect to paginator"""
        # Connect paginator signals
        paginator.pageChanged.connect(lambda curr, total: self.update_state(curr, total))
        
        # Connect our signals
        self.prevPageRequested.connect(paginator.prev_page)
        self.nextPageRequested.connect(paginator.next_page)
        
        # Initialize state
        page_info = paginator.get_page_info()
        self.update_state(page_info.current_page, page_info.total_pages)
```

### 5.5. Factory Functions

To simplify creation and configuration of the pagination system:

```python
def create_paginator(data_source, view=None, page_size=50, mode=PaginationMode.CUSTOM):
    """
    Factory function to create the appropriate paginator based on data source type.
    
    Args:
        data_source: The data source (model, list, etc.)
        view: Optional view component (for model paginators)
        page_size: Number of items per page
        mode: Pagination mode
        
    Returns:
        An appropriate paginator instance
    """
    if isinstance(data_source, QAbstractItemModel):
        if isinstance(data_source, QSortFilterProxyModel):
            return ProxyModelPaginator(data_source, page_size)
        else:
            return ModelPaginator(data_source, view, page_size)
    elif isinstance(data_source, (list, tuple)):
        return CollectionPaginator(data_source, page_size)
    else:
        # Default to base paginator for custom implementations
        paginator = BasePaginator(page_size, mode)
        return paginator

def create_pagination_controls(paginator, style="standard", **kwargs):
    """
    Create pagination controls for a paginator with the specified style.
    
    Args:
        paginator: The paginator to connect to
        style: Control style ("standard", "compact", "visual", etc.)
        **kwargs: Additional style-specific parameters
        
    Returns:
        A pagination control widget connected to the paginator
    """
    if style == "compact":
        controls = CompactPaginationControls(**kwargs)
    elif style == "visual":
        controls = VisualPaginationControls(**kwargs)
    else:
        controls = StandardPaginationControls(**kwargs)
    
    controls.connect_paginator(paginator)
    return controls
```

## 6. Implementation Plan

The migration to the unified pagination system will be implemented in multiple phases:

### Phase 1: Core Framework Implementation

**Timeline: 2 weeks**

1. Create the core interfaces and base implementations
   - `IPaginator` interface and `BasePaginator` implementation
   - `IPaginationWidget` interface and `StandardPaginationControls` implementation
   - Factory functions for creating and connecting components

2. Implement the specialized paginators
   - `ModelPaginator` for model-based views
   - `ProxyModelPaginator` for proxy models
   - `CollectionPaginator` for list-based data

3. Implement UI components
   - `StandardPaginationControls` with full features
   - `CompactPaginationControls` for space-constrained areas

4. Create unit tests for all components

### Phase 2: Refactor Existing Components

**Timeline: 3-4 weeks**

1. Refactor `TablePagerBase` to use new architecture
   - Maintain backward compatibility
   - Add deprecation warnings

2. Update `PagedFileSystemModel`
   - Implement `ProxyModelPaginator` integration
   - Update UI to use standard controls

3. Refactor `SearchResultsPanel`
   - Replace custom pagination with `CollectionPaginator`
   - Update UI to use standard controls

4. Update `IssueOnlyDialog`
   - Replace custom pagination with appropriate paginator
   - Integrate standard pagination controls

5. Test all refactored components

### Phase 3: New Features and Full Integration

**Timeline: 2-3 weeks**

1. Add new pagination features
   - Visual pagination indicators
   - Keyboard navigation support
   - Accessibility improvements

2. Create documentation
   - Usage guidelines
   - API reference
   - Migration guide for developers

3. Final integration and testing
   - End-to-end testing
   - Performance benchmarks
   - User experience validation

## 7. Component Upgrade Plans

### 7.1. Professional Explorer Upgrade

The `professional_explorer.py` file contains two pagination components that need to be upgraded:

1. **PagedFileSystemModel**:
   - Currently implements filtering in `filterAcceptsRow` with internal pagination logic
   - Upgrade plan:
     - Create `FileSystemPaginator` extending `ProxyModelPaginator`
     - Move pagination logic from model to paginator
     - Modify `filterAcceptsRow` to delegate to paginator
     - Replace paging controls with `StandardPaginationControls`

2. **SearchResultsPanel**:
   - Currently implements custom pagination for search results
   - Upgrade plan:
     - Create `SearchResultsPaginator` extending `CollectionPaginator`
     - Replace internal pagination with the new paginator
     - Replace UI controls with `StandardPaginationControls`
     - Update event handlers to use paginator methods

```python
# Example upgrade for PagedFileSystemModel
class FileSystemPaginator(ProxyModelPaginator):
    """Specialized paginator for file system models"""
    
    def __init__(self, model, page_size=200):
        super().__init__(model, page_size)
        self.filter_pattern = "*"  # Default filter pattern
    
    def set_filter_pattern(self, pattern):
        """Set file name filter pattern"""
        self.filter_pattern = pattern if pattern else "*"
        self.current_page = 0  # Reset to first page
        self._invalidate_filter()
    
    def create_filter_function(self):
        """Create file system specific filter function"""
        def file_filter(source_row, source_parent, paginator):
            # Get source model and check validity
            source_index = self.proxy_model.sourceModel().index(source_row, 0, source_parent)
            if not source_index.isValid():
                return False
            
            # Always show directories
            if self.proxy_model.sourceModel().isDir(source_index):
                return True
            
            # Apply file pattern filter
            if self.filter_pattern and self.filter_pattern.strip() and self.filter_pattern != "*":
                filename = self.proxy_model.sourceModel().fileName(source_index)
                if not fnmatch.fnmatch(filename.lower(), self.filter_pattern.lower()):
                    return False
            
            # Get all files that match the filter
            # [Implementation details for calculating file index within filtered set]
            
            # Apply pagination filter
            start_item, end_item = paginator.get_visible_range()
            return start_item <= file_index < end_item
            
        return file_filter
```

### 7.2. IssueOnlyDialog Upgrade

The `issue_only_dialog_paged.py` uses custom pagination controls:

```python
# Upgrade plan for IssueOnlyDialog
class IssueDialogPaginator(ModelPaginator):
    """Specialized paginator for issue dialog"""
    
    def __init__(self, table_model, view, page_size=50):
        super().__init__(table_model, view, page_size)
        
    def _update_view(self):
        """Update the view to show only records for current page"""
        # Get issue records for current page
        start, end = self.get_visible_range()
        
        # Update model with records for current page
        records = self.model.issue_records[start:end]
        self.model.beginResetModel()
        self.model.visible_records = records
        self.model.endResetModel()
        
        # Update status display
        if hasattr(self.parent(), 'update_status_display'):
            self.parent().update_status_display(self.get_page_info())
```

### 7.3. Table View Upgrade

The existing `TablePagerBase` in `subcmp/table_nav_widget.py` can be updated:

```python
# Upgrade plan for TablePagerBase
class TablePagerBase(BasePaginator):
    """Updated version of TablePagerBase using new architecture"""
    
    def __init__(self, table, table_model, page_size=100, parent=None):
        """Maintain backward compatibility with existing signature"""
        super().__init__(page_size, PaginationMode.TABLE, parent)
        self.table = table
        self.model = table_model
        self.total_rows = self.model.rowCount() if self.model else 0
        self.total_items = self.total_rows  # Sync with base class property
        self._connect_signals()
        self._recalculate_pages()
    
    # Maintain backward compatibility methods while delegating to base class
    def go_first(self):
        """Go to first page - for backward compatibility"""
        return self.first_page()
        
    def go_last(self):
        """Go to last page - for backward compatibility"""
        return self.last_page()
        
    def go_prev(self):
        """Go to previous page - for backward compatibility"""
        return self.prev_page()
        
    def go_next(self):
        """Go to next page - for backward compatibility"""
        return self.next_page()
        
    def get_page_indices(self):
        """For backward compatibility"""
        return self.get_visible_range()
```

## 8. Conclusion

The unified pagination design provides a robust and flexible framework for pagination across the POEditor application. By separating pagination logic from UI presentation and providing specialized implementations for different data sources, we create a more maintainable and consistent user experience.

This design allows for:

1. **Consistency**: Standard pagination behavior and UI throughout the application
2. **Extensibility**: Easy to add new pagination styles or behaviors
3. **Maintainability**: Centralized logic and reduced code duplication
4. **Improved UX**: Consistent and predictable pagination controls

The implementation plan provides a structured approach to migrating existing components while minimizing disruption to the codebase.
