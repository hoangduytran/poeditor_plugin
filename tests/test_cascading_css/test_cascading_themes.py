#!/usr/bin/env python3
"""
CSS Cascading Theme Test

This test demonstrates Qt's CSS cascading behavior by loading a common base stylesheet
and overlaying different theme-specific stylesheets.

Controls:
- Ctrl+Shift+T: Cycle through themes (Dark → Light → Colorful → Dark...)
- Use the various UI elements to see how themes affect different widgets

The test shows how you can maintain a common.css with shared styles and override
only the colors/theme-specific properties in separate theme files.
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QLineEdit, QLabel,
    QGroupBox, QStatusBar, QToolBar, QScrollArea, QTextEdit, QSplitter
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
    
    def __init__(self, app, css_dir: Path):  # Removed type hint to avoid QCoreApplication vs QApplication issue
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


class ExplorerWidget(QWidget):
    """Simple explorer-like widget for testing CSS themes."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("ExplorerWidget")
        self._setup_ui()
        self._populate_tree()
        logger.debug("ExplorerWidget initialized")
    
    def _setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title label
        title_label = QLabel("File Explorer")
        title_label.setObjectName("ExplorerTitle")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files and folders...")
        self.search_input.setObjectName("ExplorerSearchInput")
        layout.addWidget(self.search_input)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setObjectName("ExplorerTreeWidget")
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        # self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)
        
        # Button controls
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("ExplorerRefreshButton")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        
        self.new_folder_btn = QPushButton("New Folder")
        self.new_folder_btn.setObjectName("ExplorerNewFolderButton")
        self.new_folder_btn.clicked.connect(self._on_new_folder_clicked)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("ExplorerDeleteButton")
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.new_folder_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect tree selection change
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _populate_tree(self):
        """Populate the tree with sample data."""
        # Root folders
        folders = [
            ("📁 Documents", "Folder", "—", [
                ("📄 Report.docx", "Word Document", "245 KB"),
                ("📄 Notes.txt", "Text File", "12 KB"),
                ("📁 Archive", "Folder", "—", [
                    ("📄 Old_Report.pdf", "PDF Document", "1.2 MB"),
                    ("📄 Backup.zip", "Archive", "568 KB")
                ])
            ]),
            ("📁 Pictures", "Folder", "—", [
                ("🖼️ Photo1.jpg", "JPEG Image", "2.3 MB"),
                ("🖼️ Photo2.png", "PNG Image", "1.8 MB"),
                ("🖼️ Screenshot.png", "PNG Image", "456 KB")
            ]),
            ("📁 Projects", "Folder", "—", [
                ("📁 WebApp", "Folder", "—", [
                    ("📄 index.html", "HTML File", "8 KB"),
                    ("📄 style.css", "CSS File", "15 KB"),
                    ("📄 script.js", "JavaScript", "22 KB")
                ]),
                ("📁 PythonProject", "Folder", "—", [
                    ("🐍 main.py", "Python File", "4 KB"),
                    ("🐍 utils.py", "Python File", "7 KB"),
                    ("📄 requirements.txt", "Text File", "1 KB")
                ])
            ]),
            ("📄 README.md", "Markdown File", "3 KB"),
            ("📄 config.json", "JSON File", "2 KB")
        ]
        
        def add_items(parent_item, items):
            for item_data in items:
                if len(item_data) == 4:  # Folder with children
                    name, type_str, size, children = item_data
                    item = QTreeWidgetItem(parent_item, [name, type_str, size])
                    add_items(item, children)
                else:  # File
                    name, type_str, size = item_data
                    item = QTreeWidgetItem(parent_item, [name, type_str, size])
        
        add_items(self.tree, folders)
        
        # Expand the first level
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:  # Check if item exists
                item.setExpanded(True)
        
        logger.debug("Explorer tree populated with sample data")
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        logger.info("Explorer refresh requested")
        # Simulate refresh by clearing and repopulating
        self.tree.clear()
        QTimer.singleShot(200, self._populate_tree)  # Small delay for visual effect
    
    def _on_new_folder_clicked(self):
        """Handle new folder button click."""
        logger.info("Explorer new folder requested")
        # Add a new folder to the tree
        new_item = QTreeWidgetItem(self.tree, ["📁 New Folder", "Folder", "—"])
        self.tree.setCurrentItem(new_item)
    
    def _on_delete_clicked(self):
        """Handle delete button click."""
        current_item = self.tree.currentItem()
        if current_item:
            logger.info(f"Explorer delete requested for: {current_item.text(0)}")
            parent = current_item.parent()
            if parent:
                parent.removeChild(current_item)
            else:
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(current_item))
    
    def _on_selection_changed(self):
        """Handle tree selection change."""
        current_item = self.tree.currentItem()
        self.delete_btn.setEnabled(current_item is not None)
        if current_item:
            logger.debug(f"Explorer selection changed to: {current_item.text(0)}")


class CascadingCSSTestWindow(QMainWindow):
    """Main test window for CSS cascading demonstration."""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("CascadingCSSTestWindow")
        self.setWindowTitle("CSS Cascading Theme Test - Press Ctrl+Shift+T to cycle themes")
        self.resize(800, 600)
        
        # Initialize theme manager
        css_dir = Path(__file__).parent / "css"
        app_instance = QApplication.instance()
        if not app_instance:
            raise RuntimeError("No QApplication instance found")
        self.theme_manager = ThemeManager(app_instance, css_dir)
        
        self._setup_ui()
        self._setup_shortcuts()
        
        # Apply initial theme
        self.theme_manager.apply_current_theme()
        self._update_window_title()
        
        logger.info("CascadingCSSTestWindow initialized")
    
    def _setup_ui(self):
        """Set up the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Left side - Explorer
        explorer_group = QGroupBox("File Explorer")
        explorer_group.setObjectName("ExplorerGroupBox")
        explorer_layout = QVBoxLayout(explorer_group)
        
        self.explorer = ExplorerWidget()
        explorer_layout.addWidget(self.explorer)
        
        # Right side - Controls and info
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Theme info group
        theme_group = QGroupBox("Theme Information")
        theme_group.setObjectName("ThemeInfoGroupBox")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_label = QLabel()
        self.theme_label.setObjectName("CurrentThemeLabel")
        theme_layout.addWidget(self.theme_label)
        
        theme_help = QLabel("Press Ctrl+Shift+T to cycle themes")
        theme_help.setObjectName("ThemeHelpLabel")
        theme_help.setStyleSheet("color: gray; font-style: italic;")
        theme_layout.addWidget(theme_help)
        
        # CSS info
        css_info = QLabel("""
CSS Cascading Test:
• common.css: Base styles (fonts, spacing, layout)
• theme.css: Color overrides only
• Later styles override earlier ones
• Demonstrates maintainable theming
        """.strip())
        css_info.setObjectName("CSSInfoLabel")
        css_info.setWordWrap(True)
        theme_layout.addWidget(css_info)
        
        controls_layout.addWidget(theme_group)
        
        # Test controls group
        test_group = QGroupBox("Test Controls")
        test_group.setObjectName("TestControlsGroupBox")
        test_layout = QVBoxLayout(test_group)
        
        # Test buttons
        test_buttons = [
            ("Test Button 1", "TestButton1"),
            ("Test Button 2", "TestButton2"),
            ("Disabled Button", "DisabledButton")
        ]
        
        for text, object_name in test_buttons:
            btn = QPushButton(text)
            btn.setObjectName(object_name)
            if "Disabled" in text:
                btn.setEnabled(False)
            else:
                btn.clicked.connect(lambda checked, t=text: logger.info(f"Clicked: {t}"))
            test_layout.addWidget(btn)
        
        # Test input
        test_input = QLineEdit("Test input field")
        test_input.setObjectName("TestLineEdit")
        test_layout.addWidget(test_input)
        
        controls_layout.addWidget(test_group)
        
        # Text area for logs
        log_group = QGroupBox("Theme Change Log")
        log_group.setObjectName("LogGroupBox")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("LogTextEdit")
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        controls_layout.addWidget(log_group)
        controls_layout.addStretch()
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(explorer_group)
        splitter.addWidget(controls_widget)
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready - Use Ctrl+Shift+T to cycle themes")
        self.statusBar().setObjectName("MainStatusBar")
        
        # Toolbar
        toolbar = self.addToolBar("Main")
        toolbar.setObjectName("MainToolBar")
        
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.explorer._on_refresh_clicked)
        toolbar.addAction(refresh_action)
        
        theme_action = QAction("🎨 Cycle Theme", self)
        theme_action.triggered.connect(self._cycle_theme)
        toolbar.addAction(theme_action)
        
        toolbar.addSeparator()
        
        help_action = QAction("❓ Help", self)
        help_action.triggered.connect(self._show_help)
        toolbar.addAction(help_action)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Ctrl+Shift+T to cycle themes
        theme_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        theme_shortcut.activated.connect(self._cycle_theme)
        
        logger.debug("Keyboard shortcuts set up: Ctrl+Shift+T for theme cycling")
    
    def _cycle_theme(self):
        """Cycle to the next theme."""
        new_theme = self.theme_manager.cycle_theme()
        self._update_window_title()
        self._log_theme_change(new_theme)
        
        # Update status bar
        self.statusBar().showMessage(f"Theme changed to: {new_theme.title()}")
        
        logger.info(f"Theme cycled to: {new_theme}")
    
    def _update_window_title(self):
        """Update window title with current theme."""
        theme_name = self.theme_manager.get_current_theme_name()
        self.setWindowTitle(f"CSS Cascading Theme Test - Current: {theme_name.title()} - Press Ctrl+Shift+T")
        
        # Update theme label
        self.theme_label.setText(f"Current Theme: {theme_name.title()}")
    
    def _log_theme_change(self, theme_name: str):
        """Log theme change to the text area."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] Theme changed to: {theme_name.title()}\n"
        self.log_text.append(log_entry.strip())
        
        # Keep only last 10 entries
        content = self.log_text.toPlainText()
        lines = content.split('\n')
        if len(lines) > 10:
            self.log_text.setPlainText('\n'.join(lines[-10:]))
    
    def _show_help(self):
        """Show help message."""
        from PySide6.QtWidgets import QMessageBox
        
        help_text = """
CSS Cascading Theme Test

This application demonstrates Qt's CSS cascading behavior:

1. common.css contains base styles (fonts, layouts, spacing)
2. Theme files (dark.css, light.css, colorful.css) contain only color overrides
3. Themes are applied by concatenating common + theme CSS
4. Later CSS rules override earlier ones (cascading)

Controls:
• Ctrl+Shift+T: Cycle through themes
• Use UI elements to see theme effects
• Watch the log for theme changes

This approach allows you to maintain one set of common styles
and only override colors/theme-specific properties.
        """.strip()
        
        QMessageBox.information(self, "Help", help_text)
        logger.info("Help dialog shown")


def main():
    """Main function to run the CSS cascading test."""
    app = QApplication(sys.argv)
    app.setApplicationName("CSS Cascading Theme Test")
    
    logger.info("=== CSS CASCADING THEME TEST STARTED ===")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Test directory: {Path(__file__).parent}")
    
    # Create and show the main window
    window = CascadingCSSTestWindow()
    window.show()
    
    logger.info("Main window shown - test ready")
    logger.info("Press Ctrl+Shift+T to cycle between themes")
    
    # Run the application
    try:
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
