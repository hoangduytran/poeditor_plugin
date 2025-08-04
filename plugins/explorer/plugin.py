"""
Explorer Plugin for POEditor application.

This plugin provides file and directory exploration capabilities
using the clean architecture from Phase 1.
"""

from lg import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api import PluginAPI

__version__ = "1.0.0"
__plugin_name__ = "Explorer"
__plugin_description__ = "File and directory explorer with filtering capabilities"


def register(api: 'PluginAPI') -> None:
    """
    Register the Explorer plugin with the core application.

    Args:
        api: Plugin API interface for interacting with the core
    """
    logger.info(f"Registering {__plugin_name__} plugin")

    try:
        # Import panel class
        from .explorer_panel import ExplorerPanel

        # Create panel instance
        panel = ExplorerPanel()

        # Get icon from icon manager
        icon_manager = api.get_icon_manager()
        icon = icon_manager.get_icon('explorer_active')

        # Register with sidebar
        api.add_sidebar_panel('explorer', panel, icon, __plugin_name__)

        # Register commands
        api.register_command('explorer.refresh', panel.refresh)
        api.register_command('explorer.show_hidden', panel.toggle_hidden_files)
        api.register_command('explorer.set_filter', panel.set_filter_pattern)

        logger.info(f"{__plugin_name__} plugin registered successfully")

    except Exception as e:
        logger.error(f"Failed to register {__plugin_name__} plugin: {e}")
        raise
