"""
Test case for theme switching functionality using Ctrl+Shift+T hotkey.
This test creates a more realistic environment to test theme switching
and verify that the SidebarDockWidget title bar properly updates.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import cast
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QDockWidget, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

# Import the widgets and managers we want to test
from widgets.sidebar_dock_widget import SidebarDockWidget
from core.theme_manager import ThemeManager
from lg import logger

class TestSidebarContent(QWidget):
    """Test sidebar content with some interactive elements"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add some content to make it look realistic
        layout.addWidget(QLabel("EXPLORER"))

        # Add a text area to show current theme
        self.theme_display = QTextEdit()
        self.theme_display.setMaximumHeight(100)
        self.theme_display.setPlainText("Current theme: Loading...")
        layout.addWidget(self.theme_display)

        # Add some buttons
        layout.addWidget(QPushButton("Refresh"))
        layout.addWidget(QPushButton("New File"))
        layout.addWidget(QPushButton("New Folder"))

        # Add stretch to push content to top
        layout.addStretch()

class ThemeSwitchingTestWindow(QMainWindow):
    """Test window with theme switching functionality"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_theme_manager()
        self.setup_shortcuts()
        self.setup_auto_theme_switching()

    def setup_ui(self):
        self.setObjectName("main_window")
        self.setWindowTitle("Theme Switching Test - Press Ctrl+Shift+T to toggle theme")
        self.resize(1000, 700)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Add instructions
        instructions = QLabel("""
Theme Switching Test Instructions:
• Press Ctrl+Shift+T to toggle between light and dark themes
• Watch the SidebarDockWidget title bar for color changes
• Auto-switching will occur every 5 seconds for demonstration
• Check application.log for detailed theme switching information
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("instructionsLabel")
        layout.addWidget(instructions)

        # Add theme status display
        self.theme_status = QLabel("Current Theme: Initializing...")
        self.theme_status.setObjectName("themeStatusLabel")
        layout.addWidget(self.theme_status)

        # Add manual controls
        controls_layout = QHBoxLayout()
        self.toggle_btn = QPushButton("Toggle Theme (Ctrl+Shift+T)")
        self.toggle_btn.clicked.connect(self.toggle_theme)
        controls_layout.addWidget(self.toggle_btn)

        self.auto_toggle_btn = QPushButton("Disable Auto-Switch")
        self.auto_toggle_btn.clicked.connect(self.toggle_auto_switching)
        controls_layout.addWidget(self.auto_toggle_btn)

        layout.addLayout(controls_layout)

        # Add some content to central widget
        content_area = QTextEdit()
        content_area.setPlainText("""
This is the main content area.

The theme should affect:
1. This central content area
2. The SidebarDockWidget title bar (most important!)
3. All UI elements throughout the application

Monitor the application.log file to see detailed theme switching events
and palette changes for the SidebarDockWidget.
        """)
        layout.addWidget(content_area)

        # Create sidebar content
        sidebar_content = TestSidebarContent()

        # Create the SidebarDockWidget
        logger.info("=== Creating SidebarDockWidget for theme switching test ===")
        self.sidebar = SidebarDockWidget(sidebar_content, self)

        # Add the sidebar to the main window
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        logger.info("SidebarDockWidget added to main window for theme test")

    def setup_theme_manager(self):
        """Initialize the theme manager"""
        try:
            self.theme_manager = ThemeManager()
            self.current_theme = "dark"  # Start with dark theme
            logger.info("ThemeManager initialized for theme switching test")
        except Exception as e:
            logger.error(f"Failed to initialize ThemeManager: {e}")
            # Fallback: create a simple theme switcher
            self.theme_manager = None
            self.current_theme = "dark"

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for theme switching"""
        # Create Ctrl+Shift+T shortcut
        self.theme_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        self.theme_shortcut.activated.connect(self.toggle_theme)
        logger.info("Theme switching shortcut (Ctrl+Shift+T) registered")

    def setup_auto_theme_switching(self):
        """Setup automatic theme switching for demonstration"""
        self.auto_switch_enabled = True
        self.auto_switch_timer = QTimer(self)
        self.auto_switch_timer.timeout.connect(self.auto_toggle_theme)
        self.auto_switch_timer.start(5000)  # Switch every 5 seconds
        logger.info("Auto theme switching enabled (5 second intervals)")

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        logger.info("=== THEME TOGGLE REQUESTED ===")

        # Switch theme
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.apply_light_theme()
        else:
            self.current_theme = "dark"
            self.apply_dark_theme()

        # Update UI status
        self.theme_status.setText(f"Current Theme: {self.current_theme.title()}")

        # Update sidebar content - try-catch approach for unknown attributes
        sidebar_content = self.sidebar.widget()
        
        try:
            # Attempt to find QTextEdit in sidebar - may not exist
            theme_display = sidebar_content.findChild(QTextEdit)
            if theme_display:
                theme_display.setPlainText(f"Current theme: {self.current_theme.title()}")
        except (AttributeError, TypeError):
            # Widget may not have findChild or other issues
            pass

        logger.info(f"Theme switched to: {self.current_theme}")

    def apply_dark_theme(self):
        """Apply dark theme using only CSS files via ThemeManager"""
        logger.info("Applying dark theme...")
        if self.theme_manager:
            try:
                stylesheet = self.theme_manager.get_theme_stylesheet("dark")
                logger.debug(f"[DEBUG] Dark theme stylesheet content:\n{stylesheet}")
                # TEMP: Hard-code sidebar QSS to test if it works
                sidebar_test_qss = """
QDockWidget#SidebarDockWidget {
    background-color: #222244;
    color: #ffcc00;
}
QDockWidget#SidebarDockWidget::title {
    background-color: #333366;
    color: #ffcc00;
}
QDockWidget#SidebarDockWidget > QWidget {
    background-color: #222244;
    color: #ffcc00;
}
"""
                # full_stylesheet = stylesheet + "\n" + sidebar_test_qss
                full_stylesheet = stylesheet
                app = QApplication.instance()
                if app:
                    app = cast(QApplication, app)
                    app.setStyleSheet(full_stylesheet)
                    logger.info("Dark theme stylesheet (with hardcoded sidebar QSS) applied via ThemeManager")
            except Exception as e:
                logger.error(f"Failed to apply dark theme via ThemeManager: {e}")

    def apply_light_theme(self):
        """Apply light theme using only CSS files via ThemeManager"""
        logger.info("Applying light theme...")
        if self.theme_manager:
            try:
                stylesheet = self.theme_manager.get_theme_stylesheet("light")
                logger.debug(f"[DEBUG] Light theme stylesheet content:\n{stylesheet}")
                app = QApplication.instance()
                if app:
                    app = cast(QApplication, app)
                    app.setStyleSheet(stylesheet)
                    logger.info("Light theme stylesheet applied via ThemeManager")
            except Exception as e:
                logger.error(f"Failed to apply light theme via ThemeManager: {e}")

    def auto_toggle_theme(self):
        """Automatically toggle theme for demonstration"""
        if self.auto_switch_enabled:
            logger.info("Auto theme toggle triggered")
            self.toggle_theme()

    def toggle_auto_switching(self):
        """Toggle automatic theme switching"""
        self.auto_switch_enabled = not self.auto_switch_enabled

        if self.auto_switch_enabled:
            self.auto_switch_timer.start(5000)
            self.auto_toggle_btn.setText("Disable Auto-Switch")
            logger.info("Auto theme switching enabled")
        else:
            self.auto_switch_timer.stop()
            self.auto_toggle_btn.setText("Enable Auto-Switch")
            logger.info("Auto theme switching disabled")

    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Theme switching test window closing")
        try:
            self.auto_switch_timer.stop()
        except AttributeError:
            # Timer not created
            pass
        super().closeEvent(event)


def run_theme_switching_test():
    """Run the theme switching test"""
    logger.info("=== STARTING THEME SWITCHING TEST ===")

    app = QApplication(sys.argv)

    # Start with dark theme
    logger.info("Initializing with dark theme")

    # Create and show the test window
    window = ThemeSwitchingTestWindow()
    window.show()

    # Apply initial dark theme
    window.apply_dark_theme()

    logger.info("Theme switching test window created and displayed")
    logger.info("Use Ctrl+Shift+T to toggle themes manually")
    logger.info("Auto-switching will occur every 5 seconds")
    logger.info("Monitor application.log for detailed theme switching events")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_theme_switching_test())
