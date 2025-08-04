"""
Theme Manager for POEditor Plugin
Handles theme loading and application.
"""

import os
from pathlib import Path
from lg import logger

class ThemeManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent

        # self.themes_path = self.base_path / "themes" / "assets" / "styles"
        self.themes_path = self.base_path / "themes" / "css"

        # Ensure themes directory exists
        self.themes_path.mkdir(parents=True, exist_ok=True)

        self.available_themes = {
            "light": "light_theme.css",
            "dark": "dark_theme.css"
        }

        # Check if theme files exist and log their status
        for theme, filename in self.available_themes.items():
            theme_file = self.themes_path / filename
            try:
                stat = os.stat(theme_file)
                logger.info(f"Theme file '{theme_file}' exists. Size: {stat.st_size} bytes. Last modified: {stat.st_mtime}")
            except FileNotFoundError:
                logger.info(f"Theme file '{theme_file}' does NOT exist.")

    def get_theme_stylesheet(self, theme_name):
        """Load and return the stylesheet for the specified theme"""
        theme_data = ""
        if theme_name not in self.available_themes:
            theme_name = "light"  # Default fallback

        theme_file = self.themes_path / self.available_themes[theme_name]

        if not theme_file.exists():
            logger.info(f"Warning: Theme file {theme_file} not found, content is empty")
            return theme_data

        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = f.read()
            logger.info(f"Loaded theme {theme_name} from {theme_file}")
            logger.debug(f"=== DEBUG: Loaded CSS content for theme '{theme_name}' ===\n{theme_data}\n=== END CSS content, length: {len(theme_data)} ===")
        except Exception as e:
            logger.info(f"Error loading theme {theme_name}: {e}")
        return theme_data

    def get_available_themes(self):
        """Return list of available theme names"""
        return list(self.available_themes.keys())

    def theme_exists(self, theme_name):
        """Check if a theme exists"""
        return theme_name in self.available_themes

