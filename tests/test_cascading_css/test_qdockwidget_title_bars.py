#!/usr/bin/env python3
"""
QDockWidget Title Bar Customization Test

This test demonstrates various ways to customize QDockWidget title bars:
1. CSS styling of native title bar
2. Custom title bar widget with buttons
3. Advanced title bar with multiple controls
4. Theme switching to see how customizations adapt

Controls:
- Ctrl+Shift+T: Cycle through themes (Dark → Light → Colorful → Dark...)
- Use the various title bar buttons to test functionality
- Try docking/undocking the dock widgets

The test shows how much you can customize QDockWidget title bars while
maintaining theme consistency.
"""

import sys
import os
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QDockWidget, QTextEdit, QStatusBar, QFrame,
    QToolButton, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut, QAction, QFont, QPalette

# Add the project root to the path so we can import lg
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging - try to use project logger, fall back to basic logging
try:
    # Try to change to project directory for lg module
    original_cwd = os.getcwd()
    os.chdir(project_root)
    from lg import logger
    os.chdir(original_cwd)
    logger.info("Successfully imported project logger")
except Exception as e:
    # Fall back to basic logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Using fallback logger - could not import lg: {e}")


class ThemeManager:
    """Manages CSS theme loading and cascading."""

    def __init__(self, app, css_dir: Path):
        self.app = app
        self.css_dir = css_dir
        self.themes = ["dark", "light", "colorful"]
        self.current_theme_index = 0

        # Load common base styles
        self.common_css = self._load_css_file("common.css")
        logger.info(f"Loaded common CSS: {len(self.common_css)} characters")

        # Load all theme files
        self.theme_styles = {}
        for theme in self.themes:
            css_content = self._load_css_file(f"{theme}.css")
            self.theme_styles[theme] = css_content
            logger.info(f"Loaded {theme} theme CSS: {len(css_content)} characters")

    def _load_css_file(self, filename: str) -> str:
        """Load CSS content from file."""
        css_path = self.css_dir / filename
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Successfully loaded CSS file: {css_path}")
            return content
        except FileNotFoundError:
            logger.error(f"CSS file not found: {css_path}")
            return ""
        except Exception as e:
            logger.error(f"Error loading CSS file {css_path}: {e}")
            return ""

    def get_current_theme_name(self) -> str:
        """Get the name of the currently active theme."""
        return self.themes[self.current_theme_index]

    def apply_current_theme(self):
        """Apply the current theme by cascading common + theme-specific CSS."""
        theme_name = self.get_current_theme_name()
        theme_css = self.theme_styles.get(theme_name, "")

        # Add specific QDockWidget title bar styling
        dock_widget_css = self._get_dock_widget_css()

        # Cascade: common styles first, then theme-specific overrides, then dock widget styles
        combined_css = (
            self.common_css +
            "\n\n/* === THEME OVERRIDES === */\n" + theme_css +
            "\n\n/* === DOCK WIDGET TITLE BAR STYLES === */\n" + dock_widget_css
        )

        logger.info(f"=== APPLYING THEME: {theme_name.upper()} ===")
        logger.debug(f"Combined CSS length: {len(combined_css)} characters")

        # Apply the cascaded stylesheet to the application
        self.app.setStyleSheet(combined_css)

        logger.info(f"Theme '{theme_name}' applied successfully via CSS cascading")

    def _get_dock_widget_css(self) -> str:
        """Get CSS for styling QDockWidget title bars."""
        return """
/* QDockWidget Title Bar Styling */
QDockWidget::title {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 8px 12px;
    text-align: left;
    border: none;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 0.5px;
}

QDockWidget::float-button {
    background-color: #555555;
    border: 1px solid #666666;
    border-radius: 4px;
    width: 16px;
    height: 16px;
    margin: 2px;
}

QDockWidget::float-button:hover {
    background-color: #007acc;
    border-color: #0099ff;
}

QDockWidget::float-button:pressed {
    background-color: #005a9e;
}

QDockWidget::close-button {
    background-color: #d73a49;
    border: 1px solid #dc3545;
    border-radius: 4px;
    width: 16px;
    height: 16px;
    margin: 2px;
}

QDockWidget::close-button:hover {
    background-color: #e74c3c;
}

/* Custom title bar widgets */
.CustomTitleBar {
    background-color: #2d2d30;
    border-bottom: 1px solid #464647;
    padding: 4px;
}

.TitleLabel {
    color: #cccccc;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.TitleButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 3px;
    color: #cccccc;
    padding: 4px 8px;
    font-size: 10px;
    min-width: 20px;
    max-width: 30px;
}

.TitleButton:hover {
    background-color: #007acc;
    border-color: #0099ff;
    color: #ffffff;
}

.TitleButton:pressed {
    background-color: #005a9e;
}

.FloatButton {
    background-color: #4a4a4a;
    border: 1px solid #666666;
    border-radius: 3px;
    color: #cccccc;
    font-weight: bold;
}

.FloatButton:hover {
    background-color: #007acc;
    color: #ffffff;
}

.SettingsButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 3px;
    color: #cccccc;
}

.SettingsButton:hover {
    background-color: #6c6c6c;
    color: #ffffff;
}
"""

    def cycle_theme(self):
        """Cycle to the next theme."""
        old_theme = self.get_current_theme_name()
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        new_theme = self.get_current_theme_name()

        logger.info(f"Theme cycling: {old_theme} → {new_theme}")
        self.apply_current_theme()

        return new_theme


class CustomTitleBar(QFrame):
    """Custom title bar widget with full control over appearance and functionality."""

    # Signals for title bar actions
    floatRequested = Signal()
    closeRequested = Signal()
    settingsRequested = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("CustomTitleBar")
        self.setProperty("class", "CustomTitleBar")
        self.title = title
        self._setup_ui()
        self._setup_drag()
        logger.debug(f"CustomTitleBar created: {title}")

    def _setup_ui(self):
        """Set up the custom title bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setProperty("class", "TitleLabel")
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Spacer to push buttons to the right
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.setProperty("class", "SettingsButton")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(24, 20)
        self.settings_btn.clicked.connect(self.settingsRequested.emit)
        layout.addWidget(self.settings_btn)

        # Float/dock button
        self.float_btn = QPushButton("⚏")
        self.float_btn.setObjectName("FloatButton")
        self.float_btn.setProperty("class", "FloatButton")
        self.float_btn.setToolTip("Float/Dock")
        self.float_btn.setFixedSize(24, 20)
        self.float_btn.clicked.connect(self.floatRequested.emit)
        layout.addWidget(self.float_btn)

        # Close button (optional)
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setProperty("class", "TitleButton")
        self.close_btn.setToolTip("Close")
        self.close_btn.setFixedSize(24, 20)
        self.close_btn.clicked.connect(self.closeRequested.emit)
        layout.addWidget(self.close_btn)

        # Set fixed height for title bar
        self.setFixedHeight(28)

    def _setup_drag(self):
        """Set up drag functionality for the title bar."""
        self._drag_start_position = None

    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging the dock widget."""
        if (event.buttons() == Qt.MouseButton.LeftButton and
            self._drag_start_position is not None):

            # Find the parent dock widget
            dock_widget = self.parent()
            while dock_widget and not isinstance(dock_widget, QDockWidget):
                dock_widget = dock_widget.parent()

            if dock_widget and dock_widget.isFloating():
                # Move the floating dock widget
                delta = event.globalPosition().toPoint() - self._drag_start_position
                dock_widget.move(dock_widget.pos() + delta)
                self._drag_start_position = event.globalPosition().toPoint()

        super().mouseMoveEvent(event)

    def update_float_button(self, is_floating: bool):
        """Update the float button based on floating state."""
        if is_floating:
            self.float_btn.setText("⊞")  # Dock icon
            self.float_btn.setToolTip("Dock")
        else:
            self.float_btn.setText("⚏")  # Float icon
            self.float_btn.setToolTip("Float")


class AdvancedTitleBar(QFrame):
    """Advanced title bar with more controls and status indicators."""

    # Signals
    floatRequested = Signal()
    settingsRequested = Signal()
    refreshRequested = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("AdvancedTitleBar")
        self.setProperty("class", "CustomTitleBar")
        self.title = title
        self._setup_ui()
        logger.debug(f"AdvancedTitleBar created: {title}")

    def _setup_ui(self):
        """Set up the advanced title bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #28a745; font-size: 8px;")
        self.status_indicator.setToolTip("Status: Active")
        layout.addWidget(self.status_indicator)

        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setProperty("class", "TitleLabel")
        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Item count label
        self.count_label = QLabel("(0 items)")
        self.count_label.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(self.count_label)

        # Spacer
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Refresh button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setProperty("class", "TitleButton")
        self.refresh_btn.setToolTip("Refresh")
        self.refresh_btn.setFixedSize(22, 18)
        self.refresh_btn.clicked.connect(self.refreshRequested.emit)
        layout.addWidget(self.refresh_btn)

        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setProperty("class", "SettingsButton")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(22, 18)
        self.settings_btn.clicked.connect(self.settingsRequested.emit)
        layout.addWidget(self.settings_btn)

        # Float button
        self.float_btn = QPushButton("⚏")
        self.float_btn.setProperty("class", "FloatButton")
        self.float_btn.setToolTip("Float/Dock")
        self.float_btn.setFixedSize(22, 18)
        self.float_btn.clicked.connect(self.floatRequested.emit)
        layout.addWidget(self.float_btn)

        self.setFixedHeight(26)

    def update_count(self, count: int):
        """Update the item count display."""
        self.count_label.setText(f"({count} items)")

    def update_status(self, status: str, color: str = "#28a745"):
        """Update the status indicator."""
        self.status_indicator.setStyleSheet(f"color: {color}; font-size: 8px;")
        self.status_indicator.setToolTip(f"Status: {status}")


class StyledDockWidget(QDockWidget):
    """QDockWidget with CSS-styled native title bar."""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setObjectName("StyledDockWidget")

        # Enable all features to show all title bar buttons
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        # Create content
        content = QTextEdit()
        content.setPlainText(
            f"CSS-Styled Native Title Bar\n\n"
            f"This dock widget uses the native QDockWidget title bar\n"
            f"styled with CSS. You can see the customized:\n\n"
            f"• Title bar background and text\n"
            f"• Float button styling\n"
            f"• Close button styling\n"
            f"• Hover effects\n\n"
            f"The title bar is fully functional with native Qt behavior."
        )
        self.setWidget(content)

        logger.debug(f"StyledDockWidget created: {title}")


class CustomDockWidget(QDockWidget):
    """QDockWidget with completely custom title bar."""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setObjectName("CustomDockWidget")

        # Create custom title bar
        self.custom_title_bar = CustomTitleBar(title)
        self.setTitleBarWidget(self.custom_title_bar)

        # Connect signals
        self.custom_title_bar.floatRequested.connect(self._toggle_float)
        self.custom_title_bar.closeRequested.connect(self.close)
        self.custom_title_bar.settingsRequested.connect(self._show_settings)

        # Connect to floating state changes
        self.topLevelChanged.connect(self._on_floating_changed)

        # Create content
        content = QTextEdit()
        content.setPlainText(
            f"Custom Title Bar Widget\n\n"
            f"This dock widget uses a completely custom title bar widget\n"
            f"that replaces the native title bar. Features:\n\n"
            f"• Custom title label\n"
            f"• Settings button (⚙)\n"
            f"• Float/dock button (⚏/⊞)\n"
            f"• Close button (✕)\n"
            f"• Custom styling via CSS\n"
            f"• Drag support for floating windows\n\n"
            f"Click the buttons to test functionality!"
        )
        self.setWidget(content)

        logger.debug(f"CustomDockWidget created: {title}")

    def _toggle_float(self):
        """Toggle floating state."""
        self.setFloating(not self.isFloating())
        logger.info(f"CustomDockWidget float toggled: {self.isFloating()}")

    def _show_settings(self):
        """Handle settings button click."""
        logger.info("CustomDockWidget settings requested")
        # Here you could show a settings dialog

    def _on_floating_changed(self, floating: bool):
        """Handle floating state change."""
        self.custom_title_bar.update_float_button(floating)
        logger.debug(f"CustomDockWidget floating state changed: {floating}")


class AdvancedDockWidget(QDockWidget):
    """QDockWidget with advanced custom title bar."""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setObjectName("AdvancedDockWidget")

        # Create advanced title bar
        self.advanced_title_bar = AdvancedTitleBar(title)
        self.setTitleBarWidget(self.advanced_title_bar)

        # Connect signals
        self.advanced_title_bar.floatRequested.connect(self._toggle_float)
        self.advanced_title_bar.settingsRequested.connect(self._show_settings)
        self.advanced_title_bar.refreshRequested.connect(self._refresh_content)

        # Initialize item count
        self.item_count = 5

        # Create content with some items
        self.content = QTextEdit()
        self._update_content()
        self.setWidget(self.content)

        # Update title bar with initial count
        self.advanced_title_bar.update_count(self.item_count)

        logger.debug(f"AdvancedDockWidget created: {title}")

    def _update_content(self):
        """Update the content display."""
        self.content.setPlainText(
            f"Advanced Custom Title Bar\n\n"
            f"This dock widget demonstrates an advanced custom title bar with:\n\n"
            f"• Status indicator (●)\n"
            f"• Item count display\n"
            f"• Refresh button (↻)\n"
            f"• Settings button (⚙)\n"
            f"• Float button (⚏)\n"
            f"• Compact design\n\n"
            f"Current items: {self.item_count}\n"
            f"Status: Active\n\n"
            f"Try the different buttons to see their functionality!"
        )

    def _toggle_float(self):
        """Toggle floating state."""
        self.setFloating(not self.isFloating())
        logger.info(f"AdvancedDockWidget float toggled: {self.isFloating()}")

    def _show_settings(self):
        """Handle settings button click."""
        logger.info("AdvancedDockWidget settings requested")
        self.advanced_title_bar.update_status("Configuring", "#ffc107")
        QTimer.singleShot(2000, lambda: self.advanced_title_bar.update_status("Active", "#28a745"))

    def _refresh_content(self):
        """Handle refresh button click."""
        logger.info("AdvancedDockWidget refresh requested")
        self.item_count += 1
        self.advanced_title_bar.update_count(self.item_count)
        self.advanced_title_bar.update_status("Refreshing", "#007bff")
        self._update_content()
        QTimer.singleShot(1000, lambda: self.advanced_title_bar.update_status("Active", "#28a745"))


class DockWidgetTestWindow(QMainWindow):
    """Main window for testing QDockWidget title bar customizations."""

    def __init__(self):
        super().__init__()
        self.setObjectName("DockWidgetTestWindow")
        self.setWindowTitle("QDockWidget Title Bar Customization Test")
        self.setMinimumSize(1000, 700)

        # Initialize theme manager
        css_dir = Path(__file__).parent / "css"
        self.theme_manager = ThemeManager(QApplication.instance(), css_dir)

        # Setup UI
        self._setup_ui()
        self._setup_dock_widgets()
        self._setup_shortcuts()

        # Apply initial theme
        self.theme_manager.apply_current_theme()

        logger.info("DockWidgetTestWindow initialized")

    def _setup_ui(self):
        """Set up the main UI."""
        # Central widget
        central_widget = QTextEdit()
        central_widget.setPlainText(
            "QDockWidget Title Bar Customization Test\n\n"
            "This test demonstrates various approaches to customizing QDockWidget title bars:\n\n"
            "1. CSS-Styled Native Title Bar (Left)\n"
            "   - Uses native QDockWidget title bar\n"
            "   - Styled with CSS selectors\n"
            "   - Maintains native functionality\n\n"
            "2. Custom Title Bar Widget (Right)\n"
            "   - Completely custom widget\n"
            "   - Full control over appearance\n"
            "   - Custom buttons and functionality\n\n"
            "3. Advanced Title Bar (Bottom)\n"
            "   - Enhanced custom title bar\n"
            "   - Status indicators and counters\n"
            "   - Multiple action buttons\n\n"
            "Controls:\n"
            "• Ctrl+Shift+T: Cycle themes to see how title bars adapt\n"
            "• Drag title bars to move dock widgets\n"
            "• Use float buttons to dock/undock\n"
            "• Try the various custom buttons\n\n"
            "Each approach has different benefits:\n"
            "- Native styling is simpler but less flexible\n"
            "- Custom widgets offer complete control\n"
            "- Advanced bars can include rich functionality"
        )
        self.setCentralWidget(central_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    def _setup_dock_widgets(self):
        """Set up the test dock widgets."""
        # CSS-styled native title bar
        self.styled_dock = StyledDockWidget("Native CSS Styled")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.styled_dock)

        # Custom title bar
        self.custom_dock = CustomDockWidget("Custom Title Bar")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.custom_dock)

        # Advanced title bar
        self.advanced_dock = AdvancedDockWidget("Advanced Controls")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.advanced_dock)

        logger.debug("Dock widgets set up")

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Theme cycling shortcut
        theme_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        theme_shortcut.activated.connect(self._cycle_theme)

        logger.debug("Shortcuts set up: Ctrl+Shift+T for theme cycling")

    def _cycle_theme(self):
        """Cycle to the next theme."""
        new_theme = self.theme_manager.cycle_theme()
        self._update_status_bar()
        logger.info(f"Theme changed to: {new_theme}")

    def _update_status_bar(self):
        """Update the status bar with current theme info."""
        theme_name = self.theme_manager.get_current_theme_name()
        self.status_bar.showMessage(
            f"Current Theme: {theme_name.title()} | Press Ctrl+Shift+T to cycle themes | "
            f"Try docking/undocking and using the custom title bar buttons"
        )


def main():
    """Main function to run the QDockWidget title bar test."""
    logger.info("Starting QDockWidget Title Bar Customization Test")

    app = QApplication(sys.argv)
    app.setApplicationName("QDockWidget Title Bar Test")

    # Check if CSS files exist
    css_dir = Path(__file__).parent / "css"
    if not css_dir.exists():
        logger.error(f"CSS directory not found: {css_dir}")
        logger.error("Please ensure the css/ directory exists with theme files")
        return 1

    required_files = ["common.css", "dark.css", "light.css", "colorful.css"]
    missing_files = []
    for filename in required_files:
        if not (css_dir / filename).exists():
            missing_files.append(filename)

    if missing_files:
        logger.error(f"Missing CSS files: {missing_files}")
        logger.error(f"Please ensure all required CSS files exist in: {css_dir}")
        return 1

    # Create and show the main window
    window = DockWidgetTestWindow()
    window.show()

    logger.info("QDockWidget title bar test window displayed")
    logger.info("Use Ctrl+Shift+T to cycle themes")
    logger.info("Try the different title bar customizations")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
