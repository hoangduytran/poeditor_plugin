#!/usr/bin/env python3
"""
Test the theme CSS loading and application.
This test verifies if the themes load correctly and checks if common.css is needed.
"""

import sys
import os
from pathlib import Path
from lg import logger

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QDockWidget
from PySide6.QtCore import QFile, QTextStream, QIODevice, Qt
from services.theme_manager import ThemeManager, Theme, theme_manager

class ThemeCSSTest:
    """Test theme CSS loading and application."""

    def __init__(self):
        self.app = QApplication([])
        self.window = QMainWindow()
        self.theme_manager = theme_manager  # Use the global theme manager instance

        # Create simple UI for testing themes
        central_widget = QWidget()
        layout = QVBoxLayout()
        self.test_label = QLabel("Theme Test Label")
        self.test_button = QPushButton("Test Button")

        layout.addWidget(self.test_label)
        layout.addWidget(self.test_button)
        central_widget.setLayout(layout)
        self.window.setCentralWidget(central_widget)

        # Set up theme buttons
        self.light_button = QPushButton("Light Theme")
        self.dark_button = QPushButton("Dark Theme")
        self.colorful_button = QPushButton("Colorful Theme")

        self.light_button.clicked.connect(lambda: self.test_theme("Light"))
        self.dark_button.clicked.connect(lambda: self.test_theme("Dark"))
        self.colorful_button.clicked.connect(lambda: self.test_theme("Colorful"))

        theme_layout = QVBoxLayout()
        theme_layout.addWidget(self.light_button)
        theme_layout.addWidget(self.dark_button)
        theme_layout.addWidget(self.colorful_button)

        theme_widget = QWidget()
        theme_widget.setLayout(theme_layout)

        # Create a dock widget for the theme buttons
        dock = QDockWidget("Theme Controls", self.window)
        dock.setWidget(theme_widget)
        self.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        # Set window properties
        self.window.setWindowTitle("Theme CSS Test")
        self.window.resize(800, 600)

    def test_theme(self, theme_name):
        """Test applying a theme."""
        logger.info(f"Testing theme: {theme_name}")
        self.theme_manager.set_theme(theme_name)

    def test_load_direct_css(self, css_path, include_common=False):
        """Test loading CSS directly from file."""
        logger.info(f"Testing direct CSS loading: {css_path}, include_common={include_common}")
        try:
            file = QFile(css_path)
            if file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                stream = QTextStream(file)
                css_content = stream.readAll()
                file.close()

                if include_common:
                    common_path = os.path.join(os.path.dirname(css_path), "common.css")
                    common_file = QFile(common_path)
                    if common_file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                        common_stream = QTextStream(common_file)
                        css_content = common_stream.readAll() + "\n" + css_content
                        common_file.close()

                self.app.setStyleSheet(css_content)
                logger.info("CSS applied successfully")
                return True
            else:
                logger.error(f"Failed to open CSS file: {css_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading CSS: {e}")
            return False

    def run_tests(self):
        """Run all theme tests."""
        logger.info("Starting theme CSS tests")

        # Test 1: Test theme manager built-in loading
        logger.info("Test 1: Theme manager built-in loading")
        for theme_name in ["Light", "Dark", "Colorful"]:
            self.test_theme(theme_name)
            input(f"Press Enter to continue after reviewing {theme_name} theme...")

        # Test 2: Test direct CSS loading without common.css
        # Check if the themes/css directory exists
        themes_css_dir = os.path.join(project_root, "themes", "css")
        if os.path.exists(themes_css_dir):
            css_files = [
                os.path.join(themes_css_dir, "light_theme.css"),
                os.path.join(themes_css_dir, "dark_theme.css"),
                os.path.join(themes_css_dir, "colorful_theme.css")
            ]
        else:
            # If themes/css directory doesn't exist, check if themes are in resources
            css_files = [
                ":/css/light_theme.css",
                ":/css/dark_theme.css",
                ":/css/colorful_theme.css"
            ]
            # Check if resource files exist
            for css_file in css_files:
                if not QFile(css_file).exists():
                    logger.warning(f"Resource file not found: {css_file}")

        logger.info("Test 2: Direct CSS loading without common.css")
        for css_file in css_files:
            if not QFile(css_file).exists():
                logger.warning(f"Skipping non-existent file: {css_file}")
                continue

            theme_name = os.path.basename(css_file).replace("_theme.css", "").capitalize()
            if ":" in css_file:  # For resource paths
                theme_name = css_file.split("/")[-1].replace("_theme.css", "").capitalize()

            self.test_load_direct_css(css_file, include_common=False)
            input(f"Press Enter to continue after reviewing {theme_name} theme (without common.css)...")

        # Test 3: Test direct CSS loading with common.css
        logger.info("Test 3: Direct CSS loading with common.css")

        # Check if common.css exists
        common_exists = False
        if os.path.exists(themes_css_dir):
            common_css_path = os.path.join(themes_css_dir, "common.css")
            if os.path.exists(common_css_path):
                common_exists = True
        else:
            # Check if common.css exists in resources
            common_css_path = ":/css/common.css"
            if QFile(common_css_path).exists():
                common_exists = True

        if common_exists:
            for css_file in css_files:
                if not QFile(css_file).exists():
                    logger.warning(f"Skipping non-existent file: {css_file}")
                    continue

                theme_name = os.path.basename(css_file).replace("_theme.css", "").capitalize()
                if ":" in css_file:  # For resource paths
                    theme_name = css_file.split("/")[-1].replace("_theme.css", "").capitalize()

                self.test_load_direct_css(css_file, include_common=True)
                input(f"Press Enter to continue after reviewing {theme_name} theme (with common.css)...")
        else:
            logger.warning("common.css not found, skipping Test 3")
            logger.info("This is expected if the application is designed without a common.css file")
            logger.info("The test confirms that themes work fine without common.css")

        logger.info("Theme CSS tests completed")

if __name__ == "__main__":
    test = ThemeCSSTest()
    test.window.show()
    test.run_tests()
    sys.exit(test.app.exec())
