=================================
POEditor Plugin Documentation
=================================

.. only:: html

   .. container:: intro-text

      Welcome to the POEditor Plugin documentation. This documentation covers all aspects of the 
      POEditor plugin, from user guides to technical reference materials for developers.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents

   overview/index
   architecture/index
   core/index
   services/index
   models/index
   panels/index
   plugins/index
   explorer/index

Getting Started
==============

.. container:: toc-cards

   .. container:: card

      **User Guides**
      
      Documentation for end users of the POEditor plugin.
      
      :doc:`/overview/index`

   .. container:: card

      **Developer Reference**
      
      Technical information for developers working with the POEditor plugin.
      
      :doc:`/architecture/index`

Main Features
============

.. container:: toc-cards

   .. container:: card

      .. figure:: /_static/images/file_explorer.svg
         :alt: File Explorer
         :width: 100%
         :figclass: align-center
         
         File Explorer

      **File Explorer**
      
      Navigate files and directories with the enhanced file explorer.
      
      :doc:`/explorer/explorer_context_menu`

   .. container:: card

      .. figure:: /_static/images/file_operations.svg
         :alt: File Operations
         :width: 100%
         :figclass: align-center
         
         File Operations

      **File Operations**
      
      Manage files with copy, move, delete and other operations.
      
      :doc:`/services/file_operations_service`

   .. container:: card

      .. figure:: /_static/images/themes.svg
         :alt: Themes
         :width: 100%
         :figclass: align-center
         
         Themes

      **Customizable Themes**
      
      Change the look and feel with different themes.
      
      :doc:`/services/theme_manager`

API References
=============

.. grid:: 3

   .. grid-item-card:: Core APIs
      :link: /core/api
      
      Application core functionality and interfaces

   .. grid-item-card:: Services
      :link: /services/index
      
      Service-layer components

   .. grid-item-card:: Models
      :link: /models/index
      
      Data models and structures

   .. grid-item-card:: UI Components
      :link: /widgets/index
      
      User interface components

   .. grid-item-card:: Panels
      :link: /panels/index
      
      Application panels and views

   .. grid-item-card:: Plugins
      :link: /plugins/index
      
      Plugin system and extensions

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
