"""
Drag and Drop Service for handling file transfer operations.

This service provides functionality for dragging and dropping files
both within the application and between external applications.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, QMimeData, Qt, Signal, QPoint, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QDrag

from lg import logger
from services.file_operations_service import FileOperationsService, OperationType


class DragDropService(QObject):
    """
    Service for handling drag and drop operations.
    
    This service works with FileOperationsService to provide
    drag and drop capabilities for file and directory items.
    """
    
    # Signals
    drag_started = Signal(list)  # List of paths being dragged
    drop_received = Signal(list, str)  # List of paths, target directory
    drag_completed = Signal(bool)  # Success status
    
    def __init__(self, file_operations_service: Optional[FileOperationsService] = None):
        """
        Initialize the DragDropService.
        
        Args:
            file_operations_service: Service for file operations
        """
        super().__init__()
        self.file_operations_service = file_operations_service
        self.drag_source_paths = []
        self.last_drop_target = ""
        self.drag_in_progress = False
        
    def set_file_operations_service(self, service: FileOperationsService):
        """
        Set the file operations service.
        
        Args:
            service: FileOperationsService instance
        """
        self.file_operations_service = service
    
    def start_drag(self, source_paths: List[str], start_pos: QPoint, parent: QObject) -> QDrag:
        """
        Start a drag operation.
        
        Args:
            source_paths: List of file paths to drag
            start_pos: Starting position for the drag
            parent: Parent widget for the drag operation
            
        Returns:
            QDrag: The drag object
        """
        if not source_paths:
            logger.warning("Cannot start drag with no source paths")
            return QDrag(parent)  # Return empty drag object instead of None
            
        # Store the source paths
        self.drag_source_paths = source_paths
        self.drag_in_progress = True
        
        # Create mime data
        mime_data = QMimeData()
        
        # Add URLs to the mime data
        urls = []
        for path in source_paths:
            try:
                url = QUrl.fromLocalFile(path)
                if url.isValid():
                    urls.append(url)
                else:
                    logger.warning(f"Created invalid URL for path: {path}")
            except Exception as e:
                logger.error(f"Error creating URL from path {path}: {str(e)}")
                
        if urls:
            mime_data.setUrls(urls)
        else:
            logger.warning("No valid URLs created from source paths")
        
        # Add text representation as backup
        mime_data.setText("\n".join(source_paths))
        
        # Create drag object
        drag = QDrag(parent)
        drag.setMimeData(mime_data)
        
        # Set default drag action
        default_action = Qt.DropAction.CopyAction
        
        # Check if source is within our application
        try:
            app_dir = QApplication.applicationDirPath()
            if app_dir and all(path.startswith(app_dir) for path in source_paths):
                default_action = Qt.DropAction.MoveAction
        except Exception as e:
            logger.error(f"Error checking application directory: {str(e)}")
        
        # Emit signal that drag has started
        self.drag_started.emit(source_paths)
        
        # Execute the drag and capture the result
        # In PySide6, drag.exec() takes supportedActions as a combination of flags
        # and defaultAction as a separate parameter
        result = drag.exec_(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction | Qt.DropAction.LinkAction, default_action)
        
        # Reset the drag state
        self.drag_in_progress = False
        self.drag_completed.emit(result != Qt.DropAction.IgnoreAction)
        
        return drag
    
    def process_drop(self, mime_data: QMimeData, target_dir: str, 
                    suggested_action: Qt.DropAction) -> bool:
        """
        Process a drop operation.
        
        Args:
            mime_data: The mime data from the drop
            target_dir: The target directory
            suggested_action: The suggested drop action
            
        Returns:
            bool: True if the drop was successful, False otherwise
        """
        if not self.file_operations_service:
            logger.error("Cannot process drop: file operations service not set")
            return False
        
        if not mime_data:
            logger.error("Cannot process drop: mime data is empty")
            return False
        
        if not target_dir:
            logger.error("Cannot process drop: target directory not specified")
            return False
            
        # Extract URLs from mime data
        if mime_data.hasUrls():
            paths = [url.toLocalFile() for url in mime_data.urls()]
        elif mime_data.hasText():
            # Fallback to text if URLs not available
            paths = mime_data.text().split("\n")
        else:
            logger.warning("Drop data doesn't contain URLs or text")
            return False
            
        # Clean up paths
        paths = [path.replace("file://", "") for path in paths if path.strip()]
        
        if not paths:
            logger.warning("No valid paths found in drop data")
            return False
            
        # Store last drop target
        self.last_drop_target = target_dir
        
        # Emit signal that drop was received
        self.drop_received.emit(paths, target_dir)
        
        # Process the drop based on the action
        if suggested_action == Qt.DropAction.CopyAction:
            return self._handle_copy_action(paths, target_dir)
        elif suggested_action == Qt.DropAction.MoveAction:
            return self._handle_move_action(paths, target_dir)
        elif suggested_action == Qt.DropAction.LinkAction:
            return self._handle_link_action(paths, target_dir)
        else:
            logger.warning(f"Unsupported drop action: {suggested_action}")
            return False
    
    def _handle_copy_action(self, source_paths: List[str], target_dir: str) -> bool:
        """
        Handle a copy action.
        
        Args:
            source_paths: List of source file paths
            target_dir: Target directory
            
        Returns:
            bool: True if the operation was successful
        """
        logger.info(f"Copy action: {len(source_paths)} items to {target_dir}")
        
        try:
            if not self.file_operations_service:
                logger.error("File operations service is not set")
                return False
                
            self.file_operations_service.copy_to_clipboard(source_paths)
            self.file_operations_service.paste(target_dir)
            return True
        except Exception as e:
            logger.error(f"Error during copy operation: {str(e)}")
            return False
    
    def _handle_move_action(self, source_paths: List[str], target_dir: str) -> bool:
        """
        Handle a move action.
        
        Args:
            source_paths: List of source file paths
            target_dir: Target directory
            
        Returns:
            bool: True if the operation was successful
        """
        logger.info(f"Move action: {len(source_paths)} items to {target_dir}")
        
        try:
            if not self.file_operations_service:
                logger.error("File operations service is not set")
                return False
                
            self.file_operations_service.cut_to_clipboard(source_paths)
            self.file_operations_service.paste(target_dir)
            return True
        except Exception as e:
            logger.error(f"Error during move operation: {str(e)}")
            return False
    
    def _handle_link_action(self, source_paths: List[str], target_dir: str) -> bool:
        """
        Handle a link action.
        
        Args:
            source_paths: List of source file paths
            target_dir: Target directory
            
        Returns:
            bool: True if the operation was successful
        """
        logger.info(f"Link action: {len(source_paths)} items to {target_dir}")
        
        try:
            if not self.file_operations_service:
                logger.error("File operations service is not set")
                return False
                
            # For now, treat links as copies since link creation would need
            # platform-specific implementation
            return self._handle_copy_action(source_paths, target_dir)
        except Exception as e:
            logger.error(f"Error during link operation: {str(e)}")
            return False
