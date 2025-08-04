"""
Explorer panel for POEditor.

Provides file and directory navigation functionality using the SimpleExplorerWidget.
"""

from typing import Optional
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Signal

from panels.panel_interface import PanelInterface
from widgets.simple_explorer_widget import SimpleExplorerWidget
from lg import logger


class ExplorerPanel(PanelInterface):
    """Explorer panel for navigating files and directories."""

    # Signals
    file_opened = Signal(str)
    location_changed = Signal(str)

    def __init__(self, parent: Optional[PanelInterface] = None):
        super().__init__(parent)
        self._setup_ui()
        logger.info("ExplorerPanel initialized")

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for clean look

        # Add the simple explorer widget
        self.explorer_widget = SimpleExplorerWidget()
        layout.addWidget(self.explorer_widget)

        # Connect explorer signals to panel signals
        self.explorer_widget.file_opened.connect(self.file_opened.emit)
        self.explorer_widget.location_changed.connect(self.location_changed.emit)

    def on_activate(self):
        """Called when the panel is activated."""
        super().on_activate()
        logger.debug("Explorer panel activated")
        # Optionally refresh the explorer when activated

    def on_deactivate(self):
        """Called when the panel is deactivated."""
        super().on_deactivate()
        logger.debug("Explorer panel deactivated")

    def navigate_to(self, path: str) -> bool:
        """Navigate the explorer to a specific directory."""
        self.explorer_widget.set_current_path(path)
        return True

    def get_current_directory(self) -> str:
        """Get the current directory path."""
        return self.explorer_widget.get_current_path()
