"""
Enhanced Simple File View with Column Header Context Menu

This module extends the SimpleFileView class to add column header context menu support,
allowing users to toggle column visibility and manage column widths.
"""

from typing import Optional, Dict, List, Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView

from lg import logger
from widgets.simple_explorer_widget import SimpleFileView
from widgets.explorer_header_navigation_integration import HeaderNavigationWidgetIntegration
from services.column_manager_service_integration import ColumnManagerService


class SimpleFileViewWithColumnMenu(SimpleFileView):
    """
    Extends SimpleFileView to add column header context menu support.
    
    This class adds:
    - Column management capabilities via context menu
    - Column visibility toggle
    - Column width management
    - Content fitting functionality
    """
    
    def __init__(self, parent=None):
        # Initialize parent class first
        super().__init__(parent)
        
        # Create column manager service
        self.column_manager = ColumnManagerService()
        
        # Set up header navigation
        self._setup_header_navigation()
        
        # Apply initial column settings
        self._apply_initial_column_settings()
        
    def _setup_header_navigation(self):
        """Set up the header navigation widget with column management."""
        # Create header navigation widget
        self.header_nav = HeaderNavigationWidgetIntegration(Qt.Orientation.Horizontal, self)
        
        # Set it as the header for this view
        self.setHeader(self.header_nav)
        
        # Inject column manager service
        self.header_nav.inject_column_manager(self.column_manager)
        
        # Connect column visibility changed signal
        self.header_nav.column_visibility_changed.connect(self._on_column_visibility_changed)
        
        # Connect navigation requested signal
        self.header_nav.navigation_requested.connect(self._on_navigation_requested)
        
        logger.debug("Header navigation with column management set up")
        
    def _apply_initial_column_settings(self):
        """Apply initial column settings from the column manager."""
        if not self.column_manager:
            return
            
        # Get visible columns
        visible_columns = self.column_manager.get_visible_columns()
        
        # Show/hide columns based on settings
        for col_id, col_info in self.column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns
            
            if visible:
                self.showColumn(model_column)
            else:
                self.hideColumn(model_column)
                
        # Apply column widths
        if self.column_manager.get_fit_content_enabled():
            # If fit content is enabled, resize columns to fit content
            for section in range(self.header().count()):
                self.resizeColumnToContents(section)
        else:
            # Otherwise apply saved/default widths
            for col_id, col_info in self.column_manager.get_available_columns().items():
                model_column = col_info.get("model_column", 0)
                width = self.column_manager.get_column_width(col_id)
                self.setColumnWidth(model_column, width)
                
        logger.debug("Applied initial column settings")
        
    def _on_column_visibility_changed(self, visible_columns: List[str]):
        """
        Handle column visibility changes from header navigation.
        
        Args:
            visible_columns: List of visible column IDs
        """
        if not self.column_manager:
            return
            
        # Show/hide columns based on settings
        for col_id, col_info in self.column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns
            
            if visible:
                self.showColumn(model_column)
            else:
                self.hideColumn(model_column)
                
        logger.debug(f"Column visibility updated: {visible_columns}")
    
    def _on_navigation_requested(self, path: str):
        """
        Handle navigation requests from header navigation.
        
        Args:
            path: Path to navigate to
        """
        logger.info(f"Navigation requested to path: {path}")
        
        # Use our own set_current_path method
        self.set_current_path(path)
