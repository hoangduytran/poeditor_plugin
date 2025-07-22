"""
Panel interface base class for the PySide POEditor plugin.

This module defines the base class for all panel implementations.
"""

from lg import logger
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class PanelInterface(QWidget):
    """
    Base class for all panels in the POEditor plugin.
    
    All panel implementations should inherit from this class
    to ensure consistent behavior and interface.
    """
    
    # Common signals that panels can emit
    panel_ready = Signal()
    panel_closed = Signal()
    
    def __init__(self, parent=None, panel_id=None):
        """
        Initialize the panel.
        
        Args:
            parent: The parent widget
            panel_id: The ID of this panel
        """
        super().__init__(parent)
        self.panel_id = panel_id
        self.api = None
        
    def set_api(self, api):
        """
        Set the API for this panel.
        
        Args:
            api: The API instance
        """
        self.api = api
        
    def on_show(self):
        """
        Called when the panel is shown.
        
        Panels can override this method to perform
        initialization when shown.
        """
        logger.info(f"Panel {self.panel_id} shown")
        
    def on_hide(self):
        """
        Called when the panel is hidden.
        
        Panels can override this method to perform
        cleanup when hidden.
        """
        logger.info(f"Panel {self.panel_id} hidden")
        
    def on_close(self):
        """
        Called when the panel is about to be closed.
        
        Panels can override this method to perform
        cleanup before being destroyed.
        
        Returns:
            bool: True if the panel can be closed, False to prevent closing
        """
        logger.info(f"Panel {self.panel_id} closing")
        self.panel_closed.emit()
        return True
        
    def handle_event(self, event_name, event_data):
        """
        Handle an event from the application.
        
        Panels can override this method to respond to events.
        
        Args:
            event_name: The name of the event
            event_data: The event data
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Default implementation doesn't handle any events
        return False
