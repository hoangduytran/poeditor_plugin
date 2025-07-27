Plugin System
=============

Overview
-------

The POEditor Plugin application uses a plugin-based architecture to provide extensibility. Plugins can add new panels, activities, and functionality to the application.

Plugin Structure
--------------

A plugin consists of:

* A plugin descriptor (plugin.py)
* Panel implementations
* Additional resources (icons, etc.)

Plugin Registration
-----------------

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
--------------

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
