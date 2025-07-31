"""
Column Manager Service

This service manages column visibility and properties for the explorer view.
It provides methods to toggle column visibility, manage column widths,
and control content fitting behavior.
"""

from typing import Dict, List, Any, Optional
from core.explorer_settings import ExplorerSettings
from lg import logger

class ColumnManagerService:
    """
    Service for managing explorer columns visibility and properties.
    
    Features:
    - Column visibility management
    - Column width tracking
    - Content fitting preferences
    - Settings persistence
    
    This service ensures that:
    1. Required columns (like "Name") cannot be hidden
    2. Column settings persist between application sessions
    3. Column visibility changes are tracked centrally
    """
    
    def __init__(self):
        """Initialize the column manager service."""
        self.settings = ExplorerSettings()
        self._initialize_columns()
        logger.debug("ColumnManagerService initialized")
        
    def _initialize_columns(self) -> None:
        """Initialize column definitions and load settings."""
        # Define available columns with their properties
        self._columns = {
            "name": {
                "display": "Name",
                "required": True,
                "default_width": 250,
                "model_column": 0
            },
            "size": {
                "display": "Size",
                "required": False,
                "default_width": 100,
                "model_column": 1
            },
            "type": {
                "display": "Type",
                "required": False,
                "default_width": 120,
                "model_column": 2
            },
            "modified": {
                "display": "Modified Date",
                "required": False,
                "default_width": 180,
                "model_column": 3
            }
        }
        
        # Load visibility settings or use defaults
        self._visible_columns = self.settings.get(
            "explorer_visible_columns", 
            ["name", "size", "type", "modified"]
        )
        
        # Ensure required columns are always visible
        for col_id, col_info in self._columns.items():
            if col_info.get("required", False) and col_id not in self._visible_columns:
                self._visible_columns.append(col_id)
                
        # Load content fitting setting
        self._fit_content = self.settings.get("explorer_fit_column_content", False)
        
        # Load custom column widths
        self._column_widths = self.settings.get("explorer_column_widths", {})
        
        logger.debug(f"Column manager initialized with {len(self._visible_columns)} visible columns")
        
    def get_available_columns(self) -> Dict[str, Dict[str, Any]]:
        """
        Get dictionary of all available columns with their properties.
        
        Returns:
            Dict mapping column IDs to their properties
        """
        return self._columns.copy()
        
    def get_column_info(self, column_id: str) -> Dict[str, Any]:
        """
        Get information about a specific column.
        
        Args:
            column_id: The column identifier
            
        Returns:
            Dict with column properties or empty dict if not found
        """
        return self._columns.get(column_id, {}).copy()
        
    def get_visible_columns(self) -> List[str]:
        """
        Get list of visible column IDs.
        
        Returns:
            List of column IDs that are currently visible
        """
        return self._visible_columns.copy()
        
    def is_column_visible(self, column_id: str) -> bool:
        """
        Check if a column is currently visible.
        
        Args:
            column_id: The column identifier
            
        Returns:
            True if the column is visible, False otherwise
        """
        return column_id in self._visible_columns
        
    def set_column_visibility(self, column_id: str, visible: bool) -> bool:
        """
        Set column visibility.
        
        Args:
            column_id: The column identifier
            visible: Whether the column should be visible
            
        Returns:
            bool: True if visibility was changed, False otherwise
        """
        # Check if column exists
        if column_id not in self._columns:
            logger.warning(f"Cannot set visibility for unknown column: {column_id}")
            return False
            
        # Check if column is required
        if self._columns[column_id].get("required", False) and not visible:
            logger.warning(f"Cannot hide required column: {column_id}")
            return False
            
        # Update visibility
        was_visible = column_id in self._visible_columns
        
        if visible and not was_visible:
            self._visible_columns.append(column_id)
            self._save_visible_columns()
            return True
        elif not visible and was_visible:
            self._visible_columns.remove(column_id)
            self._save_visible_columns()
            return True
            
        return False
        
    def _save_visible_columns(self) -> None:
        """Save visible columns to settings."""
        self.settings.set("explorer_visible_columns", self._visible_columns)
        logger.debug(f"Saved visible columns: {self._visible_columns}")
        
    def get_fit_content_enabled(self) -> bool:
        """
        Check if fit content to values is enabled.
        
        Returns:
            True if columns should automatically fit content, False otherwise
        """
        return self._fit_content
        
    def set_fit_content_enabled(self, enabled: bool) -> None:
        """
        Set fit content to values setting.
        
        Args:
            enabled: Whether content fitting should be enabled
        """
        self._fit_content = enabled
        self.settings.set("explorer_fit_column_content", enabled)
        logger.debug(f"Set fit content enabled: {enabled}")
        
    def get_column_width(self, column_id: str) -> int:
        """
        Get column width (custom or default).
        
        Args:
            column_id: The column identifier
            
        Returns:
            Width in pixels
        """
        if column_id in self._column_widths:
            return self._column_widths[column_id]
        return self._columns.get(column_id, {}).get("default_width", 100)
        
    def set_column_width(self, column_id: str, width: int) -> None:
        """
        Save custom column width.
        
        Args:
            column_id: The column identifier
            width: Width in pixels
        """
        if column_id not in self._columns:
            logger.warning(f"Cannot set width for unknown column: {column_id}")
            return
            
        self._column_widths[column_id] = width
        self.settings.set("explorer_column_widths", self._column_widths)
        logger.debug(f"Saved column width for '{column_id}': {width}px")
        
    def reset_column_widths(self) -> None:
        """Reset all column widths to defaults."""
        self._column_widths = {}
        self.settings.set("explorer_column_widths", {})
        logger.debug("Reset all column widths to defaults")
        
    def get_model_column(self, column_id: str) -> Optional[int]:
        """
        Get the model column index for the given column ID.
        
        Args:
            column_id: The column identifier
            
        Returns:
            Model column index or None if column not found
        """
        column_info = self._columns.get(column_id, {})
        return column_info.get("model_column")
        
    def get_column_id_by_model_index(self, model_index: int) -> Optional[str]:
        """
        Get column ID by model index.
        
        Args:
            model_index: The model column index
            
        Returns:
            Column ID or None if not found
        """
        for col_id, col_info in self._columns.items():
            if col_info.get("model_column") == model_index:
                return col_id
        return None
