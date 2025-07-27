# Context Menu Implementation Details

**Date**: July 27, 2025, 13:00  
**Component**: Explorer Context Menu Implementation  
**Status**: Technical Documentation  
**Priority**: High

## Context Menu Construction

The Explorer Context Menu implementation will leverage PySide6's QMenu and QAction classes to create a dynamic context menu that adapts based on the selected item(s) and their states.

### Core Implementation

```python
from PySide6.QtWidgets import QMenu, QAction
from PySide6.QtCore import Qt
from typing import List, Dict, Any, Optional
from lg import logger

class ExplorerContextMenu:
    def __init__(self, parent=None):
        self.file_operations_service = None  # Will be injected
        self.parent = parent
        self.settings = None  # Will be injected
    
    def set_file_operations_service(self, service):
        self.file_operations_service = service
    
    def set_settings(self, settings):
        self.settings = settings
    
    def create_menu(self, paths: List[str]) -> QMenu:
        """Create a context menu for the selected path(s)."""
        if not paths:
            return self._create_empty_area_menu()
            
        menu = QMenu(self.parent)
        
        # Determine what type of items we're working with
        is_single_selection = len(paths) == 1
        is_folder = all(self._is_directory(path) for path in paths)
        
        # Add basic operations
        self._add_open_actions(menu, paths, is_single_selection, is_folder)
        menu.addSeparator()
        
        self._add_clipboard_actions(menu, paths)
        menu.addSeparator()
        
        self._add_new_item_actions(menu, paths, is_folder)
        menu.addSeparator()
        
        self._add_delete_rename_actions(menu, paths, is_single_selection)
        menu.addSeparator()
        
        self._add_path_actions(menu, paths, is_single_selection)
        menu.addSeparator()
        
        self._add_utility_actions(menu)
        
        # Allow plugins to extend the menu
        self._extend_from_plugins(menu, paths, is_folder)
        
        return menu
    
    def _create_empty_area_menu(self) -> QMenu:
        """Create a context menu for an empty area (no selection)."""
        menu = QMenu(self.parent)
        
        # New file/folder options
        new_file_action = QAction("New File...", menu)
        new_file_action.triggered.connect(lambda: self._on_new_file())
        menu.addAction(new_file_action)
        
        new_folder_action = QAction("New Folder", menu)
        new_folder_action.triggered.connect(lambda: self._on_new_folder())
        menu.addAction(new_folder_action)
        
        menu.addSeparator()
        
        # Paste (only if clipboard has content)
        if self.file_operations_service and self.file_operations_service.has_clipboard_content():
            paste_action = QAction("Paste", menu)
            paste_action.triggered.connect(lambda: self._on_paste())
            menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # Refresh explorer
        refresh_action = QAction("Refresh Explorer", menu)
        refresh_action.triggered.connect(lambda: self._on_refresh())
        menu.addAction(refresh_action)
        
        return menu
    
    def _add_open_actions(self, menu: QMenu, paths: List[str], is_single: bool, is_folder: bool):
        """Add Open and Open With actions."""
        # Basic Open action
        open_action = QAction("Open", menu)
        open_action.triggered.connect(lambda: self._on_open(paths))
        menu.addAction(open_action)
        
        # Open With (for files only)
        if is_single and not is_folder:
            open_with_action = QAction("Open With...", menu)
            open_with_action.triggered.connect(lambda: self._on_open_with(paths[0]))
            menu.addAction(open_with_action)
    
    def _add_clipboard_actions(self, menu: QMenu, paths: List[str]):
        """Add Cut, Copy, Paste, Duplicate actions."""
        cut_action = QAction("Cut", menu)
        cut_action.triggered.connect(lambda: self._on_cut(paths))
        menu.addAction(cut_action)
        
        copy_action = QAction("Copy", menu)
        copy_action.triggered.connect(lambda: self._on_copy(paths))
        menu.addAction(copy_action)
        
        # Paste (only if clipboard has content and at least one folder is selected)
        if self.file_operations_service and self.file_operations_service.has_clipboard_content():
            paste_targets = [p for p in paths if self._is_directory(p)]
            if paste_targets:
                paste_action = QAction("Paste", menu)
                paste_action.triggered.connect(lambda: self._on_paste(paste_targets[0]))
                menu.addAction(paste_action)
        
        # Duplicate (enabled for single selection)
        if len(paths) == 1:
            duplicate_action = QAction("Duplicate", menu)
            duplicate_action.triggered.connect(lambda: self._on_duplicate(paths[0]))
            menu.addAction(duplicate_action)
    
    def _add_new_item_actions(self, menu: QMenu, paths: List[str], is_folder: bool):
        """Add New File and New Folder actions."""
        target_dir = paths[0] if is_folder and len(paths) == 1 else self._get_parent_dir(paths[0])
        
        new_file_action = QAction("New File...", menu)
        new_file_action.triggered.connect(lambda: self._on_new_file(target_dir))
        menu.addAction(new_file_action)
        
        new_folder_action = QAction("New Folder", menu)
        new_folder_action.triggered.connect(lambda: self._on_new_folder(target_dir))
        menu.addAction(new_folder_action)
    
    def _add_delete_rename_actions(self, menu: QMenu, paths: List[str], is_single: bool):
        """Add Delete and Rename actions."""
        delete_action = QAction("Delete", menu)
        delete_action.triggered.connect(lambda: self._on_delete(paths))
        menu.addAction(delete_action)
        
        # Rename (only for single selection)
        if is_single:
            rename_action = QAction("Rename", menu)
            rename_action.triggered.connect(lambda: self._on_rename(paths[0]))
            menu.addAction(rename_action)
    
    def _add_path_actions(self, menu: QMenu, paths: List[str], is_single: bool):
        """Add Copy Path and Copy Relative Path actions."""
        copy_path_action = QAction("Copy Path", menu)
        copy_path_action.triggered.connect(lambda: self._on_copy_path(paths))
        menu.addAction(copy_path_action)
        
        copy_rel_path_action = QAction("Copy Relative Path", menu)
        copy_rel_path_action.triggered.connect(lambda: self._on_copy_relative_path(paths))
        menu.addAction(copy_rel_path_action)
    
    def _add_utility_actions(self, menu: QMenu):
        """Add utility actions like Refresh."""
        refresh_action = QAction("Refresh Explorer", menu)
        refresh_action.triggered.connect(lambda: self._on_refresh())
        menu.addAction(refresh_action)
    
    def _extend_from_plugins(self, menu: QMenu, paths: List[str], is_folder: bool):
        """Allow plugins to extend the context menu."""
        # This would be implemented with the plugin system
        pass
    
    # Helper methods
    def _is_directory(self, path: str) -> bool:
        """Check if the path is a directory."""
        # Implementation omitted for brevity
        pass
    
    def _get_parent_dir(self, path: str) -> str:
        """Get the parent directory of a path."""
        # Implementation omitted for brevity
        pass
    
    # Action handlers
    def _on_open(self, paths: List[str]):
        """Handle the Open action."""
        for path in paths:
            if self._is_directory(path):
                # Expand directory in tree view
                logger.debug(f"Expanding directory: {path}")
            else:
                # Open file
                logger.debug(f"Opening file: {path}")
    
    def _on_open_with(self, path: str):
        """Handle the Open With action."""
        # Implementation omitted for brevity
        pass
    
    def _on_cut(self, paths: List[str]):
        """Handle the Cut action."""
        if self.file_operations_service:
            self.file_operations_service.copy_items(paths, cut=True)
            logger.debug(f"Cut items to clipboard: {paths}")
    
    def _on_copy(self, paths: List[str]):
        """Handle the Copy action."""
        if self.file_operations_service:
            self.file_operations_service.copy_items(paths, cut=False)
            logger.debug(f"Copied items to clipboard: {paths}")
    
    def _on_paste(self, target_dir: Optional[str] = None):
        """Handle the Paste action."""
        if self.file_operations_service:
            results = self.file_operations_service.paste_items(target_dir)
            logger.debug(f"Pasted items to {target_dir}: {results}")
    
    def _on_duplicate(self, path: str):
        """Handle the Duplicate action."""
        if self.file_operations_service:
            result = self.file_operations_service.duplicate_item(path)
            logger.debug(f"Duplicated {path} to {result}")
    
    def _on_new_file(self, parent_dir: Optional[str] = None):
        """Handle the New File action."""
        # Show new file dialog and create file
        # Implementation omitted for brevity
        pass
    
    def _on_new_folder(self, parent_dir: Optional[str] = None):
        """Handle the New Folder action."""
        # Show new folder dialog and create folder
        # Implementation omitted for brevity
        pass
    
    def _on_delete(self, paths: List[str]):
        """Handle the Delete action."""
        if self.file_operations_service:
            # Check for Shift key to determine permanent delete
            permanent = False  # This would come from key state
            result = self.file_operations_service.delete_items(paths, permanent)
            logger.debug(f"Deleted items: {paths}, permanent: {permanent}, result: {result}")
    
    def _on_rename(self, path: str):
        """Handle the Rename action."""
        # Show rename dialog and rename file/folder
        # Implementation omitted for brevity
        pass
    
    def _on_copy_path(self, paths: List[str]):
        """Handle the Copy Path action."""
        # Copy absolute paths to clipboard
        # Implementation omitted for brevity
        pass
    
    def _on_copy_relative_path(self, paths: List[str]):
        """Handle the Copy Relative Path action."""
        # Copy paths relative to workspace root
        # Implementation omitted for brevity
        pass
    
    def _on_refresh(self):
        """Handle the Refresh Explorer action."""
        # Refresh the explorer view
        # Implementation omitted for brevity
        pass
```

### Menu Integration with File Explorer

```python
from PySide6.QtWidgets import QTreeView, QAbstractItemView
from PySide6.QtCore import Qt, QPoint

class ExplorerTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context_menu = ExplorerContextMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Common setup
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
    
    def set_file_operations_service(self, service):
        self.context_menu.set_file_operations_service(service)
    
    def set_settings(self, settings):
        self.context_menu.set_settings(settings)
    
    def _show_context_menu(self, position: QPoint):
        """Show the context menu at the specified position."""
        # Get selected items
        selected_paths = self._get_selected_paths()
        
        # Create and show the menu
        menu = self.context_menu.create_menu(selected_paths)
        menu.exec_(self.viewport().mapToGlobal(position))
    
    def _get_selected_paths(self) -> List[str]:
        """Get the paths of the currently selected items."""
        # Implementation depends on the model used
        # This is a placeholder
        selected_indices = self.selectionModel().selectedIndexes()
        unique_rows = set(index.row() for index in selected_indices)
        
        # In a real implementation, we would convert model indices to file paths
        paths = []
        for row in unique_rows:
            # This would access the actual model data
            path = self.model().data(self.model().index(row, 0), role=Qt.UserRole)
            paths.append(path)
        
        return paths
```

### Command Integration

To connect the context menu with the command infrastructure, we integrate with the application's command system:

```python
class ExplorerCommands:
    """Registration of explorer commands with the application command system."""
    
    def __init__(self, file_operations_service):
        self.file_operations_service = file_operations_service
    
    def register_commands(self, command_registry):
        """Register explorer commands with the application command registry."""
        # File operations
        command_registry.register('explorer.copy', self._handle_copy)
        command_registry.register('explorer.cut', self._handle_cut)
        command_registry.register('explorer.paste', self._handle_paste)
        command_registry.register('explorer.delete', self._handle_delete)
        command_registry.register('explorer.rename', self._handle_rename)
        command_registry.register('explorer.duplicate', self._handle_duplicate)
        
        # Item creation
        command_registry.register('explorer.newFile', self._handle_new_file)
        command_registry.register('explorer.newFolder', self._handle_new_folder)
        
        # Undo/Redo
        command_registry.register('explorer.undo', self._handle_undo)
        command_registry.register('explorer.redo', self._handle_redo)
        
        # Utilities
        command_registry.register('explorer.refresh', self._handle_refresh)
        command_registry.register('explorer.copyPath', self._handle_copy_path)
        command_registry.register('explorer.copyRelativePath', self._handle_copy_relative_path)
    
    # Command handlers - these would be connected to the FileOperationService
    def _handle_copy(self, paths):
        return self.file_operations_service.copy_items(paths, cut=False)
    
    def _handle_cut(self, paths):
        return self.file_operations_service.copy_items(paths, cut=True)
    
    def _handle_paste(self, target_dir):
        return self.file_operations_service.paste_items(target_dir)
    
    # Additional handlers omitted for brevity
```

## Key Integration Points

1. **Event Handling**: The context menu connects user interactions to file operation services
2. **Extensibility**: The `_extend_from_plugins` method allows third-party plugins to add menu items
3. **Command Architecture**: All actions are routed through a command system for central management
4. **Visual Feedback**: Status messages are logged for operations to provide user feedback
5. **Error Handling**: Each operation would include robust error handling (omitted in samples for brevity)
