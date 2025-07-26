#!/usr/bin/env python3
"""
QToolBar CSS Theme Test

This test demonstrates how QToolBar and QPushButton styling looks across different themes
using CSS cascading behavior (common.css + theme-specific CSS).

Controls:
- Ctrl+Shift+T: Cycle through themes (Dark → Light → Colorful → Dark...)
- Click the Exit button to close the application
- Use the toolbar buttons to see how themes affect QToolBar and QPushButton styling

The test shows how QToolBar, QPushButton, and other widgets are styled consistently
across different themes using CSS cascading.
"""

import sys
import os
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QToolBar, QTextEdit, QSplitter, QStatusBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAction

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
        
        # Cascade: common styles first, then theme-specific overrides
        combined_css = self.common_css + "\n\n/* === THEME OVERRIDES === */\n" + theme_css
        
        logger.info(f"=== APPLYING THEME: {theme_name.upper()} ===")
        logger.debug(f"Combined CSS length: {len(combined_css)} characters")
        logger.debug(f"Common CSS portion: {len(self.common_css)} characters")
        logger.debug(f"Theme CSS portion: {len(theme_css)} characters")
        
        # Apply the cascaded stylesheet to the application
        self.app.setStyleSheet(combined_css)
        
        logger.info(f"Theme '{theme_name}' applied successfully via CSS cascading")
    
    def cycle_theme(self):
        """Cycle to the next theme."""
        old_theme = self.get_current_theme_name()
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        new_theme = self.get_current_theme_name()
        
        logger.info(f"Theme cycling: {old_theme} → {new_theme}")
        self.apply_current_theme()
        
        return new_theme


class QToolBarTestWidget(QWidget):
    """Widget demonstrating QToolBar styling across themes."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("QToolBarTestWidget")
        self._setup_ui()
        logger.debug("QToolBarTestWidget initialized")
    
    def _setup_ui(self):
        """Set up the UI layout with QToolBar examples."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel("QToolBar Styling Test")
        title_label.setObjectName("TestTitle")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("This test shows how QToolBar and QPushButton are styled in different themes.\nPress Ctrl+Shift+T to cycle themes.")
        desc_label.setObjectName("TestDescription")
        desc_label.setStyleSheet("color: #888; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Toolbar 1 - Main actions
        self._create_main_toolbar(layout)
        
        # Toolbar 2 - Secondary actions (smaller buttons)
        self._create_secondary_toolbar(layout)
        
        # Toolbar 3 - Text buttons (no icons)
        self._create_text_toolbar(layout)
        
        # Content area with text
        content_area = QTextEdit()
        content_area.setObjectName("ContentArea")
        content_area.setPlainText(
            "QToolBar Styling Test Content\n\n"
            "This text area shows how the content background is styled.\n"
            "The toolbars above demonstrate different button configurations:\n\n"
            "• Main Toolbar: Contains common actions like New, Open, Save, Exit\n"
            "• Secondary Toolbar: Contains smaller utility buttons\n"
            "• Text Toolbar: Contains text-only buttons without icons\n\n"
            "Each toolbar should inherit the theme colors while maintaining\n"
            "consistent spacing and visual hierarchy.\n\n"
            "Use Ctrl+Shift+T to cycle between themes and observe how\n"
            "the QToolBar styling adapts to each theme."
        )
        layout.addWidget(content_area)
    
    def _create_main_toolbar(self, layout: QVBoxLayout):
        """Create the main toolbar with primary actions."""
        toolbar_label = QLabel("Main Toolbar (Primary Actions)")
        toolbar_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(toolbar_label)
        
        main_toolbar = QToolBar()
        main_toolbar.setObjectName("MainToolBar")
        main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        main_toolbar.setMovable(False)
        
        # Add actions
        new_action = QAction("New", self)
        new_action.setToolTip("Create new document")
        new_action.triggered.connect(lambda: logger.info("New action triggered"))
        main_toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setToolTip("Open existing document")
        open_action.triggered.connect(lambda: logger.info("Open action triggered"))
        main_toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setToolTip("Save current document")
        save_action.triggered.connect(lambda: logger.info("Save action triggered"))
        main_toolbar.addAction(save_action)
        
        main_toolbar.addSeparator()
        
        # Exit button - this is the main focus of the test
        exit_action = QAction("Exit", self)
        exit_action.setToolTip("Exit application")
        exit_action.triggered.connect(self._on_exit_clicked)
        main_toolbar.addAction(exit_action)
        
        layout.addWidget(main_toolbar)
    
    def _create_secondary_toolbar(self, layout: QVBoxLayout):
        """Create a secondary toolbar with utility actions."""
        toolbar_label = QLabel("Secondary Toolbar (Utility Actions)")
        toolbar_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(toolbar_label)
        
        secondary_toolbar = QToolBar()
        secondary_toolbar.setObjectName("SecondaryToolBar")
        secondary_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        secondary_toolbar.setMovable(False)
        
        # Add utility actions
        undo_action = QAction("↶", self)
        undo_action.setToolTip("Undo last action")
        undo_action.triggered.connect(lambda: logger.info("Undo action triggered"))
        secondary_toolbar.addAction(undo_action)
        
        redo_action = QAction("↷", self)
        redo_action.setToolTip("Redo last action")
        redo_action.triggered.connect(lambda: logger.info("Redo action triggered"))
        secondary_toolbar.addAction(redo_action)
        
        secondary_toolbar.addSeparator()
        
        copy_action = QAction("📋", self)
        copy_action.setToolTip("Copy selection")
        copy_action.triggered.connect(lambda: logger.info("Copy action triggered"))
        secondary_toolbar.addAction(copy_action)
        
        paste_action = QAction("📄", self)
        paste_action.setToolTip("Paste from clipboard")
        paste_action.triggered.connect(lambda: logger.info("Paste action triggered"))
        secondary_toolbar.addAction(paste_action)
        
        layout.addWidget(secondary_toolbar)
    
    def _create_text_toolbar(self, layout: QVBoxLayout):
        """Create a toolbar with text-only buttons."""
        toolbar_label = QLabel("Text-Only Toolbar")
        toolbar_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(toolbar_label)
        
        text_toolbar = QToolBar()
        text_toolbar.setObjectName("TextToolBar")
        text_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        text_toolbar.setMovable(False)
        
        # Add text actions
        bold_action = QAction("Bold", self)
        bold_action.setToolTip("Make text bold")
        bold_action.triggered.connect(lambda: logger.info("Bold action triggered"))
        text_toolbar.addAction(bold_action)
        
        italic_action = QAction("Italic", self)
        italic_action.setToolTip("Make text italic")
        italic_action.triggered.connect(lambda: logger.info("Italic action triggered"))
        text_toolbar.addAction(italic_action)
        
        underline_action = QAction("Underline", self)
        underline_action.setToolTip("Underline text")
        underline_action.triggered.connect(lambda: logger.info("Underline action triggered"))
        text_toolbar.addAction(underline_action)
        
        text_toolbar.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.setToolTip("Open settings")
        settings_action.triggered.connect(lambda: logger.info("Settings action triggered"))
        text_toolbar.addAction(settings_action)
        
        layout.addWidget(text_toolbar)
    
    def _on_exit_clicked(self):
        """Handle exit button click."""
        logger.info("Exit button clicked - closing application")
        app = QApplication.instance()
        if app:
            app.quit()


class QToolBarTestWindow(QMainWindow):
    """Main window for the QToolBar theme test."""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("QToolBarTestWindow")
        self.setWindowTitle("QToolBar CSS Theme Test")
        self.setMinimumSize(800, 600)
        
        # Initialize theme manager
        css_dir = Path(__file__).parent / "css"
        self.theme_manager = ThemeManager(QApplication.instance(), css_dir)
        
        # Setup UI
        self._setup_ui()
        self._setup_shortcuts()
        
        # Apply initial theme
        self.theme_manager.apply_current_theme()
        
        logger.info("QToolBarTestWindow initialized")
    
    def _setup_ui(self):
        """Set up the main UI."""
        # Central widget
        self.test_widget = QToolBarTestWidget()
        self.setCentralWidget(self.test_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()
    
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
            f"Current Theme: {theme_name.title()} | Press Ctrl+Shift+T to cycle themes | Click Exit to close"
        )


def main():
    """Main function to run the QToolBar theme test."""
    logger.info("Starting QToolBar CSS Theme Test")
    
    app = QApplication(sys.argv)
    app.setApplicationName("QToolBar CSS Theme Test")
    
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
    window = QToolBarTestWindow()
    window.show()
    
    logger.info("QToolBar theme test window displayed")
    logger.info("Use Ctrl+Shift+T to cycle themes")
    logger.info("Click the Exit button in the toolbar to close")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
