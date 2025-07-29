# Explorer Header Context Menu Technical Design

**Date**: July 29, 2025, 08:20  
**Component**: Explorer Header Context Menu  
**Status**: Technical Design  
**Priority**: High

## Overview

This document provides the detailed technical design for the Explorer Header Context Menu system. The context menu appears when right-clicking on the Explorer panel header and provides quick access to navigation features and column management.

## Context Menu Structure

### Menu Hierarchy

```
Explorer Header Context Menu
├── Quick Navigation
│   ├── Goto Dropdown Interface     ─┐ 
│   ├── Search Field Interface      ─┤ UI Components
│   └── Navigation Buttons          ─┘
├── ─────────────────────────────────
├── Quick Locations
│   ├── 🏠 Home                     (~)
│   ├── 💾 Root                     (/)
│   ├── 📁 Applications             (/Applications)
│   ├── 📄 Documents                (~/Documents)
│   ├── ⬇️  Downloads               (~/Downloads)
│   ├── 🖥️  Desktop                 (~/Desktop)
│   └── ⚙️  Project Root            (/project/path)
├── ─────────────────────────────────
├── Recent Locations
│   ├── → /recent/path/1            (2 hours ago)
│   ├── → /recent/path/2            (Yesterday)
│   └── → /recent/path/3            (3 days ago)
├── ─────────────────────────────────
├── Bookmarks
│   ├── ⭐ Favorite Project         (/path/to/project)
│   ├── ⭐ Important Docs           (/path/to/docs)
│   └── ⭐ Custom Location          (/custom/path)
├── ─────────────────────────────────
├── Navigation Actions
│   ├── 📍 Go to Path...            (Ctrl+G)
│   ├── 📚 Manage Bookmarks...
│   └── 🔄 Refresh Navigation
├── ─────────────────────────────────
├── Column Management
│   ├── 📋 Add/Remove Columns...
│   ├── ⚙️  Column Settings...
│   ├── 📏 Reset Column Widths
│   └── 🔄 Reset to Defaults
└── ─────────────────────────────────
```

## Technical Architecture

### Class Design

#### 1. ExplorerHeaderContextMenu

```python
from PySide6.QtWidgets import QMenu, QAction, QActionGroup
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon

class ExplorerHeaderContextMenu(QMenu):
    """
    Context menu for Explorer header providing navigation and column management.
    
    Signals:
        navigate_requested(str): Emitted when navigation to a path is requested
        show_goto_dialog(): Emitted when Go to Path dialog should be shown
        show_bookmark_manager(): Emitted when bookmark manager should be shown
        show_column_manager(): Emitted when column manager should be shown
        column_visibility_changed(str, bool): Emitted when column visibility changes
    """
    
    # Signals
    navigate_requested = Signal(str)
    show_goto_dialog = Signal()
    show_bookmark_manager = Signal()
    show_column_manager = Signal()
    column_visibility_changed = Signal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.location_manager = None
        self.navigation_service = None
        self.column_service = None
        self._setup_services()
        self._build_menu()
        
    def _setup_services(self):
        """Initialize required services."""
        pass
        
    def _build_menu(self):
        """Build the complete context menu structure."""
        self._add_navigation_section()
        self.addSeparator()
        self._add_quick_locations()
        self.addSeparator()
        self._add_recent_locations()
        self.addSeparator()
        self._add_bookmarks()
        self.addSeparator()
        self._add_navigation_actions()
        self.addSeparator()
        self._add_column_management()
```

#### 2. NavigationSection

```python
class NavigationSection(QObject):
    """
    Handles the navigation UI components section of the context menu.
    """
    
    def __init__(self, parent_menu: QMenu):
        super().__init__()
        self.parent_menu = parent_menu
        
    def create_section(self):
        """Create navigation interface preview section."""
        # This shows a preview/demo of the navigation interface
        nav_action = QAction("Quick Navigation Interface", self.parent_menu)
        nav_action.setEnabled(False)  # Header item
        self.parent_menu.addAction(nav_action)
        
        # Sub-items showing components
        goto_action = QAction("  [Goto ▼] - Location Dropdown", self.parent_menu)
        search_action = QAction("  [Search] - Path Search Field", self.parent_menu)
        buttons_action = QAction("  [← → ↑ 🏠] - Navigation Buttons", self.parent_menu)
        
        goto_action.triggered.connect(self._show_goto_dropdown)
        search_action.triggered.connect(self._focus_search_field)
        buttons_action.triggered.connect(self._highlight_nav_buttons)
        
        self.parent_menu.addAction(goto_action)
        self.parent_menu.addAction(search_action)
        self.parent_menu.addAction(buttons_action)
```

#### 3. QuickLocationsSection

```python
class QuickLocationsSection(QObject):
    """
    Manages quick location menu items.
    """
    
    def __init__(self, parent_menu: QMenu, location_manager):
        super().__init__()
        self.parent_menu = parent_menu
        self.location_manager = location_manager
        
    def create_section(self):
        """Create quick locations section."""
        locations = self.location_manager.get_quick_locations()
        
        for location in locations:
            action = QAction(
                location.icon, 
                f"{location.name} ({location.path})", 
                self.parent_menu
            )
            action.triggered.connect(
                lambda checked, path=location.path: self._navigate_to(path)
            )
            self.parent_menu.addAction(action)
            
    def _navigate_to(self, path: str):
        """Navigate to the specified path."""
        # Emit signal to parent menu
        self.parent().navigate_requested.emit(path)
```

#### 4. ColumnManagementSection

```python
class ColumnManagementSection(QObject):
    """
    Handles column management menu items.
    """
    
    def __init__(self, parent_menu: QMenu, column_service):
        super().__init__()
        self.parent_menu = parent_menu
        self.column_service = column_service
        
    def create_section(self):
        """Create column management section."""
        # Add/Remove Columns submenu
        columns_menu = self.parent_menu.addMenu("Add/Remove Columns")
        self._build_columns_submenu(columns_menu)
        
        # Column Settings
        settings_action = QAction("Column Settings...", self.parent_menu)
        settings_action.triggered.connect(self._show_column_settings)
        self.parent_menu.addAction(settings_action)
        
        # Reset actions
        reset_widths_action = QAction("Reset Column Widths", self.parent_menu)
        reset_all_action = QAction("Reset to Defaults", self.parent_menu)
        
        reset_widths_action.triggered.connect(self._reset_column_widths)
        reset_all_action.triggered.connect(self._reset_all_columns)
        
        self.parent_menu.addAction(reset_widths_action)
        self.parent_menu.addAction(reset_all_action)
        
    def _build_columns_submenu(self, submenu: QMenu):
        """Build the columns visibility submenu."""
        available_columns = self.column_service.get_available_columns()
        visible_columns = self.column_service.get_visible_columns()
        
        for column in available_columns:
            action = QAction(column.display_name, submenu)
            action.setCheckable(True)
            action.setChecked(column.id in visible_columns)
            action.setEnabled(column.id != 'name')  # Name column always visible
            
            action.toggled.connect(
                lambda checked, col_id=column.id: self._toggle_column(col_id, checked)
            )
            submenu.addAction(action)
```

### Service Integration

#### 5. Required Services

```python
class LocationManager:
    """Service for managing quick locations and bookmarks."""
    
    def get_quick_locations(self) -> List[QuickLocation]:
        """Get standard quick access locations."""
        return [
            QuickLocation("Home", "🏠", str(Path.home())),
            QuickLocation("Root", "💾", "/"),
            QuickLocation("Applications", "📁", "/Applications"),
            QuickLocation("Documents", "📄", str(Path.home() / "Documents")),
            QuickLocation("Downloads", "⬇️", str(Path.home() / "Downloads")),
            QuickLocation("Desktop", "🖥️", str(Path.home() / "Desktop")),
            QuickLocation("Project Root", "⚙️", self._get_project_root()),
        ]
        
    def get_recent_locations(self, limit: int = 5) -> List[RecentLocation]:
        """Get recently visited locations with timestamps."""
        # Return recent locations from history
        pass
        
    def get_bookmarks(self) -> List[LocationBookmark]:
        """Get user-defined bookmarks."""
        # Return saved bookmarks
        pass

class NavigationService:
    """Service for handling navigation operations."""
    
    def navigate_to(self, path: str) -> bool:
        """Navigate to specified path."""
        pass
        
    def add_to_history(self, path: str):
        """Add path to navigation history."""
        pass

class ColumnConfigurationService:
    """Service for managing column display settings."""
    
    def get_available_columns(self) -> List[ColumnDefinition]:
        """Get all available column definitions."""
        return [
            ColumnDefinition("name", "Name", True, False),  # Always visible
            ColumnDefinition("size", "Size", True, True),
            ColumnDefinition("modified", "Modified", True, True),
            ColumnDefinition("type", "Type", True, True),
            ColumnDefinition("created", "Created", False, True),
            ColumnDefinition("permissions", "Permissions", False, True),
            ColumnDefinition("owner", "Owner", False, True),
            ColumnDefinition("extension", "Extension", False, True),
        ]
        
    def get_visible_columns(self) -> List[str]:
        """Get currently visible column IDs."""
        pass
        
    def set_column_visibility(self, column_id: str, visible: bool):
        """Set column visibility."""
        pass
```

### Data Models

#### 6. Data Structures

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class QuickLocation:
    """Represents a quick access location."""
    name: str
    icon: str
    path: str
    description: Optional[str] = None

@dataclass  
class RecentLocation:
    """Represents a recently visited location."""
    path: str
    timestamp: datetime
    visit_count: int = 1
    
    @property
    def relative_time(self) -> str:
        """Get human-readable relative time."""
        delta = datetime.now() - self.timestamp
        if delta.days == 0:
            if delta.seconds < 3600:
                return f"{delta.seconds // 60} minutes ago"
            else:
                return f"{delta.seconds // 3600} hours ago"
        elif delta.days == 1:
            return "Yesterday"
        else:
            return f"{delta.days} days ago"

@dataclass
class LocationBookmark:
    """Represents a user-defined bookmark."""
    id: str
    name: str
    path: str
    icon: str = "⭐"
    created: datetime = None
    
    def __post_init__(self):
        if self.created is None:
            self.created = datetime.now()

@dataclass
class ColumnDefinition:
    """Defines an available column."""
    id: str
    display_name: str
    visible: bool
    can_hide: bool
    width: int = -1  # -1 for auto-width
    resizable: bool = True
    sortable: bool = True
```

## Menu Construction Logic

### 7. Dynamic Menu Building

```python
class MenuBuilder:
    """Builds the context menu dynamically based on current state."""
    
    def __init__(self, location_manager, navigation_service, column_service):
        self.location_manager = location_manager
        self.navigation_service = navigation_service
        self.column_service = column_service
        
    def build_menu(self, parent: QWidget) -> ExplorerHeaderContextMenu:
        """Build the complete context menu."""
        menu = ExplorerHeaderContextMenu(parent)
        
        # Set up service references
        menu.location_manager = self.location_manager
        menu.navigation_service = self.navigation_service
        menu.column_service = self.column_service
        
        # Build sections
        self._build_navigation_preview(menu)
        menu.addSeparator()
        
        self._build_quick_locations(menu)
        menu.addSeparator()
        
        self._build_recent_locations(menu)
        menu.addSeparator()
        
        self._build_bookmarks(menu)
        menu.addSeparator()
        
        self._build_navigation_actions(menu)
        menu.addSeparator()
        
        self._build_column_management(menu)
        
        return menu
        
    def _build_navigation_preview(self, menu: QMenu):
        """Build navigation interface preview section."""
        preview_action = QAction("Quick Navigation Interface", menu)
        preview_action.setEnabled(False)
        menu.addAction(preview_action)
        
        # Add component preview items
        components = [
            ("  [Goto ▼] Location Dropdown", self._activate_goto_dropdown),
            ("  [Search] Path Search Field", self._activate_search_field), 
            ("  [← → ↑ 🏠] Navigation Buttons", self._highlight_nav_buttons)
        ]
        
        for text, callback in components:
            action = QAction(text, menu)
            action.triggered.connect(callback)
            menu.addAction(action)
```

## Integration with Explorer Panel

### 8. Header Bar Integration

```python
class ExplorerHeaderBar(QWidget):
    """Enhanced header bar with navigation and context menu support."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context_menu_builder = None
        self._setup_ui()
        self._setup_context_menu()
        
    def _setup_ui(self):
        """Set up the header bar UI."""
        layout = QHBoxLayout(self)
        
        # Goto dropdown
        self.goto_dropdown = GotoDropdown()
        layout.addWidget(self.goto_dropdown)
        
        # Search field
        self.search_field = PathSearchField()
        layout.addWidget(self.search_field, 1)  # Stretch
        
        # Navigation buttons
        self.nav_buttons = NavigationButtons()
        layout.addWidget(self.nav_buttons)
        
    def _setup_context_menu(self):
        """Set up right-click context menu."""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _show_context_menu(self, position):
        """Show the header context menu."""
        if self.context_menu_builder:
            menu = self.context_menu_builder.build_menu(self)
            
            # Connect menu signals
            menu.navigate_requested.connect(self._handle_navigation)
            menu.show_goto_dialog.connect(self._show_goto_dialog)
            menu.show_bookmark_manager.connect(self._show_bookmark_manager)
            menu.show_column_manager.connect(self._show_column_manager)
            menu.column_visibility_changed.connect(self._handle_column_visibility)
            
            # Show menu
            menu.exec_(self.mapToGlobal(position))
```

## Event Handling

### 9. Signal/Slot Connections

```python
class ExplorerHeaderManager(QObject):
    """Manages all header-related functionality and event coordination."""
    
    # Signals
    navigation_requested = Signal(str)
    column_configuration_changed = Signal()
    
    def __init__(self, explorer_panel):
        super().__init__()
        self.explorer_panel = explorer_panel
        self.header_bar = None
        self._setup_services()
        self._setup_header()
        
    def _setup_header(self):
        """Set up the header bar with context menu."""
        self.header_bar = ExplorerHeaderBar()
        
        # Create menu builder
        menu_builder = MenuBuilder(
            self.location_manager,
            self.navigation_service, 
            self.column_service
        )
        self.header_bar.context_menu_builder = menu_builder
        
        # Connect signals
        self._connect_signals()
        
    def _connect_signals(self):
        """Connect all header-related signals."""
        # Navigation signals
        self.header_bar.goto_dropdown.location_selected.connect(self.navigation_requested)
        self.header_bar.search_field.path_entered.connect(self.navigation_requested)
        self.header_bar.nav_buttons.navigate_back.connect(self._handle_back)
        self.header_bar.nav_buttons.navigate_forward.connect(self._handle_forward)
        self.header_bar.nav_buttons.navigate_up.connect(self._handle_up)
        self.header_bar.nav_buttons.navigate_home.connect(self._handle_home)
```

## Accessibility Features

### 10. Accessibility Implementation

```python
class AccessibleHeaderContextMenu(ExplorerHeaderContextMenu):
    """Context menu with enhanced accessibility features."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_accessibility()
        
    def _setup_accessibility(self):
        """Set up accessibility features."""
        # Set accessible names and descriptions
        self.setAccessibleName("Explorer Header Context Menu")
        self.setAccessibleDescription(
            "Context menu providing navigation options and column management"
        )
        
        # Add keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Set up screen reader announcements
        self._setup_screen_reader_support()
        
    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for menu items."""
        shortcuts = {
            'goto_path': 'Ctrl+G',
            'navigate_home': 'Ctrl+H',
            'manage_bookmarks': 'Ctrl+B',
            'column_settings': 'Ctrl+Shift+C'
        }
        
        for action_name, shortcut in shortcuts.items():
            action = self.findChild(QAction, action_name)
            if action:
                action.setShortcut(shortcut)
                
    def keyPressEvent(self, event):
        """Handle keyboard navigation within menu."""
        if event.key() == Qt.Key_F1:
            # Show help for current menu item
            self._show_context_help()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Activate current item
            current_action = self.activeAction()
            if current_action and current_action.isEnabled():
                current_action.trigger()
        else:
            super().keyPressEvent(event)
```

## Testing Strategy

### 11. Test Implementation

```python
import pytest
from unittest.mock import Mock, patch
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

class TestExplorerHeaderContextMenu:
    """Test suite for Explorer Header Context Menu."""
    
    @pytest.fixture
    def setup_menu(self):
        """Set up test menu with mocked services."""
        location_manager = Mock()
        navigation_service = Mock()
        column_service = Mock()
        
        menu = ExplorerHeaderContextMenu()
        menu.location_manager = location_manager
        menu.navigation_service = navigation_service
        menu.column_service = column_service
        
        return menu
        
    def test_menu_creation(self, setup_menu):
        """Test menu is created with all sections."""
        menu = setup_menu
        actions = menu.actions()
        
        # Verify sections exist
        section_texts = [action.text() for action in actions if action.text()]
        assert "Quick Navigation Interface" in section_texts
        assert any("Home" in text for text in section_texts)
        assert any("Column" in text for text in section_texts)
        
    def test_quick_location_navigation(self, setup_menu):
        """Test navigation to quick locations."""
        menu = setup_menu
        
        # Mock location manager
        menu.location_manager.get_quick_locations.return_value = [
            QuickLocation("Home", "🏠", "/home/user")
        ]
        
        # Rebuild menu to include mocked locations
        menu._build_menu()
        
        # Find home action and trigger it
        for action in menu.actions():
            if "Home" in action.text():
                with patch.object(menu, 'navigate_requested') as mock_signal:
                    action.trigger()
                    mock_signal.emit.assert_called_once_with("/home/user")
                break
        else:
            pytest.fail("Home action not found")
            
    def test_column_visibility_toggle(self, setup_menu):
        """Test column visibility toggling."""
        menu = setup_menu
        
        # Mock column service
        mock_column = ColumnDefinition("size", "Size", True, True)
        menu.column_service.get_available_columns.return_value = [mock_column]
        menu.column_service.get_visible_columns.return_value = ["size"]
        
        # Rebuild menu
        menu._build_menu()
        
        # Find column management submenu
        for action in menu.actions():
            if hasattr(action, 'menu') and "Column" in action.text():
                submenu = action.menu()
                size_action = None
                for subaction in submenu.actions():
                    if "Size" in subaction.text():
                        size_action = subaction
                        break
                        
                if size_action:
                    with patch.object(menu, 'column_visibility_changed') as mock_signal:
                        size_action.toggle()
                        mock_signal.emit.assert_called_once()
                break
                
    def test_keyboard_shortcuts(self, setup_menu):
        """Test keyboard shortcuts work correctly."""
        menu = setup_menu
        
        # Test Ctrl+G for Go to Path
        with patch.object(menu, 'show_goto_dialog') as mock_signal:
            QTest.keySequence(menu, "Ctrl+G")
            mock_signal.emit.assert_called_once()
            
    def test_accessibility_features(self, setup_menu):
        """Test accessibility features are properly set."""
        menu = setup_menu
        
        # Check accessible name is set
        assert menu.accessibleName() == "Explorer Header Context Menu"
        
        # Check actions have accessible descriptions
        for action in menu.actions():
            if action.text() and not action.isSeparator():
                assert action.accessibleDescription() or action.toolTip()
```

## Performance Considerations

### 12. Optimization Strategies

#### 12.1 Lazy Menu Construction
```python
class LazyMenuBuilder(MenuBuilder):
    """Menu builder with lazy loading optimizations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._menu_cache = {}
        self._cache_timeout = 5.0  # seconds
        
    def build_menu(self, parent: QWidget) -> ExplorerHeaderContextMenu:
        """Build menu with caching."""
        cache_key = self._get_cache_key()
        
        if cache_key in self._menu_cache:
            cached_menu, timestamp = self._menu_cache[cache_key]
            if time.time() - timestamp < self._cache_timeout:
                return cached_menu
                
        # Build new menu
        menu = super().build_menu(parent)
        self._menu_cache[cache_key] = (menu, time.time())
        
        return menu
        
    def _get_cache_key(self) -> str:
        """Generate cache key based on current state."""
        # Include relevant state that affects menu content
        visible_columns = self.column_service.get_visible_columns()
        recent_count = len(self.location_manager.get_recent_locations())
        bookmark_count = len(self.location_manager.get_bookmarks())
        
        return f"{hash(tuple(visible_columns))}_{recent_count}_{bookmark_count}"
```

#### 12.2 Efficient Service Calls
```python
class CachedLocationManager(LocationManager):
    """Location manager with caching for expensive operations."""
    
    def __init__(self):
        super().__init__()
        self._quick_locations_cache = None
        self._cache_expiry = {}
        
    def get_quick_locations(self) -> List[QuickLocation]:
        """Get quick locations with caching."""
        if (self._quick_locations_cache is None or 
            self._is_cache_expired('quick_locations')):
            
            self._quick_locations_cache = self._load_quick_locations()
            self._cache_expiry['quick_locations'] = time.time() + 300  # 5 min
            
        return self._quick_locations_cache
        
    def _is_cache_expired(self, cache_key: str) -> bool:
        """Check if cache entry has expired."""
        return (cache_key not in self._cache_expiry or 
                time.time() > self._cache_expiry[cache_key])
```

This technical design provides a comprehensive foundation for implementing the Explorer Header Context Menu with proper architecture, accessibility, testing, and performance considerations.
