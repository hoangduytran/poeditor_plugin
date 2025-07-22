"""
Explorer Settings

Manages user preferences for the SimpleExplorer widget.
Handles settings persistence and provides defaults.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from lg import logger


class ExplorerSettings:
    """Manages explorer settings with persistence."""
    
    def __init__(self, settings_file: Optional[str] = None):
        """Initialize settings manager.
        
        Args:
            settings_file: Path to settings file. If None, uses default location.
        """
        if settings_file is None:
            settings_dir = Path.home() / ".pyside_poeditor_plugin"
            settings_dir.mkdir(exist_ok=True)
            settings_file = str(settings_dir / "explorer_settings.json")
        
        self.settings_file = settings_file
        self._settings = self._load_defaults()
        self.load()
        
        logger.debug(f"ExplorerSettings initialized with file: {self.settings_file}")
    
    def _load_defaults(self) -> Dict[str, Any]:
        """Load default settings."""
        return {
            "last_path": str(Path.home()),
            "window_geometry": {
                "width": 800,
                "height": 600,
                "x": 100,
                "y": 100
            },
            "filter_history": [],
            "show_hidden_files": False,
            "sort_directories_first": True,
            "font_size": 11,
            "theme": "default"
        }
    
    def load(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self._settings.update(loaded_settings)
                    logger.info(f"Settings loaded from {self.settings_file}")
            else:
                logger.info("No settings file found, using defaults")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Keep defaults on error
    
    def save(self):
        """Save current settings to file."""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
            logger.info(f"Settings saved to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            value = self._settings
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            value: Value to set
        """
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            target = self._settings
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            logger.debug(f"Setting updated: {key} = {value}")
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
    
    def add_to_filter_history(self, filter_pattern: str):
        """Add a filter pattern to history.
        
        Args:
            filter_pattern: Filter pattern to add
        """
        if not filter_pattern.strip():
            return
        
        history = self.get("filter_history", [])
        
        # Remove if already exists (to move to front)
        if filter_pattern in history:
            history.remove(filter_pattern)
        
        # Add to front
        history.insert(0, filter_pattern)
        
        # Limit history size
        max_history = 20
        if len(history) > max_history:
            history = history[:max_history]
        
        self.set("filter_history", history)
    
    def get_filter_history(self) -> list:
        """Get filter history list."""
        return self.get("filter_history", [])
    
    def clear_filter_history(self):
        """Clear filter history."""
        self.set("filter_history", [])
        logger.info("Filter history cleared")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._settings = self._load_defaults()
        logger.info("Settings reset to defaults")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all current settings.
        
        Returns:
            Copy of all settings
        """
        return self._settings.copy()
