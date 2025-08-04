"""
Core activity definitions for the application.

This module defines the standard activity configurations that are
available in the main application.
"""

from lg import logger
from models.activity_models import ActivityConfig

# Core Activities
EXPLORER_ACTIVITY = ActivityConfig(
    id="explorer",
    icon="📁",
    tooltip="Explorer",
    panel_class="ExplorerPanel",
    keyboard_shortcut="Ctrl+Shift+E",
    position=0
)

SEARCH_ACTIVITY = ActivityConfig(
    id="search",
    icon="🔍",
    tooltip="Search",
    panel_class="SearchPanel",
    keyboard_shortcut="Ctrl+Shift+F",
    position=1
)

PREFERENCES_ACTIVITY = ActivityConfig(
    id="preferences",
    icon="⚙️",
    tooltip="Preferences",
    panel_class="PreferencesPanel",
    keyboard_shortcut="Ctrl+,",
    position=2
)

EXTENSIONS_ACTIVITY = ActivityConfig(
    id="extensions",
    icon="🧩",
    tooltip="Extensions",
    panel_class="ExtensionsPanel",
    keyboard_shortcut="Ctrl+Shift+X",
    position=3
)

# Bottom Area Activities
ACCOUNT_ACTIVITY = ActivityConfig(
    id="account",
    icon="👤",
    tooltip="Account",
    panel_class="AccountPanel",
    keyboard_shortcut=None,
    position=100,
    area="bottom"
)

# List of all core activities
CORE_ACTIVITIES = [
    EXPLORER_ACTIVITY,
    SEARCH_ACTIVITY,
    PREFERENCES_ACTIVITY,
    EXTENSIONS_ACTIVITY,
    ACCOUNT_ACTIVITY
]

def register_core_activities(activity_manager):
    """Register all core activities with the activity manager.

    Args:
        activity_manager: The ActivityManager instance
    """
    for activity in CORE_ACTIVITIES:
        activity_manager.register_activity(activity)
        logger.info(f"Registered core activity: {activity.id}")
