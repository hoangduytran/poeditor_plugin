# Dockable Activity Bar Implementation Plan

**Date:** July 16, 2025  
**Component:** MainAppWindow Architecture Implementation  
**Related:** dockable_activity_bar_design.md

## Implementation Overview

This document provides the detailed implementation plan for converting the MainAppWindow to use a dockable activity bar system. The implementation will be done in phases to ensure stability and allow for rollback if needed.

## Git Branching Strategy

### Main Branch Structure
```
main
├── feature/dockable-activity-bar (working branch)
│   ├── phase1-dock-widget
│   ├── phase2-main-window  
│   ├── phase3-sidebar-manager
│   ├── phase4-adaptive-layout
│   └── phase5-settings-persistence
```

### Branch Management
1. Create feature branch from main
2. Create phase branches from feature branch
3. Merge phase branches back to feature branch after completion
4. Merge feature branch to main after all phases complete

## Component Reuse Strategy

This implementation **reuses 95% of existing components** rather than creating new ones from scratch:

### ✅ **Zero Changes Required**
- **ActivityBar** (`widgets/activity_bar.py`): Already perfect for docking
- **All Panels** (`panels/*.py`): Work as-is 
- **ActivityManager** (`managers/activity_manager.py`): Plugin registration unchanged
- **Plugin API** (`core/api.py`): 100% backward compatible
- **Icon System** (`services/icon_manager.py`): SVG icons work as-is
- **TabManager** (`core/tab_manager.py`): Editor tabs unaffected

### 🔧 **Minor Adjustments** 
- **SidebarManager**: Remove ~150 lines (SidebarActivityBar), keep panel management
- **MainAppWindow**: Modify layout method, add dock handling (~50 lines changed)

### 🆕 **Minimal New Code**
- **ActivityBarDockWidget**: ~100 lines (thin wrapper around existing ActivityBar)

**Total New Code**: ~150 lines  
**Total Reused Code**: ~3000+ lines  
**Reuse Ratio**: 95%+

## Phase 1: Create ActivityBarDockWidget

### Files to Create
- `widgets/activity_bar_dock_widget.py`
- `tests/widgets/test_cases/test_activity_bar_dock.py`

### Implementation Steps

#### Step 1.1: Create ActivityBarDockWidget Class
```python
from PySide6.QtWidgets import QDockWidget, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from lg import logger
from widgets.activity_bar import ActivityBar

class ActivityBarDockWidget(QDockWidget):
    """Dockable wrapper for ActivityBar that cannot be closed."""
    
    position_changed = Signal(Qt.DockWidgetArea)
    
    def __init__(self, activity_bar: ActivityBar, parent: QWidget = None):
        super().__init__("Activity Bar", parent)
        
        # Store references
        self.activity_bar = activity_bar
        
        # Configure dock widget
        self.setup_dock_widget()
        
        # Set the activity bar as widget
        self.setWidget(self.activity_bar)
    
    def setup_dock_widget(self):
        """Configure dock widget properties."""
        # Allow moving and floating, but not closing
        features = (
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.setFeatures(features)
        
        # Set size constraints
        self.setMinimumSize(48, 100)
        
        # Connect signals
        self.dockLocationChanged.connect(self.on_dock_location_changed)
        
    def closeEvent(self, event: QCloseEvent):
        """Prevent closing the dock widget."""
        event.ignore()  # Always ignore close events
        
    def on_dock_location_changed(self, area: Qt.DockWidgetArea):
        """Handle dock location changes."""
        logger.info(f"Activity bar moved to area: {area}")
        self.position_changed.emit(area)
        
        # Update activity bar orientation if needed
        self.update_activity_bar_orientation(area)
        
    def update_activity_bar_orientation(self, area: Qt.DockWidgetArea):
        """Update activity bar layout based on dock area."""
        if area in (Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea):
            # Horizontal orientation for top/bottom
            self.activity_bar.set_horizontal_orientation()
        else:
            # Vertical orientation for left/right
            self.activity_bar.set_vertical_orientation()
```

#### Step 1.2: Update ActivityBar for Orientation Support
Add orientation methods to `widgets/activity_bar.py`:
```python
def set_horizontal_orientation(self):
    """Configure for horizontal layout (top/bottom docking)."""
    self.setFixedHeight(48)
    self.setMinimumWidth(100)
    self.setMaximumWidth(16777215)  # Remove width constraint
    # Update button layout to horizontal
    
def set_vertical_orientation(self):
    """Configure for vertical layout (left/right docking)."""
    self.setFixedWidth(48)
    self.setMinimumHeight(100)
    self.setMaximumHeight(16777215)  # Remove height constraint
    # Update button layout to vertical
```

#### Step 1.3: Create Tests
```python
# tests/widgets/test_cases/test_activity_bar_dock.py
import pytest
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from widgets.activity_bar_dock_widget import ActivityBarDockWidget
from widgets.activity_bar import ActivityBar

def test_activity_bar_dock_widget_creation():
    """Test creating ActivityBarDockWidget."""
    app = QApplication.instance() or QApplication([])
    
    # Create mock activity bar
    activity_bar = ActivityBar(None)  # Mock API for testing
    
    # Create dock widget
    dock_widget = ActivityBarDockWidget(activity_bar)
    
    # Verify properties
    assert dock_widget.widget() == activity_bar
    assert not (dock_widget.features() & QDockWidget.DockWidgetFeature.DockWidgetClosable)
    assert dock_widget.features() & QDockWidget.DockWidgetFeature.DockWidgetMovable

def test_close_event_ignored():
    """Test that close events are ignored."""
    app = QApplication.instance() or QApplication([])
    
    activity_bar = ActivityBar(None)
    dock_widget = ActivityBarDockWidget(activity_bar)
    
    # Create main window and add dock widget
    main_window = QMainWindow()
    main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)
    
    # Try to close - should be ignored
    dock_widget.close()
    
    # Verify dock widget is still visible
    assert dock_widget.isVisible()
```

### Commit Strategy for Phase 1
```bash
git checkout -b feature/dockable-activity-bar
git checkout -b phase1-dock-widget

# After implementation
git add widgets/activity_bar_dock_widget.py
git commit -m "feat: Add ActivityBarDockWidget class

- Create dockable wrapper for ActivityBar
- Prevent closing through event handling
- Add orientation change support
- Emit position change signals"

git add tests/widgets/test_cases/test_activity_bar_dock.py
git commit -m "test: Add tests for ActivityBarDockWidget

- Test dock widget creation
- Test close event prevention
- Test orientation changes"

git checkout feature/dockable-activity-bar
git merge phase1-dock-widget
```

## Phase 2: Modify MainAppWindow

### Files to Modify
- `core/main_app_window.py`

### Implementation Steps

#### Step 2.1: Update MainAppWindow Layout Method
Replace `setup_main_layout()` method:
```python
def setup_main_layout(self) -> None:
    """Setup main window with dockable activity bar."""
    try:
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create activity bar and dock widget
        self.setup_activity_bar_dock()
        
        # Create main content layout
        self.setup_central_widget_layout(central_widget)
        
        # Initialize activity manager
        self.setup_activity_manager()
        
        # Connect signals
        self.connect_signals()
        
    except Exception as e:
        logger.error(f"Failed to setup main layout: {e}")
        raise

def setup_activity_bar_dock(self) -> None:
    """Setup the dockable activity bar."""
    try:
        # Create activity bar
        self.activity_bar = ActivityBar(self.plugin_api)
        
        # Create dock widget wrapper
        self.activity_bar_dock = ActivityBarDockWidget(self.activity_bar)
        
        # Add to left dock area by default
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.activity_bar_dock)
        
        # Connect signals
        self.activity_bar_dock.position_changed.connect(self.on_activity_bar_position_changed)
        
        logger.info("Activity bar dock widget created and positioned")
        
    except Exception as e:
        logger.error(f"Failed to setup activity bar dock: {e}")
        raise

def setup_central_widget_layout(self, central_widget: QWidget) -> None:
    """Setup the central widget layout."""
    try:
        # Create main layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter (will be adaptive)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # Create sidebar manager (no embedded activity bar)
        self.sidebar_manager = SidebarManager()
        self.main_splitter.addWidget(self.sidebar_manager)
        
        # Create tab manager
        self.tab_manager = TabManager()
        self.main_splitter.addWidget(self.tab_manager)
        
        # Set splitter properties
        self.update_splitter_layout(Qt.DockWidgetArea.LeftDockWidgetArea)
        
    except Exception as e:
        logger.error(f"Failed to setup central widget layout: {e}")
        raise
```

#### Step 2.2: Add Activity Bar Position Handling
```python
def on_activity_bar_position_changed(self, area: Qt.DockWidgetArea) -> None:
    """Handle activity bar position changes."""
    try:
        logger.info(f"Activity bar position changed to: {area}")
        
        # Update splitter layout based on position
        self.update_splitter_layout(area)
        
        # Update sidebar manager position if needed
        self.sidebar_manager.update_layout_for_activity_bar_position(area)
        
    except Exception as e:
        logger.error(f"Failed to handle activity bar position change: {e}")

def update_splitter_layout(self, activity_bar_area: Qt.DockWidgetArea) -> None:
    """Update splitter orientation based on activity bar position."""
    try:
        if activity_bar_area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
            # Horizontal layout for left/right activity bar
            if self.main_splitter.orientation() != Qt.Orientation.Horizontal:
                self.main_splitter.setOrientation(Qt.Orientation.Horizontal)
            self.main_splitter.setSizes([300, 900])
        else:
            # Vertical layout for top/bottom activity bar
            if self.main_splitter.orientation() != Qt.Orientation.Vertical:
                self.main_splitter.setOrientation(Qt.Orientation.Vertical)
            self.main_splitter.setSizes([200, 600])
            
    except Exception as e:
        logger.error(f"Failed to update splitter layout: {e}")
```

#### Step 2.3: Update Menu Bar
Add activity bar positioning menu:
```python
def setup_menu_bar(self) -> None:
    """Setup the application menu bar."""
    try:
        menu_bar = self.menuBar()
        
        # ... existing File menu code ...
        
        # View menu (update existing)
        view_menu = menu_bar.addMenu('&View')
        
        toggle_sidebar_action = QAction('Toggle &Sidebar', self)
        toggle_sidebar_action.setShortcut(QKeySequence('Ctrl+B'))
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)
        
        view_menu.addSeparator()
        
        # Activity bar position submenu
        activity_bar_menu = view_menu.addMenu('Activity Bar Position')
        
        left_action = QAction('Move to &Left', self)
        left_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.LeftDockWidgetArea))
        activity_bar_menu.addAction(left_action)
        
        right_action = QAction('Move to &Right', self)
        right_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.RightDockWidgetArea))
        activity_bar_menu.addAction(right_action)
        
        top_action = QAction('Move to &Top', self)
        top_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.TopDockWidgetArea))
        activity_bar_menu.addAction(top_action)
        
        bottom_action = QAction('Move to &Bottom', self)
        bottom_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.BottomDockWidgetArea))
        activity_bar_menu.addAction(bottom_action)
        
        # ... existing Help menu code ...
        
    except Exception as e:
        logger.error(f"Failed to setup menu bar: {e}")

def move_activity_bar_to(self, area: Qt.DockWidgetArea) -> None:
    """Move activity bar to specified dock area."""
    try:
        if self.activity_bar_dock:
            self.addDockWidget(area, self.activity_bar_dock)
            logger.info(f"Moved activity bar to: {area}")
    except Exception as e:
        logger.error(f"Failed to move activity bar: {e}")
```

### Commit Strategy for Phase 2
```bash
git checkout -b phase2-main-window

# After implementation
git add core/main_app_window.py
git commit -m "feat: Convert MainAppWindow to use dockable activity bar

- Replace embedded activity bar with ActivityBarDockWidget
- Add adaptive splitter layout based on activity bar position
- Add menu options for activity bar positioning
- Implement position change handling"

git checkout feature/dockable-activity-bar
git merge phase2-main-window
```

## Phase 3: Update SidebarManager

### Files to Modify
- `core/sidebar_manager.py`

### Implementation Steps

#### Step 3.1: Remove SidebarActivityBar
Remove the embedded `SidebarActivityBar` and focus on panel management:
```python
class SidebarManager(QWidget):
    """
    Manages the sidebar panel container.
    Activity bar is now external and dockable.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Initialize attributes
        self.panels: Dict[str, QWidget] = {}
        self.panel_container: Optional[QStackedWidget] = None
        self.current_panel_id: Optional[str] = None
        
        # Setup UI without activity bar
        self.setup_ui()
        
        logger.info("SidebarManager initialized (panel container only)")
    
    def setup_ui(self) -> None:
        """Setup the sidebar UI without embedded activity bar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create panel container
        self.panel_container = QStackedWidget()
        layout.addWidget(self.panel_container)
        
        # Set minimum size
        self.setMinimumWidth(200)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, 
            QSizePolicy.Policy.Expanding
        )
```

#### Step 3.2: Update Panel Management
Modify methods to work without embedded activity bar:
```python
def add_panel(self, panel_id: str, panel: QWidget, icon: QIcon, tooltip: str) -> None:
    """Add a panel to the sidebar."""
    try:
        if panel_id in self.panels:
            logger.warning(f"Panel already exists: {panel_id}")
            return
        
        # Store panel
        self.panels[panel_id] = panel
        
        # Add to container
        self.panel_container.addWidget(panel)
        
        logger.info(f"Added panel: {panel_id}")
        
    except Exception as e:
        logger.error(f"Failed to add panel {panel_id}: {e}")
        raise

def show_panel(self, panel_id: str) -> None:
    """Show the specified panel."""
    try:
        if panel_id not in self.panels:
            logger.error(f"Panel not found: {panel_id}")
            return
        
        panel = self.panels[panel_id]
        self.panel_container.setCurrentWidget(panel)
        self.current_panel_id = panel_id
        
        # Show the sidebar if hidden
        self.show()
        
        logger.info(f"Showing panel: {panel_id}")
        
    except Exception as e:
        logger.error(f"Failed to show panel {panel_id}: {e}")

def update_layout_for_activity_bar_position(self, area: Qt.DockWidgetArea) -> None:
    """Update layout based on activity bar position."""
    try:
        # This method can be used for future enhancements
        # Currently no specific layout changes needed
        logger.debug(f"SidebarManager layout updated for activity bar area: {area}")
        
    except Exception as e:
        logger.error(f"Failed to update layout for activity bar position: {e}")
```

#### Step 3.3: Connect to External Activity Bar
Add method to connect to external activity bar signals:
```python
def connect_to_activity_bar(self, activity_bar) -> None:
    """Connect to external activity bar signals."""
    try:
        # Connect panel request signal
        activity_bar.panel_requested.connect(self.show_panel)
        
        logger.info("Connected to external activity bar")
        
    except Exception as e:
        logger.error(f"Failed to connect to activity bar: {e}")
```

### Commit Strategy for Phase 3
```bash
git checkout -b phase3-sidebar-manager

# After implementation
git add core/sidebar_manager.py
git commit -m "refactor: Remove embedded activity bar from SidebarManager

- Remove SidebarActivityBar class and references
- Focus SidebarManager on panel container management
- Add method to connect to external activity bar
- Simplify layout to panel container only"

git checkout feature/dockable-activity-bar
git merge phase3-sidebar-manager
```

## Phase 4: Implement Settings Persistence

### Files to Modify
- `core/main_app_window.py`

### Implementation Steps

#### Step 4.1: Update Settings Methods
```python
def save_settings(self) -> None:
    """Save application settings including dock widget state."""
    try:
        # Save window geometry and state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Save activity bar specific settings
        if self.activity_bar_dock:
            area = self.dockWidgetArea(self.activity_bar_dock)
            self.settings.setValue("activityBarArea", int(area))
            self.settings.setValue("activityBarSize", self.activity_bar_dock.size())
        
        # Save splitter state
        if self.main_splitter:
            self.settings.setValue("splitterSizes", self.main_splitter.sizes())
        
        logger.info("Settings saved")
        
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")

def restore_settings(self) -> None:
    """Restore application settings including dock widget state."""
    try:
        # Restore window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        # Restore window state (including dock widgets)
        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))
        
        # Restore activity bar position if saved
        if self.settings.contains("activityBarArea") and self.activity_bar_dock:
            area = Qt.DockWidgetArea(int(self.settings.value("activityBarArea")))
            self.addDockWidget(area, self.activity_bar_dock)
        
        # Restore splitter sizes
        if self.settings.contains("splitterSizes") and self.main_splitter:
            sizes = self.settings.value("splitterSizes")
            if sizes:
                self.main_splitter.setSizes(sizes)
        
        logger.info("Settings restored")
        
    except Exception as e:
        logger.error(f"Failed to restore settings: {e}")
```

#### Step 4.2: Update Close Event
```python
def closeEvent(self, event) -> None:
    """Handle application close event."""
    try:
        # Save settings before closing
        self.save_settings()
        
        # Accept the close event
        event.accept()
        
        logger.info("Application closing")
        
    except Exception as e:
        logger.error(f"Error during application close: {e}")
        event.accept()  # Still close even if save fails
```

### Commit Strategy for Phase 4
```bash
git checkout -b phase4-settings-persistence

# After implementation
git add core/main_app_window.py
git commit -m "feat: Add settings persistence for dockable activity bar

- Save/restore dock widget state and position
- Persist activity bar area and size
- Save splitter sizes
- Handle settings in close event"

git checkout feature/dockable-activity-bar
git merge phase4-settings-persistence
```

## Phase 5: Update Integration Helper

### Files to Modify
- `demos/activity_bar/sidebar_integration_helper.py`

### Implementation Steps

#### Step 5.1: Update Integration Function
```python
def add_sidebar_buttons_to_main_app(main_window):
    """
    Add sidebar buttons to the main application window.
    Updated for dockable activity bar architecture.
    
    Args:
        main_window: Instance of MainAppWindow
    """
    try:
        # Import the actual panel classes
        from panels.explorer_panel import ExplorerPanel
        from panels.search_panel import SearchPanel
        from panels.preferences_panel import PreferencesPanel
        from panels.extensions_panel import ExtensionsPanel
        from panels.account_panel import AccountPanel
        
        # Create panel instances
        explorer_panel = ExplorerPanel()
        search_panel = SearchPanel()
        preferences_panel = PreferencesPanel()
        extensions_panel = ExtensionsPanel()
        account_panel = AccountPanel()
        
        # Get activity bar from dock widget
        activity_bar = main_window.activity_bar
        sidebar_manager = main_window.sidebar_manager
        
        # Connect sidebar manager to activity bar
        sidebar_manager.connect_to_activity_bar(activity_bar)
        
        # Create icons using the icon manager
        from services.icon_manager import IconManager
        icon_manager = IconManager()
        
        explorer_icon = icon_manager.get_activity_button_icon("explorer", active=False, size=32)
        search_icon = icon_manager.get_activity_button_icon("search", active=False, size=32)
        preferences_icon = icon_manager.get_activity_button_icon("preferences", active=False, size=32)
        extensions_icon = icon_manager.get_activity_button_icon("extensions", active=False, size=32)
        account_icon = icon_manager.get_activity_button_icon("account", active=False, size=32)
        
        # Add panels to sidebar
        sidebar_manager.add_panel("explorer", explorer_panel, explorer_icon, "Explorer")
        sidebar_manager.add_panel("search", search_panel, search_icon, "Search")
        sidebar_manager.add_panel("preferences", preferences_panel, preferences_icon, "Preferences")
        sidebar_manager.add_panel("extensions", extensions_panel, extensions_icon, "Extensions")
        sidebar_manager.add_panel("account", account_panel, account_icon, "Account")
        
        # Add activities to activity bar
        activity_bar.add_activity("explorer", explorer_icon, "Explorer")
        activity_bar.add_activity("search", search_icon, "Search")
        activity_bar.add_activity("preferences", preferences_icon, "Preferences")
        activity_bar.add_activity("extensions", extensions_icon, "Extensions")
        activity_bar.add_activity("account", account_icon, "Account")
        
        # Show the explorer panel by default
        sidebar_manager.show_panel("explorer")
        activity_bar.set_active_activity("explorer")
        
        logger.info("Successfully added all sidebar buttons to main application with dockable activity bar")
        
    except Exception as e:
        logger.error(f"Failed to add sidebar buttons: {e}")
        raise
```

### Commit Strategy for Phase 5
```bash
git checkout -b phase5-integration-update

# After implementation
git add demos/activity_bar/sidebar_integration_helper.py
git commit -m "feat: Update integration helper for dockable activity bar

- Update to work with new dockable architecture
- Connect sidebar manager to external activity bar
- Add activities to ActivityBar widget
- Maintain backward compatibility"

git checkout feature/dockable-activity-bar
git merge phase5-integration-update
```

## Final Integration and Testing

### Integration Steps
1. **Run Tests**: Execute all existing tests to ensure no regression
2. **Manual Testing**: Test all docking positions and functionality
3. **Performance Testing**: Verify no performance degradation
4. **Documentation Update**: Update all relevant documentation

### Final Commit and Merge
```bash
# Final integration commit
git add .
git commit -m "feat: Complete dockable activity bar implementation

- All phases integrated and tested
- Backward compatibility maintained
- Settings persistence working
- Documentation updated"

# Merge to main
git checkout main
git merge feature/dockable-activity-bar

# Tag the release
git tag -a v1.1.0-dockable-activity-bar -m "Add dockable activity bar support"
```

## Rollback Plan

### If Issues Arise
1. **Phase-level rollback**: Revert specific phase branch
2. **Feature-level rollback**: Revert entire feature branch
3. **Emergency rollback**: Revert to last known good commit on main

### Rollback Commands
```bash
# Revert specific phase
git revert <phase-commit-hash>

# Revert entire feature
git checkout main
git revert <merge-commit-hash>

# Emergency reset
git reset --hard <last-good-commit>
```

## Success Criteria

### Functional Requirements
- ✅ Activity bar can be docked to all four edges
- ✅ Activity bar cannot be closed or hidden
- ✅ All existing plugins continue to work
- ✅ Panel system functions correctly
- ✅ Settings are persisted across sessions

### Non-Functional Requirements
- ✅ Performance is not degraded
- ✅ Memory usage remains stable
- ✅ UI remains responsive during docking operations
- ✅ All tests pass
- ✅ Code quality maintained (no linting errors)

This implementation plan provides a comprehensive roadmap for converting the MainAppWindow to support a dockable activity bar while maintaining all existing functionality and ensuring proper testing and rollback capabilities.
