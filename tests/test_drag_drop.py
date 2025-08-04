#!/usr/bin/env python
"""
Test script for Enhanced Explorer Drag and Drop functionality.

This script runs a standalone window with the Enhanced Explorer Widget
to test the drag and drop implementation.
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget


class TestWindow(QMainWindow):
    """Test window for drag and drop functionality."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag & Drop Test")
        self.setMinimumSize(800, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QLabel("Enhanced Explorer Drag & Drop Test")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "• Drag files within the explorer to move them\n"
            "• Hold Ctrl while dragging to copy instead of move\n"
            "• Drag files from external applications here\n"
            "• Drag files from here to external applications"
        )
        instructions.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Explorer widget
        self.explorer = EnhancedExplorerWidget()
        layout.addWidget(self.explorer)

        # Status label
        self.status = QLabel("Ready")
        layout.addWidget(self.status)

        # Connect signals
        if hasattr(self.explorer.file_view, 'drag_drop_service') and self.explorer.file_view.drag_drop_service:
            self.explorer.file_view.drag_drop_service.drag_started.connect(
                lambda paths: self.update_status(f"Dragging {len(paths)} items")
            )
            self.explorer.file_view.drag_drop_service.drop_received.connect(
                lambda paths, target: self.update_status(
                    f"Dropped {len(paths)} items into {os.path.basename(target)}"
                )
            )
        else:
            logger.warning("Drag & drop service not available")

    def update_status(self, message):
        """Update status bar with message."""
        self.status.setText(message)
        logger.info(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
