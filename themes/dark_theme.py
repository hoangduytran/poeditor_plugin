"""
Dark theme for the POEditor application.

Provides a dark interface similar to VS Code Dark+ theme.
"""

from typing import Dict, Any
from .base_theme import BaseTheme, ThemeColors


class DarkTheme(BaseTheme):
    """
    Dark theme implementation.
    
    Features a dark interface with reduced eye strain for low-light environments.
    Similar to VS Code's Dark+ theme with appropriate contrast ratios.
    """
    
    def __init__(self):
        super().__init__("Dark")
    
    def define_colors(self) -> ThemeColors:
        """Define the dark theme color palette."""
        return ThemeColors(
            # Main background colors
            background="#1e1e1e",
            secondary_background="#252526",
            surface="#2d2d30",
            
            # Text colors
            text_primary="#cccccc",
            text_secondary="#969696",
            text_disabled="#6a6a6a",
            text_inverse="#1e1e1e",
            
            # Accent colors
            accent="#007acc",
            accent_hover="#1177bb",
            accent_pressed="#0e639c",
            accent_light="#094771",
            
            # State colors
            success="#4ec9b0",
            warning="#ffcc02",
            error="#f44747",
            info="#75beff",
            
            # Border colors
            border="#464647",
            border_focus="#007acc",
            border_hover="#6a6a6a",
            
            # Interactive element colors
            button_background="#0e639c",
            button_hover="#1177bb",
            button_pressed="#007acc",
            
            # Input field colors
            input_background="#3c3c3c",
            input_border="#616161",
            input_focus="#007acc",
            
            # Selection colors
            selection_background="#264f78",
            selection_text="#cccccc",
            
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
    def from_dict(cls, data: Dict[str, Any]) -> 'DarkTheme':
        """Create dark theme from dictionary."""
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
