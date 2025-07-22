"""
Theme manager for the PySide POEditor plugin.

This module provides centralized theme management with integrated typography support.
Supports multiple themes and user customization with JSON import/export capabilities.

Following rules.md: No hasattr/getattr usage, proper error handling with lg.py logger.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from lg import logger
from PySide6.QtCore import QObject, Signal
from themes.typography import get_typography_manager, FontRole


class ThemeValidationError(Exception):
    """Exception raised for theme validation errors."""
    pass


class ThemeManager(QObject):
    """Manages application themes and their typography."""

    theme_changed = Signal(str)  # Emits theme name
    themes_updated = Signal()    # Emits when theme list changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "vs_code_dark"  # Default to VS Code Dark+ theme
        self.themes = {}
        self.typography_manager = get_typography_manager()
        self.user_themes_dir = None

        # Load built-in themes
        self._load_builtin_themes()

    def set_user_themes_directory(self, directory_path: str):
        """Set the directory where user themes are stored."""
        try:
            path = Path(directory_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

            self.user_themes_dir = str(path)
            self._load_user_themes()
            logger.info(f"Set user themes directory: {directory_path}")
        except Exception as e:
            logger.error(f"Failed to set user themes directory: {e}")

    def _load_builtin_themes(self):
        """Load built-in theme configurations."""
        # VS Code Light theme - authentic colors
        self.themes["vs_code_light"] = {
            "name": "VS Code Light",
            "builtin": True,
            "version": "1.0",
            "typography": {
                "base_font_family": "Segoe UI, Ubuntu, Droid Sans, sans-serif",
                "base_font_size": 13,
                "scale_factor": 1.0
            },
            "colors": {
                # Primary backgrounds
                "background": "#ffffff",
                "secondary_background": "#f3f3f3",
                "surface": "#ececec",
                
                # Text colors
                "text_primary": "#333333",
                "text_secondary": "#999999",
                "text_muted": "#666666",
                "text_inverse": "#ffffff",
                
                # Legacy compatibility
                "foreground": "#333333",
                "border": "#e5e5e5",
                
                # Interactive colors
                "accent": "#0078d4",
                "accent_hover": "#106ebe",
                "accent_pressed": "#005a9e",
                "hover": "#e8e8e8",
                "active": "#d6d6d6",
                "focus": "#0078d4",
                "disabled": "#f0f0f0",
                
                # Component-specific colors
                "activity_bar_background": "#2c2c2c",
                "activity_bar_hover": "#404040",
                "activity_bar_active": "#0078d4",
                
                "explorer_background": "#f3f3f3",
                "explorer_hover": "#e8e8e8",
                "explorer_selection": "#0078d4",
                "explorer_border": "#e5e5e5",
                
                "tab_active_background": "#ffffff",
                "tab_inactive_background": "#ececec",
                "tab_active_text": "#333333",
                "tab_inactive_text": "#999999",
                "tab_border": "#e5e5e5",
                
                "input_background": "#ffffff",
                "input_border": "#cccccc",
                "input_focus": "#0078d4",
                "input_placeholder": "#999999",
                
                "status_bar_background": "#007acc",
                "status_bar_text": "#ffffff",
                
                "button_primary": "#0078d4",
                "button_hover": "#106ebe",
                "button_pressed": "#005a9e",
                
                # Scrollbar colors (VS Code Light theme)
                "scrollbar_thumb": "#c1c1c1",
                "scrollbar_thumb_hover": "#a6a6a6", 
                "scrollbar_thumb_active": "#919191",
                
                # Missing definitions for better compatibility
                "inactive_selection": "#e4e6f1",
                "button_text": "#ffffff"
            },
            "styles": {
                "panel_title": {
                    "background": "$surface",
                    "color": "$text_primary",
                    "font_role": "title",
                    "text_transform": "uppercase",
                    "letter_spacing": "0.5px",
                    "border_bottom": "1px solid $border"
                },
                "button": {
                    "background": "$button_primary",
                    "border": "1px solid $button_primary",
                    "color": "$text_inverse",
                    "font_role": "button",
                    "border_radius": "3px"
                },
                "search_input": {
                    "background": "$input_background",
                    "border": "1px solid $input_border",
                    "color": "$text_primary",
                    "font_role": "body",
                    "border_radius": "3px",
                    "padding": "4px 6px"
                }
            }
        }

        # VS Code Dark+ theme - authentic colors from official VS Code theme
        self.themes["vs_code_dark"] = {
            "name": "VS Code Dark+",
            "builtin": True,
            "version": "1.0",
            "typography": {
                "base_font_family": "Segoe UI, Ubuntu, Droid Sans, sans-serif",
                "base_font_size": 13,
                "scale_factor": 1.0
            },
            "colors": {
                # Primary backgrounds (authentic VS Code Dark+ colors)
                "background": "#1e1e1e",                # editor.background
                "secondary_background": "#252526",      # sideBar.background
                "surface": "#2d2d30",                   # tab.inactiveBackground
                "surface_secondary": "#252526",         # alternate background
                
                # Text colors (authentic VS Code Dark+ colors)
                "text_primary": "#cccccc",              # foreground
                "text_secondary": "#969696",            # tab.inactiveForeground
                "text_muted": "#6a6a6a",               # darker secondary
                "text_inverse": "#ffffff",              # high contrast text
                
                # Legacy compatibility
                "foreground": "#cccccc",
                "border": "#464647",                    # panel.border
                
                # Interactive colors (authentic VS Code Dark+ colors)
                "accent": "#007acc",                    # focusBorder, button.background
                "accent_hover": "#1177bb",              
                "accent_pressed": "#0e639c",            
                "hover": "#2a2d2e",                     # list.hoverBackground
                "active": "#094771",                    # list.activeSelectionBackground
                "focus": "#007acc",                     
                "disabled": "#3c3c3c",                  
                "selection": "#094771",                 # list.activeSelectionBackground
                "selection_text": "#ffffff",            
                
                # Component-specific colors (authentic VS Code Dark+ colors)
                "activity_bar_background": "#333333",   # activityBar.background
                "activity_bar_hover": "#2a2d2e",       
                "activity_bar_active": "#007acc",      
                
                "explorer_background": "#252526",       # sideBar.background
                "explorer_hover": "#2a2d2e",           # list.hoverBackground
                "explorer_selection": "#094771",        # list.activeSelectionBackground
                "explorer_border": "#464647",           # sideBar.border
                
                "tab_active_background": "#1e1e1e",     # tab.activeBackground
                "tab_inactive_background": "#2d2d30",   # tab.inactiveBackground
                "tab_active_text": "#ffffff",           # tab.activeForeground
                "tab_inactive_text": "#969696",         # tab.inactiveForeground
                "tab_border": "#464647",                # tab.border
                
                "input_background": "#3c3c3c",          # input.background
                "input_border": "#464647",              # input.border (more authentic)
                "input_focus": "#007acc",               # inputOption.activeBorder
                "input_placeholder": "#cccccc80",       # input.placeholderForeground
                
                "status_bar_background": "#007acc",     # statusBar.background
                "status_bar_text": "#ffffff",           # statusBar.foreground
                
                "button_primary": "#0e639c",            # button.background
                "button_text": "#ffffff",               # button.foreground
                "button_hover": "#1177bb",              # button.hoverBackground
                "button_pressed": "#0a5a94",            # button.background darker
                
                # Scrollbar colors (authentic VS Code Dark+ colors)
                "scrollbar_thumb": "#424242",           # scrollbarSlider.background
                "scrollbar_thumb_hover": "#4f4f4f",     # scrollbarSlider.hoverBackground
                "scrollbar_thumb_active": "#5a5a5a",    # scrollbarSlider.activeBackground
                
                # Missing definitions for better compatibility
                "inactive_selection": "#3a3d41"         # list.inactiveSelectionBackground
            },
            "styles": {
                "panel_title": {
                    "background": "$surface",
                    "color": "$text_primary",
                    "font_role": "title",
                    "text_transform": "uppercase",
                    "letter_spacing": "0.5px",
                    "border_bottom": "1px solid $border"
                },
                "button": {
                    "background": "$button_primary",
                    "border": "1px solid $button_primary",
                    "color": "$text_inverse",
                    "font_role": "button",
                    "border_radius": "3px"
                },
                "search_input": {
                    "background": "$input_background",
                    "border": "1px solid $input_border",
                    "color": "$text_primary",
                    "font_role": "body",
                    "border_radius": "3px",
                    "padding": "4px 6px"
                }
            }
        }

        # Colorful theme - vibrant alternative
        self.themes["colorful"] = {
            "name": "Colorful",
            "builtin": True,
            "version": "1.0",
            "typography": {
                "base_font_family": "Segoe UI, Ubuntu, Droid Sans, sans-serif",
                "base_font_size": 13,
                "scale_factor": 1.0
            },
            "colors": {
                # Primary backgrounds  
                "background": "#fdf6e3",
                "secondary_background": "#f7f1e0",
                "surface": "#f0ead6",
                
                # Text colors
                "text_primary": "#586e75",
                "text_secondary": "#93a1a1",
                "text_muted": "#839496",
                "text_inverse": "#fdf6e3",
                
                # Legacy compatibility
                "foreground": "#586e75",
                "border": "#e9d9b7",
                
                # Interactive colors
                "accent": "#268bd2",
                "accent_hover": "#2aa198",
                "accent_pressed": "#0087bd",
                "hover": "#f5efdc",
                "active": "#b58900",
                "focus": "#268bd2",
                "disabled": "#f7f3ea",
                
                # Component-specific colors
                "activity_bar_background": "#2c2c2c",
                "activity_bar_hover": "#404040",
                "activity_bar_active": "#268bd2",
                
                "explorer_background": "#f7f1e0",
                "explorer_hover": "#f5efdc",
                "explorer_selection": "#b58900",
                "explorer_border": "#e9d9b7",
                
                "tab_active_background": "#fdf6e3",
                "tab_inactive_background": "#f0ead6",
                "tab_active_text": "#073642",
                "tab_inactive_text": "#93a1a1",
                "tab_border": "#e9d9b7",
                
                "input_background": "#fdf6e3",
                "input_border": "#d3cbb7",
                "input_focus": "#268bd2",
                "input_placeholder": "#93a1a1",
                
                "status_bar_background": "#268bd2",
                "status_bar_text": "#fdf6e3",
                
                "button_primary": "#268bd2",
                "button_hover": "#2aa198",
                "button_pressed": "#0087bd",
                
                # Scrollbar colors (Colorful theme)
                "scrollbar_thumb": "#93a1a1",
                "scrollbar_thumb_hover": "#657b83",
                "scrollbar_thumb_active": "#586e75",
                
                # Missing definitions for better compatibility  
                "inactive_selection": "#f0ead6",
                "button_text": "#fdf6e3"
            },
            "styles": {
                "panel_title": {
                    "background": "$surface",
                    "color": "$text_primary",
                    "font_role": "title",
                    "text_transform": "uppercase",
                    "letter_spacing": "0.5px",
                    "border_bottom": "1px solid $border"
                },
                "button": {
                    "background": "$button_primary",
                    "border": "1px solid $button_primary", 
                    "color": "$text_inverse",
                    "font_role": "button",
                    "border_radius": "3px"
                },
                "search_input": {
                    "background": "$input_background",
                    "border": "1px solid $input_border",
                    "color": "$text_primary",
                    "font_role": "body", 
                    "border_radius": "3px",
                    "padding": "4px 6px"
                }
            }
        }

    def _load_user_themes(self):
        """Load custom user themes from the themes directory."""
        if not self.user_themes_dir:
            return

        try:
            theme_files = list(Path(self.user_themes_dir).glob("*.json"))
            for theme_file in theme_files:
                try:
                    self.import_theme_from_file(str(theme_file))
                except Exception as e:
                    logger.error(f"Failed to load user theme {theme_file}: {e}")

            logger.info(f"Loaded {len(theme_files)} user themes from {self.user_themes_dir}")

        except Exception as e:
            logger.error(f"Failed to load user themes: {e}")

    def get_style_for_component(self, component_name: str) -> str:
        """
        Get CSS style string for a specific component.

        Args:
            component_name: Name of the component (e.g., 'panel_title', 'search_input')

        Returns:
            str: CSS style string for the component
        """
        try:
            current_theme = self.themes.get(self.current_theme, {})
            styles = current_theme.get("styles", {})
            colors = current_theme.get("colors", {})

            component_style = styles.get(component_name, {})

            if not component_style:
                # Return basic fallback style
                return "background-color: #ffffff; color: #333333;"

            # Build CSS string by resolving color variables
            css_parts = []
            for property_name, value in component_style.items():
                if property_name == "font_role":
                    # Skip font_role as it's handled separately
                    continue

                # Resolve color variables (e.g., $background -> actual color)
                if isinstance(value, str) and value.startswith("$"):
                    color_key = value[1:]  # Remove $ prefix
                    resolved_value = colors.get(color_key, value)
                    css_parts.append(f"{property_name.replace('_', '-')}: {resolved_value}")
                else:
                    css_parts.append(f"{property_name.replace('_', '-')}: {value}")

            return "; ".join(css_parts) + ";" if css_parts else ""

        except Exception as e:
            logger.error(f"Failed to get style for component {component_name}: {e}")
            return "background-color: #ffffff; color: #333333;"

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        try:
            return [theme_data.get("name", theme_id) for theme_id, theme_data in self.themes.items()]
        except Exception as e:
            logger.error(f"Failed to get available themes: {e}")
            return ["Light", "Dark"]

    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        """Get the current theme data."""
        try:
            return self.themes.get(self.current_theme)
        except Exception as e:
            logger.error(f"Failed to get current theme: {e}")
            return None

    def set_theme(self, theme_name: str) -> bool:
        """
        Set the current theme by name.

        Args:
            theme_name: Display name of the theme

        Returns:
            bool: True if theme was set successfully
        """
        try:
            # Find theme by name
            theme_id = None
            for tid, theme_data in self.themes.items():
                if theme_data.get("name", tid) == theme_name:
                    theme_id = tid
                    break

            if theme_id is None:
                logger.warning(f"Theme not found: {theme_name}")
                return False

            self.current_theme = theme_id
            self._apply_theme()
            self.theme_changed.emit(theme_name)
            logger.info(f"Theme changed to: {theme_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to set theme {theme_name}: {e}")
            return False

    def customize_font_settings(self, font_family: str = None, font_size: int = None, scale_factor: float = None):
        """
        Customize font settings for the current theme.

        Args:
            font_family: New base font family
            font_size: New base font size
            scale_factor: New scale factor
        """
        try:
            current_theme = self.themes.get(self.current_theme, {})
            typography_config = current_theme.setdefault("typography", {})

            if font_family is not None:
                typography_config["base_font_family"] = font_family
                self.typography_manager.set_base_font_family(font_family)

            if font_size is not None:
                typography_config["base_font_size"] = font_size
                self.typography_manager.set_base_font_size(font_size)

            if scale_factor is not None:
                typography_config["scale_factor"] = scale_factor
                self.typography_manager.set_scale_factor(scale_factor)

            logger.info(f"Customized font settings: family={font_family}, size={font_size}, scale={scale_factor}")

        except Exception as e:
            logger.error(f"Failed to customize font settings: {e}")

    def validate_theme(self, theme_data: Dict[str, Any]) -> bool:
        """Validate theme data structure.

        Returns:
            bool: True if valid

        Raises:
            ThemeValidationError: If theme is invalid with specific error message
        """
        # Check required top-level keys
        required_keys = ["name", "version", "colors", "styles"]
        for key in required_keys:
            if key not in theme_data:
                raise ThemeValidationError(f"Missing required key: {key}")

        # Check colors
        colors = theme_data.get("colors", {})
        if not isinstance(colors, dict):
            raise ThemeValidationError("Colors must be a dictionary")

        required_colors = ["background", "foreground"]
        for color in required_colors:
            if color not in colors:
                raise ThemeValidationError(f"Missing required color: {color}")

        # Check styles
        styles = theme_data.get("styles", {})
        if not isinstance(styles, dict):
            raise ThemeValidationError("Styles must be a dictionary")

        # Validate color format
        for name, value in colors.items():
            if isinstance(value, str) and value.startswith("#"):
                # Check hex color format
                if not (len(value) == 7 or len(value) == 9):  # #RRGGBB or #RRGGBBAA
                    raise ThemeValidationError(f"Invalid color format for {name}: {value}")

        return True

    def import_theme_from_file(self, file_path: str) -> str:
        """Import a theme from a JSON file.

        Returns:
            str: Theme ID of the imported theme

        Raises:
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If JSON is invalid
            ThemeValidationError: If theme is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)

            # Validate theme
            self.validate_theme(theme_data)

            # Generate theme ID from name
            name = theme_data["name"]
            theme_id = name.lower().replace(" ", "_")

            # Add a suffix if ID already exists
            original_id = theme_id
            counter = 1
            while theme_id in self.themes:
                theme_id = f"{original_id}_{counter}"
                counter += 1

            # Set theme as non-builtin
            theme_data["builtin"] = False

            # Store theme
            self.themes[theme_id] = theme_data

            logger.info(f"Imported theme '{name}' with ID '{theme_id}' from {file_path}")
            self.themes_updated.emit()

            return theme_id

        except FileNotFoundError:
            logger.error(f"Theme file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in theme file {file_path}: {e}")
            raise
        except ThemeValidationError as e:
            logger.error(f"Theme validation failed for {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to import theme from {file_path}: {e}")
            raise

    def export_theme_to_file(self, theme_id: str, file_path: str):
        """Export a theme to a JSON file."""
        try:
            if theme_id not in self.themes:
                logger.warning(f"Theme not found: {theme_id}")
                return

            theme_data = self.themes[theme_id].copy()

            # Remove implementation-specific fields
            theme_data.pop("builtin", None)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)

            logger.info(f"Exported theme '{theme_data['name']}' to {file_path}")

        except Exception as e:
            logger.error(f"Failed to export theme to {file_path}: {e}")
            raise

    def create_new_theme(self, name: str, based_on: str = "light") -> str:
        """Create a new theme based on an existing one.

        Args:
            name: Name of the new theme
            based_on: Theme ID to base the new theme on

        Returns:
            str: Theme ID of the new theme
        """
        try:
            if based_on not in self.themes:
                logger.warning(f"Base theme not found: {based_on}")
                based_on = "light"  # Default to light theme

            # Create a deep copy of the base theme
            import copy
            theme_data = copy.deepcopy(self.themes[based_on])

            # Update theme properties
            theme_data["name"] = name
            theme_data["version"] = "1.0"
            theme_data["builtin"] = False

            # Generate theme ID
            theme_id = name.lower().replace(" ", "_")

            # Add a suffix if ID already exists
            original_id = theme_id
            counter = 1
            while theme_id in self.themes:
                theme_id = f"{original_id}_{counter}"
                counter += 1

            # Store theme
            self.themes[theme_id] = theme_data

            logger.info(f"Created new theme '{name}' with ID '{theme_id}' based on '{based_on}'")
            self.themes_updated.emit()

            return theme_id

        except Exception as e:
            logger.error(f"Failed to create new theme: {e}")
            raise

    def delete_theme(self, theme_id: str) -> bool:
        """Delete a theme.

        Args:
            theme_id: ID of the theme to delete

        Returns:
            bool: True if theme was deleted, False otherwise
        """
        try:
            if theme_id not in self.themes:
                logger.warning(f"Theme not found: {theme_id}")
                return False

            # Prevent deletion of built-in themes
            if self.themes[theme_id].get("builtin", False):
                logger.warning(f"Cannot delete built-in theme: {theme_id}")
                return False

            # If deleting current theme, switch to default
            if theme_id == self.current_theme:
                self.set_theme("light")

            # Delete theme
            theme_name = self.themes[theme_id]["name"]
            del self.themes[theme_id]

            logger.info(f"Deleted theme '{theme_name}' with ID '{theme_id}'")
            self.themes_updated.emit()

            return True

        except Exception as e:
            logger.error(f"Failed to delete theme: {e}")
            return False

    def update_theme_component(self, theme_id: str, component: str, properties: Dict[str, Any]) -> bool:
        """Update a component's properties in a theme.

        Args:
            theme_id: ID of the theme to update
            component: Component name to update
            properties: Properties to update

        Returns:
            bool: True if theme was updated, False otherwise
        """
        try:
            if theme_id not in self.themes:
                logger.warning(f"Theme not found: {theme_id}")
                return False

            theme_data = self.themes[theme_id]
            styles = theme_data.setdefault("styles", {})

            # Get or create component style
            component_style = styles.setdefault(component, {})

            # Update properties
            component_style.update(properties)

            logger.info(f"Updated component '{component}' in theme '{theme_data['name']}'")

            # Apply changes if this is the current theme
            if theme_id == self.current_theme:
                self.theme_changed.emit(theme_id)

            return True

        except Exception as e:
            logger.error(f"Failed to update theme component: {e}")
            return False

    def update_theme_color(self, theme_id: str, color_name: str, color_value: str) -> bool:
        """Update a color in a theme.

        Args:
            theme_id: ID of the theme to update
            color_name: Name of the color to update
            color_value: New color value (hex format)

        Returns:
            bool: True if theme was updated, False otherwise
        """
        try:
            if theme_id not in self.themes:
                logger.warning(f"Theme not found: {theme_id}")
                return False

            theme_data = self.themes[theme_id]
            colors = theme_data.setdefault("colors", {})

            # Update color
            colors[color_name] = color_value

            logger.info(f"Updated color '{color_name}' in theme '{theme_data['name']}'")

            # Apply changes if this is the current theme
            if theme_id == self.current_theme:
                self.theme_changed.emit(theme_id)

            return True

        except Exception as e:
            logger.error(f"Failed to update theme color: {e}")
            return False

    def get_theme_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for theme files.

        Returns:
            dict: The JSON schema for theme files
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "POEditor Theme",
            "type": "object",
            "required": ["name", "version", "colors", "styles"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Display name of the theme"
                },
                "version": {
                    "type": "string",
                    "description": "Theme version"
                },
                "typography": {
                    "type": "object",
                    "description": "Typography settings",
                    "properties": {
                        "base_font_family": {"type": "string"},
                        "base_font_size": {"type": "integer"},
                        "scale_factor": {"type": "number"}
                    }
                },
                "colors": {
                    "type": "object",
                    "description": "Theme colors",
                    "required": ["background", "foreground"],
                    "properties": {
                        "background": {"type": "string", "format": "color"},
                        "foreground": {"type": "string", "format": "color"}
                    },
                    "additionalProperties": {"type": "string", "format": "color"}
                },
                "styles": {
                    "type": "object",
                    "description": "Component styles",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "font_role": {"type": "string"}
                        },
                        "additionalProperties": {"type": "string"}
                    }
                }
            }
        }

    def save_to_settings(self, settings_service):
        """Save theme settings to persistent storage."""
        try:
            settings_service.set("theme.current", self.current_theme)
            logger.debug("Saved theme settings")

            # Save user themes if directory is set
            if self.user_themes_dir:
                for theme_id, theme_data in self.themes.items():
                    if not theme_data.get("builtin", False):
                        file_path = os.path.join(self.user_themes_dir, f"{theme_id}.json")
                        self.export_theme_to_file(theme_id, file_path)

        except Exception as e:
            logger.error(f"Failed to save theme settings: {e}")

    def load_from_settings(self, settings_service):
        """Load theme settings from persistent storage."""
        try:
            theme_id = settings_service.get("theme.current", "light")

            if theme_id in self.themes:
                self.set_theme(theme_id)
            else:
                logger.warning(f"Theme '{theme_id}' not found, using default")
                self.set_theme("light")

            logger.info(f"Loaded theme '{theme_id}' from settings")

        except Exception as e:
            logger.error(f"Failed to load theme settings: {e}")

    def get_theme_color(self, color_key: str, fallback: str = "#ffffff") -> str:
        """
        Get a specific color from the current theme.
        
        Args:
            color_key: The color key to look up
            fallback: Fallback color if key not found
            
        Returns:
            str: The color value
        """
        try:
            current_theme = self.themes.get(self.current_theme, {})
            colors = current_theme.get("colors", {})
            return colors.get(color_key, fallback)
        except Exception as e:
            logger.error(f"Failed to get theme color {color_key}: {e}")
            return fallback

    def _apply_theme(self):
        """Apply the current theme to the application with comprehensive CSS."""
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if not app:
                logger.warning("No QApplication instance found")
                return

            current_theme = self.themes.get(self.current_theme, {})
            colors = current_theme.get("colors", {})

            # Apply typography settings
            typography_config = current_theme.get("typography", {})
            if typography_config:
                font_family = typography_config.get("base_font_family")
                font_size = typography_config.get("base_font_size")
                scale_factor = typography_config.get("scale_factor")

                if font_family:
                    self.typography_manager.set_base_font_family(font_family)
                if font_size:
                    self.typography_manager.set_base_font_size(font_size)
                if scale_factor:
                    self.typography_manager.set_scale_factor(scale_factor)

            # Generate comprehensive stylesheet using theme colors
            comprehensive_stylesheet = self._generate_comprehensive_stylesheet(colors)
            app.setStyleSheet(comprehensive_stylesheet)

            logger.info(f"Applied theme CSS: {current_theme.get('name', self.current_theme)}")

        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")

    def _generate_comprehensive_stylesheet(self, colors: Dict[str, str]) -> str:
        """Generate comprehensive CSS stylesheet using theme colors."""
        # Helper function to get color with fallback
        def get_color(key: str, fallback: str = "#ffffff") -> str:
            return colors.get(key, fallback)

        return f"""
        /* === MAIN APPLICATION === */
        QMainWindow {{
            background-color: {get_color('background')};
            color: {get_color('text_primary')};
        }}
        
        QWidget {{
            background-color: {get_color('background')};
            color: {get_color('text_primary')};
        }}

        /* === PANELS === */
        QWidget#explorer_panel {{
            background-color: {get_color('secondary_background')};
            border-right: 1px solid {get_color('border')};
        }}
        
        QWidget#search_panel {{
            background-color: {get_color('secondary_background')};
            border-right: 1px solid {get_color('border')};
        }}
        
        QWidget#preferences_panel {{
            background-color: {get_color('secondary_background')};
            border-right: 1px solid {get_color('border')};
        }}
        
        QWidget#extensions_panel {{
            background-color: {get_color('secondary_background')};
            border-right: 1px solid {get_color('border')};
        }}
        
        QWidget#account_panel {{
            background-color: {get_color('secondary_background')};
            border-right: 1px solid {get_color('border')};
        }}

        /* === PANEL TITLES === */
        QLabel#panel_title {{
            background-color: transparent;
            color: {get_color('text_secondary')};
            font-weight: normal;
            font-size: 11px;
            padding: 8px 12px 4px 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* === BUTTONS === */
        QPushButton {{
            background-color: {get_color('input_background')};
            border: 1px solid {get_color('input_border')};
            color: {get_color('text_primary')};
            border-radius: 2px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: normal;
        }}
        
        QPushButton:hover {{
            background-color: {get_color('hover')};
            border-color: {get_color('input_focus')};
        }}
        
        QPushButton:pressed {{
            background-color: {get_color('active')};
            border-color: {get_color('input_focus')};
        }}
        
        QPushButton:disabled {{
            background-color: {get_color('disabled')};
            border-color: {get_color('disabled')};
            color: {get_color('text_muted')};
        }}

        /* === INPUT FIELDS === */
        QLineEdit {{
            background-color: {get_color('input_background')};
            border: 1px solid {get_color('input_border')};
            border-radius: 3px;
            padding: 6px 8px;
            color: {get_color('text_primary')};
            font-size: 13px;
        }}
        
        QLineEdit:focus {{
            border-color: {get_color('input_focus')};
            outline: none;
        }}
        
        QLineEdit:disabled {{
            background-color: {get_color('disabled')};
            color: {get_color('text_muted')};
        }}

        /* === COMBO BOXES === */
        QComboBox {{
            background-color: {get_color('input_background')};
            border: 1px solid {get_color('input_border')};
            border-radius: 3px;
            padding: 6px 8px;
            color: {get_color('text_primary')};
            font-size: 13px;
            min-width: 120px;
        }}
        
        QComboBox:focus {{
            border-color: {get_color('input_focus')};
        }}
        
        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {get_color('surface')};
            border: 1px solid {get_color('border')};
            selection-background-color: {get_color('hover')};
            color: {get_color('text_primary')};
        }}

        /* === LIST WIDGETS === */
        QListWidget {{
            background-color: {get_color('secondary_background')};
            border: none;
            outline: none;
            color: {get_color('text_primary')};
            alternate-background-color: transparent;
            font-size: 13px;
            padding: 0px;
        }}
        
        QListWidget::item {{
            padding: 2px 8px;
            border: none;
            background-color: transparent;
            height: 18px;
            color: {get_color('text_primary')};
        }}
        
        QListWidget::item:hover {{
            background-color: {get_color('hover')};
        }}
        
        QListWidget::item:selected {{
            background-color: {get_color('selection')};
            color: {get_color('text_primary')};
        }}

        /* === TREE WIDGETS === */
        QTreeView {{
            background-color: {get_color('secondary_background')};
            alternate-background-color: transparent;
            border: none;
            outline: none;
            color: {get_color('text_primary')};
            show-decoration-selected: 1;
            font-size: 13px;
        }}
        
        QTreeView::item {{
            padding: 2px;
            border: none;
            background-color: transparent;
            height: 18px;
        }}
        
        QTreeView::item:hover {{
            background-color: {get_color('hover')};
        }}
        
        QTreeView::item:selected {{
            background-color: {get_color('selection')};
            color: {get_color('text_primary')};
        }}
        
        QTreeView::item:selected:!active {{
            background-color: {get_color('inactive_selection')};
        }}
        
        QTreeView::branch {{
            background: transparent;
        }}
        
        QTreeView::branch:has-siblings:!adjoins-item {{
            border-image: none;
            border: none;
        }}
        
        QTreeView::branch:has-siblings:adjoins-item {{
            border-image: none;
            border: none;
        }}
        
        QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: none;
            border: none;
        }}
        
        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: none;
        }}
        
        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            image: none;
        }}

        /* === TAB WIDGETS === */
        QTabWidget::pane {{
            background-color: {get_color('background')};
            border: none;
        }}
        
        QTabBar::tab {{
            background-color: {get_color('tab_inactive_background')};
            color: {get_color('tab_inactive_text')};
            padding: 8px 16px;
            margin: 0;
            border: none;
            border-right: 1px solid {get_color('tab_border')};
            font-size: 13px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {get_color('tab_active_background')};
            color: {get_color('tab_active_text')};
            border-bottom: 2px solid {get_color('accent')};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {get_color('hover')};
            color: {get_color('text_primary')};
        }}

        /* === GROUP BOXES === */
        QGroupBox {{
            background-color: transparent;
            border: 1px solid {get_color('border')};
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            color: {get_color('text_primary')};
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
            color: {get_color('text_primary')};
        }}

        /* === SCROLL AREAS === */
        QScrollArea {{
            background-color: {get_color('background')};
            border: none;
        }}
        
        /* Vertical scrollbar - authentic VS Code style */
        QScrollBar:vertical {{
            background-color: {get_color('secondary_background')};
            width: 14px;
            border: none;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {get_color('scrollbar_thumb')};
            border: none;
            border-radius: 7px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {get_color('scrollbar_thumb_hover')};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            border: none;
            height: 0px;
            width: 0px;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        
        /* Horizontal scrollbar - authentic VS Code style */
        QScrollBar:horizontal {{
            background-color: {get_color('secondary_background')};
            height: 14px;
            border: none;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {get_color('scrollbar_thumb')};
            border: none;
            border-radius: 7px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {get_color('scrollbar_thumb_hover')};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
            border: none;
            height: 0px;
            width: 0px;
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}

        /* === LABELS === */
        QLabel {{
            color: {get_color('text_primary')};
            background-color: transparent;
        }}

        /* === CHECK BOXES === */
        QCheckBox {{
            color: {get_color('text_primary')};
            background-color: transparent;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            background-color: {get_color('input_background')};
            border: 1px solid {get_color('input_border')};
            border-radius: 2px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {get_color('accent')};
            border-color: {get_color('accent')};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {get_color('input_focus')};
        }}

        /* === SPIN BOXES === */
        QSpinBox {{
            background-color: {get_color('input_background')};
            border: 1px solid {get_color('input_border')};
            border-radius: 3px;
            padding: 6px 8px;
            color: {get_color('text_primary')};
            font-size: 13px;
        }}
        
        QSpinBox:focus {{
            border-color: {get_color('input_focus')};
        }}

        /* === SLIDERS === */
        QSlider::groove:horizontal {{
            background-color: {get_color('surface')};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {get_color('accent')};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {get_color('accent_hover')};
        }}

        /* === MENU BAR === */
        QMenuBar {{
            background-color: {get_color('surface')};
            color: {get_color('text_primary')};
            border-bottom: 1px solid {get_color('border')};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {get_color('hover')};
        }}

        /* === CONTEXT MENUS === */
        QMenu {{
            background-color: {get_color('surface')};
            border: 1px solid {get_color('border')};
            color: {get_color('text_primary')};
        }}
        
        QMenu::item {{
            padding: 6px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {get_color('hover')};
        }}

        /* === STATUS BAR === */
        QStatusBar {{
            background-color: {get_color('status_bar_background')};
            color: {get_color('status_bar_text')};
            border: none;
            font-size: 12px;
        }}
        
        QStatusBar::item {{
            border: none;
            background-color: transparent;
            padding: 2px 8px;
        }}

        /* === TOOL TIPS === */
        QToolTip {{
            background-color: {get_color('surface')};
            color: {get_color('text_primary')};
            border: 1px solid {get_color('border')};
            padding: 4px;
            border-radius: 2px;
        }}

        /* === SPECIFIC COMPONENTS === */
        
        /* Activity Bar (should remain dark) */
        QWidget#activity_bar {{
            background-color: {get_color('activity_bar_background')};
            border-right: 1px solid {get_color('border')};
        }}
        
        /* Breadcrumb navigation */
        QScrollArea#breadcrumb_scroll {{
            background-color: {get_color('surface')};
            border: 1px solid {get_color('border')};
            border-radius: 0;
        }}
        
        QPushButton[breadcrumb="true"] {{
            background-color: transparent;
            border: none;
            color: {get_color('accent')};
            padding: 4px 6px;
            font-size: 12px;
        }}
        
        QPushButton[breadcrumb="true"]:hover {{
            background-color: {get_color('hover')};
            border-radius: 2px;
        }}

        /* Extension items */
        QWidget#extension_item {{
            background-color: transparent;
            color: {get_color('text_primary')};
        }}
        
        /* === OBJECT-SPECIFIC ENHANCED SELECTORS === */
        
        /* Panel titles - authentic VS Code style */
        QLabel[objectName="panel_title"] {{
            font-weight: normal;
            color: {get_color('text_secondary')};
            padding: 8px 12px 4px 12px;
            margin-bottom: 4px;
            font-size: 11px;
            background-color: transparent;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* Search inputs - authentic VS Code style */
        QLineEdit[objectName="search_input"] {{
            background-color: {get_color('input_background')};
            border: 1px solid {get_color('input_border')};
            border-radius: 2px;
            padding: 4px 6px;
            color: {get_color('text_primary')};
            font-size: 13px;
        }}
        
        QLineEdit[objectName="search_input"]:focus {{
            border-color: {get_color('input_focus')};
            outline: none;
            background-color: {get_color('input_background')};
        }}
        
        QLineEdit[objectName="search_input"]:hover {{
            border-color: {get_color('input_border')};
        }}
        
        /* Primary buttons - more subtle VS Code style */
        QPushButton[objectName="primary_button"] {{
            background-color: {get_color('button_primary')};
            color: {get_color('button_text')};
            border: none;
            padding: 4px 8px;
            border-radius: 2px;
            font-weight: normal;
            font-size: 12px;
        }}
        
        QPushButton[objectName="primary_button"]:hover {{
            background-color: {get_color('button_hover')};
        }}
        
        QPushButton[objectName="primary_button"]:pressed {{
            background-color: {get_color('button_pressed')};
        }}
        
        QPushButton[objectName="primary_button"]:disabled {{
            background-color: {get_color('disabled')};
            color: {get_color('text_muted')};
        }}
        
        /* Secondary buttons - authentic VS Code style */
        QPushButton[objectName="secondary_button"] {{
            background-color: {get_color('input_background')};
            color: {get_color('text_primary')};
            border: 1px solid {get_color('input_border')};
            padding: 4px 8px;
            border-radius: 2px;
            font-size: 12px;
            font-weight: normal;
        }}
        
        QPushButton[objectName="secondary_button"]:hover {{
            background-color: {get_color('hover')};
            border-color: {get_color('input_focus')};
        }}
        
        QPushButton[objectName="secondary_button"]:pressed {{
            background-color: {get_color('active')};
        }}
        
        /* List widgets */
        QListWidget[objectName="list_widget"] {{
            background-color: {get_color('surface')};
            color: {get_color('text_primary')};
            border: 1px solid {get_color('border')};
            alternate-background-color: {get_color('surface_secondary')};
            outline: none;
        }}
        
        QListWidget[objectName="list_widget"]::item {{
            padding: 4px 8px;
            border-bottom: 1px solid {get_color('border')};
        }}
        
        QListWidget[objectName="list_widget"]::item:selected {{
            background-color: {get_color('selection')};
            color: {get_color('selection_text')};
        }}
        
        QListWidget[objectName="list_widget"]::item:hover {{
            background-color: {get_color('hover')};
        }}
        
        /* Tree views */
        QTreeView[objectName="tree_view"] {{
            background-color: {get_color('surface')};
            color: {get_color('text_primary')};
            border: 1px solid {get_color('border')};
            alternate-background-color: {get_color('surface_secondary')};
            outline: none;
        }}
        
        QTreeView[objectName="tree_view"]::item {{
            padding: 2px 4px;
        }}
        
        QTreeView[objectName="tree_view"]::item:selected {{
            background-color: {get_color('selection')};
            color: {get_color('selection_text')};
        }}
        
        QTreeView[objectName="tree_view"]::item:hover {{
            background-color: {get_color('hover')};
        }}
        
        QTreeView[objectName="tree_view"]::branch:selected {{
            background-color: {get_color('selection')};
        }}
        
        QTreeView[objectName="tree_view"]::branch:hover {{
            background-color: {get_color('hover')};
        }}
        
        /* Group boxes */
        QGroupBox[objectName="group_box"] {{
            font-weight: bold;
            color: {get_color('text_primary')};
            border: 1px solid {get_color('border')};
            border-radius: 3px;
            margin: 8px 0px;
            padding-top: 12px;
            background-color: transparent;
        }}
        
        QGroupBox[objectName="group_box"]::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {get_color('text_primary')};
        }}
        
        /* Tab widgets */
        QTabWidget[objectName="tab_widget"]::pane {{
            border: 1px solid {get_color('border')};
            background-color: {get_color('surface')};
            top: -1px;
        }}
        
        QTabWidget[objectName="tab_widget"] QTabBar::tab {{
            background-color: {get_color('surface_secondary')};
            color: {get_color('text_secondary')};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            border: 1px solid {get_color('border')};
            border-bottom: none;
        }}
        
        QTabWidget[objectName="tab_widget"] QTabBar::tab:selected {{
            background-color: {get_color('surface')};
            color: {get_color('text_primary')};
            border-bottom: 1px solid {get_color('surface')};
        }}
        
        QTabWidget[objectName="tab_widget"] QTabBar::tab:hover {{
            background-color: {get_color('hover')};
        }}
        
        /* Status labels */
        QLabel[objectName="status_label"] {{
            color: {get_color('text_secondary')};
            padding: 4px;
            font-size: 12px;
            background-color: transparent;
        }}
        
        /* Info labels */
        QLabel[objectName="info_label"] {{
            color: {get_color('text_secondary')};
            font-size: 13px;
            background-color: transparent;
        }}
        
        /* Description labels */
        QLabel[objectName="description_label"] {{
            color: {get_color('text_secondary')};
            font-size: 12px;
            background-color: transparent;
        }}
        
        /* Version labels */
        QLabel[objectName="version_label"] {{
            color: {get_color('text_secondary')};
            font-size: 11px;
            font-weight: bold;
            background-color: transparent;
        }}
        """


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

