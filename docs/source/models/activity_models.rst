Activity Models
==============

.. automodule:: models.activity_models
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Activity Models module defines data structures for managing application activities, which are the primary components of the application's navigation system. Each activity represents a functional area of the application, such as Explorer, Search, or Extensions.

Class Reference
-------------

Activity
~~~~~~~

Base class for defining an application activity:

.. code-block:: python

    class Activity:
        def __init__(self, id, name, active_icon, inactive_icon, order=100):
            self.id = id
            self.name = name
            self.active_icon = active_icon
            self.inactive_icon = inactive_icon
            self.order = order
            
        def __lt__(self, other):
            """For sorting activities by order."""
            if isinstance(other, Activity):
                return self.order < other.order
            return NotImplemented

ActivityCollection
~~~~~~~~~~~~~~~

Collection for managing a set of activities:

.. code-block:: python

    class ActivityCollection:
        def __init__(self):
            self.activities = {}
            self.active_activity_id = None
            
        def add_activity(self, activity):
            """Add an activity to the collection."""
            self.activities[activity.id] = activity
            
        def remove_activity(self, activity_id):
            """Remove an activity from the collection."""
            if activity_id in self.activities:
                del self.activities[activity_id]
                
                # Reset active activity if it was removed
                if self.active_activity_id == activity_id:
                    self.active_activity_id = None
                    
        def get_activity(self, activity_id):
            """Get an activity by ID."""
            return self.activities.get(activity_id)
            
        def get_activities(self):
            """Get all activities, sorted by order."""
            return sorted(self.activities.values())
            
        def set_active_activity(self, activity_id):
            """Set the active activity."""
            if activity_id in self.activities:
                self.active_activity_id = activity_id
                return True
            return False
            
        def get_active_activity(self):
            """Get the active activity."""
            if self.active_activity_id:
                return self.get_activity(self.active_activity_id)
            return None

ActivityRegistry
~~~~~~~~~~~~~

Registry for accessing all application activities:

.. code-block:: python

    class ActivityRegistry:
        _instance = None
        
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = ActivityRegistry()
            return cls._instance
            
        def __init__(self):
            self.activities = ActivityCollection()
            
        def register_activity(self, activity):
            """Register an activity with the registry."""
            self.activities.add_activity(activity)
            
        def get_activity(self, activity_id):
            """Get an activity by ID."""
            return self.activities.get_activity(activity_id)
            
        def get_all_activities(self):
            """Get all registered activities."""
            return self.activities.get_activities()

Usage Examples
------------

Creating Activities
~~~~~~~~~~~~~~~~

.. code-block:: python

    from models.activity_models import Activity
    
    # Create an activity
    explorer_activity = Activity(
        id="explorer",
        name="Explorer",
        active_icon=":/icons/explorer_active.svg",
        inactive_icon=":/icons/explorer_inactive.svg",
        order=10  # Lower order means higher priority in UI
    )
    
    search_activity = Activity(
        id="search",
        name="Search",
        active_icon=":/icons/search_active.svg",
        inactive_icon=":/icons/search_inactive.svg",
        order=20
    )

Working with the Activity Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from models.activity_models import ActivityRegistry
    
    # Get the registry singleton
    registry = ActivityRegistry.instance()
    
    # Register activities
    registry.register_activity(explorer_activity)
    registry.register_activity(search_activity)
    
    # Get all activities, sorted by order
    all_activities = registry.get_all_activities()
    
    # Get a specific activity
    explorer = registry.get_activity("explorer")

Using Activity Collections
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from models.activity_models import ActivityCollection
    
    # Create a collection
    collection = ActivityCollection()
    
    # Add activities
    collection.add_activity(explorer_activity)
    collection.add_activity(search_activity)
    
    # Set active activity
    collection.set_active_activity("explorer")
    
    # Get active activity
    active = collection.get_active_activity()
    print(f"Active activity: {active.name}")

Integration with UI Components
---------------------------

Activities are typically used with UI components:

.. code-block:: python

    class ActivityBar(QWidget):
        activity_selected = Signal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            
            self.layout = QVBoxLayout()
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.setLayout(self.layout)
            
            self.buttons = {}
            
            # Add a stretch at the bottom to push buttons to the top
            self.layout.addStretch(1)
            
            # Add buttons for registered activities
            registry = ActivityRegistry.instance()
            for activity in registry.get_all_activities():
                self.add_activity_button(activity)
                
        def add_activity_button(self, activity):
            """Add a button for an activity."""
            button = QPushButton(self)
            button.setToolTip(activity.name)
            button.setCheckable(True)
            button.setIcon(QIcon(activity.inactive_icon))
            button.setProperty("activityId", activity.id)
            button.setProperty("activeIcon", activity.active_icon)
            button.setProperty("inactiveIcon", activity.inactive_icon)
            
            button.clicked.connect(
                lambda checked, aid=activity.id: self.activity_selected.emit(aid)
            )
            
            # Insert before the stretch
            self.layout.insertWidget(self.layout.count() - 1, button)
            self.buttons[activity.id] = button
            
        def set_active_activity(self, activity_id):
            """Set the active activity button."""
            for id, button in self.buttons.items():
                is_active = (id == activity_id)
                button.setChecked(is_active)
                
                # Update icon based on state
                if is_active:
                    icon_path = button.property("activeIcon")
                else:
                    icon_path = button.property("inactiveIcon")
                    
                button.setIcon(QIcon(icon_path))
