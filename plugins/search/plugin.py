"""
Search Plugin Registration Module

This module handles the registration of the Search plugin with the core application.
"""

from lg import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api import PluginAPI

__version__ = "1.0.0"
__plugin_name__ = "Search"
__plugin_description__ = "Advanced file and content search with pattern matching"


def register(api: 'PluginAPI') -> None:
    """
    Register the Search plugin with the core application.

    Args:
        api: Plugin API interface for interacting with the core
    """
    logger.info(f"Registering {__plugin_name__} plugin")

    try:
        # Import panel class
        from .search_panel import SearchPanel

        # Create panel instance
        panel = SearchPanel()

        # Get icon from icon manager
        icon_manager = api.get_icon_manager()
        icon = icon_manager.get_icon('search_active')

        # Register with sidebar
        api.add_sidebar_panel('search', panel, icon, __plugin_name__)

        # Register commands
        api.register_command('search.find', panel.start_search)
        api.register_command('search.clear', panel.clear_results)
        api.register_command('search.find_in_files', panel.find_in_files)

        logger.info(f"{__plugin_name__} plugin registered successfully")

    except Exception as e:
        logger.error(f"Failed to register {__plugin_name__} plugin: {e}")
        raise
