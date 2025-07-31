#!/usr/bin/env python3
"""
Column Header Context Menu Integration Test

This test demonstrates the integration of column header context menu
with column management functionality for the Explorer panel.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

# Add project root to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from widgets.explorer.explorer_header_bar import HeaderNavigationWidget
from services.column_manager_service import ColumnManagerService


class ColumnHeaderTestWindow(QMainWindow):
    """Test window for column header context menu functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Column Header Context Menu Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create explorer widget
        self.explorer = EnhancedExplorerWidget()
        self.setCentralWidget(self.explorer)
        
        logger.info("Test window initialized")
        
        # Run tests after the window is shown
        QTimer.singleShot(1000, self.run_test_sequence)
        
    def run_test_sequence(self):
        """Run test sequence for column header context menu."""
        logger.info("Starting test sequence for column header context menu")
        
        # Get the column manager service
        column_manager = self.explorer.column_manager_service
        
        # Check initial column settings
        visible_columns = column_manager.get_visible_columns()
        logger.info(f"Initial visible columns: {visible_columns}")
        logger.info(f"Fit content enabled: {column_manager.get_fit_content_enabled()}")
        
        # Test 1: Hide Size column
        logger.info("Test 1: Hide Size column")
        column_manager.set_column_visibility("size", False)
        logger.info(f"Visible columns after hiding Size: {column_manager.get_visible_columns()}")
        
        # Test 2: Enable fit content
        logger.info("Test 2: Enable fit content")
        column_manager.set_fit_content_enabled(True)
        logger.info(f"Fit content enabled: {column_manager.get_fit_content_enabled()}")
        
        # Test 3: Reset column widths
        logger.info("Test 3: Reset column widths")
        column_manager.reset_column_widths()
        logger.info("Column widths have been reset")
        
        # Test 4: Show all columns again
        logger.info("Test 4: Show all columns")
        for col_id in ["name", "size", "type", "modified"]:
            column_manager.set_column_visibility(col_id, True)
        logger.info(f"All columns visible: {column_manager.get_visible_columns()}")
        
        logger.info("Test sequence completed")
        logger.info("Right-click on the column header to show the context menu")


def main():
    app = QApplication(sys.argv)
    window = ColumnHeaderTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
