"""
Unified Sidebar Dock Widget for the POEditor application.

This module provides a QDockWidget wrapper for the unified sidebar frame,
ensuring that the activity bar and sidebar panels move together as one unit
during docking operations while preventing the activity bar from being closed.
"""

from typing import Optional
from PySide6.QtWidgets import QDockWidget, QWidget, QMainWindow
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QCloseEvent
from lg import logger

from widgets.unified_sidebar_frame import UnifiedSidebarFrame


class UnifiedSidebarDockWidget(QDockWidget):
    """
    Dockable widget wrapper for the unified sidebar frame.

    This dock widget ensures that:
    - The activity bar and sidebar panels move together as one unit
    - The activity bar cannot be closed (dock widget cannot be closed)
    - The sidebar panels can be collapsed within the dock widget
    - Proper orientation handling for different dock positions
    """

    # Signals
    dock_position_changed = Signal(Qt.DockWidgetArea)
    panels_visibility_changed = Signal(bool)

    def __init__(self, unified_frame: UnifiedSidebarFrame, parent: Optional[QWidget] = None):
        super().__init__("Sidebar", parent)

        self.unified_frame = unified_frame
        self._current_dock_area = Qt.DockWidgetArea.LeftDockWidgetArea

        self.setup_dock_widget()
        self.connect_signals()
        logger.info("UnifiedSidebarDockWidget initialized")

    def setup_dock_widget(self) -> None:
        """Configure the dock widget properties."""
        # Set the unified frame as the widget content
        self.setWidget(self.unified_frame)

        # Configure dock widget features
        # Allow moving and floating, but prevent closing
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            # Notably, NOT including DockWidgetClosable
        )

        # Set object name for settings persistence
        self.setObjectName("UnifiedSidebarDock")

        # Configure title bar
        self.setWindowTitle("Sidebar")

        # Size constraints
        self.setMinimumWidth(self.unified_frame.get_minimum_width())
        self.setMaximumWidth(500)  # Reasonable maximum width

        # Disable context menu that might allow closing
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

    def connect_signals(self) -> None:
        """Connect internal signals and dock widget events."""
        # Connect to dock widget area changes
        self.dockLocationChanged.connect(self._on_dock_location_changed)

        # Connect unified frame signals to pass through
        self.unified_frame.panel_visibility_changed.connect(self.panels_visibility_changed.emit)
        self.unified_frame.dock_position_changed.connect(self.dock_position_changed.emit)

    def _on_dock_location_changed(self, area: Qt.DockWidgetArea) -> None:
        """Handle dock widget area changes."""
        logger.info(f"Unified sidebar dock moved to area: {area}")
        self._current_dock_area = area

        # Update the unified frame for the new position
        self.unified_frame.update_for_dock_position(area)

        # Update size constraints based on dock position
        self._update_size_constraints_for_area(area)

        # Emit signal for external components
        self.dock_position_changed.emit(area)

    def _update_size_constraints_for_area(self, area: Qt.DockWidgetArea) -> None:
        """Update size constraints based on dock area."""
        if area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
            # Horizontal docking - constrain width
            self.setMinimumWidth(self.unified_frame.get_minimum_width())
            self.setMaximumWidth(500)
            self.setMinimumHeight(100)
            self.setMaximumHeight(9999)
        elif area in (Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea):
            # Vertical docking - constrain height
            self.setMinimumHeight(100)
            self.setMaximumHeight(300)
            self.setMinimumWidth(200)
            self.setMaximumWidth(9999)
        else:
            # Floating - allow flexible sizing
            self.setMinimumWidth(self.unified_frame.get_minimum_width())
            self.setMaximumWidth(600)
            self.setMinimumHeight(150)
            self.setMaximumHeight(800)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Override close event to prevent the dock widget from being closed.

        This is a critical safety measure to ensure the activity bar is never hidden.
        """
        logger.warning("Attempted to close unified sidebar dock widget - ignoring")
        event.ignore()  # Prevent closing

        # Instead of closing, just hide the panels if they're visible
        if self.unified_frame.are_panels_visible():
            self.unified_frame.hide_panels()

    def event(self, event: QEvent) -> bool:
        """Override event handling to prevent unwanted closing."""
        # Block any events that might try to hide or close the dock widget
        if event.type() == QEvent.Type.Hide:
            logger.warning("Attempted to hide unified sidebar dock widget - preventing")
            return True  # Block the event

        return super().event(event)

    def get_current_dock_area(self) -> Qt.DockWidgetArea:
        """Get the current dock widget area."""
        return self._current_dock_area

    def get_unified_frame(self) -> UnifiedSidebarFrame:
        """Get the unified sidebar frame."""
        return self.unified_frame

    def toggle_panels_visibility(self) -> None:
        """Toggle the visibility of sidebar panels."""
        self.unified_frame.toggle_panels_visibility()

    def show_panels(self) -> None:
        """Show the sidebar panels."""
        self.unified_frame.show_panels()

    def hide_panels(self) -> None:
        """Hide the sidebar panels."""
        self.unified_frame.hide_panels()

    def are_panels_visible(self) -> bool:
        """Check if sidebar panels are currently visible."""
        return self.unified_frame.are_panels_visible()

    def move_to_dock_area(self, area: Qt.DockWidgetArea) -> None:
        """
        Programmatically move the dock widget to a specific area.

        Args:
            area: The target dock widget area
        """
        if self.parent() and isinstance(self.parent(), QMainWindow):
            parent_window = self.parent()
            parent_window.addDockWidget(area, self)
            logger.info(f"Moved unified sidebar dock to area: {area}")
        else:
            logger.warning("Cannot move dock widget - no valid parent window")

    def save_state(self) -> dict:
        """Save the current state of the dock widget and its contents."""
        return {
            'dock_area': self._current_dock_area,
            'geometry': self.saveGeometry().data(),  # QDockWidget always has saveGeometry
            'unified_frame_state': self.unified_frame.save_state()
        }

    def restore_state(self, state: dict) -> None:
        """Restore the dock widget state."""
        try:
            # Restore dock area
            if 'dock_area' in state:
                target_area = state['dock_area']
                if target_area != self._current_dock_area:
                    self.move_to_dock_area(target_area)

            # Restore geometry
            if 'geometry' in state and state['geometry']:
                geometry_data = state['geometry']
                self.restoreGeometry(geometry_data)  # QDockWidget always has restoreGeometry

            # Restore unified frame state
            if 'unified_frame_state' in state:
                self.unified_frame.restore_state(state['unified_frame_state'])

            logger.info("UnifiedSidebarDockWidget state restored")
        except Exception as e:
            logger.error(f"Failed to restore dock widget state: {e}")

    def set_title(self, title: str) -> None:
        """Set the dock widget title."""
        self.setWindowTitle(title)
        logger.debug(f"Unified sidebar dock title set to: {title}")

    def add_menu_actions(self, menu) -> None:
        """Add context menu actions for dock positioning."""
        try:
            from PySide6.QtGui import QAction

            # Add dock position actions
            left_action = QAction("Move to Left", self)
            left_action.triggered.connect(lambda: self.move_to_dock_area(Qt.DockWidgetArea.LeftDockWidgetArea))
            menu.addAction(left_action)

            right_action = QAction("Move to Right", self)
            right_action.triggered.connect(lambda: self.move_to_dock_area(Qt.DockWidgetArea.RightDockWidgetArea))
            menu.addAction(right_action)

            top_action = QAction("Move to Top", self)
            top_action.triggered.connect(lambda: self.move_to_dock_area(Qt.DockWidgetArea.TopDockWidgetArea))
            menu.addAction(top_action)

            bottom_action = QAction("Move to Bottom", self)
            bottom_action.triggered.connect(lambda: self.move_to_dock_area(Qt.DockWidgetArea.BottomDockWidgetArea))
            menu.addAction(bottom_action)

            menu.addSeparator()

            # Add panel visibility toggle
            toggle_action = QAction("Toggle Panels", self)
            toggle_action.triggered.connect(self.toggle_panels_visibility)
            menu.addAction(toggle_action)

        except Exception as e:
            logger.error(f"Failed to add menu actions: {e}")
