"""
Main Theme Manager for POEditor Application.

This file provides backward compatibility by importing from the CSS file-based theme manager.
All new code should use css_file_based_theme_manager directly.
"""

# Import everything from the CSS file-based theme manager
from .css_file_based_theme_manager import CSSFileBasedThemeManager

# Alias for backward compatibility
ThemeManager = CSSFileBasedThemeManager

# Create a global instance for backward compatibility
theme_manager = CSSFileBasedThemeManager.get_instance()

# Export for backward compatibility
__all__ = ['ThemeManager', 'theme_manager']