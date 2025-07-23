"""
Theme Manager service for the POEditor application.

Centralized theme management including theme switching, CSS generation,
and theme persistence.
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional, List, Any
from PySide6.QtCore import QObject, Signal, QSettings, QFile, QTextStream, QIODevice
from PySide6.QtWidgets import QApplication, QWidget

from lg import logger

@dataclass
class Theme:
    """Simple theme data class."""
    name: str
    css_path: str
    dark_mode: bool = False
    accent_color: str = ""
    description: str = ""


class ThemeManager(QObject):
    """
    Centralized theme management service.
    
    Handles theme switching, CSS application, and theme persistence.
    Follows singleton pattern for global access.
    """
    
    # Signals
    theme_changed = Signal(object)  # Emitted when theme changes
    theme_applied = Signal(str)     # Emitted when CSS is applied
    
    _instance: Optional['ThemeManager'] = None
    
    def __new__(cls) -> 'ThemeManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Singleton pattern: prevent reinitialization
        if getattr(self, '_initialized', False):
            return
        
        super().__init__()
        self._initialized = True
        
        # Available themes
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._settings = QSettings('POEditor', 'ThemeManager')
        
        # Initialize default themes
        self._register_default_themes()
        
        # Load saved theme or default to Light
        saved_theme = str(self._settings.value('current_theme', 'Light'))
        if saved_theme in self._themes:
            self._current_theme = self._themes[saved_theme]
            # Try to apply theme, but don't fail initialization if no QApplication
            self._apply_theme()
        else:
            # Fallback to Light theme
            self._current_theme = self._themes.get('Light')
            if self._current_theme:
                self._apply_theme()
        
        logger.info("ThemeManager initialized")
    
    def _register_default_themes(self) -> None:
        """Register the default built-in themes."""
        try:
            # Register the default themes using the CSS files from resource system
            # First try to use resource files, fall back to local files if needed
            self._themes['Light'] = Theme(
                name="Light", 
                css_path=":/css/light_theme.css",
                dark_mode=False,
                accent_color="#0078d4",
                description="Light theme inspired by VS Code Light"
            )
            
            self._themes['Dark'] = Theme(
                name="Dark", 
                css_path=":/css/dark_theme.css",
                dark_mode=True,
                accent_color="#007acc",
                description="Dark theme inspired by VS Code Dark+"
            )
            
            self._themes['Colorful'] = Theme(
                name="Colorful", 
                css_path=":/css/colorful_theme.css",
                dark_mode=False,
                accent_color="#268bd2",
                description="Colorful theme inspired by Solarized Light"
            )
            
            logger.info(f"Registered {len(self._themes)} default themes")
            
        except Exception as e:
            logger.error(f"Failed to register default themes: {e}")
            raise
    
    def register_theme(self, theme: Theme) -> bool:
        """
        Register a custom theme.
        
        Args:
            theme: Theme instance to register
            
        Returns:
            True if theme was registered successfully
        """
        try:
            if theme.name in self._themes:
                logger.warning(f"Theme '{theme.name}' already exists, overwriting")
            
            self._themes[theme.name] = theme
            logger.info(f"Registered theme: {theme.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register theme '{theme.name}': {e}")
            return False
    
    def unregister_theme(self, theme_name: str) -> bool:
        """
        Unregister a theme.
        
        Args:
            theme_name: Name of the theme to unregister
            
        Returns:
            True if theme was unregistered successfully
        """
        try:
            if theme_name not in self._themes:
                logger.warning(f"Theme '{theme_name}' not found")
                return False
            
            # Don't allow unregistering the current theme
            if self._current_theme and self._current_theme.name == theme_name:
                logger.error(f"Cannot unregister current theme '{theme_name}'")
                return False
            
            # Don't allow unregistering default themes
            if theme_name in ['Light', 'Dark', 'Colorful']:
                logger.error(f"Cannot unregister default theme '{theme_name}'")
                return False
            
            del self._themes[theme_name]
            logger.info(f"Unregistered theme: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister theme '{theme_name}': {e}")
            return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self._themes.keys())
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """
        Get a theme by name.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Theme instance or None if not found
        """
        return self._themes.get(theme_name)
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get the currently active theme."""
        return self._current_theme
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set the active theme.
        
        Args:
            theme_name: Name of the theme to activate
            
        Returns:
            True if theme was set successfully
        """
        try:
            if theme_name not in self._themes:
                logger.error(f"Theme '{theme_name}' not found")
                return False
            
            old_theme = self._current_theme
            self._current_theme = self._themes[theme_name]
            
            # Apply the theme
            if self._apply_theme():
                # Save the theme selection
                self._settings.setValue('current_theme', theme_name)
                
                # Emit signals
                self.theme_changed.emit(self._current_theme)
                
                logger.info(f"Switched to theme: {theme_name}")
                return True
            else:
                # Revert on failure
                self._current_theme = old_theme
                return False
                
        except Exception as e:
            logger.error(f"Failed to set theme '{theme_name}': {e}")
            return False
    
    def _apply_theme(self) -> bool:
        """
        Apply the current theme to the application.
        
        Returns:
            True if theme was applied successfully
        """
        try:
            if not self._current_theme:
                logger.error("No current theme set")
                return False
            
            # Load CSS from file
            css_file = QFile(self._current_theme.css_path)
            if not css_file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                logger.error(f"Failed to open CSS file: {self._current_theme.css_path}")
                return False
                
            # Read CSS content
            stream = QTextStream(css_file)
            css = stream.readAll()
            css_file.close()
            
            # Apply CSS to application
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                app.setStyleSheet(css)
                self.theme_applied.emit(self._current_theme.name)
                logger.info(f"Applied theme CSS: {self._current_theme.name}")
                return True
            else:
                logger.error("No QApplication instance found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")
            return False
    
    def refresh_theme(self) -> bool:
        """
        Refresh the current theme (reapply CSS).
        
        Returns:
            True if theme was refreshed successfully
        """
        try:
            if not self._current_theme:
                logger.warning("No current theme to refresh")
                return False
            
            # Reapply the theme
            return self._apply_theme()
            
        except Exception as e:
            logger.error(f"Failed to refresh theme: {e}")
            return False
            
    def toggle_theme(self) -> str:
        """
        Toggle between available themes in a cycle.
        
        Returns:
            The name of the newly activated theme
        """
        current_theme_name = self._current_theme.name if self._current_theme else "Unknown"
        logger.info(f"Toggle theme requested. Current theme: {current_theme_name}")
        
        available_themes = list(self._themes.keys())
        logger.debug(f"Available themes: {available_themes}")
        
        if not available_themes:
            logger.warning("No themes available to toggle")
            return current_theme_name
            
        # Find the index of the current theme
        try:
            current_name = self._current_theme.name if self._current_theme else ""
            current_index = available_themes.index(current_name)
            logger.debug(f"Current theme index: {current_index}")
        except (ValueError, AttributeError) as e:
            # Current theme not found in list, default to first theme
            current_index = -1
            logger.warning(f"Current theme not found in available themes: {e}")
            
        # Move to the next theme in the cycle
        next_index = (current_index + 1) % len(available_themes)
        next_theme_name = available_themes[next_index]
        logger.info(f"Switching to next theme: '{next_theme_name}' at index {next_index}")
        
        # Apply the next theme
        if self.set_theme(next_theme_name):
            logger.info(f"Successfully toggled theme to '{next_theme_name}'")
            return next_theme_name
        else:
            logger.error(f"Failed to toggle to theme '{next_theme_name}'")
            return self._current_theme.name if self._current_theme else ""
    
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """
        Export a theme to a JSON file.
        
        Args:
            theme_name: Name of the theme to export
            file_path: Path to save the theme file
            
        Returns:
            True if theme was exported successfully
        """
        try:
            if theme_name not in self._themes:
                logger.error(f"Theme '{theme_name}' not found")
                return False
            
            theme = self._themes[theme_name]
            theme_data = {
                "name": theme.name,
                "dark_mode": theme.dark_mode,
                "accent_color": theme.accent_color,
                "description": theme.description,
                "css_path": theme.css_path
            }
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            logger.info(f"Exported theme '{theme_name}' to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export theme '{theme_name}': {e}")
            return False
    
    def import_theme(self, file_path: str) -> bool:
        """
        Import a theme from a JSON file.
        
        Args:
            file_path: Path to the theme file
            
        Returns:
            True if theme was imported successfully
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Theme file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Create a Theme object from the data
            theme = Theme(
                name=theme_data.get("name", "Custom Theme"),
                css_path=theme_data.get("css_path", ""),
                dark_mode=theme_data.get("dark_mode", False),
                accent_color=theme_data.get("accent_color", "#007acc"),
                description=theme_data.get("description", "Custom imported theme")
            )
            
            return self.register_theme(theme)
            
        except Exception as e:
            logger.error(f"Failed to import theme from {file_path}: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """
        Reset to the default Light theme.
        
        Returns:
            True if reset was successful
        """
        try:
            return self.set_theme('Light')
        except Exception as e:
            logger.error(f"Failed to reset to default theme: {e}")
            return False
            
    def apply_activity_bar_theme(self, activity_bar: QWidget) -> None:
        """
        Apply the activity bar theme to the activity bar widget.
        
        Args:
            activity_bar: The activity bar widget to style
        """
        try:
            # Load the activity bar CSS file
            css_file = QFile(":/css/themes/css/activity_bar.css")
            if not css_file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                logger.error(f"Failed to open activity bar CSS file")
                return
                
            # Read CSS content
            stream = QTextStream(css_file)
            css = stream.readAll()
            css_file.close()
            
            # Apply CSS to activity bar
            activity_bar.setStyleSheet(css)
            logger.info(f"Applied activity bar theme to widget: {activity_bar.objectName()}")
            
        except Exception as e:
            logger.error(f"Failed to apply activity bar theme: {e}")
    
    def get_style_for_component(self, component_name: str) -> str:
        """
        Get CSS style for a component (simplified implementation).
        
        Args:
            component_name: Name of the component
            
        Returns:
            Empty string (basic implementation)
        """
        # This is a simplified implementation
        # The comprehensive theme manager has a full implementation
        logger.debug(f"Style requested for component: {component_name}")
        return ""
    
    def get_theme_info(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a theme.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Dictionary with theme information or None if not found
        """
        if theme_name not in self._themes:
            return None
        
        theme = self._themes[theme_name]
        return {
            'name': theme.name,
            'is_current': self._current_theme and self._current_theme.name == theme_name,
            'dark_mode': theme.dark_mode,
            'accent_color': theme.accent_color,
            'description': theme.description
        }


# Global theme manager instance
theme_manager = ThemeManager()
