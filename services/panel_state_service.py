"""
Panel State Management Service for POEditor application.

Provides persistent state management for all sidebar panels using QSettings.
Supports directory history, search patterns, and panel-specific settings.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtCore import QSettings
from lg import logger


class PanelStateManager:
    """Base class for managing panel state persistence using QSettings."""

    def __init__(self, panel_id: str):
        """
        Initialize panel state manager.

        Args:
            panel_id: Unique identifier for the panel (e.g., 'explorer', 'search')
        """
        self.panel_id = panel_id
        self.settings = QSettings("POEditor", "PanelStates")
        self._cache = {}  # In-memory cache for frequently accessed settings
        logger.info(f"PanelStateManager initialized for panel: {panel_id}")

    def save_state(self, state_data: Dict[str, Any]) -> None:
        """
        Save complete panel state to persistent storage.

        Args:
            state_data: Dictionary containing all panel state data
        """
        try:
            self.settings.beginGroup(self.panel_id)

            for key, value in state_data.items():
                self.settings.setValue(key, value)
                self._cache[key] = value

            self.settings.endGroup()
            self.settings.sync()

            logger.debug(f"Saved state for panel {self.panel_id}: {len(state_data)} settings")

        except Exception as e:
            logger.error(f"Failed to save state for panel {self.panel_id}: {e}")

    def load_state(self) -> Dict[str, Any]:
        """
        Load complete panel state from persistent storage.

        Returns:
            Dictionary containing all saved panel state data
        """
        try:
            state_data = {}
            self.settings.beginGroup(self.panel_id)

            for key in self.settings.childKeys():
                value = self.settings.value(key)
                state_data[key] = value
                self._cache[key] = value

            self.settings.endGroup()

            logger.debug(f"Loaded state for panel {self.panel_id}: {len(state_data)} settings")
            return state_data

        except Exception as e:
            logger.error(f"Failed to load state for panel {self.panel_id}: {e}")
            return {}

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value with caching.

        Args:
            key: Setting key name
            default: Default value if setting doesn't exist

        Returns:
            Setting value or default
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        try:
            full_key = f"{self.panel_id}/{key}"
            value = self.settings.value(full_key, default)
            self._cache[key] = value
            return value

        except Exception as e:
            logger.error(f"Failed to get setting {key} for panel {self.panel_id}: {e}")
            return default

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting value with immediate persistence.

        Args:
            key: Setting key name
            value: Setting value
        """
        try:
            full_key = f"{self.panel_id}/{key}"
            self.settings.setValue(full_key, value)
            self.settings.sync()
            self._cache[key] = value

            logger.debug(f"Set setting {key} = {value} for panel {self.panel_id}")

        except Exception as e:
            logger.error(f"Failed to set setting {key} for panel {self.panel_id}: {e}")

    def clear_state(self) -> None:
        """Clear all state data for this panel."""
        try:
            self.settings.beginGroup(self.panel_id)
            self.settings.remove("")  # Remove all keys in this group
            self.settings.endGroup()
            self.settings.sync()
            self._cache.clear()

            logger.info(f"Cleared all state for panel {self.panel_id}")

        except Exception as e:
            logger.error(f"Failed to clear state for panel {self.panel_id}: {e}")

    def has_setting(self, key: str) -> bool:
        """
        Check if a setting exists.

        Args:
            key: Setting key name

        Returns:
            True if setting exists, False otherwise
        """
        full_key = f"{self.panel_id}/{key}"
        return self.settings.contains(full_key)


class ExplorerStateManager(PanelStateManager):
    """Manages Explorer panel state persistence including directory history and navigation."""

    def __init__(self):
        super().__init__("explorer")
        self.max_history_entries = 50
        self.max_recent_locations = 20

    # Directory Location Management
    def save_current_location(self, path: str) -> None:
        """Save the current directory location."""
        self.set_setting("current_location", path)
        logger.debug(f"Saved current location: {path}")

    def load_current_location(self) -> Optional[str]:
        """Load the last saved directory location."""
        location = self.get_setting("current_location")
        if location:
            logger.debug(f"Loaded current location: {location}")
        return location

    # Directory History Management
    def save_location_history(self, history: List[str]) -> None:
        """Save directory navigation history."""
        # Limit history size
        limited_history = history[-self.max_history_entries:] if len(history) > self.max_history_entries else history
        self.set_setting("location_history", limited_history)
        logger.debug(f"Saved location history: {len(limited_history)} entries")

    def load_location_history(self) -> List[str]:
        """Load directory navigation history."""
        history = self.get_setting("location_history", [])
        # Ensure it's a list
        if not isinstance(history, list):
            history = []
        logger.debug(f"Loaded location history: {len(history)} entries")
        return history

    def save_history_index(self, index: int) -> None:
        """Save current position in history."""
        self.set_setting("history_index", index)

    def load_history_index(self) -> int:
        """Load current position in history."""
        return self.get_setting("history_index", -1)

    # Recent Locations Management
    def add_recent_location(self, path: str) -> None:
        """Add a location to recent locations list."""
        recent = self.get_recent_locations()

        # Remove if already exists
        if path in recent:
            recent.remove(path)

        # Add to beginning
        recent.insert(0, path)

        # Limit size
        recent = recent[:self.max_recent_locations]

        self.set_setting("recent_locations", recent)
        logger.debug(f"Added recent location: {path}")

    def get_recent_locations(self) -> List[str]:
        """Get list of recent locations."""
        recent = self.get_setting("recent_locations", [])
        if not isinstance(recent, list):
            recent = []
        return recent

    # View Settings Management
    def save_view_settings(self, settings: Dict[str, Any]) -> None:
        """Save explorer view settings."""
        self.set_setting("view_settings", settings)
        logger.debug(f"Saved view settings: {settings}")

    def load_view_settings(self) -> Dict[str, Any]:
        """Load explorer view settings."""
        settings = self.get_setting("view_settings", {})
        if not isinstance(settings, dict):
            settings = {}
        return settings

    # Search History in Explorer
    def save_search_history(self, history: List[str]) -> None:
        """Save explorer search history."""
        limited_history = history[-self.max_history_entries:] if len(history) > self.max_history_entries else history
        self.set_setting("search_history", limited_history)
        logger.debug(f"Saved explorer search history: {len(limited_history)} entries")

    def load_search_history(self) -> List[str]:
        """Load explorer search history."""
        history = self.get_setting("search_history", [])
        if not isinstance(history, list):
            history = []
        return history


class SearchStateManager(PanelStateManager):
    """Manages Search panel state persistence including search patterns and options."""

    def __init__(self):
        super().__init__("search")
        self.max_pattern_history = 50

    # Search Pattern History
    def save_search_history(self, history: List[str]) -> None:
        """Save search pattern history."""
        limited_history = history[-self.max_pattern_history:] if len(history) > self.max_pattern_history else history
        self.set_setting("pattern_history", limited_history)
        logger.debug(f"Saved search pattern history: {len(limited_history)} entries")

    def load_search_history(self) -> List[str]:
        """Load search pattern history."""
        history = self.get_setting("pattern_history", [])
        if not isinstance(history, list):
            history = []
        return history

    def add_search_pattern(self, pattern: str) -> None:
        """Add a search pattern to history."""
        if not pattern.strip():
            return

        history = self.load_search_history()

        # Remove if already exists
        if pattern in history:
            history.remove(pattern)

        # Add to end (most recent)
        history.append(pattern)

        # Save updated history
        self.save_search_history(history)
        logger.debug(f"Added search pattern: {pattern}")

    def get_search_pattern_at_index(self, index: int) -> Optional[str]:
        """Get search pattern at specific index."""
        history = self.load_search_history()
        if 0 <= index < len(history):
            return history[index]
        return None

    # Search Options
    def save_search_options(self, options: Dict[str, Any]) -> None:
        """Save search options (case sensitive, regex, etc.)."""
        self.set_setting("search_options", options)
        logger.debug(f"Saved search options: {options}")

    def load_search_options(self) -> Dict[str, Any]:
        """Load search options."""
        options = self.get_setting("search_options", {})
        if not isinstance(options, dict):
            options = {}
        return options

    # Current Search State
    def save_current_pattern(self, pattern: str) -> None:
        """Save current search pattern."""
        self.set_setting("current_pattern", pattern)

    def load_current_pattern(self) -> str:
        """Load current search pattern."""
        return self.get_setting("current_pattern", "")

    def save_history_index(self, index: int) -> None:
        """Save current position in search history."""
        self.set_setting("history_index", index)

    def load_history_index(self) -> int:
        """Load current position in search history."""
        return self.get_setting("history_index", -1)


class PanelStateService:
    """Central service for managing all panel states."""

    def __init__(self):
        """Initialize the panel state service."""
        self.state_managers = {
            'explorer': ExplorerStateManager(),
            'search': SearchStateManager(),
            # Add other panel managers as needed
        }
        logger.info("PanelStateService initialized")

    def get_manager(self, panel_id: str) -> Optional[PanelStateManager]:
        """Get state manager for a specific panel."""
        return self.state_managers.get(panel_id)

    def save_all_states(self) -> None:
        """Save states for all panels."""
        try:
            for panel_id, manager in self.state_managers.items():
                # Each manager handles its own state saving
                logger.debug(f"State manager for {panel_id} ready for save operations")
            logger.info("All panel states ready for saving")

        except Exception as e:
            logger.error(f"Failed to save all panel states: {e}")

    def clear_all_states(self) -> None:
        """Clear states for all panels."""
        try:
            for panel_id, manager in self.state_managers.items():
                manager.clear_state()
            logger.info("Cleared all panel states")

        except Exception as e:
            logger.error(f"Failed to clear all panel states: {e}")


# Global instance
panel_state_service = PanelStateService()
