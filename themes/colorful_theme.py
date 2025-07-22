"""
Colorful theme for the POEditor application.

Provides a vibrant interface with accent colors and personality.
"""

from typing import Dict, Any
from .base_theme import BaseTheme, ThemeColors


class ColorfulTheme(BaseTheme):
    """
    Colorful theme implementation.
    
    Features a vibrant interface with colorful accents while maintaining
    good readability and usability. Adds personality to the application.
    """
    
    def __init__(self):
        super().__init__("Colorful")
    
    def define_colors(self) -> ThemeColors:
        """Define the colorful theme color palette."""
        return ThemeColors(
            # Main background colors
            background="#fafbfc",
            secondary_background="#f1f8ff",
            surface="#ffffff",
            
            # Text colors
            text_primary="#24292e",
            text_secondary="#586069",
            text_disabled="#959da5",
            text_inverse="#ffffff",
            
            # Accent colors
            accent="#e36209",
            accent_hover="#d15704",
            accent_pressed="#b54900",
            accent_light="#fff8f0",
            
            # State colors
            success="#28a745",
            warning="#ffd33d",
            error="#d73a49",
            info="#0366d6",
            
            # Border colors
            border="#e1e4e8",
            border_focus="#e36209",
            border_hover="#d1d5da",
            
            # Interactive element colors
            button_background="#f6f8fa",
            button_hover="#f1f8ff",
            button_pressed="#e1e4e8",
            
            # Input field colors
            input_background="#ffffff",
            input_border="#e1e4e8",
            input_focus="#e36209",
            
            # Selection colors
            selection_background="#fff8f0",
            selection_text="#24292e",
            
            # Sidebar colors (fixed dark theme - same for all themes)
            sidebar_background="#333333",
            sidebar_secondary="#2d2d30",
            sidebar_border="#464647",
            sidebar_text="#cccccc",
            sidebar_icon_active="#ffffff",
            sidebar_icon_hover="#cccccc",
            sidebar_icon_inactive="#858585",
            
            # Status bar colors (fixed dark theme like VS Code)
            statusbar_background="#007acc",
            statusbar_text="#ffffff",
            statusbar_border="#005a9e",
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColorfulTheme':
        """Create colorful theme from dictionary."""
        theme = cls()
        if 'colors' in data:
            # Update colors from data using predefined ThemeColors fields
            colors_data = data['colors']
            valid_color_fields = {
                'background', 'secondary_background', 'surface',
                'text_primary', 'text_secondary', 'text_disabled', 'text_inverse',
                'accent', 'accent_hover', 'accent_pressed', 'accent_light',
                'success', 'warning', 'error', 'info',
                'border', 'border_focus', 'border_hover',
                'button_background', 'button_hover', 'button_pressed',
                'input_background', 'input_border', 'input_focus',
                'selection_background', 'selection_text',
                'sidebar_background', 'sidebar_secondary', 'sidebar_border', 'sidebar_text',
                'sidebar_icon_active', 'sidebar_icon_hover', 'sidebar_icon_inactive',
                'statusbar_background', 'statusbar_text', 'statusbar_border'
            }
            for field_name, value in colors_data.items():
                if field_name in valid_color_fields:
                    setattr(theme._colors, field_name, value)
        return theme
