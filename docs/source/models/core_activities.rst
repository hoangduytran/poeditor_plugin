Core Activities
==============

.. automodule:: models.core_activities
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Core Activities module defines the standard activities available in the application by default. These include Explorer, Search, Extensions, Preferences, and Account activities. Each activity represents a functional area of the application and corresponds to a panel in the UI.

Class Reference
-------------

CoreActivities
~~~~~~~~~~~~

Class that provides access to core activity definitions:

.. code-block:: python

    class CoreActivities:
        """Defines the core activities for the application."""
        
        @classmethod
        def register_all(cls, registry):
            """Register all core activities with the registry."""
            registry.register_activity(cls.explorer())
            registry.register_activity(cls.search())
            registry.register_activity(cls.extensions())
            registry.register_activity(cls.preferences())
            registry.register_activity(cls.account())
            
        @staticmethod
        def explorer():
            """Explorer activity for file navigation."""
            return Activity(
                id="explorer",
                name="Explorer",
                active_icon=":/icons/explorer_active.svg",
                inactive_icon=":/icons/explorer_inactive.svg",
                order=10
            )
            
        @staticmethod
        def search():
            """Search activity for finding content."""
            return Activity(
                id="search",
                name="Search",
                active_icon=":/icons/search_active.svg",
                inactive_icon=":/icons/search_inactive.svg",
                order=20
            )
            
        @staticmethod
        def extensions():
            """Extensions activity for managing plugins."""
            return Activity(
                id="extensions",
                name="Extensions",
                active_icon=":/icons/extensions_active.svg",
                inactive_icon=":/icons/extensions_inactive.svg",
                order=30
            )
            
        @staticmethod
        def preferences():
            """Preferences activity for application settings."""
            return Activity(
                id="preferences",
                name="Preferences",
                active_icon=":/icons/preferences_active.svg",
                inactive_icon=":/icons/preferences_inactive.svg",
                order=40
            )
            
        @staticmethod
        def account():
            """Account activity for user profile and authentication."""
            return Activity(
                id="account",
                name="Account",
                active_icon=":/icons/account_active.svg",
                inactive_icon=":/icons/account_inactive.svg",
                order=50
            )

Usage Examples
------------

Registering Core Activities
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from models.core_activities import CoreActivities
    from models.activity_models import ActivityRegistry
    
    # Get the registry singleton
    registry = ActivityRegistry.instance()
    
    # Register all core activities
    CoreActivities.register_all(registry)
    
    # Or register individual activities
    registry.register_activity(CoreActivities.explorer())
    registry.register_activity(CoreActivities.search())

Accessing Core Activity Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from models.core_activities import CoreActivities
    
    # Get the explorer activity definition
    explorer_activity = CoreActivities.explorer()
    
    # Access activity properties
    print(f"ID: {explorer_activity.id}")
    print(f"Name: {explorer_activity.name}")
    print(f"Active Icon: {explorer_activity.active_icon}")
    print(f"Order: {explorer_activity.order}")

Integration with Application Startup
--------------------------------

Core activities are typically registered during application startup:

.. code-block:: python

    class Application:
        def __init__(self):
            # Create activity registry
            self.activity_registry = ActivityRegistry.instance()
            
            # Register core activities
            CoreActivities.register_all(self.activity_registry)
            
            # Set initial active activity
            self.activity_registry.activities.set_active_activity("explorer")
            
            # Create UI components
            self.main_window = MainWindow(self.activity_registry)
            self.main_window.show()

Customizing Core Activities
-----------------------

You can customize core activities by extending them:

.. code-block:: python

    from models.core_activities import CoreActivities
    from models.activity_models import Activity
    
    class CustomCoreActivities:
        @staticmethod
        def custom_explorer():
            """Custom explorer with different icons and order."""
            base_explorer = CoreActivities.explorer()
            return Activity(
                id=base_explorer.id,
                name="Files",  # Custom name
                active_icon=":/custom_icons/files_active.svg",
                inactive_icon=":/custom_icons/files_inactive.svg",
                order=5  # Custom order, higher priority
            )
            
        @staticmethod
        def register_custom(registry):
            """Register custom versions of core activities."""
            registry.register_activity(CustomCoreActivities.custom_explorer())
            # Register other standard activities
            registry.register_activity(CoreActivities.search())
            registry.register_activity(CoreActivities.extensions())
            # Skip preferences and account
            
    # Usage
    registry = ActivityRegistry.instance()
    CustomCoreActivities.register_custom(registry)
