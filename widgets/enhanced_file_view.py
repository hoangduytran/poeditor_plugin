"""
Enhanced File View with context menu support for the Explorer panel.

This extends the SimpleFileView class to add context menu support and integration
with the FileOperationsService.
"""

from typing import Optional, Dict, List, Any, TYPE_CHECKING
from PySide6.QtCore import Qt, Signal, QModelIndex, QItemSelectionModel, QMimeData
from PySide6.QtWidgets import QApplication, QTreeView, QMenu, QHeaderView
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent

from lg import logger
from widgets.simple_explorer_widget import SimpleFileView
from widgets.explorer_context_menu import ExplorerContextMenu
from widgets.explorer.explorer_header_bar import HeaderNavigationWidget
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager
from services.drag_drop_service import DragDropService
from services.column_manager_service import ColumnManagerService
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService


class EnhancedFileView(SimpleFileView):
    """
    Enhanced file view with context menu support.

    This class extends SimpleFileView to add context menu support
    and integration with file operations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Will be set by parent widget
        self.context_menu_manager = None
        self.file_operations_service = None
        self.undo_redo_manager = None
        self.drag_drop_service = None
        self.column_manager = None

        # Set up drag and drop support
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeView.DragDropMode.DragDrop)

        # Track drag start position
        self.drag_start_position = None

        # Create and set header navigation widget
        self._setup_header_navigation()

    def setup_context_menu(self, file_operations_service: FileOperationsService,
                         undo_redo_manager: UndoRedoManager,
                         column_manager: Optional[ColumnManagerService] = None,
                         navigation_service: Optional[Any] = None,
                         history_service: Optional[Any] = None,
                         location_manager: Optional[Any] = None,
                         completion_service: Optional[Any] = None):
        """
        Set up the context menu manager and services.

        Args:
            file_operations_service: Service for file operations
            undo_redo_manager: Manager for undo/redo operations
            column_manager: Column management service
            navigation_service: Service for navigation
            history_service: Service for navigation history
            location_manager: Service for location management
            completion_service: Service for path completion
        """
        self.file_operations_service = file_operations_service
        self.undo_redo_manager = undo_redo_manager
        self.column_manager = column_manager
        self.navigation_service = navigation_service
        self.history_service = history_service
        self.location_manager = location_manager
        self.completion_service = completion_service

        # Create context menu manager
        self.context_menu_manager = ExplorerContextMenu(
            file_operations_service,
            undo_redo_manager
        )

        # Create drag and drop service
        self.drag_drop_service = DragDropService(file_operations_service)

        # Connect context menu signal
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Connect context menu signals
        self.context_menu_manager.show_properties.connect(self._show_properties)
        self.context_menu_manager.show_open_with.connect(self._show_open_with)
        self.context_menu_manager.refresh_requested.connect(self._refresh_view)

        # Set up header with services if available
        if hasattr(self, 'header_nav'):
            # Inject navigation services if available
            if all([self.navigation_service, self.history_service,
                    self.location_manager, self.completion_service]):
                logger.debug("Injecting navigation services into header navigation widget")
                # Use explicit type casting to resolve type checking issues
                self.header_nav.inject_services(
                    navigation_service=self.navigation_service,  # type: ignore
                    history_service=self.history_service,  # type: ignore
                    location_manager=self.location_manager,  # type: ignore
                    completion_service=self.completion_service,  # type: ignore
                    column_manager=self.column_manager
                )

                # Connect navigation service signals to update the file view
                assert self.navigation_service is not None  # Help type checker understand it's not None here
                self.navigation_service.current_path_changed.connect(self._on_navigation_path_changed)
                self.header_nav.navigation_requested.connect(lambda path: logger.debug(f"Navigation requested to: {path}"))

            # Otherwise just inject column manager if available
            elif self.column_manager:
                logger.debug(f"Injecting column manager into header navigation widget: {self.column_manager}")
                self.header_nav.inject_column_manager(self.column_manager)

            # Apply initial column settings if column manager is available
            if self.column_manager:
                self._apply_initial_column_settings()

                # Connect to column visibility changes
                self.header_nav.column_visibility_changed.connect(self._on_column_visibility_changed)

    def _show_context_menu(self, position):
        """
        Show context menu at the given position.

        Args:
            position: Position to show the menu at
        """
        if not self.context_menu_manager:
            logger.warning("Context menu manager not set")
            return

        # Get index at position
        index = self.indexAt(position)

        # Get selected items
        selected_items = []

        if index.isValid():
            # If the item under cursor is not selected, select it
            if not self.selectionModel().isSelected(index):
                self.selectionModel().clear()
                self.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)

            # Get all selected indices
            selected_indices = self.selectionModel().selectedIndexes()

            # Convert to source indices
            source_indices = [self.proxy_model.mapToSource(idx) for idx in selected_indices]

            # Create item dictionaries
            for idx in source_indices:
                path = self.file_system_model.filePath(idx)
                is_dir = self.file_system_model.isDir(idx)
                name = self.file_system_model.fileName(idx)

                selected_items.append({
                    'path': path,
                    'is_dir': is_dir,
                    'name': name
                })

        # Get the current directory
        current_directory = self.rootPath()

        # Create menu based on selection and current directory
        menu = self.context_menu_manager.create_menu(selected_items, current_directory)

        # Show menu at position
        menu.exec_(self.viewport().mapToGlobal(position))

    def _show_properties(self, paths):
        """
        Show properties dialog for the given paths.

        Args:
            paths: List of paths to show properties for
        """
        # This would be implemented with a properties dialog
        logger.debug(f"Show properties for: {paths}")

    def _show_open_with(self, paths):
        """
        Show 'Open With' dialog for the given paths.

        Args:
            paths: List of paths to show 'Open With' dialog for
        """
        # This would be implemented with an 'Open With' dialog
        logger.debug(f"Show 'Open With' for: {paths}")

    # ============== HEADER NAVIGATION IMPLEMENTATION ==============

    def _setup_header_navigation(self) -> None:
        """Set up the header navigation widget."""
        # Create header navigation widget
        self.header_nav = HeaderNavigationWidget(Qt.Orientation.Horizontal, self)

        # Set it as the header for this view
        self.setHeader(self.header_nav)

        # Enable custom context menu for the header
        self.header_nav.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Connect a debug handler to track context menu requests
        self.header_nav.customContextMenuRequested.connect(
            lambda pos: logger.debug(f"Header context menu requested at position: {pos}")
        )

        logger.debug("Header navigation widget set up")

    def _on_navigation_path_changed(self, new_path: str) -> None:
        """
        Handle path change from navigation service.

        Args:
            new_path: The new path to navigate to
        """
        logger.debug(f"Navigation path changed to: {new_path}")
        # Update the file view to show the new directory
        self.set_current_path(new_path)

# ============== COLUMN MANAGEMENT IMPLEMENTATION ==============

    def _apply_initial_column_settings(self) -> None:
        """Apply initial column settings from the column manager."""
        if not self.column_manager:
            return

        # Get visible columns
        visible_columns = self.column_manager.get_visible_columns()

        # Show/hide columns based on settings
        for col_id, col_info in self.column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns

            if visible:
                self.showColumn(model_column)
            else:
                self.hideColumn(model_column)

        # Apply column widths
        if self.column_manager.get_fit_content_enabled():
            # If fit content is enabled, resize columns to fit content
            for section in range(self.header().count()):
                self.resizeColumnToContents(section)
        else:
            # Otherwise apply saved/default widths
            for col_id, col_info in self.column_manager.get_available_columns().items():
                model_column = col_info.get("model_column", 0)
                width = self.column_manager.get_column_width(col_id)
                self.setColumnWidth(model_column, width)

        logger.debug("Applied initial column settings")

    def _on_column_visibility_changed(self, visible_columns: List[str]) -> None:
        """
        Handle column visibility changes from the header.

        Args:
            visible_columns: List of column IDs that should be visible
        """
        if not self.column_manager:
            return

        # Update column visibility
        for col_id, col_info in self.column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns

            if visible:
                self.showColumn(model_column)
            else:
                self.hideColumn(model_column)

        logger.debug(f"Updated column visibility from header: {visible_columns}")

    # ============== DRAG AND DROP IMPLEMENTATION ==============

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for drag and drop."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events to initiate drag operations."""
        if not event.buttons() & Qt.MouseButton.LeftButton:
            return

        if not self.drag_start_position:
            return

        # Check if the distance is far enough to start a drag
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return

        # Get the selected paths
        selected_paths = self._get_selected_paths()
        if not selected_paths:
            return

        # Start the drag operation
        if self.drag_drop_service:
            self.drag_drop_service.start_drag(selected_paths, event.pos(), self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Handle drag move events."""
        # Get the index at the cursor position
        index = self.indexAt(event.pos())

        if not index.isValid():
            # Over an empty area, accept if we're in a valid directory
            if self.rootPath():
                event.acceptProposedAction()
            else:
                event.ignore()
            return

        # Get the path at the cursor position
        source_index = self.proxy_model.mapToSource(index)
        path = self.file_system_model.filePath(source_index)

        # Accept if it's a directory
        if self.file_system_model.isDir(source_index):
            event.acceptProposedAction()
            # Highlight the item
            self.setCurrentIndex(index)
        else:
            # Over a file, accept the parent directory
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        # Get the drop location
        index = self.indexAt(event.pos())

        # Determine the target directory
        if index.isValid():
            source_index = self.proxy_model.mapToSource(index)
            path = self.file_system_model.filePath(source_index)

            # If it's a file, use its parent directory
            if not self.file_system_model.isDir(source_index):
                parent_index = self.file_system_model.parent(source_index)
                path = self.file_system_model.filePath(parent_index)
        else:
            # Dropped in empty space, use current directory
            path = self.rootPath()

        # Process the drop with our service
        if self.drag_drop_service and path:
            success = self.drag_drop_service.process_drop(
                event.mimeData(), path, event.proposedAction()
            )

            if success:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def _get_selected_paths(self) -> list:
        """Get the file paths of the selected items."""
        selected_indexes = self.selectionModel().selectedIndexes()

        # Filter to only get the first column (name column)
        filtered_indexes = [idx for idx in selected_indexes if idx.column() == 0]

        # Convert to paths
        paths = []
        for index in filtered_indexes:
            source_index = self.proxy_model.mapToSource(index)
            path = self.file_system_model.filePath(source_index)
            paths.append(path)

        return paths

    def rootPath(self) -> str:
        """Get the current root path of the view."""
        return self.file_system_model.rootPath()

    def _refresh_view(self):
        """
        Refresh the file view by reloading the current directory.

        This updates the view to reflect any changes in the file system
        that may have occurred (new files, deleted files, etc).
        """
        current_path = self.rootPath()
        if current_path:
            # Refresh by resetting the root path
            self.file_system_model.setRootPath(current_path)
            logger.info(f"Refreshed view for directory: {current_path}")
