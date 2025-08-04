"""
Panel interface for sidebar panels.

All sidebar panels should implement this interface.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class PanelInterface(QWidget):
    """Base interface for all sidebar panels."""

    # Signals
    panel_activated = Signal()
    panel_deactivated = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the panel interface."""
        super().__init__(parent)
        self._api = None

    def set_api(self, api):
        """Set the plugin API instance."""
        self._api = api

    def on_activate(self):
        """Called when the panel is activated (shown)."""
        self.panel_activated.emit()

    def on_deactivate(self):
        """Called when the panel is deactivated (hidden)."""
        self.panel_deactivated.emit()

    def on_theme_changed(self, theme_name: str):
        """Called when the theme changes."""
        pass

    def on_typography_changed(self):
        """Called when the typography changes."""
        pass
