"""
Explorer Header Navigation Widget Integration

This module provides a HeaderNavigationWidget that integrates with the existing SimpleExplorerWidget
to add column management and navigation functionality to the header.
"""

import logging
import os
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import QHeaderView, QMenu, QMessageBox, QTreeView, QWidget
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction

from lg import logger
from services.column_manager_service_integration import ColumnManagerService


class HeaderNavigationWidgetIntegration(QHeaderView):
    """
    Enhanced header view that adds column management functionality to table headers.
    
    When right-clicking on the header, shows a context menu with:
    - Column management options (visibility, fit content)
    - Navigation options (quick locations, bookmarks)
    
    Signals:
        column_visibility_changed: Emitted when column visibility changes
        navigation_requested: Emitted when navigation to a path is requested
    """
    
    # Signals
    column_visibility_changed = Signal(list)  # List of visible column IDs
    navigation_requested = Signal(str)  # Path to navigate to
    
    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        """
        Initialize the header navigation widget.
        
        Args:
            orientation: Header orientation (Horizontal or Vertical)
            parent: Parent widget
        """
        super().__init__(orientation, parent)
        
        # Services (will be injected)
        self._column_manager: Optional[ColumnManagerService] = None
        
        # Setup navigation context menu
        self._setup_context_menu()
        
    def _setup_context_menu(self) -> None:
        """Setup the context menu for the header."""
        # Enable custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def inject_column_manager(self, column_manager: ColumnManagerService) -> None:
        """
        Inject column manager service into the header.
        
        Args:
            column_manager: Column management service
        """
        self._column_manager = column_manager
        
        # Connect to section resize signal if column manager is available
        if self._column_manager:
            self._connect_section_resize_signal()
            
    def _connect_section_resize_signal(self) -> None:
        """Connect to the section resize signal to track column width changes."""
        self.sectionResized.connect(self._handle_section_resize)
        logger.debug("Connected to section resize signal")
            
    def _show_context_menu(self, position: QPoint) -> None:
        """
        Show the context menu.
        
        Args:
            position: Position where the context menu was requested
        """
        if not self._column_manager:
            logger.info("Column manager not available - cannot show context menu")
            return
            
        logger.info(f"Creating column context menu at position: {position}")
        menu = QMenu(self)
        
        # Add navigation section first
        self._add_navigation_section(menu)
        
        # Add a separator
        menu.addSeparator()
        
        # Add column management section
        self._add_column_management_section(menu)
        
        # Show the menu at the global position
        global_position = self.mapToGlobal(position)
        logger.info(f"Showing menu at global position: {global_position}")
        
        # Make menu more visible with styling
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 20px;
                margin: 2px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QMenu::separator {
                height: 2px;
                background-color: #555;
                margin: 5px;
            }
        """)
        
        result = menu.exec(global_position)
        logger.info(f"Menu exec result: {result}")
        if result:
            logger.info(f"Menu action triggered: {result.text()}")
        else:
            logger.info("Menu dismissed without selection")
    
    def _add_column_management_section(self, menu: QMenu) -> None:
        """
        Add column management section to the menu.
        
        Args:
            menu: The menu to add the section to
        """
        if not self._column_manager:
            return
            
        # Create Column Management submenu
        columns_menu = menu.addMenu("📋 Column Management")
        
        # Column visibility options
        for col_id, col_info in self._column_manager.get_available_columns().items():
            column_title = col_info.get("title", col_id.title())
            
            # Create checkbox action
            action = QAction(column_title, self)
            action.setCheckable(True)
            
            # Set checked state based on current visibility
            visible_columns = self._column_manager.get_visible_columns()
            action.setChecked(col_id in visible_columns)
            
            # Disable checkbox for required columns
            if col_id in self._column_manager._required_columns:
                action.setEnabled(False)
                
            # Connect to toggle action
            action.triggered.connect(lambda checked, cid=col_id: self._toggle_column_visibility(cid, checked))
            columns_menu.addAction(action)
            
        # Add separator
        columns_menu.addSeparator()
        
        # Fit Content toggle
        fit_content_action = QAction("Fit Content to Values", self)
        fit_content_action.setCheckable(True)
        fit_content_action.setChecked(self._column_manager.get_fit_content_enabled())
        fit_content_action.triggered.connect(self._toggle_fit_content)
        columns_menu.addAction(fit_content_action)
        
        # Reset Column Widths action
        reset_widths_action = QAction("Reset Column Widths", self)
        reset_widths_action.triggered.connect(self._reset_column_widths)
        columns_menu.addAction(reset_widths_action)
        
        logger.debug("Column management section added to context menu")
    
    def _toggle_column_visibility(self, column_id: str, visible: bool) -> None:
        """
        Toggle column visibility.
        
        Args:
            column_id: ID of the column to toggle
            visible: Whether the column should be visible
        """
        if not self._column_manager:
            return
            
        # Update visibility in column manager
        success = self._column_manager.set_column_visibility(column_id, visible)
        
        if success:
            # Get updated visibility and emit our own signal
            visible_columns = self._column_manager.get_visible_columns()
            self.column_visibility_changed.emit(visible_columns)
            logger.debug(f"Column visibility toggled - '{column_id}' is now {'visible' if visible else 'hidden'}")
    
    def _toggle_fit_content(self, enabled: bool) -> None:
        """
        Toggle fit content mode.
        
        Args:
            enabled: Whether fit content should be enabled
        """
        if not self._column_manager:
            return
            
        self._column_manager.set_fit_content_enabled(enabled)
        
        if enabled:
            # If enabled, resize columns to fit content now
            self._resize_columns_to_fit_content()
        
        logger.debug(f"Fit content {'enabled' if enabled else 'disabled'}")
    
    def _resize_columns_to_fit_content(self) -> None:
        """Resize all columns to fit their content."""
        # Get the tree view (parent)
        tree_view = self.parent()
        if not tree_view or not isinstance(tree_view, QTreeView):
            logger.warning("Cannot resize columns - parent is not a tree view")
            return
            
        # Resize each column
        for section in range(self.count()):
            tree_view.resizeColumnToContents(section)
            
        logger.debug(f"Resized {self.count()} columns to fit content")
    
    def _reset_column_widths(self) -> None:
        """Reset column widths to defaults."""
        if not self._column_manager:
            return
            
        self._column_manager.reset_column_widths()
        logger.debug("Column widths reset to defaults")
    
    def _handle_section_resize(self, logical_index: int, old_size: int, new_size: int) -> None:
        """
        Handle section resize events to update column widths.
        
        Args:
            logical_index: Index of the resized column
            old_size: Previous column width
            new_size: New column width
        """
        if not self._column_manager:
            return
            
        # Get column ID from model column index
        column_id = self._column_manager.get_column_id_from_model_column(logical_index)
        if column_id:
            # Save the new width
            self._column_manager.set_column_width(column_id, new_size)
            logger.debug(f"Saved custom width for column '{column_id}': {new_size}px")
            
    def _add_navigation_section(self, menu: QMenu) -> None:
        """
        Add navigation section to the menu with quick location options.
        
        Args:
            menu: The menu to add the section to
        """
        # Create Navigation submenu
        navigation_menu = menu.addMenu("🧭 Quick Navigation")
        
        # Get home directory
        home_path = os.path.expanduser("~")
        
        # Add common locations
        locations = [
            {"name": "Home", "icon": "🏠", "path": home_path},
            {"name": "Root", "icon": "💽", "path": "/"},
            {"name": "Desktop", "icon": "🖥️", "path": os.path.join(home_path, "Desktop")},
            {"name": "Documents", "icon": "📁", "path": os.path.join(home_path, "Documents")},
            {"name": "Downloads", "icon": "📥", "path": os.path.join(home_path, "Downloads")},
            {"name": "Applications", "icon": "📱", "path": "/Applications"},
        ]
        
        # Add each location to the menu
        for location in locations:
            action_text = f"{location['icon']} {location['name']}"
            action = QAction(action_text, self)
            # Store path in the action's data
            action.setData(location["path"])
            # Connect to our navigation handler
            action.triggered.connect(lambda checked=False, path=location["path"]: 
                                    self._navigate_to_location(path))
            navigation_menu.addAction(action)
            
        # Add separator before special actions
        navigation_menu.addSeparator()
        
        # Add "Go to Path..." action (in a future implementation, this could show a dialog)
        goto_action = QAction("📍 Go to Path...", self)
        goto_action.triggered.connect(self._show_goto_path_dialog)
        navigation_menu.addAction(goto_action)
        
        logger.debug("Navigation section added to context menu")
    
    def _navigate_to_location(self, path: str) -> None:
        """
        Navigate to a specific location.
        
        Args:
            path: Path to navigate to
        """
        if os.path.exists(path):
            logger.info(f"Navigating to: {path}")
            self.navigation_requested.emit(path)
        else:
            logger.warning(f"Cannot navigate to non-existent path: {path}")
            QMessageBox.warning(self, "Navigation Error", 
                               f"Cannot navigate to {path}.\nThe location does not exist.")
    
    def _show_goto_path_dialog(self) -> None:
        """Show a dialog to enter a custom path for navigation."""
        from widgets.goto_path_dialog import GotoPathDialog
        from core.explorer_settings import ExplorerSettings
        
        # Get recent paths from settings
        settings = ExplorerSettings()
        recent_paths = settings.get("explorer_path_history", [])
        
        # Create and configure the dialog
        dialog = GotoPathDialog(parent=self, recent_paths=recent_paths)
        
        # Get current path from the parent view if possible
        tree_view = self.parent()
        current_path = None
        
        # Try to get the current path from the file view or its model
        from PySide6.QtWidgets import QTreeView
        
        # Check if we have a tree view
        if isinstance(tree_view, QTreeView):
            model = tree_view.model()
            # Check if model has rootPath method (common in file system models)
            if hasattr(model, "rootPath") and callable(getattr(model, "rootPath", None)):
                try:
                    # Use getattr to avoid lint errors when accessing dynamically
                    rootPath = getattr(model, "rootPath")
                    current_path = rootPath()
                    logger.debug(f"Got current path from model: {current_path}")
                except Exception as e:
                    logger.error(f"Error getting root path from model: {e}")
            else:
                logger.debug("Tree view model does not have rootPath method")
        else:
            logger.debug("Parent is not a QTreeView")
            
        if current_path:
            dialog.set_path(current_path)
            
        # Connect the path_accepted signal
        dialog.path_accepted.connect(self._navigate_to_location)
        
        # Show the dialog (modal)
        dialog.setModal(True)
        dialog.show()
        
        # Save updated history when dialog closes
        dialog.finished.connect(lambda result: self._save_path_history(dialog.get_recent_paths()))
        
    def _save_path_history(self, paths: list) -> None:
        """
        Save path history to settings.
        
        Args:
            paths: List of paths to save
        """
        try:
            from core.explorer_settings import ExplorerSettings
            settings = ExplorerSettings()
            
            # Limit number of paths to reasonable amount (e.g., 20)
            max_history = settings.get("explorer_max_path_history", 20)
            if len(paths) > max_history:
                paths = paths[:max_history]
                
            # Save the paths
            settings.set("explorer_path_history", paths)
            settings.save()
            logger.debug(f"Saved {len(paths)} paths to history")
        except Exception as e:
            logger.error(f"Failed to save path history: {e}")
        