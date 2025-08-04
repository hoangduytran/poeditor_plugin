"""
Activity Button widget for the Activity Bar.

This module defines the ActivityButton class, which represents individual
clickable buttons in the Activity Bar.
"""

from lg import logger
from PySide6.QtWidgets import QPushButton, QToolTip
from PySide6.QtCore import Signal, Qt, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QFontMetrics, QIcon, QEnterEvent
from services.icon_manager import IconManager
# Import typography and theme system
from themes.typography import get_typography_manager, FontRole, get_font
from services.theme_manager import theme_manager


class ActivityButton(QPushButton):
    """Individual button in the Activity Bar.

    An ActivityButton represents a single activity in the activity bar,
    with an icon, tooltip, and optional badge count.

    Signals:
        clicked_with_id: Emitted when button is clicked, with the activity_id
    """
    clicked_with_id = Signal(str)

    def __init__(self, activity_id: str, icon: str, tooltip: str):
        """Initialize an activity button.

        Args:
            activity_id: Unique identifier for the activity
            icon: Icon text (emoji) or path to icon file - DEPRECATED, will use SVG icons
            tooltip: Tooltip text to show on hover
        """
        super().__init__()

        # Initialize attributes directly to avoid hasattr/getattr
        self.activity_id = activity_id
        self.icon_text = icon  # Keep for backward compatibility
        self.tooltip_text = tooltip
        self.is_active = False
        self.is_hovered = False  # Track hover state for icon changes
        self.badge_count = 0

        # Initialize icon manager
        self.icon_manager = IconManager()

        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = theme_manager

        # Configure button appearance
        self.setToolTip(tooltip)
        self.setObjectName(f"activity_button_{activity_id}")
        self.setFixedSize(48, 48)  # VS Code style: 48x48 square buttons
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        # Set initial icon (inactive state)
        self._update_icon()

        # Apply initial typography
        self._update_typography()

        # Connect signals
        self.clicked.connect(self._on_clicked)
        self._connect_typography_signals()

        logger.info(f"ActivityButton created: {activity_id}")

    def enterEvent(self, event: QEnterEvent):
        """Handle mouse enter event - show lighter icon on hover."""
        super().enterEvent(event)
        self.is_hovered = True
        self._update_icon()

    def leaveEvent(self, event):
        """Handle mouse leave event - return to normal icon."""
        super().leaveEvent(event)
        self.is_hovered = False
        self._update_icon()

    def _on_clicked(self):
        """Handle click event and emit signal with activity_id."""
        self.clicked_with_id.emit(self.activity_id)
        logger.debug(f"ActivityButton clicked: {self.activity_id}")

    def _update_icon(self):
        """Update the button icon based on current state."""
        try:
            # Determine which icon state to use
            state = "active"
            if self.is_active:
                state = "active"
            elif self.is_hovered:
                state = "hovered"
            else:
                state = "inactive"

            # Get the appropriate icon
            use_active_icon = self.is_active or self.is_hovered
            icon = self.icon_manager.get_activity_button_icon(
                self.activity_id,
                active=use_active_icon,  # Use active (white) icon when active or hovered
                size=24  # Smaller icon size for VS Code-like appearance
            )
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))  # Set smaller icon size
            # Clear text since we're using icons now
            self.setText("")

            # Log state for debugging
            logger.debug(f"Icon updated for {self.activity_id}: {state}")

        except Exception as e:
            logger.error(f"Failed to update icon for {self.activity_id}: {e}")
            # Fallback to emoji if icon fails
            self.setText(self.icon_text)

    def set_active(self, active: bool):
        """Set the active state of the button.

        Args:
            active: True if the button should be active, False otherwise
        """
        if self.is_active != active:
            self.is_active = active
            self._update_icon()  # Update icon based on new state

            # Update visual style
            if active:
                self.setProperty("active", "true")
            else:
                self.setProperty("active", "false")

            # Force style recalculation
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

            logger.debug(f"Activity {self.activity_id} active state: {active}")

    def set_badge(self, count: int):
        """Set the badge count.

        Args:
            count: Number to display in the badge, or 0 to hide badge
        """
        self.badge_count = max(0, count)
        self.update()  # Trigger repaint
        logger.debug(f"Activity {self.activity_id} badge count: {count}")

    def clear_badge(self):
        """Clear the badge count (set to 0)."""
        self.badge_count = 0
        self.update()
        logger.debug(f"Activity {self.activity_id} badge cleared")

    def get_activity_id(self) -> str:
        """Get the activity ID.

        Returns:
            The activity ID string
        """
        return self.activity_id

    def paintEvent(self, event):
        """Custom paint event to draw the button and badge.

        Args:
            event: The paint event
        """
        # Call parent paint event to draw the button
        super().paintEvent(event)

        # Draw badge if count > 0
        if self.badge_count > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Badge background
            badge_color = QColor("#f14c4c")
            painter.setBrush(badge_color)
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw badge in top-right corner
            badge_size = 16
            badge_rect = QRect(
                self.width() - badge_size - 4,
                4,
                badge_size,
                badge_size
            )
            painter.drawEllipse(badge_rect)

            # Badge text
            badge_text = str(self.badge_count) if self.badge_count < 10 else "9+"
            painter.setPen(Qt.GlobalColor.white)
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            # Center text in badge
            fm = QFontMetrics(font)
            text_rect = fm.boundingRect(badge_text)
            text_x = badge_rect.center().x() - text_rect.width() // 2
            text_y = badge_rect.center().y() + text_rect.height() // 4
            painter.drawText(text_x, text_y, badge_text)

            painter.end()

    def _connect_typography_signals(self):
        """Connect to typography manager signals for theme updates."""
        # TypographyManager has 'fonts_changed' signal (not 'typography_changed')
        self.typography_manager.fonts_changed.connect(self._update_typography)
        self.theme_manager.theme_changed.connect(self._update_typography)

    def _update_typography(self):
        """Update typography settings for the button."""
        try:
            # Get appropriate font for button text (if using text fallback)
            font = get_font(FontRole.BODY)
            if font:
                self.setFont(font)

            # Update tooltip font if we have typography manager
            # Note: get_tooltip_font method doesn't exist, using standard font approach
            tooltip_font = get_font(FontRole.TOOLTIP)
            if tooltip_font:
                # Apply tooltip font through style (limited support in Qt)
                pass

            logger.debug(f"Typography updated for ActivityButton {self.activity_id}")
        except Exception as e:
            logger.error(f"Failed to update typography for ActivityButton {self.activity_id}: {e}")

    def update_theme(self):
        """Update the button's appearance based on current theme."""
        self._update_typography()
        self._update_icon()
        self.update()

