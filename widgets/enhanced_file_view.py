"""
Enhanced File View with context menu support for the Explorer panel.

This extends the SimpleFileView class to add context menu support and integration
with the FileOperationsService.
"""

from PySide6.QtCore import Qt, Signal, QModelIndex, QItemSelectionModel, QMimeData
from PySide6.QtWidgets import QApplication, QTreeView, QMenu
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent

from lg import logger
from widgets.simple_explorer_widget import SimpleFileView
from widgets.explorer_context_menu import ExplorerContextMenu
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager
from services.drag_drop_service import DragDropService


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
        
        # Set up drag and drop support
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeView.DragDropMode.DragDrop)
        
        # Track drag start position
        self.drag_start_position = None
        
    def setup_context_menu(self, file_operations_service: FileOperationsService, 
                         undo_redo_manager: UndoRedoManager):
        """
        Set up the context menu manager.
        
        Args:
            file_operations_service: Service for file operations
            undo_redo_manager: Manager for undo/redo operations
        """
        self.file_operations_service = file_operations_service
        self.undo_redo_manager = undo_redo_manager
        
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
        
        # Create menu based on selection
        menu = self.context_menu_manager.create_menu(selected_items)
        
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
