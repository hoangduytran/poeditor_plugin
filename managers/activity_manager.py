"""
Activity Manager for managing activities and panels.

This module defines the ActivityManager class, which manages the registration,
activation, and state of activities and their corresponding panels.
"""

from lg import logger
from typing import Dict, Optional, List, Callable, Type
import importlib

# Import activity bar types for proper type checking
from widgets.activity_bar import ActivityBar
from core.sidebar_manager import SidebarManager

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from models.activity_models import ActivityConfig, ActivityState, DEFAULT_ACTIVITY_CONFIG
from widgets.activity_button import ActivityButton


class ActivityManager(QObject):
    """Manages activity registration and coordination.

    The ActivityManager handles registering activities, creating their
    panels, and managing the state and visibility of panels.

    Signals:
        activity_changed: Emitted when the active activity changes,
                          with old_id and new_id
    """
    activity_changed = Signal(object, object)  # old_id, new_id (can be str or None)

    def __init__(self, api, activity_bar=None, panel_container=None):
        """Initialize the activity manager.

        Args:
            api: The plugin API instance
            activity_bar: The activity bar widget
            panel_container: The container for panels
        """
        super().__init__()

        # Initialize attributes directly to avoid hasattr/getattr
        self.api = api
        self.activities: Dict[str, ActivityConfig] = {}
        self.panels: Dict[str, QWidget] = {}
        self.current_activity_id: Optional[str] = None
        self.panel_classes: Dict[str, Type[QWidget]] = {}
        self.current_panel: Optional[QWidget] = None
        self.activity_bar = activity_bar
        self.panel_container = panel_container
        self.active_panel_id = None

        # Initialize state object
        from models.activity_models import ActivityState
        self.state = ActivityState()
        # Override default "explorer" with None for fresh start
        self.state.active_activity = None

        # Connect signals if activity_bar is provided
        if self.activity_bar:
            self.activity_bar.panel_requested.connect(self._handle_panel_request)

    def _handle_panel_request(self, activity_id):
        """Handle a request to show a panel for an activity.

        Args:
            activity_id: The ID of the activity to show
        """
        logger.info(f"Panel requested for activity: {activity_id}")

        if activity_id == self.current_activity_id:
            # Toggle the panel if already active
            self._toggle_panel(activity_id)
        else:
            # Show the panel
            self._toggle_panel(activity_id)

        # Update the active button in activity bar if available
        if self.activity_bar:
            # Try different activity bar interfaces in order of preference
            try:
                # Main ActivityBar implementation
                self.activity_bar.set_active_activity(self.current_activity_id or "")
            except AttributeError:
                try:
                    # SidebarActivityBar implementation
                    self.activity_bar.set_active_panel(self.current_activity_id or "")
                except AttributeError:
                    logger.warning(f"ActivityBar type {type(self.activity_bar)} has unknown interface")

    def _toggle_panel(self, activity_id):
        """Toggle a panel visibility.

        Args:
            activity_id: The ID of the activity panel to toggle
        """
        # If panel is already active, hide it
        if activity_id == self.current_activity_id and self.current_panel:
            logger.info(f"Hiding panel: {activity_id}")
            self.current_panel.hide()
            self.current_panel = None
            self.current_activity_id = None
            self.active_panel_id = None
            return

        # Get or create the panel
        if activity_id not in self.panels:
            # Only create if we have the activity config
            if activity_id not in self.activities:
                logger.error(f"Activity not registered: {activity_id}")
                return

            panel = self._create_panel(activity_id)
            if not panel:
                logger.error(f"Could not create panel for activity: {activity_id}")
                return

            self.panels[activity_id] = panel

        # Hide the current panel
        if self.current_panel:
            self.current_panel.hide()

        # Show the new panel
        panel = self.panels[activity_id]
        if self.panel_container and panel.parent() != self.panel_container:
            panel.setParent(self.panel_container)

        panel.show()
        self.current_panel = panel

        # Update current activity ID
        old_activity_id = self.current_activity_id
        self.current_activity_id = activity_id
        self.active_panel_id = activity_id

        # Emit signal
        self.activity_changed.emit(old_activity_id or "", activity_id)
        logger.info(f"Switched to activity: {activity_id}")

    def _create_panel(self, activity_id, panel_class_name=None):
        """Create a panel instance for an activity.

        Args:
            activity_id: The ID of the panel
            panel_class_name: The class name of the panel (optional, will use activity config if not provided)

        Returns:
            The created panel or None if creation failed
        """
        try:
            # If no panel_class_name provided, get it from activity config
            if panel_class_name is None:
                if activity_id in self.activities:
                    panel_class_name = self.activities[activity_id].panel_class
                else:
                    logger.error(f"Activity not registered: {activity_id}")
                    return None

            # Import the panel class
            panel_class = self._import_panel_class(panel_class_name)
            if not panel_class:
                logger.error(f"Could not import panel class: {panel_class_name}")
                return None

            # Create the panel instance
            panel = panel_class(self.panel_container, activity_id)

            # Set API if the panel has a set_api method
            try:
                panel.set_api(self.api)
            except AttributeError:
                # Panel doesn't have set_api method, that's ok
                pass

            # Hide initially
            panel.hide()

            logger.info(f"Created panel: {activity_id} using class: {panel_class_name}")
            return panel

        except Exception as e:
            logger.error(f"Error creating panel: {e}")
            return None

    def register_activity(self, activity_config):
        """Register an activity with the manager.

        Args:
            activity_config: The activity configuration
        """
        # Validate activity config
        if not activity_config.id:
            logger.error("ActivityConfig missing id attribute")
            return

        # Store the activity config
        self.activities[activity_config.id] = activity_config

        # Add button to the activity bar if available
        if self.activity_bar:
            try:
                # Use the ActivityBar's add_activity_button method
                self.activity_bar.add_activity_button(activity_config)
                logger.info(f"Added activity button: {activity_config.id}")
            except Exception as e:
                logger.error(f"Error adding activity button: {e}")

        logger.info(f"Registered activity: {activity_config.id}")

        # Emit event for activity registration
        # API is initialized in __init__, so we can directly use it
        try:
            self.api.emit_event("activity.registered", activity_id=activity_config.id)
        except AttributeError:
            # If api or emit_event doesn't exist, just skip it
            pass

    def _import_panel_class(self, class_name):
        """Import a panel class by name.

        Args:
            class_name: The name of the class to import (can be full module path or just class name)

        Returns:
            The imported class or None if import failed
        """
        try:
            # Handle full module path like "panels.explorer_panel.ExplorerPanel"
            if "." in class_name:
                parts = class_name.split(".")
                module_path = ".".join(parts[:-1])  # panels.explorer_panel
                class_name_only = parts[-1]  # ExplorerPanel

                try:
                    module = importlib.import_module(module_path)
                    try:
                        panel_class = module.__dict__[class_name_only]
                        logger.info(f"Successfully imported real panel: {class_name}")
                        return panel_class
                    except KeyError:
                        logger.warning(f"Class {class_name_only} not found in module {module_path}")
                except ImportError as e:
                    logger.warning(f"Failed to import module {module_path}: {e}")

            # Try various possible modules for the panel (fallback for class name only)
            possible_modules = [
                f"panels.{class_name.lower()}",  # panels.explorerpanel
                "panels." + class_name[0].lower() + class_name[1:],  # panels.explorerPanel
                f"panels.{class_name.replace('Panel', '').lower()}_panel"  # panels.explorer_panel
            ]

            for module_name in possible_modules:
                try:
                    module = importlib.import_module(module_name)
                    try:
                        return module.__dict__[class_name]
                    except KeyError:
                        # Class not found in this module
                        pass
                except ImportError:
                    pass

            # If not found, try the base panels module
            try:
                module = importlib.import_module("panels")
                try:
                    return module.__dict__[class_name]
                except KeyError:
                    # Class not found in this module
                    pass
            except ImportError:
                pass

            # Return the mock panel class for testing
            from PySide6.QtWidgets import QLabel, QVBoxLayout

            class MockPanel(QWidget):
                def __init__(self, parent=None, panel_id=None):
                    super().__init__(parent)
                    self.panel_id = panel_id
                    layout = QVBoxLayout(self)
                    label = QLabel(f"Mock Panel: {panel_id}", self)
                    layout.addWidget(label)

                def set_api(self, api):
                    pass

            logger.warning(f"Using mock panel for: {class_name}")
            return MockPanel

        except Exception as e:
            logger.error(f"Error importing panel class: {e}")
            return None

        # Load configuration
        self.config = DEFAULT_ACTIVITY_CONFIG
        self.state = ActivityState()

        logger.info("ActivityManager initialized")

    def set_panel_container(self, container: QWidget) -> None:
        """Set the container widget for panels.

        Args:
            container: The widget that will contain panels
        """
        self.panel_container = container
        logger.info("Panel container set")

    # The register_activity implementation was consolidated with the version above

    def register_panel_class(self, activity_id: str, panel_class: Type[QWidget]) -> None:
        """Register a panel class for an activity.

        Args:
            activity_id: ID of the activity
            panel_class: Class to instantiate for the panel
        """
        if activity_id not in self.activities:
            logger.error(f"Cannot register panel class for unknown activity: {activity_id}")
            return

        self.panel_classes[activity_id] = panel_class
        logger.info(f"Registered panel class for activity: {activity_id}")

    def unregister_activity(self, activity_id: str) -> None:
        """Unregister an activity.

        Args:
            activity_id: ID of the activity to unregister
        """
        if activity_id not in self.activities:
            logger.warning(f"Activity {activity_id} not found for unregistration")
            return

        # Clean up panel if it exists
        if activity_id in self.panels:
            panel = self.panels[activity_id]
            panel.hide()
            panel.deleteLater()
            del self.panels[activity_id]

        # Remove from registry
        del self.activities[activity_id]

        # Remove from panel classes
        if activity_id in self.panel_classes:
            del self.panel_classes[activity_id]

        logger.info(f"Unregistered activity: {activity_id}")

        # Emit event for activity unregistration
        self.api.emit_event("activity.unregistered", {
            "activity_id": activity_id
        })

    def activate_panel(self, activity_id: str) -> None:
        """Activate an activity panel.

        Args:
            activity_id: ID of the activity to activate
        """
        if activity_id not in self.activities:
            logger.error(f"Cannot activate unknown activity: {activity_id}")
            return

        if not self.panel_container:
            logger.error("Cannot activate panel: no panel container set")
            return

        old_activity_id = self.current_activity_id

        # Toggle behavior: if clicking the same activity, deactivate it
        if self.current_activity_id == activity_id:
            # Deactivate current panel
            if self.current_panel:
                self.current_panel.hide()
                self.current_panel = None

            # Update state
            self.current_activity_id = None
            self.active_panel_id = None
            self.state.active_activity = None
            self.state.panel_visible = False

            # Emit signal for deactivation
            self.activity_changed.emit(old_activity_id, None)
            logger.info(f"Deactivated activity: {activity_id}")

            # Emit event
            self.api.emit_event("activity.changed",
                old_activity_id=old_activity_id,
                new_activity_id=None,
                panel=None
            )
            return

        # Activate different panel
        self.current_activity_id = activity_id

        # Hide current panel
        if self.current_panel:
            self.current_panel.hide()

        # Create panel if it doesn't exist
        if activity_id not in self.panels:
            panel = self._create_panel(activity_id)
            if panel:
                self.panels[activity_id] = panel

        # Show panel
        if activity_id in self.panels:
            panel = self.panels[activity_id]
            panel.show()
            self.current_panel = panel

            # Update state consistently
            self.state.active_activity = activity_id
            self.state.panel_visible = True
            self.active_panel_id = activity_id  # Make sure this is set for consistency

            # Emit signal
            self.activity_changed.emit(old_activity_id, activity_id)
            logger.info(f"Activated activity: {activity_id}")

            # Emit event
            self.api.emit_event("activity.changed",
                old_activity_id=old_activity_id,
                new_activity_id=activity_id,
                panel=panel
            )

    # The _create_panel implementation was consolidated with the version above

    def get_current_activity(self) -> str:
        """Get the ID of the current activity.

        Returns:
            The current activity ID, or empty string if none active
        """
        return self.current_activity_id or ""

    def get_activity_config(self, activity_id: str) -> Optional[ActivityConfig]:
        """Get the configuration for an activity.

        Args:
            activity_id: ID of the activity

        Returns:
            The activity configuration, or None if not found
        """
        return self.activities.get(activity_id)

    def get_all_activities(self) -> List[ActivityConfig]:
        """Get all registered activities.

        Returns:
            List of all activity configurations
        """
        return list(self.activities.values())

    def hide_current_panel(self) -> None:
        """Hide the current panel."""
        if self.current_panel:
            self.current_panel.hide()
            self.state.panel_visible = False
            logger.info(f"Hidden panel for activity: {self.current_activity_id}")

    def show_current_panel(self) -> None:
        """Show the current panel."""
        if self.current_panel:
            self.current_panel.show()
            self.state.panel_visible = True
            logger.info(f"Shown panel for activity: {self.current_activity_id}")

    def toggle_current_panel(self) -> None:
        """Toggle visibility of the current panel."""
        if self.current_panel:
            if self.current_panel.isVisible():
                self.hide_current_panel()
            else:
                self.show_current_panel()

    def save_state(self) -> None:
        """Save the current state of activities and panels."""
        # TODO: Implement saving state to configuration
        pass

    def load_state(self) -> None:
        """Load saved state of activities and panels."""
        # TODO: Implement loading state from configuration
        pass
