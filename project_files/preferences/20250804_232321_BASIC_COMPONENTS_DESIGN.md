# Preferences Basic Components Design Plan

## Overview

This document outlines the detailed design for building the foundational components that will be shared across all preference panels. These components integrate with the existing unified pagination framework and provide common functionality, with enhanced virtual metamorphic paging mechanism for optimal UI performance.

## Virtual Metamorphic Paging Architecture

### Core Concepts

**Virtual Metamorphic Paging** is an advanced pagination technique that combines:
- **Virtual Scrolling**: Only renders visible items in viewport
- **Metamorphic Adaptation**: Dynamically adjusts page sizes based on content and performance
- **Intelligent Prefetching**: Preloads adjacent pages based on scroll patterns
- **Memory Management**: Automatically releases non-visible data to optimize memory usage

### Benefits
- **Ultra-fast UI refresh**: Only updates visible elements
- **Memory efficient**: Handles large datasets without memory bloat
- **Adaptive performance**: Adjusts to system capabilities and user behavior
- **Smooth scrolling**: Seamless user experience even with massive datasets

### Basic Paging Operations

The virtual metamorphic paging system supports essential navigation operations:

1. **Go to Top (First Page)**: Navigate to the beginning of the dataset
2. **Go to Bottom (Last Page)**: Navigate to the end of the dataset  
3. **Next Page**: Move forward by one page
4. **Previous Page**: Move backward by one page
5. **Go to Specific Page**: Direct navigation to any page number
6. **Refresh Current Page**: Reload current page data

These operations will be implemented by viewer components like `TableViewer`, `DatabaseViewer`, `SearchResultsViewer`, etc.

## 1. Enhanced Pagination Integration Components

### 1.1 VirtualMetamorphicPagingController

**Purpose:** Core controller implementing virtual metamorphic paging with system settings integration.

**File:** `services/virtual_metamorphic_paging_controller.py`

**Design:**
```python
from PySide6.QtCore import QObject, Signal, QTimer, QSettings
from PySide6.QtWidgets import QTableWidget, QScrollBar
from typing import Dict, Optional, List, Any, Callable
import time
from dataclasses import dataclass

@dataclass
class PageMetrics:
    """Metrics for metamorphic adaptation"""
    load_time: float
    render_time: float
    memory_usage: int
    user_scroll_speed: float
    optimal_page_size: int

class VirtualMetamorphicPagingController(QObject):
    """Enhanced pagination controller with virtual metamorphic capabilities"""
    
    # Enhanced signals for virtual paging
    virtualPageChanged = Signal(int, int)  # start_index, end_index
    metamorphicAdaptation = Signal(dict)   # adaptation metrics
    prefetchCompleted = Signal(int, list)  # page_number, prefetched_data
    memoryOptimized = Signal(int)          # released_pages_count
    navigationCompleted = Signal(str, int) # operation_type, target_page
    
    def __init__(self, table_widget: QTableWidget, 
                 data_provider: 'PaginationDataProvider',
                 component_name: str,
                 settings_manager: 'PreferencesPagingSettingsManager',
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self.table_widget = table_widget
        self.data_provider = data_provider
        self.component_name = component_name
        self.settings_manager = settings_manager
        
        # Virtual paging state
        self._viewport_start = 0
        self._viewport_size = 0
        self._total_items = 0
        self._visible_range = (0, 0)
        self._current_page = 1
        self._total_pages = 1
        
        # Metamorphic adaptation state
        self._page_metrics: Dict[int, PageMetrics] = {}
        self._optimal_page_size = self._get_initial_page_size()
        self._adaptation_enabled = True
        
        # Prefetch and memory management
        self._page_cache: Dict[int, List[Any]] = {}
        self._prefetch_queue: List[int] = []
        self._max_cached_pages = self._get_max_cached_pages()
        
        # Performance monitoring
        self._scroll_timer = QTimer()
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(self._on_scroll_finished)
        
        self._adaptation_timer = QTimer()
        self._adaptation_timer.timeout.connect(self._perform_metamorphic_adaptation)
        self._adaptation_timer.start(5000)  # Adapt every 5 seconds
        
        self._setup_virtual_scrolling()
        
    def _setup_virtual_scrolling(self):
        """Setup virtual scrolling on table widget"""
        # Connect to scroll events
        scrollbar = self.table_widget.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_scroll)
        
        # Setup initial viewport
        self._update_viewport_size()
        
        # Enable virtual mode
        self.table_widget.setUpdatesEnabled(False)
        self._load_initial_data()
        self.table_widget.setUpdatesEnabled(True)
        
    def _get_initial_page_size(self) -> int:
        """Get initial page size from settings with virtual paging optimization"""
        base_size = self.settings_manager.get_page_size(self.component_name)
        
        # Virtual paging uses larger pages for better performance
        virtual_multiplier = self._get_virtual_multiplier()
        return base_size * virtual_multiplier
        
    def _get_virtual_multiplier(self) -> int:
        """Get virtual page multiplier based on system settings"""
        settings = QSettings("POEditor", "VirtualPaging")
        
        # Adaptive based on system performance
        system_performance = settings.value("system_performance", "medium")
        performance_multipliers = {
            "low": 2,      # Smaller pages for low-end systems
            "medium": 4,   # Balanced approach
            "high": 8,     # Larger pages for high-end systems
            "ultra": 16    # Maximum performance systems
        }
        
        return performance_multipliers.get(system_performance, 4)
        
    def _get_max_cached_pages(self) -> int:
        """Get maximum cached pages from system settings"""
        settings = QSettings("POEditor", "VirtualPaging")
        memory_limit_mb = int(settings.value("memory_limit_mb", 100))
        
        # Estimate pages based on memory limit
        estimated_page_memory = 1024 * 50  # ~50KB per page estimate
        max_pages = (memory_limit_mb * 1024 * 1024) // estimated_page_memory
        
        return max(5, min(max_pages, 50))  # Between 5-50 pages
        
    def _update_viewport_size(self):
        """Update viewport size based on table dimensions"""
        visible_height = self.table_widget.viewport().height()
        row_height = self.table_widget.rowHeight(0) if self.table_widget.rowCount() > 0 else 30
        
        self._viewport_size = max(1, visible_height // row_height)
        
        # Add buffer for smooth scrolling
        buffer_multiplier = self._get_buffer_multiplier()
        self._viewport_size = int(self._viewport_size * buffer_multiplier)
        
    def _get_buffer_multiplier(self) -> float:
        """Get buffer multiplier for smooth scrolling"""
        settings = QSettings("POEditor", "VirtualPaging")
        smooth_scrolling = settings.value("smooth_scrolling", True, type=bool)
        
        if smooth_scrolling:
            return 2.5  # 150% buffer above and below viewport
        else:
            return 1.5  # 50% buffer for basic scrolling
            
    def _on_scroll(self, value: int):
        """Handle scroll events with virtual paging"""
        # Calculate new visible range
        new_start = max(0, value - self._viewport_size // 4)
        new_end = min(self._total_items, new_start + self._viewport_size)
        
        if (new_start, new_end) != self._visible_range:
            self._visible_range = (new_start, new_end)
            self._update_virtual_display()
            
        # Start scroll timer for metamorphic adaptation
        self._scroll_timer.start(200)
        
    def _on_scroll_finished(self):
        """Handle scroll completion for performance analysis"""
        # Record scroll performance metrics
        self._record_scroll_metrics()
        
        # Trigger prefetch for adjacent pages
        self._schedule_prefetch()
        
    def _update_virtual_display(self):
        """Update table display with virtual items"""
        start_time = time.time()
        
        start_idx, end_idx = self._visible_range
        page_number = start_idx // self._optimal_page_size
        
        # Check if data is cached
        if page_number in self._page_cache:
            data = self._page_cache[page_number]
        else:
            # Load data with performance monitoring
            data = self._load_page_data(page_number)
            self._cache_page_data(page_number, data)
            
        # Update table with virtual subset
        virtual_data = self._extract_virtual_subset(data, start_idx, end_idx)
        self._render_virtual_data(virtual_data)
        
        # Record performance metrics
        render_time = time.time() - start_time
        self._update_page_metrics(page_number, render_time=render_time)
        
        # Emit virtual page change
        self.virtualPageChanged.emit(start_idx, end_idx)
        
    def _load_page_data(self, page_number: int) -> List[Any]:
        """Load data for specific page with performance monitoring"""
        start_time = time.time()
        
        start_idx = page_number * self._optimal_page_size
        data = self.data_provider.get_page_items(start_idx, self._optimal_page_size)
        
        load_time = time.time() - start_time
        self._update_page_metrics(page_number, load_time=load_time)
        
        return data
        
    def _cache_page_data(self, page_number: int, data: List[Any]):
        """Cache page data with memory management"""
        self._page_cache[page_number] = data
        
        # Memory management - remove oldest cached pages if limit exceeded
        if len(self._page_cache) > self._max_cached_pages:
            # Remove least recently used pages
            oldest_pages = sorted(self._page_cache.keys())[:-self._max_cached_pages]
            for old_page in oldest_pages:
                del self._page_cache[old_page]
                
            self.memoryOptimized.emit(len(oldest_pages))
            
    def _extract_virtual_subset(self, page_data: List[Any], 
                              start_idx: int, end_idx: int) -> List[Any]:
        """Extract virtual subset from page data"""
        page_start = (start_idx // self._optimal_page_size) * self._optimal_page_size
        relative_start = start_idx - page_start
        relative_end = min(len(page_data), end_idx - page_start)
        
        return page_data[relative_start:relative_end]
        
    def _render_virtual_data(self, data: List[Any]):
        """Render virtual data to table widget"""
        # Clear existing items efficiently
        self.table_widget.setRowCount(len(data))
        
        # Render only visible items
        for row, item in enumerate(data):
            self._render_table_row(row, item)
            
    def _render_table_row(self, row: int, item: Any):
        """Render individual table row (implemented by subclasses)"""
        # This method should be overridden by specific implementations
        pass
        
    def _schedule_prefetch(self):
        """Schedule prefetch of adjacent pages"""
        current_page = self._visible_range[0] // self._optimal_page_size
        
        # Prefetch adjacent pages
        prefetch_pages = [
            current_page - 1,
            current_page + 1,
            current_page + 2  # Look ahead for fast scrolling
        ]
        
        for page in prefetch_pages:
            if (page >= 0 and 
                page not in self._page_cache and 
                page not in self._prefetch_queue):
                self._prefetch_queue.append(page)
                
        # Process prefetch queue
        if self._prefetch_queue:
            self._process_prefetch_queue()
            
    def _process_prefetch_queue(self):
        """Process prefetch queue asynchronously"""
        if not self._prefetch_queue:
            return
            
        page_number = self._prefetch_queue.pop(0)
        
        # Load data asynchronously
        QTimer.singleShot(10, lambda: self._async_prefetch(page_number))
        
    def _async_prefetch(self, page_number: int):
        """Asynchronously prefetch page data"""
        try:
            data = self._load_page_data(page_number)
            self._cache_page_data(page_number, data)
            self.prefetchCompleted.emit(page_number, data)
            
        except Exception as e:
            # Silent failure for prefetch operations
            pass
            
        # Continue processing queue
        if self._prefetch_queue:
            QTimer.singleShot(50, self._process_prefetch_queue)
            
    def _perform_metamorphic_adaptation(self):
        """Perform metamorphic adaptation based on collected metrics"""
        if not self._adaptation_enabled or not self._page_metrics:
            return
            
        # Analyze performance metrics
        metrics_analysis = self._analyze_performance_metrics()
        
        # Adapt page size if needed
        if metrics_analysis.get('should_adapt', False):
            new_page_size = metrics_analysis.get('optimal_page_size', self._optimal_page_size)
            
            if new_page_size != self._optimal_page_size:
                self._optimal_page_size = new_page_size
                self._clear_cache()  # Clear cache to use new page size
                
                # Update settings
                virtual_multiplier = new_page_size // self.settings_manager.get_page_size(self.component_name)
                settings = QSettings("POEditor", "VirtualPaging")
                settings.setValue(f"{self.component_name}_virtual_multiplier", virtual_multiplier)
                
                self.metamorphicAdaptation.emit(metrics_analysis)
                
    def _analyze_performance_metrics(self) -> Dict:
        """Analyze collected performance metrics for adaptation"""
        if len(self._page_metrics) < 3:
            return {'should_adapt': False}
            
        # Calculate average metrics
        avg_load_time = sum(m.load_time for m in self._page_metrics.values()) / len(self._page_metrics)
        avg_render_time = sum(m.render_time for m in self._page_metrics.values()) / len(self._page_metrics)
        
        # Performance thresholds from settings
        settings = QSettings("POEditor", "VirtualPaging")
        max_load_time = float(settings.value("max_load_time_ms", 100.0)) / 1000.0
        max_render_time = float(settings.value("max_render_time_ms", 50.0)) / 1000.0
        
        should_adapt = False
        new_page_size = self._optimal_page_size
        
        # Adaptation logic
        if avg_load_time > max_load_time:
            # Reduce page size for faster loading
            new_page_size = max(10, int(self._optimal_page_size * 0.7))
            should_adapt = True
        elif avg_render_time > max_render_time:
            # Reduce page size for faster rendering
            new_page_size = max(10, int(self._optimal_page_size * 0.8))
            should_adapt = True
        elif avg_load_time < max_load_time * 0.5 and avg_render_time < max_render_time * 0.5:
            # Increase page size for better efficiency
            new_page_size = min(1000, int(self._optimal_page_size * 1.3))
            should_adapt = True
            
        return {
            'should_adapt': should_adapt,
            'optimal_page_size': new_page_size,
            'avg_load_time': avg_load_time,
            'avg_render_time': avg_render_time,
            'current_page_size': self._optimal_page_size,
            'cache_hit_rate': self._calculate_cache_hit_rate()
        }
        
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate for performance monitoring"""
        # Implementation would track cache hits vs misses
        return 0.85  # Placeholder
        
    def _update_page_metrics(self, page_number: int, **kwargs):
        """Update performance metrics for specific page"""
        if page_number not in self._page_metrics:
            self._page_metrics[page_number] = PageMetrics(
                load_time=0.0,
                render_time=0.0, 
                memory_usage=0,
                user_scroll_speed=0.0,
                optimal_page_size=self._optimal_page_size
            )
            
        metrics = self._page_metrics[page_number]
        
        # Update metrics with provided values
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
                
    def _record_scroll_metrics(self):
        """Record scroll performance metrics"""
        # Implementation would track scroll patterns and speed
        pass
        
    def _clear_cache(self):
        """Clear page cache for adaptation"""
        self._page_cache.clear()
        self._prefetch_queue.clear()
        
    def _load_initial_data(self):
        """Load initial data for table"""
        self._total_items = self.data_provider.get_total_count()
        self._update_viewport_size()
        
        # Load first visible page
        if self._total_items > 0:
            self._visible_range = (0, min(self._viewport_size, self._total_items))
            self._update_virtual_display()
            
    # Public interface methods
    def set_adaptation_enabled(self, enabled: bool):
        """Enable/disable metamorphic adaptation"""
        self._adaptation_enabled = enabled
        
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        return self._analyze_performance_metrics()
        
    def force_adaptation(self):
        """Force immediate metamorphic adaptation"""
        self._perform_metamorphic_adaptation()
        
    def clear_metrics(self):
        """Clear collected performance metrics"""
        self._page_metrics.clear()
        
    def refresh_data(self):
        """Refresh all data with virtual paging"""
        self._clear_cache()
        self._load_initial_data()
        
    # Basic Paging Operations
    def go_to_first_page(self):
        """Navigate to the first page (top of dataset)"""
        if self._current_page != 1:
            self._navigate_to_page(1, "go_to_first")
            
    def go_to_last_page(self):
        """Navigate to the last page (bottom of dataset)"""
        if self._current_page != self._total_pages:
            self._navigate_to_page(self._total_pages, "go_to_last")
            
    def go_to_next_page(self):
        """Navigate to the next page"""
        if self._current_page < self._total_pages:
            self._navigate_to_page(self._current_page + 1, "go_to_next")
            
    def go_to_previous_page(self):
        """Navigate to the previous page"""
        if self._current_page > 1:
            self._navigate_to_page(self._current_page - 1, "go_to_previous")
            
    def go_to_page(self, page_number: int):
        """Navigate to a specific page"""
        if 1 <= page_number <= self._total_pages and page_number != self._current_page:
            self._navigate_to_page(page_number, "go_to_specific")
            
    def refresh_current_page(self):
        """Refresh the current page data"""
        # Clear current page from cache to force reload
        if self._current_page in self._page_cache:
            del self._page_cache[self._current_page]
            
        # Reload current page
        self._navigate_to_page(self._current_page, "refresh")
        
    def _navigate_to_page(self, target_page: int, operation_type: str):
        """Internal method to handle page navigation"""
        if not (1 <= target_page <= self._total_pages):
            return
            
        self._current_page = target_page
        
        # Calculate new visible range for virtual display
        start_idx = (target_page - 1) * self._optimal_page_size
        end_idx = min(start_idx + self._optimal_page_size, self._total_items)
        
        # Update virtual display
        self._visible_range = (start_idx, end_idx)
        self._update_virtual_display()
        
        # Emit navigation completed signal
        self.navigationCompleted.emit(operation_type, target_page)
        
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
        
    def get_total_pages(self) -> int:
        """Get total number of pages"""
        return self._total_pages
        
    def get_total_items(self) -> int:
        """Get total number of items"""
        return self._total_items
        
    def can_go_previous(self) -> bool:
        """Check if can navigate to previous page"""
        return self._current_page > 1
        
    def can_go_next(self) -> bool:
        """Check if can navigate to next page"""
        return self._current_page < self._total_pages
        
    def get_page_info(self) -> Dict:
        """Get comprehensive page information"""
        start_item = (self._current_page - 1) * self._optimal_page_size + 1
        end_item = min(self._current_page * self._optimal_page_size, self._total_items)
        
        return {
            'current_page': self._current_page,
            'total_pages': self._total_pages,
            'page_size': self._optimal_page_size,
            'total_items': self._total_items,
            'start_item': start_item,
            'end_item': end_item,
            'can_go_previous': self.can_go_previous(),
            'can_go_next': self.can_go_next()
        }

    # ...existing code...
    
    # Basic Paging Operations
    def go_to_first_page(self):
        """Navigate to the first page (top of dataset)"""
        if self._current_page != 1:
            self._navigate_to_page(1, "go_to_first")
            
    def go_to_last_page(self):
        """Navigate to the last page (bottom of dataset)"""
        if self._current_page != self._total_pages:
            self._navigate_to_page(self._total_pages, "go_to_last")
            
    def go_to_next_page(self):
        """Navigate to the next page"""
        if self._current_page < self._total_pages:
            self._navigate_to_page(self._current_page + 1, "go_to_next")
            
    def go_to_previous_page(self):
        """Navigate to the previous page"""
        if self._current_page > 1:
            self._navigate_to_page(self._current_page - 1, "go_to_previous")
            
    def go_to_page(self, page_number: int):
        """Navigate to a specific page"""
        if 1 <= page_number <= self._total_pages and page_number != self._current_page:
            self._navigate_to_page(page_number, "go_to_specific")
            
    def refresh_current_page(self):
        """Refresh the current page data"""
        # Clear current page from cache to force reload
        if self._current_page in self._page_cache:
            del self._page_cache[self._current_page]
            
        # Reload current page
        self._navigate_to_page(self._current_page, "refresh")
        
    def _navigate_to_page(self, target_page: int, operation_type: str):
        """Internal method to handle page navigation"""
        if not (1 <= target_page <= self._total_pages):
            return
            
        self._current_page = target_page
        
        # Calculate new visible range for virtual display
        start_idx = (target_page - 1) * self._optimal_page_size
        end_idx = min(start_idx + self._optimal_page_size, self._total_items)
        
        # Update virtual display
        self._visible_range = (start_idx, end_idx)
        self._update_virtual_display()
        
        # Emit navigation completed signal
        self.navigationCompleted.emit(operation_type, target_page)
        
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
        
    def get_total_pages(self) -> int:
        """Get total number of pages"""
        return self._total_pages
        
    def get_total_items(self) -> int:
        """Get total number of items"""
        return self._total_items
        
    def can_go_previous(self) -> bool:
        """Check if can navigate to previous page"""
        return self._current_page > 1
        
    def can_go_next(self) -> bool:
        """Check if can navigate to next page"""
        return self._current_page < self._total_pages
        
    def get_page_info(self) -> Dict:
        """Get comprehensive page information"""
        start_item = (self._current_page - 1) * self._optimal_page_size + 1
        end_item = min(self._current_page * self._optimal_page_size, self._total_items)
        
        return {
            'current_page': self._current_page,
            'total_pages': self._total_pages,
            'page_size': self._optimal_page_size,
            'total_items': self._total_items,
            'start_item': start_item,
            'end_item': end_item,
            'can_go_previous': self.can_go_previous(),
            'can_go_next': self.can_go_next()
        }

    # ...existing code...
```

### 1.2 Enhanced PreferencesPagingSettingsManager

**Purpose:** Extended paging settings manager with virtual metamorphic configurations.

```python
# In services/preferences_paging_service.py - add these methods to existing class

    def get_virtual_paging_settings(self, component_name: str) -> Dict:
        """Get virtual paging specific settings"""
        return {
            "virtual_multiplier": int(self.settings.value(f"{component_name}_virtual_multiplier", 4)),
            "buffer_size": int(self.settings.value(f"{component_name}_buffer_size", 50)),
            "prefetch_enabled": self.settings.value(f"{component_name}_prefetch", True, type=bool),
            "adaptation_enabled": self.settings.value(f"{component_name}_adaptation", True, type=bool),
            "cache_limit": int(self.settings.value(f"{component_name}_cache_limit", 20))
        }
        
    def set_virtual_paging_settings(self, component_name: str, settings_dict: Dict):
        """Set virtual paging specific settings"""
        for key, value in settings_dict.items():
            self.settings.setValue(f"{component_name}_{key}", value)
            
    def get_system_performance_settings(self) -> Dict:
        """Get system-wide performance settings"""
        settings = QSettings("POEditor", "VirtualPaging")
        return {
            "system_performance": settings.value("system_performance", "medium"),
            "memory_limit_mb": int(settings.value("memory_limit_mb", 100)),
            "max_load_time_ms": float(settings.value("max_load_time_ms", 100.0)),
            "max_render_time_ms": float(settings.value("max_render_time_ms", 50.0)),
            "smooth_scrolling": settings.value("smooth_scrolling", True, type=bool),
            "adaptation_interval_ms": int(settings.value("adaptation_interval_ms", 5000))
        }
```

### 1.3 VirtualTableWidget

**Purpose:** Enhanced table widget with virtual metamorphic paging capabilities.

**File:** `widgets/shared/virtual_table_widget.py`

```python
from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                               QAbstractItemView, QMenu, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QWidget)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QAction, QFont
from typing import List, Dict, Any, Optional

class VirtualTableWidget(QTableWidget):
    """Enhanced table widget with virtual metamorphic paging"""
    
    # Enhanced signals for virtual operations
    itemVirtuallySelected = Signal(int, dict)  # row_index, item_data
    virtualContextMenu = Signal(int, dict)     # row_index, item_data
    virtualDataChanged = Signal()
    performanceMetrics = Signal(dict)
    
    def __init__(self, column_configs: List[Dict], parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.column_configs = column_configs
        self.virtual_controller = None
        self._virtual_data: List[Dict] = []
        self._virtual_selection_model = {}
        
        self._setup_virtual_table()
        self._setup_performance_monitoring()
        
    def _setup_virtual_table(self):
        """Setup virtual table configuration"""
        # Configure table for optimal virtual performance
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)  # Disable built-in sorting for virtual mode
        
        # Setup columns
        self.setColumnCount(len(self.column_configs))
        headers = [config['title'] for config in self.column_configs]
        self.setHorizontalHeaderLabels(headers)
        
        # Configure column widths
        header = self.horizontalHeader()
        for i, config in enumerate(self.column_configs):
            if 'width' in config:
                self.setColumnWidth(i, config['width'])
            elif config.get('stretch', False):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
                
        # Setup context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_virtual_context_menu)
        
        # Connect selection changes
        self.itemSelectionChanged.connect(self._on_virtual_selection_changed)
        
    def _setup_performance_monitoring(self):
        """Setup performance monitoring for virtual operations"""
        self._perf_timer = QTimer()
        self._perf_timer.timeout.connect(self._emit_performance_metrics)
        self._perf_timer.start(10000)  # Every 10 seconds
        
        self._render_times = []
        self._selection_times = []
        
    def set_virtual_controller(self, controller: 'VirtualMetamorphicPagingController'):
        """Set the virtual paging controller"""
        self.virtual_controller = controller
        
        # Connect controller signals
        controller.virtualPageChanged.connect(self._on_virtual_page_changed)
        controller.metamorphicAdaptation.connect(self._on_metamorphic_adaptation)
        controller.navigationCompleted.connect(self._on_navigation_completed)
        
    def _on_virtual_page_changed(self, start_idx: int, end_idx: int):
        """Handle virtual page changes from controller"""
        # This is called by the controller when virtual display updates
        pass
        
    def _on_metamorphic_adaptation(self, metrics: Dict):
        """Handle metamorphic adaptation events"""
        # Update table configuration based on adaptation
        if metrics.get('should_adapt', False):
            self._adapt_table_configuration(metrics)
            
    def _adapt_table_configuration(self, metrics: Dict):
        """Adapt table configuration based on performance metrics"""
        # Adjust row height for performance
        avg_render_time = metrics.get('avg_render_time', 0)
        if avg_render_time > 0.05:  # > 50ms
            # Reduce row height for faster rendering
            current_height = self.rowHeight(0) if self.rowCount() > 0 else 30
            new_height = max(20, int(current_height * 0.9))
            self.verticalHeader().setDefaultSectionSize(new_height)
            
    def render_virtual_data(self, data: List[Dict]):
        """Render virtual data to table"""
        import time
        start_time = time.time()
        
        self._virtual_data = data
        self.setRowCount(len(data))
        
        # Render rows efficiently
        for row, item in enumerate(data):
            self._render_virtual_row(row, item)
            
        render_time = time.time() - start_time
        self._render_times.append(render_time)
        
        # Keep only recent render times for metrics
        if len(self._render_times) > 50:
            self._render_times = self._render_times[-50:]
            
    def _render_virtual_row(self, row: int, item: Dict):
        """Render individual virtual row"""
        for col, config in enumerate(self.column_configs):
            field = config['field']
            value = item.get(field, '')
            
            # Create item with virtual data
            table_item = QTableWidgetItem(str(value))
            
            # Apply formatting based on config
            if 'format' in config:
                formatted_value = config['format'](value)
                table_item.setText(formatted_value)
                
            # Apply styling
            if 'style' in config:
                self._apply_item_style(table_item, config['style'], item)
                
            # Set item data for virtual operations
            table_item.setData(Qt.UserRole, item)
            
            self.setItem(row, col, table_item)
            
    def _apply_item_style(self, item: QTableWidgetItem, style: Dict, data: Dict):
        """Apply styling to table item"""
        # Font styling
        if 'font' in style:
            font = QFont()
            font_config = style['font']
            if 'family' in font_config:
                font.setFamily(font_config['family'])
            if 'size' in font_config:
                font.setPointSize(font_config['size'])
            if 'bold' in font_config:
                font.setBold(font_config['bold'])
            item.setFont(font)
            
        # Color styling based on data
        if 'color_rules' in style:
            for rule in style['color_rules']:
                if self._evaluate_color_rule(rule, data):
                    if 'background' in rule:
                        item.setBackground(rule['background'])
                    if 'foreground' in rule:
                        item.setForeground(rule['foreground'])
                    break
                    
    def _evaluate_color_rule(self, rule: Dict, data: Dict) -> bool:
        """Evaluate color rule against data"""
        condition = rule.get('condition', {})
        field = condition.get('field')
        operator = condition.get('operator', '==')
        value = condition.get('value')
        
        if not field or field not in data:
            return False
            
        data_value = data[field]
        
        if operator == '==':
            return data_value == value
        elif operator == '!=':
            return data_value != value
        elif operator == '>':
            return data_value > value
        elif operator == '<':
            return data_value < value
        elif operator == 'contains':
            return value in str(data_value)
        elif operator == 'enabled':
            return bool(data_value)
            
        return False
        
    def _show_virtual_context_menu(self, position):
        """Show context menu for virtual items"""
        item = self.itemAt(position)
        if not item:
            return
            
        row = item.row()
        if row >= len(self._virtual_data):
            return
            
        item_data = self._virtual_data[row]
        
        # Create context menu
        menu = QMenu(self)
        
        # Add standard actions
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self._edit_virtual_item(row, item_data))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_virtual_item(row, item_data))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(lambda: self._copy_virtual_item(row, item_data))
        menu.addAction(copy_action)
        
        # Emit signal for custom context menu handling
        self.virtualContextMenu.emit(row, item_data)
        
        menu.exec(self.mapToGlobal(position))
        
    def _edit_virtual_item(self, row: int, item_data: Dict):
        """Edit virtual item (to be implemented by subclasses)"""
        pass
        
    def _delete_virtual_item(self, row: int, item_data: Dict):
        """Delete virtual item (to be implemented by subclasses)"""
        pass
        
    def _copy_virtual_item(self, row: int, item_data: Dict):
        """Copy virtual item to clipboard"""
        from PySide6.QtWidgets import QApplication
        
        # Create text representation
        text_parts = []
        for config in self.column_configs:
            field = config['field']
            value = item_data.get(field, '')
            text_parts.append(f"{config['title']}: {value}")
            
        clipboard_text = "\n".join(text_parts)
        
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)
        
    def _on_virtual_selection_changed(self):
        """Handle virtual selection changes"""
        import time
        start_time = time.time()
        
        current_row = self.currentRow()
        if 0 <= current_row < len(self._virtual_data):
            item_data = self._virtual_data[current_row]
            self.itemVirtuallySelected.emit(current_row, item_data)
            
        selection_time = time.time() - start_time
        self._selection_times.append(selection_time)
        
        if len(self._selection_times) > 50:
            self._selection_times = self._selection_times[-50:]
            
    def _emit_performance_metrics(self):
        """Emit performance metrics for monitoring"""
        if not self._render_times and not self._selection_times:
            return
            
        metrics = {
            'avg_render_time': sum(self._render_times) / len(self._render_times) if self._render_times else 0,
            'max_render_time': max(self._render_times) if self._render_times else 0,
            'avg_selection_time': sum(self._selection_times) / len(self._selection_times) if self._selection_times else 0,
            'total_virtual_items': len(self._virtual_data),
            'visible_rows': self.rowCount(),
            'memory_estimate': len(self._virtual_data) * 1024  # Rough estimate
        }
        
        self.performanceMetrics.emit(metrics)
        
    def get_virtual_data(self) -> List[Dict]:
        """Get current virtual data"""
        return self._virtual_data.copy()
        
    def get_selected_virtual_item(self) -> Optional[Dict]:
        """Get currently selected virtual item"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self._virtual_data):
            return self._virtual_data[currentRow]
        return None
        
    def refresh_virtual_display(self):
        """Refresh virtual display"""
        if self.virtual_controller:
            self.virtual_controller.refresh_data()
```

## 2. Viewer Component Implementations

### 2.1 TableViewer

**Purpose:** Implements virtual paging for table data viewing with basic navigation operations.

**File:** `widgets/viewers/table_viewer.py`

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Signal, QObject
from typing import List, Dict, Any, Optional
from widgets.shared.virtual_table_widget import VirtualTableWidget
from widgets.shared.advanced_pagination_controls import AdvancedPaginationControls
from services.virtual_metamorphic_paging_controller import VirtualMetamorphicPagingController

class TableViewer(QWidget):
    """Table viewer with virtual metamorphic paging support"""
    
    # Signals for data operations
    itemSelected = Signal(dict)
    itemsChanged = Signal()
    navigationChanged = Signal(str, int)  # operation, page_number
    
    def __init__(self, column_configs: List[Dict], 
                 data_provider: 'PaginationDataProvider',
                 settings_manager: 'PreferencesPagingSettingsManager',
                 component_name: str = "table_viewer",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.component_name = component_name
        self.data_provider = data_provider
        self.settings_manager = settings_manager
        
        self._setup_ui(column_configs)
        self._setup_virtual_paging()
        self._setup_connections()
        
    def _setup_ui(self, column_configs: List[Dict]):
        """Setup the table viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Create virtual table widget
        self.table_widget = VirtualTableWidget(column_configs, self)
        layout.addWidget(self.table_widget, 1)
        
        # Create pagination controls
        self.pagination_controls = AdvancedPaginationControls(self)
        layout.addWidget(self.pagination_controls)
        
    def _setup_virtual_paging(self):
        """Setup virtual metamorphic paging controller"""
        self.paging_controller = VirtualMetamorphicPagingController(
            table_widget=self.table_widget,
            data_provider=self.data_provider,
            component_name=self.component_name,
            settings_manager=self.settings_manager,
            parent=self
        )
        
        # Connect table widget to controller
        self.table_widget.set_virtual_controller(self.paging_controller)
        
    def _setup_connections(self):
        """Setup signal connections"""
        # Pagination control connections
        self.pagination_controls.pageChanged.connect(self._on_page_changed)
        self.pagination_controls.pageSizeChanged.connect(self._on_page_size_changed)
        self.pagination_controls.virtualModeToggled.connect(self._on_virtual_mode_toggled)
        self.pagination_controls.adaptationToggled.connect(self._on_adaptation_toggled)
        
        # Controller connections
        self.paging_controller.navigationCompleted.connect(self._on_navigation_completed)
        self.paging_controller.virtualPageChanged.connect(self._on_virtual_page_changed)
        self.paging_controller.metamorphicAdaptation.connect(self._on_metamorphic_adaptation)
        
        # Table widget connections
        self.table_widget.itemVirtuallySelected.connect(self._on_item_selected)
        self.table_widget.virtualDataChanged.connect(self.itemsChanged.emit)
        self.table_widget.performanceMetrics.connect(self._on_performance_metrics)
        
    # Basic Navigation Operations Implementation
    def go_to_first_page(self):
        """Navigate to first page"""
        self.paging_controller.go_to_first_page()
        
    def go_to_last_page(self):
        """Navigate to last page"""
        self.paging_controller.go_to_last_page()
        
    def go_to_next_page(self):
        """Navigate to next page"""
        self.paging_controller.go_to_next_page()
        
    def go_to_previous_page(self):
        """Navigate to previous page"""
        self.paging_controller.go_to_previous_page()
        
    def go_to_page(self, page_number: int):
        """Navigate to specific page"""
        self.paging_controller.go_to_page(page_number)
        
    def refresh_current_page(self):
        """Refresh current page data"""
        self.paging_controller.refresh_current_page()
        
    def get_current_page_info(self) -> Dict:
        """Get current page information"""
        return self.paging_controller.get_page_info()
        
    # Event handlers
    def _on_page_changed(self, page_number: int):
        """Handle page change from pagination controls"""
        self.go_to_page(page_number)
        
    def _on_page_size_changed(self, page_size: int):
        """Handle page size change"""
        # Update settings and refresh
        self.settings_manager.set_page_size(self.component_name, page_size)
        self.refresh_current_page()
        
    def _on_virtual_mode_toggled(self, enabled: bool):
        """Handle virtual mode toggle"""
        self.paging_controller.set_adaptation_enabled(enabled)
        
    def _on_adaptation_toggled(self, enabled: bool):
        """Handle adaptation toggle"""
        self.paging_controller.set_adaptation_enabled(enabled)
        
    def _on_navigation_completed(self, operation_type: str, target_page: int):
        """Handle navigation completion"""
        # Update pagination controls
        page_info = self.paging_controller.get_page_info()
        self.pagination_controls.set_pagination_info(
            page_info['current_page'],
            page_info['total_pages'],
            page_info['total_items'],
            page_info['page_size']
        )
        
        # Emit navigation signal
        self.navigationChanged.emit(operation_type, target_page)
        
    def _on_virtual_page_changed(self, start_idx: int, end_idx: int):
        """Handle virtual page changes"""
        # Update any UI elements that depend on visible range
        pass
        
    def _on_metamorphic_adaptation(self, metrics: Dict):
        """Handle metamorphic adaptation"""
        # Update pagination controls with new metrics
        self.pagination_controls.update_performance_metrics(metrics)
        
    def _on_item_selected(self, row_index: int, item_data: Dict):
        """Handle item selection"""
        self.itemSelected.emit(item_data)
        
    def _on_performance_metrics(self, metrics: Dict):
        """Handle performance metrics updates"""
        self.pagination_controls.update_performance_metrics(metrics)
        
    # Public interface
    def get_selected_item(self) -> Optional[Dict]:
        """Get currently selected item"""
        return self.table_widget.get_selected_virtual_item()
        
    def get_visible_data(self) -> List[Dict]:
        """Get currently visible data"""
        return self.table_widget.get_virtual_data()
        
    def set_data_provider(self, data_provider: 'PaginationDataProvider'):
        """Set new data provider and refresh"""
        self.data_provider = data_provider
        self.paging_controller.data_provider = data_provider
        self.refresh_current_page()
```

### 2.2 DatabaseViewer

**Purpose:** Specialized viewer for database table data with virtual paging.

**File:** `widgets/viewers/database_viewer.py`

```python
from widgets.viewers.table_viewer import TableViewer
from PySide6.QtCore import Signal
from typing import List, Dict, Optional

class DatabaseViewer(TableViewer):
    """Specialized database table viewer with virtual paging"""
    
    # Additional signals for database operations
    recordInserted = Signal(dict)
    recordUpdated = Signal(dict)
    recordDeleted = Signal(int)
    queryExecuted = Signal(str, int)  # query, affected_rows
    
    def __init__(self, table_name: str,
                 column_configs: List[Dict],
                 data_provider: 'DatabasePaginationProvider',
                 settings_manager: 'PreferencesPagingSettingsManager',
                 parent: Optional[QWidget] = None):
        self.table_name = table_name
        
        super().__init__(
            column_configs=column_configs,
            data_provider=data_provider,
            settings_manager=settings_manager,
            component_name=f"database_viewer_{table_name}",
            parent=parent
        )
        
        self._setup_database_specific_features()
        
    def _setup_database_specific_features(self):
        """Setup database-specific features"""
        # Add database-specific context menu actions
        self.table_widget.virtualContextMenu.connect(self._on_database_context_menu)
        
        # Override table row rendering for database-specific formatting
        self.table_widget._render_table_row = self._render_database_row
        
    def _render_database_row(self, row: int, item: Dict):
        """Custom rendering for database rows"""
        # Implement database-specific row rendering
        # Handle NULL values, data types, etc.
        for col, config in enumerate(self.table_widget.column_configs):
            field = config['field']
            value = item.get(field, '')
            
            # Handle database-specific value formatting
            if value is None:
                display_value = "NULL"
            elif isinstance(value, bool):
                display_value = "TRUE" if value else "FALSE"
            elif isinstance(value, (int, float)) and config.get('data_type') == 'currency':
                display_value = f"${value:.2f}"
            else:
                display_value = str(value)
                
            table_item = self.table_widget.QTableWidgetItem(display_value)
            
            # Apply database-specific styling
            if value is None:
                table_item.setForeground(self.table_widget.Qt.gray)
                
            self.table_widget.setItem(row, col, table_item)
            
    def _on_database_context_menu(self, row: int, item_data: Dict):
        """Handle database-specific context menu"""
        # Add database-specific context menu items
        # Insert, Update, Delete operations
        pass
        
    # Database-specific navigation operations
    def execute_query_and_navigate(self, query: str, page_number: int = 1):
        """Execute query and navigate to specific page"""
        # Update data provider with new query
        self.data_provider.set_query(query)
        
        # Navigate to specified page
        self.go_to_page(page_number)
        
        # Emit query executed signal
        total_rows = self.paging_controller.get_total_items()
        self.queryExecuted.emit(query, total_rows)
        
    def filter_and_refresh(self, filter_conditions: Dict):
        """Apply filters and refresh data"""
        # Update data provider with filters
        self.data_provider.set_filters(filter_conditions)
        
        # Refresh from first page
        self.go_to_first_page()
        
    def sort_and_refresh(self, sort_column: str, sort_order: str):
        """Apply sorting and refresh data"""
        # Update data provider with sorting
        self.data_provider.set_sorting(sort_column, sort_order)
        
        # Refresh current page
        self.refresh_current_page()
```

### 2.3 SearchResultsViewer

**Purpose:** Viewer for search results with virtual paging and highlighting.

**File:** `widgets/viewers/search_results_viewer.py`

```python
from widgets.viewers.table_viewer import TableViewer
from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCharFormat, QColor
from typing import List, Dict, Optional

class SearchResultsViewer(TableViewer):
    """Search results viewer with virtual paging and highlighting"""
    
    # Additional signals for search operations
    searchTermHighlighted = Signal(str, int)  # term, occurrences
    resultSelected = Signal(dict)
    searchNavigated = Signal(str, int, int)  # direction, current_result, total_results
    
    def __init__(self, column_configs: List[Dict],
                 data_provider: 'SearchPaginationProvider',
                 settings_manager: 'PreferencesPagingSettingsManager',
                 parent: Optional[QWidget] = None):
        
        self.search_terms: List[str] = []
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor(255, 255, 0, 100))  # Yellow highlight
        
        super().__init__(
            column_configs=column_configs,
            data_provider=data_provider,
            settings_manager=settings_manager,
            component_name="search_results_viewer",
            parent=parent
        )
        
        self._setup_search_specific_features()
        
    def _setup_search_specific_features(self):
        """Setup search-specific features"""
        # Override table row rendering for search highlighting
        self.table_widget._render_table_row = self._render_search_result_row
        
        # Add search navigation methods
        self._current_search_result = 0
        self._total_search_results = 0
        
    def _render_search_result_row(self, row: int, item: Dict):
        """Custom rendering for search result rows with highlighting"""
        for col, config in enumerate(self.column_configs):
            field = config['field']
            value = str(item.get(field, ''))
            
            # Apply search term highlighting
            highlighted_value = self._highlight_search_terms(value)
            
            table_item = self.table_widget.QTableWidgetItem(highlighted_value)
            
            # Apply search result specific styling
            if self._is_exact_match(value):
                table_item.setBackground(QColor(200, 255, 200))  # Light green for exact matches
                
            self.table_widget.setItem(row, col, table_item)
            
    def _highlight_search_terms(self, text: str) -> str:
        """Highlight search terms in text"""
        highlighted_text = text
        for term in self.search_terms:
            if term.lower() in text.lower():
                highlighted_text = highlighted_text.replace(
                    term, f"<mark>{term}</mark>"
                )
        return highlighted_text
        
    def _is_exact_match(self, text: str) -> bool:
        """Check if text contains exact match for any search term"""
        return any(term.lower() == text.lower() for term in self.search_terms)
        
    # Search-specific navigation operations
    def set_search_terms(self, terms: List[str]):
        """Set search terms for highlighting"""
        self.search_terms = terms
        self.refresh_current_page()
        
        # Count total occurrences
        total_occurrences = sum(
            len([item for item in self.get_visible_data() 
                 if any(term.lower() in str(item.get(field, '')).lower() 
                       for field in [config['field'] for config in self.table_widget.column_configs]
                       for term in self.search_terms)])
        )
        
        self.searchTermHighlighted.emit(', '.join(terms), total_occurrences)
        
    def navigate_to_next_result(self):
        """Navigate to next search result"""
        if self._current_search_result < self._total_search_results - 1:
            self._current_search_result += 1
            self._navigate_to_search_result()
            
    def navigate_to_previous_result(self):
        """Navigate to previous search result"""
        if self._current_search_result > 0:
            self._current_search_result -= 1
            self._navigate_to_search_result()
            
    def _navigate_to_search_result(self):
        """Navigate to current search result"""
        # Calculate which page contains the current result
        items_per_page = self.paging_controller.get_page_info()['page_size']
        target_page = (self._current_search_result // items_per_page) + 1
        
        # Navigate to the page
        self.go_to_page(target_page)
        
        # Highlight the specific result in the table
        result_row = self._current_search_result % items_per_page
        if result_row < self.table_widget.rowCount():
            self.table_widget.selectRow(result_row)
            
        self.searchNavigated.emit(
            "next" if self._current_search_result > 0 else "first",
            self._current_search_result + 1,
            self._total_search_results
        )
        
    def clear_search_results(self):
        """Clear search results and reset viewer"""
        self.search_terms.clear()
        self._current_search_result = 0
        self._total_search_results = 0
        self.data_provider.clear_search()
        self.go_to_first_page()
```

## 2. Enhanced GUI Components from Old Codes

### 2.1 Advanced Pagination Controls Widget

**Purpose:** Advanced pagination controls with virtual mode and adaptation settings.

**File:** `widgets/shared/advanced_pagination_controls.py`

**Design:**
```python
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                               QSpinBox, QComboBox, QPushButton, QFrame)
from PySide6.QtCore import Signal, Qt, QTimer
from typing import Optional

class AdvancedPaginationControls(QWidget):
    """Advanced pagination controls with virtual mode and adaptation settings"""
    
    # Signals for pagination operations
    pageChanged = Signal(int)            # page_number
    pageSizeChanged = Signal(int)        # page_size
    virtualModeToggled = Signal(bool)    # enabled
    adaptationToggled = Signal(bool)     # enabled
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setObjectName("advanced_pagination_controls")
        
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """Setup the pagination controls UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Page size selector
        self.page_size_label = QLabel("Page Size:")
        self.page_size_spinbox = QSpinBox()
        self.page_size_spinbox.setMinimum(1)
        self.page_size_spinbox.setMaximum(1000)
        self.page_size_spinbox.setValue(50)
        self.page_size_spinbox.setObjectName("page_size_spinbox")
        
        layout.addWidget(self.page_size_label)
        layout.addWidget(self.page_size_spinbox)
        
        # Spacer
        layout.addStretch(1)
        
        # Virtual mode toggle
        self.virtual_mode_button = QPushButton("Enable Virtual Mode")
        self.virtual_mode_button.setCheckable(True)
        self.virtual_mode_button.setObjectName("virtual_mode_button")
        
        layout.addWidget(self.virtual_mode_button)
        
        # Adaptation toggle
        self.adaptation_button = QPushButton("Enable Adaptation")
        self.adaptation_button.setCheckable(True)
        self.adaptation_button.setObjectName("adaptation_button")
        
        layout.addWidget(self.adaptation_button)
        
        # Current page info
        self.current_page_label = QLabel("Page: 1")
        self.current_page_label.setObjectName("current_page_label")
        
        layout.addWidget(self.current_page_label)
        
    def _setup_connections(self):
        """Setup signal connections"""
        self.page_size_spinbox.valueChanged.connect(self._on_page_size_changed)
        self.virtual_mode_button.toggled.connect(self._on_virtual_mode_toggled)
        self.adaptation_button.toggled.connect(self._on_adaptation_toggled)
        
    def _on_page_size_changed(self, value: int):
        """Handle page size changes"""
        self.pageSizeChanged.emit(value)
        
    def _on_virtual_mode_toggled(self, checked: bool):
        """Handle virtual mode toggle"""
        if checked:
            self.virtual_mode_button.setText("Disable Virtual Mode")
        else:
            self.virtual_mode_button.setText("Enable Virtual Mode")
            
        self.virtualModeToggled.emit(checked)
        
    def _on_adaptation_toggled(self, checked: bool):
        """Handle adaptation toggle"""
        if checked:
            self.adaptation_button.setText("Disable Adaptation")
        else:
            self.adaptation_button.setText("Enable Adaptation")
            
        self.adaptationToggled.emit(checked)
        
    def set_page_info(self, current_page: int, total_pages: int, total_items: int, page_size: int):
        """Set current page information"""
        self.current_page_label.setText(f"Page: {current_page} of {total_pages} (Total: {total_items})")
        self.page_size_spinbox.setValue(page_size)
        
    def set_virtual_mode_enabled(self, enabled: bool):
        """Set virtual mode enabled/disabled"""
        self.virtual_mode_button.setChecked(enabled)
        self._on_virtual_mode_toggled(enabled)
        
    def set_adaptation_enabled(self, enabled: bool):
        """Set adaptation enabled/disabled"""
        self.adaptation_button.setChecked(enabled)
        self._on_adaptation_toggled(enabled)
```

## 3. Basic Shared Components (From Old Codes Analysis)

### 3.1 BaseDialog

**Purpose:** Standardized dialog base class with consistent styling and behavior.

**File:** `widgets/shared/base_dialog.py`

**Design:**
```python
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QDialogButtonBox, QLabel, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from typing import Optional, List
from lg import logger

class BaseDialog(QDialog):
    """Base dialog class with standardized behavior and styling"""
    
    # Signals for dialog operations
    dialogAccepted = Signal()
    dialogRejected = Signal()
    dialogApplied = Signal()
    
    def __init__(self, title: str = "Dialog", 
                 width: int = 400, 
                 height: int = 300,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.setModal(True)
        
        self._setup_ui()
        self._setup_connections()
        self._apply_theme()
        
    def _setup_ui(self):
        """Setup the base dialog UI structure"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)
        
        # Content area
        self.content_frame = QFrame()
        self.content_frame.setObjectName("dialog_content_frame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addWidget(self.content_frame, 1)
        
        # Button box
        self.button_box = QDialogButtonBox()
        self.button_box.setObjectName("dialog_button_box")
        
        # Standard buttons
        self.ok_button = self.button_box.addButton(QDialogButtonBox.Ok)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.Cancel)
        
        self.main_layout.addWidget(self.button_box)
        
    def _setup_connections(self):
        """Setup signal connections"""
        self.button_box.accepted.connect(self._on_accepted)
        self.button_box.rejected.connect(self._on_rejected)
        
    def _apply_theme(self):
        """Apply dialog-specific theming"""
        self.setObjectName("base_dialog")
        
    def add_apply_button(self) -> QPushButton:
        """Add an Apply button to the dialog"""
        apply_button = self.button_box.addButton(QDialogButtonBox.Apply)
        apply_button.clicked.connect(self._on_applied)
        return apply_button
        
    def add_custom_button(self, text: str, role: QDialogButtonBox.ButtonRole = QDialogButtonBox.ActionRole) -> QPushButton:
        """Add a custom button to the dialog"""
        return self.button_box.addButton(text, role)
        
    def set_content_widget(self, widget: QWidget):
        """Set the main content widget"""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        self.content_layout.addWidget(widget)
        
    def _on_accepted(self):
        """Handle dialog acceptance"""
        if self.validate_input():
            self.dialogAccepted.emit()
            self.accept()
        else:
            logger.warning("Dialog validation failed")
            
    def _on_rejected(self):
        """Handle dialog rejection"""
        self.dialogRejected.emit()
        self.reject()
        
    def _on_applied(self):
        """Handle apply button click"""
        if self.validate_input():
            self.dialogApplied.emit()
        else:
            logger.warning("Dialog validation failed on apply")
            
    def validate_input(self) -> bool:
        """Validate dialog input (override in subclasses)"""
        return True
        
    def set_help_text(self, text: str):
        """Add help text to the dialog"""
        help_label = QLabel(text)
        help_label.setObjectName("dialog_help_text")
        help_label.setWordWrap(True)
        self.content_layout.addWidget(help_label)
```

### 3.2 StatusBarWidget

**Purpose:** Standardized status bar with progress, message, and action areas.

**File:** `widgets/shared/status_bar_widget.py`

**Design:**
```python
from PySide6.QtWidgets import (QStatusBar, QLabel, QProgressBar, QPushButton, 
                               QHBoxLayout, QWidget, QFrame)
from PySide6.QtCore import Signal, QTimer, Qt
from typing import Optional

class StatusBarWidget(QStatusBar):
    """Enhanced status bar with progress and action areas"""
    
    # Signals for status operations
    actionRequested = Signal(str)  # action_name
    progressClicked = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setObjectName("main_status_bar")
        
        self._setup_ui()
        self._setup_timers()
        
    def _setup_ui(self):
        """Setup status bar UI components"""
        # Main message area (permanent widget on left)
        self.message_label = QLabel("Ready")
        self.message_label.setObjectName("status_message")
        self.addPermanentWidget(self.message_label, 1)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setObjectName("status_separator")
        self.addPermanentWidget(separator1)
        
        # Progress area
        self.progress_widget = QWidget()
        self.progress_layout = QHBoxLayout(self.progress_widget)
        self.progress_layout.setContentsMargins(4, 2, 4, 2)
        self.progress_layout.setSpacing(4)
        
        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setMaximumHeight(16)
        
        self.progress_layout.addWidget(self.progress_label)
        self.progress_layout.addWidget(self.progress_bar)
        
        self.addPermanentWidget(self.progress_widget)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setObjectName("status_separator")
        self.addPermanentWidget(separator2)
        
        # Action area
        self.action_widget = QWidget()
        self.action_layout = QHBoxLayout(self.action_widget)
        self.action_layout.setContentsMargins(4, 2, 4, 2)
        self.action_layout.setSpacing(4)
        
        self.addPermanentWidget(self.action_widget)
        
    def _setup_timers(self):
        """Setup timers for auto-clearing messages"""
        self.message_timer = QTimer()
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self._clear_temporary_message)
        
    def show_message(self, message: str, timeout: int = 0):
        """Show message in status bar"""
        self.message_label.setText(message)
        
        if timeout > 0:
            self.message_timer.start(timeout)
            
    def show_permanent_message(self, message: str):
        """Show permanent message"""
        self.message_timer.stop()
        self.message_label.setText(message)
        
    def _clear_temporary_message(self):
        """Clear temporary message"""
        self.message_label.setText("Ready")
        
    def show_progress(self, text: str = "", maximum: int = 100, value: int = 0):
        """Show progress bar with optional text"""
        self.progress_label.setText(text)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)
        
    def update_progress(self, value: int, text: str = None):
        """Update progress value and optional text"""
        self.progress_bar.setValue(value)
        if text is not None:
            self.progress_label.setText(text)
            
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        
    def add_action_button(self, text: str, action_name: str) -> QPushButton:
        """Add action button to status bar"""
        button = QPushButton(text)
        button.setObjectName("status_action_button")
        button.setMaximumHeight(20)
        button.clicked.connect(lambda: self.actionRequested.emit(action_name))
        
        self.action_layout.addWidget(button)
        return button
        
    def clear_action_buttons(self):
        """Clear all action buttons"""
        for i in reversed(range(self.action_layout.count())):
            child = self.action_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
```

### 3.3 SearchWidget

**Purpose:** Reusable search input with advanced features and history.

**File:** `widgets/shared/search_widget.py`

**Design:**
```python
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QPushButton, 
                               QCompleter, QComboBox, QLabel, QMenu)
from PySide6.QtCore import Signal, QTimer, QStringListModel, Qt
from PySide6.QtGui import QAction
from typing import List, Optional
from lg import logger

class SearchWidget(QWidget):
    """Advanced search widget with history and filtering options"""
    
    # Signals for search operations
    searchTriggered = Signal(str)           # search_text
    searchCleared = Signal()
    filterChanged = Signal(str)             # filter_type
    searchModeChanged = Signal(str)         # search_mode
    
    def __init__(self, placeholder: str = "Search...",
                 show_filter: bool = True,
                 show_mode: bool = True,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.show_filter = show_filter
        self.show_mode = show_mode
        self.search_history: List[str] = []
        self.max_history = 20
        
        self._setup_ui(placeholder)
        self._setup_search_timer()
        self._setup_connections()
        
    def _setup_ui(self, placeholder: str):
        """Setup search widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Search mode combo (if enabled)
        if self.show_mode:
            mode_label = QLabel("Mode:")
            self.mode_combo = QComboBox()
            self.mode_combo.addItems(["Contains", "Exact", "Regex", "Wildcard"])
            self.mode_combo.setMaximumWidth(80)
            
            layout.addWidget(mode_label)
            layout.addWidget(self.mode_combo)
            
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setObjectName("search_input")
        
        # Setup completer for history
        self.completer = QCompleter()
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.search_input.setCompleter(self.completer)
        
        layout.addWidget(self.search_input, 1)
        
        # Search button
        self.search_button = QPushButton("🔍")
        self.search_button.setObjectName("search_button")
        self.search_button.setMaximumWidth(30)
        self.search_button.setToolTip("Search")
        
        layout.addWidget(self.search_button)
        
        # Clear button
        self.clear_button = QPushButton("✕")
        self.clear_button.setObjectName("clear_button")
        self.clear_button.setMaximumWidth(30)
        self.clear_button.setToolTip("Clear search")
        
        layout.addWidget(self.clear_button)
        
        # Filter combo (if enabled)
        if self.show_filter:
            filter_label = QLabel("Filter:")
            self.filter_combo = QComboBox()
            self.filter_combo.addItems(["All", "Recent", "Favorites"])
            self.filter_combo.setMaximumWidth(80)
            
            layout.addWidget(filter_label)
            layout.addWidget(self.filter_combo)
            
        # History button
        self.history_button = QPushButton("⏷")
        self.history_button.setObjectName("history_button")
        self.history_button.setMaximumWidth(30)
        self.history_button.setToolTip("Search history")
        
        layout.addWidget(self.history_button)
        
    def _setup_search_timer(self):
        """Setup timer for search delay"""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
    def _setup_connections(self):
        """Setup signal connections"""
        # Search input connections
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self._perform_search)
        
        # Button connections
        self.search_button.clicked.connect(self._perform_search)
        self.clear_button.clicked.connect(self._clear_search)
        self.history_button.clicked.connect(self._show_history_menu)
        
        # Combo connections
        if self.show_mode:
            self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        if self.show_filter:
            self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
            
    def _on_text_changed(self, text: str):
        """Handle text changes with delay"""
        # Start timer for delayed search
        self.search_timer.start(300)  # 300ms delay
        
    def _perform_search(self):
        """Perform the search operation"""
        search_text = self.search_input.text().strip()
        
        if search_text:
            # Add to history
            self._add_to_history(search_text)
            
            # Emit search signal
            self.searchTriggered.emit(search_text)
            
            logger.info(f"Search triggered: {search_text}")
        else:
            self.searchCleared.emit()
            
    def _clear_search(self):
        """Clear search input and emit signal"""
        self.search_input.clear()
        self.searchCleared.emit()
        
    def _show_history_menu(self):
        """Show search history menu"""
        if not self.search_history:
            return
            
        menu = QMenu(self)
        
        for search_term in self.search_history[-10:]:  # Show last 10
            action = QAction(search_term, self)
            action.triggered.connect(lambda checked, term=search_term: self._select_history_item(term))
            menu.addAction(action)
            
        if self.search_history:
            menu.addSeparator()
            clear_action = QAction("Clear History", self)
            clear_action.triggered.connect(self._clear_history)
            menu.addAction(clear_action)
            
        menu.exec(self.history_button.mapToGlobal(self.history_button.rect().bottomLeft()))
        
    def _select_history_item(self, search_term: str):
        """Select item from search history"""
        self.search_input.setText(search_term)
        self._perform_search()
        
    def _add_to_history(self, search_term: str):
        """Add search term to history"""
        # Remove if already exists
        if search_term in self.search_history:
            self.search_history.remove(search_term)
            
        # Add to beginning
        self.search_history.insert(0, search_term)
        
        # Limit history size
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[:self.max_history]
            
        # Update completer
        self.completer_model.setStringList(self.search_history)
        
    def _clear_history(self):
        """Clear search history"""
        self.search_history.clear()
        self.completer_model.setStringList([])
        
    def _on_mode_changed(self, mode: str):
        """Handle search mode changes"""
        self.searchModeChanged.emit(mode.lower())
        
    def _on_filter_changed(self, filter_type: str):
        """Handle filter changes"""
        self.filterChanged.emit(filter_type.lower())
        
    # Public interface
    def set_search_text(self, text: str):
        """Set search text programmatically"""
        self.search_input.setText(text)
        
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_input.text()
        
    def get_search_mode(self) -> str:
        """Get current search mode"""
        if self.show_mode:
            return self.mode_combo.currentText().lower()
        return "contains"
        
    def get_filter_type(self) -> str:
        """Get current filter type"""
        if self.show_filter:
            return self.filter_combo.currentText().lower()
        return "all"
        
    def set_filter_options(self, options: List[str]):
        """Set filter dropdown options"""
        if self.show_filter:
            current = self.filter_combo.currentText()
            self.filter_combo.clear()
            self.filter_combo.addItems(options)
            
            # Restore selection if available
            index = self.filter_combo.findText(current)
            if index >= 0:
                self.filter_combo.setCurrentIndex(index)
```

### 3.4 ToolbarWidget

**Purpose:** Standardized toolbar with actions, search, and customization.

**File:** `widgets/shared/toolbar_widget.py`

**Design:**
```python
from PySide6.QtWidgets import (QToolBar, QWidget, QHBoxLayout, QVBoxLayout, 
                               QToolButton, QLabel, QComboBox, QSizePolicy)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QAction, QIcon
from typing import Dict, List, Optional
from widgets.shared.search_widget import SearchWidget

class ToolbarWidget(QToolBar):
    """Enhanced toolbar with customizable actions and search integration"""
    
    # Signals for toolbar operations
    actionTriggered = Signal(str)           # action_name
    searchTriggered = Signal(str)           # search_text
    viewModeChanged = Signal(str)           # view_mode
    
    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(title, parent)
        
        self.setObjectName("main_toolbar")
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.actions_dict: Dict[str, QAction] = {}
        self._setup_toolbar()
        
    def _setup_toolbar(self):
        """Setup toolbar structure"""
        # Left section - main actions
        self.left_widget = QWidget()
        self.left_layout = QHBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(4, 2, 4, 2)
        self.left_layout.setSpacing(4)
        
        self.addWidget(self.left_widget)
        
        # Spacer to push right section to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)
        
        # Right section - search and view controls
        self.right_widget = QWidget()
        self.right_layout = QHBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(4, 2, 4, 2)
        self.right_layout.setSpacing(8)
        
        # View mode selector
        view_label = QLabel("View:")
        self.view_combo = QComboBox()
        self.view_combo.addItems(["List", "Details", "Icons", "Tree"])
        self.view_combo.setMaximumWidth(80)
        self.view_combo.currentTextChanged.connect(self._on_view_mode_changed)
        
        self.right_layout.addWidget(view_label)
        self.right_layout.addWidget(self.view_combo)
        
        # Search widget
        self.search_widget = SearchWidget(
            placeholder="Search items...",
            show_filter=True,
            show_mode=False
        )
        self.search_widget.searchTriggered.connect(self.searchTriggered.emit)
        
        self.right_layout.addWidget(self.search_widget)
        
        self.addWidget(self.right_widget)
        
    def add_action_group(self, group_name: str, actions: List[Dict]):
        """Add a group of actions to the toolbar"""
        if actions:
            # Add separator before group (except for first group)
            if self.left_layout.count() > 0:
                self.addSeparator()
                
        for action_config in actions:
            self.add_toolbar_action(
                name=action_config['name'],
                text=action_config['text'],
                icon=action_config.get('icon'),
                tooltip=action_config.get('tooltip', action_config['text']),
                enabled=action_config.get('enabled', True)
            )
            
    def add_toolbar_action(self, name: str, text: str, 
                          icon: Optional[QIcon] = None,
                          tooltip: str = "",
                          enabled: bool = True) -> QAction:
        """Add action to toolbar"""
        action = QAction(text, self)
        action.setObjectName(f"toolbar_action_{name}")
        
        if icon:
            action.setIcon(icon)
            
        if tooltip:
            action.setToolTip(tooltip)
            
        action.setEnabled(enabled)
        action.triggered.connect(lambda: self.actionTriggered.emit(name))
        
        # Add to toolbar and store reference
        self.addAction(action)
        self.actions_dict[name] = action
        
        return action
        
    def add_custom_widget(self, widget: QWidget, position: str = "left"):
        """Add custom widget to toolbar"""
        if position == "left":
            self.left_layout.addWidget(widget)
        elif position == "right":
            # Insert before search widget
            self.right_layout.insertWidget(self.right_layout.count() - 1, widget)
            
    def update_action_state(self, name: str, enabled: bool = None, 
                           visible: bool = None, checked: bool = None):
        """Update action state"""
        if name in self.actions_dict:
            action = self.actions_dict[name]
            
            if enabled is not None:
                action.setEnabled(enabled)
            if visible is not None:
                action.setVisible(visible)
            if checked is not None and action.isCheckable():
                action.setChecked(checked)
                
    def set_action_checkable(self, name: str, checkable: bool = True):
        """Make action checkable"""
        if name in self.actions_dict:
            self.actions_dict[name].setCheckable(checkable)
            
    def get_action(self, name: str) -> Optional[QAction]:
        """Get action by name"""
        return self.actions_dict.get(name)
        
    def _on_view_mode_changed(self, mode: str):
        """Handle view mode changes"""
        self.viewModeChanged.emit(mode.lower())
        
    def set_view_mode(self, mode: str):
        """Set view mode programmatically"""
        index = self.view_combo.findText(mode, Qt.MatchFixedString)
        if index >= 0:
            self.view_combo.setCurrentIndex(index)
            
    def get_view_mode(self) -> str:
        """Get current view mode"""
        return self.view_combo.currentText().lower()
        
    def set_search_focus(self):
        """Set focus to search widget"""
        self.search_widget.search_input.setFocus()
        
    def clear_search(self):
        """Clear search widget"""
        self.search_widget._clear_search()
```

### 3.5 LoadingOverlay

**Purpose:** Reusable loading overlay for any widget with progress indication.

**File:** `widgets/shared/loading_overlay.py`

**Design:**
```python
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QProgressBar, QFrame)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor
from typing import Optional

class LoadingOverlay(QWidget):
    """Loading overlay widget with progress indication"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setObjectName("loading_overlay")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        self._setup_ui()
        self._setup_animation()
        
        # Initially hidden
        self.hide()
        
    def _setup_ui(self):
        """Setup loading overlay UI"""
        # Make overlay fill parent
        if self.parent():
            self.resize(self.parent().size())
            
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Loading content frame
        self.content_frame = QFrame()
        self.content_frame.setObjectName("loading_content_frame")
        self.content_frame.setMaximumSize(300, 150)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Loading message
        self.message_label = QLabel("Loading...")
        self.message_label.setObjectName("loading_message")
        self.message_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.message_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("loading_progress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate by default
        content_layout.addWidget(self.progress_bar)
        
        # Detail text (optional)
        self.detail_label = QLabel("")
        self.detail_label.setObjectName("loading_detail")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setVisible(False)
        content_layout.addWidget(self.detail_label)
        
        layout.addWidget(self.content_frame)
        
    def _setup_animation(self):
        """Setup fade in/out animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def paintEvent(self, event):
        """Paint semi-transparent background"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))  # Semi-transparent black
        
    def resizeEvent(self, event):
        """Handle parent resize"""
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)
        
    def show_loading(self, message: str = "Loading...", 
                    show_progress: bool = True,
                    determinate: bool = False,
                    detail: str = ""):
        """Show loading overlay"""
        self.message_label.setText(message)
        
        # Configure progress bar
        self.progress_bar.setVisible(show_progress)
        if show_progress:
            if determinate:
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(100)
                self.progress_bar.setValue(0)
            else:
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(0)
                
        # Configure detail text
        if detail:
            self.detail_label.setText(detail)
            self.detail_label.setVisible(True)
        else:
            self.detail_label.setVisible(False)
            
        # Animate in
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
    def hide_loading(self):
        """Hide loading overlay with animation"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def update_progress(self, value: int, detail: str = ""):
        """Update progress value and detail text"""
        if self.progress_bar.maximum() > 0:  # Determinate mode
            self.progress_bar.setValue(value)
            
        if detail:
            self.detail_label.setText(detail)
            self.detail_label.setVisible(True)
            
    def update_message(self, message: str):
        """Update loading message"""
        self.message_label.setText(message)
```

## 4. Font Management Components

// ...existing code...

## 5. Database Operations Components

// ...existing code...

## System Settings Integration

The virtual metamorphic paging system integrates deeply with system settings to provide optimal performance across different hardware configurations and usage patterns. The settings affect:

1. **Page Size Adaptation**: Automatically adjusts based on system performance
2. **Memory Management**: Respects system memory limits and user preferences  
3. **Rendering Performance**: Adapts to maintain smooth UI experience
4. **User Behavior**: Learns from scroll patterns and usage to optimize performance
5. **Basic Navigation**: Provides consistent navigation operations across all viewer components
6. **Shared Components**: Common UI elements used throughout the application (dialogs, search, toolbars, overlays, status bars)

## Implementation Summary

The basic paging operations (go top/bottom/next/prev pages) are implemented through:

- **VirtualMetamorphicPagingController**: Core navigation logic with virtual paging optimization
- **TableViewer**: Base implementation for all table-based viewers
- **DatabaseViewer**: Specialized for database table viewing with additional database operations
- **SearchResultsViewer**: Specialized for search results with highlighting and search navigation

Additional shared components provide consistent UI experience:

- **BaseDialog**: Standardized dialog base class
- **StatusBarWidget**: Enhanced status bar with progress and actions
- **SearchWidget**: Advanced search with history and filtering
- **ToolbarWidget**: Customizable toolbar with integrated search
- **LoadingOverlay**: Reusable loading indicator for any widget

Each viewer component inherits the basic navigation operations while adding specialized functionality for their specific use cases. The virtual metamorphic paging ensures optimal performance regardless of dataset size, while shared components maintain UI consistency across the application.
```
