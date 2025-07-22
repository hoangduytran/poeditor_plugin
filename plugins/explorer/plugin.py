"""
Explorer Plugin Registration

This module registers the explorer plugin with the main application.
"""

from lg import logger


def register(api):
    """
    Register the explorer plugin with the application.
    
    Args:
        api: PluginAPI instance for registering panels and commands
    """
    try:
        from .explorer_panel import ExplorerPanel
        from services.icon_manager import icon_manager
        
        # Create the explorer panel
        explorer_panel = ExplorerPanel()
        
        # Get the explorer icon
        icon = icon_manager.get_icon("explorer_active")
        
        # Register the panel with the sidebar
        api.add_sidebar_panel(
            panel_id="explorer",
            widget=explorer_panel,
            icon=icon,
            title="Explorer"
        )
        
        logger.info("Explorer plugin registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register explorer plugin: {e}")
        raise
