"""
Explorer Context Menu Keyboard Navigation

Provides enhanced keyboard navigation for the Explorer Context Menu.
"""

from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMenu, QApplication

from lg import logger
from widgets.explorer_context_menu_accessibility import menu_accessibility_manager


def setup_menu_keyboard_navigation(menu: QMenu) -> None:
    """
    Set up enhanced keyboard navigation for context menus.
    
    Args:
        menu: The menu to enhance
    """
    # First letter navigation is handled by the accessibility manager
    
    # Add a menu event filter for additional keyboard handling
    menu.installEventFilter(MenuKeyboardNavigator(menu))
    
    # Apply to submenus recursively
    for action in menu.actions():
        submenu = action.menu()
        if submenu and isinstance(submenu, QMenu):
            setup_menu_keyboard_navigation(submenu)


class MenuKeyboardNavigator(QObject):
    """
    Event filter for enhanced keyboard navigation in menus.
    
    Provides:
    - Section navigation with Tab key
    - Back navigation with Escape or Backspace
    - Improved submenu navigation
    """
    
    def __init__(self, parent=None):
        """Initialize the keyboard navigator."""
        super().__init__(parent)
    
    def eventFilter(self, obj, event):
        """Handle key events for menu navigation."""
        if not isinstance(obj, QMenu) or event.type() != QEvent.Type.KeyPress:
            return False
            
        # Cast to QKeyEvent for access to key() method
        key_event = event
        if not isinstance(key_event, QKeyEvent):
            return False
            
        # Handle Tab key for section navigation
        if key_event.key() == Qt.Key.Key_Tab:
            self._navigate_sections(obj)
            return True
            
        # Handle Backspace for menu navigation
        if key_event.key() == Qt.Key.Key_Backspace:
            self._navigate_back(obj)
            return True
            
        return False
        
    def _navigate_sections(self, menu: QMenu) -> None:
        """
        Navigate between sections in the menu.
        
        Args:
            menu: The menu being navigated
        """
        # Find separators in the menu
        separators = []
        for i, action in enumerate(menu.actions()):
            if action.isSeparator():
                separators.append(i)
                
        if not separators:
            return
            
        # Find current active action
        current_index = -1
        current_action = menu.activeAction()
        if current_action:
            for i, action in enumerate(menu.actions()):
                if action == current_action:
                    current_index = i
                    break
        
        # Find the next section
        next_section_start = 0
        for sep_index in separators:
            if sep_index > current_index:
                next_section_start = sep_index + 1
                break
        else:
            # Wrap around to the beginning
            next_section_start = 0
            
        # Activate the first action in the next section
        if next_section_start < len(menu.actions()):
            menu.setActiveAction(menu.actions()[next_section_start])
            
            # Announce section change to screen reader
            action = menu.actions()[next_section_start]
            menu_accessibility_manager.announce_to_screen_reader(f"Section: {action.text()}")
            
    def _navigate_back(self, menu: QMenu) -> None:
        """
        Navigate back to the parent menu.
        
        Args:
            menu: The menu being navigated
        """
        # This is just a hint to the user - actual back navigation
        # is handled by the menu system
        menu_accessibility_manager.announce_to_screen_reader("Back to previous menu")
