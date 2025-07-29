"""
Phase 3 Feature Demo

This demo specifically tests the new Phase 3 features:
- Go to Path dialog
- Bookmark Manager dialog
- Enhanced context menu sections
"""

import sys
from pathlib import Path

# Add project root to path
# Add project root to path
# tests/explorer/test_cases/phase3_feature_demo.py -> project root is 3 levels up
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

# Import our Phase 3 features
from widgets.explorer.goto_path_dialog import show_goto_path_dialog
from widgets.explorer.bookmark_manager_dialog import show_bookmark_manager
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService

class Phase3DemoWindow(QMainWindow):
    """Demo window for Phase 3 features."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 3: Enhanced Context Menu Features Demo")
        self.setGeometry(100, 100, 500, 400)
        
        # Initialize services
        self._setup_services()
        
        # Setup UI
        self._setup_ui()
        
    def _setup_services(self):
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
        
        # Add some sample data
        current_path = str(Path.cwd())
        self.navigation_service.navigate_to(current_path)
        
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🚀 Phase 3: Enhanced Context Menu Features")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Test the new Phase 3 features that are now available in the context menu:\n\n"
            "• Go to Path dialog with auto-completion\n"
            "• Bookmark Manager for organizing locations\n"
            "• Enhanced context menu sections\n"
            "• Column Management preview (Phase 4)"
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Test buttons
        buttons_layout = QVBoxLayout()
        
        # Go to Path button
        goto_button = QPushButton("📍 Test Go to Path Dialog")
        goto_button.clicked.connect(self._test_goto_path)
        buttons_layout.addWidget(goto_button)
        
        # Bookmark Manager button
        bookmark_button = QPushButton("⭐ Test Bookmark Manager")
        bookmark_button.clicked.connect(self._test_bookmark_manager)
        buttons_layout.addWidget(bookmark_button)
        
        # Full context menu test button
        context_button = QPushButton("🖱️ Test Full Context Menu")
        context_button.clicked.connect(self._show_context_menu_info)
        buttons_layout.addWidget(context_button)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Status
        self.status_label = QLabel("Ready to test Phase 3 features!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)
        
    def _test_goto_path(self):
        """Test the Go to Path dialog."""
        self.status_label.setText("Opening Go to Path dialog...")
        
        selected_path = show_goto_path_dialog(
            parent=self,
            current_path=str(Path.cwd()),
            completion_service=self.completion_service,
            history_service=self.history_service
        )
        
        if selected_path:
            self.status_label.setText(f"Selected path: {selected_path}")
            self.navigation_service.navigate_to(selected_path)
        else:
            self.status_label.setText("Go to Path dialog cancelled")
            
    def _test_bookmark_manager(self):
        """Test the Bookmark Manager dialog."""
        self.status_label.setText("Opening Bookmark Manager...")
        
        bookmarks_changed = show_bookmark_manager(
            parent=self,
            location_manager=self.location_manager
        )
        
        if bookmarks_changed:
            self.status_label.setText("Bookmarks were modified!")
        else:
            self.status_label.setText("Bookmark Manager closed")
            
    def _show_context_menu_info(self):
        """Show information about the context menu."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.information(
            self, "Full Context Menu Test",
            "To test the full enhanced context menu:\n\n"
            "1. Run header_navigation_demo.py\n"
            "2. Right-click on any table header column\n"
            "3. You'll see the enhanced menu with:\n"
            "   • Navigation Actions submenu\n"
            "   • Column Management submenu\n"
            "   • All Phase 3 features integrated\n\n"
            "The context menu now includes 22+ actions!"
        )
        
        self.status_label.setText("See the message box for context menu test instructions")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Phase 3 Feature Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show window
    window = Phase3DemoWindow()
    window.show()
    
    print("🚀 Phase 3 Feature Demo Started!")
    print("📍 Test individual Phase 3 features using the buttons")
    print("🖱️ For full context menu test, use header_navigation_demo.py")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
