Sidebar Manager
==============

.. automodule:: core.sidebar_manager
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Sidebar Manager is responsible for managing the application's sidebar, which contains the activity bar and content panels. It handles the creation, display, and switching of panels based on the selected activity.

Class Reference
-------------

SidebarManager
~~~~~~~~~~~~

Main class that manages the sidebar components:

.. code-block:: python

    class SidebarManager(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.activity_manager = None
            self.panel_container = None
            self.activity_bar = None
            self.panels = {}
            
        def setup(self, activity_manager, panel_container, activity_bar):
            """Set up the sidebar manager with required components."""
            self.activity_manager = activity_manager
            self.panel_container = panel_container
            self.activity_bar = activity_bar
            
            # Connect activity change signals
            self.activity_manager.activity_changed.connect(self._on_activity_changed)
            self.activity_bar.activity_clicked.connect(self._on_activity_bar_clicked)
            
        def register_panel(self, activity_id, panel):
            """Register a panel for an activity."""
            self.panels[activity_id] = panel
            self.panel_container.addWidget(panel)
            
        def _on_activity_changed(self, activity_id):
            """Handle activity change from the activity manager."""
            if activity_id in self.panels:
                self.panel_container.setCurrentWidget(self.panels[activity_id])
                self.activity_bar.set_active_activity(activity_id)
                
        def _on_activity_bar_clicked(self, activity_id):
            """Handle activity button click from the activity bar."""
            self.activity_manager.set_active_activity(activity_id)

SidebarActivityBar
~~~~~~~~~~~~~~~~

Simple activity bar implementation for basic sidebar functionality:

.. code-block:: python

    class SidebarActivityBar(QWidget):
        activity_clicked = Signal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.layout = QVBoxLayout()
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.setLayout(self.layout)
            
            # Activity buttons
            self.buttons = {}
            
        def add_activity(self, activity):
            """Add an activity button to the bar."""
            button = ActivityButton(
                activity.id, 
                activity.name,
                activity.active_icon,
                activity.inactive_icon
            )
            button.clicked.connect(lambda: self.activity_clicked.emit(activity.id))
            
            self.layout.addWidget(button)
            self.buttons[activity.id] = button
            
        def set_active_activity(self, activity_id):
            """Set the active activity button."""
            for id, button in self.buttons.items():
                button.set_active(id == activity_id)

Usage Examples
------------

Creating a Sidebar
~~~~~~~~~~~~~~~~

.. code-block:: python

    # In the main application
    from PySide6.QtWidgets import QMainWindow, QStackedWidget
    from core.sidebar_manager import SidebarManager, SidebarActivityBar
    from managers.activity_manager import ActivityManager
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Create components
            self.activity_manager = ActivityManager()
            self.panel_container = QStackedWidget()
            self.activity_bar = SidebarActivityBar()
            
            # Set up sidebar manager
            self.sidebar_manager = SidebarManager()
            self.sidebar_manager.setup(
                self.activity_manager,
                self.panel_container,
                self.activity_bar
            )
            
            # Layout components
            # ...

Adding Panels
~~~~~~~~~~~

.. code-block:: python

    # Register panels for activities
    explorer_panel = ExplorerPanel()
    search_panel = SearchPanel()
    
    sidebar_manager.register_panel("explorer", explorer_panel)
    sidebar_manager.register_panel("search", search_panel)
    
    # Set initial active activity
    activity_manager.set_active_activity("explorer")

Integration with Plugins
---------------------

The Sidebar Manager integrates with the plugin system to allow plugins to add their own panels:

.. code-block:: python

    # In a plugin's initialize method
    def initialize(self):
        # Create panel
        my_panel = MyCustomPanel()
        
        # Get services
        sidebar_manager = self.plugin_manager.get_service("sidebar_manager")
        activity_manager = self.plugin_manager.get_service("activity_manager")
        
        # Register activity and panel
        activity_manager.register_activity(my_activity)
        sidebar_manager.register_panel(my_activity.id, my_panel)
