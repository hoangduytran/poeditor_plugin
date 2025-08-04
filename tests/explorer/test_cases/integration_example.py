"""
HeaderNavigationWidget Integration Guide

This document shows how to integrate the HeaderNavigationWidget with the existing
SimpleExplorerWidget to add navigation functionality to the table header.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Qt

from widgets.simple_explorer_widget import SimpleExplorerWidget
from widgets.explorer.explorer_header_bar import HeaderNavigationWidget
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService


class EnhancedExplorerWidget(QWidget):
    """
    Enhanced explorer widget that integrates HeaderNavigationWidget
    with the existing SimpleExplorerWidget.

    This widget replaces the standard table header with our navigation-enabled header.
    """

    # Signals
    file_opened = Signal(str)
    location_changed = Signal(str)
    navigation_requested = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the enhanced explorer widget."""
        super().__init__(parent)

        # Initialize services
        self._setup_services()

        # Setup UI
        self._setup_ui()

        # Connect signals
        self._setup_connections()

    def _setup_services(self) -> None:
        """Initialize navigation services."""
        self.navigation_service = NavigationService()
        self.history_service = NavigationHistoryService()
        self.location_manager = LocationManager()
        self.completion_service = PathCompletionService()

        # Set up dependencies
        self.navigation_service.set_dependencies(
            history_service=self.history_service,
            location_manager=self.location_manager
        )

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create the simple explorer widget
        self.explorer_widget = SimpleExplorerWidget()

        # Get the file view and replace its header
        file_view = self.explorer_widget.file_view

        # Create our navigation header
        self.nav_header = HeaderNavigationWidget(Qt.Orientation.Horizontal)

        # Replace the default header with our navigation header
        file_view.setHeader(self.nav_header)

        # Inject services into the navigation header
        self.nav_header.inject_services(
            self.navigation_service,
            self.history_service,
            self.location_manager,
            self.completion_service
        )

        # Add the explorer widget to our layout
        layout.addWidget(self.explorer_widget)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Forward explorer widget signals
        self.explorer_widget.file_opened.connect(self.file_opened.emit)
        self.explorer_widget.location_changed.connect(self._on_location_changed)

        # Connect navigation header signals
        self.nav_header.navigation_requested.connect(self._on_navigation_requested)
        self.nav_header.path_changed.connect(self.location_changed.emit)

        # Connect navigation service to explorer widget
        self.navigation_service.current_path_changed.connect(self._sync_explorer_path)

    def _on_location_changed(self, path: str) -> None:
        """Handle location change from explorer widget."""
        # Update navigation service when explorer path changes
        self.navigation_service.navigate_to(path)
        self.location_changed.emit(path)

    def _on_navigation_requested(self, path: str) -> None:
        """Handle navigation request from header."""
        # Navigate both the service and the explorer widget
        self.set_current_path(path)
        self.navigation_requested.emit(path)

    def _sync_explorer_path(self, path: str) -> None:
        """Sync explorer widget path with navigation service."""
        # Update explorer widget when navigation service changes path
        self.explorer_widget.set_current_path(path)

    def set_current_path(self, path: str) -> None:
        """Set the current path for both services and UI."""
        self.navigation_service.navigate_to(path)
        self.explorer_widget.set_current_path(path)

    def get_current_path(self) -> str:
        """Get the current path."""
        return self.explorer_widget.get_current_path()


# Usage example for the enhanced explorer panel
class EnhancedExplorerPanel:
    """
    Example showing how to update the ExplorerPanel to use
    the EnhancedExplorerWidget with navigation header.
    """

    def _setup_ui_enhanced(self):
        """Enhanced version of ExplorerPanel._setup_ui()"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Use the enhanced explorer widget instead of SimpleExplorerWidget
        self.explorer_widget = EnhancedExplorerWidget()
        layout.addWidget(self.explorer_widget)

        # Connect enhanced signals
        self.explorer_widget.file_opened.connect(self.file_opened.emit)
        self.explorer_widget.location_changed.connect(self.location_changed.emit)
        self.explorer_widget.navigation_requested.connect(self._on_navigation_requested)

    def _on_navigation_requested(self, path: str):
        """Handle navigation requests from the header context menu."""
        print(f"Navigation requested to: {path}")
        # Additional navigation handling can be added here


if __name__ == "__main__":
    """
    Integration Steps for existing ExplorerPanel:

    1. Replace SimpleExplorerWidget with EnhancedExplorerWidget
    2. Connect the navigation_requested signal
    3. The header context menu will automatically provide:
       - Back/Forward navigation
       - Quick locations (Home, Documents, etc.)
       - Recent locations
       - Bookmarks
       - Current path display

    The user can right-click on any column header (Name, Size, Modified, Type)
    to access the navigation context menu.
    """
    print("HeaderNavigationWidget Integration Guide")
    print("See the code above for integration examples.")
    print()
    print("Key Benefits:")
    print("- No additional UI space required")
    print("- Integrates seamlessly with existing table headers")
    print("- Provides full navigation functionality via context menu")
    print("- Maintains existing table functionality (sorting, resizing)")
    print("- Works with any QTableView or QTreeView header")
