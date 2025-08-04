"""
Path Search Field Widget

Provides an intelligent path search field with:
- Real-time path completion
- Navigation history integration
- Path validation feedback
- Keyboard navigation support
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QLineEdit, QWidget, QCompleter, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt, QTimer, QStringListModel
from PySide6.QtGui import QKeyEvent, QPalette

from services.path_completion_service import PathCompletionService
from services.navigation_history_service import NavigationHistoryService


class PathSearchField(QLineEdit):
    """
    Intelligent path search field with auto-completion and validation.

    Features:
    - Real-time path completion as user types
    - Integration with navigation history for suggestions
    - Visual feedback for valid/invalid paths
    - Keyboard shortcuts for navigation

    Signals:
        path_entered: Emitted when user enters a path (path: str)
        path_validated: Emitted when path is validated (path: str, is_valid: bool)
    """

    # Signals
    path_entered = Signal(str)
    path_validated = Signal(str, bool)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the path search field.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Services (will be injected)
        self._completion_service: Optional[PathCompletionService] = None
        self._history_service: Optional[NavigationHistoryService] = None

        # UI components
        self._completer: Optional[QCompleter] = None
        self._completion_model = QStringListModel()

        # State
        self._validation_timer = QTimer()
        self._last_valid_path = ""
        self._is_path_valid = True

        # Setup UI
        self._setup_ui()
        self._setup_completer()
        self._setup_connections()
        self._setup_styles()

    def _setup_ui(self) -> None:
        """Setup the search field UI."""
        # Configure line edit
        self.setPlaceholderText("Enter path or start typing...")
        self.setClearButtonEnabled(True)
        self.setFixedHeight(28)

        # Set size policy
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _setup_completer(self) -> None:
        """Setup the auto-completion functionality."""
        self._completer = QCompleter(self._completion_model, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(10)

        # Configure popup
        popup = self._completer.popup()
        if popup:
            popup.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.setCompleter(self._completer)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Text change handling
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._on_return_pressed)

        # Validation timer (debounced validation)
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._validate_current_path)

        # Completer signals
        if self._completer:
            self._completer.activated.connect(self._on_completion_selected)

    def _setup_styles(self) -> None:
        """Setup widget styling."""
        self._update_validation_style(True)  # Start with valid style

    def inject_services(
        self,
        completion_service: PathCompletionService,
        history_service: NavigationHistoryService
    ) -> None:
        """
        Inject services for path completion and history.

        Args:
            completion_service: Path completion service
            history_service: Navigation history service
        """
        self._completion_service = completion_service
        self._history_service = history_service

        # Connect to completion service
        if self._completion_service:
            self._completion_service.completions_available.connect(self._on_completions_ready)

    def _on_text_changed(self, text: str) -> None:
        """
        Handle text change in the search field.

        Args:
            text: Current text in the field
        """
        # Start validation timer (debounced)
        self._validation_timer.start(300)  # 300ms delay

        # Request completions if we have a completion service
        if self._completion_service and text.strip():
            self._completion_service.request_completions(text.strip())

    def _on_return_pressed(self) -> None:
        """Handle Enter key press."""
        current_text = self.text().strip()
        if current_text:
            # Validate the path first
            is_valid = self._validate_path(current_text)
            if is_valid:
                self.path_entered.emit(current_text)
                # Add to history if we have history service
                if self._history_service:
                    # History service will handle this through navigation
                    pass
            else:
                # Show validation error (visual feedback already applied)
                pass

    def _on_completion_selected(self, completion: str) -> None:
        """
        Handle completion selection from dropdown.

        Args:
            completion: Selected completion text
        """
        # Update the text and trigger validation
        self.setText(completion)
        self._validate_current_path()

    def _on_completions_ready(self, query: str, completions: List[str]) -> None:
        """
        Handle completion results from the completion service.

        Args:
            query: The query that was completed
            completions: List of completion suggestions
        """
        # Only use completions if they match the current text
        current_text = self.text().strip()
        if query == current_text:
            # Update the completion model
            self._completion_model.setStringList(completions)

            # Show completions if we have any
            if completions and self._completer:
                self._completer.complete()

    def _validate_current_path(self) -> None:
        """Validate the current path and update UI accordingly."""
        current_text = self.text().strip()
        is_valid = self._validate_path(current_text)

        # Update validation state
        if self._is_path_valid != is_valid:
            self._is_path_valid = is_valid
            self._update_validation_style(is_valid)

        # Emit validation signal
        self.path_validated.emit(current_text, is_valid)

    def _validate_path(self, path: str) -> bool:
        """
        Validate a file system path.

        Args:
            path: Path to validate

        Returns:
            True if path is valid and accessible
        """
        if not path or not path.strip():
            return True  # Empty path is considered valid (no error state)

        try:
            from pathlib import Path
            path_obj = Path(path)

            # Check if path exists and is accessible
            return path_obj.exists() and path_obj.is_dir()
        except Exception:
            return False

    def _update_validation_style(self, is_valid: bool) -> None:
        """
        Update the visual style based on validation state.

        Args:
            is_valid: Whether the current path is valid
        """
        if is_valid:
            # Valid style - default appearance
            self.setStyleSheet("""
                QLineEdit {
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                    padding: 4px 8px;
                    background-color: palette(base);
                    selection-background-color: palette(highlight);
                }
                QLineEdit:focus {
                    border-color: palette(highlight);
                }
            """)
        else:
            # Invalid style - red border
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e74c3c;
                    border-radius: 4px;
                    padding: 3px 7px;
                    background-color: palette(base);
                    selection-background-color: palette(highlight);
                }
                QLineEdit:focus {
                    border-color: #c0392b;
                }
            """)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle key press events for keyboard navigation.

        Args:
            event: Key event
        """
        key = event.key()
        modifiers = event.modifiers()

        # Handle special key combinations
        if key == Qt.Key.Key_Escape:
            # Clear the field and reset validation
            self.clear()
            self._is_path_valid = True
            self._update_validation_style(True)
            return

        elif key == Qt.Key.Key_Tab:
            # Try to complete the current path
            if self._completer and self._completer.completionCount() > 0:
                completion = self._completer.currentCompletion()
                if completion:
                    self.setText(completion)
                    return

        # Handle default behavior
        super().keyPressEvent(event)

    def set_current_path(self, path: str) -> None:
        """
        Set the current path in the search field.

        Args:
            path: Path to display
        """
        self.setText(path)
        self._validate_current_path()

    def get_current_path(self) -> str:
        """
        Get the current path from the search field.

        Returns:
            Current path text
        """
        return self.text().strip()

    def is_valid_path(self) -> bool:
        """
        Check if the current path is valid.

        Returns:
            True if the current path is valid
        """
        return self._is_path_valid

    def clear_and_focus(self) -> None:
        """Clear the field and set focus for user input."""
        self.clear()
        self.setFocus()
        self._is_path_valid = True
        self._update_validation_style(True)
