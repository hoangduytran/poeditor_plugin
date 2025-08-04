Core Components
===============

This section covers the core components that form the foundation of the POEditor Plugin application.

.. toctree::
   :maxdepth: 2

   api
   directory_model
   explorer_settings
   file_filter
   plugin_manager
   sidebar_manager
   tab_manager

Overview
--------

The core components provide fundamental functionality for the application:

**Application Programming Interface**
  :doc:`api` - Base interfaces and contracts for plugin development
  → Related: :doc:`../guides/plugin_development_guide`

**Data Models**
  :doc:`directory_model` - File system directory representation
  → Related: :doc:`../models/file_system_models`

**Configuration Management**
  :doc:`explorer_settings` - Explorer-specific configuration and preferences
  :doc:`file_filter` - File filtering and search functionality
  → Related: :doc:`../services/index`

**System Managers**
  :doc:`plugin_manager` - Plugin discovery, loading, and lifecycle management
  → Related: :doc:`../architecture/plugin_system`,
  :doc:`../guides/plugin_development_guide`

  :doc:`sidebar_manager` - Sidebar layout, panel switching, and UI state
  management → Related: :doc:`../panels/index`,
  :doc:`../architecture/activity_system`

  :doc:`tab_manager` - Tabbed interface and content organization
  → Related: :doc:`../widgets/index`

Architecture Integration
------------------------

These core components integrate with other system layers:

* **Services Layer** → :doc:`../services/index` - Core services utilize
  these managers
* **Plugin System** → :doc:`../architecture/plugin_system` - Plugins interact
  through these APIs
* **UI Components** → :doc:`../widgets/index` - UI components depend on
  core managers
* **Data Models** → :doc:`../models/index` - Core components use application
  data models
