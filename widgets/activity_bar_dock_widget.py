"""
Dockable widget wrapper for ActivityBar.

This module provides the ActivityBarDockWidget class, which wraps the ActivityBar
in a QDockWidget to enable docking functionality while preventing the activity bar
from being closed or hidden.
"""

from PySide6.QtWidgets import QDockWidget, QWidget, QMainWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from lg import logger
from widgets.activity_bar import ActivityBar


class ActivityBarDockWidget(QDockWidget):
    """
    Dockable wrapper for ActivityBar that cannot be closed.

    This widget wraps the ActivityBar in a QDockWidget to provide docking
    functionality while ensuring the activity bar remains always visible.
    It handles orientation changes and prevents accidental closing.

    Signals:
        position_changed: Emitted when dock position changes with the new dock area
    """

    position_changed = Signal(Qt.DockWidgetArea)

    def __init__(self, activity_bar: ActivityBar, parent: QWidget | None = None):
        """
        Initialize the dockable activity bar widget.

        Args:
            activity_bar: The ActivityBar widget to wrap
            parent: Parent widget (usually MainAppWindow)
        """
        super().__init__("Activity Bar", parent)

        # Store references
        self.activity_bar = activity_bar

        # Configure dock widget
        self.setup_dock_widget()

        # Set proper object name for CSS styling
        self.setObjectName("ActivityBarDock")

        # Set the activity bar as widget
        self.setWidget(self.activity_bar)

        logger.info("ActivityBarDockWidget initialized")

    def setup_dock_widget(self) -> None:
        """Configure dock widget properties."""
        try:
            # Allow moving and floating, but not closing
            features = (
                QDockWidget.DockWidgetFeature.DockWidgetMovable |
                QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            self.setFeatures(features)

            # Set size constraints
            self.setMinimumSize(48, 100)

            # Connect signals
            self.dockLocationChanged.connect(self.on_dock_location_changed)

            # Set initial properties
            self.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea |
                Qt.DockWidgetArea.RightDockWidgetArea |
                Qt.DockWidgetArea.TopDockWidgetArea |
                Qt.DockWidgetArea.BottomDockWidgetArea
            )

            logger.info("Dock widget configured successfully")

        except Exception as e:
            logger.error(f"Failed to setup dock widget: {e}")
            raise

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Prevent closing the dock widget.

        Args:
            event: The close event (will be ignored)
        """
        logger.debug("Activity bar close event ignored - cannot close activity bar")
        event.ignore()  # Always ignore close events

    def on_dock_location_changed(self, area: Qt.DockWidgetArea) -> None:
        """
        Handle dock location changes.

        Args:
            area: The new dock widget area
        """
        try:
            logger.info(f"Activity bar moved to area: {area}")

            # Emit position change signal
            self.position_changed.emit(area)

            # Update activity bar orientation if needed
            self.update_activity_bar_orientation(area)

        except Exception as e:
            logger.error(f"Failed to handle dock location change: {e}")

    def update_activity_bar_orientation(self, area: Qt.DockWidgetArea) -> None:
        """
        Update activity bar layout based on dock area.

        Args:
            area: The dock widget area
        """
        try:
            if area in (Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea):
                # Horizontal orientation for top/bottom
                self.activity_bar.set_horizontal_orientation()
                logger.debug("Activity bar set to horizontal orientation")
            else:
                # Vertical orientation for left/right
                self.activity_bar.set_vertical_orientation()
                logger.debug("Activity bar set to vertical orientation")

        except Exception as e:
            logger.error(f"Failed to update activity bar orientation: {e}")

    def get_activity_bar(self) -> ActivityBar:
        """
        Get the wrapped activity bar widget.

        Returns:
            The ActivityBar widget
        """
        return self.activity_bar

    def is_docked(self) -> bool:
        """
        Check if the activity bar is currently docked.

        Returns:
            True if docked, False if floating
        """
        return not self.isFloating()

    def get_dock_area(self) -> Qt.DockWidgetArea:
        """
        Get the current dock area.

        Returns:
            The current dock widget area, or NoDockWidgetArea if floating
        """
        parent = self.parent()
        if parent and isinstance(parent, QMainWindow):
            # Cast to QMainWindow to access dockWidgetArea
            main_window = parent
            return main_window.dockWidgetArea(self)
        return Qt.DockWidgetArea.NoDockWidgetArea
