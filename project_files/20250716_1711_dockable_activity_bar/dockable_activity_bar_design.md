# Dockable Activity Bar Design Document

**Date:** July 16, 2025  
**Component:** MainAppWindow Architecture  
**Scope:** Redesign MainAppWindow to support dockable activity bar that can be moved but never closed

## Overview

This document outlines the redesign of the MainAppWindow architecture to support a dockable activity bar that can be positioned on left, right, top, or bottom edges of the main window while maintaining the constraint that it cannot be closed or hidden completely.

## Current Architecture Analysis

### Current Layout Structure
```
MainAppWindow (QMainWindow)
├── MenuBar
├── CentralWidget
│   └── QHBoxLayout
│       └── QSplitter (Horizontal)
│           ├── SidebarManager
│           │   ├── SidebarActivityBar (50px fixed width)
│           │   └── QStackedWidget (panels)
│           └── TabManager
└── StatusBar
```

### Current Components
- **SidebarManager**: Contains both activity bar and panel container
- **SidebarActivityBar**: Simple activity bar (50px fixed width)
- **ActivityBar**: Full-featured widget with plugin support (48px fixed width)
- **TabManager**: Manages editor tabs

## Design Goals

1. **Dockable Activity Bar**: Activity bar can be docked to any edge (left, right, top, bottom)
2. **Never Closeable**: Activity bar cannot be hidden or closed completely
3. **Maintain Plugin API**: Existing plugin system should continue working
4. **Preserve Panel System**: Sidebar panels should remain functional
5. **Responsive Layout**: Layout should adapt to different activity bar positions
6. **User Preferences**: Remember user's preferred docking position

## New Architecture Design

### Architecture Terminology (Updated)
- **ActivityBar** (`widgets/activity_bar.py`): Full-featured dockable navigation bar with plugin API support
- **ActivityBarDockWidget** (`widgets/activity_bar_dock_widget.py`): QDockWidget wrapper for ActivityBar
- **SidebarManager** (`core/sidebar_manager.py`): Manages panel container only (no embedded activity bar)
- **MainAppWindow** (`core/main_app_window.py`): Uses QDockWidget system for activity bar management

### New Layout Structure
```
MainAppWindow (QMainWindow)
├── MenuBar
├── ActivityBarDockWidget (QDockWidget) [DOCKABLE, NON-CLOSABLE]
│   └── ActivityBar (widgets/activity_bar.py)
├── CentralWidget
│   └── QHBoxLayout
│       └── QSplitter (Horizontal/Vertical - adaptive)
│           ├── SidebarManager (panel container only)
│           └── TabManager
└── StatusBar
```

## Implementation Plan

### Phase 1: Create ActivityBarDockWidget

#### New File: `widgets/activity_bar_dock_widget.py`
```python
class ActivityBarDockWidget(QDockWidget):
    """
    Dockable widget wrapper for ActivityBar.
    Ensures the activity bar cannot be closed and provides
    position-aware layout management.
    """
    
    def __init__(self, activity_bar: ActivityBar):
        # Configure as non-closable dock widget
        # Handle orientation changes based on dock area
        # Emit signals for layout changes
```

**Features:**
- Wraps existing ActivityBar widget
- Handles orientation changes (vertical for left/right, horizontal for top/bottom)
- Prevents closing through feature flags and event handling
- Emits signals when docking position changes

### Phase 2: Modify MainAppWindow

#### Changes to `core/main_app_window.py`
1. **Remove activity bar from SidebarManager**
2. **Create ActivityBarDockWidget as separate dock widget**
3. **Implement adaptive splitter orientation**
4. **Add dock area change handling**

```python
def setup_main_layout(self) -> None:
    """Setup main window with dockable activity bar."""
    # Create activity bar as dockable widget
    self.activity_bar = ActivityBar(self.plugin_api)
    self.activity_bar_dock = ActivityBarDockWidget(self.activity_bar)
    
    # Configure dock widget properties
    self.activity_bar_dock.setFeatures(
        QDockWidget.DockWidgetFeature.DockWidgetMovable |
        QDockWidget.DockWidgetFeature.DockWidgetFloatable
    )
    
    # Add to left dock area by default
    self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.activity_bar_dock)
    
    # Create central widget with adaptive layout
    self.setup_central_widget()
```

### Phase 3: Update SidebarManager

#### Changes to `core/sidebar_manager.py`
1. **Remove SidebarActivityBar**
2. **Focus on panel container management**
3. **Receive activity signals from external ActivityBar**

```python
class SidebarManager(QWidget):
    """
    Manages only the panel container.
    Activity bar is now external and dockable.
    """
    
    def __init__(self):
        # Remove embedded activity bar
        # Keep panel container (QStackedWidget)
        # Connect to external activity bar signals
```

### Phase 4: Implement Adaptive Layout

#### Layout Adaptation Logic
- **Left/Right Docking**: Horizontal splitter (sidebar | tabs)
- **Top/Bottom Docking**: Vertical splitter (sidebar above/below tabs)
- **Floating**: Maintain current layout

#### Position Detection
```python
def on_dock_area_changed(self, area: Qt.DockWidgetArea):
    """Handle activity bar position changes."""
    if area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
        self.set_horizontal_layout()
    elif area in (Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea):
        self.set_vertical_layout()
```

### Phase 5: Settings and Persistence

#### Settings Management
- Save/restore activity bar dock position
- Save/restore activity bar size
- Maintain panel visibility state

```python
def save_settings(self):
    """Save window and dock widget state."""
    self.settings.setValue("geometry", self.saveGeometry())
    self.settings.setValue("windowState", self.saveState())
    self.settings.setValue("activityBarArea", self.dockWidgetArea(self.activity_bar_dock))

def restore_settings(self):
    """Restore window and dock widget state."""
    if self.settings.contains("geometry"):
        self.restoreGeometry(self.settings.value("geometry"))
    if self.settings.contains("windowState"):
        self.restoreState(self.settings.value("windowState"))
```

## Component Reuse Analysis

### ✅ **Components That Can Be Reused (95% reuse!)**

#### 1. **ActivityBar Widget** (`widgets/activity_bar.py`)
- **Reuse 100%**: Already perfect for docking with plugin API support
- **Minor Addition**: Add orientation methods for horizontal/vertical layout
- **Current Features Preserved**: 
  - Activity registration (`add_activity_button()`)
  - Plugin API integration
  - Signal emission (`panel_requested`)
  - Badge support and state management

#### 2. **All Panel Classes** (`panels/*.py`)
- **Reuse 100%**: No changes needed
- **Components**: ExplorerPanel, SearchPanel, PreferencesPanel, ExtensionsPanel, AccountPanel

#### 3. **ActivityManager** (`managers/activity_manager.py`) 
- **Reuse 100%**: Activity registration and coordination logic unchanged
- **Plugin API**: `api.register_activity()` continues working identically

#### 4. **Icon System** (`services/icon_manager.py`)
- **Reuse 100%**: SVG icon management and activity button icons work as-is

#### 5. **TabManager** (`core/tab_manager.py`)
- **Reuse 100%**: Editor tabs completely unaffected

### 🔧 **Components Needing Minor Adjustments**

#### 1. **SidebarManager** (`core/sidebar_manager.py`)
- **Remove**: `SidebarActivityBar` class (lines 25-180, ~150 lines removed)
- **Keep**: Panel container and management (80% of existing code)
- **Add**: `connect_to_activity_bar()` method (~10 lines)

#### 2. **MainAppWindow** (`core/main_app_window.py`)
- **Modify**: `setup_main_layout()` method to use QDockWidget
- **Add**: Dock area change handling (~30 lines)
- **Keep**: All other functionality (menus, settings, plugin loading)

### 🆕 **New Components (Minimal New Code)**

#### 1. **ActivityBarDockWidget** (`widgets/activity_bar_dock_widget.py`)
- **Size**: ~100 lines total
- **Purpose**: Thin wrapper around existing ActivityBar
- **Function**: Docking behavior, close prevention, orientation management

## API Compatibility

### Plugin API Preservation
**100% Backward Compatible** - No plugin changes required:
- `api.register_activity()` continues to work identically
- Activity button creation remains unchanged  
- Panel registration stays the same
- All existing plugins work without modification

### Migration Path
1. **ActivityBar widget**: Add 2 orientation methods (~20 lines)
2. **SidebarManager**: Remove embedded activity bar, keep panel management
3. **MainAppWindow**: Replace embedded layout with QDockWidget system
4. **New wrapper**: Create ActivityBarDockWidget (minimal new code)

## User Experience

### Visual Changes
- Activity bar can be dragged to any edge
- Visual feedback during docking operations
- Activity bar maintains its appearance regardless of position

### Interaction Changes
- Right-click context menu on activity bar for quick positioning
- Keyboard shortcuts for moving activity bar
- Double-click title area to reset to default position

### Menu Integration
Add View menu options:
- "Move Activity Bar to Left"
- "Move Activity Bar to Right" 
- "Move Activity Bar to Top"
- "Move Activity Bar to Bottom"

## Technical Considerations

### Performance
- Minimal performance impact (QDockWidget is optimized)
- Layout changes are handled efficiently by Qt
- No impact on plugin loading or execution

### Testing Strategy
- Unit tests for ActivityBarDockWidget
- Integration tests for layout changes
- User interaction tests for docking operations
- Settings persistence tests

### Error Handling
- Graceful fallback to left docking if invalid position saved
- Handle edge cases with very small window sizes
- Prevent activity bar from being hidden accidentally

## Implementation Files

### New Files
- `widgets/activity_bar_dock_widget.py`: Dockable wrapper for activity bar
- `tests/widgets/test_cases/test_activity_bar_dock.py`: Test file for dock widget

### Modified Files
- `core/main_app_window.py`: Use QDockWidget system
- `core/sidebar_manager.py`: Remove embedded activity bar
- `demos/activity_bar/sidebar_integration_helper.py`: Update integration example

### Documentation Updates
- Update architecture documentation
- Add user guide for activity bar positioning
- Update plugin development guide

## Migration Timeline

1. **Day 1**: Implement ActivityBarDockWidget
2. **Day 2**: Modify MainAppWindow to use dock system
3. **Day 3**: Update SidebarManager and remove embedded activity bar
4. **Day 4**: Implement adaptive layout logic
5. **Day 5**: Add settings persistence and menu integration
6. **Day 6**: Testing and bug fixes
7. **Day 7**: Documentation updates

## Conclusion

This design provides a flexible, user-friendly dockable activity bar while maintaining the existing plugin architecture and ensuring the activity bar cannot be accidentally hidden. The implementation leverages Qt's proven QDockWidget system for robust docking functionality while preserving all current features and plugin compatibility.
