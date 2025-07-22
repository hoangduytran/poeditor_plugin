# Simple File Explorer Design Document

## Overview
Design for a simplified file explorer with two modes: Simple Mode (in-panel view) and Advanced Mode (modal dialog). The explorer button will have single-click and right-click behaviors for mode selection.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Explorer Button Integration                   │
├─────────────────────────────────────────────────────────────────┤
│  Single Click → Simple Mode (Panel)                            │
│  Right Click  → Context Menu (Simple/Advanced Mode)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │   Mode Selection  │
                    └───────────────────┘
                           │         │
                    ┌─────────┐  ┌─────────┐
                    │ Simple  │  │Advanced │
                    │  Mode   │  │  Mode   │
                    └─────────┘  └─────────┘
                          │           │
                          ▼           ▼
              ┌─────────────────┐  ┌─────────────────┐
              │   Panel View    │  │  Modal Dialog   │
              │ (Embedded UI)   │  │(Professional UI)│
              └─────────────────┘  └─────────────────┘
```

## Component Architecture

### 1. Explorer Button Integration
```python
class ExplorerButtonManager:
    """Manages explorer button behavior and mode switching"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_mode = ExplorerMode.SIMPLE
        self.simple_explorer = None
        self.advanced_explorer = None
        
    def on_button_click(self):
        """Single click - show simple mode"""
        
    def on_button_right_click(self):
        """Right click - show context menu for mode selection"""
        
    def show_simple_mode(self):
        """Show simple explorer in panel"""
        
    def show_advanced_mode(self):
        """Show professional explorer in modal dialog"""
```

### 2. Simple Explorer Components

#### 2.1 SimpleFileExplorer (Main Container)
```python
class SimpleFileExplorer(QWidget):
    """Simple file explorer with essential features"""
    
    # Signals
    file_opened = Signal(str)
    directory_changed = Signal(str)
    
    def __init__(self, parent=None):
        self.current_directory = self._get_saved_directory()
        self.navigation_history = NavigationHistory()
        self.view_settings = ViewSettings()
        
        # UI Components
        self.toolbar = SimpleToolbar(self)
        self.file_view = SimpleFileView(self)
        self.status_bar = SimpleStatusBar(self)
        
    def _get_saved_directory(self) -> str:
        """Restore last directory from settings"""
        
    def _save_current_directory(self):
        """Save current directory to settings"""
```

#### 2.2 SimpleToolbar (Navigation & Controls)
```python
class SimpleToolbar(QWidget):
    """Simplified toolbar with essential navigation"""
    
    def __init__(self, parent):
        # Navigation buttons
        self.prev_button = QPushButton("←")
        self.next_button = QPushButton("→") 
        self.up_button = QPushButton("↑")
        self.home_button = QPushButton("🏠")
        self.refresh_button = QPushButton("⟳")
        
        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter (e.g., *.py)")
        
        # Current path display
        self.path_label = QLabel()
```

#### 2.3 SimpleFileView (File Display)
```python
class SimpleFileView(QTableView):
    """Simple table view for files with essential columns"""
    
    def __init__(self, parent):
        self.model = SimpleFileSystemModel()
        self.setModel(self.model)
        
        # Configure columns
        self.setup_columns()
        self.setup_sorting()
        self.setup_context_menu()
        
    def setup_columns(self):
        """Setup file table columns"""
        # Columns: Name, Size, Type, Modified
        
    def setup_header_context_menu(self):
        """Right-click header context menu for view modes"""
        
    def auto_resize_columns(self):
        """Double-click header to auto-resize all columns"""
```

#### 2.4 SimpleFileSystemModel (Data Model)
```python
class SimpleFileSystemModel(QFileSystemModel):
    """Optimized file system model for simple view"""
    
    def __init__(self):
        super().__init__()
        self.filter_pattern = "*"
        self.setup_filters()
        
    def set_filter_pattern(self, pattern: str):
        """Set glob filter pattern (e.g., *.py)"""
        
    def apply_filters(self):
        """Apply current filter settings"""
```

### 3. Advanced Explorer (Modal Dialog)

#### 3.1 AdvancedExplorerDialog
```python
class AdvancedExplorerDialog(QDialog):
    """Professional file explorer in modal dialog"""
    
    def __init__(self, parent=None):
        self.professional_explorer = ProfessionalFileExplorer(self)
        self.setup_dialog()
        
    def setup_dialog(self):
        """Setup modal dialog with professional explorer"""
        # Full-screen or large modal dialog
        # Close button integration
        # Settings persistence
```

### 4. Supporting Components

#### 4.1 NavigationHistory
```python
class NavigationHistory:
    """Manages navigation history for prev/next buttons"""
    
    def __init__(self):
        self.history = []
        self.current_index = -1
        
    def add_location(self, path: str):
        """Add new location to history"""
        
    def can_go_back(self) -> bool:
        """Check if can navigate back"""
        
    def can_go_forward(self) -> bool:
        """Check if can navigate forward"""
        
    def go_back(self) -> Optional[str]:
        """Navigate to previous location"""
        
    def go_forward(self) -> Optional[str]:
        """Navigate to next location"""
```

#### 4.2 ViewSettings
```python
class ViewSettings:
    """Manages view preferences and settings"""
    
    def __init__(self):
        self.view_mode = ViewMode.LIST
        self.column_widths = {}
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder
        
    def save_settings(self):
        """Save settings to QSettings"""
        
    def load_settings(self):
        """Load settings from QSettings"""
```

#### 4.3 FileContentViewer
```python
class FileContentViewer(QDialog):
    """Separate window for viewing file content"""
    
    def __init__(self, file_path: str, parent=None):
        self.file_path = file_path
        self.content_widget = self.create_content_widget()
        
    def create_content_widget(self):
        """Create appropriate content viewer based on file type"""
        # Text files: syntax highlighted editor
        # Images: image viewer
        # Other: hex/binary viewer
```

## UI Layout Specifications

### Simple Mode Layout (Panel View)
```
┌─────────────────────────────────────────────────────────────────┐
│ ← → ↑ 🏠 ⟳  [Current/Path/Display]     Filter: [*.py        ] │
├─────────────────────────────────────────────────────────────────┤
│ Name ▼          │ Size     │ Type      │ Modified            │⚙️│
├─────────────────┼──────────┼───────────┼─────────────────────┼───┤
│ 📁 folder1      │          │ Folder    │ 2025-07-14 10:00   │   │
│ 📄 script.py    │ 2.5 KB   │ Python    │ 2025-07-14 09:30   │   │
│ 📄 readme.md    │ 1.2 KB   │ Markdown  │ 2025-07-14 09:15   │   │
│ ...             │          │           │                     │   │
├─────────────────────────────────────────────────────────────────┤
│ 125 items │ 15 folders │ 110 files │ Last updated: 10:05    │
└─────────────────────────────────────────────────────────────────┘
```

### Advanced Mode Layout (Modal Dialog)
```
┌─────────────────────────────────────────────────────────────────┐
│                   Professional File Explorer                    │
├─────────────────────────────────────────────────────────────────┤
│ File Edit View Tools Help                                      │
├─────────────────────────────────────────────────────────────────┤
│ ← → ↑ 🏠 ⟳ │ 📍 Bookmarks │ 🔍 Search │ ⚙️ Settings │ ❌ Close │
├─────────────────────────────────────────────────────────────────┤
│ [Sidebar] │              Main Content Area                      │
│ Bookmarks │ ┌─────────────────────────────────────────────────┐ │
│ Recent    │ │ Detailed file listing with all features        │ │
│ Favorites │ │ Multiple view modes available                   │ │
│           │ │ Advanced search and filtering                   │ │
│           │ │ File preview capabilities                       │ │
│           │ └─────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Status bar with detailed information and progress               │
└─────────────────────────────────────────────────────────────────┘
```

## Feature Specifications

### 1. Core Features (Simple Mode)

#### 1.1 Directory Display
- **Table View**: Name, Size, Type, Modified columns
- **Sortable Columns**: Click header to sort (ascending/descending)
- **Resizable Columns**: Drag column borders to resize
- **Auto-resize**: Double-click header to auto-fit all columns to content
- **Default Mode**: List view with detailed information

#### 1.2 Column Context Menu (Right-click header)
```
┌─────────────────┐
│ List View   ✓   │
│ Icon View       │
│ Compact View    │
├─────────────────┤
│ Show Hidden     │
│ Show Details    │
├─────────────────┤
│ Auto-size Cols  │
│ Reset Layout    │
└─────────────────┘
```

#### 1.3 Navigation Controls
- **Previous (←)**: Go to previous directory in history
- **Next (→)**: Go to next directory in history  
- **Up (↑)**: Go to parent directory
- **Home (🏠)**: Go to user's home directory
- **Refresh (⟳)**: Refresh current directory listing

#### 1.4 Filtering
- **Glob Pattern Input**: Text field for patterns like `*.py`, `*.md`, etc.
- **Real-time Filtering**: Apply filter as user types
- **Common Patterns**: Dropdown with common patterns (*.py, *.js, *.md, etc.)

#### 1.5 File Operations
- **Double-click**: Open file with default application
- **Context Menu**: Basic file operations (copy, delete, rename)
- **View Content**: Right-click → "View Content" opens content viewer

### 2. Advanced Features (Advanced Mode)

#### 2.1 Professional Interface
- Full menu bar with File, Edit, View, Tools, Help
- Advanced toolbar with extended navigation
- Sidebar with bookmarks, recent locations, favorites
- Enhanced status bar with progress indicators

#### 2.2 Multiple View Modes
- **List View**: Detailed table with all columns
- **Icon View**: Large icons with filenames
- **Column View**: Miller columns (like macOS Finder)
- **Timeline View**: Files organized by modification time

#### 2.3 Advanced Search
- Content search within files
- Advanced filter options
- Search result management
- Search history

#### 2.4 File Preview
- Syntax-highlighted text files
- Image preview
- Document preview (if possible)
- Binary file inspection

## Settings Integration

### QSettings Keys
```python
SETTINGS_KEYS = {
    'explorer/current_directory': 'Last visited directory',
    'explorer/view_mode': 'Current view mode (simple/advanced)',
    'explorer/simple_mode_view': 'Simple mode view type (list/icon/compact)',
    'explorer/column_widths': 'Column width preferences',
    'explorer/sort_column': 'Default sort column',
    'explorer/sort_order': 'Default sort order',
    'explorer/filter_pattern': 'Last used filter pattern',
    'explorer/show_hidden': 'Show hidden files',
    'explorer/navigation_history': 'Navigation history (last 50)',
    'explorer/window_geometry': 'Advanced mode dialog geometry',
    'explorer/bookmarks': 'User bookmarks list'
}
```

### Default Settings
```python
DEFAULT_SETTINGS = {
    'current_directory': os.path.expanduser('~'),
    'view_mode': 'simple',
    'simple_mode_view': 'list',
    'column_widths': {'name': 200, 'size': 80, 'type': 100, 'modified': 150},
    'sort_column': 0,  # Name column
    'sort_order': 'ascending',
    'filter_pattern': '*',
    'show_hidden': False
}
```

## Implementation Plan

### Phase 1: Core Simple Explorer
1. **SimpleFileExplorer widget**
   - Basic table view with file system model
   - Navigation toolbar (prev/next/up/home/refresh)
   - Filter input with glob pattern support

2. **Navigation History**
   - History management for prev/next buttons
   - Settings persistence

3. **Column Management**
   - Sortable, resizable columns
   - Header context menu for view modes
   - Auto-resize functionality

### Phase 2: Explorer Button Integration
1. **Button Behavior**
   - Single-click for simple mode
   - Right-click context menu for mode selection

2. **Panel Integration**
   - Embed simple explorer in existing panel system
   - Proper layout management

### Phase 3: Advanced Mode Integration
1. **Modal Dialog**
   - Wrap existing ProfessionalFileExplorer in dialog
   - Settings persistence for dialog geometry

2. **Mode Switching**
   - Seamless switching between modes
   - State preservation during mode changes

### Phase 4: Content Viewer
1. **File Content Dialog**
   - Separate window for file viewing
   - Syntax highlighting for code files
   - Image and document preview

### Phase 5: Settings & Polish
1. **Settings Integration**
   - Comprehensive settings management
   - Import/export settings

2. **Performance Optimization**
   - Lazy loading for large directories
   - Background directory monitoring

3. **Accessibility**
   - Keyboard navigation
   - Screen reader support

## File Structure

```
plugins/explorer/
├── __init__.py
├── plugin.py                          # Main plugin entry point
├── explorer_button_manager.py         # Button behavior management
├── simple/
│   ├── __init__.py
│   ├── simple_file_explorer.py        # Main simple explorer widget
│   ├── simple_toolbar.py              # Navigation toolbar
│   ├── simple_file_view.py            # Table view for files
│   ├── simple_file_model.py           # File system model
│   ├── navigation_history.py          # History management
│   ├── view_settings.py               # View preferences
│   └── file_content_viewer.py         # Content viewing dialog
├── advanced/
│   ├── __init__.py
│   ├── advanced_explorer_dialog.py    # Modal dialog wrapper
│   └── professional_explorer.py       # Existing professional explorer
└── common/
    ├── __init__.py
    ├── explorer_types.py              # Common types and enums
    └── explorer_utils.py              # Utility functions
```

## Integration Points

### 1. Main Window Integration
```python
class MainWindow:
    def setup_explorer_button(self):
        """Setup explorer button with new behavior"""
        self.explorer_button.clicked.connect(self.explorer_manager.on_button_click)
        self.explorer_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.explorer_button.customContextMenuRequested.connect(
            self.explorer_manager.on_button_right_click
        )
```

### 2. Panel System Integration
```python
class PanelManager:
    def add_simple_explorer(self, explorer_widget):
        """Add simple explorer to panel system"""
        # Integration with existing panel layout
        # Proper sizing and visibility management
```

### 3. Settings System Integration
```python
class SettingsManager:
    def register_explorer_settings(self):
        """Register explorer-specific settings"""
        # Add explorer settings to main settings system
        # Provide settings UI integration
```

## User Experience Flow

### Simple Mode Flow
1. User clicks explorer button
2. Simple explorer appears in panel (if not already visible)
3. Shows current directory with basic file listing
4. User can navigate using toolbar buttons
5. Filter files using glob patterns
6. Double-click to open files
7. Right-click header for view options
8. Directory and preferences automatically saved

### Advanced Mode Flow
1. User right-clicks explorer button
2. Context menu appears with mode options
3. User selects "Advanced Mode"
4. Modal dialog opens with professional explorer
5. Full feature set available (bookmarks, search, preview, etc.)
6. User can work with advanced features
7. Close dialog returns to previous state
8. All settings preserved

### Context Menu Flow
```
Right-click Explorer Button
├── Simple Mode (show in panel)
├── Advanced Mode (modal dialog)
├── ─────────────────────────
├── Settings...
└── Help
```

## Testing Strategy

### Unit Tests
- Navigation history functionality
- Filter pattern parsing
- Settings persistence
- File model operations

### Integration Tests
- Button behavior with different modes
- Panel integration
- Modal dialog lifecycle
- Settings synchronization

### User Experience Tests
- Navigation workflow testing
- Column resizing and sorting
- Filter functionality
- Content viewer operation

This design provides a clean, user-friendly file explorer that scales from simple to advanced use cases while maintaining excellent performance and usability.
