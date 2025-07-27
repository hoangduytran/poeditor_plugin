Plugin Manager
=============

.. automodule:: core.plugin_manager
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Plugin Manager is a core component that handles plugin discovery, registration, and lifecycle management. It provides a central point for plugins to register themselves and access shared services.

Class Reference
-------------

PluginBase
~~~~~~~~~

Base class for plugins to extend:

.. code-block:: python

    class PluginBase:
        def __init__(self, plugin_id, name):
            self.plugin_id = plugin_id
            self.name = name
            
        def initialize(self):
            """Called when the plugin is initialized."""
            pass
            
        def shutdown(self):
            """Called when the plugin is being shut down."""
            pass

PluginManager
~~~~~~~~~~~

Singleton class that manages all plugins:

.. code-block:: python

    class PluginManager:
        _instance = None
        
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = PluginManager()
            return cls._instance
            
        def __init__(self):
            self.plugins = {}
            self.services = {}
            
        def register_plugin(self, plugin_id, plugin):
            """Register a plugin with the manager."""
            self.plugins[plugin_id] = plugin
            
        def get_plugin(self, plugin_id):
            """Get a plugin by ID."""
            return self.plugins.get(plugin_id)
            
        def register_service(self, service_id, service):
            """Register a service with the manager."""
            self.services[service_id] = service
            
        def get_service(self, service_id):
            """Get a service by ID."""
            return self.services.get(service_id)

Usage Examples
------------

Registering a Plugin
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # In a plugin's __init__.py
    from core.plugin_manager import PluginBase, PluginManager
    
    class MyPlugin(PluginBase):
        def __init__(self):
            super().__init__("my_plugin", "My Plugin")
            
        def initialize(self):
            # Plugin initialization code
            pass
    
    # Register the plugin
    plugin_manager = PluginManager.instance()
    plugin_manager.register_plugin("my_plugin", MyPlugin())

Registering a Service
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Create and register a service
    my_service = MyServiceClass()
    plugin_manager = PluginManager.instance()
    plugin_manager.register_service("my_service", my_service)

Accessing a Service
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get a service by ID
    plugin_manager = PluginManager.instance()
    file_operations = plugin_manager.get_service("file_operations")
    
    # Use the service
    file_operations.copy_to_clipboard(["/path/to/file.txt"])

Plugin Discovery
--------------

The plugin manager discovers plugins by scanning the `plugins` directory:

.. code-block:: python

    def discover_plugins(self):
        """Discover and load plugins from the plugins directory."""
        plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
        
        for item in os.listdir(plugins_dir):
            plugin_dir = os.path.join(plugins_dir, item)
            if os.path.isdir(plugin_dir):
                try:
                    self._load_plugin(plugin_dir)
                except Exception as e:
                    logger.error(f"Failed to load plugin {item}: {e}")

Plugin Loading
------------

Plugins are loaded by importing their `plugin.py` file:

.. code-block:: python

    def _load_plugin(self, plugin_dir):
        """Load a plugin from its directory."""
        plugin_file = os.path.join(plugin_dir, "plugin.py")
        
        if os.path.exists(plugin_file):
            spec = importlib.util.spec_from_file_location("plugin", plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "initialize_plugin"):
                module.initialize_plugin(self)
