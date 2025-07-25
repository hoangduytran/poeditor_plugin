"""
Theme Manager for the POEditor Application.

Manages theme loading, switching, and application.
Now supports both file-based CSS and resource-based CSS with fallback.
"""

import os
from typing import Optional, Dict
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtWidgets import QApplication
from .css_manager import CSSManager
from lg import logger

class ThemeManager:
    """
    Manages the application's theme, including loading, switching, and applying themes.
    Supports both file-based CSS themes and resource-based themes with fallback.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        """
        Initialize the ThemeManager instance.
        """
        self.current_theme = None
        self.css_manager = None
        self.use_file_css = False

        # Initialize CSS Manager for file-based CSS loading
        logger.debug("About to initialize CSS Manager...")
        try:
            self.css_manager = CSSManager()
            logger.debug(f"CSS Manager created, cache size: {len(self.css_manager.css_cache)}")
            self.use_file_css = len(self.css_manager.css_cache) > 0
            if self.use_file_css:
                logger.info("ThemeManager using file-based CSS system")
            else:
                logger.info("ThemeManager falling back to resource-based CSS system")
        except Exception as e:
            logger.error(f"Failed to initialize CSS Manager, using resources: {e}")
            self.css_manager = None
            self.use_file_css = False

    def set_theme(self, theme_name: str):
        """
        Set and apply the theme by name.

        Args:
            theme_name (str): The name of the theme to apply.
        """
        self.current_theme = theme_name
        theme_file_name = theme_name.lower().replace(" ", "_")

        # Load and apply the theme CSS
        css_content = self._load_theme_css(theme_file_name)
        self._apply_theme(css_content)

    def _load_theme_css(self, theme_file_name: str) -> str:
        """Load theme CSS content with fallback to resources."""
        logger.debug(f"Loading theme CSS for: {theme_file_name}")
        logger.debug(f"Use file CSS: {self.use_file_css}")
        logger.debug(f"CSS Manager available: {self.css_manager is not None}")
        
        # Try file-based CSS first
        if self.use_file_css and self.css_manager:
            css_content = self.css_manager.get_css(theme_file_name)
            if css_content:
                logger.info(f"Loaded theme CSS from file: {theme_file_name} ({len(css_content)} chars)")
                return css_content
            else:
                logger.warning(f"Theme CSS not found in files: {theme_file_name}, trying resources")
        
        logger.info(f"Falling back to resource-based CSS for: {theme_file_name}")
        # Fallback to resource-based CSS
        try:
            file = QFile(f":/themes/css/{theme_file_name}.css")
            if file.open(QIODevice.OpenModeFlag.ReadOnly):
                # Fix: Use .data() to get bytes and then decode
                byte_array = file.readAll()
                content = bytes(byte_array.data()).decode('utf-8')
                file.close()
                logger.debug(f"Loaded theme CSS from resources: {theme_file_name}")
                return content
            else:
                logger.error(f"Failed to open theme CSS resource: {theme_file_name}")
                return ""
        except Exception as e:
            logger.error(f"Error loading theme CSS from resources {theme_file_name}: {e}")
            return ""

    def _apply_theme(self, css_content: str):
        """Apply theme CSS to the application."""
        try:
            app = QApplication.instance()
            if not app:
                logger.error("No QApplication instance found for theme application")
                return
                
            # Add explicit type check for Pylance
            if not isinstance(app, QApplication):
                logger.error("Application instance is not QApplication")
                return
                
            app.setStyleSheet(css_content)
            logger.info(f"Applied theme CSS: {self.current_theme}")
        except Exception as e:
            logger.error(f"Failed to apply theme CSS: {e}")

    def reload_current_theme(self) -> bool:
        """Reload the current theme from disk (file-based CSS only)."""
        if not self.use_file_css or not self.css_manager:
            logger.warning("Reload not available - using resource-based CSS")
            return False
        
        if not self.current_theme:
            logger.warning("No current theme to reload")
            return False
        
        try:
            # Reload the CSS file
            theme_file_name = self.current_theme.lower().replace(" ", "_")
            if self.css_manager.reload_css_file(theme_file_name):
                # Reapply the theme
                self.set_theme(self.current_theme)
                logger.info(f"Successfully reloaded theme: {self.current_theme}")
                return True
            else:
                logger.error(f"Failed to reload theme file: {theme_file_name}")
                return False
        except Exception as e:
            logger.error(f"Error reloading theme: {e}")
            return False

    def get_raw_css(self, theme_name: str) -> Optional[str]:
        """Get raw CSS content for debugging."""
        theme_file_name = theme_name.lower().replace(" ", "_")
        
        if self.use_file_css and self.css_manager:
            return self.css_manager.get_css(theme_file_name)
        else:
            # Fallback to loading from resources
            return self._load_theme_css(theme_file_name)

    def inject_css(self, css_snippet: str, temporary: bool = True) -> bool:
        """Inject custom CSS snippet (development feature)."""
        try:
            app = QApplication.instance()  # Pylance thinks this is QCoreApplication
            if not app:
                logger.error("No QApplication instance for CSS injection")
                return False
            
            # Add explicit type checking/casting to tell Pylance it's a QApplication
            if not isinstance(app, QApplication):
                logger.error("Application instance is not QApplication")
                return False
                
            if temporary:
                # Append to current stylesheet
                current_css = app.styleSheet()
                new_css = f"{current_css}\n\n/* Injected CSS */\n{css_snippet}"
                app.setStyleSheet(new_css)
            else:
                # Replace stylesheet entirely
                app.setStyleSheet(css_snippet)
            
            logger.info("CSS injection successful")
            return True
            
        except Exception as e:
            logger.error(f"CSS injection failed: {e}")
            return False

    def get_css_manager_info(self) -> Dict:
        """Get information about CSS manager state."""
        info = {
            "use_file_css": self.use_file_css,
            "css_manager_available": self.css_manager is not None,
            "current_theme": self.current_theme
        }
        
        if self.css_manager:
            info["loaded_css_files"] = self.css_manager.get_css_info()
            info["available_themes"] = self.css_manager.get_available_themes()
        
        return info

    def get_available_themes(self) -> list:
        """Get list of available themes."""
        themes = ["Dark", "Light", "Colorful"]
        return themes

    def get_current_theme(self) -> Optional[str]:
        """Get the name of the currently applied theme."""
        return self.current_theme
        
    def apply_activity_bar_theme(self, widget) -> bool:
        """Apply activity bar specific theme."""
        try:
            if self.use_file_css and self.css_manager:
                activity_css = self.css_manager.get_css('activity_bar')
                if activity_css:
                    widget.setStyleSheet(activity_css)
                    logger.info(f"Applied activity bar theme to widget: {widget.objectName()}")
                    return True
            
            # Fallback to resource-based CSS
            file = QFile(":/themes/css/activity_bar.css")
            if file.open(QIODevice.OpenModeFlag.ReadOnly):
                # Fix: Use .data() to get bytes and then decode
                byte_array = file.readAll()
                content = bytes(byte_array.data()).decode('utf-8')
                file.close()
                widget.setStyleSheet(content)
                logger.info(f"Applied activity bar theme to widget: {widget.objectName()}")
                return True
            else:
                logger.error("Failed to open activity bar CSS resource")
                return False
        except Exception as e:
            logger.error(f"Error applying activity bar theme: {e}")
            return False

    def get_style_for_component(self, component_name: str) -> Dict:
        """Get style information for a specific component."""
        if component_name == "tabs":
            return {
                "background_color": "#1e1e1e",
                "border_color": "#464647",
                "text_color": "#cccccc" 
            }
        elif component_name == "tab_active":
            return {
                "background_color": "#1e1e1e",
                "text_color": "#ffffff",
                "border_color": "#007acc"
            }
        elif component_name == "tab_inactive":
            return {
                "background_color": "#2d2d30",
                "text_color": "#969696",
                "border_color": "#464647"
            }
        elif component_name == "tab_hover":
            return {
                "background_color": "#2a2d2e",
                "text_color": "#cccccc",
                "border_color": "#464647"
            }
        else:
            # Default style
            return {
                "background_color": "#252526",
                "text_color": "#cccccc",
                "border_color": "#464647"
            }

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of ThemeManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance