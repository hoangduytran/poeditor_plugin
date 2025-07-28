"""
Explorer Context Menu

Provides context menu functionality for the Explorer panel, integrating with
file operations service, undo/redo manager, and supporting various selection states.
"""

import os
from typing import List, Optional, Dict, Any

from PySide6.QtWidgets import QMenu, QMessageBox, QApplication
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QIcon, QKeySequence, QAction

from lg import logger
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager


class ExplorerContextMenu(QObject):
    """
    Context menu manager for the Explorer panel.
    
    Provides context-sensitive menus for files, folders, and empty areas,
    with appropriate operations based on selection state.
    """
    
    # Signals for operations that require additional UI
    show_properties = Signal(list)  # list of file paths
    show_open_with = Signal(list)   # list of file paths
    
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
        
        # Icons for common operations
        self._load_icons()
    
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
    
    def create_menu(self, selected_items: List[Dict[str, Any]]) -> QMenu:
        """
        Create a context menu based on the selected items.
        
        Args:
            selected_items: List of selected items, each is a dict with:
                - 'path': str - Full path to the item
                - 'is_dir': bool - True if directory, False if file
                - 'name': str - Item name
        
        Returns:
            QMenu: The context menu
        """
        menu = QMenu()
        
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
                self.file_operations_service.get_current_directory()
            )
        )
        menu.addAction(paste_action)
        
        # View options
        menu.addSeparator()
        
        # Terminal here
        terminal_action = QAction(self.icons.get("terminal", QIcon()), "Open Terminal Here", menu)
        terminal_action.triggered.connect(
            lambda: self._open_terminal(self.file_operations_service.get_current_directory())
        )
        menu.addAction(terminal_action)
        
        # Refresh
        refresh_action = QAction("Refresh", menu)
        refresh_action.triggered.connect(
            lambda: self.file_operations_service.refresh()
        )
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
        delete_action.setShortcut(QKeySequence(Qt.Key.Key_Delete))
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
                
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(('open', path))
                    elif platform.system() == 'Windows':
                        subprocess.Popen(['start', path], shell=True)
                    else:  # Linux and other Unix
                        subprocess.call(('xdg-open', path))
                    logger.debug(f"Opened file: {path}")
                except Exception as e:
                    logger.error(f"Failed to open file {path}: {e}")
    
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
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', '-a', 'Terminal', path])
            elif platform.system() == 'Windows':
                subprocess.Popen(['cmd.exe'], cwd=path, shell=True)
            else:  # Linux
                subprocess.Popen(['x-terminal-emulator'], cwd=path)
            logger.debug(f"Opened terminal at {path}")
        except Exception as e:
            logger.error(f"Failed to open terminal at {path}: {e}")
    
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
            path: Path to the file or folder to rename
            current_name: Current name of the file or folder
        """
        from PySide6.QtWidgets import QInputDialog
        
        # Show rename dialog
        new_name, ok = QInputDialog.getText(
            None, 
            "Rename", 
            "Enter new name:", 
            text=current_name
        )
        
        if ok and new_name and new_name != current_name:
            try:
                import os
                dir_path = os.path.dirname(path)
                self.file_operations_service.rename_item(path, new_name)
            except Exception as e:
                logger.error(f"Error renaming {path} to {new_name}: {e}")
