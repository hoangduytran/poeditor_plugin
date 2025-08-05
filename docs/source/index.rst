=================================
POEditor Plugin Documentation
=================================

Welcome to the POEditor Plugin documentation. This documentation covers all
aspects of the POEditor plugin, from user guides to technical reference
materials for developers.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents

   overview/index
   guides/index
   architecture/index
   core/index
   services/index
   models/index
   panels/index
   plugins/index
   widgets/index
   explorer/index
   preferences/index
   testing/index

Getting Started
===============

* **User Guides** - Documentation for end users of the POEditor plugin →
  :doc:`/overview/index`

* **Developer Guides** - Step-by-step guides for CSS, icons, themes, and
  component development → :doc:`/guides/index`

* **Developer Reference** - Technical information and API reference for
  developers → :doc:`/architecture/index`

Main Features
=============

* **File Explorer** - Navigate files and directories with the enhanced file
  explorer → :doc:`/explorer/explorer_context_menu`

* **File Operations** - Manage files with copy, move, delete and other
  operations → :doc:`/services/file_operations_service`

* **Preferences System** - Comprehensive settings management with database
  persistence → :doc:`/preferences/index`

* **Customizable Themes** - Change the look and feel with different themes →
  :doc:`/services/theme_manager`

Architecture Overview
=====================

* **Plugin System** - Comprehensive plugin architecture with activity
  management → :doc:`/architecture/plugin_system`

* **Services Layer** - Service-oriented architecture for core functionality →
  :doc:`/architecture/services`

API References
===============

* **Core APIs** - Application core functionality and interfaces →
  :doc:`/core/api`

* **Preferences APIs** - Settings and preference management system →
  :doc:`/preferences/preferences_api_documentation`

* **Services** - Service-layer components → :doc:`/services/index`

* **Models** - Data models and structures → :doc:`/models/index`

* **UI Components** - User interface components → :doc:`/widgets/index`

* **Panels** - Application panels and views → :doc:`/panels/index`

* **Plugins** - Plugin system and extensions → :doc:`/plugins/index`

Components
==========

.. toctree::
   :maxdepth: 1
   :caption: Core Services

   services/file_numbering_service
   services/undo_redo_service
   services/file_operations_service
   services/drag_drop_service
   services/theme_manager

.. toctree::
   :maxdepth: 1
   :caption: Models

   models/file_system_models
   models/activity_models
   models/core_activities

.. toctree::
   :maxdepth: 1
   :caption: Core Components

   core/api
   core/directory_model
   core/explorer_settings
   core/file_filter
   core/plugin_manager
   core/sidebar_manager
   core/tab_manager

.. toctree::
   :maxdepth: 1
   :caption: Explorer Components

   widgets/enhanced_explorer_widget
   widgets/enhanced_file_view
   widgets/explorer_context_menu
   panels/enhanced_explorer_panel

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
