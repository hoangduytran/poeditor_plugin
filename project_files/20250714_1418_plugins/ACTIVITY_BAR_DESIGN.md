# Activity Bar Design

## Overview
The Activity Bar is a vertical sidebar component that provides quick access to the main features of the POEditor application. It follows VS Code's design patterns with icon-based buttons for core functionality including Explorer, Search, Preferences, and Extensions (Plugins).

## Visual Architecture

### Activity Bar Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│                       POEditor Main Window                              │
├───┬─────────────────────────────────────────────────────────────────────┤
│   │                      Main Content Area                              │
│ A │ ┌─────────────────────────┬─────────────────────────────────────────┐ │
│ c │ │                         │                                         │ │
│ t │ │      Sidebar Panel      │           Tab Area                      │ │
│ i │ │                         │                                         │ │
│ v │ │ ┌─────────────────────┐ │ ┌─────────────────────────────────────┐ │ │
│ i │ │ │                     │ │ │                                     │ │ │
│ t │ │ │   Plugin Content    │ │ │        Editor Tabs                  │ │ │
│ y │ │ │                     │ │ │                                     │ │ │
│   │ │ │   (Explorer,        │ │ │                                     │ │ │
│ B │ │ │    Search,          │ │ │                                     │ │ │
│ a │ │ │    Preferences,     │ │ │                                     │ │ │
│ r │ │ │    Extensions)      │ │ │                                     │ │ │
│   │ │ │                     │ │ │                                     │ │ │
│   │ │ └─────────────────────┘ │ └─────────────────────────────────────┘ │ │
│   │ └─────────────────────────┴─────────────────────────────────────────┘ │
│   │                                                                     │ │
├───┴─────────────────────────────────────────────────────────────────────┤
│                            Status Bar                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Activity Bar Detailed View
```
┌─────┐
│  📁  │ ← Explorer (File tree, workspace navigation)
│     │
├─────┤
│  🔍  │ ← Search (Global search and replace)
│     │
├─────┤
│  ⚙️  │ ← Preferences (Settings and configuration)
│     │
├─────┤
│  🧩  │ ← Extensions (Plugin management)
│     │
├─────┤
│     │
│     │ ← Spacer area
│     │
├─────┤
│  👤  │ ← Account/User (bottom area)
│     │
└─────┘
```

## Component Architecture

### 1. ActivityBar (widgets/activity_bar.py)
**Purpose:** Main vertical sidebar container with navigation buttons

**Key Features:**
- Icon-based navigation buttons
- Active state indication
- Tooltip support
- Keyboard navigation
- Dark theme styling

**Interface:**
```python
from lg import logger
from typing import Dict, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

class ActivityBar(QWidget):
    panel_requested = Signal(str)  # panel_id
    
    def __init__(self, api: PluginAPI):
        super().__init__()
        self.api = api
        self.layout = QVBoxLayout()
        self.buttons: Dict[str, ActivityButton] = {}
        self.active_activity_id: Optional[str] = None
        logger.info("ActivityBar initialized")
        
    def add_activity_button(self, activity: ActivityButton) -> None:
        """Add activity button ensuring proper object attribute access"""
        if not activity.activity_id:
            logger.error("ActivityButton missing activity_id attribute")
            return
        self.buttons[activity.activity_id] = activity
        self.layout.addWidget(activity)
        logger.info(f"Added activity button: {activity.activity_id}")
        
    def set_active_activity(self, activity_id: str) -> None:
        """Set active activity with direct attribute access"""
        if activity_id not in self.buttons:
            logger.error(f"Activity {activity_id} not found in buttons")
            return
        
        # Deactivate current active button
        if self.active_activity_id and self.active_activity_id in self.buttons:
            self.buttons[self.active_activity_id].is_active = False
            
        # Activate new button
        self.buttons[activity_id].is_active = True
        self.active_activity_id = activity_id
        logger.info(f"Set active activity: {activity_id}")
        
    def get_active_activity(self) -> str:
        return self.active_activity_id or ""
        
    def remove_activity_button(self, activity_id: str) -> None:
        """Remove activity button with proper cleanup"""
        if activity_id not in self.buttons:
            logger.warning(f"Activity {activity_id} not found for removal")
            return
            
        button = self.buttons[activity_id]
        self.layout.removeWidget(button)
        button.deleteLater()
        del self.buttons[activity_id]
        
        if self.active_activity_id == activity_id:
            self.active_activity_id = None
        logger.info(f"Removed activity button: {activity_id}")
```

### 2. ActivityButton (widgets/activity_button.py)
**Purpose:** Individual clickable button in the activity bar

**Key Features:**
- Icon display with emoji or SVG support
- Active/inactive states
- Badge support for notifications
- Hover effects
- Accessibility support

**Interface:**
```python
from lg import logger
from typing import Optional
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal

class ActivityButton(QPushButton):
    clicked_with_id = Signal(str)
    
    def __init__(self, activity_id: str, icon: str, tooltip: str):
        super().__init__()
        self.activity_id = activity_id
        self.icon_text = icon
        self.tooltip_text = tooltip
        self.is_active = False
        self.badge_count = 0
        
        self.setText(icon)
        self.setToolTip(tooltip)
        logger.info(f"ActivityButton created: {activity_id}")
        
    def set_active(self, active: bool) -> None:
        """Set active state with direct attribute access"""
        self.is_active = active
        if active:
            self.setProperty("class", "active")
        else:
            self.setProperty("class", "")
        self.style().unpolish(self)
        self.style().polish(self)
        logger.debug(f"Activity {self.activity_id} active state: {active}")
        
    def set_badge(self, count: int) -> None:
        """Set badge count ensuring proper attribute assignment"""
        self.badge_count = max(0, count)
        self.update()  # Trigger repaint
        logger.debug(f"Activity {self.activity_id} badge count: {count}")
        
    def clear_badge(self) -> None:
        """Clear badge with direct attribute access"""
        self.badge_count = 0
        self.update()
        logger.debug(f"Activity {self.activity_id} badge cleared")
        
    def get_activity_id(self) -> str:
        """Get activity ID with direct attribute access"""
        return self.activity_id
```

### 3. ActivityManager (managers/activity_manager.py)
**Purpose:** Manages activity registration and coordination

**Key Features:**
- Activity registration from plugins
- Panel visibility management
- State persistence
- Event coordination

**Interface:**
```python
from lg import logger
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal

class ActivityManager(QObject):
    activity_changed = Signal(str, str)  # old_id, new_id
    
    def __init__(self, api: PluginAPI):
        super().__init__()
        self.api = api
        self.activities: Dict[str, ActivityConfig] = {}
        self.panels: Dict[str, QWidget] = {}
        self.current_activity_id: Optional[str] = None
        logger.info("ActivityManager initialized")
        
    def register_activity(self, activity: ActivityConfig) -> None:
        """Register activity with direct attribute access"""
        if not activity.id:
            logger.error("ActivityConfig missing id attribute")
            return
            
        self.activities[activity.id] = activity
        logger.info(f"Registered activity: {activity.id}")
        
    def unregister_activity(self, activity_id: str) -> None:
        """Unregister activity ensuring proper cleanup"""
        if activity_id not in self.activities:
            logger.warning(f"Activity {activity_id} not found for unregistration")
            return
            
        # Clean up panel if exists
        if activity_id in self.panels:
            panel = self.panels[activity_id]
            panel.deleteLater()
            del self.panels[activity_id]
            
        del self.activities[activity_id]
        logger.info(f"Unregistered activity: {activity_id}")
        
    def activate_panel(self, activity_id: str) -> None:
        """Activate panel with direct attribute access"""
        if activity_id not in self.activities:
            logger.error(f"Cannot activate unknown activity: {activity_id}")
            return
            
        old_activity = self.current_activity_id
        self.current_activity_id = activity_id
        
        # Get or create panel
        if activity_id not in self.panels:
            activity_config = self.activities[activity_id]
            # Direct attribute access instead of getattr
            panel_class_name = activity_config.panel_class
            logger.info(f"Creating panel for activity: {activity_id}")
            
        self.activity_changed.emit(old_activity or "", activity_id)
        logger.info(f"Activated activity: {activity_id}")
        
    def get_current_activity(self) -> str:
        """Get current activity with direct attribute access"""
        return self.current_activity_id or ""
```

## Activity Definitions

### Core Activities

#### 1. Explorer Activity
```python
EXPLORER_ACTIVITY = ActivityConfig(
    id="explorer",
    icon="📁",
    tooltip="Explorer",
    panel_class="ExplorerPanel",
    keyboard_shortcut="Ctrl+Shift+E",
    position=0
)
```

**Features:**
- File tree navigation
- Workspace management
- PO file status indicators
- File operations (create, delete, rename)

#### 2. Search Activity
```python
SEARCH_ACTIVITY = ActivityConfig(
    id="search",
    icon="🔍",
    tooltip="Search",
    panel_class="SearchPanel",
    keyboard_shortcut="Ctrl+Shift+F",
    position=1
)
```

**Features:**
- Global workspace search
- Find and replace operations
- PO-specific search capabilities
- Search history management

#### 3. Preferences Activity
```python
PREFERENCES_ACTIVITY = ActivityConfig(
    id="preferences",
    icon="⚙️",
    tooltip="Preferences",
    panel_class="PreferencesPanel",
    keyboard_shortcut="Ctrl+,",
    position=2
)
```

**Features:**
- Application settings
- Plugin configuration
- Theme and appearance
- Keyboard shortcuts
- User preferences

#### 4. Extensions Activity
```python
EXTENSIONS_ACTIVITY = ActivityConfig(
    id="extensions",
    icon="🧩",
    tooltip="Extensions",
    panel_class="ExtensionsPanel",
    keyboard_shortcut="Ctrl+Shift+X",
    position=3
)
```

**Features:**
- Plugin marketplace
- Installed plugin management
- Plugin enable/disable
- Plugin settings access

### Additional Activities (Future)

#### 5. Account Activity
```python
ACCOUNT_ACTIVITY = ActivityConfig(
    id="account",
    icon="👤",
    tooltip="Account",
    panel_class="AccountPanel",
    keyboard_shortcut=None,
    position=100,  # Bottom area
    area="bottom"
)
```

**Features:**
- User profile management
- Cloud sync settings
- Translation service accounts
- Collaboration features

## Data Models

### ActivityConfig
```python
@dataclass
class ActivityConfig:
    id: str
    icon: str  # Emoji or icon path
    tooltip: str
    panel_class: str
    keyboard_shortcut: str = None
    position: int = 0
    area: str = "main"  # "main" or "bottom"
    badge_count: int = 0
    enabled: bool = True
```

### ActivityState
```python
@dataclass
class ActivityState:
    active_activity: str = "explorer"
    panel_width: int = 300
    panel_visible: bool = True
    activity_positions: Dict[str, int] = None
```

## Visual Styling

### CSS Styling
```css
/* Activity Bar Container */
ActivityBar {
    background-color: #2d2d30;
    border-right: 1px solid #3e3e42;
    min-width: 48px;
    max-width: 48px;
}

/* Activity Button */
ActivityButton {
    background-color: transparent;
    border: none;
    color: #cccccc;
    font-size: 20px;
    min-height: 48px;
    max-height: 48px;
    min-width: 48px;
    max-width: 48px;
    padding: 0px;
    margin: 0px;
}

/* Activity Button Hover */
ActivityButton:hover {
    background-color: #37373d;
}

/* Activity Button Active */
ActivityButton.active {
    background-color: #37373d;
    border-left: 2px solid #0078d4;
}

/* Activity Button Badge */
ActivityButton::badge {
    background-color: #f14c4c;
    color: white;
    border-radius: 6px;
    font-size: 9px;
    font-weight: bold;
    min-width: 12px;
    height: 12px;
    position: absolute;
    top: 8px;
    right: 8px;
}
```

### Icon Specifications
- **Size:** 20x20 pixels for emoji, 16x16 for SVG icons
- **Format:** Unicode emoji preferred, SVG as fallback
- **Color:** Monochrome icons that adapt to theme
- **Hover State:** Slight brightness increase
- **Active State:** Full opacity with accent border

## Behavioral Patterns

### Click Behavior
1. **Single Click:**
   - Activates the corresponding panel
   - Switches panel content if different activity
   - Toggles panel visibility if same activity

2. **Keyboard Navigation:**
   - Tab/Shift+Tab: Navigate between buttons
   - Enter/Space: Activate selected button
   - Escape: Close current panel

3. **Context Menu:**
   - Right-click shows activity options
   - Hide/show activity
   - Customize position
   - Access activity settings

### Panel Management
1. **Panel Switching:**
   - Smooth transition between panels
   - State preservation for each panel
   - Lazy loading of panel content

2. **Panel Visibility:**
   - Remember last visible state
   - Keyboard shortcuts toggle visibility
   - Auto-hide on small screens

## Integration with Core System

### Plugin Registration
```python
from lg import logger

# In plugin's register() method
def register(api: PluginAPI) -> None:
    activity = ActivityConfig(
        id="my_plugin",
        icon="🔧",
        tooltip="My Plugin",
        panel_class="MyPluginPanel",
        keyboard_shortcut="Ctrl+Shift+M"
    )
    api.register_activity(activity)
    logger.info(f"Plugin registered activity: {activity.id}")
```

### Event Handling
```python
from lg import logger

# Activity Manager handles panel switching
def on_activity_clicked(self, activity_id: str) -> None:
    # Hide current panel - using direct attribute access
    if self.current_panel:
        self.current_panel.hide()
        logger.debug(f"Hidden panel for activity: {self.current_activity_id}")
    
    # Show new panel - ensuring attributes exist
    if activity_id in self.panels:
        new_panel = self.panels[activity_id]
        new_panel.show()
        self.current_panel = new_panel
        self.current_activity_id = activity_id
        
        self.api.emit_event("activity.changed", {
            "activity_id": activity_id,
            "panel": new_panel
        })
        logger.info(f"Switched to activity: {activity_id}")
    else:
        logger.error(f"Panel not found for activity: {activity_id}")
```

### Configuration Integration
```python
# Activity bar settings in "activity_bar" namespace
DEFAULT_CONFIG = {
    "visible": True,
    "width": 48,
    "position": "left",
    "auto_hide": False,
    "show_badges": True,
    "animation_enabled": True,
    "active_activities": ["explorer", "search", "preferences", "extensions"],
    "activity_order": {
        "explorer": 0,
        "search": 1,
        "preferences": 2,
        "extensions": 3
    }
}
```

## Accessibility Features

### Screen Reader Support
- Proper ARIA labels for all buttons
- Role definitions for navigation elements
- State announcements for active/inactive

### Keyboard Navigation
- Full keyboard accessibility
- Logical tab order
- Shortcut key support
- Focus indicators

### High Contrast Support
- Respect system high contrast settings
- Sufficient color contrast ratios
- Clear focus indicators

## Performance Considerations

### Lazy Loading
- Panels loaded only when first accessed
- Icon loading optimized
- Memory efficient panel management

### Animation Performance
- GPU-accelerated transitions
- Reduced animations on low-end hardware
- Configurable animation settings

### Resource Management
- Efficient icon caching
- Panel state preservation
- Memory cleanup on panel destruction

## Testing Strategy

### Unit Tests
```python
from lg import logger
import pytest
from PySide6.QtWidgets import QApplication
from widgets.activity_bar import ActivityBar, ActivityButton
from managers.activity_manager import ActivityManager

class TestActivityBar:
    def setup_method(self):
        """Setup test environment with proper attribute initialization"""
        self.app = QApplication.instance() or QApplication([])
        self.api = MockPluginAPI()  # Assuming MockPluginAPI exists
        self.activity_bar = ActivityBar(self.api)
        logger.info("Test setup completed")
        
    def test_add_activity_button(self):
        """Test adding activity button with direct attribute access"""
        button = ActivityButton("test_id", "🔧", "Test Tooltip")
        
        # Ensure button has required attributes before adding
        assert button.activity_id == "test_id"
        assert button.icon_text == "🔧"
        assert button.tooltip_text == "Test Tooltip"
        
        self.activity_bar.add_activity_button(button)
        
        # Direct attribute access instead of hasattr/getattr
        assert "test_id" in self.activity_bar.buttons
        assert self.activity_bar.buttons["test_id"] is button
        logger.info("Activity button addition test passed")
        
    def test_set_active_activity(self):
        """Test setting active activity with proper attribute management"""
        button1 = ActivityButton("test1", "🔧", "Test 1")
        button2 = ActivityButton("test2", "🔍", "Test 2")
        
        self.activity_bar.add_activity_button(button1)
        self.activity_bar.add_activity_button(button2)
        
        # Test activation with direct attribute access
        self.activity_bar.set_active_activity("test1")
        assert self.activity_bar.active_activity_id == "test1"
        assert button1.is_active is True
        assert button2.is_active is False
        
        # Test switching
        self.activity_bar.set_active_activity("test2")
        assert self.activity_bar.active_activity_id == "test2"
        assert button1.is_active is False
        assert button2.is_active is True
        
        logger.info("Active activity test passed")
```

### Integration Tests
```python
from lg import logger
import pytest
from core.plugin_manager import PluginManager
from widgets.activity_bar import ActivityBar

class TestActivityBarIntegration:
    def setup_method(self):
        """Setup integration test environment"""
        self.plugin_manager = PluginManager()
        self.activity_bar = ActivityBar(self.plugin_manager.api)
        logger.info("Integration test setup completed")
        
    def test_plugin_activity_registration(self):
        """Test plugin registering activities with proper attribute validation"""
        # Mock plugin that registers an activity
        class MockPlugin:
            def __init__(self):
                self.id = "mock_plugin"
                self.name = "Mock Plugin"
                
            def register(self, api):
                activity_config = ActivityConfig(
                    id=self.id,
                    icon="🔧",
                    tooltip=self.name,
                    panel_class="MockPanel"
                )
                # Ensure all required attributes are set
                assert activity_config.id == self.id
                assert activity_config.icon == "🔧"
                
                api.register_activity(activity_config)
                logger.info(f"Mock plugin registered: {self.id}")
        
        plugin = MockPlugin()
        plugin.register(self.plugin_manager.api)
        
        # Verify registration with direct attribute access
        activities = self.plugin_manager.api.activity_manager.activities
        assert plugin.id in activities
        assert activities[plugin.id].icon == "🔧"
        
        logger.info("Plugin registration integration test passed")
        
    def test_event_system_integration(self):
        """Test event handling with proper attribute management"""
        event_received = False
        received_data = {}
        
        def on_activity_changed(data):
            nonlocal event_received, received_data
            event_received = True
            received_data = data
            # Direct attribute access for event data
            assert data.activity_id  # Ensure attribute exists
            logger.info(f"Activity changed event received: {data.activity_id}")
        
        self.plugin_manager.api.register_event_handler(
            "activity.changed", 
            on_activity_changed
        )
        
        # Trigger activity change
        self.activity_bar.panel_requested.emit("test_activity")
        
        # Verify event was handled
        assert event_received
        logger.info("Event system integration test passed")
```

### UI Tests
- Visual styling verification
- Hover and click interactions
- Badge display functionality
- Accessibility compliance

### Performance Tests
- Panel switching speed
- Memory usage monitoring
- Animation performance
- Large workspace handling

## Migration from Old Code

### Existing Components
The Activity Bar adapts functionality from:

**old_codes/toolbars/**
- Basic toolbar structure and styling
- Icon management and theming

**old_codes/main_gui.py**
- Main window layout integration
- Panel management logic

### Backward Compatibility
- Graceful fallback for missing icons
- Configuration migration from old settings
- Preserved keyboard shortcuts

## Future Enhancements

### Advanced Features
- Drag and drop reordering
- Custom activity creation
- Badge notifications from plugins
- Activity grouping and categories

### Customization Options
- Icon theme support
- Custom positioning (top, bottom, right)
- Activity hiding and showing
- Size and spacing adjustments

### Plugin Ecosystem
- Activity marketplace
- Community-created activities
- Activity templates and generators
- Advanced plugin integration APIs

## Dependencies

**Core Services:**
- ConfigurationService: Activity settings and state
- EventService: Activity switching events
- PluginAPI: Activity registration interface

**Qt Components:**
- QWidget: Main container
- QPushButton: Activity buttons
- QVBoxLayout: Vertical button arrangement
- QPropertyAnimation: Smooth transitions

**External Libraries:**
- None (pure Qt implementation)

This Activity Bar design provides a foundational navigation system that seamlessly integrates with the plugin architecture while maintaining consistency with modern IDE patterns.
