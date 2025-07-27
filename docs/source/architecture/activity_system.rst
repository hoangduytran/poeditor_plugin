Activity System
==============

Overview
--------

The Activity System provides a way to organize and switch between different user interfaces and functionality modes in the application. Activities are represented by icons in the Activity Bar and corresponding panels in the sidebar.

Components
---------

The Activity System consists of several components:

1. **Activity Models**: Data structures that define activities
2. **Activity Manager**: Service that manages activity registration and selection
3. **Activity Bar**: UI component that displays activity buttons
4. **Activity Panels**: Content panels that provide functionality for each activity

Activity Model
------------

Activities are defined by the ``ActivityModel`` class:

.. code-block:: python

    class ActivityModel:
        def __init__(self, id, name, active_icon, inactive_icon, panel_class):
            self.id = id
            self.name = name
            self.active_icon = active_icon
            self.inactive_icon = inactive_icon
            self.panel_class = panel_class

Core Activities
-------------

The application provides several core activities:

* **Explorer**: File navigation and management
* **Search**: Text search across files
* **Account**: User account management
* **Extensions**: Manage application extensions
* **Preferences**: Application settings

These are defined in ``models.core_activities``:

.. code-block:: python

    EXPLORER_ACTIVITY = ActivityModel(
        "explorer",
        "Explorer",
        ":/icons/explorer_active.svg",
        ":/icons/explorer_inactive.svg",
        ExplorerPanel
    )
    
    SEARCH_ACTIVITY = ActivityModel(
        "search",
        "Search",
        ":/icons/search_active.svg",
        ":/icons/search_inactive.svg",
        SearchPanel
    )
    
    # ... other activities

Activity Manager
--------------

The ``ActivityManager`` handles:

1. Registering activities from core and plugins
2. Switching between activities
3. Maintaining the current activity state

.. code-block:: python

    class ActivityManager:
        def register_activity(self, activity):
            """Register a new activity."""
            self.activities[activity.id] = activity
            self.activity_added.emit(activity)
            
        def set_active_activity(self, activity_id):
            """Set the active activity by ID."""
            if activity_id in self.activities:
                self.active_activity = activity_id
                self.activity_changed.emit(activity_id)

Adding Custom Activities
----------------------

Plugins can add custom activities to the application:

.. code-block:: python

    # In a plugin's initialize method
    def initialize(self):
        custom_activity = ActivityModel(
            "my_activity",
            "My Activity",
            ":/plugins/my_plugin/active.svg",
            ":/plugins/my_plugin/inactive.svg",
            MyCustomPanel
        )
        
        activity_manager = self.plugin_manager.get_service("activity_manager")
        activity_manager.register_activity(custom_activity)
