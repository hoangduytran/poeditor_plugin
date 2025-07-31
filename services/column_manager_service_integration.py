"""
Column Manager Service Integration

This module integrates the column manager service with the current explorer implementation.
It extends the existing SimpleExplorerWidget to add column management capabilities.
"""

from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal

from lg import logger
from core.explorer_settings import ExplorerSettings


class ColumnManagerService(QObject):
    """
    Service for managing column visibility and properties in explorer views.
    
    This service manages:
    - Column visibility (which columns are shown/hidden)
    - Column width properties
    - Content fitting settings
    - Persistence of column settings between sessions
    
    Signals:
        column_visibility_changed: Emitted when visibility of any column changes
        column_width_changed: Emitted when a column's width is changed
        fit_content_setting_changed: Emitted when fit content setting changes
    """
    
    # Signals
    column_visibility_changed = Signal(list)  # List of visible column IDs
    column_width_changed = Signal(str, int)   # Column ID and new width
    fit_content_setting_changed = Signal(bool)  # New setting value
    
    def __init__(self):
        """Initialize the column manager service."""
        super().__init__()
        
        # Use explorer settings for persistence
        self.settings = ExplorerSettings()
        
        # Required columns (cannot be hidden)
        self._required_columns = ["name"]
        
        # Define the available columns with their properties
        self._available_columns = {
            "name": {
                "title": "Name",
                "default_width": 250,
                "model_column": 0,  # Column index in the model
                "required": True
            },
            "size": {
                "title": "Size",
                "default_width": 100,
                "model_column": 1,
                "required": False
            },
            "type": {
                "title": "Type",
                "default_width": 120,
                "model_column": 2,
                "required": False
            },
            "modified": {
                "title": "Modified",
                "default_width": 180,
                "model_column": 3,
                "required": False
            }
        }
        
        # Initialize internal state
        self._initialize_columns()
        
        logger.debug("ColumnManagerService initialized")
    
    def _initialize_columns(self):
        """Initialize column visibility and properties from settings."""
        # Load visible columns from settings or use defaults
        visible_columns = self.settings.get("explorer_visible_columns")
        if not visible_columns:
            # By default, show all columns
            visible_columns = list(self._available_columns.keys())
            self._save_visible_columns(visible_columns)
        
        # Ensure required columns are always visible
        for required_col in self._required_columns:
            if required_col not in visible_columns:
                visible_columns.append(required_col)
                self._save_visible_columns(visible_columns)
                
        # Load fit content setting
        fit_content = self.settings.get("explorer_fit_column_content")
        if fit_content is None:
            # Default to False - don't auto-resize columns
            fit_content = False
            self.settings.set("explorer_fit_column_content", fit_content)
            
        # Load custom column widths
        self._column_widths = self.settings.get("explorer_column_widths") or {}
        
        logger.debug(f"Column manager initialized with {len(visible_columns)} visible columns")
    
    def get_available_columns(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available columns with their properties.
        
        Returns:
            Dict mapping column IDs to their property dictionaries
        """
        return self._available_columns
    
    def get_visible_columns(self) -> List[str]:
        """
        Get the list of currently visible column IDs.
        
        Returns:
            List of column IDs that should be visible
        """
        visible_columns = self.settings.get("explorer_visible_columns") or []
        
        # Ensure required columns are always included
        for required_col in self._required_columns:
            if required_col not in visible_columns:
                visible_columns.append(required_col)
                
        return visible_columns
    
    def set_column_visibility(self, column_id: str, visible: bool) -> bool:
        """
        Set the visibility of a specific column.
        
        Args:
            column_id: ID of the column to modify
            visible: Whether the column should be visible
            
        Returns:
            bool: True if visibility was changed, False otherwise
        """
        # Check if column exists
        if column_id not in self._available_columns:
            logger.warning(f"Cannot set visibility for unknown column: {column_id}")
            return False
            
        # Don't allow hiding required columns
        if not visible and column_id in self._required_columns:
            logger.warning(f"Cannot hide required column: {column_id}")
            return False
            
        # Get current visible columns
        visible_columns = self.get_visible_columns()
        
        # Check if state is already as requested
        is_currently_visible = column_id in visible_columns
        if is_currently_visible == visible:
            return False  # No change needed
            
        # Update visibility
        if visible:
            if column_id not in visible_columns:
                visible_columns.append(column_id)
        else:
            if column_id in visible_columns:
                visible_columns.remove(column_id)
                
        # Save changes
        self._save_visible_columns(visible_columns)
        
        # Emit signal
        self.column_visibility_changed.emit(visible_columns)
        
        return True
    
    def _save_visible_columns(self, columns: List[str]) -> None:
        """
        Save the visible columns list to settings.
        
        Args:
            columns: List of visible column IDs
        """
        self.settings.set("explorer_visible_columns", columns)
        logger.debug(f"Saved visible columns: {columns}")
    
    def get_fit_content_enabled(self) -> bool:
        """
        Check if content fitting is enabled.
        
        Returns:
            bool: True if content fitting is enabled, False otherwise
        """
        return bool(self.settings.get("explorer_fit_column_content"))
    
    def set_fit_content_enabled(self, enabled: bool) -> None:
        """
        Set the fit content setting.
        
        Args:
            enabled: Whether columns should automatically fit their content
        """
        # Save setting
        self.settings.set("explorer_fit_column_content", enabled)
        
        # Emit signal
        self.fit_content_setting_changed.emit(enabled)
        
        logger.debug(f"Set fit content enabled: {enabled}")
    
    def get_column_width(self, column_id: str) -> int:
        """
        Get the width for a specific column.
        
        Args:
            column_id: ID of the column
            
        Returns:
            int: Column width in pixels
        """
        # Check if we have a custom width
        widths = self.settings.get("explorer_column_widths") or {}
        if column_id in widths:
            return widths[column_id]
            
        # Fall back to default width
        if column_id in self._available_columns:
            return self._available_columns[column_id]["default_width"]
            
        # Default fallback
        return 100
    
    def set_column_width(self, column_id: str, width: int) -> None:
        """
        Set the width for a specific column.
        
        Args:
            column_id: ID of the column
            width: New width in pixels
        """
        if column_id not in self._available_columns:
            logger.warning(f"Cannot set width for unknown column: {column_id}")
            return
            
        # Get current widths
        widths = self.settings.get("explorer_column_widths") or {}
        
        # Update width
        widths[column_id] = width
        
        # Save changes
        self.settings.set("explorer_column_widths", widths)
        
        # Emit signal
        self.column_width_changed.emit(column_id, width)
        
        logger.debug(f"Saved column width for '{column_id}': {width}px")
    
    def reset_column_widths(self) -> None:
        """Reset all column widths to their default values."""
        # Clear saved widths
        self.settings.set("explorer_column_widths", {})
        
        # Emit signals for each column
        for column_id, props in self._available_columns.items():
            default_width = props["default_width"]
            self.column_width_changed.emit(column_id, default_width)
            
        logger.debug("Reset all column widths to defaults")
        
    def get_column_id_from_model_column(self, model_column: int) -> Optional[str]:
        """
        Get the column ID corresponding to a model column index.
        
        Args:
            model_column: The column index in the model
            
        Returns:
            str: The corresponding column ID, or None if not found
        """
        for col_id, props in self._available_columns.items():
            if props["model_column"] == model_column:
                return col_id
        return None
