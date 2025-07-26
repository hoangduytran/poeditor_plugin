#!/usr/bin/env python3
"""
Test Qt6 dark mode functionality.

Based on: https://stackoverflow.com/questions/73060080/how-do-i-use-qt6-dark-theme-with-pyside6

This test checks if Qt6's built-in dark mode works on macOS.
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
)

# Try different platform arguments for macOS
# Note: The original example uses 'windows:darkmode=2' which is Windows-specific
# For macOS, we'll try different approaches
print("Testing Qt6 dark mode on macOS...")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Qt6 Dark Mode Test - POEditor")
        self.setMinimumSize(400, 600)

        layout = QVBoxLayout()
        
        # Add a title label
        title = QLabel("Qt6 Dark Mode Test")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test widgets from the example
        widgets = [
            QCheckBox,
            QComboBox,
            QDateEdit,
            QDateTimeEdit,
            QDial,
            QDoubleSpinBox,
            QFontComboBox,
            QLCDNumber,
            QLabel,
            QLineEdit,
            QProgressBar,
            QPushButton,
            QRadioButton,
            QSlider,
            QSpinBox,
            QTimeEdit,
        ]

        for w in widgets:
            widget = w()
            if isinstance(widget, QLabel):
                widget.setText(f"Test {w.__name__}")
            elif isinstance(widget, QComboBox):
                widget.addItems(["Option 1", "Option 2", "Option 3"])
            elif isinstance(widget, QPushButton):
                widget.setText("Test Button")
            elif isinstance(widget, QCheckBox):
                widget.setText("Test Checkbox")
            elif isinstance(widget, QRadioButton):
                widget.setText("Test Radio Button")
            layout.addWidget(widget)
        
        # Add a list widget to test selection colors (our main concern)
        list_widget = QListWidget()
        list_widget.addItem(QListWidgetItem("List Item 1"))
        list_widget.addItem(QListWidgetItem("List Item 2"))
        list_widget.addItem(QListWidgetItem("List Item 3"))
        list_widget.addItem(QListWidgetItem("List Item 4 (select me to test highlight color)"))
        layout.addWidget(list_widget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

def test_qt_dark_mode():
    """Test different approaches to enable Qt dark mode."""
    
    # Approach 1: Try macOS-specific platform arguments
    print("Approach 1: Testing with macOS platform arguments...")
    try:
        # macOS doesn't use 'windows:darkmode=2', but we can try other approaches
        # sys.argv += ['-platform', 'cocoa']  # Standard macOS platform
        
        app = QApplication(sys.argv)
        
        # Approach 2: Set Fusion style (cross-platform dark-friendly style)
        print("Setting Fusion style...")
        app.setStyle('Fusion')
        
        # Approach 3: Try to use system dark mode detection
        print("Checking system dark mode...")
        palette = app.palette()
        window_color = palette.color(palette.ColorRole.Window)
        print(f"System window color: {window_color.name()}")
        print(f"System highlight color: {palette.color(palette.ColorRole.Highlight).name()}")
        
        # Create and show window
        window = MainWindow()
        window.show()
        
        print("Window created. Check if it appears with dark styling.")
        print("Pay attention to the list widget selection color.")
        print("Close the window to continue...")
        
        return app.exec()
        
    except Exception as e:
        print(f"Error in Qt dark mode test: {e}")
        return 1

if __name__ == "__main__":
    exit_code = test_qt_dark_mode()
    print(f"Test completed with exit code: {exit_code}")
    sys.exit(exit_code)
