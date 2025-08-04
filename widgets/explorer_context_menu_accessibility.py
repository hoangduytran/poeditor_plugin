"""
Explorer Context Menu Accessibility Support.

This module provides accessibility features for the Explorer Context Menu,
including screen reader support, keyboard navigation improvements, and
focus management.
"""

from PySide6.QtCore import QObject, Qt, QEvent
from PySide6.QtGui import QAction, QKeyEvent
from PySide6.QtWidgets import QMenu, QWidget, QApplication

from lg import logger


class MenuAccessibilityManager(QObject):
    """
    Manages accessibility features for context menus.

    Provides support for:
    - Screen reader announcements
    - Keyboard navigation enhancements
    - Focus management
    """

    def __init__(self, parent=None):
        """Initialize the accessibility manager."""
        super().__init__(parent)
        self._first_letter_map = {}
        self._last_focused_item = None
        self._focus_history = []

    def add_accessibility_to_menu(self, menu: QMenu) -> None:
        """
        Add accessibility features to a menu.

        Args:
            menu: The menu to enhance with accessibility features
        """
        if not menu:
            return

        # Add ARIA attributes to menu
        menu.setProperty("aria-role", "menu")
        menu.setProperty("aria-label", menu.title() or "Context Menu")

        # Add ARIA attributes to menu items
        for action in menu.actions():
            self._add_accessibility_to_action(action)

        # Set up event filter for keyboard navigation
        menu.installEventFilter(self)

        # Build first letter navigation map
        self._build_first_letter_map(menu)

        logger.debug(f"Added accessibility features to menu: {menu.title() or 'Context Menu'}")

    def _add_accessibility_to_action(self, action: QAction) -> None:
        """
        Add accessibility features to an action.

        Args:
            action: The action to enhance
        """
        if not action:
            return

        # Add ARIA attributes
        action.setProperty("aria-role", "menuitem")

        if action.isSeparator():
            action.setProperty("aria-role", "separator")
            return

        # Handle submenus
        if action.menu():
            action.setProperty("aria-haspopup", "true")
            action.setProperty("aria-expanded", "false")

            # Also enhance the submenu
            submenu = action.menu()
            if isinstance(submenu, QMenu):
                self.add_accessibility_to_menu(submenu)

        # Set enabled/disabled state for screen readers
        action.setProperty("aria-disabled", str(not action.isEnabled()).lower())

        # Handle checkable actions
        if action.isCheckable():
            action.setProperty("aria-role", "menuitemcheckbox")
            action.setProperty("aria-checked", str(action.isChecked()).lower())

    def announce_to_screen_reader(self, text: str) -> None:
        """
        Announce text to screen readers.

        Args:
            text: The text to announce
        """
        # Use Qt's accessibility system to announce text
        # This method depends on the platform's accessibility system
        # Use a custom event type for accessibility announcements
        QApplication.postEvent(self, QEvent(QEvent.Type.User))

        # Set the text to be announced
        current_focus = QApplication.focusWidget()
        if current_focus:
            current_focus.setProperty("aria-live", "polite")
            current_focus.setProperty("aria-atomic", "true")
            current_focus.setAccessibleDescription(text)

        logger.debug(f"Screen reader announcement: {text}")

    def _build_first_letter_map(self, menu: QMenu) -> None:
        """
        Build a map for first-letter navigation.

        Args:
            menu: The menu to build the map for
        """
        self._first_letter_map.clear()

        for action in menu.actions():
            if action.isSeparator() or not action.isEnabled():
                continue

            text = action.text()
            if not text:
                continue

            # Get first letter, normalizing case
            first_letter = text[0].lower()

            if first_letter not in self._first_letter_map:
                self._first_letter_map[first_letter] = []

            self._first_letter_map[first_letter].append(action)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Filter events for enhanced keyboard navigation.

        Args:
            obj: The object receiving the event
            event: The event being processed

        Returns:
            True if the event was handled, False otherwise
        """
        if not isinstance(obj, QMenu):
            return False

        # Handle key press events
        if event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
            key_event = event

            # Handle first letter navigation
            if key_event.key() >= Qt.Key.Key_A and key_event.key() <= Qt.Key.Key_Z:
                letter = chr(key_event.key()).lower()
                if letter in self._first_letter_map:
                    actions = self._first_letter_map[letter]

                    # Find the next action starting with this letter
                    current_action = obj.activeAction()
                    if current_action in actions:
                        index = actions.index(current_action)
                        next_action = actions[(index + 1) % len(actions)]
                    else:
                        next_action = actions[0]

                    # Activate the action
                    obj.setActiveAction(next_action)
                    self.announce_to_screen_reader(next_action.text())
                    return True

        return False

    def track_focus(self, widget: QWidget) -> None:
        """
        Track focus for later restoration.

        Args:
            widget: The widget that currently has focus
        """
        if not widget:
            return

        # Store this widget in focus history
        self._last_focused_item = widget
        self._focus_history.append(widget)

        # Limit history size
        if len(self._focus_history) > 10:
            self._focus_history.pop(0)

    def restore_focus(self) -> None:
        """Restore focus to the last focused widget."""
        if not self._last_focused_item:
            return

        if not self._last_focused_item.isVisible():
            # Try to find a parent that is visible
            parent = self._last_focused_item.parentWidget()
            while parent:
                if parent.isVisible():
                    parent.setFocus()
                    return
                parent = parent.parentWidget()
        else:
            self._last_focused_item.setFocus()

    def get_focus_history(self) -> list:
        """
        Get the focus history.

        Returns:
            List of previously focused widgets
        """
        return self._focus_history.copy()


# Singleton instance
menu_accessibility_manager = MenuAccessibilityManager()
