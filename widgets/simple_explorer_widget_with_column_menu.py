"""
Enhanced Simple Explorer Widget with Column Management

This module extends the SimpleExplorerWidget to add column management capabilities
while preserving the clean, focused UI design.
"""

from typing import Optional, Dict, List, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal

from lg import logger
from core.explorer_settings import ExplorerSettings
from widgets.simple_explorer_widget import SimpleSearchBar, SimpleExplorerWidget
from widgets.simple_file_view_with_column_menu import SimpleFileViewWithColumnMenu


class SimpleExplorerWidgetWithColumnMenu(SimpleExplorerWidget):
    """
    Extends SimpleExplorerWidget to add column management capabilities.
    
    Features:
    - All features of SimpleExplorerWidget
    - Column management via header context menu
    - Column visibility toggle
    - Column width management
    - Content fitting functionality
    """
    
    def __init__(self, parent=None):
        # Don't call super().__init__() yet as we want to customize initialization
        QWidget.__init__(self, parent)
        self.settings = ExplorerSettings()

        # Initialize UI components with our enhanced file view
        self.search_bar = SimpleSearchBar()
        self.clear_button = QPushButton("✕")
        self.file_view = SimpleFileViewWithColumnMenu()  # Use our enhanced file view
        self.path_label = QLabel("Initializing...")
        self.up_button = QPushButton("↑ Up")

        self._setup_ui()
        self._connect_signals()
        self._load_initial_state()
        
        logger.info("SimpleExplorerWidgetWithColumnMenu initialized")
        
    # The rest of the methods are inherited from SimpleExplorerWidget
