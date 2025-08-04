"""
Settings Manager for POEditor Plugin
Handles application settings persistence and retrieval.
"""

import json
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.config_dir = Path.home() / ".poeditor_plugin"
        self.config_file = self.config_dir / "settings.json"

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        self.default_settings = {
            "api_token": "",
            "theme": "light",
            "window_geometry": None,
            "last_project": None,
        }
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()

    def get_theme(self):
        """Get current theme setting"""
        return self.get_setting("theme", "light")

    def set_theme(self, theme_name):
        """Set theme setting"""
        self.set_setting("theme", theme_name)
