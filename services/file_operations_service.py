"""
File Operations Service for handling file system operations.

This service provides a centralized way to perform file operations
with proper error handling, undo/redo support, and event notifications.
"""

import os
import shutil
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any

from PySide6.QtCore import QObject, Signal, Slot, QMimeData, QUrl
from PySide6.QtWidgets import QApplication, QMessageBox

from lg import logger
from services.undo_redo_service import UndoRedoManager, FileOperation
from services.file_numbering_service import FileNumberingService
from models.file_system_models import FileSystemItem


class OperationType(Enum):
    """Enumeration of supported file operations."""
    COPY = "copy"
    CUT = "cut"
    PASTE = "paste"
    DELETE = "delete"
    RENAME = "rename"
    DUPLICATE = "duplicate"
    NEW_FILE = "new_file"
    NEW_FOLDER = "new_folder"
    MOVE = "move"


class FileOperationsService(QObject):
    """
    Service for handling file operations in the Explorer.
    
    This service provides a centralized way to perform file operations
    with proper error handling, undo/redo support, and event notifications.
    
    This service uses:
    - FileNumberingService to handle naming conflicts
    - UndoRedoManager to track operations for undo/redo capability
    - Qt clipboard for copy/paste operations
    
    Example:
        >>> file_ops = FileOperationsService()
        >>> file_ops.operationCompleted.connect(lambda op_type, sources, target: 
        ...     print(f"Operation {op_type} completed"))
        >>> file_ops.copy_to_clipboard(["/path/to/file.txt"])
        >>> new_paths = file_ops.paste("/destination/")
        
    Thread Safety:
        This service must be used from the main thread only. File operations are
        performed synchronously, but signals can be connected to handle UI updates
        asynchronously after operations complete.
    """
    
    # Signals
    operationStarted = Signal(str, list)  # operation_type, paths
    operationCompleted = Signal(str, list, str)  # operation_type, source_paths, target_path
    operationFailed = Signal(str, list, str)  # operation_type, paths, error_message
    
    # Clipboard operations
    clipboardChanged = Signal()
    
    def __init__(self, parent=None):
        """Initialize the file operations service."""
        super().__init__(parent)
        
        self.undo_redo_manager = UndoRedoManager()
        self.numbering_service = FileNumberingService()
        
        # Internal clipboard state
        self._clipboard_mode: Optional[str] = None  # "copy" or "cut"
        self._clipboard_paths: List[str] = []
        
        # Track operations in progress
        self._operations_in_progress: Dict[str, Any] = {}
        
    # =============== CLIPBOARD OPERATIONS ===============
    
    def copy_to_clipboard(self, paths: List[str]) -> bool:
        """
        Copy the specified paths to the internal clipboard.
        
        Args:
            paths: List of paths to copy
            
        Returns:
            True if successful, False otherwise
        """
        if not paths:
            return False
            
        # Validate paths exist
        valid_paths = [p for p in paths if os.path.exists(p)]
        if not valid_paths:
            self.operationFailed.emit(OperationType.COPY.value, paths, 
                                      "No valid paths to copy")
            return False
        
        # Store in internal clipboard
        self._clipboard_mode = "copy"
        self._clipboard_paths = valid_paths
        
        # Also copy to system clipboard as text
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText("\n".join(valid_paths))
        # On platforms that support it, also add as URLs
        urls = [QUrl.fromLocalFile(path) for path in valid_paths]
        mime_data.setUrls(urls)
        clipboard.setMimeData(mime_data)
        
        self.clipboardChanged.emit()
        self.operationCompleted.emit(OperationType.COPY.value, valid_paths, "")
        return True
    
    def cut_to_clipboard(self, paths: List[str]) -> bool:
        """
        Cut the specified paths to the internal clipboard.
        
        Args:
            paths: List of paths to cut
            
        Returns:
            True if successful, False otherwise
        """
        if not paths:
            return False
            
        # Validate paths exist
        valid_paths = [p for p in paths if os.path.exists(p)]
        if not valid_paths:
            self.operationFailed.emit(OperationType.CUT.value, paths, 
                                       "No valid paths to cut")
            return False
        
        # Store in internal clipboard
        self._clipboard_mode = "cut"
        self._clipboard_paths = valid_paths
        
        # Also cut to system clipboard as text
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText("\n".join(valid_paths))
        # On platforms that support it, also add as URLs
        urls = [QUrl.fromLocalFile(path) for path in valid_paths]
        mime_data.setUrls(urls)
        clipboard.setMimeData(mime_data)
        
        self.clipboardChanged.emit()
        self.operationCompleted.emit(OperationType.CUT.value, valid_paths, "")
        return True
    
    def get_clipboard_contents(self) -> Tuple[Optional[str], List[str]]:
        """
        Get the current clipboard mode and contents.
        
        Returns:
            Tuple of (mode, paths) where mode is "copy", "cut" or None
        """
        return (self._clipboard_mode, self._clipboard_paths)
    
    def can_paste(self, target_dir: str) -> bool:
        """
        Check if paste operation is possible at the target directory.
        
        Args:
            target_dir: Target directory path
            
        Returns:
            True if paste operation is possible, False otherwise
        """
        # Check clipboard has content
        if not self._clipboard_paths or self._clipboard_mode not in ["copy", "cut"]:
            return False
        
        # Check target exists and is a directory
        if not os.path.isdir(target_dir):
            return False
        
        # Check permissions
        if not os.access(target_dir, os.W_OK):
            return False
            
        return True
    
    def paste(self, target_dir: str) -> List[str]:
        """
        Paste the clipboard contents to the target directory.
        
        Args:
            target_dir: Target directory path
            
        Returns:
            List of successfully created paths
        """
        if not self.can_paste(target_dir):
            self.operationFailed.emit(OperationType.PASTE.value, [], 
                                       f"Cannot paste to {target_dir}")
            return []
            
        self.operationStarted.emit(OperationType.PASTE.value, self._clipboard_paths)
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.PASTE.value,
            'paths': self._clipboard_paths,
            'target': target_dir
        }
        
        created_paths = []
        source_paths = self._clipboard_paths.copy()
        is_cut = self._clipboard_mode == "cut"
        
        try:
            for source_path in source_paths:
                # Skip if source doesn't exist
                if not os.path.exists(source_path):
                    continue
                    
                source_name = os.path.basename(source_path)
                target_path = os.path.join(target_dir, source_name)
                
                # Handle name conflicts
                if os.path.exists(target_path):
                    target_path = self.numbering_service.generate_numbered_name(target_path)
                
                # Perform the operation
                if is_cut:
                    shutil.move(source_path, target_path)
                else:  # copy
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, target_path)
                    else:
                        shutil.copy2(source_path, target_path)
                
                created_paths.append(target_path)
            
            # Record for undo/redo
            operation = FileOperation(
                operation_type='paste',
                source_paths=source_paths,
                target_path=target_dir,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={
                    'created_paths': created_paths,
                    'was_cut': is_cut,
                    'original_paths': source_paths if is_cut else []
                }
            )
            self.undo_redo_manager.record_operation(operation)
            
            # Clear clipboard after cut operation
            if is_cut and created_paths:
                self._clipboard_paths = []
                self._clipboard_mode = None
                self.clipboardChanged.emit()
            
            self.operationCompleted.emit(OperationType.PASTE.value, 
                                         source_paths, target_dir)
            
            return created_paths
            
        except Exception as e:
            logger.error(f"Paste operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.PASTE.value, 
                                      source_paths, str(e))
            return created_paths
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
    
    # =============== DIRECT FILE OPERATIONS ===============
    
    def delete_items(self, paths: List[str], skip_trash: bool = False) -> bool:
        """
        Delete the specified items.
        
        Args:
            paths: List of paths to delete
            skip_trash: If True, permanently delete instead of moving to trash
            
        Returns:
            True if successful, False otherwise
        """
        if not paths:
            return False
            
        # Filter valid paths
        valid_paths = [p for p in paths if os.path.exists(p)]
        if not valid_paths:
            self.operationFailed.emit(OperationType.DELETE.value, paths, 
                                       "No valid paths to delete")
            return False
            
        self.operationStarted.emit(OperationType.DELETE.value, valid_paths)
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.DELETE.value,
            'paths': valid_paths
        }
        
        try:
            # Prepare undo data (we need to collect info before deleting)
            undo_data = {
                'items': []
            }
            
            for path in valid_paths:
                item_data = {
                    'path': path,
                    'is_dir': os.path.isdir(path),
                    'parent_dir': os.path.dirname(path)
                }
                
                # For files, store content for potential undo
                if not item_data['is_dir'] and os.path.getsize(path) < 10 * 1024 * 1024:  # 10MB limit
                    try:
                        with open(path, 'rb') as f:
                            item_data['content'] = f.read()
                    except Exception as e:
                        item_data['content'] = None
                        logger.error(f"Failed to read file content for undo: {e}")
                
                undo_data['items'].append(item_data)
            
            # Perform deletion
            for path in valid_paths:
                try:
                    if skip_trash:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.unlink(path)
                    else:
                        # Check if send2trash is available
                        try:
                            import send2trash
                            send2trash.send2trash(path)
                        except ImportError:
                            logger.warning("send2trash not available, using permanent delete")
                            if os.path.isdir(path):
                                shutil.rmtree(path)
                            else:
                                os.unlink(path)
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {str(e)}")
                    raise
            
            # Record for undo/redo if not skipping trash
            if not skip_trash:
                operation = FileOperation(
                    operation_type='delete',
                    source_paths=valid_paths,
                    target_path="",
                    timestamp=datetime.now(),
                    is_undoable=True,
                    undo_data=undo_data
                )
                self.undo_redo_manager.record_operation(operation)
            
            self.operationCompleted.emit(OperationType.DELETE.value, valid_paths, "")
            return True
            
        except Exception as e:
            logger.error(f"Delete operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.DELETE.value, valid_paths, str(e))
            return False
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
    
    def rename_item(self, path: str, new_name: str) -> str:
        """
        Rename a file or directory.
        
        Args:
            path: Path of the item to rename
            new_name: New name (not full path)
            
        Returns:
            The new path if successful, empty string otherwise
        """
        if not os.path.exists(path):
            self.operationFailed.emit(OperationType.RENAME.value, [path],
                                       f"Path does not exist: {path}")
            return ""
            
        # Ensure new_name is just the name, not a path
        if os.path.sep in new_name:
            new_name = os.path.basename(new_name)
            
        # Get the parent directory
        parent_dir = os.path.dirname(path)
        new_path = os.path.join(parent_dir, new_name)
        
        # Check if target already exists
        if os.path.exists(new_path) and path != new_path:
            self.operationFailed.emit(OperationType.RENAME.value, [path],
                                       f"Target already exists: {new_path}")
            return ""
            
        self.operationStarted.emit(OperationType.RENAME.value, [path])
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.RENAME.value,
            'path': path,
            'new_name': new_name
        }
        
        try:
            # Store original info for undo
            old_path = path
            
            # Perform rename
            os.rename(path, new_path)
            
            # Record for undo/redo
            operation = FileOperation(
                operation_type='rename',
                source_paths=[old_path],
                target_path=new_path,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={
                    'old_path': old_path,
                    'new_path': new_path
                }
            )
            self.undo_redo_manager.record_operation(operation)
            
            self.operationCompleted.emit(OperationType.RENAME.value, [path], new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Rename operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.RENAME.value, [path], str(e))
            return ""
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
                
    def duplicate_item(self, path: str) -> str:
        """
        Create a duplicate of a file or directory with auto-numbering.
        
        Args:
            path: Path of the item to duplicate
            
        Returns:
            Path of the new item if successful, empty string otherwise
        """
        if not os.path.exists(path):
            self.operationFailed.emit(OperationType.DUPLICATE.value, [path],
                                       f"Path does not exist: {path}")
            return ""
            
        self.operationStarted.emit(OperationType.DUPLICATE.value, [path])
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.DUPLICATE.value,
            'path': path
        }
        
        try:
            # Generate a numbered name for the duplicate
            new_path = self.numbering_service.generate_numbered_name(path)
            
            # Perform copy
            if os.path.isdir(path):
                shutil.copytree(path, new_path)
            else:
                shutil.copy2(path, new_path)
            
            # Record for undo/redo
            operation = FileOperation(
                operation_type='duplicate',
                source_paths=[path],
                target_path=new_path,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={'created_path': new_path}
            )
            self.undo_redo_manager.record_operation(operation)
            
            self.operationCompleted.emit(OperationType.DUPLICATE.value, [path], new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Duplicate operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.DUPLICATE.value, [path], str(e))
            return ""
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
    
    def create_new_file(self, parent_dir: str, name: str = "New File.txt") -> str:
        """
        Create a new empty file in the specified directory.
        
        Args:
            parent_dir: Directory in which to create the file
            name: Name of the new file
            
        Returns:
            Path of the new file if successful, empty string otherwise
        """
        if not os.path.isdir(parent_dir):
            self.operationFailed.emit(OperationType.NEW_FILE.value, [parent_dir],
                                       f"Parent directory does not exist: {parent_dir}")
            return ""
            
        # Check write permissions
        if not os.access(parent_dir, os.W_OK):
            self.operationFailed.emit(OperationType.NEW_FILE.value, [parent_dir],
                                       f"No write permission in: {parent_dir}")
            return ""
            
        # Create full path
        new_path = os.path.join(parent_dir, name)
        
        # Handle name conflicts
        if os.path.exists(new_path):
            new_path = self.numbering_service.generate_numbered_name(new_path)
            
        self.operationStarted.emit(OperationType.NEW_FILE.value, [parent_dir])
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.NEW_FILE.value,
            'parent_dir': parent_dir,
            'name': name
        }
        
        try:
            # Create empty file
            with open(new_path, 'w') as f:
                pass  # Just create it empty
            
            # Record for undo/redo
            operation = FileOperation(
                operation_type='new_file',
                source_paths=[parent_dir],
                target_path=new_path,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={'created_path': new_path}
            )
            self.undo_redo_manager.record_operation(operation)
            
            self.operationCompleted.emit(OperationType.NEW_FILE.value, [parent_dir], new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Create file operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.NEW_FILE.value, [parent_dir], str(e))
            return ""
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
    
    def create_new_folder(self, parent_dir: str, name: str = "New Folder") -> str:
        """
        Create a new folder in the specified directory.
        
        Args:
            parent_dir: Directory in which to create the folder
            name: Name of the new folder
            
        Returns:
            Path of the new folder if successful, empty string otherwise
        """
        if not os.path.isdir(parent_dir):
            self.operationFailed.emit(OperationType.NEW_FOLDER.value, [parent_dir],
                                       f"Parent directory does not exist: {parent_dir}")
            return ""
            
        # Check write permissions
        if not os.access(parent_dir, os.W_OK):
            self.operationFailed.emit(OperationType.NEW_FOLDER.value, [parent_dir],
                                       f"No write permission in: {parent_dir}")
            return ""
            
        # Create full path
        new_path = os.path.join(parent_dir, name)
        
        # Handle name conflicts
        if os.path.exists(new_path):
            new_path = self.numbering_service.generate_numbered_name(new_path)
            
        self.operationStarted.emit(OperationType.NEW_FOLDER.value, [parent_dir])
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.NEW_FOLDER.value,
            'parent_dir': parent_dir,
            'name': name
        }
        
        try:
            # Create directory
            os.makedirs(new_path, exist_ok=True)
            
            # Record for undo/redo
            operation = FileOperation(
                operation_type='new_folder',
                source_paths=[parent_dir],
                target_path=new_path,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={'created_path': new_path}
            )
            self.undo_redo_manager.record_operation(operation)
            
            self.operationCompleted.emit(OperationType.NEW_FOLDER.value, [parent_dir], new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Create folder operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.NEW_FOLDER.value, [parent_dir], str(e))
            return ""
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
    
    def move_items(self, paths: List[str], target_dir: str) -> List[str]:
        """
        Move files/folders to a target directory.
        
        Args:
            paths: List of paths to move
            target_dir: Target directory path
            
        Returns:
            List of new paths after moving
        """
        if not os.path.isdir(target_dir):
            self.operationFailed.emit(OperationType.MOVE.value, paths,
                                       f"Target is not a directory: {target_dir}")
            return []
            
        # Filter valid paths and check for conflicts
        valid_paths = []
        for path in paths:
            if not os.path.exists(path):
                continue
                
            # Skip if trying to move inside itself
            if os.path.isdir(path) and (
                target_dir == path or 
                target_dir.startswith(os.path.join(path, ""))):
                continue
                
            valid_paths.append(path)
            
        if not valid_paths:
            self.operationFailed.emit(OperationType.MOVE.value, paths,
                                       "No valid paths to move")
            return []
            
        self.operationStarted.emit(OperationType.MOVE.value, valid_paths)
        
        operation_id = str(uuid.uuid4())
        self._operations_in_progress[operation_id] = {
            'type': OperationType.MOVE.value,
            'paths': valid_paths,
            'target_dir': target_dir
        }
        
        moved_items = []
        original_paths = []
        
        try:
            for path in valid_paths:
                original_paths.append(path)
                name = os.path.basename(path)
                new_path = os.path.join(target_dir, name)
                
                # Handle name conflicts
                if os.path.exists(new_path) and path != new_path:
                    new_path = self.numbering_service.generate_numbered_name(new_path)
                    
                # Perform move
                shutil.move(path, new_path)
                moved_items.append(new_path)
            
            # Record for undo/redo
            operation = FileOperation(
                operation_type='move',
                source_paths=original_paths,
                target_path=target_dir,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={
                    'original_paths': original_paths,
                    'new_paths': moved_items
                }
            )
            self.undo_redo_manager.record_operation(operation)
            
            self.operationCompleted.emit(OperationType.MOVE.value, original_paths, target_dir)
            return moved_items
            
        except Exception as e:
            logger.error(f"Move operation failed: {str(e)}")
            self.operationFailed.emit(OperationType.MOVE.value, original_paths, str(e))
            return moved_items
        finally:
            if operation_id in self._operations_in_progress:
                del self._operations_in_progress[operation_id]
    
    # =============== UNDO/REDO OPERATIONS ===============
    
    @Slot()
    def undo(self) -> bool:
        """
        Undo the last file operation.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.undo_redo_manager.can_undo():
            return False
            
        try:
            last_op = self.undo_redo_manager.peek_undo()
            if last_op is None:
                logger.warning("No operation to undo")
                return False
                
            op_type = last_op.operation_type
            
            logger.debug(f"Undoing operation: {op_type}")
            
            # Ensure undo_data is not None
            if last_op.undo_data is None:
                logger.warning(f"Missing undo data for operation: {op_type}")
                return False
                
            if op_type == 'paste':
                # Undo paste by deleting created files
                created_paths = last_op.undo_data.get('created_paths', [])
                was_cut = last_op.undo_data.get('was_cut', False)
                original_paths = last_op.undo_data.get('original_paths', [])
                
                # Delete the pasted items
                for path in created_paths:
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.unlink(path)
                
                # If it was a cut operation, we need to restore the originals
                if was_cut:
                    for path in original_paths:
                        parent_dir = os.path.dirname(path)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, exist_ok=True)
                            
                        # Find the corresponding new path
                        basename = os.path.basename(path)
                        for created in created_paths:
                            if os.path.basename(created) == basename:
                                # Move back
                                if os.path.exists(created):
                                    shutil.move(created, path)
                                break
                                
            elif op_type == 'delete':
                # Undo delete by restoring from undo_data
                items = last_op.undo_data.get('items', [])
                
                for item in items:
                    path = item.get('path')
                    is_dir = item.get('is_dir', False)
                    parent_dir = item.get('parent_dir', '')
                    
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir, exist_ok=True)
                        
                    if is_dir:
                        if not os.path.exists(path):
                            os.makedirs(path, exist_ok=True)
                    else:
                        content = item.get('content')
                        if content and not os.path.exists(path):
                            with open(path, 'wb') as f:
                                f.write(content)
                        
            elif op_type == 'rename':
                # Undo rename by renaming back
                old_path = last_op.undo_data.get('old_path')
                new_path = last_op.undo_data.get('new_path')
                
                if old_path is None or new_path is None:
                    logger.warning("Missing path information for rename undo")
                    return False
                
                if os.path.exists(new_path) and not os.path.exists(old_path):
                    # Rename back to original
                    parent_dir = os.path.dirname(old_path)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir, exist_ok=True)
                        
                    os.rename(new_path, old_path)
                    
            elif op_type in ['duplicate', 'new_file', 'new_folder']:
                # Undo by deleting the created path
                created_path = last_op.undo_data.get('created_path')
                
                if created_path is None:
                    logger.warning(f"Missing created_path for {op_type} undo")
                    return False
                
                if os.path.exists(created_path):
                    if os.path.isdir(created_path):
                        shutil.rmtree(created_path)
                    else:
                        os.unlink(created_path)
                        
            elif op_type == 'move':
                # Undo move by moving items back to original locations
                original_paths = last_op.undo_data.get('original_paths', [])
                new_paths = last_op.undo_data.get('new_paths', [])
                
                for i, new_path in enumerate(new_paths):
                    if i < len(original_paths) and os.path.exists(new_path):
                        original = original_paths[i]
                        parent_dir = os.path.dirname(original)
                        
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, exist_ok=True)
                            
                        # Move back to original location
                        shutil.move(new_path, original)
            
            # Pop the operation from undo stack
            self.undo_redo_manager.undo()
            return True
            
        except Exception as e:
            logger.error(f"Undo operation failed: {str(e)}")
            return False
    
    @Slot()
    def redo(self) -> bool:
        """
        Redo the last undone file operation.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.undo_redo_manager.can_redo():
            return False
            
        try:
            next_op = self.undo_redo_manager.peek_redo()
            if next_op is None:
                logger.warning("No operation to redo")
                return False
                
            op_type = next_op.operation_type
            
            # Ensure undo_data is not None
            if next_op.undo_data is None:
                logger.warning(f"Missing undo data for operation: {op_type}")
                return False
                
            logger.debug(f"Redoing operation: {op_type}")
            
            if op_type == 'paste':
                # Redo paste operation
                source_paths = next_op.source_paths
                target_dir = next_op.target_path
                was_cut = next_op.undo_data.get('was_cut', False)
                
                created_paths = []
                for source_path in source_paths:
                    if not os.path.exists(source_path):
                        continue
                        
                    name = os.path.basename(source_path)
                    new_path = os.path.join(target_dir, name)
                    
                    # Handle conflicts
                    if os.path.exists(new_path):
                        new_path = self.numbering_service.generate_numbered_name(new_path)
                        
                    # Perform operation
                    if was_cut:
                        shutil.move(source_path, new_path)
                    else:
                        if os.path.isdir(source_path):
                            shutil.copytree(source_path, new_path)
                        else:
                            shutil.copy2(source_path, new_path)
                            
                    created_paths.append(new_path)
                    
                # Update undo data with new created paths
                next_op.undo_data['created_paths'] = created_paths
                
            elif op_type == 'delete':
                # Redo delete operation
                items = next_op.undo_data.get('items', [])
                
                for item in items:
                    path = item.get('path')
                    
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.unlink(path)
                            
            elif op_type == 'rename':
                # Redo rename operation
                old_path = next_op.undo_data.get('old_path')
                new_path = next_op.undo_data.get('new_path')
                
                if old_path is None or new_path is None:
                    logger.warning("Missing path information for rename redo")
                    return False
                
                if os.path.exists(old_path) and not os.path.exists(new_path):
                    parent_dir = os.path.dirname(new_path)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir, exist_ok=True)
                        
                    os.rename(old_path, new_path)
                    
            elif op_type == 'duplicate':
                # Redo duplication
                source_path = next_op.source_paths[0] if next_op.source_paths else None
                created_path = next_op.undo_data.get('created_path')
                
                if created_path is None:
                    logger.warning("Missing created_path for duplicate redo")
                    return False
                
                if source_path and os.path.exists(source_path) and not os.path.exists(created_path):
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, created_path)
                    else:
                        shutil.copy2(source_path, created_path)
                        
            elif op_type == 'new_file':
                # Redo new file creation
                created_path = next_op.undo_data.get('created_path')
                
                if created_path is None:
                    logger.warning("Missing created_path for new_file redo")
                    return False
                
                if not os.path.exists(created_path):
                    parent_dir = os.path.dirname(created_path)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir, exist_ok=True)
                        
                    # Create empty file
                    with open(created_path, 'w') as f:
                        pass
                        
            elif op_type == 'new_folder':
                # Redo new folder creation
                created_path = next_op.undo_data.get('created_path')
                
                if created_path is None:
                    logger.warning("Missing created_path for new_folder redo")
                    return False
                
                if not os.path.exists(created_path):
                    os.makedirs(created_path, exist_ok=True)
                    
            elif op_type == 'move':
                # Redo move operation
                original_paths = next_op.undo_data.get('original_paths', [])
                new_paths = next_op.undo_data.get('new_paths', [])
                target_dir = next_op.target_path
                
                for i, original in enumerate(original_paths):
                    if os.path.exists(original):
                        # Find target path
                        if i < len(new_paths):
                            target = new_paths[i]
                        else:
                            name = os.path.basename(original)
                            target = os.path.join(target_dir, name)
                            
                        # Ensure parent exists
                        parent_dir = os.path.dirname(target)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, exist_ok=True)
                            
                        # Move to target
                        shutil.move(original, target)
            
            # Pop operation from redo stack
            self.undo_redo_manager.redo()
            return True
            
        except Exception as e:
            logger.error(f"Redo operation failed: {str(e)}")
            return False
    
    @Slot()
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.undo_redo_manager.can_undo()
    
    @Slot()
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.undo_redo_manager.can_redo()
    
    # =============== HELPERS ===============
    
    def is_operation_in_progress(self) -> bool:
        """Check if any operation is currently in progress."""
        return len(self._operations_in_progress) > 0
    
    def clear_clipboard(self):
        """Clear the internal clipboard."""
        self._clipboard_paths = []
        self._clipboard_mode = None
        self.clipboardChanged.emit()
