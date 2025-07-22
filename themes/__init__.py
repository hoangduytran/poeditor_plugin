"""
Theme system for the POEditor application.

This package provides a comprehensive theming system with support for
multiple themes including Light, Dark, and Colorful variants.
Also includes typography management and theme switching capabilities.
"""

from .base_theme import BaseTheme, ThemeColors
from .light_theme import LightTheme
from .dark_theme import DarkTheme
from .colorful_theme import ColorfulTheme
from .typography import TypographyManager, FontRole, get_typography_manager, get_font
from .theme_manager import ThemeManager, get_theme_manager

__all__ = [
    'BaseTheme', 
    'ThemeColors',
    'LightTheme',
    'DarkTheme', 
    'ColorfulTheme',
    'TypographyManager',
    'FontRole',
    'get_typography_manager',
    'get_font',
    'ThemeManager',
    'get_theme_manager'
]
