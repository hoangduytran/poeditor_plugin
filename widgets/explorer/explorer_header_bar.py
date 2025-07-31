"""
Explorer Header Bar module provides the HeaderNavigationWidget that enhances QHeaderView
with navigation context menu functionality for the Explorer panel.
"""

import logging
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import QHeaderView, QMenu, QWidget, QWidgetAction, QHBoxLayout, QTreeView
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QAction

from lg import logger
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService
from services.column_manager_service import ColumnManagerService
from PySide6.QtWidgets import QHeaderView, QMenu, QMessageBox, QTreeView
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction

from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService
from services.column_manager_service import ColumnManagerService
from widgets.explorer.goto_path_dialog import show_goto_path_dialog
from widgets.explorer.bookmark_manager_dialog import show_bookmark_manager

logger = logging.getLogger(__name__)

from typing import Optional, List
from PySide6.QtWidgets import QHeaderView, QMenu, QWidget, QWidgetAction, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QAction

from lg import logger
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService


class HeaderNavigationWidget(QHeaderView):
    """
    Enhanced header view that adds navigation functionality to table headers.
    
    When right-clicking on the header, shows a context menu with:
    - Navigation actions (Back, Forward, Up, Home)
    - Quick locations and bookmarks
    - Current path display and navigation
    - Column management options (visibility, fit content)
    
    Signals:
        navigation_requested: Emitted when navigation to a path is requested
        path_changed: Emitted when current path changes
        column_visibility_changed: Emitted when column visibility changes
    """
    
    # Signals
    navigation_requested = Signal(str)
    path_changed = Signal(str)
    column_visibility_changed = Signal(list)  # List of visible column IDs
    
    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        """
        Initialize the header navigation widget.
        
        Args:
            orientation: Header orientation (Horizontal or Vertical)
            parent: Parent widget
        """
        super().__init__(orientation, parent)
        
        # Services (will be injected)
        self._navigation_service: Optional[NavigationService] = None
        self._history_service: Optional[NavigationHistoryService] = None
        self._location_manager: Optional[LocationManager] = None
        self._completion_service: Optional[PathCompletionService] = None
        self._column_manager: Optional[ColumnManagerService] = None
        
        # Setup navigation context menu
        self._setup_navigation_context_menu()
        
    def _setup_navigation_context_menu(self) -> None:
        """Setup the navigation context menu for the header."""
        # Enable custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_navigation_context_menu)
        
    def inject_services(
        self,
        navigation_service: NavigationService,
        history_service: NavigationHistoryService,
        location_manager: LocationManager,
        completion_service: PathCompletionService,
        column_manager: Optional[ColumnManagerService] = None
    ) -> None:
        """
        Inject navigation services into the header.
        
        Args:
            navigation_service: Core navigation service
            history_service: Navigation history service
            location_manager: Location and bookmark manager
            completion_service: Path completion service
            column_manager: Column management service
        """
        self._navigation_service = navigation_service
        self._history_service = history_service
        self._location_manager = location_manager
        self._completion_service = completion_service
        self._column_manager = column_manager
        
        # Connect to section resize signal if column manager is available
        if self._column_manager:
            self._connect_section_resize_signal()
        
        # Connect to navigation service signals
        if self._navigation_service:
            self._navigation_service.current_path_changed.connect(self._on_path_changed)
            
    def _on_path_changed(self, new_path: str) -> None:
        """
        Handle path change from navigation service.
        
        Args:
            new_path: The new current path
        """
        self.path_changed.emit(new_path)
        
    def _show_navigation_context_menu(self, position: QPoint) -> None:
        """
        Show the navigation context menu.
        
        Args:
            position: Position where the context menu was requested
        """
        if not self._navigation_service:
            logger.info("Navigation service not available - cannot show context menu")
            return
            
        logger.info(f"Creating navigation context menu at position: {position}")
        menu = QMenu(self)
        self._populate_navigation_menu(menu)
        
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
        
    def _populate_navigation_menu(self, menu: QMenu) -> None:
        """
        Populate the navigation context menu with actions.
        
        Args:
            menu: The menu to populate
        """
        logger.info("Populating navigation menu")
        
        # Column Management Section (Phase 4 implementation)
        if self._column_manager:
            logger.info("Adding column management section")
            self._add_column_management_section(menu)
            menu.addSeparator()
            
        # Current path section
        current_path = self._get_current_path()
        logger.info(f"Current path: {current_path}")
        if current_path:
            path_action = QAction(f"📁 {current_path}", self)
            path_action.setEnabled(False)  # Just for display
            menu.addAction(path_action)
            menu.addSeparator()
        
        # Navigation actions (Back, Forward, Up only - Home will be in Quick Locations)
        logger.info("Adding navigation actions")
        self._add_navigation_actions(menu)
        menu.addSeparator()
        
        # Quick locations (includes Home and other standard locations)
        logger.info("Adding quick locations")
        self._add_quick_locations(menu)
        
        # Recent locations
        if self._history_service:
            recent_locations = self._history_service.get_recent_locations(limit=5)
            logger.info(f"Found {len(recent_locations)} recent locations")
            if recent_locations:
                menu.addSeparator()
                self._add_recent_locations(menu, recent_locations)
        
        # Bookmarks
        if self._location_manager:
            bookmarks = self._location_manager.get_bookmarks()
            logger.info(f"Found {len(bookmarks)} bookmarks")
            if bookmarks:
                menu.addSeparator()
                self._add_bookmarks(menu, bookmarks)
                
        # Phase 3: Enhanced Navigation Actions
        menu.addSeparator()
        
        # Navigation Actions Section
        actions_section = menu.addMenu("🎯 Navigation Actions")
        
        # Go to Path action
        goto_action = QAction("📍 Go to Path... (Ctrl+G)", menu)
        goto_action.setToolTip("Navigate to a specific path")
        goto_action.triggered.connect(lambda: self._show_goto_path_dialog())
        actions_section.addAction(goto_action)
        
        # Manage Bookmarks action  
        bookmarks_action = QAction("⭐ Manage Bookmarks...", menu)
        bookmarks_action.setToolTip("Add, edit, or delete bookmarks")
        bookmarks_action.triggered.connect(lambda: self._show_bookmark_manager())
        actions_section.addAction(bookmarks_action)
        
        # Refresh action
        refresh_action = QAction("🔄 Refresh", menu)
        refresh_action.setToolTip("Refresh current location")
        refresh_action.triggered.connect(lambda: self._refresh_current_location())
        actions_section.addAction(refresh_action)
        
        # Phase 4: Column Management Section (Real implementation now)
        if self._column_manager:
            # We now have a real implementation of column management
            self._add_column_management_section(menu)
        else:
            # Fallback to preview if column manager not available
            column_section = menu.addMenu("📋 Column Management")
            
            # Placeholder message
            placeholder_action = QAction("Column Management (Requires Phase 4)", menu)
            placeholder_action.setEnabled(False)
            column_section.addAction(placeholder_action)
                
        logger.info(f"Menu populated with {menu.actions().__len__()} actions")
                
    def _add_navigation_actions(self, menu: QMenu) -> None:
        """
        Add basic navigation actions to the menu.
        
        Args:
            menu: The menu to add actions to
        """
        if not self._navigation_service:
            logger.info("Navigation service not available for navigation actions")
            return
            
        # Back action
        back_action = QAction("← Back", self)
        back_action.setEnabled(self._navigation_service.can_navigate_back())
        back_action.triggered.connect(lambda: self._navigation_service.navigate_back() if self._navigation_service else None)
        menu.addAction(back_action)
        
        # Forward action
        forward_action = QAction("→ Forward", self)
        forward_action.setEnabled(self._navigation_service.can_navigate_forward())
        forward_action.triggered.connect(lambda: self._navigation_service.navigate_forward() if self._navigation_service else None)
        menu.addAction(forward_action)
        
        # Up action
        up_action = QAction("↑ Up", self)
        up_action.setEnabled(True)  # Always available
        up_action.triggered.connect(lambda: self._navigation_service.navigate_up() if self._navigation_service else None)
        menu.addAction(up_action)
        
        logger.info("Added 3 navigation actions to menu")
        
    def _add_quick_locations(self, menu: QMenu) -> None:
        """
        Add quick locations to the menu.
        
        Args:
            menu: The menu to add actions to
        """
        if not self._location_manager:
            return
            
        quick_locations = self._location_manager.get_quick_locations()
        if not quick_locations:
            return
            
        # Add section header
        quick_action = QAction("Quick Locations", self)
        quick_action.setEnabled(False)
        menu.addAction(quick_action)
        
        # Add each quick location
        for location in quick_locations:
            action = QAction(f"{location.icon} {location.name}", self)
            action.triggered.connect(lambda checked, path=location.path: self._navigate_to(path))
            menu.addAction(action)
            
    def _add_recent_locations(self, menu: QMenu, recent_locations: List[dict]) -> None:
        """
        Add recent locations to the menu.
        
        Args:
            menu: The menu to add actions to
            recent_locations: List of recent location dictionaries
        """
        # Add section header
        recent_action = QAction("Recent Locations", self)
        recent_action.setEnabled(False)
        menu.addAction(recent_action)
        
        # Add each recent location
        for location_data in recent_locations:
            path = location_data.get('path', '')
            if path:
                display_name = self._get_display_name(path)
                action = QAction(f"📂 {display_name}", self)
                action.triggered.connect(lambda checked, p=path: self._navigate_to(p))
                menu.addAction(action)
                
    def _add_bookmarks(self, menu: QMenu, bookmarks: List) -> None:
        """
        Add bookmarks to the menu.
        
        Args:
            menu: The menu to add actions to
            bookmarks: List of bookmark objects
        """
        # Add section header
        bookmark_action = QAction("Bookmarks", self)
        bookmark_action.setEnabled(False)
        menu.addAction(bookmark_action)
        
        # Add each bookmark
        for bookmark in bookmarks:
            action = QAction(f"{bookmark.icon} {bookmark.name}", self)
            action.triggered.connect(lambda checked, path=bookmark.path: self._navigate_to(path))
            menu.addAction(action)
            
    def _navigate_to(self, path: str) -> None:
        """
        Navigate to the specified path.
        
        Args:
            path: Path to navigate to
        """
        if self._navigation_service:
            success = self._navigation_service.navigate_to(path)
            if success:
                self.navigation_requested.emit(path)
            
    def _get_current_path(self) -> str:
        """
        Get the current path from the navigation service.
        
        Returns:
            Current path or empty string if no service
        """
        if self._navigation_service:
            return self._navigation_service.current_path or ""
        return ""
        
    def _get_display_name(self, path: str) -> str:
        """
        Get a user-friendly display name for a path.
        
        Args:
            path: File system path
            
        Returns:
            Display name
        """
        if not path:
            return "Unknown"
            
        try:
            from pathlib import Path
            path_obj = Path(path)
            return path_obj.name or str(path_obj)
        except Exception:
            return path
            
    # Phase 3: Enhanced Navigation Methods
    
    def _show_goto_path_dialog(self) -> None:
        """Show the Go to Path dialog."""
        current_path = self._get_current_path()
        
        selected_path = show_goto_path_dialog(
            parent=self,
            current_path=current_path,
            completion_service=self._completion_service,
            history_service=self._history_service
        )
        
        if selected_path:
            self._navigate_to(selected_path)
            
    def _show_bookmark_manager(self) -> None:
        """Show the bookmark manager dialog."""        
        bookmarks_changed = show_bookmark_manager(
            parent=self,
            location_manager=self._location_manager
        )
        
        # Note: The bookmark manager dialog handles navigation internally
        # when bookmarks are selected. If bookmarks were changed, we could
        # refresh our quick locations here in a future enhancement.
        
    def _refresh_current_location(self) -> None:
        """Refresh the current location."""
        current_path = self._get_current_path()
        if current_path and self._navigation_service:
            # Force a refresh by re-navigating to the same path
            self._navigation_service.navigate_to(current_path)
            self.navigation_requested.emit(current_path)
            
    # Phase 3: Column Management Methods (Placeholders for Phase 4)
    
    def _add_column_management_section(self, menu: QMenu) -> None:
        """
        Add column management section to the context menu.
        
        Args:
            menu: The menu to add the section to
        """
        if not self._column_manager:
            return
            
        # Create submenu for column management
        columns_menu = menu.addMenu("📊 Column Management")
        
        # Add column visibility options
        available_columns = self._column_manager.get_available_columns()
        for col_id, col_info in available_columns.items():
            action = QAction(col_info["display"], self)
            action.setCheckable(True)
            action.setChecked(self._column_manager.is_column_visible(col_id))
            
            # Disable toggling for required columns
            if col_info.get("required", False):
                action.setToolTip("This column cannot be hidden")
            
            # Connect action
            action.triggered.connect(
                lambda checked, c_id=col_id: self._toggle_column_visibility(c_id, checked)
            )
            
            columns_menu.addAction(action)
            
        # Add separator
        columns_menu.addSeparator()
        
        # Add fit content option
        fit_action = QAction("Fit Content to Values", self)
        fit_action.setCheckable(True)
        fit_action.setChecked(self._column_manager.get_fit_content_enabled())
        fit_action.triggered.connect(self._toggle_fit_content)
        fit_action.setToolTip("Automatically resize columns to fit their content")
        columns_menu.addAction(fit_action)
        
        # Add reset widths option
        reset_action = QAction("Reset Column Widths", self)
        reset_action.setToolTip("Reset all columns to their default widths")
        reset_action.triggered.connect(self._reset_column_widths)
        columns_menu.addAction(reset_action)
        
        logger.debug("Column management section added to context menu")

    def _toggle_column_visibility(self, column_id: str, visible: bool) -> None:
        """
        Toggle column visibility.
        
        Args:
            column_id: Column identifier
            visible: New visibility state
        """
        if not self._column_manager:
            return
            
        # Try to update visibility (this may fail for required columns)
        changed = self._column_manager.set_column_visibility(column_id, visible)
        
        if changed:
            # Update column visibility in the view
            self._update_column_visibility()
            logger.debug(f"Column '{column_id}' visibility changed to: {visible}")
            
            # Emit signal with updated visible columns
            self.column_visibility_changed.emit(self._column_manager.get_visible_columns())
            
    def _update_column_visibility(self) -> None:
        """Update column visibility in the view based on settings."""
        if not self._column_manager:
            return
            
        # Get the tree view (parent of the header)
        tree_view = self.parent()
        if not isinstance(tree_view, QTreeView):
            logger.warning("Header parent is not a QTreeView, cannot update column visibility")
            return
            
        # Get visible column IDs
        visible_columns = self._column_manager.get_visible_columns()
        
        # Update column visibility in the header
        for col_id, col_info in self._column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns
            
            if visible:
                tree_view.showColumn(model_column)
            else:
                tree_view.hideColumn(model_column)
                
        logger.debug(f"Updated column visibility: {visible_columns}")
        
    def _toggle_fit_content(self, enabled: bool) -> None:
        """
        Toggle fit content setting.
        
        Args:
            enabled: Whether content fitting should be enabled
        """
        if not self._column_manager:
            return
            
        self._column_manager.set_fit_content_enabled(enabled)
        
        if enabled:
            # Resize columns to fit content
            self._resize_columns_to_fit_content()
        else:
            # Restore saved column widths
            self._restore_saved_column_widths()
            
        logger.debug(f"Fit content setting changed to: {enabled}")
        
    def _resize_columns_to_fit_content(self) -> None:
        """Resize all columns to fit their content."""
        # Get the tree view (parent of the header)
        tree_view = self.parent()
        if not isinstance(tree_view, QTreeView):
            logger.warning("Header parent is not a QTreeView, cannot resize columns")
            return
            
        # Resize each column individually
        for section in range(self.count()):
            tree_view.resizeColumnToContents(section)
            
        logger.debug("Resized columns to fit content")
            
    def _restore_saved_column_widths(self) -> None:
        """Restore saved column widths."""
        if not self._column_manager:
            return
            
        # Get the tree view (parent of the header)
        tree_view = self.parent()
        if not isinstance(tree_view, QTreeView):
            logger.warning("Header parent is not a QTreeView, cannot restore column widths")
            return
            
        # Apply saved widths for each column
        for col_id, col_info in self._column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            width = self._column_manager.get_column_width(col_id)
            tree_view.setColumnWidth(model_column, width)
            
        logger.debug("Restored saved column widths")
        
    def _reset_column_widths(self) -> None:
        """Reset all column widths to defaults."""
        if not self._column_manager:
            return
            
        # Reset widths in the manager
        self._column_manager.reset_column_widths()
        
        # Get the tree view (parent of the header)
        tree_view = self.parent()
        if not isinstance(tree_view, QTreeView):
            logger.warning("Header parent is not a QTreeView, cannot reset column widths")
            return
            
        # Apply default widths
        for col_id, col_info in self._column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            default_width = col_info.get("default_width", 100)
            tree_view.setColumnWidth(model_column, default_width)
                
        logger.debug("Reset column widths to defaults")
        
    def _connect_section_resize_signal(self) -> None:
        """Connect to sectionResized signal to track column width changes."""
        self.sectionResized.connect(self._handle_section_resize)
        logger.debug("Connected to section resize signal")
        
    def _handle_section_resize(self, logical_index: int, old_size: int, new_size: int) -> None:
        """
        Handle column resizing to save custom widths.
        
        Args:
            logical_index: Index of the resized section
            old_size: Old section size
            new_size: New section size
        """
        if not self._column_manager:
            return
            
        # Find column ID for the logical index
        col_id = self._column_manager.get_column_id_by_model_index(logical_index)
        if col_id:
            # Save the new width
            self._column_manager.set_column_width(col_id, new_size)
            logger.debug(f"Saved custom width for column '{col_id}': {new_size}px")
            
    def inject_column_manager(self, column_manager: ColumnManagerService) -> None:
        """
        Inject column manager service.
        
        Args:
            column_manager: Column management service
        """
        self._column_manager = column_manager
        
        # Connect section resize signal
        self._connect_section_resize_signal()
        
        logger.debug("Column manager injected into header navigation widget")
