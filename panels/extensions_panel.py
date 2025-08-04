"""
Extensions panel for POEditor.

Provides management of plugins and extensions.
"""

from typing import Optional
from PySide6.QtWidgets import QVBoxLayout, QLabel

from panels.panel_interface import PanelInterface
from lg import logger


class ExtensionsPanel(PanelInterface):
    """Extensions panel for managing plugins and extensions."""

    def __init__(self, parent: Optional[PanelInterface] = None):
        super().__init__(parent)
        self._setup_ui()
        logger.info("ExtensionsPanel initialized")

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Placeholder content
        label = QLabel("Extensions Panel\n\nThis is a placeholder for the Extensions panel.")
        layout.addWidget(label)

        # Set layout properties
        layout.setContentsMargins(10, 10, 10, 10)

    def on_activate(self):
        """Called when the panel is activated."""
        super().on_activate()
        logger.debug("Extensions panel activated")

    def on_deactivate(self):
        """Called when the panel is deactivated."""
        super().on_deactivate()
        logger.debug("Extensions panel deactivated")
