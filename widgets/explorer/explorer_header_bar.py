"""
Header Navigation Widget

Enhances the existing table header (QHeaderView) with navigation functionality.
Provides a context menu with navigation features when right-clicking the header.
"""

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
    
    Signals:
        navigation_requested: Emitted when navigation to a path is requested
        path_changed: Emitted when current path changes
    """
    
    # Signals
    navigation_requested = Signal(str)
    path_changed = Signal(str)
    
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
        completion_service: PathCompletionService
    ) -> None:
        """
        Inject navigation services into the header.
        
        Args:
            navigation_service: Core navigation service
            history_service: Navigation history service
            location_manager: Location and bookmark manager
            completion_service: Path completion service
        """
        self._navigation_service = navigation_service
        self._history_service = history_service
        self._location_manager = location_manager
        self._completion_service = completion_service
        
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
