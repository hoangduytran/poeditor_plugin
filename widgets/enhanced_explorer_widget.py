"""
Enhanced Explorer Widget with context menu support.

This extends the SimpleExplorerWidget to incorporate context menu functionality
and integration with file operations services.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from lg import logger
from core.explorer_settings import ExplorerSettings
from widgets.simple_explorer_widget import SimpleSearchBar
from widgets.enhanced_file_view import EnhancedFileView
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager
from services.file_numbering_service import FileNumberingService
from services.drag_drop_service import DragDropService
from services.column_manager_service import ColumnManagerService
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService


class EnhancedExplorerWidget(QWidget):
    """
    Enhanced explorer widget with context menu support.
    
    Features:
    - All features of SimpleExplorerWidget
    - Context menu support with file operations
    - Integration with undo/redo system
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = ExplorerSettings()
        
        # Create services
        self._create_services()
        
        # Initialize UI components
        self.search_bar = SimpleSearchBar()
        self.file_view = EnhancedFileView()
        self.path_label = QLabel("Initializing...")
        self.up_button = QPushButton("↑ Up")
        
        self._setup_ui()
        self._connect_signals()
        self._load_initial_state()
        
    def _create_services(self):
        """Create and initialize the required services."""
        # Create file numbering service
        self.file_numbering_service = FileNumberingService()
        
        # Create undo/redo manager
        self.undo_redo_manager = UndoRedoManager()
        
        # Create file operations service
        self.file_operations_service = FileOperationsService()
        
        # Create drag and drop service
        self.drag_drop_service = DragDropService(self.file_operations_service)
        
        # Create column manager service
        self.column_manager_service = ColumnManagerService()
        
        # Create navigation services
        self.navigation_service = NavigationService()
        self.history_service = NavigationHistoryService()
        self.location_manager = LocationManager()
        self.completion_service = PathCompletionService()
        
        # Set up navigation service dependencies
        self.navigation_service.set_dependencies(
            history_service=self.history_service,
            location_manager=self.location_manager
        )
        
        logger.debug("Explorer services initialized")
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Navigation button
        self.up_button.setToolTip("Go to parent directory")
        
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.up_button)
        nav_layout.addWidget(self.path_label, 1)  # Stretch the label
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.file_view, 1)  # Stretch the file view
        
        # Set up context menu with services
        self.file_view.setup_context_menu(
            self.file_operations_service,
            self.undo_redo_manager,
            self.column_manager_service,
            self.navigation_service,
            self.history_service,
            self.location_manager,
            self.completion_service
        )
        
    def _connect_signals(self):
        """Connect signals to slots."""
        self.up_button.clicked.connect(self._on_up_button_clicked)
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        self.file_view.file_activated.connect(self._on_file_activated)
        self.file_view.directory_changed.connect(self._on_directory_changed)
        
        # Update path label when directory changes
        self.file_view.directory_changed.connect(
            lambda path: self.path_label.setText(path)
        )
        
        # Connect file operations service signals
        self._connect_service_signals()
        
    def _connect_service_signals(self):
        """Connect signals from file operations service."""
        # Operation status signals
        self.file_operations_service.operationStarted.connect(self._on_operation_started)
        self.file_operations_service.operationCompleted.connect(self._on_operation_completed)
        self.file_operations_service.operationFailed.connect(self._on_operation_failed)
        
    def _load_initial_state(self):
        """Load the last visited path from settings."""
        import os
        from pathlib import Path
        
        last_path = self.settings.get("last_path")
        if last_path and os.path.isdir(last_path):
            self.file_view.set_current_path(last_path)
        else:
            # Fallback to home directory if last path is invalid
            self.file_view.set_current_path(str(Path.home()))
        
    def _on_up_button_clicked(self):
        """Handle the 'Up' button click."""
        current_path = self.file_view.get_current_path()
        import os
        parent_path = os.path.dirname(current_path)
        if parent_path and parent_path != current_path:
            self.file_view.set_current_path(parent_path)
            
    def _on_search_text_changed(self, text: str):
        """Handle search/filter text changes."""
        self.file_view.apply_filter(text)
        
    def _on_directory_changed(self, path: str):
        """Handle directory navigation."""
        self.settings.set("last_path", path)
        
    def _on_file_activated(self, path: str):
        """Handle file activation (double-click)."""
        # Open file with default application
        import os
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':  # Windows
                subprocess.Popen(['start', path], shell=True)
            else:  # Linux and other Unix
                subprocess.call(('xdg-open', path))
            logger.debug(f"Opened file: {path}")
        except Exception as e:
            logger.error(f"Failed to open file {path}: {e}")
        
    def _on_operation_started(self, operation_type, targets):
        """Handle operation started event."""
        logger.debug(f"Operation started: {operation_type} on {targets}")
        
    def _on_operation_completed(self, operation_type, targets, target_path):
        """Handle operation completed event."""
        logger.debug(f"Operation completed: {operation_type} on {targets} to {target_path}")
        # Refresh the view if needed
        
    def _on_operation_failed(self, operation_type, targets, error):
        """Handle operation failed event."""
        logger.error(f"Operation failed: {operation_type} on {targets}, error: {error}")
        
    def set_current_path(self, path: str):
        """Public method to set the current path."""
        self.file_view.set_current_path(path)
        
    def get_current_path(self) -> str:
        """Public method to get the current path."""
        return self.file_view.get_current_path()
        
    def closeEvent(self, event):
        """Handle widget close event."""
        self.settings.save()
        super().closeEvent(event)
