# Core Components Design

## Overview
This document outlines the design for the core components of the plugin-based POEditor application following VS Code-like architecture.

## Core Components

### 1. MainAppWindow
**File:** `core/main_app_window.py`

**Purpose:** The main application window that hosts all UI components.

**Key Features:**
- Uses QSplitter(Qt.Horizontal) for layout
- Manages global application state
- Coordinates between sidebar and tab area
- Handles application-level events and shortcuts

**Interface:**
```python
class MainAppWindow(QMainWindow):
    def __init__(self)
    def setup_ui(self) -> None
    def setup_splitter(self) -> None
    def load_plugins(self) -> None
    def show_sidebar(self, visible: bool) -> None
    def get_active_tab(self) -> Optional[QWidget]
    def closeEvent(self, event: QCloseEvent) -> None
```

### 2. PluginManager
**File:** `core/plugin_manager.py`

**Purpose:** Discovers, loads, and manages plugins dynamically.

**Key Features:**
- Plugin discovery from plugins/ directory
- Plugin lifecycle management (load, unload, reload)
- Error handling and plugin isolation
- Plugin dependency resolution

**Interface:**
```python
class PluginManager:
    def __init__(self, plugin_dir: str, api: 'PluginAPI')
    def discover_plugins(self) -> List[str]
    def load_plugin(self, plugin_name: str) -> bool
    def unload_plugin(self, plugin_name: str) -> bool
    def reload_plugin(self, plugin_name: str) -> bool
    def get_loaded_plugins(self) -> List[str]
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]
```

### 3. SidebarManager
**File:** `core/sidebar_manager.py`

**Purpose:** Manages the left sidebar panels provided by plugins.

**Key Features:**
- Panel registration and management
- Activity bar for panel switching
- Panel visibility toggle
- Resizable sidebar

**Interface:**
```python
class SidebarManager(QWidget):
    def __init__(self, parent: Optional[QWidget] = None)
    def add_panel(self, panel_id: str, widget: QWidget, icon: QIcon, title: str) -> None
    def remove_panel(self, panel_id: str) -> bool
    def show_panel(self, panel_id: str) -> None
    def hide_panel(self, panel_id: str) -> None
    def get_active_panel(self) -> Optional[str]
    def toggle_visibility(self) -> None
```

### 4. TabManager
**File:** `core/tab_manager.py`

**Purpose:** Manages document tabs in the main editor area.

**Key Features:**
- Tab creation and management
- Tab switching and navigation
- Tab close handling
- Support for different tab types

**Interface:**
```python
class TabManager(QTabWidget):
    def __init__(self, parent: Optional[QWidget] = None)
    def add_tab(self, widget: QWidget, title: str, icon: Optional[QIcon] = None) -> int
    def close_tab(self, index: int) -> bool
    def close_all_tabs(self) -> bool
    def get_active_tab(self) -> Optional[QWidget]
    def find_tab(self, widget: QWidget) -> int
    def set_tab_modified(self, index: int, modified: bool) -> None
```

### 5. PluginAPI
**File:** `core/api.py`

**Purpose:** Provides the interface for plugins to interact with the core application.

**Key Features:**
- Sidebar panel registration
- Tab management
- Command registration
- Event subscription
- Core service access

**Interface:**
```python
class PluginAPI:
    def __init__(self, main_window: 'MainAppWindow')
    
    # Sidebar management
    def add_sidebar_panel(self, panel_id: str, widget: QWidget, icon: QIcon, title: str) -> None
    def remove_sidebar_panel(self, panel_id: str) -> bool
    
    # Tab management
    def add_tab(self, widget: QWidget, title: str, icon: Optional[QIcon] = None) -> int
    def close_tab(self, widget: QWidget) -> bool
    def get_active_tab(self) -> Optional[QWidget]
    
    # Command system
    def register_command(self, command_id: str, callback: Callable) -> None
    def execute_command(self, command_id: str, *args, **kwargs) -> Any
    
    # Events
    def subscribe_event(self, event_name: str, callback: Callable) -> None
    def emit_event(self, event_name: str, *args, **kwargs) -> None
    
    # Services
    def get_service(self, service_name: str) -> Optional[Any]
    def register_service(self, service_name: str, service: Any) -> None
```

## Data Flow

1. **Application Startup:**
   - MainAppWindow initializes
   - Creates PluginManager with PluginAPI
   - PluginManager discovers and loads plugins
   - Plugins register panels and commands via API

2. **User Interaction:**
   - User clicks sidebar panel → SidebarManager shows panel
   - User opens file → Plugin creates tab via TabManager
   - User executes command → PluginAPI routes to plugin

3. **Plugin Communication:**
   - Plugins communicate via events through PluginAPI
   - Core services accessible through PluginAPI

## Error Handling

- All plugin operations wrapped in try-catch
- Plugin failures logged but don't crash core
- Graceful degradation when plugins fail
- User notification for plugin errors

## Threading

- Core components run on main thread
- Plugin operations may use worker threads
- Thread-safe event emission
- UI updates marshaled to main thread

## Configuration

- Core settings stored in QSettings
- Plugin settings namespaced by plugin ID
- Configuration service accessible via PluginAPI

## Logging

- Use lg.py module for all logging
- Plugin operations logged with plugin context
- Error tracking and debugging support
