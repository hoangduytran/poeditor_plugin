"""
Sidebar Manager for the POEditor application.

This module manages the sidebar panel container. The activity bar is now external
and dockable, so this manager focuses solely on panel management and switching.
"""

from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from lg import logger

class SidebarManager(QWidget):
    """
    Manages the application sidebar containing plugin panels.
    
    The sidebar consists of:
    - Panel area: Stacked widget containing the actual panels
    """
    
    panel_changed = Signal(str)  # panel_id
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._panels: Dict[str, QWidget] = {}
        self._active_panel: Optional[str] = None
        self._visible = True  # CRITICAL: Always start visible
        
        # UI components - initialize immediately to avoid None issues
        self.panel_stack = QStackedWidget()
        
        self.setup_ui()
        # SAFETY: Ensure sidebar is always visible to prevent blank screen deadlock
        self.ensure_always_visible()
        logger.info("SidebarManager initialized with safety guarantees")

    def update_layout_for_activity_bar_position(self, area: Qt.DockWidgetArea) -> None:
        """
        Update sidebar layout based on activity bar dock position.
        Args:
            area: The new dock widget area
        """
        # Example: Adjust minimum width or orientation if needed
        if area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
            self.setMinimumWidth(250)
            self.setMaximumWidth(400)
        else:
            self.setMinimumWidth(200)
            self.setMaximumWidth(9999)
        logger.info(f"SidebarManager layout updated for activity bar position: {area}")

    def setup_ui(self) -> None:
        """Setup the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Configure the panel stack (already created in __init__)
        self.panel_stack.setMinimumWidth(250)
        layout.addWidget(self.panel_stack)
        
        # Initial state
        self.setMinimumWidth(250)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
    def add_panel(self, panel_id: str, widget: QWidget, icon=None, title: Optional[str] = None) -> None:
        """
        Add a panel to the sidebar.
        
        Args:
            panel_id: Unique identifier for the panel
            widget: The panel widget
            icon: Optional icon for the panel (for compatibility)
            title: Optional title for the panel (for compatibility)
        """
        try:
            if panel_id in self._panels:
                logger.warning(f"Panel already exists: {panel_id}")
                return
            self._panels[panel_id] = widget
            self.panel_stack.addWidget(widget)
            logger.info(f"Added panel: {panel_id}")
        except Exception as e:
            logger.error(f"Failed to add panel {panel_id}: {e}")
            raise
    
    def remove_panel(self, panel_id: str) -> bool:
        """
        Remove a panel from the sidebar.
        
        Args:
            panel_id: Identifier of the panel
        Returns:
            True if panel was removed successfully
        """
        try:
            if panel_id not in self._panels:
                logger.warning(f"Panel not found: {panel_id}")
                return False
            widget = self._panels[panel_id]
            self.panel_stack.removeWidget(widget)
            widget.setParent(None)
            del self._panels[panel_id]
            logger.info(f"Removed panel: {panel_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove panel {panel_id}: {e}")
            return False
    
    def set_active_panel(self, panel_id: str) -> None:
        """
        Set the active panel in the sidebar.
        """
        try:
            if panel_id not in self._panels:
                logger.warning(f"Panel not found: {panel_id}")
                return
            widget = self._panels[panel_id]
            self.panel_stack.setCurrentWidget(widget)
            self._active_panel = panel_id
            self.panel_changed.emit(panel_id)
            logger.info(f"Active panel set: {panel_id}")
        except Exception as e:
            logger.error(f"Failed to set active panel {panel_id}: {e}")

    def ensure_always_visible(self) -> None:
        """
        Ensure the sidebar is always visible.
        """
        self.setVisible(True)
        self._visible = True

    def is_visible(self) -> bool:
        return self._visible
    
    def toggle_visibility(self) -> None:
        """Toggle sidebar visibility."""
        try:
            if self._visible:
                self.hide()
                self._visible = False
                logger.info("Sidebar hidden")
            else:
                self.show()
                self._visible = True
                logger.info("Sidebar shown")
        except Exception as e:
            logger.error(f"Failed to toggle sidebar visibility: {e}")

    def get_activity_bar(self):
        """
        Get the activity bar reference.
        Note: In the new design, activity bar is managed separately,
        but this method maintains compatibility.
        """
        # Return None since activity bar is now managed by MainAppWindow
        return None

    def get_active_panel_id(self) -> Optional[str]:
        """Get the currently active panel ID."""
        return self._active_panel

    def get_panels(self) -> Dict[str, QWidget]:
        """Get all registered panels."""
        return self._panels.copy()

    def get_panel_container(self):
        """
        Get the panel container (stack widget).
        Added for compatibility with activity manager.
        """
        return self.panel_stack
