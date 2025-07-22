"""
Preferences Plugin Registration Module

This module handles the registration of the Preferences plugin with the core application.
"""

from lg import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api import PluginAPI

__version__ = "1.0.0"
__plugin_name__ = "Preferences"
__plugin_description__ = "Application settings and configuration management"


def register(api: 'PluginAPI') -> None:
    """
    Register the Preferences plugin with the core application.
    
    Args:
        api: Plugin API interface for interacting with the core
    """
    logger.info(f"Registering {__plugin_name__} plugin")
    
    try:
        # Import panel class
        from .preferences_panel import PreferencesPanel
        
        # Create panel instance
        panel = PreferencesPanel()
        
        # Get icon from icon manager
        icon_manager = api.get_icon_manager()
        icon = icon_manager.get_icon('preferences_active')
        
        # Register with sidebar
        api.add_sidebar_panel('preferences', panel, icon, __plugin_name__)
        
        # Register commands
        api.register_command('preferences.open', lambda: api.show_sidebar_panel('preferences'))
        api.register_command('preferences.reset', panel.reset_to_defaults)
        api.register_command('preferences.export', panel.export_settings)
        api.register_command('preferences.import', panel.import_settings)
        
        logger.info(f"{__plugin_name__} plugin registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register {__plugin_name__} plugin: {e}")
        raise
