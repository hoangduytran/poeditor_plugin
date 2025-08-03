"""
Icon Manager service for the POEditor application.

Handles dynamic icon generation with different states (active, hover, inactive)
for the sidebar and other components.
"""

from typing import Dict, Tuple, Optional
from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from PySide6.QtCore import Qt, QSize
from PySide6.QtSvg import QSvgRenderer
from lg import logger

# Resources are imported in main.py
# Icons are loaded from the compiled resources.py file
logger.info("IconManager using compiled resources from main application")


class IconManager:
    """
    Manages icons with different states for the application.
    
    Provides dynamic icon generation for sidebar buttons with proper
    state handling (active, hover, inactive).
    """
    
    def __init__(self):
        self._icon_cache: Dict[str, QIcon] = {}
        self._default_size = 32
        
        # Sidebar icon colors (fixed dark theme)
        self._sidebar_colors = {
            'active': '#ffffff',
            'hover': '#cccccc', 
            'inactive': '#858585'
        }
        
        logger.info("IconManager initialized")
    
    def create_emoji_icon(self, emoji: str, size: Optional[int] = None, 
                         color: str = '#ffffff') -> QIcon:
        """
        Create an icon from an emoji character.
        
        Args:
            emoji: Unicode emoji character
            size: Icon size in pixels (defaults to _default_size)
            color: Text color for the emoji
            
        Returns:
            QIcon with the emoji rendered
        """
        if size is None:
            size = self._default_size
            
        cache_key = f"emoji_{emoji}_{size}_{color}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Paint emoji
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        try:
            # Try using a good emoji font
            font = QFont("Apple Color Emoji", size // 2)
            font.setPixelSize(size // 2)
        except:
            try:
                # Fallback to system font
                font = QFont("Segoe UI Emoji", size // 2)
                font.setPixelSize(size // 2)
            except:
                # Fallback to default font
                font = QFont()
                font.setPixelSize(size // 2)
        
        painter.setFont(font)
        painter.setPen(QColor(color))
        painter.drawText(
            pixmap.rect(), 
            Qt.AlignmentFlag.AlignCenter, 
            emoji
        )
        painter.end()
        
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon
    
    def create_sidebar_icon_states(self, emoji: str, size: Optional[int] = None) -> Dict[str, QIcon]:
        """
        Create icons for all sidebar states (active, hover, inactive).
        
        Args:
            emoji: Unicode emoji character
            size: Icon size in pixels (defaults to _default_size)
            
        Returns:
            Dictionary with 'active', 'hover', 'inactive' QIcon objects
        """
        if size is None:
            size = self._default_size
            
        return {
            'active': self.create_emoji_icon(emoji, size, "#ffffff"),
            'hover': self.create_emoji_icon(emoji, size, "#cccccc"),
            'inactive': self.create_emoji_icon(emoji, size, "#858585")
        }
    
    def create_text_icon(self, text: str, size: Optional[int] = None,
                        color: str = '#ffffff', 
                        background_color: str = 'transparent') -> QIcon:
        """
        Create an icon from text.
        
        Args:
            text: Text to render
            size: Icon size in pixels (defaults to _default_size)
            color: Text color
            background_color: Background color
            
        Returns:
            QIcon with the text rendered
        """
        if size is None:
            size = self._default_size
            
        cache_key = f"text_{text}_{size}_{color}_{background_color}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Create pixmap
        pixmap = QPixmap(size, size)
        if background_color == 'transparent':
            pixmap.fill(Qt.GlobalColor.transparent)
        else:
            pixmap.fill(QColor(background_color))
        
        # Paint text
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont()
        font.setPixelSize(size // 3)
        font.setBold(True)
        
        painter.setFont(font)
        painter.setPen(QColor(color))
        painter.drawText(
            pixmap.rect(), 
            Qt.AlignmentFlag.AlignCenter, 
            text
        )
        painter.end()
        
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon
    
    def create_colored_rect_icon(self, color: str, size: Optional[int] = None,
                                border_color: Optional[str] = None) -> QIcon:
        """
        Create a colored rectangle icon.
        
        Args:
            color: Fill color
            size: Icon size in pixels (defaults to _default_size)
            border_color: Optional border color
            
        Returns:
            QIcon with colored rectangle
        """
        if size is None:
            size = self._default_size
            
        cache_key = f"rect_{color}_{size}_{border_color or 'none'}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Paint rectangle
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(pixmap.rect(), QColor(color))
        
        if border_color:
            painter.setPen(QColor(border_color))
            painter.drawRect(pixmap.rect())
            
        painter.end()
        
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon
    
    def _create_fallback_icon(self, size: int, color: str) -> QIcon:
        """
        Create a fallback icon when other methods fail.
        
        Args:
            size: Icon size in pixels
            color: Icon color
            
        Returns:
            Simple fallback QIcon
        """
        return self.create_text_icon("●", size, color)
    
    def create_svg_icon(self, icon_name: str, size: int = 16, active: bool = False) -> QIcon:
        """Create an icon from an SVG resource.
        
        Args:
            icon_name: Name of the icon (e.g., 'explorer', 'search')
            size: Icon size in pixels
            active: Whether to create active (white) or inactive (gray) version
            
        Returns:
            QIcon object
        """
        try:
            # Determine icon path based on state
            state_suffix = "_active" if active else "_inactive"
            resource_path = f":icons/{icon_name}{state_suffix}.svg"
            
            cache_key = f"svg_{icon_name}_{state_suffix}_{size}"
            if cache_key in self._icon_cache:
                return self._icon_cache[cache_key]
            
            # Create SVG renderer
            renderer = QSvgRenderer(resource_path)
            if not renderer.isValid():
                logger.warning(f"Invalid SVG resource: {resource_path}")
                emoji_map = {
                    'explorer': '📁', 'search': '🔍', 'preferences': '⚙️',
                    'extensions': '🧩', 'account': '👤'
                }
                emoji = emoji_map.get(icon_name, '●')
                color = self._sidebar_colors['active'] if active else self._sidebar_colors['inactive']
                return self.create_emoji_icon(emoji, size, color)
            
            # Render to pixmap
            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            icon = QIcon(pixmap)
            self._icon_cache[cache_key] = icon
            return icon
            
        except Exception as e:
            logger.error(f"Failed to create SVG icon for {icon_name}: {e}")
            # Fallback to emoji
            emoji_map = {
                'explorer': '📁', 'search': '🔍', 'preferences': '⚙️',
                'extensions': '🧩', 'account': '👤'
            }
            emoji = emoji_map.get(icon_name, '●')
            color = self._sidebar_colors['active'] if active else self._sidebar_colors['inactive']
            return self.create_emoji_icon(emoji, size, color)
    
    def get_sidebar_icon(self, activity_id: str, size: int = 16) -> Dict[str, QIcon]:
        """
        Get icon states for sidebar activity.
        
        Args:
            activity_id: The activity ID (explorer, search, etc.)
            size: Icon size in pixels
            
        Returns:
            Dictionary with 'active', 'hover', 'inactive' icons
        """
        emoji_map = {
            'explorer': '📁', 'search': '🔍', 'preferences': '⚙️',
            'extensions': '🧩', 'account': '👤'
        }
        
        emoji = emoji_map.get(activity_id, '●')
        
        return {
            'active': self.create_emoji_icon(emoji, size, "#ffffff"),
            'hover': self.create_emoji_icon(emoji, size, "#cccccc"),
            'inactive': self.create_emoji_icon(emoji, size, "#858585")
        }
    
    def get_activity_button_icon(self, activity_id: str, active: bool = False, size: int = 32) -> QIcon:
        """
        Get a single icon for an activity button with proper sizing.
        
        Args:
            activity_id: The activity ID (explorer, search, preferences, etc.)
            active: Whether to get the active or inactive version
            size: Icon size in pixels (optimized for activity buttons)
            
        Returns:
            QIcon object for the activity button
        """
        return self.create_svg_icon(activity_id, size, active)
    
    def get_default_sidebar_icons(self) -> Dict[str, QIcon]:
        """
        Get default icons for sidebar panels.
        
        Returns:
            Dictionary mapping panel names to QIcon objects
        """
        icons = {}
        
        # Default panel icons with emojis
        default_panels = {
            'explorer': '📁',
            'search': '🔍',
            'preferences': '⚙️',
            'extensions': '🧩',
            'account': '👤'
        }
        
        for panel_name, emoji in default_panels.items():
            try:
                # Create icon with active state color
                icons[panel_name] = self.create_emoji_icon(
                    emoji, 
                    color=self._sidebar_colors['active']
                )
            except Exception as e:
                logger.error(f"Failed to create icon for {panel_name}: {e}")
                icons[panel_name] = self._create_fallback_icon(
                    self._default_size, 
                    self._sidebar_colors['active']
                )
        
        return icons
    
    def clear_cache(self) -> None:
        """Clear the icon cache."""
        self._icon_cache.clear()
        logger.info("Icon cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the number of cached icons."""
        return len(self._icon_cache)
    
    def set_default_size(self, size: int) -> None:
        """
        Set the default icon size.
        
        Args:
            size: Default size in pixels
        """
        self._default_size = size
        logger.info(f"Default icon size set to {size}px")
    
    def update_sidebar_colors(self, active: str, hover: str, inactive: str) -> None:
        """
        Update sidebar icon colors.
        
        Args:
            active: Color for active icons
            hover: Color for hover icons  
            inactive: Color for inactive icons
        """
        self._sidebar_colors = {
            'active': active,
            'hover': hover,
            'inactive': inactive
        }
        
        # Clear cache to force regeneration with new colors
        self.clear_cache()
        logger.info("Sidebar icon colors updated")
        
    def get_icon(self, icon_name: str) -> QIcon:
        """
        Get a QIcon by name, ensuring compatibility with plugin API.
        
        Args:
            icon_name: Name of the icon (e.g., 'explorer_active', 'search_inactive')
            
        Returns:
            QIcon object for the specified icon name
        """
        try:
            # Handle different naming patterns
            if icon_name.endswith('_active'):
                base_name = icon_name.replace('_active', '')
                return self.create_svg_icon(base_name, active=True)
            elif icon_name.endswith('_inactive'):
                base_name = icon_name.replace('_inactive', '')
                return self.create_svg_icon(base_name, active=False)
            else:
                # Default to active icon if state not specified
                return self.create_svg_icon(icon_name, active=True)
        except Exception as e:
            logger.error(f"Failed to get icon {icon_name}: {e}")
            return self._create_fallback_icon(self._default_size, '#ffffff')


# Global icon manager instance
icon_manager = IconManager()
