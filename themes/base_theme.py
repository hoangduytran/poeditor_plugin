"""
Base theme system for the POEditor application.

This module provides the foundation for all themes, defining the color palette
structure and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass
from PySide6.QtGui import QColor


@dataclass
class ThemeColors:
    """Color palette for a theme."""
    
    # Main background colors
    background: str = "#ffffff"
    secondary_background: str = "#f3f3f3"
    surface: str = "#ffffff"
    
    # Text colors
    text_primary: str = "#333333"
    text_secondary: str = "#666666"
    text_disabled: str = "#cccccc"
    text_inverse: str = "#ffffff"
    
    # Accent colors
    accent: str = "#007acc"
    accent_hover: str = "#005a9e"
    accent_pressed: str = "#004578"
    accent_light: str = "#e8f4fd"
    
    # State colors
    success: str = "#28a745"
    warning: str = "#ffc107"
    error: str = "#dc3545"
    info: str = "#17a2b8"
    
    # Border colors
    border: str = "#e5e5e5"
    border_focus: str = "#007acc"
    border_hover: str = "#cccccc"
    
    # Interactive element colors
    button_background: str = "#f8f9fa"
    button_hover: str = "#e9ecef"
    button_pressed: str = "#dee2e6"
    
    # Input field colors
    input_background: str = "#ffffff"
    input_border: str = "#ced4da"
    input_focus: str = "#007acc"
    
    # Selection colors
    selection_background: str = "#e8f4fd"
    selection_text: str = "#333333"
    
    # Sidebar colors (fixed dark theme)
    sidebar_background: str = "#333333"
    sidebar_secondary: str = "#2d2d30"
    sidebar_border: str = "#464647"
    sidebar_text: str = "#cccccc"
    sidebar_icon_active: str = "#ffffff"
    sidebar_icon_hover: str = "#cccccc"
    sidebar_icon_inactive: str = "#858585"
    
    # Status bar colors (fixed dark theme like VS Code)
    statusbar_background: str = "#007acc"  # VS Code blue
    statusbar_text: str = "#ffffff"
    statusbar_border: str = "#005a9e"


class BaseTheme(ABC):
    """
    Base class for all themes.
    
    Defines the interface that all themes must implement and provides
    common functionality for CSS generation and color management.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._colors = self.define_colors()
        self._css_cache: Dict[str, str] = {}
    
    @abstractmethod
    def define_colors(self) -> ThemeColors:
        """Define the color palette for this theme."""
        pass
    
    @property
    def colors(self) -> ThemeColors:
        """Get the theme colors."""
        return self._colors
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color value by name.

        Args:
            color_name: Name of the color (e.g., 'background', 'text_primary')
            
        Returns:
            Hex color string
        """
        try:
            return self._colors.__dict__[color_name]
        except KeyError:
            raise ValueError(f"Color '{color_name}' not found in theme '{self.name}'")

    def get_qcolor(self, color_name: str) -> QColor:
        """
        Get a QColor object for a named color.
        
        Args:
            color_name: Name of the color
            
        Returns:
            QColor object
        """
        hex_color = self.get_color(color_name)
        return QColor(hex_color)
    
    def generate_main_window_css(self) -> str:
        """Generate CSS for the main application window."""
        if 'main_window' in self._css_cache:
            return self._css_cache['main_window']
        
        css = f"""
        MainAppWindow {{
            background-color: {self._colors.background};
            color: {self._colors.text_primary};
        }}
        
        QWidget {{
            background-color: {self._colors.background};
            color: {self._colors.text_primary};
            selection-background-color: {self._colors.selection_background};
            selection-color: {self._colors.selection_text};
        }}
        
        QMenuBar {{
            background-color: {self._colors.secondary_background};
            color: {self._colors.text_primary};
            border-bottom: 1px solid {self._colors.border};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self._colors.button_hover};
        }}
        
        QStatusBar {{
            background-color: {self._colors.statusbar_background};
            color: {self._colors.statusbar_text};
            border-top: 1px solid {self._colors.statusbar_border};
            font-size: 11px;
        }}
        """
        
        self._css_cache['main_window'] = css
        return css
    
    def generate_button_css(self) -> str:
        """Generate CSS for buttons."""
        if 'button' in self._css_cache:
            return self._css_cache['button']
        
        css = f"""
        QPushButton {{
            background-color: {self._colors.button_background};
            color: {self._colors.text_primary};
            border: 1px solid {self._colors.border};
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {self._colors.button_hover};
            border-color: {self._colors.border_hover};
        }}
        
        QPushButton:pressed {{
            background-color: {self._colors.button_pressed};
        }}
        
        QPushButton:disabled {{
            background-color: {self._colors.secondary_background};
            color: {self._colors.text_disabled};
            border-color: {self._colors.border};
        }}
        
        QPushButton[primary="true"] {{
            background-color: {self._colors.accent};
            color: {self._colors.text_inverse};
            border-color: {self._colors.accent};
        }}
        
        QPushButton[primary="true"]:hover {{
            background-color: {self._colors.accent_hover};
            border-color: {self._colors.accent_hover};
        }}
        
        QPushButton[primary="true"]:pressed {{
            background-color: {self._colors.accent_pressed};
        }}
        """
        
        self._css_cache['button'] = css
        return css
    
    def generate_input_css(self) -> str:
        """Generate CSS for input fields."""
        if 'input' in self._css_cache:
            return self._css_cache['input']
        
        css = f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self._colors.input_background};
            color: {self._colors.text_primary};
            border: 1px solid {self._colors.input_border};
            padding: 6px;
            border-radius: 4px;
            selection-background-color: {self._colors.selection_background};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self._colors.input_focus};
            outline: none;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {self._colors.secondary_background};
            color: {self._colors.text_disabled};
        }}
        
        QComboBox {{
            background-color: {self._colors.input_background};
            color: {self._colors.text_primary};
            border: 1px solid {self._colors.input_border};
            padding: 6px;
            border-radius: 4px;
        }}
        
        QComboBox:hover {{
            border-color: {self._colors.border_hover};
        }}
        
        QComboBox:focus {{
            border-color: {self._colors.input_focus};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {self._colors.text_secondary};
            border-top: none;
            border-right: none;
            width: 6px;
            height: 6px;
            transform: rotate(-45deg);
        }}
        """
        
        self._css_cache['input'] = css
        return css
    
    def generate_sidebar_css(self) -> str:
        """
        Generate CSS for the sidebar (fixed dark theme).
        
        Note: This CSS is always the same regardless of the main theme,
        matching VS Code's consistent dark sidebar across all themes.
        """
        return f"""
        /* Fixed Dark Activity Bar - Never changes like VS Code */
        SidebarActivityBar {{
            background-color: {self._colors.sidebar_background};
            border-right: 1px solid {self._colors.sidebar_border};
        }}
        
        /* Sidebar Manager Container - Uses theme colors */
        SidebarManager {{
            background-color: {self._colors.secondary_background};
            border-right: 1px solid {self._colors.border};
        }}
        
        /* Activity Bar Icons - Match VS Code states exactly */
        SidebarActivityBar QToolButton {{
            border: none;
            padding: 12px 8px;
            margin: 0px;
            background-color: transparent;
            color: {self._colors.sidebar_icon_inactive};
            font-size: 20px;
            min-width: 34px;
            min-height: 34px;
            border-left: 3px solid transparent;
        }}
        
        SidebarActivityBar QToolButton:hover {{
            background-color: rgba(255, 255, 255, 0.1);
            color: {self._colors.sidebar_icon_hover};
        }}
        
        SidebarActivityBar QToolButton:checked {{
            background-color: rgba(255, 255, 255, 0.08);
            color: {self._colors.sidebar_icon_active};
            border-left: 3px solid {self._colors.sidebar_icon_active};
        }}
        
        SidebarActivityBar QToolButton:checked:hover {{
            background-color: rgba(255, 255, 255, 0.12);
        }}
        
        /* Panel Stack - Uses theme colors (not fixed dark) */
        QStackedWidget {{
            background-color: {self._colors.secondary_background};
            border-right: 1px solid {self._colors.border};
            color: {self._colors.text_primary};
        }}
        
        /* Panel content styling - Uses theme colors */
        QStackedWidget QWidget {{
            background-color: {self._colors.secondary_background};
            color: {self._colors.text_primary};
        }}
        
        /* Panel headers and labels - Uses theme colors */
        QStackedWidget QLabel[panel_title="true"] {{
            color: {self._colors.text_primary};
            font-weight: bold;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px;
            background-color: {self._colors.background};
        }}
        """
    
    def generate_complete_css(self) -> str:
        """Generate complete CSS for the entire application."""
        css_parts = [
            self.generate_main_window_css(),
            self.generate_button_css(),
            self.generate_input_css(),
            self.generate_sidebar_css(),
        ]
        
        return "\\n".join(css_parts)
    
    def clear_cache(self) -> None:
        """Clear the CSS cache to force regeneration."""
        self._css_cache.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert theme to dictionary for serialization.
        
        Returns:
            Dictionary representation of the theme
        """
        color_dict = {}
        for field_name in self._colors.__dataclass_fields__:
            color_dict[field_name] = self._colors.__dict__[field_name]

        return {
            'name': self.name,
            'colors': color_dict
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseTheme':
        """
        Create theme from dictionary.
        
        Args:
            data: Dictionary containing theme data
            
        Returns:
            Theme instance
        """
        # This will be implemented by subclasses
        raise NotImplementedError("Subclasses must implement from_dict")
