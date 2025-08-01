# Plugin System Design

## Overview
This document details the plugin architecture that allows the POEditor application to be extended with new functionality through a modular plugin system.

## Plugin Architecture

### Plugin Structure
Each plugin is a Python package in the `plugins/` directory with the following structure:

```
plugins/
├── explorer/
│   ├── __init__.py
│   ├── plugin.py          # Main plugin entry point
│   ├── explorer_panel.py  # UI components
│   └── models/            # Plugin-specific models
├── search/
│   ├── __init__.py
│   ├── plugin.py
│   └── search_panel.py
└── settings/
    ├── __init__.py
    ├── plugin.py
    └── settings_panel.py
```

### Plugin Entry Point
Every plugin must have a `plugin.py` file with a `register()` function:

```python
# plugins/example/plugin.py
from lg import logger

def register(api):
    """
    Plugin registration function called by PluginManager
    
    Args:
        api (PluginAPI): Core application API for plugin interaction
    """
    try:
        logger.info(f"Registering plugin: example")
        
        # Import plugin components
        from .example_panel import ExamplePanel
        
        # Create and register UI panel
        panel = ExamplePanel()
        api.add_sidebar_panel(
            panel_id="example",
            widget=panel,
            icon=QIcon(":/icons/example.png"),
            title="Example"
        )
        
        # Register commands
        api.register_command("example.hello", lambda: logger.info("Hello from plugin!"))
        
        logger.info(f"Plugin 'example' registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register plugin 'example': {e}")
        raise

def unregister(api):
    """
    Optional cleanup function called when plugin is unloaded
    """
    try:
        api.remove_sidebar_panel("example")
        logger.info(f"Plugin 'example' unregistered successfully")
    except Exception as e:
        logger.error(f"Failed to unregister plugin 'example': {e}")
```

## Plugin Types

### 1. Sidebar Panel Plugins
Provide panels for the left sidebar (like VS Code's Explorer, Search, etc.)

**Requirements:**
- Must provide a QWidget-based panel
- Should handle panel lifecycle (show/hide events)
- Can persist panel state

**Example:**
```python
class ExplorerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Add UI components
    
    def showEvent(self, event):
        # Panel becoming visible
        self.refresh_content()
    
    def hideEvent(self, event):
        # Panel being hidden
        self.save_state()
```

### 2. Tab Provider Plugins
Create new tab types for the main editor area

**Requirements:**
- Must provide QWidget-based tab content
- Should handle tab lifecycle events
- Can provide custom context menus

**Example:**
```python
class CustomEditorTab(QWidget):
    modified_changed = Signal(bool)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self.setup_ui()
    
    def setup_ui(self):
        # Create tab content
        pass
    
    def save(self) -> bool:
        # Save tab content
        return True
    
    def close(self) -> bool:
        # Handle tab close (check for unsaved changes)
        return True
```

### 3. Command Plugins
Provide application commands accessible via menus, shortcuts, or other plugins

**Example:**
```python
def register(api):
    api.register_command("file.open", lambda: open_file_dialog())
    api.register_command("edit.find", lambda: show_find_dialog())
    api.register_command("view.toggle_sidebar", lambda: api.toggle_sidebar())
```

### 4. Service Plugins
Provide core services that other plugins can use

**Example:**
```python
class TranslationService:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        # Translation logic
        pass

def register(api):
    service = TranslationService()
    api.register_service("translation", service)
```

## Plugin Discovery and Loading

### Discovery Process
1. PluginManager scans `plugins/` directory
2. Identifies Python packages (directories with `__init__.py`)
3. Checks for `plugin.py` with `register()` function
4. Validates plugin metadata (optional `plugin.json`)

### Loading Process
1. Import plugin module
2. Call `register(api)` function
3. Handle registration errors gracefully
4. Track plugin state and dependencies

### Plugin Metadata (Optional)
```json
{
    "name": "Explorer Plugin",
    "version": "1.0.0",
    "description": "File system explorer panel",
    "author": "Plugin Author",
    "requires": ["core>=1.0.0"],
    "dependencies": ["other_plugin"],
    "entry_point": "plugin.py"
}
```

## Plugin API Capabilities

### Core Services Access
- Configuration management
- Logging system
- Event system
- File system utilities
- Database access (for PO files)

### UI Integration
- Sidebar panel registration
- Tab creation and management
- Menu and toolbar integration
- Status bar updates
- Dialog creation

### Event System
Plugins can subscribe to and emit events:

```python
# Subscribe to events
api.subscribe_event("file.opened", on_file_opened)
api.subscribe_event("tab.closed", on_tab_closed)

# Emit custom events
api.emit_event("translation.updated", entry_id="123", new_text="Hello")
```

## Plugin Communication

### Event-Based Communication
Plugins communicate through the event system to maintain loose coupling:

```python
# Plugin A emits event
api.emit_event("search.result_selected", file_path="file.po", line=42)

# Plugin B listens for event
def on_search_result(file_path, line):
    # Open file and navigate to line
    api.execute_command("file.open", file_path)
    api.execute_command("editor.goto_line", line)

api.subscribe_event("search.result_selected", on_search_result)
```

### Service-Based Communication
Plugins can provide and consume services:

```python
# Plugin provides service
class DatabaseService:
    def get_po_entries(self, file_path: str):
        # Return PO entries
        pass

api.register_service("database", DatabaseService())

# Other plugin uses service
db_service = api.get_service("database")
entries = db_service.get_po_entries("file.po")
```

## Plugin Error Handling

### Error Isolation
- Plugin errors don't crash the core application
- Failed plugins are disabled but other plugins continue working
- Error information logged and available for debugging

### Error Recovery
- Plugins can be reloaded after fixing errors
- Core provides fallback behavior when plugins fail
- User notifications for plugin issues

### Debugging Support
- Detailed error logging with stack traces
- Plugin state inspection
- Development mode with enhanced debugging

## Plugin Hot Reloading (Advanced)

For development convenience, plugins can be reloaded without restarting the application:

```python
# Reload a specific plugin
plugin_manager.reload_plugin("explorer")

# Reload all plugins
plugin_manager.reload_all_plugins()
```

## Security Considerations

### Plugin Sandboxing
- Plugins run in the same process (PySide6 limitation)
- Trust-based security model
- Code review for included plugins

### Input Validation
- All plugin inputs validated by core
- File path sanitization
- Command parameter validation

### Resource Limits
- Plugin resource usage monitoring
- Memory and CPU limits (future enhancement)
- Timeout for long-running operations

## Plugin Development Guidelines

### Best Practices
1. Use dependency injection through PluginAPI
2. Handle errors gracefully with proper logging
3. Follow PEP8 coding standards
4. Provide comprehensive docstrings
5. Use type hints for all public interfaces
6. Minimize startup time
7. Clean up resources in unregister()

### Testing
- Unit tests for plugin logic
- Integration tests with PluginAPI
- Mock API for isolated testing
- Test plugin loading/unloading

### Documentation
- README.md for each plugin
- API usage examples
- Configuration options
- Known limitations

## Standard Plugins

### Explorer Plugin
- File system navigation
- PO file management
- File operations (create, delete, rename)
- Integration with tab system

### Search Plugin
- Global search across files
- Find and replace functionality
- Search result navigation
- Integration with editor tabs

### Settings Plugin
- Application preferences
- Plugin configuration
- Theme management
- Keyboard shortcuts

### POEditor Plugin
- PO file editing tabs
- Translation entry management
- Import/export functionality
- Integration with database service

## Future Enhancements

### Plugin Marketplace
- Online plugin repository
- Plugin installation/update system
- Plugin rating and reviews
- Dependency management

### Plugin SDK
- Development tools and templates
- Plugin scaffolding commands
- Testing utilities
- Documentation generator

### Advanced Features
- Plugin permissions system
- Plugin update notifications
- Plugin usage analytics
- Performance profiling
