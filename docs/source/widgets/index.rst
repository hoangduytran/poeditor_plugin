Widgets
=======

This section documents all the UI widgets used in the POEditor Plugin application.

.. toctree::
   :maxdepth: 2

   simple_explorer
   enhanced_explorer_widget
   enhanced_file_view
   explorer_context_menu

Overview
--------

The widgets provide reusable UI components throughout the application:

Explorer Widgets
~~~~~~~~~~~~~~~~

**File System Navigation**
  :doc:`simple_explorer` - Basic file system explorer widget
  :doc:`enhanced_explorer_widget` - Advanced file explorer with enhanced
  features
  :doc:`enhanced_file_view` - Enhanced file view component with custom styling
  → Related: :doc:`../panels/enhanced_explorer_panel`,
  :doc:`../core/directory_model`

**Context Menu Systems**
  :doc:`explorer_context_menu` - Context menu for file operations
  → Related: :doc:`../services/file_operations_service`,
  :doc:`../explorer/explorer_context_menu`

Widget Integration
------------------

Widgets integrate with other application components:

* **Core Components** → :doc:`../core/index` - Core managers coordinate widgets
* **Services Layer** → :doc:`../services/index` - Widgets use application
  services
* **Panels** → :doc:`../panels/index` - Panels contain and organize widgets
* **Models** → :doc:`../models/index` - Widgets display and manipulate
  model data

Development
-----------

For widget development guidance:

* :doc:`../guides/component_styling_guide` - Styling custom widgets
* :doc:`../guides/css_development_guide` - CSS development for widgets
* :doc:`../guides/panel_development_guide` - Integrating widgets into panels
* :doc:`../architecture/css_system` - Understanding the styling architecture
