"""
Main Theme Manager for POEditor Application.

    # Make Theme accessible through ThemeManager
    Theme = Theme

This file provides backward compatibility by importing from the CSS file-based theme manager.
All new code should use css_file_based_theme_manager directly.
"""


# Import Theme and everything else from the CSS file-based theme manager
from .css_file_based_theme_manager import CSSFileBasedThemeManager, Theme


# Alias for backward compatibility
ThemeManager = CSSFileBasedThemeManager


# Create a global instance for backward compatibility
theme_manager = CSSFileBasedThemeManager.get_instance()

# Export for backward compatibility
__all__ = ['ThemeManager', 'Theme', 'theme_manager']