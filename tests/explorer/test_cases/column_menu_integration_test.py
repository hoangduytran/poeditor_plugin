#!/usr/bin/env python3
"""
Column Header Context Menu Integration Test

This script demonstrates how the column header context menu has been integrated
with the existing explorer implementation.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

# Add project root to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from lg import logger
from widgets.simple_explorer_widget_with_column_menu import SimpleExplorerWidgetWithColumnMenu


class ColumnMenuIntegrationTest(QMainWindow):
    """Test window for column header context menu integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Column Header Context Menu Integration Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the enhanced explorer widget
        self.explorer = SimpleExplorerWidgetWithColumnMenu()
        self.setCentralWidget(self.explorer)
        
        logger.info("Test window initialized")
        logger.info("Right-click on the column header to show the context menu")
        
        # Instruct the user
        print("-------------------------------------------------------------")
        print("Column Header Context Menu Integration Test")
        print("-------------------------------------------------------------")
        print("1. Right-click on the column header to show the context menu")
        print("2. Toggle columns using the checkboxes")
        print("3. Try the 'Fit Content to Values' option")
        print("4. Reset column widths using the 'Reset Column Widths' option")
        print("-------------------------------------------------------------")


def main():
    app = QApplication(sys.argv)
    window = ColumnMenuIntegrationTest()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
