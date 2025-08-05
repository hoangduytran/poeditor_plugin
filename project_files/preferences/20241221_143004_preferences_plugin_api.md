# Preferences System: Plugin API

## Overview
This document defines the Plugin Extension API for the preferences system, allowing third-party developers to extend the application with custom functionality while maintaining integration with the preferences framework.

## Plugin Architecture

The plugin system follows a modular architecture with clear extension points:

### Core Concepts

1. **Plugin Registry**: Central manager that discovers, loads, and tracks plugins
2. **Extension Points**: Well-defined interfaces where plugins can add functionality 
3. **Plugin Descriptor**: Metadata file that describes a plugin's capabilities
4. **Plugin Container**: Isolated environment for plugin execution
5. **Plugin API**: Public interfaces available to plugins

## Plugin Lifecycle

### Registration and Discovery

```python
class PluginRegistry:
    """Central registry for plugin management."""
    
    plugin_loaded = Signal(str)  # Plugin ID
    plugin_unloaded = Signal(str)  # Plugin ID
    
    def __init__(self):
        self._plugins = {}  # Plugin ID -> Plugin instance
        self._extension_points = {}  # Extension point ID -> Extension point
        self._plugin_states = {}  # Plugin ID -> PluginState
        
    def register_extension_point(self, extension_point: ExtensionPoint) -> None:
        """Register an extension point where plugins can integrate."""
        
    def discover_plugins(self) -> list[PluginDescriptor]:
        """Scan for available plugins in the plugins directory."""
        
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin by ID."""
        
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin and clean up its resources."""
        
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin instance by ID."""
        
    def get_plugins_for_extension_point(self, extension_point_id: str) -> list[Plugin]:
        """Get all plugins that implement a specific extension point."""
```

### Plugin Descriptor

Each plugin must include a `plugin.json` descriptor file:

```json
{
  "id": "com.example.translation-helper",
  "name": "Translation Helper",
  "version": "1.0.0",
  "description": "Provides additional translation assistance tools",
  "author": "Example Developer",
  "main": "translation_helper.py",
  "requires": "2.0.0",
  "extension_points": [
    "preferences.page",
    "editor.context_menu",
    "translation.processor"
  ],
  "configuration": {
    "api_key": {
      "type": "string",
      "default": "",
      "description": "API key for translation service"
    },
    "enable_suggestions": {
      "type": "boolean",
      "default": true,
      "description": "Enable automatic suggestions"
    }
  }
}
```

### Plugin Base Class

```python
class Plugin:
    """Base class for all plugins."""
    
    def __init__(self, descriptor: PluginDescriptor, registry: PluginRegistry):
        self.descriptor = descriptor
        self.registry = registry
        self.logger = logging.getLogger(f"plugin.{descriptor.id}")
        self._extension_implementations = {}
        
    def initialize(self) -> bool:
        """Initialize the plugin. Override in subclasses."""
        return True
        
    def shutdown(self) -> None:
        """Clean up resources. Override in subclasses."""
        pass
        
    def register_extension(self, extension_point_id: str, 
                           implementation: Any) -> None:
        """Register an implementation for an extension point."""
        
    def get_configuration(self) -> dict:
        """Get the plugin's configuration from preferences."""
        
    def set_configuration_value(self, key: str, value: Any) -> None:
        """Update a configuration value."""
```

## Extension Points

The preferences system exposes several extension points for plugins:

### Preference Pages

Plugins can add custom pages to the preferences dialog:

```python
class PreferencePageExtensionPoint(ExtensionPoint):
    """Extension point for adding pages to the preferences dialog."""
    
    def __init__(self):
        super().__init__("preferences.page")
        
    def create_extension(self, plugin: Plugin, 
                        implementation_class: Type) -> Optional[PreferencePage]:
        """Create a preference page from the plugin."""
        
    def get_pages(self) -> list[PreferencePage]:
        """Get all registered preference pages from plugins."""
```

Plugin implementation:

```python
class MyPluginPreferencePage(PreferencePage):
    """Custom preferences page from a plugin."""
    
    def __init__(self, parent=None):
        super().__init__("My Plugin", QIcon(":/icons/plugin.svg"), parent)
        self._setup_ui()
        
    def _setup_ui(self):
        # Create custom UI elements
        
    def apply_changes(self) -> bool:
        # Apply configuration changes
        return True
        
    def reset_to_defaults(self) -> None:
        # Reset to defaults
        pass
```

### Context Menus

Plugins can add items to context menus:

```python
class ContextMenuExtensionPoint(ExtensionPoint):
    """Extension point for adding items to context menus."""
    
    def __init__(self):
        super().__init__("editor.context_menu")
        
    def get_menu_items(self, context: dict) -> list[tuple[str, Callable]]:
        """Get menu items from all plugins for the given context."""
```

### Translation Processors

Plugins can process translations:

```python
class TranslationProcessorExtensionPoint(ExtensionPoint):
    """Extension point for processing translations."""
    
    def __init__(self):
        super().__init__("translation.processor")
        
    def process_translation(self, source: str, translation: str, 
                          context: dict) -> list[tuple[str, dict]]:
        """Get processed translations from all plugins."""
```

## Plugin Configuration UI

### Standard Configuration Components

To maintain UI consistency, plugins should use standard configuration components:

```python
class PluginConfigBuilder:
    """Helper for building plugin configuration UI."""
    
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.layout = QVBoxLayout()
        
    def add_text_field(self, key: str, label: str) -> QLineEdit:
        """Add a text field for a configuration value."""
        
    def add_checkbox(self, key: str, label: str) -> QCheckBox:
        """Add a checkbox for a boolean configuration value."""
        
    def add_combo_box(self, key: str, label: str, 
                     options: list[str]) -> QComboBox:
        """Add a combo box for a multiple-choice configuration value."""
        
    def add_file_picker(self, key: str, label: str) -> QPushButton:
        """Add a file picker for a file path configuration value."""
        
    def build(self) -> QWidget:
        """Build and return the configuration widget."""
```

## Plugin Manager UI

A dedicated Plugin Manager UI allows users to:

1. Browse installed plugins
2. Enable/disable plugins
3. Configure plugin settings
4. Install/uninstall plugins

```python
class PluginManagerPage(PreferencePage):
    """Preference page for managing plugins."""
    
    def __init__(self, parent=None):
        super().__init__("Plugins", QIcon(":/icons/plugins.svg"), parent)
        self._plugin_registry = PluginRegistry.instance()
        self._setup_ui()
        
    def _setup_ui(self):
        # Create plugin list, details panel, and action buttons
        
    def _on_plugin_selected(self, plugin_id: str):
        # Show details for the selected plugin
        
    def _on_enable_toggle(self, plugin_id: str, enabled: bool):
        # Enable or disable the plugin
        
    def _on_configure(self, plugin_id: str):
        # Show configuration dialog for plugin
        
    def _on_install(self):
        # Show dialog to install a new plugin
        
    def _on_uninstall(self, plugin_id: str):
        # Uninstall the selected plugin
```

## Plugin Development API

### Plugin Development Kit

To assist plugin developers, we provide a Plugin Development Kit (PDK):

```python
class PluginDevelopmentKit:
    """Tools and utilities for plugin development."""
    
    @staticmethod
    def create_plugin_template(plugin_id: str, output_dir: str) -> bool:
        """Generate a plugin template structure."""
        
    @staticmethod
    def validate_plugin(plugin_dir: str) -> list[str]:
        """Validate a plugin structure and report issues."""
        
    @staticmethod
    def package_plugin(plugin_dir: str, output_file: str) -> bool:
        """Package a plugin for distribution."""
```

### Plugin Template Structure

```
my-plugin/
├── plugin.json          # Plugin descriptor
├── my_plugin.py         # Main plugin class
├── resources/           # Plugin resources
│   ├── icons/
│   └── translations/
├── preferences/         # Preference page implementations
│   └── my_settings.py
└── README.md            # Plugin documentation
```

## Plugin API Documentation

### Accessible Services

Plugins have access to core application services:

```python
class PluginAPI:
    """API exposed to plugins."""
    
    @staticmethod
    def get_translation_service() -> TranslationService:
        """Get the translation service instance."""
        
    @staticmethod
    def get_preferences_service() -> PreferencesService:
        """Get the preferences service instance."""
        
    @staticmethod
    def get_ui_service() -> UIService:
        """Get the UI service instance."""
        
    @staticmethod
    def get_project_service() -> ProjectService:
        """Get the project service instance."""
```

### Event Subscription

Plugins can subscribe to application events:

```python
class PluginEventBus:
    """Event bus for plugin communication."""
    
    @staticmethod
    def subscribe(event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        
    @staticmethod
    def unsubscribe(event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        
    @staticmethod
    def publish(event_type: str, data: Any) -> None:
        """Publish an event."""
```

## Security Considerations

### Plugin Sandbox

Plugins run in a restricted environment:

```python
class PluginSandbox:
    """Security sandbox for plugin execution."""
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self._allowed_apis = set()
        self._file_access = "restricted"  # or "none" or "full"
        
    def run_plugin_code(self, code_obj: Any, globals_dict: dict) -> Any:
        """Execute plugin code in the sandbox."""
        
    def allow_api(self, api_name: str) -> None:
        """Allow access to a specific API."""
        
    def set_file_access(self, level: str) -> None:
        """Set the file access level."""
```

### Plugin Permissions

Plugins must request permissions in their descriptor:

```json
{
  "id": "com.example.translation-helper",
  "name": "Translation Helper",
  "permissions": [
    "preferences.read",
    "preferences.write",
    "files.read",
    "network.connect"
  ]
}
```

## Implementation Plan

1. **Phase 1: Core Infrastructure**
   - Plugin registry and descriptor loading
   - Basic extension point system
   - Plugin lifecycle management

2. **Phase 2: Preference Integration**
   - Preferences extension point
   - Plugin configuration storage
   - Plugin settings UI components

3. **Phase 3: Plugin Manager UI**
   - Plugin listing and details
   - Enable/disable functionality
   - Configuration dialogs

4. **Phase 4: Developer Tools**
   - Plugin Development Kit
   - Documentation generator
   - Example plugins and templates

## Migration Path

For existing plugin-like functionality:

1. **Identify Current Extensions**: Audit existing code for extension points
2. **Create Migration Adapters**: Build adapters for legacy extensions
3. **Documentation**: Provide migration guides for extension developers
4. **Compatibility Layer**: Support both old and new plugin systems during transition

## Testing Strategy

1. **Unit Testing**: Test each plugin system component in isolation
2. **Integration Testing**: Test plugin loading and interaction with core systems
3. **Mock Plugins**: Create test plugins that verify extension points
4. **Security Testing**: Verify sandbox restrictions and permission enforcement

## Reference Implementation

A minimal example plugin that adds a preferences page:

```python
# my_plugin.py
from core.plugin import Plugin
from core.preferences import PreferencePage
from PySide6.QtWidgets import QVBoxLayout, QLabel, QCheckBox

class MyPlugin(Plugin):
    def initialize(self) -> bool:
        # Register preference page
        self.register_extension("preferences.page", MyPreferencePage)
        return True

class MyPreferencePage(PreferencePage):
    def __init__(self, parent=None):
        super().__init__("My Plugin", None, parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("My Plugin Settings"))
        
        enable_feature = QCheckBox("Enable feature")
        enable_feature.setChecked(self.get_setting("enable_feature", True))
        enable_feature.toggled.connect(lambda checked: 
                                     self.set_setting("enable_feature", checked))
        layout.addWidget(enable_feature)
        
        layout.addStretch(1)
        
    def get_setting(self, key: str, default=None):
        """Get a plugin setting."""
        plugin_id = "com.example.my-plugin"
        return self.registry.get_plugin(plugin_id).get_configuration().get(key, default)
        
    def set_setting(self, key: str, value):
        """Set a plugin setting."""
        plugin_id = "com.example.my-plugin"
        self.registry.get_plugin(plugin_id).set_configuration_value(key, value)
```

## Future Enhancements

1. **Plugin Marketplace**: Online repository for discovering and installing plugins
2. **Dependency Management**: Handle plugin dependencies automatically
3. **Plugin Updates**: Auto-update mechanism for installed plugins
4. **Plugin Analytics**: Collect anonymous usage data for plugin developers
5. **Multi-Version Support**: Allow multiple versions of plugins to coexist
