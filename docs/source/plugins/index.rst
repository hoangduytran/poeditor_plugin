Plugins
=======

This section documents the plugin system and available plugins in the POEditor Plugin application.

Plugin System Overview
----------------------

The POEditor Plugin uses an extensible plugin architecture that allows adding new functionality through custom plugins. The plugin system provides:

* **Activity Management** - Plugins can register new activities and panels
* **Service Integration** - Access to core application services
* **Event Handling** - Plugin lifecycle and application event hooks
* **UI Extension** - Add custom panels, menus, and interface elements

For detailed information about developing plugins, see the :doc:`../guides/plugin_development_guide`.

For the core plugin system architecture, see :doc:`../architecture/plugin_system`.

Available Plugin APIs
---------------------

* **Core Plugin API** - :doc:`../core/api` - Base interfaces for plugin development
* **Plugin Manager** - :doc:`../core/plugin_manager` - Plugin registration and lifecycle management
* **Sidebar Manager** - :doc:`../core/sidebar_manager` - Activity and panel coordination

.. toctree::
   :maxdepth: 2
   :hidden:
