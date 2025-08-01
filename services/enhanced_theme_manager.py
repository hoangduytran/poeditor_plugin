import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from lg import logger
from services.css_preprocessor import CSSPreprocessor

# For PySide6 support
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

class EnhancedThemeManager:
    """Enhanced Theme Manager for CSS-based theming in Qt applications

    This class manages theme loading, switching, and application in Qt applications.
    It uses the CSSPreprocessor to handle CSS variables which aren't natively supported
    in PySide6.
    """

    DEFAULT_THEME = "light"
    SETTINGS_GROUP = "Appearance"
    THEME_SETTING_KEY = "Theme"

    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.preprocessor = CSSPreprocessor(themes_dir)

        # Cache for processed CSS
        self.processed_css: Dict[str, str] = {}

        # Current theme
        self._current_theme = self._load_theme_from_settings()

        logger.info(f"Enhanced Theme Manager initialized with current theme: {self._current_theme}")

    def get_theme_list(self) -> List[str]:
        """Get list of available themes

        Returns:
            List of theme names
        """
        themes = []
        variants_dir = self.themes_dir / "variants"

        if variants_dir.exists():
            for theme_file in variants_dir.glob("*.css"):
                theme_name = theme_file.stem
                themes.append(theme_name)

        return sorted(themes)

    def get_current_theme(self) -> str:
        """Get the current theme name

        Returns:
            Current theme name
        """
        return self._current_theme

    def _load_theme_from_settings(self) -> str:
        """Load theme name from application settings

        Returns:
            Theme name from settings or default theme
        """
        settings = QSettings()
        settings.beginGroup(self.SETTINGS_GROUP)
        theme = settings.value(self.THEME_SETTING_KEY, self.DEFAULT_THEME)
        settings.endGroup()

        # Validate theme exists (after directory structure is created)
        variants_dir = self.themes_dir / "variants"
        if variants_dir.exists():
            theme_file = variants_dir / f"{theme}.css"
            if not theme_file.exists():
                logger.warning(f"Theme '{theme}' from settings not found, using default theme")
                theme = self.DEFAULT_THEME

        return theme

    def _save_theme_to_settings(self, theme_name: str):
        """Save theme name to application settings

        Args:
            theme_name: Theme name to save
        """
        settings = QSettings()
        settings.beginGroup(self.SETTINGS_GROUP)
        settings.setValue(self.THEME_SETTING_KEY, theme_name)
        settings.endGroup()

        logger.debug(f"Saved theme '{theme_name}' to settings")

    def load_theme(self, theme_name: str) -> str:
        """Load and process CSS for a theme

        Args:
            theme_name: Theme name

        Returns:
            Processed CSS for the theme
        """
        # Check cache first
        if theme_name in self.processed_css:
            logger.debug(f"Using cached CSS for theme: {theme_name}")
            return self.processed_css[theme_name]

        # Generate CSS
        css = self.preprocessor.generate_final_css(theme_name)

        # Cache processed CSS
        self.processed_css[theme_name] = css

        return css

    def switch_theme(self, theme_name: str) -> bool:
        """Switch to a different theme

        Args:
            theme_name: Theme name

        Returns:
            True if theme was switched, False otherwise
        """
        # Check if theme exists
        available_themes = self.get_theme_list()
        if theme_name not in available_themes:
            logger.error(f"Theme '{theme_name}' not found. Available themes: {available_themes}")
            return False

        # No change needed if already using this theme
        if theme_name == self._current_theme:
            logger.debug(f"Already using theme: {theme_name}")
            return True

        # Update current theme
        self._current_theme = theme_name

        # Save to settings
        self._save_theme_to_settings(theme_name)

        logger.info(f"Switched to theme: {theme_name}")
        return True

    def reload_styles(self) -> str:
        """Reload styles for the current theme

        This is useful during development when CSS files are changed

        Returns:
            Reloaded CSS for current theme
        """
        # Clear caches
        self.processed_css = {}
        self.preprocessor.clear_cache()

        # Reload current theme
        return self.load_theme(self._current_theme)

    def apply_theme_to_application(self, app: QApplication) -> bool:
        """Apply the current theme to the application

        Args:
            app: QApplication instance

        Returns:
            True if theme was applied, False otherwise
        """
        if app is None:
            logger.error("Cannot apply theme: QApplication instance is None")
            return False

        # Load theme CSS
        css = self.load_theme(self._current_theme)
        if not css:
            logger.error(f"Failed to load theme: {self._current_theme}")
            return False

        # Set data-theme attribute on root element
        # This is used by CSS selectors like :root[data-theme="dark"]
        app.setProperty("data-theme", self._current_theme)

        # Apply stylesheet
        app.setStyleSheet(css)

        logger.info(f"Applied theme '{self._current_theme}' to application")
        return True

    def apply_theme_to_widget(self, widget: Any, theme_name: Optional[str] = None) -> bool:
        """Apply a theme to a specific widget

        Args:
            widget: Widget to apply theme to
            theme_name: Theme name (uses current theme if None)

        Returns:
            True if theme was applied, False otherwise
        """
        if widget is None:
            logger.error("Cannot apply theme: Widget is None")
            return False

        # Use current theme if not specified
        if theme_name is None:
            theme_name = self._current_theme

        # Check if theme exists
        if theme_name not in self.get_theme_list():
            logger.error(f"Theme '{theme_name}' not found")
            return False

        # Load theme CSS
        css = self.load_theme(theme_name)
        if not css:
            logger.error(f"Failed to load theme: {theme_name}")
            return False

        # Set data-theme attribute
        widget.setProperty("data-theme", theme_name)

        # Apply stylesheet
        widget.setStyleSheet(css)

        logger.debug(f"Applied theme '{theme_name}' to widget: {widget.objectName()}")
        return True
