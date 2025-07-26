"""
Typography system for the PySide POEditor plugin.

This module provides centralized font and typography management across the application.
Supports theme-based font configurations and user preferences.

Following rules.md: No hasattr/getattr usage, proper error handling with lg.py logger.
"""

from enum import Enum
from typing import Dict, Optional
from lg import logger
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class FontRole(Enum):
    """Typography roles for different UI elements."""
    DEFAULT = "default"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    BODY = "body"
    SMALL = "small"
    CAPTION = "caption"
    CODE = "code"
    BUTTON = "button"
    MENU = "menu"
    TOOLTIP = "tooltip"
    TITLE = "title"
    SUBTITLE = "subtitle"
    PANEL_TITLE = "panel_title"  # Add missing PANEL_TITLE role


class TypographyManager(QObject):
    """Manages fonts and typography throughout the application."""

    # Signal emitted when fonts change
    fonts_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_font_family = "Inter, Segoe UI, Arial, sans-serif"
        self._base_font_size = 13
        self._scale_factor = 1.0
        self._fonts = {}
        self._font_configs = {}

        self._initialize_default_typography()

    def _initialize_default_typography(self):
        """Initialize default font configurations."""
        try:
            # Base font sizes relative to base size
            self._font_configs = {
                FontRole.DEFAULT: {"size": 1.0, "weight": QFont.Weight.Normal},
                FontRole.HEADING_1: {"size": 2.0, "weight": QFont.Weight.Bold},
                FontRole.HEADING_2: {"size": 1.7, "weight": QFont.Weight.Bold},
                FontRole.HEADING_3: {"size": 1.4, "weight": QFont.Weight.Bold},
                FontRole.BODY: {"size": 1.0, "weight": QFont.Weight.Normal},
                FontRole.SMALL: {"size": 0.85, "weight": QFont.Weight.Normal},
                FontRole.CAPTION: {"size": 0.75, "weight": QFont.Weight.Normal},
                FontRole.CODE: {"size": 0.9, "weight": QFont.Weight.Normal, "family": "Consolas, Monaco, monospace"},
                FontRole.BUTTON: {"size": 1.0, "weight": QFont.Weight.Medium},
                FontRole.MENU: {"size": 0.95, "weight": QFont.Weight.Normal},
                FontRole.TOOLTIP: {"size": 0.85, "weight": QFont.Weight.Normal},
                FontRole.TITLE: {"size": 1.2, "weight": QFont.Weight.Medium},
                FontRole.SUBTITLE: {"size": 1.1, "weight": QFont.Weight.Normal},
                FontRole.PANEL_TITLE: {"size": 1.1, "weight": QFont.Weight.Bold},  # Default config for PANEL_TITLE
            }

            # Generate all fonts
            self._generate_fonts()

            logger.info("Typography system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize typography system: {e}")
            self._create_fallback_fonts()

    def _generate_fonts(self):
        """Generate all fonts based on current configuration."""
        try:
            self._fonts.clear()

            for role, config in self._font_configs.items():
                font = QFont()

                # Set font family
                family = config.get("family", self._base_font_family)
                font.setFamily(family)

                # Set font size
                size_multiplier = config.get("size", 1.0)
                final_size = int(self._base_font_size * size_multiplier * self._scale_factor)
                font.setPointSize(final_size)

                # Set font weight
                weight = config.get("weight", QFont.Weight.Normal)
                font.setWeight(weight)

                self._fonts[role] = font

        except Exception as e:
            logger.error(f"Failed to generate fonts: {e}")
            self._create_fallback_fonts()

    def _create_fallback_fonts(self):
        """Create basic fallback fonts if generation fails."""
        try:
            fallback_font = QFont("Arial", 13)
            for role in FontRole:
                self._fonts[role] = fallback_font
            logger.warning("Using fallback fonts due to typography initialization failure")
        except Exception as e:
            logger.error(f"Failed to create fallback fonts: {e}")

    def get_font(self, role: FontRole) -> QFont:
        """
        Get font for a specific role.

        Args:
            role: FontRole enum value

        Returns:
            QFont configured for the role
        """
        try:
            if role in self._fonts:
                return QFont(self._fonts[role])  # Return a copy
            else:
                logger.warning(f"Font role {role} not found, using default")
                return self.get_font(FontRole.DEFAULT)
        except Exception as e:
            logger.error(f"Failed to get font for role {role}: {e}")
            # Return basic fallback font
            return QFont("Arial", 13)

    def set_base_font_family(self, family: str):
        """Set the base font family and regenerate all fonts."""
        try:
            self._base_font_family = family
            self._generate_fonts()
            self.fonts_changed.emit()
            logger.info(f"Base font family changed to: {family}")
        except Exception as e:
            logger.error(f"Failed to set base font family: {e}")

    def set_base_font_size(self, size: int):
        """Set the base font size and regenerate all fonts."""
        try:
            if size < 8 or size > 72:
                logger.warning(f"Font size {size} is outside recommended range (8-72)")

            self._base_font_size = size
            self._generate_fonts()
            self.fonts_changed.emit()
            logger.info(f"Base font size changed to: {size}")
        except Exception as e:
            logger.error(f"Failed to set base font size: {e}")

    def set_scale_factor(self, scale: float):
        """Set the global scale factor and regenerate all fonts."""
        try:
            if scale < 0.5 or scale > 3.0:
                logger.warning(f"Scale factor {scale} is outside recommended range (0.5-3.0)")

            self._scale_factor = scale
            self._generate_fonts()
            self.fonts_changed.emit()
            logger.info(f"Font scale factor changed to: {scale}")
        except Exception as e:
            logger.error(f"Failed to set scale factor: {e}")

    def get_font_metrics(self, role: FontRole) -> QFontMetrics:
        """Get font metrics for a specific role."""
        try:
            font = self.get_font(role)
            return QFontMetrics(font)
        except Exception as e:
            logger.error(f"Failed to get font metrics for role {role}: {e}")
            return QFontMetrics(QFont("Arial", 13))

    def get_base_font_family(self) -> str:
        """Get the current base font family."""
        return self._base_font_family

    def get_base_font_size(self) -> int:
        """Get the current base font size."""
        return self._base_font_size

    def get_scale_factor(self) -> float:
        """Get the current scale factor."""
        return self._scale_factor

    def get_available_roles(self) -> list:
        """Get list of available font roles."""
        return list(FontRole)


# Global typography manager instance
_typography_manager: Optional[TypographyManager] = None


def get_typography_manager() -> TypographyManager:
    """Get the global typography manager instance."""
    global _typography_manager
    try:
        if _typography_manager is None:
            _typography_manager = TypographyManager()
        return _typography_manager
    except Exception as e:
        logger.error(f"Failed to get typography manager: {e}")
        # Create a new instance if needed
        _typography_manager = TypographyManager()
        return _typography_manager


def get_font(role: FontRole) -> QFont:
    """
    Convenience function to get a font for a specific role.

    Args:
        role: FontRole enum value

    Returns:
        QFont configured for the role
    """
    try:
        manager = get_typography_manager()
        return manager.get_font(role)
    except Exception as e:
        logger.error(f"Failed to get font for role {role}: {e}")
        # Return basic fallback font
        return QFont("Arial", 13)


def set_base_font_family(family: str):
    """Set the base font family globally."""
    try:
        manager = get_typography_manager()
        manager.set_base_font_family(family)
    except Exception as e:
        logger.error(f"Failed to set base font family: {e}")


def set_base_font_size(size: int):
    """Set the base font size globally."""
    try:
        manager = get_typography_manager()
        manager.set_base_font_size(size)
    except Exception as e:
        logger.error(f"Failed to set base font size: {e}")


def set_scale_factor(scale: float):
    """Set the global scale factor."""
    try:
        manager = get_typography_manager()
        manager.set_scale_factor(scale)
    except Exception as e:
        logger.error(f"Failed to set scale factor: {e}")
