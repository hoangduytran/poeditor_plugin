"""
Tab Manager for the POEditor application.

This module manages document tabs in the main editor area.
It handles tab creation, switching, closing, and state management.
"""

from typing import Optional
from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal
from lg import logger

# Import theme system
from services.theme_manager import theme_manager
from themes.typography import get_typography_manager, get_font, FontRole


class CustomTabBar(QTabBar):
    """
    Custom tab bar with enhanced functionality and typography integration.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setExpanding(False)
        
        # Initialize typography manager
        self.typography_manager = get_typography_manager()
        
        # Apply typography
        self.apply_typography()
        
        # Note: Styling is now handled by parent TabManager
        # to ensure consistency with theme system
    
    def apply_typography(self):
        """Apply typography to the tab bar."""
        try:
            # Use MENU font role for tab text
            self.setFont(get_font(FontRole.MENU))
        except Exception as e:
            logger.error(f"Failed to apply typography to CustomTabBar: {e}")


class TabManager(QTabWidget):
    """
    Manages document tabs in the main editor area.
    
    Features:
    - Tab creation and management
    - Modified state tracking (shows * in title)
    - Tab close handling with confirmation
    - Context menu support
    """
    
    # Signals
    tab_changed = Signal(int)  # tab index
    tab_close_requested = Signal(int)  # tab index
    tab_modified_changed = Signal(int, bool)  # tab index, modified
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._modified_tabs = set()  # Track which tabs are modified
        
        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = theme_manager
        
        self.setup_ui()
        self.connect_signals()
        
        # Connect to typography and theme signals
        self._connect_typography_signals()
        
        # Apply initial typography and theme
        self.apply_typography()
        self.apply_theme()
        
        logger.info("TabManager initialized with typography integration")
    
    def setup_ui(self) -> None:
        """Setup the tab manager UI."""
        # Use custom tab bar
        custom_tab_bar = CustomTabBar()
        self.setTabBar(custom_tab_bar)
        
        # Configure tab widget
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # # Style the tab widget
        # self.setStyleSheet("""
        #     QTabWidget::pane {
        #         border: 1px solid #464647;
        #         background-color: #1e1e1e;
        #     }
        #     QTabWidget::tab-bar {
        #         alignment: left;
        #     }
        # """)
    
    def connect_signals(self) -> None:
        """Connect internal signals."""
        self.currentChanged.connect(self._on_current_changed)
        self.tabCloseRequested.connect(self._on_tab_close_requested)
    
    def add_tab(self, widget: QWidget, title: str, icon: Optional[QIcon] = None) -> int:
        """
        Add a new tab.
        
        Args:
            widget: The widget to display in the tab
            title: Tab title
            icon: Optional icon for the tab
            
        Returns:
            Index of the created tab
        """
        try:
            if icon:
                index = super().addTab(widget, icon, title)
            else:
                index = super().addTab(widget, title)
            
            # Set the new tab as current
            self.setCurrentIndex(index)
            
            logger.info(f"Added tab: {title} at index {index}")
            return index
            
        except Exception as e:
            logger.error(f"Failed to add tab {title}: {e}")
            return -1
    
    def close_tab(self, index: int) -> bool:
        """
        Close a tab at the specified index.
        
        Args:
            index: Index of the tab to close
            
        Returns:
            True if tab was closed successfully
        """
        try:
            if index < 0 or index >= self.count():
                logger.warning(f"Invalid tab index: {index}")
                return False
            
            widget = self.widget(index)
            title = self.tabText(index)
            
            # Check if widget has a close method and call it
            can_close = True
            if widget:
                # Direct attribute access with try/except
                try:
                    can_close = widget.can_close()  # type: ignore
                except (AttributeError, TypeError):
                    # Widget doesn't have can_close method, default to True
                    can_close = True
            
            if not can_close:
                logger.info(f"Tab close cancelled by widget: {title}")
                return False
            
            # Remove from modified tabs set
            self._modified_tabs.discard(index)
            
            # Remove the tab
            self.removeTab(index)
            
            # Clean up widget if it has cleanup method
            if widget:
                # Direct attribute access with try/except
                try:
                    widget.cleanup()  # type: ignore
                except (AttributeError, TypeError):
                    # Widget doesn't have cleanup method, continue normally
                    pass
            
            logger.info(f"Closed tab: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close tab at index {index}: {e}")
            return False
    
    def close_all_tabs(self) -> bool:
        """
        Close all tabs.
        
        Returns:
            True if all tabs were closed successfully
        """
        try:
            # Close tabs from right to left to maintain correct indices
            for i in range(self.count() - 1, -1, -1):
                if not self.close_tab(i):
                    return False
            
            logger.info("Closed all tabs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close all tabs: {e}")
            return False
    
    def get_active_tab(self) -> Optional[QWidget]:
        """Get the currently active tab widget."""
        try:
            current_index = self.currentIndex()
            if current_index >= 0:
                return self.widget(current_index)
            return None
        except Exception as e:
            logger.error(f"Failed to get active tab: {e}")
            return None
    
    def find_tab(self, widget: QWidget) -> int:
        """
        Find the index of a tab containing the specified widget.
        
        Args:
            widget: The widget to find
            
        Returns:
            Index of the tab, or -1 if not found
        """
        try:
            for i in range(self.count()):
                if self.widget(i) == widget:
                    return i
            return -1
        except Exception as e:
            logger.error(f"Failed to find tab: {e}")
            return -1
    
    def find_tab_by_path(self, file_path: str) -> int:
        """
        Find the index of a tab containing a file with the specified path.
        
        Args:
            file_path: The file path to find
            
        Returns:
            Index of the tab, or -1 if not found
        """
        try:
            for i in range(self.count()):
                widget = self.widget(i)
                # Check if widget has a file_path attribute
                try:
                    if widget.file_path == file_path:  # type: ignore
                        return i
                except (AttributeError, TypeError):
                    # Widget doesn't have file_path attribute, skip
                    continue
            return -1
        except Exception as e:
            logger.error(f"Failed to find tab by path {file_path}: {e}")
            return -1
    
    def set_tab_modified(self, index: int, modified: bool) -> None:
        """
        Set the modified state of a tab.
        
        Args:
            index: Index of the tab
            modified: True if tab content is modified
        """
        try:
            if index < 0 or index >= self.count():
                logger.warning(f"Invalid tab index: {index}")
                return
            
            current_title = self.tabText(index)
            
            if modified:
                if index not in self._modified_tabs:
                    self._modified_tabs.add(index)
                    # Add asterisk to title if not already present
                    if not current_title.endswith(' *'):
                        self.setTabText(index, current_title + ' *')
            else:
                if index in self._modified_tabs:
                    self._modified_tabs.remove(index)
                    # Remove asterisk from title
                    if current_title.endswith(' *'):
                        self.setTabText(index, current_title[:-2])
            
            self.tab_modified_changed.emit(index, modified)
            
        except Exception as e:
            logger.error(f"Failed to set tab modified state: {e}")
    
    def is_tab_modified(self, index: int) -> bool:
        """
        Check if a tab is modified.
        
        Args:
            index: Index of the tab
            
        Returns:
            True if tab is modified
        """
        return index in self._modified_tabs
    
    def get_tab_title(self, index: int) -> str:
        """
        Get the clean title of a tab (without modification indicator).
        
        Args:
            index: Index of the tab
            
        Returns:
            Clean tab title
        """
        try:
            title = self.tabText(index)
            if title.endswith(' *'):
                return title[:-2]
            return title
        except Exception as e:
            logger.error(f"Failed to get tab title: {e}")
            return ""
    
    def set_tab_icon(self, index: int, icon: QIcon) -> None:
        """
        Set the icon for a tab.
        
        Args:
            index: Index of the tab
            icon: Icon to set
        """
        try:
            if index >= 0 and index < self.count():
                super().setTabIcon(index, icon)
        except Exception as e:
            logger.error(f"Failed to set tab icon: {e}")
    
    def get_modified_tabs(self) -> list:
        """Get list of modified tab indices."""
        return list(self._modified_tabs)
    
    def has_modified_tabs(self) -> bool:
        """Check if any tabs are modified."""
        return len(self._modified_tabs) > 0
    
    def _on_current_changed(self, index: int) -> None:
        """Handle tab change."""
        try:
            if index >= 0:
                widget = self.widget(index)
                if widget:
                    # Direct attribute access with try/except
                    try:
                        widget.on_activated()  # type: ignore
                    except (AttributeError, TypeError):
                        # Widget doesn't have on_activated method, continue normally
                        pass
                
                self.tab_changed.emit(index)
                logger.info(f"Tab changed to index: {index}")
                
        except Exception as e:
            logger.error(f"Error handling tab change: {e}")
    
    def _on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request."""
        try:
            self.tab_close_requested.emit(index)
            # The actual closing is handled by the close_tab method
            # This allows for external handling of close requests
            
        except Exception as e:
            logger.error(f"Error handling tab close request: {e}")
    
    def contextMenuEvent(self, event):
        """Handle context menu for tabs."""
        try:
            # Get the tab under the cursor
            tab_bar = self.tabBar()
            index = tab_bar.tabAt(event.pos())
            
            if index >= 0:
                # Could implement context menu here
                # For now, just call parent implementation
                super().contextMenuEvent(event)
        except Exception as e:
            logger.error(f"Error handling context menu: {e}")
    
    def save_all_modified_tabs(self) -> bool:
        """
        Save all modified tabs.
        
        Returns:
            True if all tabs were saved successfully
        """
        try:
            for index in list(self._modified_tabs):
                widget = self.widget(index)
                if widget:
                    # Direct attribute access with try/except
                    try:
                        if not widget.save():  # type: ignore
                            logger.error(f"Failed to save tab at index {index}")
                            return False
                    except (AttributeError, TypeError):
                        # Widget doesn't have save method, skip
                        logger.warning(f"Tab at index {index} doesn't support saving")
                        continue
            
            logger.info("Saved all modified tabs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save all modified tabs: {e}")
            return False

    def _connect_typography_signals(self):
        """Connect to typography and theme change signals."""
        try:
            # Connect to typography manager signals
            self.typography_manager.fonts_changed.connect(self._on_typography_changed)
            
            # Connect to theme manager signals
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
            
            logger.info("TabManager connected to typography and theme change signals")
        except Exception as e:
            logger.error(f"Failed to connect to typography signals in TabManager: {e}")
    
    def apply_typography(self):
        """Public method to apply typography to the tab manager.
        
        This method is part of the typography integration public API.
        It applies the current typography settings to tab headers.
        """
        self._apply_typography()
    
    def apply_theme(self):
        """Public method to apply theme styling to the tab manager.
        
        This method is part of the theme integration public API.
        It applies the current theme styles to tabs and headers.
        """
        self._apply_theme_styling()
    
    def _apply_typography(self):
        """Apply typography to tab headers and labels."""
        try:
            logger.info("Applying typography to TabManager")
            
            # Apply font to tab bar
            tab_bar = self.tabBar()
            if tab_bar:
                tab_bar.setFont(get_font(FontRole.MENU))  # Tabs act like menu items
                
                # Update all tab text fonts (implicit through tab bar font)
                for i in range(self.count()):
                    # Tab text font is inherited from tab bar
                    pass
            
            logger.info("Typography applied successfully to TabManager")
            
        except Exception as e:
            logger.error(f"Failed to apply typography to TabManager: {e}")
    
    def _apply_theme_styling(self):
        """Apply theme-based styling to tabs."""
        try:
            logger.info("Applying theme styling to TabManager")
            
            # Get tab styles from theme manager
            tab_styles = self.theme_manager.get_style_for_component("tabs")
            tab_active_styles = self.theme_manager.get_style_for_component("tab_active")
            tab_inactive_styles = self.theme_manager.get_style_for_component("tab_inactive")
            tab_hover_styles = self.theme_manager.get_style_for_component("tab_hover")
            
            # Build complete stylesheet
            stylesheet_parts = []
            
            # Tab widget pane styling
            if tab_styles:
                stylesheet_parts.append(f"QTabWidget::pane {{ {tab_styles} }}")
            else:
                # Fallback default styling
                stylesheet_parts.append("""
                    QTabWidget::pane {
                        border: 1px solid #464647;
                        background-color: #1e1e1e;
                    }
                """)
            
            # Tab bar styling
            stylesheet_parts.append("QTabWidget::tab-bar { alignment: left; }")
            
            # Tab button styling
            if tab_inactive_styles:
                stylesheet_parts.append(f"QTabBar::tab {{ {tab_inactive_styles} }}")
            else:
                # Fallback default styling
                stylesheet_parts.append("""
                    QTabBar::tab {
                        background-color: #2d2d30;
                        color: #cccccc;
                        border: 1px solid #464647;
                        border-bottom: none;
                        padding: 8px 12px;
                        margin-right: 2px;
                        min-width: 100px;
                    }
                """)
            
            if tab_active_styles:
                stylesheet_parts.append(f"QTabBar::tab:selected {{ {tab_active_styles} }}")
            else:
                # Fallback default styling
                stylesheet_parts.append("""
                    QTabBar::tab:selected {
                        background-color: #1e1e1e;
                        color: #ffffff;
                        border-bottom: 2px solid #0078d4;
                    }
                """)
            
            if tab_hover_styles:
                stylesheet_parts.append(f"QTabBar::tab:hover {{ {tab_hover_styles} }}")
            else:
                # Fallback default styling
                stylesheet_parts.append("""
                    QTabBar::tab:hover {
                        background-color: #3e3e42;
                    }
                """)
            
            # Close button styling
            stylesheet_parts.append("""
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                QTabBar::close-button {
                    image: url(:/icons/close.png);
                    subcontrol-position: right;
                }
                QTabBar::close-button:hover {
                    background-color: #e81123;
                    border-radius: 2px;
                }
            """)
            
            # Apply the complete stylesheet
            complete_stylesheet = "\n".join(stylesheet_parts)
            self.setStyleSheet(complete_stylesheet)
            
            # Also apply to custom tab bar
            tab_bar = self.tabBar()
            if tab_bar:
                tab_bar.setStyleSheet(complete_stylesheet)
            
            logger.info("Theme styling applied successfully to TabManager")
            
        except Exception as e:
            logger.error(f"Failed to apply theme styling to TabManager: {e}")
    
    def _on_typography_changed(self):
        """Handle typography change events."""
        logger.info("TabManager typography changed, updating")
        self._apply_typography()
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change events."""
        logger.info(f"TabManager theme changed to {theme_name}, updating styling")
        self._apply_theme_styling()
