"""
Directory and Search History Management for POEditor panels.

Provides navigation history functionality with prev/next capabilities and
keyboard navigation for search patterns.
"""

from typing import List, Optional
from PySide6.QtCore import Qt
from lg import logger


class DirectoryHistory:
    """Manages directory navigation history with prev/next functionality."""

    def __init__(self, state_manager):
        """
        Initialize directory history manager.

        Args:
            state_manager: ExplorerStateManager instance for persistence
        """
        self.state_manager = state_manager
        self.history = []
        self.current_index = -1
        self.max_history = 50
        self.load_from_settings()
        logger.debug(f"DirectoryHistory initialized with {len(self.history)} entries")

    def add_location(self, path: str) -> None:
        """
        Add a new location to history.

        Args:
            path: Directory path to add
        """
        if not path:
            return

        # If we're not at the end of history, remove everything after current position
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        # Don't add duplicate consecutive entries
        if self.history and self.history[-1] == path:
            return

        # Add new location
        self.history.append(path)
        self.current_index = len(self.history) - 1

        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.current_index = len(self.history) - 1

        self.save_to_settings()
        logger.debug(f"Added location to history: {path} (index: {self.current_index})")

    def can_go_back(self) -> bool:
        """Check if we can navigate back in history."""
        return self.current_index > 0

    def can_go_forward(self) -> bool:
        """Check if we can navigate forward in history."""
        return self.current_index < len(self.history) - 1

    def go_back(self) -> Optional[str]:
        """
        Navigate to previous location in history.

        Returns:
            Previous directory path or None if can't go back
        """
        if not self.can_go_back():
            return None

        self.current_index -= 1
        path = self.history[self.current_index]
        self.save_to_settings()

        logger.debug(f"Navigated back to: {path} (index: {self.current_index})")
        return path

    def go_forward(self) -> Optional[str]:
        """
        Navigate to next location in history.

        Returns:
            Next directory path or None if can't go forward
        """
        if not self.can_go_forward():
            return None

        self.current_index += 1
        path = self.history[self.current_index]
        self.save_to_settings()

        logger.debug(f"Navigated forward to: {path} (index: {self.current_index})")
        return path

    def get_current_location(self) -> Optional[str]:
        """Get current location in history."""
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None

    def get_history_list(self) -> List[str]:
        """Get complete history list."""
        return self.history.copy()

    def save_to_settings(self) -> None:
        """Save history to persistent storage."""
        try:
            self.state_manager.save_location_history(self.history)
            self.state_manager.save_history_index(self.current_index)

        except Exception as e:
            logger.error(f"Failed to save directory history: {e}")

    def load_from_settings(self) -> None:
        """Load history from persistent storage."""
        try:
            self.history = self.state_manager.load_location_history()
            self.current_index = self.state_manager.load_history_index()

            # Validate index
            if self.current_index >= len(self.history):
                self.current_index = len(self.history) - 1
            if self.current_index < -1:
                self.current_index = -1

            logger.debug(f"Loaded directory history: {len(self.history)} entries, index: {self.current_index}")

        except Exception as e:
            logger.error(f"Failed to load directory history: {e}")
            self.history = []
            self.current_index = -1


class SearchHistory:
    """Manages search pattern history with keyboard navigation (Ctrl+Up/Down)."""

    def __init__(self, state_manager):
        """
        Initialize search history manager.

        Args:
            state_manager: SearchStateManager instance for persistence
        """
        self.state_manager = state_manager
        self.patterns = []
        self.current_index = -1  # -1 means no pattern selected
        self.max_patterns = 50
        self.load_from_settings()
        logger.debug(f"SearchHistory initialized with {len(self.patterns)} patterns")

    def add_pattern(self, pattern: str) -> None:
        """
        Add a new search pattern to history.

        Args:
            pattern: Search pattern to add
        """
        if not pattern or not pattern.strip():
            return

        pattern = pattern.strip()

        # Remove if already exists
        if pattern in self.patterns:
            self.patterns.remove(pattern)

        # Add to end (most recent)
        self.patterns.append(pattern)

        # Limit size
        if len(self.patterns) > self.max_patterns:
            self.patterns = self.patterns[-self.max_patterns:]

        # Reset index to indicate no selection
        self.current_index = -1

        self.save_to_settings()
        logger.debug(f"Added search pattern: {pattern}")

    def get_previous_pattern(self) -> Optional[str]:
        """
        Get previous pattern in history (Ctrl+Up equivalent).

        Returns:
            Previous search pattern or None if at beginning
        """
        if not self.patterns:
            return None

        # If no pattern selected, start from the end
        if self.current_index == -1:
            self.current_index = len(self.patterns) - 1
        # Move to previous pattern
        elif self.current_index > 0:
            self.current_index -= 1
        else:
            # Already at first pattern
            return None

        pattern = self.patterns[self.current_index]
        self.save_index_to_settings()

        logger.debug(f"Retrieved previous pattern: {pattern} (index: {self.current_index})")
        return pattern

    def get_next_pattern(self) -> Optional[str]:
        """
        Get next pattern in history (Ctrl+Down equivalent).

        Returns:
            Next search pattern or None if at end
        """
        if not self.patterns or self.current_index == -1:
            return None

        # Move to next pattern
        if self.current_index < len(self.patterns) - 1:
            self.current_index += 1
            pattern = self.patterns[self.current_index]
            self.save_index_to_settings()

            logger.debug(f"Retrieved next pattern: {pattern} (index: {self.current_index})")
            return pattern
        else:
            # At end, clear selection
            self.current_index = -1
            self.save_index_to_settings()
            logger.debug("Cleared pattern selection (at end of history)")
            return ""

    def handle_key_navigation(self, key: Qt.Key, modifiers: Qt.KeyboardModifier) -> Optional[str]:
        """
        Handle keyboard navigation for search history.

        Args:
            key: Pressed key
            modifiers: Keyboard modifiers (Ctrl, Alt, etc.)

        Returns:
            Pattern to set in search field or None if no change
        """
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Up:
                return self.get_previous_pattern()
            elif key == Qt.Key.Key_Down:
                return self.get_next_pattern()

        return None

    def reset_index(self) -> None:
        """Reset current index to indicate no pattern selected."""
        self.current_index = -1
        self.save_index_to_settings()

    def get_all_patterns(self) -> List[str]:
        """Get all search patterns."""
        return self.patterns.copy()

    def get_current_pattern(self) -> Optional[str]:
        """Get currently selected pattern."""
        if 0 <= self.current_index < len(self.patterns):
            return self.patterns[self.current_index]
        return None

    def save_to_settings(self) -> None:
        """Save search history to persistent storage."""
        try:
            self.state_manager.save_search_history(self.patterns)
            self.save_index_to_settings()

        except Exception as e:
            logger.error(f"Failed to save search history: {e}")

    def save_index_to_settings(self) -> None:
        """Save current index to settings."""
        try:
            self.state_manager.save_history_index(self.current_index)

        except Exception as e:
            logger.error(f"Failed to save search history index: {e}")

    def load_from_settings(self) -> None:
        """Load search history from persistent storage."""
        try:
            self.patterns = self.state_manager.load_search_history()
            self.current_index = self.state_manager.load_history_index()

            # Validate index
            if self.current_index >= len(self.patterns):
                self.current_index = -1
            if self.current_index < -1:
                self.current_index = -1

            logger.debug(f"Loaded search history: {len(self.patterns)} patterns, index: {self.current_index}")

        except Exception as e:
            logger.error(f"Failed to load search history: {e}")
            self.patterns = []
            self.current_index = -1
