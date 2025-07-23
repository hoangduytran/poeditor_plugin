"""
Explorer panel for POEditor.

Provides file and directory navigation functionality.
"""

from typing import Optional
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Signal

from panels.panel_interface import PanelInterface
from lg import logger


class ExplorerPanel(PanelInterface):
    """Explorer panel for navigating files and directories."""
    
    # Signals
    file_opened = Signal(str)
    location_changed = Signal(str)
    
    def __init__(self, parent: Optional[PanelInterface] = None):
        super().__init__(parent)
        self._setup_ui()
        logger.info("ExplorerPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Placeholder content
        label = QLabel("Explorer Panel\n\nThis is a placeholder for the Explorer panel.")
        layout.addWidget(label)
        
        # Set layout properties
        layout.setContentsMargins(10, 10, 10, 10)
    
    def on_activate(self):
        """Called when the panel is activated."""
        super().on_activate()
        logger.debug("Explorer panel activated")
    
    def on_deactivate(self):
        """Called when the panel is deactivated."""
        super().on_deactivate()
        logger.debug("Explorer panel deactivated")
