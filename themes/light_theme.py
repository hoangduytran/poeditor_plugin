"""
Light theme for the POEditor application.

Provides a clean, bright interface similar to VS Code Light theme.
"""

from typing import Dict, Any
from .base_theme import BaseTheme, ThemeColors


class LightTheme(BaseTheme):
    """
    Light theme implementation.
    
    Features a clean, bright interface with good contrast and readability.
    Suitable for well-lit environments and users who prefer light backgrounds.
    """
    
    def __init__(self):
        super().__init__("Light")
    
    def define_colors(self) -> ThemeColors:
        """Define the light theme color palette."""
        return ThemeColors(
            # Main background colors
            background="#ffffff",
            secondary_background="#f8f9fa",
            surface="#ffffff",
            
            # Text colors
            text_primary="#212529",
            text_secondary="#6c757d",
            text_disabled="#adb5bd",
            text_inverse="#ffffff",
            
            # Accent colors
            accent="#0066cc",
            accent_hover="#0052a3",
            accent_pressed="#003d7a",
            accent_light="#e6f2ff",
            
            # State colors
            success="#28a745",
            warning="#fd7e14",
            error="#dc3545",
            info="#17a2b8",
            
            # Border colors
            border="#dee2e6",
            border_focus="#0066cc",
            border_hover="#adb5bd",
            
            # Interactive element colors
            button_background="#f8f9fa",
            button_hover="#e9ecef",
            button_pressed="#dee2e6",
            
            # Input field colors
            input_background="#ffffff",
            input_border="#ced4da",
            input_focus="#0066cc",
            
            # Selection colors
            selection_background="#e6f2ff",
            selection_text="#212529",
            
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
    def from_dict(cls, data: Dict[str, Any]) -> 'LightTheme':
        """Create light theme from dictionary."""
        theme = cls()
        if 'colors' in data:
            # Update colors from data - use predefined color fields from ThemeColors
            colors_data = data['colors']
            valid_color_fields = {
                'background', 'secondary_background', 'surface',
                'text_primary', 'text_secondary', 'text_disabled', 'text_inverse',
                'accent', 'accent_hover', 'accent_pressed', 'accent_light',
                'success', 'warning', 'error', 'info',
                'border', 'border_focus', 'border_hover',
                'button_background', 'button_hover', 'button_pressed'
            }
            
            for field_name, value in colors_data.items():
                if field_name in valid_color_fields:
                    try:
                        setattr(theme._colors, field_name, value)
                    except AttributeError:
                        # Field doesn't exist in this ThemeColors instance
                        pass
        return theme
