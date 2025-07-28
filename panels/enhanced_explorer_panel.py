"""
Enhanced Explorer Panel with context menu and drag & drop support.

This enhances the default Explorer panel with context menu functionality
and drag & drop capabilities for file operations.
"""

from typing import Optional
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Signal

from lg import logger
from panels.panel_interface import PanelInterface
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget


class EnhancedExplorerPanel(PanelInterface):
    """
    Enhanced Explorer panel with context menu and drag & drop support.
    
    This panel extends the standard Explorer panel with:
    1. Context menu functionality for file operations
    2. Drag & drop capabilities for intuitive file management
    3. Integration with file operations services
    """
    
    # Signals
    file_opened = Signal(str)
    location_changed = Signal(str)
    
    def __init__(self, parent: Optional[PanelInterface] = None):
        super().__init__(parent)
        self._setup_ui()
        logger.info("EnhancedExplorerPanel initialized")
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for clean look
        
        # Add the enhanced explorer widget
        self.explorer_widget = EnhancedExplorerWidget()
        layout.addWidget(self.explorer_widget)
        
        # Connect explorer signals to panel signals
        self.explorer_widget.file_view.file_activated.connect(self.file_opened.emit)
        self.explorer_widget.file_view.directory_changed.connect(self.location_changed.emit)
    
    def on_activate(self):
        """Called when the panel is activated."""
        super().on_activate()
        logger.debug("Enhanced explorer panel activated")
        # Optionally refresh the explorer when activated
    
    def on_deactivate(self):
        """Called when the panel is deactivated."""
        super().on_deactivate()
        logger.debug("Enhanced explorer panel deactivated")
