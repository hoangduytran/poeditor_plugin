Models
======

Data models and structures used throughout the POEditor Plugin application.

.. toctree::
   :maxdepth: 2
   
   activity_models
   core_activities
   file_system_models

Overview
--------

The models layer provides data structures and business objects for the
application:

Activity and Plugin Models
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Activity Management**
  :doc:`activity_models` - Data models for activity states and configuration
  :doc:`core_activities` - Core activity definitions and metadata
  → Related: :doc:`../architecture/activity_system`,
  :doc:`../core/plugin_manager`

**File System Models**
  :doc:`file_system_models` - File and directory representation models
  → Related: :doc:`../core/directory_model`,
  :doc:`../services/file_operations_service`

Model Integration
-----------------

Models integrate with other application components:

* **Core Components** → :doc:`../core/index` - Core managers use data models
* **Services Layer** → :doc:`../services/index` - Services operate on
  model data
* **UI Components** → :doc:`../widgets/index` - UI components display
  model data
* **Plugin System** → :doc:`../architecture/plugin_system` - Plugins access
  models

Development
-----------

For model development guidance:

* :doc:`../guides/service_development_guide` - Working with data models
* :doc:`../architecture/index` - Understanding data flow architecture
