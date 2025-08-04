Services
========

Core application services providing business logic and data operations.

.. toctree::
   :maxdepth: 2
   
   theme_manager
   css_file_based_theme_manager
   css_preprocessor
   css_cache_optimizer
   icon_preprocessor
   file_operations_service
   file_numbering_service
   undo_redo_service
   drag_drop_service

Overview
--------

The services layer provides reusable business logic and data operations:

Theme and Styling Services
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Theme Management**
  :doc:`theme_manager` - Core theme management and switching functionality
  :doc:`css_file_based_theme_manager` - File-based CSS theme loading system
  → Related: :doc:`../architecture/theme_system`,
  :doc:`../guides/theme_creation_guide`

**CSS Processing**
  :doc:`css_preprocessor` - CSS variable processing and compilation
  :doc:`css_cache_optimizer` - CSS caching and performance optimization
  → Related: :doc:`../architecture/css_system`,
  :doc:`../guides/css_development_guide`

**Icon Management**
  :doc:`icon_preprocessor` - Icon processing and SVG optimization
  → Related: :doc:`../guides/icon_development_guide`

File and Data Services
~~~~~~~~~~~~~~~~~~~~~~

**File Operations**
  :doc:`file_operations_service` - File system operations with undo/redo
  support
  :doc:`file_numbering_service` - Automatic file numbering and organization
  :doc:`drag_drop_service` - Drag and drop functionality for file management
  → Related: :doc:`../panels/enhanced_explorer_panel`,
  :doc:`../widgets/enhanced_explorer_widget`

**History Management**
  :doc:`undo_redo_service` - Comprehensive undo/redo operation tracking
  → Related: :doc:`../core/plugin_manager`

Service Integration
-------------------

Services integrate with other application layers:

* **Core Components** → :doc:`../core/index` - Core managers coordinate
  services
* **Plugin System** → :doc:`../architecture/plugin_system` - Plugins access
  services
* **UI Components** → :doc:`../widgets/index` - UI components use service
  functionality
* **Architecture** → :doc:`../architecture/services` - Service layer design
  patterns

Development Guides
-------------------

For service development guidance:

* :doc:`../guides/service_development_guide` - Creating new services
* :doc:`../guides/css_development_guide` - CSS service development
* :doc:`../guides/theme_creation_guide` - Theme service usage
