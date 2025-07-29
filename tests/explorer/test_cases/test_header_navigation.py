"""
Test HeaderNavigationWidget functionality.

This test demonstrates the enhanced table header with navigation context menu.
"""

import sys
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableView
from PySide6.QtCore import Qt

# Add project root to path
# tests/explorer/test_cases/test_header_navigation.py -> project root is 3 levels up
sys.path.insert(0, str(Path(__file__).parents[3]))

from widgets.explorer.explorer_header_bar import HeaderNavigationWidget
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService


class TestWindow(QMainWindow):
    """Test window for HeaderNavigationWidget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Header Navigation Widget Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create a simple table view to test the header
        self.table_view = QTableView()
        
        # Replace the default header with our navigation header
        self.nav_header = HeaderNavigationWidget(Qt.Orientation.Horizontal)
        self.table_view.setHorizontalHeader(self.nav_header)
        
        layout.addWidget(self.table_view)
        
        # Initialize services
        self._setup_services()
        
        # Inject services into the header
        self.nav_header.inject_services(
            self.navigation_service,
            self.history_service,
            self.location_manager,
            self.completion_service
        )
        
        # Connect signals
        self.nav_header.navigation_requested.connect(self._on_navigation_requested)
        self.nav_header.path_changed.connect(self._on_path_changed)
        
        print("HeaderNavigationWidget Test Ready!")
        print("Right-click on the table header to see the navigation context menu.")
        
    def _setup_services(self):
        """Setup navigation services."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize services
        self.navigation_service = NavigationService()
        self.history_service = NavigationHistoryService()
        self.location_manager = LocationManager()
        self.completion_service = PathCompletionService()
        
        # Inject dependencies
        self.navigation_service.set_dependencies(
            history_service=self.history_service,
            location_manager=self.location_manager
        )
        
        # Set initial path
        home_path = str(Path.home())
        self.navigation_service.navigate_to(home_path)
        
        print(f"Services initialized. Current path: {home_path}")
        
    def _on_navigation_requested(self, path: str):
        """Handle navigation request from header."""
        print(f"Navigation requested to: {path}")
        
    def _on_path_changed(self, new_path: str):
        """Handle path change from navigation service."""
        print(f"Path changed to: {new_path}")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = TestWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
