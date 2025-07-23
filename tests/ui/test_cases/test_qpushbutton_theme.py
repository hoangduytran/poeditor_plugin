#!/usr/bin/env python3
"""
QPushButton Theme Test
Test QSS styling for QPushButton across different themes
"""

import sys
import os
import importlib
from pathlib import Path
import logging

# Configure proper import paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# First import lg to set up logging
from lg import logger

# Import PySide6 components
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QGridLayout, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt, QSize

# Now import our services
try:
    # Try direct import first
    from services.theme_manager import ThemeManager, Theme, theme_manager
except ImportError as e:
    logger.warning(f"Direct import failed: {e}")
    try:
        # Try importing using full path as fallback
        sys.path.append(str(project_root))
        theme_manager_module = importlib.import_module('services.theme_manager')
        ThemeManager = theme_manager_module.ThemeManager
        Theme = theme_manager_module.Theme
        theme_manager = theme_manager_module.theme_manager
        logger.info("Successfully imported services.theme_manager using full path")
    except Exception as e2:
        logger.error(f"Failed to import services.theme_manager: {e2}")
        raise

class QPushButtonThemeTest(QMainWindow):
    """Test QPushButton theming across different styles and states."""
    
    def __init__(self):
        super().__init__()
        self.theme_manager = theme_manager  # Use global theme_manager instance
        self.initUI()
        
    def initUI(self):
        """Set up the UI components."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        
        # Get available themes from theme manager
        themes = self.theme_manager.get_available_themes()
        self.theme_combo.addItems(themes)
        
        # Set current theme
        current_theme = self.theme_manager.get_current_theme()
        if current_theme:
            index = self.theme_combo.findText(current_theme.name)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
        
        # Connect theme selection change event
        self.theme_combo.currentTextChanged.connect(self.changeTheme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch(1)
        main_layout.addLayout(theme_layout)
        
        # Section title
        title_label = QLabel("QPushButton Theme Test")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        main_layout.addWidget(title_label)
        
        # Create grid for buttons
        grid = QGridLayout()
        
        # Regular buttons
        self.addButtonSection(grid, 0, "Standard Buttons")
        
        standard_btn = QPushButton("Standard Button")
        primary_btn = QPushButton("Primary Button")
        primary_btn.setProperty("class", "primary")
        
        danger_btn = QPushButton("Danger Button")
        danger_btn.setProperty("class", "danger")
        
        success_btn = QPushButton("Success Button")
        success_btn.setProperty("class", "success")
        
        warning_btn = QPushButton("Warning Button")
        warning_btn.setProperty("class", "warning")
        
        grid.addWidget(standard_btn, 1, 0)
        grid.addWidget(primary_btn, 1, 1)
        grid.addWidget(danger_btn, 1, 2)
        grid.addWidget(success_btn, 1, 3)
        grid.addWidget(warning_btn, 1, 4)
        
        # Disabled buttons
        self.addButtonSection(grid, 2, "Disabled Buttons")
        
        disabled_std_btn = QPushButton("Disabled Standard")
        disabled_std_btn.setEnabled(False)
        
        disabled_primary_btn = QPushButton("Disabled Primary")
        disabled_primary_btn.setProperty("class", "primary")
        disabled_primary_btn.setEnabled(False)
        
        disabled_danger_btn = QPushButton("Disabled Danger")
        disabled_danger_btn.setProperty("class", "danger")
        disabled_danger_btn.setEnabled(False)
        
        grid.addWidget(disabled_std_btn, 3, 0)
        grid.addWidget(disabled_primary_btn, 3, 1)
        grid.addWidget(disabled_danger_btn, 3, 2)
        
        # Different sizes
        self.addButtonSection(grid, 4, "Button Sizes")
        
        small_btn = QPushButton("Small Button")
        small_btn.setProperty("size", "small")
        
        large_btn = QPushButton("Large Button")
        large_btn.setProperty("size", "large")
        
        grid.addWidget(small_btn, 5, 0)
        grid.addWidget(QPushButton("Normal Button"), 5, 1)
        grid.addWidget(large_btn, 5, 2)
        
        # Icon buttons
        self.addButtonSection(grid, 6, "Icon Buttons")
        
        # Custom property buttons
        self.addButtonSection(grid, 8, "Custom Buttons")
        
        flat_btn = QPushButton("Flat Button")
        flat_btn.setFlat(True)
        
        custom_btn = QPushButton("Custom Style Button")
        custom_btn.setProperty("custom", "special")
        
        breadcrumb_btn = QPushButton("Breadcrumb Button")
        breadcrumb_btn.setProperty("class", "breadcrumb-button")
        
        rounded_btn = QPushButton("Rounded Button")
        rounded_btn.setProperty("rounded", True)
        
        grid.addWidget(flat_btn, 9, 0)
        grid.addWidget(custom_btn, 9, 1)
        grid.addWidget(breadcrumb_btn, 9, 2)
        grid.addWidget(rounded_btn, 9, 3)
        
        # Add grid to main layout
        main_layout.addLayout(grid)
        
        # Add click handler for all buttons
        for i in range(grid.count()):
            item = grid.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QPushButton):
                # We know it's a QPushButton because of the isinstance check
                button = item.widget()
                # Use a function to handle type casting for the linter
                self.connect_button_clicked(button)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Set window properties
        self.setWindowTitle("QPushButton Theme Test")
        self.resize(800, 600)
    
    def addButtonSection(self, grid, row, title):
        """Add a section title to the grid."""
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        grid.addWidget(label, row, 0, 1, 5)
    
    def changeTheme(self, theme_name):
        """Change the application theme."""
        logger.info(f"Changing theme to: {theme_name}")
        self.theme_manager.set_theme(theme_name)
    
    def connect_button_clicked(self, btn):
        """Connect a button's clicked signal to the onButtonClicked handler."""
        if isinstance(btn, QPushButton):
            btn.clicked.connect(lambda checked, button=btn: self.onButtonClicked(button))
            
    def onButtonClicked(self, btn):
        """Handle button clicks."""
        logger.info(f"Button clicked: {btn.text()}, Properties: {[btn.property(prop) for prop in ['class', 'size', 'custom', 'rounded']]}")


def run_test():
    """Run the QPushButton theme test application."""
    app = QApplication.instance() or QApplication([])

    # Import resources to register Qt resource system
    import resources_rc

    test_window = QPushButtonThemeTest()
    test_window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_test())
