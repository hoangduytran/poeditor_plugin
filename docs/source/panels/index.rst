Panels
======

This section documents all the side panels used in the POEditor Plugin application.

.. toctree::
   :maxdepth: 2

   enhanced_explorer_panel

Overview
--------

Panels provide organized content areas in the application sidebar:

Explorer Panels
~~~~~~~~~~~~~~~

**File Management**
  :doc:`enhanced_explorer_panel` - Advanced file explorer panel with context
  menus, drag-and-drop, and enhanced file operations
  → Related: :doc:`../widgets/enhanced_explorer_widget`,
  :doc:`../services/file_operations_service`

Panel Integration
-----------------

Panels integrate with the application architecture:

* **Core Management** → :doc:`../core/sidebar_manager` - Sidebar manager
  coordinates panel display
* **Activity System** → :doc:`../architecture/activity_system` - Activity
  system manages panel activation
* **Plugin System** → :doc:`../architecture/plugin_system` - Plugins can
  register custom panels
* **Widget Components** → :doc:`../widgets/index` - Panels contain and organize
  widget components

Development
-----------

For panel development guidance:

* :doc:`../guides/panel_development_guide` - Creating custom panels
* :doc:`../guides/component_styling_guide` - Styling panel components
* :doc:`../core/sidebar_manager` - Understanding panel management
* :doc:`../architecture/activity_system` - Panel activation and coordination
