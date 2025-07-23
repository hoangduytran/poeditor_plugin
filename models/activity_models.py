"""
Activity Bar data models.

This module defines the data models used by the ActivityBar and ActivityManager components.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ActivityConfig:
    """Configuration for an Activity in the ActivityBar.
    
    Attributes:
        id: Unique identifier for the activity
        icon: Icon text (emoji) or path to icon file
        tooltip: Tooltip text shown on hover
        panel_class: Name of the panel class to instantiate
        keyboard_shortcut: Keyboard shortcut to activate this activity
        position: Position in the ActivityBar (lower numbers at top)
        area: Area in the ActivityBar ("main" or "bottom")
        badge_count: Number to show on badge (0 for no badge)
        enabled: Whether this activity is currently enabled
    """
    id: str
    icon: str
    tooltip: str
    panel_class: str
    keyboard_shortcut: Optional[str] = None
    position: int = 0
    area: str = "main"  # "main" or "bottom"
    badge_count: int = 0
    enabled: bool = True


@dataclass
class ActivityState:
    """Persistent state of the ActivityBar.
    
    Attributes:
        active_activity: ID of currently active activity
        panel_width: Width of the sidebar panel in pixels
        panel_visible: Whether the panel is currently visible
        activity_positions: Custom positions for activities
    """
    active_activity: str = "explorer"
    panel_width: int = 300
    panel_visible: bool = True
    activity_positions: Dict[str, int] = field(default_factory=dict)


# Default activities
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

ACCOUNT_ACTIVITY = ActivityConfig(
    id="account",
    icon="👤",
    tooltip="Account",
    panel_class="AccountPanel",
    keyboard_shortcut=None,
    position=100,
    area="bottom"
)

# Default configuration
DEFAULT_ACTIVITY_CONFIG = {
    "visible": True,
    "width": 48,
    "position": "left",
    "auto_hide": False,
    "show_badges": True,
    "animation_enabled": True,
    "active_activities": ["explorer", "search", "preferences", "extensions"],
    "activity_order": {
        "explorer": 0,
        "search": 1,
        "preferences": 2,
        "extensions": 3,
        "account": 100
    }
}
