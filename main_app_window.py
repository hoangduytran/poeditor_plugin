"""
Main Application Window for POEditor.
"""

from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction
from managers.theme_manager import ThemeManager
import logging

logger = logging.getLogger(__name__)

class MainAppWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainAppWindow, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # ...existing setup code...

        # Add development menu for CSS features
        self._setup_development_menu()

        # ...existing setup code...

    def _setup_development_menu(self):
        """Setup development menu with CSS debugging features."""
        try:
            logger.debug("Setting up development menu...")
            menubar = self.menuBar()
            if not menubar:
                logger.error("No menubar found!")
                return

            # Create Development menu
            dev_menu = menubar.addMenu("Development")
            logger.debug("Development menu created")

            # Theme reloading action
            reload_action = QAction("Reload Current Theme", self)
            reload_action.setShortcut("Ctrl+Shift+R")
            reload_action.triggered.connect(self._reload_current_theme)
            dev_menu.addAction(reload_action)

            # CSS info action
            css_info_action = QAction("CSS Manager Info", self)
            css_info_action.triggered.connect(self._show_css_info)
            dev_menu.addAction(css_info_action)

            # CSS injection action
            inject_css_action = QAction("Inject Test CSS", self)
            inject_css_action.triggered.connect(self._inject_test_css)
            dev_menu.addAction(inject_css_action)

            logger.debug("Development menu created with CSS features")

        except Exception as e:
            logger.error(f"Failed to create development menu: {e}")

    def _reload_current_theme(self):
        """Reload the current theme from disk."""
        try:
            theme_manager = ThemeManager.get_instance()
            if theme_manager.reload_current_theme():
                logger.info("Theme reloaded successfully")
                # Show status message
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage("Theme reloaded", 2000)
            else:
                logger.warning("Theme reload failed or not available")
        except Exception as e:
            logger.error(f"Error during theme reload: {e}")

    def _show_css_info(self):
        """Show CSS manager information."""
        try:
            theme_manager = ThemeManager.get_instance()
            info = theme_manager.get_css_manager_info()

            info_text = []
            info_text.append(f"CSS System: {'File-based' if info['use_file_css'] else 'Resource-based'}")
            info_text.append(f"Current Theme: {info['current_theme']}")

            if info.get('loaded_css_files'):
                info_text.append("\nLoaded CSS Files:")
                for name, size in info['loaded_css_files'].items():
                    info_text.append(f"  {name}: {size} characters")

            if info.get('available_themes'):
                info_text.append(f"\nAvailable Themes: {', '.join(info['available_themes'])}")

            # Add debug info about CSS Manager state
            if hasattr(theme_manager, 'css_manager') and theme_manager.css_manager:
                info_text.append(f"\nCSS Manager initialized: True")
                info_text.append(f"CSS Cache size: {len(theme_manager.css_manager.css_cache)}")
                info_text.append(f"CSS Directory: {theme_manager.css_manager.css_directory}")
            else:
                info_text.append(f"\nCSS Manager initialized: False")

            print("=== CSS MANAGER DEBUG INFO ===")
            for line in info_text:
                print(line)
            print("==============================")

            logger.info("CSS Manager Info:\n" + "\n".join(info_text))

        except Exception as e:
            logger.error(f"Error getting CSS info: {e}")

    def _inject_test_css(self):
        """Inject test CSS to verify the toolbar issue."""
        test_css = """
        /* Test CSS for Sidebar Toolbar */
        QToolBar#sidebar_toolbar {
            background-color: #ff0000 !important;
            border: 2px solid #00ff00 !important;
            min-height: 40px !important;
        }

        QPushButton#sidebar_arrow_button {
            background-color: #0000ff !important;
            color: #ffffff !important;
            font-weight: bold !important;
        }
        """

        try:
            theme_manager = ThemeManager.get_instance()
            if theme_manager.inject_css(test_css):
                logger.info("Test CSS injected - toolbar should now be red with green border")
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage("Test CSS injected", 3000)
            else:
                logger.error("Failed to inject test CSS")
        except Exception as e:
            logger.error(f"Error injecting test CSS: {e}")

    def setup_theme_system(self):
        """Initialize and setup the theme system."""
        from managers.theme_manager import ThemeManager
        
        theme_manager = ThemeManager.get_instance()
        theme_manager.set_theme("Dark")  # Default theme
        
        logger.info("Theme system initialized")

    # ...existing methods...