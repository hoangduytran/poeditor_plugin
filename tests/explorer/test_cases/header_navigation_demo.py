#!/usr/bin/env python3
"""
HeaderNavigationWidget Integration Demo

This script demonstrates how to integrate the HeaderNavigationWidget into
the existing explorer panel structure using the enhanced explorer widgets.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

# Add project root to path
# tests/explorer/test_cases/header_navigation_demo.py -> project root is 3 levels up
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from lg import logger
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from widgets.explorer.explorer_header_bar import HeaderNavigationWidget


class ExplorerDemoWindow(QMainWindow):
    """Demo window showing HeaderNavigationWidget integration."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Explorer Header Navigation Demo")
        self.setGeometry(100, 100, 800, 600)

        # Create services
        self._create_services()

        # Setup UI
        self._setup_ui()

        # Connect services
        self._connect_services()

        logger.info("Explorer demo window initialized")

    def _create_services(self):
        """Create navigation services."""
        self.navigation_service = NavigationService()
        self.history_service = NavigationHistoryService()
        self.location_manager = LocationManager()
        self.completion_service = PathCompletionService()

        # Set up service dependencies
        self.navigation_service.set_dependencies(
            history_service=self.history_service,
            location_manager=self.location_manager
        )

        logger.info("Navigation services created")

    def _setup_ui(self):
        """Setup the demo UI."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(4, 4, 4, 4)

        # Create enhanced explorer widget
        self.explorer_widget = EnhancedExplorerWidget()
        layout.addWidget(self.explorer_widget)

        # Replace the tree view header with our navigation header
        tree_view = self.explorer_widget.file_view

        # Create our navigation header
        self.nav_header = HeaderNavigationWidget(Qt.Orientation.Horizontal)

        # Inject services into the navigation header
        self.nav_header.inject_services(
            navigation_service=self.navigation_service,
            history_service=self.history_service,
            location_manager=self.location_manager,
            completion_service=self.completion_service
        )

        # Replace the tree view's header with our navigation header
        tree_view.setHeader(self.nav_header)

        # Debug: Add some logging for context menu events
        self.nav_header.customContextMenuRequested.connect(
            lambda pos: logger.info(f"Context menu requested at position: {pos}")
        )

        logger.info("UI setup complete")

    def _connect_services(self):
        """Connect service signals."""
        # Connect navigation service to file view
        self.navigation_service.current_path_changed.connect(self._on_path_changed)
        self.navigation_service.navigation_completed.connect(self._on_navigation_completed)

        # Connect header navigation signals
        self.nav_header.navigation_requested.connect(self._on_navigation_requested)

        # Connect explorer file view signals
        if hasattr(self.explorer_widget.file_view, 'directory_changed'):
            self.explorer_widget.file_view.directory_changed.connect(
                self._on_directory_changed
            )

        logger.info("Services connected")

        # Initialize with current directory
        current_dir = str(Path.cwd())
        self.navigation_service.navigate_to(current_dir)

    def _on_path_changed(self, new_path: str):
        """Handle path change from navigation service."""
        logger.info(f"Path changed to: {new_path}")

        # Update path label if it exists
        if hasattr(self.explorer_widget, 'path_label'):
            self.explorer_widget.path_label.setText(new_path)

    def _on_navigation_completed(self, path: str):
        """Handle navigation completion."""
        logger.info(f"Navigation completed to: {path}")

    def _on_navigation_requested(self, path: str):
        """Handle navigation request from header."""
        logger.info(f"Navigation requested to: {path}")

    def _on_directory_changed(self, path: str):
        """Handle directory change from file view."""
        logger.info(f"Directory changed to: {path}")
        # Update navigation service
        self.navigation_service.navigate_to(path)


def main():
    """Run the explorer header navigation demo."""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Explorer Header Navigation Demo")
        app.setApplicationVersion("1.0.0")

        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        logger.info("Starting Explorer Header Navigation Demo")

        # Create and show demo window
        window = ExplorerDemoWindow()
        window.show()

        logger.info("Demo started successfully")
        logger.info("🖱️  Right-click on the table header to see navigation menu!")
        print("🖱️  Right-click on the table header to see navigation menu!")

        # Run the application
        exit_code = app.exec()

        logger.info(f"Demo exiting with code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Failed to start demo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
