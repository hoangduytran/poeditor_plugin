"""
Explorer Panel for Main Application

Integrates the clean SimpleExplorer widget into the main application's sidebar.
Provides the interface expected by the main application while using the clean architecture.
"""

import os
from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Signal, Slot
from lg import logger

from widgets.simple_explorer import SimpleExplorer
from panels.panel_interface import PanelInterface


class ExplorerPanel(PanelInterface):
    """
    Main application explorer panel using clean architecture.
    
    This panel integrates the SimpleExplorer widget into the main application
    and provides the interface expected by the main window and sidebar manager.
    """
    
    # Signals expected by main application
    file_opened = Signal(str)
    location_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api = None  # Will be set by main application
        
        self._setup_ui()
        self._connect_signals()
        
        # Start at user home directory
        self.set_path(str(Path.home()))
        
        logger.info("ExplorerPanel initialized with clean architecture")
    
    def _setup_ui(self):
        """Setup the panel UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 4)
        
        # Title
        title_label = QLabel("EXPLORER")
        title_label.setObjectName("panel_title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Quick navigation buttons
        self.home_button = QPushButton("🏠")
        self.home_button.setMaximumWidth(30)
        self.home_button.setToolTip("Go to Home Directory")
        
        self.up_button = QPushButton("⬆️")
        self.up_button.setMaximumWidth(30)
        self.up_button.setToolTip("Go to Parent Directory")
        
        header_layout.addWidget(self.home_button)
        header_layout.addWidget(self.up_button)
        
        layout.addLayout(header_layout)
        
        # Main explorer widget
        self.explorer = SimpleExplorer()
        layout.addWidget(self.explorer)
    
    def _connect_signals(self):
        """Connect internal signals."""
        # Connect explorer signals to panel signals (for main app)
        self.explorer.file_opened.connect(self.file_opened.emit)
        self.explorer.directory_changed.connect(self._on_directory_changed)
        
        # Connect navigation buttons
        self.home_button.clicked.connect(self._go_home)
        self.up_button.clicked.connect(self._go_up)
    
    @Slot(str)
    def _on_directory_changed(self, path: str):
        """Handle directory changes in the explorer."""
        self.location_changed.emit(path)
        logger.info(f"Explorer panel navigated to: {path}")
    
    @Slot()
    def _go_home(self):
        """Navigate to home directory."""
        home_path = str(Path.home())
        self.set_path(home_path)
        logger.info("Navigated to home directory")
    
    @Slot()
    def _go_up(self):
        """Navigate to parent directory."""
        current_path = Path(self.explorer.get_current_path())
        parent_path = current_path.parent
        
        if parent_path != current_path:  # Avoid root directory issues
            self.set_path(str(parent_path))
            logger.info(f"Navigated up to: {parent_path}")
    
    def set_path(self, path: str):
        """
        Set the current directory path.
        
        Args:
            path: Directory path to navigate to
        """
        self.explorer.set_path(path)
    
    def get_current_path(self) -> str:
        """Get the current directory path."""
        return self.explorer.get_current_path()
    
    def refresh(self):
        """Refresh the explorer view."""
        self.explorer.refresh()
        logger.info("Explorer panel refreshed")
    
    # PanelInterface implementation
    def set_api(self, api):
        """Set the plugin API (required by main application)."""
        self.api = api
        logger.info("Explorer panel API set")
    
    def get_title(self) -> str:
        """Get panel title."""
        return "Explorer"
    
    def get_icon(self) -> Optional[str]:
        """Get panel icon."""
        return "explorer"
    
    def activate(self):
        """Called when panel is activated."""
        self.refresh()
        logger.debug("Explorer panel activated")
    
    def deactivate(self):
        """Called when panel is deactivated."""
        logger.debug("Explorer panel deactivated")
    
    # Additional methods for main application integration
    def open_path(self, path: str):
        """Open a specific path (used by main application)."""
        if os.path.isdir(path):
            self.set_path(path)
        elif os.path.isfile(path):
            # Navigate to directory and select file
            directory = os.path.dirname(path)
            self.set_path(directory)
            # TODO: Add file selection in future version
        
        logger.info(f"Explorer opened path: {path}")
    
    def get_selected_files(self) -> list:
        """Get currently selected files."""
        return self.explorer.get_selected_files()
    
    def apply_filter(self, pattern: str):
        """Apply a filter pattern."""
        self.explorer.filter_input.setText(pattern)
        self.explorer._apply_filter()
        logger.info(f"Applied filter: {pattern}")
    
    def clear_filter(self):
        """Clear the current filter."""
        self.explorer._clear_filter()
        logger.info("Filter cleared")


# Export for main application
__all__ = ['ExplorerPanel']
