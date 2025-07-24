# Component Design: Configurable Paging System

## 1. Component Overview

The Configurable Paging System is a sophisticated collection of interconnected components that provides self-drawn GUI navigation for large datasets. The system supports multiple display modes, custom visual markers, and configurable pagination controls for optimal user experience across different use cases.

### 1.1 Core Components
- **PagedNavScrollbar**: Main dockable navigation widget combining list display with scrollbar
- **TransparentMarkerScrollbar**: PyCharm-inspired marker-based navigation bar
- **PagingScrollBar**: Compact vertical scrollbar with navigation buttons
- **TablePagerBase**: Abstract pagination controller for data models
- **NavBar**: Highlighting navigation bar for marked items

### 1.2 Key Features
- Self-drawn custom GUI components with configurable styling
- Multiple pagination modes (list-based, marker-based, button-based)
- Adaptive UI that responds to width constraints
- Configurable page sizes and display formats
- Visual markers for data highlighting and navigation
- Dockable and resizable interface panels

## 2. Architecture Design

### 2.1 Component Hierarchy

```
Configurable Paging System
├── PagedNavScrollbar (QDockWidget)
│   ├── ListWidget (Current page items)
│   └── TransparentMarkerScrollbar (Navigation)
├── TransparentMarkerScrollbar (QWidget)
│   ├── Custom painted markers
│   └── Mouse interaction handling
├── PagingScrollBar (QWidget)
│   ├── Navigation buttons (First/Prev/Next/Last)
│   ├── Vertical slider
│   └── Page markers (Enhanced version)
├── TablePagerBase (QObject)
│   └── Abstract pagination logic
└── NavBar (QDockWidget)
    └── Highlighted item navigation
```

### 2.2 Data Flow Architecture

```
Data Source → Records/Results → Pagination Controller → Display Components → User Interaction
     ↑                                                                              ↓
     └── Page Change Events ← Navigation Signals ← User Actions ← Visual Components
```

### 2.3 Configuration System

The paging system supports multiple configuration modes:
- **Minimalistic Mode**: Reduced visual elements for compact display
- **Enhanced Mode**: Full feature set with visual markers and tooltips
- **Adaptive Mode**: Automatically adjusts based on available space
- **Custom Styling**: Configurable colors, sizes, and display formats

## 3. Core Components Detail

### 3.1 PagedNavScrollbar

**Purpose**: Main navigation widget that combines list display with marker-based scrollbar navigation.

**Key Features**:
- Dockable widget that can be positioned on left/right sides
- Displays current page items in a list widget
- Integrated marker scrollbar for full dataset navigation
- Adaptive width handling with different display formats
- Status information display

**Configuration Options**:
```python
class PagedNavScrollbar(QDockWidget):
    def __init__(self, title: str = "Navigation", parent: Optional[QWidget] = None):
        # Configurable properties
        self.page_size: int = 20          # Items per page
        self.current_page: int = 0        # Current page index
        self.total_pages: int = 1         # Total page count
        self.current_highlight: int = -1  # Highlighted item index
```

**Display Modes**:
- **Wide Mode**: Shows detailed item information with IDs and indices
- **Narrow Mode**: Compact display with abbreviated text
- **Icon Mode**: Minimal display for very narrow widths

### 3.2 TransparentMarkerScrollbar

**Purpose**: PyCharm-inspired navigation bar with custom-drawn visual markers.

**Key Features**:
- Custom paint events for marker rendering
- Transparent background with overlay markers
- Mouse interaction for direct page jumping
- Tooltip display for page information
- Configurable marker density and styling

**Configuration Options**:
```python
class TransparentMarkerScrollbar(QWidget):
    def set_minimalistic_mode(self, enabled: bool)
    def set_marker_color(self, color: QColor)
    def set_marker_size(self, size: int)
    def set_total_pages(self, pages: int)
```

**Visual Customization**:
- Marker colors and shapes
- Density and spacing
- Transparency levels
- Hover effects and tooltips

### 3.3 PagingScrollBar

**Purpose**: Compact vertical scrollbar with integrated navigation controls.

**Key Features**:
- First/Previous/Next/Last navigation buttons
- Vertical slider for direct page selection
- Page count display
- Entry range indicators
- Configurable button styling

**Enhanced Version Features**:
- Page marker visualization
- Adaptive button sizing
- Custom slider styling
- Entry count tooltips

### 3.4 TablePagerBase

**Purpose**: Abstract base class for pagination logic and data management.

**Key Features**:
```python
class TablePagerBase(QObject):
    # Signals
    pageChanged = Signal(int)
    pageSizeChanged = Signal(int)
    
    # Core methods
    def go_to_page(self, page: int)
    def set_page_size(self, size: int)
    def get_page_info(self) -> tuple
    def get_page_indices(self) -> tuple
```

**Data Management**:
- Page calculation and bounds checking
- Page size configuration
- Navigation state tracking
- Signal emission for UI updates

### 3.5 NavBar

**Purpose**: Specialized navigation for highlighted/marked items.

**Key Features**:
- Visual highlighting with configurable colors
- Clickable marked items only
- Compact dockable interface
- Item selection signals

## 4. Configuration and Customization

### 4.1 Visual Configuration

**Color Schemes**:
```python
# Default color configuration
BG_COLOR = "#f0f0f0"           # Background color
HL_COLOR = "#e6f3ff"           # Highlight color
ALT_ROW_COLOR = "#f8f8f8"      # Alternating row color
MARKED_COLOR = "lightgreen"     # Marked item color
UNMARKED_COLOR = "lightgray"    # Unmarked item color
```

**Size Configuration**:
```python
# Configurable dimensions
minimum_width = 40              # Minimum widget width
default_page_size = 20          # Default items per page
button_height = 28              # Navigation button height
marker_size = 4                 # Marker width in pixels
```

### 4.2 Behavioral Configuration

**Page Size Options**:
- Configurable page sizes (10, 20, 50, 100)
- Dynamic page size adjustment
- Automatic recalculation of page indices

**Display Format Options**:
- Detailed format: `#{id} (index/total)`
- Compact format: `#{id}`
- Icon-only format for narrow displays

**Navigation Modes**:
- Button-based navigation (First/Prev/Next/Last)
- Slider-based navigation (Direct page selection)
- Marker-based navigation (Click on visual markers)
- Keyboard navigation support

### 4.3 Settings Integration

The system integrates with Qt Settings for persistent configuration:

```python
from PySide6.QtCore import QSettings

settings = QSettings("POEditor", "Settings")
use_minimalistic = settings.value("ui/minimalistic_scrollbar", "0") == "1"
default_page_size = int(settings.value("paging/default_page_size", "20"))
```

**Environment Variable Support**:
```python
import os
minimalistic = os.environ.get("MARKER_SCROLLBAR_MINIMALISTIC") == "1"
```

## 5. Data Models and Types

### 5.1 Core Data Types

```python
@dataclass
class NavRecord:
    row_index: int      # Original row index in source data
    unique_id: Any      # Unique identifier for the record
    page_index: int     # Which page this record belongs to
    local_index: int    # Index within the page

@dataclass
class FindReplaceResult:
    matched_row_id: int  # Database row ID
    row_index: int       # Table row index
    # Additional result data...
```

### 5.2 Page Management

```python
class PageManager:
    def calculate_pagination(self, total_items: int, page_size: int) -> tuple:
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        return total_pages, page_size
    
    def get_page_bounds(self, page_idx: int, page_size: int) -> tuple:
        start_idx = page_idx * page_size
        end_idx = start_idx + page_size
        return start_idx, end_idx
```

## 6. Signal Communication

### 6.1 Navigation Signals

```python
# Page change signals
pageHasChanged = Signal(int)    # Emitted after page change
selectPage = Signal(int)        # Emitted when page is selected
goFirst = Signal()              # First page navigation
goLast = Signal()               # Last page navigation
goNext = Signal()               # Next page navigation
goPrev = Signal()               # Previous page navigation

# Selection signals
itemSelected = Signal(int)      # Item selection in navigation
item_selected = Signal(int)     # Marked item selection
navbar_closed = Signal()        # Navigation bar closed
```

### 6.2 Data Update Signals

```python
# Data management signals
dataChanged = Signal()          # Dataset changed
pageSizeChanged = Signal(int)   # Page size modified
totalPagesChanged = Signal(int) # Total page count changed
highlightChanged = Signal(int)  # Highlight position changed
```

## 7. Custom Drawing and Styling

### 7.1 Marker Rendering

The system includes sophisticated custom drawing for visual markers:

```python
def _paint_markers(self, event):
    """Custom paint event for marker rendering"""
    painter = QPainter(self.marker_container)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Calculate marker positions and draw
    for page_idx in range(self.total_pages):
        y_pos = (page_idx / self.total_pages) * container_height
        self._draw_marker(painter, x_pos, y_pos, is_current, container_width)
```

### 7.2 Adaptive Styling

The components automatically adapt their appearance based on available space:

```python
def _adjust_items_to_width(self) -> None:
    """Adjust display format based on current width"""
    current_width = self.list_widget.width()
    
    if current_width < 60:
        # Icon mode - very compact
        format_function = lambda record: f"#{record.unique_id}"
    elif current_width < 120:
        # Compact mode
        format_function = lambda record: f"#{record.unique_id} ({record.row_index})"
    else:
        # Detailed mode
        format_function = lambda record: f"#{record.unique_id} ({global_idx+1}/{total})"
```

### 7.3 Theme Integration

The paging system supports custom themes and styling:

```python
# Enhanced slider styling
slider_style = """
QSlider::groove:vertical {
    background: #e0e0e0;
    width: 4px;
    border-radius: 2px;
}
QSlider::handle:vertical {
    background: #2196F3;
    border: none;
    height: 10px;
    width: 12px;
    margin: 0 -4px;
    border-radius: 3px;
}
"""
```

## 8. Integration Patterns

### 8.1 Widget Integration

Components can be easily integrated into existing layouts:

```python
# Dock widget integration
paged_nav = PagedNavScrollbar("Search Results")
main_window.addDockWidget(Qt.LeftDockWidgetArea, paged_nav)

# Layout integration
layout = QHBoxLayout()
layout.addWidget(content_area, 1)
layout.addWidget(paging_scrollbar)
```

### 8.2 Data Source Integration

The system works with various data sources:

```python
# Database results
paging_widget.setResults(database_results, page_size=20)

# Search results
paging_widget.set_page_data(search_results, total_items=1000)

# Filtered data
paging_widget.update_pagination()
```

## 9. Performance Considerations

### 9.1 Lazy Loading

The system supports lazy loading of page data:
- Only current page items are rendered in the list
- Markers are drawn efficiently without loading full data
- Page data is loaded on-demand during navigation

### 9.2 Memory Management

- Efficient storage of navigation records
- Minimal memory footprint for large datasets
- Proper cleanup of UI elements during page changes

### 9.3 Rendering Optimization

- Custom paint events use optimized drawing operations
- Marker density adaptation for performance
- Efficient update cycles for smooth navigation

## 10. Testing and Examples

### 10.1 Test Components

The system includes comprehensive test components:
- `enhanced_paged_nav_scrollbar.py`: Full-featured test implementation
- `enhanced_paging_scrollbar.py`: Scrollbar-specific testing
- `paged_nav_scrollbar_enhanced.py`: Enhanced navigation testing

### 10.2 Demo Applications

Example applications demonstrate usage patterns:
- Large dataset navigation
- Search result browsing
- Table data pagination
- Multi-context integration

### 10.3 Configuration Examples

```python
# Minimalistic configuration
pager = PagedNavScrollbar("Results")
pager.scrollbar.set_minimalistic_mode(True)
pager.set_page_size(50)

# Enhanced configuration
pager = PagedNavScrollbar("Enhanced Results")
pager.enhance_scrollbar_appearance()
pager.set_page_size(20)
```

## 11. Future Extensions

### 11.1 Planned Enhancements
- Virtual scrolling for very large datasets
- Custom marker shapes and animations
- Keyboard shortcut integration
- Touch gesture support for tablet interfaces

### 11.2 Plugin Architecture
- Custom formatter plugins
- Theme extension system
- Navigation behavior plugins
- Data source adapters

This configurable paging system provides a comprehensive, flexible solution for navigating large datasets with a self-drawn GUI that adapts to different use cases and display constraints. The modular design allows for easy customization and integration into various application contexts.
