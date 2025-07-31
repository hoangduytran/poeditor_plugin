import os
from pathlib import Path

class ThemeManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.themes_path = self.base_path / "assets" / "styles"

        # Ensure themes directory exists
        self.themes_path.mkdir(parents=True, exist_ok=True)

        self.available_themes = {
            "light": "light_theme.css",
            "dark": "dark_theme.css"
        }

    def get_theme_stylesheet(self, theme_name):
        """Load and return the stylesheet for the specified theme"""
        if theme_name not in self.available_themes:
            theme_name = "light"  # Default fallback

        theme_file = self.themes_path / self.available_themes[theme_name]

        if not theme_file.exists():
            print(f"Warning: Theme file {theme_file} not found")
            return ""

        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading theme {theme_name}: {e}")
            return ""

    def get_available_themes(self):
        """Return list of available theme names"""
        return list(self.available_themes.keys())

    def theme_exists(self, theme_name):
        """Check if a theme exists"""
        return theme_name in self.available_themes

