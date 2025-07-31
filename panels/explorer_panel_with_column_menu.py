"""
Explorer panel with column management support.

Extends the standard explorer panel with column header context menu functionality.
"""

from typing import Optional
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Signal

from panels.panel_interface import PanelInterface
from widgets.simple_explorer_widget_with_column_menu import SimpleExplorerWidgetWithColumnMenu
from lg import logger


class ExplorerPanelWithColumnMenu(PanelInterface):
    """Explorer panel with column management support."""
    
    # Signals
    file_opened = Signal(str)
    location_changed = Signal(str)
    
    def __init__(self, parent: Optional[PanelInterface] = None):
        super().__init__(parent)
        self._setup_ui()
        logger.info("ExplorerPanelWithColumnMenu initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for clean look

        # Add the enhanced explorer widget
        self.explorer_widget = SimpleExplorerWidgetWithColumnMenu()
        layout.addWidget(self.explorer_widget)

        # Connect explorer signals to panel signals
        self.explorer_widget.file_opened.connect(self.file_opened.emit)
        self.explorer_widget.location_changed.connect(self.location_changed.emit)

    def on_activate(self):
        """Called when the panel is activated."""
        super().on_activate()
        logger.debug("Enhanced explorer panel activated")
        # Optionally refresh the explorer when activated

    def on_deactivate(self):
        """Called when the panel is deactivated."""
        super().on_deactivate()
        logger.debug("Enhanced explorer panel deactivated")
        
    def set_api(self, api):
        """Set the plugin API for enhanced functionality."""
        super().set_api(api)
        # No additional API usage needed for now
