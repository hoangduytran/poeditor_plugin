"""
Explorer Context Menu

Provides context menu functionality for the Explorer panel, integrating with
file operations service, undo/redo manager, and supporting various selection states.
Includes keyboard shortcut support and accessibility features.
"""

import os
import platform
import subprocess
from typing import List, Dict, Any, Optional, Tuple

from PySide6.QtWidgets import QMenu, QMessageBox, QApplication, QInputDialog
from PySide6.QtCore import QObject, Signal, Qt, QMimeData, QUrl
from PySide6.QtGui import QIcon, QKeySequence, QAction, QFont

from lg import logger
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager
from services.keyboard_shortcut_service import keyboard_shortcut_service


class ExplorerContextMenu(QObject):
    """
    Context menu manager for the Explorer panel.
    
    Provides context-sensitive menus for files, folders, and empty areas,
    with appropriate operations based on selection state.
    Supports keyboard shortcuts and accessibility features.
    """
    
    # Signals for operations that require additional UI
    show_properties = Signal(list)  # list of file paths
    show_open_with = Signal(list)   # list of file paths
    refresh_requested = Signal()    # Signal emitted when refresh is requested
    
    # Property to track current selection for shortcut operations
    selected_items = []
    
    def __init__(self, 
                 file_operations_service: FileOperationsService,
                 undo_redo_manager: UndoRedoManager):
        """
        Initialize the context menu manager.
        
        Args:
            file_operations_service: Service for performing file operations
            undo_redo_manager: Manager for tracking undo/redo operations
        """
        super().__init__()
        self.file_operations_service = file_operations_service
        self.undo_redo_manager = undo_redo_manager
        self.current_directory = None  # Will be updated when creating menu
        self.keyboard_shortcut_service = keyboard_shortcut_service
        
        # Icons for common operations
        self._load_icons()
        
        # Register keyboard shortcuts
        self._register_shortcuts()
    
    def _load_icons(self):
        """Load icons for menu actions."""
        self.icons = {
            "open": QIcon("icons/open.svg"),
            "open_with": QIcon("icons/open_with.svg"),
            "open_new_window": QIcon("icons/open_new_window.svg"),
            "cut": QIcon("icons/cut.svg"),
            "copy": QIcon("icons/copy.svg"),
            "paste": QIcon("icons/paste.svg"),
            "duplicate": QIcon("icons/duplicate.svg"),
            "rename": QIcon("icons/rename.svg"),
            "delete": QIcon("icons/delete.svg"),
            "new_file": QIcon("icons/new_file.svg"),
            "new_folder": QIcon("icons/new_folder.svg"),
            "properties": QIcon("icons/properties.svg"),
            "terminal": QIcon("icons/terminal.svg"),
            "find": QIcon("icons/search.svg"),
            "favorites": QIcon("icons/star.svg"),
        }
        
    def _register_shortcuts(self):
        """Register keyboard shortcuts for common file operations."""
        # Define shortcuts for file operations
        shortcuts = [
            {
                'id': 'explorer.cut',
                'name': 'Cut',
                'sequence': 'Ctrl+X',
                'callback': self._shortcut_cut,
                'category': 'File Operations',
                'description': 'Cut selected files or folders'
            },
            {
                'id': 'explorer.copy',
                'name': 'Copy',
                'sequence': 'Ctrl+C',
                'callback': self._shortcut_copy,
                'category': 'File Operations',
                'description': 'Copy selected files or folders'
            },
            {
                'id': 'explorer.paste',
                'name': 'Paste',
                'sequence': 'Ctrl+V',
                'callback': self._shortcut_paste,
                'category': 'File Operations',
                'description': 'Paste files or folders'
            },
            {
                'id': 'explorer.delete',
                'name': 'Delete',
                'sequence': 'Delete',
                'callback': self._shortcut_delete,
                'category': 'File Operations',
                'description': 'Delete selected files or folders'
            },
            {
                'id': 'explorer.rename',
                'name': 'Rename',
                'sequence': 'F2',
                'callback': self._shortcut_rename,
                'category': 'File Operations',
                'description': 'Rename selected file or folder'
            },
            {
                'id': 'explorer.newFile',
                'name': 'New File',
                'sequence': 'Ctrl+N',
                'callback': self._shortcut_new_file,
                'category': 'File Operations',
                'description': 'Create a new file'
            },
            {
                'id': 'explorer.newFolder',
                'name': 'New Folder',
                'sequence': 'Ctrl+Shift+N',
                'callback': self._shortcut_new_folder,
                'category': 'File Operations',
                'description': 'Create a new folder'
            },
            {
                'id': 'explorer.refresh',
                'name': 'Refresh',
                'sequence': 'F5',
                'callback': self._shortcut_refresh,
                'category': 'File Operations',
                'description': 'Refresh the file explorer'
            },
        ]
        
        # Register all shortcuts with the keyboard shortcut service
        for shortcut in shortcuts:
            self.keyboard_shortcut_service.register_shortcut(
                id=shortcut['id'],
                name=shortcut['name'],
                default_sequence=shortcut['sequence'],
                callback=shortcut['callback'],
                category=shortcut['category'],
                context="explorer",
                context_sensitive=True,
                description=shortcut['description']
            )
            
    # Shortcut handler methods
    def _shortcut_cut(self):
        """Handle cut shortcut."""
        self._handle_selection_shortcut('cut')
    
    def _shortcut_copy(self):
        """Handle copy shortcut."""
        self._handle_selection_shortcut('copy')
    
    def _shortcut_paste(self):
        """Handle paste shortcut."""
        # Only works if we have a current directory
        if self.current_directory:
            self._paste_items(self.current_directory)
    
    def _shortcut_delete(self):
        """Handle delete shortcut."""
        self._handle_selection_shortcut('delete')
    
    def _shortcut_rename(self):
        """Handle rename shortcut."""
        self._handle_selection_shortcut('rename')
    
    def _shortcut_new_file(self):
        """Handle new file shortcut."""
        if self.current_directory:
            self._create_new_file(self.current_directory)
    
    def _shortcut_new_folder(self):
        """Handle new folder shortcut."""
        if self.current_directory:
            self._create_new_folder(self.current_directory)
    
    def _shortcut_refresh(self):
        """Handle refresh shortcut."""
        self.refresh_requested.emit()
    
    def _handle_selection_shortcut(self, operation: str):
        """
        Handle shortcuts for operations that require selected items.
        
        This is called by the individual shortcut handlers when
        we need to apply an operation to currently selected items.
        
        The Explorer panel should update this object's 'selected_items'
        property whenever selection changes.
        
        Args:
            operation: The operation to perform ('cut', 'copy', 'delete', 'rename')
        """
        # This requires the Explorer panel to set this property when selection changes
        if not self.selected_items:
            logger.debug(f"No items selected for {operation} shortcut")
            return
        
        items = self.selected_items
        paths = [item['path'] for item in items]
        
        if operation == 'cut':
            self._cut_items(paths)
        elif operation == 'copy':
            self._copy_items(paths)
        elif operation == 'delete':
            self._delete_items(paths)
        elif operation == 'rename' and len(items) == 1:
            self._rename_item(items[0]['path'])
            
    def _cut_items(self, paths: List[str]):
        """Cut selected items to clipboard."""
        try:
            # Create mime data
            mime_data = self._create_file_mime_data(paths)
            
            # Set operation type for paste
            mime_data.setData("application/x-explorer-operation", b"cut")
            
            # Set clipboard data
            clipboard = QApplication.clipboard()
            clipboard.setMimeData(mime_data)
            
            logger.debug(f"Cut items to clipboard: {paths}")
        except Exception as e:
            logger.error(f"Error cutting items: {e}")
            
    def _copy_items(self, paths: List[str]):
        """Copy selected items to clipboard."""
        try:
            # Create mime data
            mime_data = self._create_file_mime_data(paths)
            
            # Set operation type for paste
            mime_data.setData("application/x-explorer-operation", b"copy")
            
            # Set clipboard data
            clipboard = QApplication.clipboard()
            clipboard.setMimeData(mime_data)
            
            logger.debug(f"Copied items to clipboard: {paths}")
        except Exception as e:
            logger.error(f"Error copying items: {e}")
            
    def _paste_items(self, target_path: str):
        """Paste items from clipboard to target path."""
        try:
            # Get clipboard data
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            
            if not self._clipboard_has_files(mime_data):
                logger.warning("Clipboard does not contain files")
                return
            
            # Get paths from clipboard
            paths = self._get_paths_from_mime_data(mime_data)
            
            # Get operation type (cut or copy)
            operation_bytes = mime_data.data("application/x-explorer-operation")
            operation = operation_bytes.data().decode('utf-8') if operation_bytes else "copy"
            
            # Perform operation
            if operation == "cut":
                self.file_operations_service.move_items(paths, target_path)
            else:  # copy
                self.file_operations_service.copy_items(paths, target_path)
                
            logger.debug(f"Pasted items to {target_path}: {paths}")
        except Exception as e:
            logger.error(f"Error pasting items: {e}")
            
    def _delete_items(self, paths: List[str]):
        """Delete selected items."""
        try:
            # Confirm deletion
            confirm = QMessageBox.question(
                None,  # Parent window
                "Confirm Delete",
                f"Are you sure you want to delete {len(paths)} item(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                # Delete items
                self.file_operations_service.delete_items(paths)
                logger.debug(f"Deleted items: {paths}")
        except Exception as e:
            logger.error(f"Error deleting items: {e}")
            
    def _rename_item(self, path: str):
        """Rename selected item."""
        try:
            # Get current name
            current_name = os.path.basename(path)
            
            # Show dialog to get new name
            new_name, ok = QInputDialog.getText(
                None,  # Parent window
                "Rename",
                "Enter new name:",
                text=current_name
            )
            
            if ok and new_name:
                # Rename item
                new_path = os.path.join(os.path.dirname(path), new_name)
                self.file_operations_service.rename_item(path, new_path)
                logger.debug(f"Renamed {path} to {new_path}")
        except Exception as e:
            logger.error(f"Error renaming item: {e}")
            
    def _create_new_file(self, directory: str):
        """Create a new file in the specified directory."""
        try:
            # Show dialog to get file name
            file_name, ok = QInputDialog.getText(
                None,  # Parent window
                "New File",
                "Enter file name:",
            )
            
            if ok and file_name:
                # Create file using the correct method name
                self.file_operations_service.create_new_file(directory, file_name)
                logger.debug(f"Created new file: {file_name} in {directory}")
        except Exception as e:
            logger.error(f"Error creating new file: {e}")
            
    def _create_new_folder(self, directory: str):
        """Create a new folder in the specified directory."""
        try:
            # Show dialog to get folder name
            folder_name, ok = QInputDialog.getText(
                None,  # Parent window
                "New Folder",
                "Enter folder name:",
            )
            
            if ok and folder_name:
                # Create folder using the correct method name
                self.file_operations_service.create_new_folder(directory, folder_name)
                logger.debug(f"Created new folder: {folder_name} in {directory}")
        except Exception as e:
            logger.error(f"Error creating new folder: {e}")
            
    def _clipboard_has_files(self, mime_data: QMimeData) -> bool:
        """Check if clipboard has file data."""
        return mime_data.hasFormat("application/x-explorer-file-list")
    
    def _create_file_mime_data(self, paths: List[str]) -> QMimeData:
        """Create mime data for file operations."""
        mime_data = QMimeData()
        
        # Store paths as text
        mime_data.setText("\n".join(paths))
        
        # Store paths in custom format for internal operations
        path_bytes = "\n".join(paths).encode('utf-8')
        mime_data.setData("application/x-explorer-file-list", path_bytes)
        
        # Create URLs for system-wide drag and drop
        urls = [QUrl.fromLocalFile(path) for path in paths]
        mime_data.setUrls(urls)
        
        return mime_data
    
    def _get_paths_from_mime_data(self, mime_data: QMimeData) -> List[str]:
        """Get file paths from mime data."""
        if mime_data.hasFormat("application/x-explorer-file-list"):
            # Get paths from custom format
            path_bytes = mime_data.data("application/x-explorer-file-list")
            try:
                # Just use the text representation as fallback
                return mime_data.text().split("\n")
            except Exception as e:
                logger.error(f"Error decoding paths from mime data: {e}")
                return []
        elif mime_data.hasUrls():
            # Get paths from URLs
            urls = mime_data.urls()
            return [url.toLocalFile() for url in urls if url.isLocalFile()]
        elif mime_data.hasText():
            # Get paths from text
            return mime_data.text().split("\n")
        
        return []
        
    def _open_items(self, paths: List[str]):
        """Open selected items."""
        for path in paths:
            try:
                if os.path.isfile(path):
                    # Open file
                    if platform.system() == "Windows":
                        # Windows-specific method, use subprocess as fallback
                        subprocess.call(["start", "", path], shell=True)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", path])
                    else:  # Linux
                        subprocess.call(["xdg-open", path])
                elif os.path.isdir(path):
                    # Open directory in file explorer
                    if platform.system() == "Windows":
                        subprocess.call(["explorer", path])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", path])
                    else:  # Linux
                        subprocess.call(["xdg-open", path])
            except Exception as e:
                logger.error(f"Error opening item {path}: {e}")
                
    def _open_in_new_window(self, paths: List[str]):
        """Open directories in new window."""
        for path in paths:
            try:
                if os.path.isdir(path):
                    # This should be implemented based on application design
                    # For example, by emitting a signal to open a new window
                    logger.debug(f"Opening directory in new window: {path}")
                    # self.open_in_new_window_signal.emit(path)
            except Exception as e:
                logger.error(f"Error opening directory in new window {path}: {e}")
    
    def create_menu(self, selected_items: List[Dict[str, Any]], current_directory: Optional[str] = None) -> QMenu:
        """
        Create a context menu based on the selected items.
        
        Args:
            selected_items: List of selected items, each is a dict with:
                - 'path': str - Full path to the item
                - 'is_dir': bool - True if directory, False if file
                - 'name': str - Item name
            current_directory: Current directory path, used for paste operations
        
        Returns:
            QMenu: The context menu
        """
        menu = QMenu()
        menu.setObjectName("ExplorerContextMenu")
        
        # Store the current directory for use in menu actions
        self.current_directory = current_directory
        
        # Update selected items for shortcut operations
        self.selected_items = selected_items
        
        # Check selection state
        if not selected_items:
            # Empty area clicked - show background menu
            return self._create_background_menu()
        
        # Check if selection contains only directories, only files, or both
        only_dirs = all(item['is_dir'] for item in selected_items)
        only_files = all(not item['is_dir'] for item in selected_items)
        single_item = len(selected_items) == 1
        
        # Primary operations section
        self._add_primary_operations(menu, selected_items, only_dirs, only_files, single_item)
        menu.addSeparator()
        
        # Edit operations section
        self._add_edit_operations(menu, selected_items, only_dirs, only_files, single_item)
        menu.addSeparator()
        
        # Creation operations (only if in a directory or empty space)
        if only_dirs or not selected_items:
            self._add_creation_operations(menu, selected_items, only_dirs)
            menu.addSeparator()
        
        # Advanced operations
        self._add_advanced_operations(menu, selected_items, only_dirs, only_files, single_item)
        
        # Plugin operations (if any)
        # This would be integrated with the plugin system
        # self._add_plugin_operations(menu, selected_items)
        
        return menu
    
    def _create_background_menu(self) -> QMenu:
        """
        Create a context menu for the background (no selection).
        
        Returns:
            QMenu: The background context menu
        """
        menu = QMenu()
        
        # Creation operations
        self._add_creation_operations(menu, [], True)
        menu.addSeparator()
        
        # Paste operation (if clipboard has data)
        paste_action = QAction(self.icons.get("paste", QIcon()), "Paste", menu)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        
        # Check if clipboard has data
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        has_urls = mime_data.hasUrls() if mime_data else False
        
        paste_action.setEnabled(has_urls)
        paste_action.triggered.connect(
            lambda: self.file_operations_service.paste(
                self.current_directory
            ) if self.current_directory else logger.error("No current directory set")
        )
        menu.addAction(paste_action)
        
        # View options
        menu.addSeparator()
        
        # Terminal here
        terminal_action = QAction(self.icons.get("terminal", QIcon()), "Open Terminal Here", menu)
        terminal_action.triggered.connect(
            lambda: self._open_terminal(self.current_directory) if self.current_directory else logger.error("No current directory set")
        )
        menu.addAction(terminal_action)
        
        # Refresh
        refresh_action = QAction("Refresh", menu)
        # Emit a signal that parent widgets can connect to
        refresh_action.triggered.connect(self.refresh_requested.emit)
        menu.addAction(refresh_action)
        
        return menu
    
    def _add_primary_operations(self, menu: QMenu, selected_items: List[Dict[str, Any]], 
                              only_dirs: bool, only_files: bool, single_item: bool):
        """
        Add primary operations to the menu.
        
        Args:
            menu: The menu to add actions to
            selected_items: List of selected items
            only_dirs: True if selection contains only directories
            only_files: True if selection contains only files
            single_item: True if selection contains only one item
        """
        paths = [item['path'] for item in selected_items]
        
        # Open (default action)
        open_action = QAction(self.icons.get("open", QIcon()), "Open", menu)
        open_action.triggered.connect(lambda: self._open_items(paths))
        menu.addAction(open_action)
        
        # Open with... (for files)
        if only_files:
            open_with_action = QAction(self.icons.get("open_with", QIcon()), "Open With...", menu)
            open_with_action.triggered.connect(lambda: self.show_open_with.emit(paths))
            menu.addAction(open_with_action)
        
        # Open in new window (for directories)
        if only_dirs:
            open_new_window_action = QAction(
                self.icons.get("open_new_window", QIcon()), 
                "Open in New Window", 
                menu
            )
            open_new_window_action.triggered.connect(lambda: self._open_in_new_window(paths))
            menu.addAction(open_new_window_action)
    
    def _add_edit_operations(self, menu: QMenu, selected_items: List[Dict[str, Any]], 
                           only_dirs: bool, only_files: bool, single_item: bool):
        """
        Add edit operations to the menu.
        
        Args:
            menu: The menu to add actions to
            selected_items: List of selected items
            only_dirs: True if selection contains only directories
            only_files: True if selection contains only files
            single_item: True if selection contains only one item
        """
        paths = [item['path'] for item in selected_items]
        
        # Cut
        cut_action = QAction(self.icons.get("cut", QIcon()), "Cut", menu)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        cut_action.triggered.connect(lambda: self.file_operations_service.cut_to_clipboard(paths))
        menu.addAction(cut_action)
        
        # Copy
        copy_action = QAction(self.icons.get("copy", QIcon()), "Copy", menu)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(lambda: self.file_operations_service.copy_to_clipboard(paths))
        menu.addAction(copy_action)
        
        # Paste (enabled if clipboard has data and selection is a directory or empty)
        paste_action = QAction(self.icons.get("paste", QIcon()), "Paste", menu)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        
        # Check if clipboard has data
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        has_urls = mime_data.hasUrls() if mime_data else False
        
        # Determine paste target (selected directory or current directory)
        import os
        current_dir = os.path.dirname(paths[0]) if paths else os.getcwd()
        paste_target = paths[0] if only_dirs and single_item else current_dir
        
        paste_action.setEnabled(has_urls and (only_dirs or not selected_items))
        paste_action.triggered.connect(lambda: self.file_operations_service.paste(paste_target))
        menu.addAction(paste_action)
        
        # Duplicate
        duplicate_action = QAction(self.icons.get("duplicate", QIcon()), "Duplicate", menu)
        duplicate_action.setShortcut(QKeySequence("Ctrl+D"))
        duplicate_action.triggered.connect(lambda: [self.file_operations_service.duplicate_item(path) for path in paths])
        menu.addAction(duplicate_action)
        
        # Rename (only for single item)
        if single_item:
            rename_action = QAction(self.icons.get("rename", QIcon()), "Rename", menu)
            rename_action.setShortcut(QKeySequence("F2"))
            # Get just the filename without directory
            import os
            current_name = os.path.basename(paths[0])
            rename_action.triggered.connect(lambda: self._handle_rename(paths[0], current_name))
            menu.addAction(rename_action)
        
        # Delete
        delete_action = QAction(self.icons.get("delete", QIcon()), "Delete", menu)
        # Use string representation for the key which works across PySide6 versions
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(lambda: self._confirm_delete(paths))
        menu.addAction(delete_action)
    
    def _add_creation_operations(self, menu: QMenu, selected_items: List[Dict[str, Any]], only_dirs: bool):
        """
        Add creation operations to the menu.
        
        Args:
            menu: The menu to add actions to
            selected_items: List of selected items
            only_dirs: True if selection contains only directories
        """
        # Determine target directory
        if only_dirs and len(selected_items) == 1:
            target_dir = selected_items[0]['path']
        else:
            import os
            target_dir = os.getcwd()  # Current working directory as fallback
        
        # New file
        new_file_action = QAction(self.icons.get("new_file", QIcon()), "New File", menu)
        new_file_action.triggered.connect(lambda: self.file_operations_service.create_new_file(target_dir))
        menu.addAction(new_file_action)
        
        # New folder
        new_folder_action = QAction(self.icons.get("new_folder", QIcon()), "New Folder", menu)
        new_folder_action.triggered.connect(lambda: self.file_operations_service.create_new_folder(target_dir))
        menu.addAction(new_folder_action)
        
        # New from template (submenu)
        # This would be integrated with the template system
        # self._add_template_submenu(menu, target_dir)
    
    def _add_advanced_operations(self, menu: QMenu, selected_items: List[Dict[str, Any]], 
                               only_dirs: bool, only_files: bool, single_item: bool):
        """
        Add advanced operations to the menu.
        
        Args:
            menu: The menu to add actions to
            selected_items: List of selected items
            only_dirs: True if selection contains only directories
            only_files: True if selection contains only files
            single_item: True if selection contains only one item
        """
        paths = [item['path'] for item in selected_items]
        
        # Properties
        properties_action = QAction(self.icons.get("properties", QIcon()), "Properties", menu)
        properties_action.triggered.connect(lambda: self.show_properties.emit(paths))
        menu.addAction(properties_action)
        
        # Directory-specific operations
        if only_dirs:
            # Open terminal here
            terminal_action = QAction(self.icons.get("terminal", QIcon()), "Open Terminal Here", menu)
            terminal_action.triggered.connect(lambda: self._open_terminal(paths[0]))
            menu.addAction(terminal_action)
            
            # Find in folder
            find_action = QAction(self.icons.get("find", QIcon()), "Find in Folder", menu)
            find_action.triggered.connect(lambda: self._find_in_folder(paths[0]))
            menu.addAction(find_action)
        
        # Add to favorites
        favorites_action = QAction(self.icons.get("favorites", QIcon()), "Add to Favorites", menu)
        favorites_action.triggered.connect(lambda: self._add_to_favorites(paths))
        menu.addAction(favorites_action)
    
    def _confirm_delete(self, paths: List[str]):
        """
        Show confirmation dialog before deleting files.
        
        Args:
            paths: List of paths to delete
        """
        count = len(paths)
        if count == 1:
            msg = f"Are you sure you want to delete '{os.path.basename(paths[0])}'?"
        else:
            msg = f"Are you sure you want to delete {count} items?"
        
        # Use StandardButton which is available in PySide6
        result = QMessageBox.question(
            None,
            "Confirm Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            self.file_operations_service.delete_items(paths)
    
    def _open_items(self, paths: List[str]):
        """
        Open the selected items.
        
        Args:
            paths: List of paths to open
        """
        for path in paths:
            if os.path.isdir(path):
                # Emit signal to be handled by parent widget
                logger.debug(f"Directory activated: {path}")
                # Use a signal to change directory - implemented by parent
            else:
                # Open file with default application
                import platform
                import subprocess
                
                # Use direct platform-specific calls without try/except
                if platform.system() == 'Darwin':  # macOS
                    result = subprocess.call(('open', path))
                    if result != 0:
                        logger.error(f"Failed to open file {path} with return code {result}")
                    else:
                        logger.debug(f"Opened file: {path}")
                elif platform.system() == 'Windows':
                    subprocess.Popen(['start', path], shell=True)
                    logger.debug(f"Opened file: {path}")
                else:  # Linux and other Unix
                    result = subprocess.call(('xdg-open', path))
                    if result != 0:
                        logger.error(f"Failed to open file {path} with return code {result}")
                    else:
                        logger.debug(f"Opened file: {path}")
    
    def _open_in_new_window(self, paths: List[str]):
        """
        Open directories in new windows.
        
        Args:
            paths: List of paths to open in new windows
        """
        # This would be implemented with app-specific functionality
        # For now just log the action
        for path in paths:
            if os.path.isdir(path):
                logger.debug(f"Open in new window: {path}")
                # TODO: Implement open in new window functionality
    
    def _open_terminal(self, path: str):
        """
        Open a terminal at the specified path.
        
        Args:
            path: Path to open terminal at
        """
        import subprocess
        import platform
        
        # Direct calls without try/except
        if platform.system() == 'Darwin':  # macOS
            process = subprocess.Popen(['open', '-a', 'Terminal', path])
            if process.returncode is not None and process.returncode != 0:
                logger.error(f"Failed to open terminal at {path} with return code {process.returncode}")
            else:
                logger.debug(f"Opened terminal at {path}")
        elif platform.system() == 'Windows':
            process = subprocess.Popen(['cmd.exe'], cwd=path, shell=True)
            if process.returncode is not None and process.returncode != 0:
                logger.error(f"Failed to open terminal at {path} with return code {process.returncode}")
            else:
                logger.debug(f"Opened terminal at {path}")
        else:  # Linux
            process = subprocess.Popen(['x-terminal-emulator'], cwd=path)
            if process.returncode is not None and process.returncode != 0:
                logger.error(f"Failed to open terminal at {path} with return code {process.returncode}")
            else:
                logger.debug(f"Opened terminal at {path}")
    
    def _find_in_folder(self, path: str):
        """
        Open search in the specified folder.
        
        Args:
            path: Path to search in
        """
        # This would be integrated with the search panel
        logger.debug(f"Find in folder: {path}")
    
    def _add_to_favorites(self, paths: List[str]):
        """
        Add paths to favorites.
        
        Args:
            paths: List of paths to add to favorites
        """
        # This would be integrated with a favorites system
        logger.debug(f"Add to favorites: {paths}")
        
    def _handle_rename(self, path: str, current_name: str):
        """
        Handle renaming of a file or folder.
        
        Args:
            path: Full path to the file or folder to rename
            current_name: Current filename (without directory path)
        """
        # Show rename dialog using the imported QInputDialog
        new_name, ok = QInputDialog.getText(
            None, 
            "Rename", 
            "Enter new name:", 
            text=current_name
        )
        
        # Only proceed if user pressed OK and provided a different name
        if ok and new_name and new_name != current_name:
            # Call the file operations service to handle the rename
            # The service is expected to handle the full path logic internally
            new_path = self.file_operations_service.rename_item(path, new_name)
            
            # Check if rename was successful (service returns new path or empty string on failure)
            if new_path:
                logger.debug(f"Renamed '{current_name}' to '{new_name}'")
            else:
                logger.error(f"Failed to rename {path} to {new_name}")
