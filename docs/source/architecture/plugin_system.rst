Plugin System
=============

.. raw:: html

   <div style="text-align: center; margin: 20px 0;">
      <img src="../_static/images/architecture_diagram.svg" alt="Plugin Architecture Diagram" style="width: 100%; max-width: 800px; height: auto;"/>
   </div>

Overview
--------

The POEditor Plugin application uses a sophisticated plugin-based architecture that provides extensibility and modularity. The system is built around a central plugin manager that coordinates activities, manages UI components, and provides services to plugin instances.

Architecture Components
-----------------------

Core Application Layer
~~~~~~~~~~~~~~~~~~~~~~

**MainAppWindow** serves as the application core, initializing and coordinating all system components:

- Initializes the plugin manager and core services
- Manages the main window layout and UI structure
- Provides the central coordination point for all subsystems

Plugin Management Layer
~~~~~~~~~~~~~~~~~~~~~~~

**Plugin Manager**
  Central coordinator for plugin discovery, loading, and lifecycle management

**Activity Manager**
  Manages activity registration, activation, and panel coordination

**Sidebar Manager**
  Handles sidebar layout, panel switching, and UI state management

**Tab Manager**
  Manages tabbed interfaces and content organization

Activity Configuration Layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ActivityConfig**
  Defines configuration for individual activities including:
  
  - Activity metadata (name, icon, description)
  - Panel class associations
  - Keyboard shortcuts and menu items
  - Plugin dependencies

**ActivityModel**
  Provides the data model for activities, handling:
  
  - Activity state management
  - Inter-activity communication
  - Event handling and notifications

**Panel Interface**
  Base interface that all panels must implement:
  
  - Standard panel lifecycle methods
  - UI integration points
  - Service access mechanisms

Core Activities
~~~~~~~~~~~~~~~

The system includes five core activities that provide essential functionality:

**Explorer Activity**
  - File system navigation and management
  - Directory tree view with filtering
  - File operations (copy, move, delete, rename)
  - Context menu integration

**Search Activity**  
  - File and content searching capabilities
  - Advanced search filters and patterns
  - Search result organization and navigation

**Preferences Activity**
  - Application settings and configuration
  - Theme selection and customization
  - Plugin management and configuration

**Extensions Activity**
  - Plugin discovery and installation
  - Extension marketplace integration
  - Plugin configuration and management

**Account Activity**
  - User profile management
  - Authentication and session handling
  - Cloud service integration

Plugin Structure
----------------

A plugin consists of:

* A plugin descriptor (plugin.py)
* Panel implementations
* Additional resources (icons, etc.)

Plugin Registration
-------------------

Plugins are registered with the core application through the ``PluginManager``:

.. code-block:: python

    class PluginManager:
        def register_plugin(self, plugin_id, plugin_instance):
            """Register a plugin with the application."""
            self.plugins[plugin_id] = plugin_instance
            
        def get_plugin(self, plugin_id):
            """Get a plugin instance by ID."""
            return self.plugins.get(plugin_id)

Plugin Discovery
----------------

The application scans the plugins directory at startup to discover and load available plugins:

.. code-block:: python

    def discover_plugins(self):
        """Discover and load plugins from the plugins directory."""
        for plugin_dir in os.listdir(self.plugins_path):
            if os.path.isdir(os.path.join(self.plugins_path, plugin_dir)):
                try:
                    self._load_plugin(plugin_dir)
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_dir}: {e}")

Data Flow Architecture
----------------------

.. raw:: html

   <div style="text-align: center; margin: 20px 0;">
      <img src="../_static/images/system_dataflow.svg" alt="System Data Flow Diagram" style="width: 100%; max-width: 800px; height: auto;"/>
   </div>

The plugin system follows a clear data flow pattern:

1. **User Interactions** → UI components capture user actions
2. **Application Core** → MainAppWindow routes requests to appropriate managers
3. **Plugin System** → Plugin Manager coordinates with Activity and Sidebar Managers
4. **Services System** → Core services handle business logic and data operations
5. **Activity Instances** → Individual plugins process requests and update UI
6. **Data Models & Widgets** → Support components manage state and UI elements
7. **Storage & External Systems** → Persistent storage and external API integration

Service Integration
-------------------

Plugins integrate with the service layer through well-defined APIs:

- **File Operations Service** for file system interactions
- **Theme Manager** for UI styling and theming
- **Undo/Redo Manager** for operation history
- **Icon Manager** for consistent iconography
- **CSS Manager** for dynamic styling

This architecture ensures that plugins can access core functionality while maintaining clean separation of concerns and enabling independent development and testing.

Plugin Lifecycle
--------------

1. **Discovery**: Plugin directories are discovered at startup
2. **Initialization**: Plugin instances are created
3. **Registration**: Plugins register their panels and activities
4. **Activation**: Plugins are activated when their functionality is needed
5. **Deactivation**: Plugins can be deactivated to free resources

Creating a Plugin
---------------

To create a new plugin:

1. Create a new directory in the `plugins` folder with your plugin name
2. Create a `plugin.py` file with a Plugin class:

   .. code-block:: python

       from core.plugin_manager import PluginBase
       
       class MyPlugin(PluginBase):
           def __init__(self):
               super().__init__("my_plugin", "My Plugin")
               
           def initialize(self):
               # Register panels, activities, etc.
               pass
               
           def shutdown(self):
               # Clean up resources
               pass

3. Create panel implementations as needed
4. Add your plugin to the application by placing it in the plugins directory

Plugin Communication
------------------

Plugins can communicate with the core application and other plugins through:

1. **Services**: Accessing shared services through the plugin manager
2. **Events**: Publishing and subscribing to application events
3. **Direct API**: Directly accessing APIs exposed by other plugins
