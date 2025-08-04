"""
Account Plugin Registration Module

This module handles the registration of the Account plugin with the core application.
"""

from lg import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api import PluginAPI

__version__ = "1.0.0"
__plugin_name__ = "Account"
__plugin_description__ = "User account management and authentication"


def register(api: 'PluginAPI') -> None:
    """
    Register the Account plugin with the core application.

    Args:
        api: Plugin API interface for interacting with the core
    """
    logger.info(f"Registering {__plugin_name__} plugin")

    try:
        # Import panel class
        from .account_panel import AccountPanel

        # Create panel instance
        panel = AccountPanel()

        # Get icon from icon manager
        icon_manager = api.get_icon_manager()
        icon = icon_manager.get_icon('account_active')

        # Register with sidebar
        api.add_sidebar_panel('account', panel, icon, __plugin_name__)

        # Register commands
        api.register_command('account.login', panel.show_login)
        api.register_command('account.logout', panel.logout)
        api.register_command('account.profile', panel.show_profile)

        logger.info(f"{__plugin_name__} plugin registered successfully")

    except Exception as e:
        logger.error(f"Failed to register {__plugin_name__} plugin: {e}")
        raise
