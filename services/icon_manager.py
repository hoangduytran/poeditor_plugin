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
            QIcon object
        """
        if size is None:
            size = self._default_size
        
        cache_key = f"emoji_{emoji}_{size}_{color}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        try:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            
            # Use system font for emoji rendering
            font = QFont()
            try:
                import platform
                if platform.system() == 'Darwin':  # macOS
                    font.setFamily("Apple Color Emoji")
                elif platform.system() == 'Windows':
                    font.setFamily("Segoe UI Emoji")
                else:  # Linux
                    font.setFamily("Noto Color Emoji")
            except:
                # Fallback to default font
                pass
            
            font.setPointSize(max(8, size // 2))  # Ensure minimum font size
            painter.setFont(font)
            painter.setPen(QColor(color))
            
            # Center the emoji
            painter.drawText(0, 0, size, size, 
                           Qt.AlignmentFlag.AlignCenter, emoji)
            painter.end()
            
            icon = QIcon(pixmap)
            self._icon_cache[cache_key] = icon
            
            return icon
            
        except Exception as e:
            logger.error(f"Failed to create emoji icon for '{emoji}': {e}")
            return self._create_fallback_icon(size, color)
    
    def create_sidebar_icon_states(self, emoji: str, size: Optional[int] = None) -> Dict[str, QIcon]:
        """
        Create all icon states for sidebar buttons.
        
        Args:
            emoji: Unicode emoji character
            size: Icon size in pixels
            
        Returns:
            Dictionary with 'active', 'hover', 'inactive' QIcon objects
        """
        if size is None:
            size = self._default_size
        
        states = {}
        for state, color in self._sidebar_colors.items():
            states[state] = self.create_emoji_icon(emoji, size, color)
        
        return states
    
    def create_text_icon(self, text: str, size: Optional[int] = None,
                        background_color: str = '#333333',
                        text_color: str = '#ffffff') -> QIcon:
        """
        Create an icon from text.
        
        Args:
            text: Text to render
            size: Icon size in pixels
            background_color: Background color
            text_color: Text color
            
        Returns:
            QIcon object
        """
        if size is None:
            size = self._default_size
        
        cache_key = f"text_{text}_{size}_{background_color}_{text_color}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        try:
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(background_color))
            
            painter = QPainter(pixmap)
            
            font = QFont()
            font.setPointSize(size // 3)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(text_color))
            
            # Center the text
            painter.drawText(0, 0, size, size,
                           Qt.AlignmentFlag.AlignCenter, text)
            painter.end()
            
            icon = QIcon(pixmap)
            self._icon_cache[cache_key] = icon
            
            return icon
            
        except Exception as e:
            logger.error(f"Failed to create text icon for '{text}': {e}")
            return self._create_fallback_icon(size, text_color)
    
    def create_colored_rect_icon(self, color: str, size: Optional[int] = None,
                                border_color: Optional[str] = None) -> QIcon:
        """
        Create a simple colored rectangle icon.
        
        Args:
            color: Fill color
            size: Icon size in pixels
            border_color: Optional border color
            
        Returns:
            QIcon object
        """
        if size is None:
            size = self._default_size
        
        cache_key = f"rect_{color}_{size}_{border_color}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        try:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            
            # Fill the rectangle
            painter.fillRect(2, 2, size-4, size-4, QColor(color))
            
            # Add border if specified
            if border_color:
                painter.setPen(QColor(border_color))
                painter.drawRect(2, 2, size-4, size-4)
            
            painter.end()
            
            icon = QIcon(pixmap)
            self._icon_cache[cache_key] = icon
            
            return icon
            
        except Exception as e:
            logger.error(f"Failed to create colored rect icon: {e}")
            return self._create_fallback_icon(size, color)
    
    def _create_fallback_icon(self, size: int, color: str) -> QIcon:
        """
        Create a simple fallback icon.
        
        Args:
            size: Icon size in pixels
            color: Icon color
            
        Returns:
            Simple rectangular QIcon
        """
        try:
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(color))
            return QIcon(pixmap)
        except Exception as e:
            logger.error(f"Failed to create fallback icon: {e}")
            # Return empty icon as last resort
            return QIcon()
    
    def create_svg_icon(self, icon_name: str, size: int = 16, active: bool = False) -> QIcon:
        """
        Create a QIcon from SVG files using compiled Qt resources.
        
        Args:
            icon_name: Name of the icon (e.g., 'explorer', 'search')
            size: Size of the icon in pixels
            active: Whether to load the active (white) or inactive (grey) version
            
        Returns:
            QIcon object with the SVG icon
        """
        try:
            # Determine resource path
            state = "active" if active else "inactive"
            resource_path = f":/icons/{icon_name}_{state}.svg"
            
            # Create QIcon from resource
            icon = QIcon(resource_path)
            
            if icon.isNull():
                logger.warning(f"Failed to load SVG icon from resource: {resource_path}")
                # Fallback to file system if resource loading fails
                svg_file = Path(__file__).parent.parent / "icons" / f"{icon_name}_{state}.svg"
                if svg_file.exists():
                    icon = QIcon(str(svg_file))
                    logger.debug(f"Loaded SVG icon from file system: {svg_file}")
                else:
                    logger.warning(f"SVG file not found: {svg_file}")
                    return self.create_emoji_icon("❓", size)  # Fallback
            else:
                logger.debug(f"Created SVG icon from resource: {icon_name} ({state}) at size {size}")
            
            return icon
            
        except Exception as e:
            logger.error(f"Failed to create SVG icon {icon_name}: {e}")
            return self.create_emoji_icon("❓", size)  # Fallback
    
    def get_sidebar_icon(self, activity_id: str, size: int = 16) -> Dict[str, QIcon]:
        """
        Get both active and inactive icons for a sidebar activity.
        
        Args:
            activity_id: The activity ID (explorer, search, preferences, etc.)
            size: Icon size in pixels
            
        Returns:
            Dictionary with 'active' and 'inactive' QIcon objects
        """
        try:
            return {
                'active': self.create_svg_icon(activity_id, size, active=True),
                'inactive': self.create_svg_icon(activity_id, size, active=False)
            }
        except Exception as e:
            logger.error(f"Failed to get sidebar icons for {activity_id}: {e}")
            # Fallback to emoji-based icons
            emoji_map = {
                'explorer': '📁',
                'search': '🔍', 
                'preferences': '⚙️',
                'extensions': '🧩',
                'account': '👤'
            }
            emoji = emoji_map.get(activity_id, '❓')
            return {
                'active': self.create_emoji_icon(emoji, size, "#ffffff"),
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
