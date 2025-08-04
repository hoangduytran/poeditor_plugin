"""
Activity Bar widget for the application sidebar.

This module defines the ActivityBar class, which is the main container
for activity buttons in the sidebar.
"""

from lg import logger
from typing import Dict, Optional, List
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSpacerItem, QSizePolicy,
    QStyleOption, QStyle
)
from PySide6.QtCore import Signal, Qt, QFile, QTextStream
from PySide6.QtGui import QPainter

from widgets.activity_button import ActivityButton
from models.activity_models import ActivityConfig
# Import typography and theme system
from themes.typography import get_typography_manager, FontRole, get_font
from services.theme_manager import theme_manager


class ActivityBar(QWidget):
    """Main vertical sidebar container with navigation buttons.

    The ActivityBar displays activity buttons in a vertical layout,
    and manages their active state and interactions.

    Signals:
        panel_requested: Emitted when an activity panel should be shown,
                         with the activity_id
    """
    panel_requested = Signal(str)  # panel_id

    def __init__(self, api):
        """Initialize the activity bar.

        Args:
            api: The plugin API instance
        """
        super().__init__()

        # Initialize attributes directly to avoid hasattr/getattr
        self.api = api
        self.buttons: Dict[str, ActivityButton] = {}
        self.active_activity_id: Optional[str] = None
        self.main_layout = QVBoxLayout()
        self.main_buttons_layout = QVBoxLayout()
        self.bottom_buttons_layout = QVBoxLayout()

        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = theme_manager

        # Configure layouts
        self.setup_layout()

        # Connect to typography and theme signals
        self._connect_typography_signals()

        # Set the main layout
        self.setLayout(self.main_layout)

        logger.info("ActivityBar initialized")

    def setup_layout(self):
        """Set up the widget layout."""
        # Main layout
        self.setObjectName("activity_bar")
        self.setFixedWidth(48)

        # Configure main layout
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main area buttons (top)
        self.main_layout.addLayout(self.main_buttons_layout)
        self.main_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.main_buttons_layout.setSpacing(0)

        # Spacer to push bottom buttons down
        self.main_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                       QSizePolicy.Policy.Expanding)
        )

        # Bottom area buttons
        self.main_layout.addLayout(self.bottom_buttons_layout)
        self.bottom_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.bottom_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_buttons_layout.setSpacing(0)

        self.setLayout(self.main_layout)

        # Set minimal style sheet - detailed styling handled by external CSS
        self.setObjectName("activity_bar")

        # Load activity bar specific CSS
        self._load_activity_bar_css()

    def _load_activity_bar_css(self):
        """Load activity bar specific CSS using ThemeManager."""
        try:
            # Use ThemeManager to apply activity bar styles
            if self.theme_manager:
                self.theme_manager.apply_activity_bar_theme(self)
                logger.info("Activity bar CSS loaded and applied successfully via ThemeManager")
            else:
                logger.warning("ThemeManager not available for activity bar styling")

        except Exception as e:
            logger.error(f"Failed to load activity bar CSS: {e}")


    def add_activity_button(self, activity_config: ActivityConfig) -> None:
        """Add an activity button from config.

        Args:
            activity_config: Configuration for the activity
        """
        # Ensure we have necessary attributes
        try:
            if not activity_config.id:
                logger.error("ActivityConfig missing id attribute")
                return

            # Create button
            button = ActivityButton(
                activity_config.id,
                activity_config.icon,
                activity_config.tooltip
            )
        except Exception as e:
            logger.error(f"Error creating activity button: {e}")
            return

        # Connect signal
        button.clicked_with_id.connect(self._on_button_clicked)

        # Add to appropriate layout
        if activity_config.area == "bottom":
            self.bottom_buttons_layout.addWidget(button)
        else:
            self.main_buttons_layout.addWidget(button)

        # Store reference
        self.buttons[activity_config.id] = button

        logger.info(f"Added activity button: {activity_config.id}")

    def _on_button_clicked(self, activity_id: str) -> None:
        """Handle button click events.

        Args:
            activity_id: ID of the clicked activity
        """
        # Toggle panel if already active, otherwise activate
        if activity_id == self.active_activity_id:
            # TODO: Toggle panel visibility
            logger.debug(f"Activity {activity_id} already active, toggling panel")

        # Set active and emit signal
        self.set_active_activity(activity_id)
        self.panel_requested.emit(activity_id)

    def set_active_activity(self, activity_id: str) -> None:
        """Set the active activity.

        Args:
            activity_id: ID of the activity to activate
        """
        if activity_id not in self.buttons:
            logger.error(f"Activity {activity_id} not found in buttons")
            return

        # Reset all buttons to inactive state - this ensures no hover states are stuck
        for button_id, button in self.buttons.items():
            if button_id != activity_id:
                button.is_hovered = False
                button.set_active(False)

        # Activate new button
        self.buttons[activity_id].set_active(True)
        self.active_activity_id = activity_id
        logger.info(f"Set active activity: {activity_id}")

    def get_active_activity(self) -> str:
        """Get the ID of the active activity.

        Returns:
            The active activity ID, or empty string if none active
        """
        return self.active_activity_id or ""

    def set_badge(self, activity_id: str, count: int) -> None:
        """Set badge count for an activity.

        Args:
            activity_id: ID of the activity
            count: Badge count to display
        """
        if activity_id in self.buttons:
            self.buttons[activity_id].set_badge(count)
        else:
            logger.warning(f"Activity {activity_id} not found for badge update")

    def remove_activity_button(self, activity_id: str) -> None:
        """Remove an activity button.

        Args:
            activity_id: ID of the activity to remove
        """
        if activity_id not in self.buttons:
            logger.warning(f"Activity {activity_id} not found for removal")
            return

        # Get button and remove from layout
        button = self.buttons[activity_id]

        # Remove from appropriate layout
        # Check which layout contains this button
        if self.bottom_buttons_layout.indexOf(button) != -1:
            self.bottom_buttons_layout.removeWidget(button)
        elif self.main_buttons_layout.indexOf(button) != -1:
            self.main_buttons_layout.removeWidget(button)
        else:
            logger.warning(f"Button {activity_id} not found in any layout")

        # Clean up
        button.deleteLater()
        del self.buttons[activity_id]

        # Reset active if this was the active one
        if self.active_activity_id == activity_id:
            self.active_activity_id = None

        logger.info(f"Removed activity button: {activity_id}")

    def get_ordered_activity_ids(self) -> List[str]:
        """Get ordered list of activity IDs.

        Returns:
            List of activity IDs in display order
        """
        # TODO: Implement proper ordering based on position
        return list(self.buttons.keys())

    def set_horizontal_orientation(self) -> None:
        """Configure for horizontal layout (top/bottom docking)."""
        try:
            # Change to horizontal layout
            self.setFixedHeight(48)
            self.setMinimumWidth(100)
            self.setMaximumWidth(16777215)  # Remove width constraint

            # TODO: Update button layout to horizontal if needed
            # For now, keep vertical button arrangement even in horizontal mode

            logger.debug("ActivityBar configured for horizontal orientation")

        except Exception as e:
            logger.error(f"Failed to set horizontal orientation: {e}")

    def set_vertical_orientation(self) -> None:
        """Configure for vertical layout (left/right docking)."""
        try:
            # Change to vertical layout (default)
            self.setFixedWidth(48)
            self.setMinimumHeight(100)
            self.setMaximumHeight(16777215)  # Remove height constraint

            # Buttons remain in vertical arrangement

            logger.debug("ActivityBar configured for vertical orientation")

        except Exception as e:
            logger.error(f"Failed to set vertical orientation: {e}")

    def paintEvent(self, event):
        """Custom paint event to ensure stylesheets work with custom widgets.

        Args:
            event: The paint event
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    def _connect_typography_signals(self):
        """Connect to typography and theme change signals."""
        try:
            # Connect to typography manager signals
            self.typography_manager.fonts_changed.connect(self._on_typography_changed)

            # Connect to theme manager signals
            self.theme_manager.theme_changed.connect(self._on_theme_changed)

            logger.info("ActivityBar connected to typography and theme change signals")
        except Exception as e:
            logger.error(f"Failed to connect to typography signals in ActivityBar: {e}")

    def apply_typography(self):
        """Public method to apply typography to the activity bar.

        This method is part of the typography integration public API.
        It applies the current typography settings to all components.
        """
        self._apply_typography()

    def apply_theme(self):
        """Public method to apply theme styling to the activity bar.

        This method is part of the theme integration public API.
        It applies the current theme styles to all components.
        """
        self._apply_theme_styling()

    def _apply_typography(self):
        """Apply typography to all activity buttons."""
        try:
            logger.info("Applying typography to ActivityBar buttons")

            # Apply button font role to all activity buttons
            for button in self.buttons.values():
                button.setFont(get_font(FontRole.BUTTON))

                # Apply typography to button tooltips if needed
                if button.toolTip():
                    # Tooltips use the system default, but we could customize if needed
                    pass

            logger.info("Typography applied successfully to ActivityBar buttons")

        except Exception as e:
            logger.error(f"Failed to apply typography to ActivityBar: {e}")

    def _apply_theme_styling(self):
        """Apply theme-based styling to activity buttons.

        NOTE: Disabled to allow external CSS file to control styling.
        Individual button stylesheets override global CSS.
        """
        # Disabled to prevent conflicts with external CSS file
        logger.debug("Theme styling skipped - using external CSS file instead")
        return

    def _on_typography_changed(self):
        """Handle typography change events."""
        logger.info("ActivityBar typography changed, updating buttons")
        self._apply_typography()

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change events by refreshing activity bar CSS.

        Args:
            theme_name: Name of the new theme
        """
        logger.debug(f"ActivityBar refreshing CSS for theme change to {theme_name}")
        # Reload activity bar CSS from ThemeManager
        self._load_activity_bar_css()
