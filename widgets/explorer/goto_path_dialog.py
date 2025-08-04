"""
Go to Path Dialog

This dialog allows users to navigate to a specific path with auto-completion
and validation. Integrates with the PathCompletionService for real-time
path suggestions.
"""

import os
import logging
from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QFrame,
    QDialogButtonBox, QCompleter, QFileSystemModel, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QDir, QThread
from PySide6.QtGui import QFont, QIcon

from services.path_completion_service import PathCompletionService
from services.navigation_history_service import NavigationHistoryService

logger = logging.getLogger(__name__)


class PathCompletionThread(QThread):
    """Background thread for path completion to avoid UI blocking."""

    completion_ready = Signal(list)

    def __init__(self, path: str, completion_service: PathCompletionService):
        super().__init__()
        self.path = path
        self.completion_service = completion_service

    def run(self):
        """Run path completion in background."""
        try:
            completions = self.completion_service.get_quick_completions(self.path)
            # Extract just the path strings from the completion dictionaries
            paths = [comp.get('path', comp.get('text', '')) for comp in completions if comp]
            self.completion_ready.emit(paths)
        except Exception as e:
            logger.error(f"Path completion error: {e}")
            self.completion_ready.emit([])


class GotoPathDialog(QDialog):
    """
    Dialog for navigating to a specific path with auto-completion.

    Features:
    - Real-time path completion
    - Recent paths dropdown
    - Path validation
    - Keyboard navigation
    """

    path_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None,
                 completion_service: Optional[PathCompletionService] = None,
                 history_service: Optional[NavigationHistoryService] = None):
        """Initialize the goto path dialog."""
        super().__init__(parent)

        self.completion_service = completion_service
        self.history_service = history_service
        self.completion_thread = None

        self._setup_ui()
        self._setup_connections()
        self._load_recent_paths()

        # Auto-resize
        self.resize(500, 300)

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self.setWindowTitle("Go to Path")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title and instruction
        title_label = QLabel("Go to Path")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        instruction_label = QLabel("Enter a path to navigate to:")
        layout.addWidget(instruction_label)

        # Path input section
        path_layout = QVBoxLayout()

        # Path input field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter path (e.g., /Users/username/Documents)")
        path_layout.addWidget(self.path_input)

        # Completion list
        self.completion_list = QListWidget()
        self.completion_list.setMaximumHeight(150)
        self.completion_list.hide()  # Initially hidden
        path_layout.addWidget(self.completion_list)

        layout.addLayout(path_layout)

        # Recent paths section
        recent_frame = QFrame()
        recent_frame.setFrameStyle(QFrame.Shape.Box)
        recent_layout = QVBoxLayout(recent_frame)

        recent_label = QLabel("Recent Paths:")
        recent_font = QFont()
        recent_font.setBold(True)
        recent_label.setFont(recent_font)
        recent_layout.addWidget(recent_label)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(100)
        recent_layout.addWidget(self.recent_list)

        layout.addWidget(recent_frame)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)  # Disabled until valid path entered
        layout.addWidget(button_box)

        # Store references
        self.button_box = button_box

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Path input changes
        self.path_input.textChanged.connect(self._on_path_changed)
        self.path_input.returnPressed.connect(self._accept_current_path)

        # Completion list
        self.completion_list.itemClicked.connect(self._on_completion_selected)
        self.completion_list.itemActivated.connect(self._on_completion_selected)

        # Recent paths list
        self.recent_list.itemClicked.connect(self._on_recent_selected)
        self.recent_list.itemActivated.connect(self._on_recent_selected)

        # Button box
        self.button_box.accepted.connect(self._accept_current_path)
        self.button_box.rejected.connect(self.reject)

        # Timer for debounced completion
        self.completion_timer = QTimer()
        self.completion_timer.setSingleShot(True)
        self.completion_timer.timeout.connect(self._trigger_completion)

    def _load_recent_paths(self) -> None:
        """Load recent paths from history service."""
        if not self.history_service:
            return

        try:
            recent_locations = self.history_service.get_recent_locations(limit=10)

            for location in recent_locations:
                path = location.get('path', '')
                if path and os.path.exists(path):
                    item = QListWidgetItem(path)
                    item.setToolTip(f"Last visited: {location.get('timestamp', 'Unknown')}")
                    self.recent_list.addItem(item)

        except Exception as e:
            logger.error(f"Error loading recent paths: {e}")

    def _on_path_changed(self, text: str) -> None:
        """Handle path input changes."""
        # Validate path and enable/disable OK button
        is_valid = self._validate_path(text)
        self.ok_button.setEnabled(is_valid)

        # Trigger completion with delay
        if text.strip() and self.completion_service:
            self.completion_timer.stop()
            self.completion_timer.start(300)  # 300ms delay
        else:
            self.completion_list.hide()

    def _validate_path(self, path: str) -> bool:
        """Validate if the path exists and is accessible."""
        if not path.strip():
            return False

        try:
            expanded_path = os.path.expanduser(path.strip())
            return os.path.exists(expanded_path)
        except Exception:
            return False

    def _trigger_completion(self) -> None:
        """Trigger path completion in background thread."""
        path = self.path_input.text().strip()
        if not path or not self.completion_service:
            return

        # Stop any existing completion thread
        if self.completion_thread and self.completion_thread.isRunning():
            self.completion_thread.quit()
            self.completion_thread.wait()

        # Start new completion thread
        self.completion_thread = PathCompletionThread(path, self.completion_service)
        self.completion_thread.completion_ready.connect(self._show_completions)
        self.completion_thread.start()

    def _show_completions(self, completions: List[str]) -> None:
        """Show completion results."""
        self.completion_list.clear()

        if completions:
            for completion in completions:
                item = QListWidgetItem(completion)
                self.completion_list.addItem(item)
            self.completion_list.show()
        else:
            self.completion_list.hide()

    def _on_completion_selected(self, item: QListWidgetItem) -> None:
        """Handle completion selection."""
        path = item.text()
        self.path_input.setText(path)
        self.completion_list.hide()
        self.path_input.setFocus()

    def _on_recent_selected(self, item: QListWidgetItem) -> None:
        """Handle recent path selection."""
        path = item.text()
        self.path_input.setText(path)
        self.path_input.setFocus()

    def _accept_current_path(self) -> None:
        """Accept the current path if valid."""
        path = self.path_input.text().strip()
        if self._validate_path(path):
            expanded_path = os.path.expanduser(path)
            self.path_selected.emit(expanded_path)
            self.accept()
        else:
            # Show error feedback
            self.path_input.setStyleSheet("QLineEdit { border: 2px solid red; }")
            QTimer.singleShot(2000, lambda: self.path_input.setStyleSheet(""))

    def get_selected_path(self) -> Optional[str]:
        """Get the selected path."""
        path = self.path_input.text().strip()
        if self._validate_path(path):
            return os.path.expanduser(path)
        return None

    def set_current_path(self, path: str) -> None:
        """Set the current path in the input field."""
        self.path_input.setText(path)
        self.path_input.selectAll()

    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.completion_list.isVisible() and self.completion_list.currentItem():
                self._on_completion_selected(self.completion_list.currentItem())
            else:
                self._accept_current_path()
        elif event.key() == Qt.Key.Key_Down and not self.completion_list.isVisible():
            # Focus recent list if no completions
            if self.recent_list.count() > 0:
                self.recent_list.setFocus()
                self.recent_list.setCurrentRow(0)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        """Handle dialog close event."""
        # Stop any running completion thread
        if self.completion_thread and self.completion_thread.isRunning():
            self.completion_thread.quit()
            self.completion_thread.wait()
        super().closeEvent(event)


def show_goto_path_dialog(parent: Optional[QWidget] = None,
                         current_path: str = "",
                         completion_service: Optional[PathCompletionService] = None,
                         history_service: Optional[NavigationHistoryService] = None) -> Optional[str]:
    """
    Show the goto path dialog and return the selected path.

    Args:
        parent: Parent widget
        current_path: Current path to pre-fill
        completion_service: Path completion service
        history_service: Navigation history service

    Returns:
        Selected path or None if cancelled
    """
    dialog = GotoPathDialog(parent, completion_service, history_service)

    if current_path:
        dialog.set_current_path(current_path)

    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        return dialog.get_selected_path()
    return None
