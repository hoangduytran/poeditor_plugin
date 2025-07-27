# Explorer Context Menu Implementation

**Date**: July 27, 2025, 14:00  
**Component**: Explorer Context Menu UI  
**Status**: Technical Documentation  
**Priority**: High

## Overview

This document details the implementation of the Explorer Context Menu system, which provides contextual operations for files and directories in the Explorer panel. The context menu dynamically adjusts its contents based on selection, location, and available actions.

## Class Implementation

```python
import os
from typing import List, Optional, Dict, Any

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QMenu, QWidget, QTreeView, QMessageBox, QInputDialog

from lg import logger
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager


class ExplorerContextMenu(QMenu):
    """
    Context menu for Explorer panel file operations.
    
    This class generates a context menu for file operations in the Explorer panel,
    with commands that adapt to the current selection and context.
    """
    
    def __init__(self, parent=None):
        """Initialize the Explorer context menu."""
        super().__init__(parent)
        
        self.file_ops = FileOperationsService()
        
        # Store items needed for action handling
        self._selected_paths = []
        self._context_path = ""
        self._is_directory_context = False
        
        # Initialize standard actions dictionary
        self._actions = {}
        self._create_standard_actions()
        
        # Initialize extension points
        self._extension_points = {
            "file_context_top": [],
            "file_context_mid": [],
            "file_context_bottom": [],
            "directory_context_top": [],
            "directory_context_mid": [],
            "directory_context_bottom": [],
            "background_context_top": [],
            "background_context_mid": [],
            "background_context_bottom": [],
        }
        
    def _create_standard_actions(self):
        """Create standard actions used in the context menu."""
        # File operations
        self._actions["open"] = QAction("Open", self)
        self._actions["open_with"] = QAction("Open With...", self)
        self._actions["open_containing"] = QAction("Open Containing Folder", self)
        
        # Clipboard operations
        self._actions["cut"] = QAction("Cut", self)
        self._actions["cut"].setShortcut(QKeySequence.Cut)
        
        self._actions["copy"] = QAction("Copy", self)
        self._actions["copy"].setShortcut(QKeySequence.Copy)
        
        self._actions["paste"] = QAction("Paste", self)
        self._actions["paste"].setShortcut(QKeySequence.Paste)
        
        # Item operations
        self._actions["rename"] = QAction("Rename", self)
        self._actions["rename"].setShortcut(QKeySequence("F2"))
        
        self._actions["duplicate"] = QAction("Duplicate", self)
        self._actions["duplicate"].setShortcut(QKeySequence("Ctrl+D"))
        
        self._actions["delete"] = QAction("Delete", self)
        self._actions["delete"].setShortcut(QKeySequence.Delete)
        
        # Creation actions
        self._actions["new_file"] = QAction("New File", self)
        self._actions["new_folder"] = QAction("New Folder", self)
        self._actions["new_folder"].setShortcut(QKeySequence("Ctrl+Shift+N"))
        
        # Connect standard action signals
        self._actions["cut"].triggered.connect(self._cut_selected)
        self._actions["copy"].triggered.connect(self._copy_selected)
        self._actions["paste"].triggered.connect(self._paste_to_context)
        self._actions["rename"].triggered.connect(self._rename_selected)
        self._actions["duplicate"].triggered.connect(self._duplicate_selected)
        self._actions["delete"].triggered.connect(self._delete_selected)
        self._actions["new_file"].triggered.connect(self._create_new_file)
        self._actions["new_folder"].triggered.connect(self._create_new_folder)
        
        # Load icons (would use themed icons in real implementation)
        # self._actions["open"].setIcon(QIcon(":/icons/open.svg"))
        # ...
    
    def show_menu(self, view: QTreeView, position: QPoint, 
                  selected_paths: List[str], context_path: str):
        """
        Show the context menu at the given position.
        
        Args:
            view: The tree view showing the context menu
            position: The position to show the menu at
            selected_paths: List of selected file paths
            context_path: The path where the context menu was requested
        """
        # Store context for action handlers
        self._selected_paths = selected_paths
        self._context_path = context_path
        self._is_directory_context = os.path.isdir(context_path) if context_path else False
        
        # Clear previous menu items
        self.clear()
        
        # Build the appropriate menu
        if not selected_paths:
            # Background context menu (no selection)
            self._build_background_menu()
        elif len(selected_paths) == 1 and selected_paths[0] == context_path:
            # Single item context menu
            if self._is_directory_context:
                self._build_directory_menu()
            else:
                self._build_file_menu()
        else:
            # Multiple selection context menu
            self._build_multi_selection_menu()
        
        # Show the menu
        self.exec_(view.mapToGlobal(position))
    
    def _build_file_menu(self):
        """Build menu for a single file."""
        # Add top extension point items
        self._add_extension_items("file_context_top")
        
        # Add standard file actions
        self.addAction(self._actions["open"])
        
        # Open With submenu
        open_with_menu = self.addMenu("Open With...")
        self._populate_open_with_menu(open_with_menu, self._selected_paths[0])
        
        self.addAction(self._actions["open_containing"])
        self.addSeparator()
        
        # Add clipboard actions
        self.addAction(self._actions["cut"])
        self.addAction(self._actions["copy"])
        
        # Add middle extension point items
        self._add_extension_items("file_context_mid")
        
        # Add file operations
        self.addSeparator()
        self.addAction(self._actions["rename"])
        self.addAction(self._actions["duplicate"])
        self.addSeparator()
        self.addAction(self._actions["delete"])
        
        # Add bottom extension point items
        self._add_extension_items("file_context_bottom")
    
    def _build_directory_menu(self):
        """Build menu for a directory."""
        # Add top extension point items
        self._add_extension_items("directory_context_top")
        
        # Add standard directory actions
        self.addAction(self._actions["open"])
        self.addSeparator()
        
        # Add clipboard actions
        self.addAction(self._actions["cut"])
        self.addAction(self._actions["copy"])
        
        # Add paste if clipboard has content
        clipboard_mode, clipboard_paths = self.file_ops.get_clipboard_contents()
        if clipboard_mode and clipboard_paths:
            self.addAction(self._actions["paste"])
        
        # Add middle extension point items
        self._add_extension_items("directory_context_mid")
        
        # Add directory operations
        self.addSeparator()
        self.addAction(self._actions["rename"])
        self.addAction(self._actions["duplicate"])
        self.addSeparator()
        
        # Add new item submenu
        new_menu = self.addMenu("New")
        new_menu.addAction(self._actions["new_file"])
        new_menu.addAction(self._actions["new_folder"])
        self._add_new_item_templates(new_menu)
        
        self.addSeparator()
        self.addAction(self._actions["delete"])
        
        # Add bottom extension point items
        self._add_extension_items("directory_context_bottom")
    
    def _build_background_menu(self):
        """Build menu for background (no selection)."""
        # Add top extension point items
        self._add_extension_items("background_context_top")
        
        # Add paste if clipboard has content
        clipboard_mode, clipboard_paths = self.file_ops.get_clipboard_contents()
        if clipboard_mode and clipboard_paths:
            self.addAction(self._actions["paste"])
            self.addSeparator()
        
        # Add middle extension point items
        self._add_extension_items("background_context_mid")
        
        # Add new item actions
        new_menu = self.addMenu("New")
        new_menu.addAction(self._actions["new_file"])
        new_menu.addAction(self._actions["new_folder"])
        self._add_new_item_templates(new_menu)
        
        # Add bottom extension point items
        self._add_extension_items("background_context_bottom")
    
    def _build_multi_selection_menu(self):
        """Build menu for multiple selected items."""
        # Add clipboard actions
        self.addAction(self._actions["cut"])
        self.addAction(self._actions["copy"])
        self.addSeparator()
        
        # Add delete action
        self.addAction(self._actions["delete"])
        
        # Add custom multi-selection actions
        # This could include batch operations, etc.
        multi_count = len(self._selected_paths)
        
        # Check if all selected items are files or directories
        all_files = all(not os.path.isdir(p) for p in self._selected_paths)
        all_dirs = all(os.path.isdir(p) for p in self._selected_paths)
        
        # Add specialized multi-selection actions based on selection type
        if all_files:
            # Add file-specific batch operations
            self._add_batch_file_operations()
        elif all_dirs:
            # Add directory-specific batch operations
            self._add_batch_directory_operations()
    
    def _add_batch_file_operations(self):
        """Add batch operations for multiple files."""
        # This would be implemented based on specific needs
        # Examples might include:
        # - Batch rename
        # - Compress selected files
        # - Convert file formats
        pass
    
    def _add_batch_directory_operations(self):
        """Add batch operations for multiple directories."""
        # This would be implemented based on specific needs
        # Examples might include:
        # - Merge directories
        # - Compare directories
        # - Calculate combined size
        pass
    
    def _add_extension_items(self, extension_point: str):
        """
        Add extension items for a specific extension point.
        
        Args:
            extension_point: The name of the extension point
        """
        extensions = self._extension_points.get(extension_point, [])
        if not extensions:
            return
            
        # Add all registered extension actions
        for extension in extensions:
            if callable(extension):
                # Execute function to get dynamic menu items
                extension(self, self._selected_paths, self._context_path)
            elif isinstance(extension, QAction):
                # Add action directly
                self.addAction(extension)
            elif isinstance(extension, dict) and "action" in extension:
                # Add action with visibility check
                if extension.get("visible", True):
                    self.addAction(extension["action"])
    
    def _populate_open_with_menu(self, menu: QMenu, file_path: str):
        """
        Populate the 'Open With' submenu for a file.
        
        Args:
            menu: The menu to populate
            file_path: The file path to get applications for
        """
        # This would integrate with system application registry
        # For demonstration, just add some placeholder items
        menu.addAction("Default Application")
        menu.addSeparator()
        menu.addAction("Choose Application...")
    
    def _add_new_item_templates(self, menu: QMenu):
        """
        Add new item templates to the 'New' submenu.
        
        Args:
            menu: The menu to add templates to
        """
        menu.addSeparator()
        
        # This would load templates from a configuration
        # For demonstration, just add some placeholder items
        menu.addAction("Text Document")
        menu.addAction("Markdown Document")
        menu.addAction("Python File")
        menu.addAction("HTML File")
        
        # Option to manage templates
        menu.addSeparator()
        menu.addAction("Manage Templates...")
    
    # =============== EXTENSION REGISTRATION ===============
    
    def register_extension(self, extension_point: str, action):
        """
        Register an extension to the context menu.
        
        Args:
            extension_point: The extension point name
            action: The action to add (QAction or callable)
        """
        if extension_point in self._extension_points:
            self._extension_points[extension_point].append(action)
    
    def unregister_extension(self, extension_point: str, action):
        """
        Unregister an extension from the context menu.
        
        Args:
            extension_point: The extension point name
            action: The action to remove
        """
        if extension_point in self._extension_points:
            try:
                self._extension_points[extension_point].remove(action)
            except ValueError:
                pass
    
    # =============== ACTION HANDLERS ===============
    
    def _cut_selected(self):
        """Cut selected items to clipboard."""
        if self._selected_paths:
            self.file_ops.cut_to_clipboard(self._selected_paths)
    
    def _copy_selected(self):
        """Copy selected items to clipboard."""
        if self._selected_paths:
            self.file_ops.copy_to_clipboard(self._selected_paths)
    
    def _paste_to_context(self):
        """Paste clipboard contents to context location."""
        target_dir = self._context_path
        
        # If context is a file, use its parent directory
        if not os.path.isdir(target_dir):
            target_dir = os.path.dirname(target_dir)
            
        # Check if we can paste here
        if self.file_ops.can_paste(target_dir):
            self.file_ops.paste(target_dir)
    
    def _rename_selected(self):
        """Rename selected item."""
        if len(self._selected_paths) == 1:
            path = self._selected_paths[0]
            
            # Get current name
            current_name = os.path.basename(path)
            
            # Show rename dialog
            new_name, ok = QInputDialog.getText(
                self.parentWidget(),
                "Rename",
                "Enter new name:",
                text=current_name
            )
            
            if ok and new_name and new_name != current_name:
                self.file_ops.rename_item(path, new_name)
    
    def _duplicate_selected(self):
        """Duplicate selected item."""
        if len(self._selected_paths) == 1:
            path = self._selected_paths[0]
            self.file_ops.duplicate_item(path)
    
    def _delete_selected(self):
        """Delete selected items."""
        if self._selected_paths:
            # Ask for confirmation if multiple items or a directory
            needs_confirm = len(self._selected_paths) > 1 or any(
                os.path.isdir(p) for p in self._selected_paths
            )
            
            if needs_confirm:
                count = len(self._selected_paths)
                msg = f"Are you sure you want to delete {count} items?" if count > 1 else \
                      "Are you sure you want to delete this folder?" if os.path.isdir(self._selected_paths[0]) else \
                      "Are you sure you want to delete this file?"
                
                result = QMessageBox.question(
                    self.parentWidget(),
                    "Confirm Delete",
                    msg,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if result != QMessageBox.Yes:
                    return
            
            # Perform deletion
            self.file_ops.delete_items(self._selected_paths)
    
    def _create_new_file(self):
        """Create a new file in the context location."""
        target_dir = self._context_path
        
        # If context is a file, use its parent directory
        if not os.path.isdir(target_dir):
            target_dir = os.path.dirname(target_dir)
            
        # Get filename from user
        name, ok = QInputDialog.getText(
            self.parentWidget(),
            "New File",
            "Enter file name:",
            text="New File.txt"
        )
        
        if ok and name:
            self.file_ops.create_new_file(target_dir, name)
    
    def _create_new_folder(self):
        """Create a new folder in the context location."""
        target_dir = self._context_path
        
        # If context is a file, use its parent directory
        if not os.path.isdir(target_dir):
            target_dir = os.path.dirname(target_dir)
            
        # Get folder name from user
        name, ok = QInputDialog.getText(
            self.parentWidget(),
            "New Folder",
            "Enter folder name:",
            text="New Folder"
        )
        
        if ok and name:
            self.file_ops.create_new_folder(target_dir, name)
```

## Integration with Explorer Panel

```python
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QTreeView, QFileSystemModel

from services.file_operations_service import FileOperationsService
from widgets.explorer_context_menu import ExplorerContextMenu

class ExplorerTreeView(QTreeView):
    """Tree view for the Explorer panel with context menu support."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.file_ops = FileOperationsService()
        self.context_menu = ExplorerContextMenu(self)
        
        # Configure view
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, position: QPoint):
        """
        Show the context menu at the given position.
        
        Args:
            position: The position to show the menu at
        """
        # Get the model index at the position
        index = self.indexAt(position)
        model = self.model()
        
        # Get the file path for the context
        context_path = ""
        if index.isValid():
            if isinstance(model, QFileSystemModel):
                context_path = model.filePath(index)
        else:
            # Clicked on background, use root path
            if isinstance(model, QFileSystemModel):
                context_path = model.rootPath()
        
        # Get all selected paths
        selected_paths = []
        for idx in self.selectedIndexes():
            if idx.column() == 0 and isinstance(model, QFileSystemModel):
                path = model.filePath(idx)
                if path not in selected_paths:
                    selected_paths.append(path)
        
        # Show the context menu
        self.context_menu.show_menu(self, position, selected_paths, context_path)
```

## Usage Examples

### Basic Context Menu

```python
# In the Explorer panel initialization
from widgets.explorer_context_menu import ExplorerContextMenu
from services.file_operations_service import FileOperationsService

class ExplorerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create the tree view
        self.tree_view = QTreeView()
        
        # Create and set up the model
        self.model = QFileSystemModel()
        self.model.setRootPath("/")
        self.tree_view.setModel(self.model)
        
        # Set up context menu
        self.file_ops = FileOperationsService()
        self.context_menu = ExplorerContextMenu(self)
        
        # Configure view for context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
    def _show_context_menu(self, position):
        """Handle context menu requests."""
        index = self.tree_view.indexAt(position)
        
        # Get context path
        context_path = ""
        if index.isValid():
            context_path = self.model.filePath(index)
        else:
            context_path = self.model.rootPath()
        
        # Get selected paths
        selected_paths = []
        for idx in self.tree_view.selectedIndexes():
            if idx.column() == 0:
                path = self.model.filePath(idx)
                if path not in selected_paths:
                    selected_paths.append(path)
        
        # Show menu
        self.context_menu.show_menu(self.tree_view, position, selected_paths, context_path)
```

### Adding Custom Extensions

```python
# Register a custom action to the directory context menu
from PySide6.QtGui import QAction

def add_custom_actions(explorer_panel):
    """Add custom actions to the explorer context menu."""
    # Create a custom action
    custom_action = QAction("Custom Command", explorer_panel)
    custom_action.triggered.connect(lambda: custom_command_handler(explorer_panel))
    
    # Register with the context menu
    explorer_panel.context_menu.register_extension("directory_context_bottom", custom_action)
    
    # Add a dynamic extension that varies based on selection
    explorer_panel.context_menu.register_extension(
        "file_context_mid", 
        lambda menu, paths, context: add_dynamic_items(menu, paths, context)
    )

def custom_command_handler(panel):
    """Handle the custom command."""
    # Implementation of custom command
    print("Custom command triggered")
    
def add_dynamic_items(menu, paths, context):
    """Add dynamic items based on selection."""
    # Check selection and add appropriate actions
    if paths and all(path.endswith('.py') for path in paths):
        python_action = QAction("Run Python Script", menu)
        python_action.triggered.connect(lambda: run_python_script(paths[0]))
        menu.addAction(python_action)
    
def run_python_script(path):
    """Run a Python script."""
    # Implementation to run Python script
    print(f"Running Python script: {path}")
```

## Context Menu Structure

The Explorer Context Menu adapts its structure based on the current context:

### Single File Menu Structure

```
[File-specific Extensions - Top]
Open
Open With >
   Default Application
   --------------------
   Choose Application...
Open Containing Folder
--------------------
Cut
Copy
[File-specific Extensions - Middle]
--------------------
Rename
Duplicate
--------------------
Delete
[File-specific Extensions - Bottom]
```

### Directory Menu Structure

```
[Directory-specific Extensions - Top]
Open
--------------------
Cut
Copy
Paste (if clipboard has content)
[Directory-specific Extensions - Middle]
--------------------
Rename
Duplicate
--------------------
New >
   New File
   New Folder
   --------------------
   Text Document
   Markdown Document
   Python File
   HTML File
   --------------------
   Manage Templates...
--------------------
Delete
[Directory-specific Extensions - Bottom]
```

### Background Menu Structure (No Selection)

```
[Background-specific Extensions - Top]
Paste (if clipboard has content)
--------------------
[Background-specific Extensions - Middle]
New >
   New File
   New Folder
   --------------------
   Text Document
   Markdown Document
   Python File
   HTML File
   --------------------
   Manage Templates...
[Background-specific Extensions - Bottom]
```

### Multiple Selection Menu Structure

```
Cut
Copy
--------------------
Delete
[Multi-selection specific options based on selection type]
```

## Extension Points

The context menu system provides several extension points:

1. **file_context_top**: Top of single file context menu
2. **file_context_mid**: Middle of single file context menu
3. **file_context_bottom**: Bottom of single file context menu
4. **directory_context_top**: Top of directory context menu
5. **directory_context_mid**: Middle of directory context menu
6. **directory_context_bottom**: Bottom of directory context menu
7. **background_context_top**: Top of background context menu
8. **background_context_mid**: Middle of background context menu
9. **background_context_bottom**: Bottom of background context menu

Plugins can register actions at these extension points to extend the menu functionality.

## Integration with Keyboard Shortcuts

The context menu includes keyboard shortcut information:

1. **Cut**: Ctrl+X (platform-dependent)
2. **Copy**: Ctrl+C (platform-dependent)
3. **Paste**: Ctrl+V (platform-dependent)
4. **Rename**: F2
5. **Duplicate**: Ctrl+D
6. **Delete**: Delete key
7. **New Folder**: Ctrl+Shift+N

The shortcuts are displayed in the menu and also work when the Explorer panel has focus.

## Customization Capabilities

The context menu system is designed for customization:

1. **Extension registration**: Plugins can add custom actions
2. **Dynamic content**: Menu items can be conditionally shown based on selection
3. **Template system**: File templates in the "New" menu can be customized
4. **Action overriding**: Core actions can be replaced or modified
5. **Appearance theming**: Menu styling integrates with the application theme
