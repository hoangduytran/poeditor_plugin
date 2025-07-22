"""
Extensions Plugin Registration Module

This module handles the registration of the Extensions plugin with the core application.
"""

from lg import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api import PluginAPI

__version__ = "1.0.0"
__plugin_name__ = "Extensions"
__plugin_description__ = "Plugin management and extension system"


def register(api: 'PluginAPI') -> None:
    """
    Register the Extensions plugin with the core application.
    
    Args:
        api: Plugin API interface for interacting with the core
    """
    logger.info(f"Registering {__plugin_name__} plugin")
    
    try:
        # Import panel class
        from .extensions_panel import ExtensionsPanel
        
        # Create panel instance
        panel = ExtensionsPanel()
        
        # Get icon from icon manager
        icon_manager = api.get_icon_manager()
        icon = icon_manager.get_icon('extensions_active')
        
        # Register with sidebar
        api.add_sidebar_panel('extensions', panel, icon, __plugin_name__)
        
        # Register commands
        api.register_command('extensions.refresh', panel.refresh_plugins)
        api.register_command('extensions.install', panel.install_plugin)
        api.register_command('extensions.uninstall', panel.uninstall_plugin)
        
        logger.info(f"{__plugin_name__} plugin registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register {__plugin_name__} plugin: {e}")
        raise
