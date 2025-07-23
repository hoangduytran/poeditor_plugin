"""
Unified Sidebar Frame for the POEditor application.

This module creates a unified frame that contains both the activity bar and sidebar panels
as a single dockable unit. The activity bar is always visible while sidebar panels can be
collapsed/hidden, but the entire frame moves together during docking operations.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from lg import logger

from widgets.activity_bar import ActivityBar
from core.sidebar_manager import SidebarManager


class UnifiedSidebarFrame(QWidget):
    """
    Unified frame containing both activity bar and sidebar panels.

    Layout Structure:
    +----------------------------------+
    | [Activity Bar] | [Sidebar Panel] |
    | (Always)       | (Collapsible)   |
    +----------------------------------+

    Features:
    - Activity bar is always visible and cannot be hidden
    - Sidebar panels can be collapsed but the activity bar remains
    - Entire frame moves together during docking
    - Smooth animations for panel collapse/expand
    """

    # Signals
    panel_visibility_changed = Signal(bool)  # True when panels visible
    dock_position_changed = Signal(Qt.DockWidgetArea)

    def __init__(self, activity_bar: ActivityBar, sidebar_manager: SidebarManager, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.activity_bar = activity_bar
        self.sidebar_manager = sidebar_manager
        self._panels_visible = True
        self._minimum_activity_bar_width = 48
        self._default_panel_width = 250

        # Animation for smooth panel transitions
        self.panel_animation: Optional[QPropertyAnimation] = None

        self.setup_ui()
        self.connect_signals()
        logger.info("UnifiedSidebarFrame initialized")

    def setup_ui(self) -> None:
        """Setup the unified frame UI."""
        # Main layout - horizontal to place activity bar and panels side by side
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Activity bar container (always visible)
        self.activity_bar_container = QFrame()
        self.activity_bar_container.setFrameStyle(QFrame.Shape.NoFrame)
        self.activity_bar_container.setFixedWidth(self._minimum_activity_bar_width)

        activity_layout = QVBoxLayout(self.activity_bar_container)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.addWidget(self.activity_bar)

        # Panel container (collapsible)
        self.panel_container = QFrame()
        self.panel_container.setFrameStyle(QFrame.Shape.StyledPanel)
        self.panel_container.setMinimumWidth(self._default_panel_width)

        panel_layout = QVBoxLayout(self.panel_container)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        # Add collapse/expand button at the top of panels
        self.toggle_button = QPushButton()
        self.toggle_button.setMaximumHeight(24)
        self.toggle_button.setToolTip("Toggle sidebar visibility")
        self.update_toggle_button()

        panel_layout.addWidget(self.toggle_button)
        panel_layout.addWidget(self.sidebar_manager)

        # Add both containers to main layout
        main_layout.addWidget(self.activity_bar_container)
        main_layout.addWidget(self.panel_container)

        # Size policies
        self.activity_bar_container.setSizePolicy(
            QWidget.SizePolicy.Policy.Fixed,
            QWidget.SizePolicy.Policy.Expanding
        )
        self.panel_container.setSizePolicy(
            QWidget.SizePolicy.Policy.Preferred,
            QWidget.SizePolicy.Policy.Expanding
        )

    def connect_signals(self) -> None:
        """Connect internal signals."""
        self.toggle_button.clicked.connect(self.toggle_panels_visibility)

        # Connect activity bar signals to pass through
        try:
            self.activity_bar.panel_requested.connect(self._on_panel_requested)
        except AttributeError:
            logger.debug("Activity bar does not have panel_requested signal")

    def _on_panel_requested(self, panel_id: str) -> None:
        """Handle panel request from activity bar."""
        # Ensure panels are visible when a panel is requested
        if not self._panels_visible:
            self.show_panels()

        # Switch to the requested panel
        self.sidebar_manager.show_panel(panel_id)

    def toggle_panels_visibility(self) -> None:
        """Toggle the visibility of sidebar panels."""
        if self._panels_visible:
            self.hide_panels()
        else:
            self.show_panels()

    def hide_panels(self) -> None:
        """Hide the sidebar panels while keeping activity bar visible."""
        if not self._panels_visible:
            return

        logger.info("Hiding sidebar panels")
        self._panels_visible = False

        # Animate the panel container width to 0
        self._animate_panel_width(self.panel_container.width(), 0)

        self.update_toggle_button()
        self.panel_visibility_changed.emit(False)

    def show_panels(self) -> None:
        """Show the sidebar panels."""
        if self._panels_visible:
            return

        logger.info("Showing sidebar panels")
        self._panels_visible = True

        # Animate the panel container width back to default
        self._animate_panel_width(0, self._default_panel_width)

        self.update_toggle_button()
        self.panel_visibility_changed.emit(True)

    def _animate_panel_width(self, start_width: int, end_width: int) -> None:
        """Animate the panel container width change."""
        if self.panel_animation and self.panel_animation.state() == QPropertyAnimation.State.Running:
            self.panel_animation.stop()

        self.panel_animation = QPropertyAnimation(self.panel_container, b"maximumWidth")
        self.panel_animation.setDuration(200)  # 200ms animation
        self.panel_animation.setStartValue(start_width)
        self.panel_animation.setEndValue(end_width)
        self.panel_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Set minimum width during animation
        if end_width == 0:
            self.panel_animation.finished.connect(lambda: self.panel_container.setMaximumWidth(0))
            self.panel_container.setMinimumWidth(0)
        else:
            self.panel_container.setMinimumWidth(self._default_panel_width)
            self.panel_container.setMaximumWidth(9999)  # Allow expansion

        self.panel_animation.start()

    def update_toggle_button(self) -> None:
        """Update the toggle button appearance based on panel visibility."""
        if self._panels_visible:
            self.toggle_button.setText("◄")  # Left arrow to collapse
            self.toggle_button.setToolTip("Collapse sidebar")
        else:
            self.toggle_button.setText("►")  # Right arrow to expand
            self.toggle_button.setToolTip("Expand sidebar")

    def update_for_dock_position(self, dock_area: Qt.DockWidgetArea) -> None:
        """
        Update the frame layout based on dock position.

        Args:
            dock_area: The new dock widget area
        """
        logger.info(f"Updating unified frame for dock position: {dock_area}")

        # For horizontal docking (left/right), use horizontal layout
        if dock_area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
            self._setup_horizontal_layout()
        # For vertical docking (top/bottom), use vertical layout
        elif dock_area in (Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea):
            self._setup_vertical_layout()

        # Update activity bar orientation
        try:
            if dock_area in (Qt.DockWidgetArea.TopDockWidgetArea, Qt.DockWidgetArea.BottomDockWidgetArea):
                self.activity_bar.set_orientation(Qt.Orientation.Horizontal)
            else:
                self.activity_bar.set_orientation(Qt.Orientation.Vertical)
        except AttributeError:
            logger.debug("Activity bar does not have set_orientation method")

        # Update sidebar manager layout
        self.sidebar_manager.update_layout_for_activity_bar_position(dock_area)

        self.dock_position_changed.emit(dock_area)

    def _setup_horizontal_layout(self) -> None:
        """Setup layout for horizontal docking (left/right)."""
        # Activity bar on the side, panels next to it
        self.activity_bar_container.setFixedWidth(self._minimum_activity_bar_width)
        self.activity_bar_container.setFixedHeight(9999)  # Allow vertical expansion

        if self._panels_visible:
            self.panel_container.setMinimumWidth(self._default_panel_width)

        # Update toggle button for horizontal layout
        self.update_toggle_button()

    def _setup_vertical_layout(self) -> None:
        """Setup layout for vertical docking (top/bottom)."""
        # Activity bar on top/bottom, panels below/above it
        self.activity_bar_container.setFixedHeight(self._minimum_activity_bar_width)
        self.activity_bar_container.setFixedWidth(9999)  # Allow horizontal expansion

        if self._panels_visible:
            self.panel_container.setMinimumHeight(200)

        # Update toggle button for vertical layout
        if self._panels_visible:
            self.toggle_button.setText("▲")  # Up arrow to collapse
        else:
            self.toggle_button.setText("▼")  # Down arrow to expand

    def are_panels_visible(self) -> bool:
        """Check if sidebar panels are currently visible."""
        return self._panels_visible

    def get_activity_bar(self) -> ActivityBar:
        """Get the activity bar widget."""
        return self.activity_bar

    def get_sidebar_manager(self) -> SidebarManager:
        """Get the sidebar manager."""
        return self.sidebar_manager

    def set_panel_width(self, width: int) -> None:
        """Set the default panel width."""
        self._default_panel_width = max(200, width)  # Minimum 200px
        if self._panels_visible:
            self.panel_container.setMinimumWidth(self._default_panel_width)

    def get_minimum_width(self) -> int:
        """Get the minimum width of the unified frame."""
        if self._panels_visible:
            return self._minimum_activity_bar_width + self._default_panel_width
        else:
            return self._minimum_activity_bar_width

    def save_state(self) -> dict:
        """Save the current state of the unified frame."""
        # Get activity bar state
        try:
            activity_bar_state = self.activity_bar.save_state()
        except AttributeError:
            activity_bar_state = {}

        # Get sidebar state
        try:
            sidebar_state = self.sidebar_manager.save_state()
        except AttributeError:
            sidebar_state = {}

        return {
            'panels_visible': self._panels_visible,
            'panel_width': self._default_panel_width,
            'activity_bar_state': activity_bar_state,
            'sidebar_state': sidebar_state
        }

    def restore_state(self, state: dict) -> None:
        """Restore the unified frame state."""
        try:
            if 'panels_visible' in state:
                if state['panels_visible']:
                    self.show_panels()
                else:
                    self.hide_panels()

            if 'panel_width' in state:
                self.set_panel_width(state['panel_width'])

            if 'activity_bar_state' in state:
                try:
                    self.activity_bar.restore_state(state['activity_bar_state'])
                except AttributeError:
                    logger.debug("Activity bar does not have restore_state method")

            if 'sidebar_state' in state:
                try:
                    self.sidebar_manager.restore_state(state['sidebar_state'])
                except AttributeError:
                    logger.debug("Sidebar manager does not have restore_state method")

            logger.info("UnifiedSidebarFrame state restored")
        except Exception as e:
            logger.error(f"Failed to restore unified frame state: {e}")
