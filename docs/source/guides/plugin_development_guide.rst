==============================
Plugin Development Guide
==============================

.. py:module:: guides.plugin_development

Complete guide for creating custom plugins for the PySide POEditor Plugin system.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

The PySide POEditor Plugin supports a modular plugin architecture that allows developers to extend functionality without modifying core code. This guide covers:

* **Plugin Architecture**: Understanding the plugin system
* **Plugin API**: Working with the plugin interface
* **Activity Integration**: Adding plugins to the activity bar
* **Panel Integration**: Creating plugin panels
* **Plugin Lifecycle**: Loading, initialization, and cleanup

Plugin System Architecture
==========================

How Plugins Work
---------------

The plugin system is built on a modular architecture:

.. code-block:: text

   Plugin System Architecture:
   ├── PluginManager               # Core plugin loading and management
   ├── PluginAPI                   # Interface for plugin communication
   ├── ActivityManager             # Activity bar integration
   ├── SidebarManager             # Panel container management
   └── Individual Plugins
       ├── ExplorerPlugin         # File explorer functionality
       ├── SearchPlugin           # Search functionality
       ├── AccountPlugin          # Account management
       └── CustomPlugin           # Your custom plugin

**Key Components:**

* ``core/plugin_manager.py`` - Main plugin loading and lifecycle management
* ``core/api.py`` - Plugin API interface definitions
* ``managers/activity_manager.py`` - Activity bar integration
* ``models/activity_models.py`` - Activity definitions
* ``plugins/`` - Plugin implementations

Plugin Interface
---------------

All plugins must implement the base plugin interface:

.. code-block:: python

   # Base plugin interface structure
   class BasePlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
       
       def activate(self) -> None:
           """Called when plugin is activated"""
           pass
       
       def deactivate(self) -> None:
           """Called when plugin is deactivated"""
           pass
       
       def get_activity_item(self) -> Optional[ActivityItem]:
           """Return activity bar item for this plugin"""
           return None

Creating a Custom Plugin
=======================

Step 1: Plugin Directory Structure
----------------------------------

Create your plugin directory structure:

.. code-block:: bash

   # Navigate to plugins directory
   cd /path/to/pyside_poeditor_plugin/plugins
   
   # Create plugin directory
   mkdir my_custom_plugin
   cd my_custom_plugin
   
   # Create plugin files
   touch __init__.py
   touch plugin.py
   touch panel.py

**Recommended Directory Structure:**

.. code-block:: text

   plugins/
   └── my_custom_plugin/
       ├── __init__.py              # Plugin package initialization
       ├── plugin.py                # Main plugin class
       ├── panel.py                 # Plugin panel implementation
       ├── services/                # Plugin-specific services
       │   └── my_service.py
       ├── models/                  # Plugin-specific models
       │   └── my_models.py
       └── resources/               # Plugin assets
           ├── icons/
           └── styles/

Step 2: Implement Plugin Class
------------------------------

Create the main plugin class:

.. code-block:: python

   # plugins/my_custom_plugin/plugin.py
   from typing import Optional
   from PySide6.QtCore import QObject
   
   from core.api import PluginAPI
   from models.activity_models import ActivityItem
   from .panel import MyCustomPanel
   
   class MyCustomPlugin(QObject):
       """Custom plugin for demonstrating plugin development"""
       
       def __init__(self, api: PluginAPI):
           super().__init__()
           self.api = api
           self.panel = None
           self._is_active = False
       
       def activate(self) -> None:
           """Activate the plugin"""
           if self._is_active:
               return
           
           print(f"Activating {self.__class__.__name__}")
           
           # Create panel instance
           self.panel = MyCustomPanel(self.api)
           
           # Register with activity manager
           activity_item = self.get_activity_item()
           if activity_item:
               self.api.activity_manager.register_activity(activity_item)
           
           self._is_active = True
       
       def deactivate(self) -> None:
           """Deactivate the plugin"""
           if not self._is_active:
               return
           
           print(f"Deactivating {self.__class__.__name__}")
           
           # Unregister from activity manager
           activity_item = self.get_activity_item()
           if activity_item:
               self.api.activity_manager.unregister_activity(activity_item.id)
           
           # Clean up panel
           if self.panel:
               self.panel.cleanup()
               self.panel = None
           
           self._is_active = False
       
       def get_activity_item(self) -> Optional[ActivityItem]:
           """Get activity bar item for this plugin"""
           return ActivityItem(
               id="my_custom_plugin",
               title="My Custom Plugin",
               icon_name="my_custom",  # Corresponds to my_custom_active.svg
               panel_class=MyCustomPanel,
               tooltip="My custom plugin functionality"
           )
       
       @property
       def is_active(self) -> bool:
           """Check if plugin is currently active"""
           return self._is_active

Step 3: Create Plugin Panel
---------------------------

Create the UI panel for your plugin:

.. code-block:: python

   # plugins/my_custom_plugin/panel.py
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
   from PySide6.QtCore import Signal
   
   from core.api import PluginAPI
   from panels.panel_interface import PanelInterface
   
   class MyCustomPanel(QWidget, PanelInterface):
       """Custom panel for the plugin"""
       
       # Panel interface signals
       panel_activated = Signal()
       panel_deactivated = Signal()
       
       def __init__(self, api: PluginAPI, parent=None):
           super().__init__(parent)
           self.api = api
           self.setup_ui()
           self.apply_theme()
       
       def setup_ui(self):
           """Set up the panel UI"""
           self.setObjectName("my-custom-panel")
           
           layout = QVBoxLayout(self)
           layout.setContentsMargins(16, 16, 16, 16)
           layout.setSpacing(12)
           
           # Title
           title = QLabel("My Custom Plugin")
           title.setObjectName("panel-title")
           layout.addWidget(title)
           
           # Description
           description = QLabel("This is a custom plugin demonstrating plugin development.")
           description.setObjectName("panel-description")
           description.setWordWrap(True)
           layout.addWidget(description)
           
           # Action button
           action_button = QPushButton("Perform Action")
           action_button.setObjectName("action-button")
           action_button.clicked.connect(self.perform_action)
           layout.addWidget(action_button)
           
           # Results area
           self.results_area = QTextEdit()
           self.results_area.setObjectName("results-area")
           self.results_area.setPlaceholderText("Action results will appear here...")
           layout.addWidget(self.results_area)
           
           # Add stretch to push content to top
           layout.addStretch()
       
       def apply_theme(self):
           """Apply current theme to the panel"""
           if hasattr(self.api, 'theme_manager'):
               css = self.api.theme_manager.get_processed_css()
               self.setStyleSheet(css)
       
       def perform_action(self):
           """Perform the main plugin action"""
           self.results_area.append("Action performed successfully!")
           self.results_area.append(f"API available: {self.api is not None}")
           
           # Example: Use API to get theme information
           if hasattr(self.api, 'theme_manager'):
               current_theme = self.api.theme_manager.current_theme_name
               self.results_area.append(f"Current theme: {current_theme}")
       
       def cleanup(self):
           """Clean up resources when panel is destroyed"""
           # Clean up any resources, connections, etc.
           pass
       
       # PanelInterface implementation
       def get_title(self) -> str:
           """Get panel title"""
           return "My Custom Plugin"
       
       def get_icon_name(self) -> str:
           """Get panel icon name"""
           return "my_custom"
       
       def refresh(self):
           """Refresh panel content"""
           self.results_area.clear()
           self.results_area.append("Panel refreshed")

Step 4: Plugin Package Initialization
-------------------------------------

Set up the plugin package:

.. code-block:: python

   # plugins/my_custom_plugin/__init__.py
   """
   My Custom Plugin
   
   A custom plugin demonstrating plugin development for the PySide POEditor Plugin.
   """
   
   from .plugin import MyCustomPlugin
   
   __version__ = "1.0.0"
   __author__ = "Your Name"
   __description__ = "Custom plugin demonstrating plugin development"
   
   # Plugin entry point
   def create_plugin(api):
       """Create and return plugin instance"""
       return MyCustomPlugin(api)

Step 5: Register Plugin
----------------------

Add your plugin to the plugin manager's discovery:

.. code-block:: python

   # Update core/plugin_manager.py or add to plugin registry
   AVAILABLE_PLUGINS = [
       "explorer",
       "search", 
       "account",
       "extensions",
       "preferences",
       "my_custom_plugin",  # Add your plugin here
   ]

Plugin API Usage
===============

Working with the Plugin API
---------------------------

The Plugin API provides access to core application services:

.. code-block:: python

   class MyAdvancedPlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
       
       def use_api_services(self):
           """Demonstrate API usage"""
           
           # Theme management
           if hasattr(self.api, 'theme_manager'):
               current_theme = self.api.theme_manager.current_theme_name
               themes = self.api.theme_manager.get_available_themes()
               self.api.theme_manager.set_theme('dark')
           
           # Activity management
           if hasattr(self.api, 'activity_manager'):
               activities = self.api.activity_manager.get_activities()
               self.api.activity_manager.set_active_activity('my_plugin')
           
           # Settings management (if available)
           if hasattr(self.api, 'settings_manager'):
               value = self.api.settings_manager.get_setting('my_setting', 'default')
               self.api.settings_manager.set_setting('my_setting', 'new_value')

Event System Integration
-----------------------

Plugins can listen to and emit events:

.. code-block:: python

   from PySide6.QtCore import QObject, Signal, Slot
   
   class EventAwarePlugin(QObject):
       # Custom plugin signals
       data_updated = Signal(dict)
       action_completed = Signal(str)
       
       def __init__(self, api: PluginAPI):
           super().__init__()
           self.api = api
           self.connect_events()
       
       def connect_events(self):
           """Connect to application events"""
           # Connect to theme changes
           if hasattr(self.api, 'theme_manager'):
               self.api.theme_manager.theme_changed.connect(self.on_theme_changed)
           
           # Connect to activity changes
           if hasattr(self.api, 'activity_manager'):
               self.api.activity_manager.activity_changed.connect(self.on_activity_changed)
       
       @Slot(str)
       def on_theme_changed(self, theme_name: str):
           """Handle theme change events"""
           print(f"Plugin: Theme changed to {theme_name}")
           # Update plugin UI for new theme
           if self.panel:
               self.panel.apply_theme()
       
       @Slot(str)
       def on_activity_changed(self, activity_id: str):
           """Handle activity change events"""
           if activity_id == "my_plugin":
               print("Plugin: My plugin became active")
               # Perform activation tasks
           else:
               print(f"Plugin: Activity changed to {activity_id}")

Advanced Plugin Features
=======================

Plugin Settings
--------------

Create persistent settings for your plugin:

.. code-block:: python

   class SettingsAwarePlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
           self.settings_key = "my_custom_plugin"
           self.load_settings()
       
       def load_settings(self):
           """Load plugin settings"""
           if hasattr(self.api, 'settings_manager'):
               self.enabled = self.api.settings_manager.get_setting(
                   f"{self.settings_key}.enabled", True
               )
               self.auto_refresh = self.api.settings_manager.get_setting(
                   f"{self.settings_key}.auto_refresh", False
               )
               self.refresh_interval = self.api.settings_manager.get_setting(
                   f"{self.settings_key}.refresh_interval", 5000
               )
       
       def save_settings(self):
           """Save plugin settings"""
           if hasattr(self.api, 'settings_manager'):
               self.api.settings_manager.set_setting(
                   f"{self.settings_key}.enabled", self.enabled
               )
               self.api.settings_manager.set_setting(
                   f"{self.settings_key}.auto_refresh", self.auto_refresh
               )
               self.api.settings_manager.set_setting(
                   f"{self.settings_key}.refresh_interval", self.refresh_interval
               )

Plugin Services
--------------

Create reusable services within your plugin:

.. code-block:: python

   # plugins/my_custom_plugin/services/data_service.py
   from PySide6.QtCore import QObject, Signal
   
   class DataService(QObject):
       """Service for handling plugin data operations"""
       
       data_loaded = Signal(dict)
       data_error = Signal(str)
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self.cache = {}
       
       def load_data(self, source: str):
           """Load data from source"""
           try:
               # Simulate data loading
               data = {"source": source, "items": [1, 2, 3, 4, 5]}
               self.cache[source] = data
               self.data_loaded.emit(data)
           except Exception as e:
               self.data_error.emit(str(e))
       
       def get_cached_data(self, source: str) -> dict:
           """Get cached data"""
           return self.cache.get(source, {})

Multi-Panel Plugins
------------------

Create plugins with multiple panels:

.. code-block:: python

   class MultiPanelPlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
           self.main_panel = None
           self.settings_panel = None
       
       def get_activity_items(self) -> list:
           """Return multiple activity items"""
           return [
               ActivityItem(
                   id="my_plugin_main",
                   title="My Plugin",
                   icon_name="my_plugin",
                   panel_class=MyMainPanel
               ),
               ActivityItem(
                   id="my_plugin_settings",
                   title="Plugin Settings",
                   icon_name="my_plugin_settings",
                   panel_class=MySettingsPanel
               )
           ]

Plugin Testing
==============

Unit Testing Plugins
--------------------

Create unit tests for your plugin:

.. code-block:: python

   # tests/plugins/test_my_custom_plugin.py
   import unittest
   from unittest.mock import Mock, MagicMock
   
   from core.api import PluginAPI
   from plugins.my_custom_plugin.plugin import MyCustomPlugin
   
   class TestMyCustomPlugin(unittest.TestCase):
       def setUp(self):
           """Set up test environment"""
           self.mock_api = Mock(spec=PluginAPI)
           self.mock_api.activity_manager = Mock()
           self.mock_api.theme_manager = Mock()
           
           self.plugin = MyCustomPlugin(self.mock_api)
       
       def test_plugin_activation(self):
           """Test plugin activation"""
           self.assertFalse(self.plugin.is_active)
           
           self.plugin.activate()
           
           self.assertTrue(self.plugin.is_active)
           self.assertIsNotNone(self.plugin.panel)
           self.mock_api.activity_manager.register_activity.assert_called_once()
       
       def test_plugin_deactivation(self):
           """Test plugin deactivation"""
           self.plugin.activate()
           self.plugin.deactivate()
           
           self.assertFalse(self.plugin.is_active)
           self.mock_api.activity_manager.unregister_activity.assert_called_once()
       
       def test_activity_item_creation(self):
           """Test activity item creation"""
           activity_item = self.plugin.get_activity_item()
           
           self.assertIsNotNone(activity_item)
           self.assertEqual(activity_item.id, "my_custom_plugin")
           self.assertEqual(activity_item.title, "My Custom Plugin")

Integration Testing
------------------

Test plugin integration with the application:

.. code-block:: python

   # tests/integration/test_plugin_integration.py
   import unittest
   from PySide6.QtWidgets import QApplication
   
   from core.plugin_manager import PluginManager
   from core.api import PluginAPI
   from managers.activity_manager import ActivityManager
   
   class TestPluginIntegration(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           """Set up test application"""
           cls.app = QApplication.instance() or QApplication([])
       
       def setUp(self):
           """Set up test environment"""
           self.activity_manager = ActivityManager()
           self.api = PluginAPI(activity_manager=self.activity_manager)
           self.plugin_manager = PluginManager(self.api)
       
       def test_plugin_loading(self):
           """Test plugin loading and registration"""
           # Load plugins
           self.plugin_manager.load_plugins()
           
           # Check that custom plugin is loaded
           self.assertIn("my_custom_plugin", self.plugin_manager.plugins)
           
           # Check activity registration
           activities = self.activity_manager.get_activities()
           plugin_activities = [a for a in activities if a.id == "my_custom_plugin"]
           self.assertTrue(len(plugin_activities) > 0)

Plugin Styling
==============

Adding Plugin CSS
-----------------

Style your plugin components:

.. code-block:: css

   /* Add to theme files */
   
   /* === MY CUSTOM PLUGIN === */
   #my-custom-panel {
       background-color: var(--color-bg-primary);
       padding: var(--spacing-md);
   }
   
   #my-custom-panel #panel-title {
       font-size: var(--font-size-lg);
       font-weight: var(--font-weight-bold);
       color: var(--color-primary);
       margin-bottom: var(--spacing-sm);
   }
   
   #my-custom-panel #panel-description {
       color: var(--color-text-muted);
       margin-bottom: var(--spacing-md);
   }
   
   #my-custom-panel #action-button {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
       border: none;
       padding: var(--spacing-sm) var(--spacing-md);
       border-radius: var(--border-radius-md);
   }
   
   #my-custom-panel #action-button:hover {
       background-color: color-mix(in srgb, var(--color-primary) 85%, black);
   }
   
   #my-custom-panel #results-area {
       background-color: var(--color-bg-secondary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-sm);
       padding: var(--spacing-sm);
       font-family: monospace;
   }

Plugin Icons
-----------

Add icons for your plugin:

.. code-block:: bash

   # Add icon files
   cp my_custom_active.svg icons/
   cp my_custom_inactive.svg icons/

The icon system will automatically process these icons and make them available for use.

Best Practices
=============

Plugin Architecture
------------------

1. **Single Responsibility**: Each plugin should have a clear, focused purpose
2. **Loose Coupling**: Minimize dependencies on other plugins
3. **API Usage**: Use the Plugin API for all core application interactions
4. **Resource Management**: Properly clean up resources in deactivate()
5. **Error Handling**: Handle errors gracefully and provide meaningful feedback

Code Organization
----------------

1. **Modular Structure**: Organize code into logical modules (services, models, panels)
2. **Clear Interfaces**: Define clear interfaces between plugin components
3. **Documentation**: Document all public methods and classes
4. **Testing**: Include comprehensive unit and integration tests
5. **Version Management**: Use semantic versioning for plugin releases

Performance Guidelines
---------------------

1. **Lazy Loading**: Load resources only when needed
2. **Efficient UI Updates**: Minimize unnecessary UI updates
3. **Memory Management**: Clean up resources properly
4. **Caching**: Use appropriate caching strategies
5. **Background Processing**: Use background threads for long-running operations

Common Patterns
==============

Data Processing Plugin
---------------------

.. code-block:: python

   class DataProcessingPlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
           self.worker_thread = None
       
       def process_data(self, data):
           """Process data in background thread"""
           from PySide6.QtCore import QThread, QObject, Signal
           
           class DataWorker(QObject):
               finished = Signal(dict)
               error = Signal(str)
               
               def __init__(self, data):
                   super().__init__()
                   self.data = data
               
               def process(self):
                   try:
                       # Process data
                       result = {"processed": len(self.data)}
                       self.finished.emit(result)
                   except Exception as e:
                       self.error.emit(str(e))
           
           self.worker = DataWorker(data)
           self.worker_thread = QThread()
           self.worker.moveToThread(self.worker_thread)
           
           self.worker.finished.connect(self.on_processing_finished)
           self.worker.error.connect(self.on_processing_error)
           self.worker_thread.started.connect(self.worker.process)
           
           self.worker_thread.start()

Configuration Plugin
-------------------

.. code-block:: python

   class ConfigurationPlugin:
       def __init__(self, api: PluginAPI):
           self.api = api
           self.config_file = "plugin_config.json"
       
       def load_configuration(self):
           """Load plugin configuration"""
           import json
           try:
               with open(self.config_file, 'r') as f:
                   return json.load(f)
           except FileNotFoundError:
               return self.get_default_config()
       
       def save_configuration(self, config):
           """Save plugin configuration"""
           import json
           with open(self.config_file, 'w') as f:
               json.dump(config, f, indent=2)
       
       def get_default_config(self):
           """Get default configuration"""
           return {
               "enabled": True,
               "auto_refresh": False,
               "refresh_interval": 5000
           }

Troubleshooting
==============

Common Issues
------------

**Plugin Not Loading**

1. Check plugin directory structure
2. Verify __init__.py contains create_plugin function
3. Check for syntax errors in plugin code
4. Ensure plugin is added to AVAILABLE_PLUGINS list

**Activity Not Appearing**

1. Verify ActivityItem is returned from get_activity_item()
2. Check icon files exist (my_plugin_active.svg, my_plugin_inactive.svg)
3. Ensure activity registration is called in activate()

**Panel Not Displaying**

1. Check panel_class in ActivityItem points to correct class
2. Verify panel inherits from QWidget and PanelInterface
3. Check for UI setup errors in setup_ui()

**API Access Issues**

1. Verify API is passed correctly to plugin constructor
2. Check API attributes exist before using them
3. Use hasattr() to safely check for API features

Debug Tools
----------

.. code-block:: python

   # Add to plugin for debugging
   def debug_plugin_state(self):
       """Debug plugin state"""
       print(f"Plugin active: {self.is_active}")
       print(f"Panel exists: {self.panel is not None}")
       print(f"API available: {self.api is not None}")
       
       if self.api:
           print(f"API has theme_manager: {hasattr(self.api, 'theme_manager')}")
           print(f"API has activity_manager: {hasattr(self.api, 'activity_manager')}")

Summary
======

Creating custom plugins for the PySide POEditor Plugin involves:

1. **Plugin Structure**: Create proper directory structure with __init__.py, plugin.py, panel.py
2. **Plugin Class**: Implement activate(), deactivate(), and get_activity_item() methods
3. **Panel Class**: Create UI panel inheriting from QWidget and PanelInterface
4. **API Integration**: Use Plugin API for core application services
5. **Registration**: Add plugin to AVAILABLE_PLUGINS list
6. **Testing**: Create comprehensive unit and integration tests
7. **Styling**: Add CSS for plugin components
8. **Icons**: Create active/inactive icon variants

**Key Points:**

* Follow the established plugin interface
* Use the Plugin API for all core interactions
* Handle activation and deactivation properly
* Create comprehensive tests
* Follow performance and architecture best practices

For additional information, see:

* :doc:`service_development_guide` - Creating plugin services
* :doc:`panel_development_guide` - Advanced panel development
* :doc:`css_development_guide` - Styling plugin components
* :doc:`/core/plugin_manager` - Plugin manager API reference
