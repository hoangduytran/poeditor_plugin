# Explorer Context Menu Integration Guide

**Date**: July 27, 2025, 14:30  
**Component**: Explorer Context Menu Integration  
**Status**: Technical Documentation  
**Priority**: Medium

## Overview

This document provides a guide for integrating the Explorer Context Menu system with other components of the application and extending its functionality through plugins. It covers integration points, customization options, and best practices.

## Core Integration Points

### 1. Explorer Panel Integration

The Explorer Context Menu is designed to be integrated with the Explorer panel as follows:

```python
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QTreeView, QWidget, QVBoxLayout

from services.file_operations_service import FileOperationsService
from widgets.explorer_context_menu import ExplorerContextMenu
from models.file_system_model import EnhancedFileSystemModel

class ExplorerPanel(QWidget):
    """Main panel for Explorer functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.file_ops = FileOperationsService()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tree view
        self.tree_view = QTreeView(self)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # Set up the model
        self.model = EnhancedFileSystemModel()
        self.tree_view.setModel(self.model)
        
        # Create context menu
        self.context_menu = ExplorerContextMenu(self)
        
        # Add tree view to layout
        layout.addWidget(self.tree_view)
        
    def _show_context_menu(self, position: QPoint):
        """Show the context menu at the given position."""
        # Get selected paths
        selected_paths = self._get_selected_paths()
        
        # Get context path (where right-click occurred)
        context_path = self._get_path_at_position(position)
        
        # Show the context menu
        self.context_menu.show_menu(self.tree_view, position, selected_paths, context_path)
        
    def _get_selected_paths(self) -> List[str]:
        """Get the paths of selected items."""
        selected_paths = []
        for index in self.tree_view.selectedIndexes():
            if index.column() == 0:  # Only process first column
                path = self.model.filePath(index)
                if path not in selected_paths:
                    selected_paths.append(path)
        return selected_paths
        
    def _get_path_at_position(self, position: QPoint) -> str:
        """Get the path at the given position."""
        index = self.tree_view.indexAt(position)
        if index.isValid():
            return self.model.filePath(index)
        else:
            # Clicked on empty area, use root path
            return self.model.rootPath()
```

### 2. Main Application Integration

To integrate the Explorer Context Menu with the main application:

```python
from PySide6.QtWidgets import QMainWindow, QAction
from PySide6.QtGui import QKeySequence

class MainAppWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Create explorer panel
        self.explorer_panel = ExplorerPanel(self)
        self.setCentralWidget(self.explorer_panel)
        
        # Create edit menu
        edit_menu = self.menuBar().addMenu("Edit")
        
        # Add undo/redo actions
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.explorer_panel.file_ops.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.explorer_panel.file_ops.redo)
        edit_menu.addAction(redo_action)
        
        # Connect to undo/redo manager signals
        undo_redo = self.explorer_panel.file_ops.undo_redo_manager
        undo_redo.undoAvailable.connect(undo_action.setEnabled)
        undo_redo.redoAvailable.connect(redo_action.setEnabled)
        undo_redo.undoTextChanged.connect(undo_action.setText)
        undo_redo.redoTextChanged.connect(redo_action.setText)
        
        # Initialize action states
        undo_action.setEnabled(False)
        redo_action.setEnabled(False)
```

## Plugin Extension System

### 1. Defining a Plugin Interface

To allow plugins to extend the context menu:

```python
from typing import Protocol, List, Any, Callable, Optional
from PySide6.QtWidgets import QMenu, QAction

class ExplorerContextMenuExtension(Protocol):
    """Protocol for Explorer context menu extensions."""
    
    def get_file_context_actions(self, paths: List[str]) -> List[Any]:
        """
        Get actions for the file context menu.
        
        Args:
            paths: List of selected file paths
            
        Returns:
            List of actions (QAction or dict with 'action' and 'visible' keys)
        """
        ...
        
    def get_directory_context_actions(self, paths: List[str]) -> List[Any]:
        """
        Get actions for the directory context menu.
        
        Args:
            paths: List of selected directory paths
            
        Returns:
            List of actions (QAction or dict with 'action' and 'visible' keys)
        """
        ...
        
    def get_background_context_actions(self, directory_path: str) -> List[Any]:
        """
        Get actions for the background context menu.
        
        Args:
            directory_path: The directory path where the menu was invoked
            
        Returns:
            List of actions (QAction or dict with 'action' and 'visible' keys)
        """
        ...
```

### 2. Plugin Registration

Allow plugins to register extensions:

```python
class PluginManager:
    """Manager for application plugins."""
    
    def __init__(self):
        self.explorer_context_extensions = []
        
    def register_explorer_context_extension(self, extension):
        """Register an Explorer context menu extension."""
        if extension not in self.explorer_context_extensions:
            self.explorer_context_extensions.append(extension)
            
    def unregister_explorer_context_extension(self, extension):
        """Unregister an Explorer context menu extension."""
        if extension in self.explorer_context_extensions:
            self.explorer_context_extensions.remove(extension)
            
    def get_explorer_context_extensions(self):
        """Get all registered Explorer context menu extensions."""
        return self.explorer_context_extensions
```

### 3. Extension Integration

Modify the context menu to use extensions:

```python
class ExplorerContextMenu(QMenu):
    # ... existing code ...
    
    def __init__(self, parent=None, plugin_manager=None):
        super().__init__(parent)
        
        self.file_ops = FileOperationsService()
        self.plugin_manager = plugin_manager
        
        # ... rest of initialization ...
    
    def _build_file_menu(self):
        """Build menu for a single file."""
        # ... existing code ...
        
        # Add plugin extensions
        if self.plugin_manager:
            extensions = self.plugin_manager.get_explorer_context_extensions()
            for extension in extensions:
                actions = extension.get_file_context_actions(self._selected_paths)
                if actions:
                    # Add a separator if needed
                    if len(self.actions()) > 0:
                        self.addSeparator()
                        
                    # Add the actions
                    for action in actions:
                        if isinstance(action, dict) and 'action' in action:
                            if action.get('visible', True):
                                self.addAction(action['action'])
                        elif isinstance(action, QAction):
                            self.addAction(action)
        
        # ... rest of the method ...
```

## Example Plugin Implementation

### Custom File Type Plugin

```python
from PySide6.QtWidgets import QAction, QMenu
from PySide6.QtGui import QIcon
import os

class PythonFilePlugin:
    """Plugin for Python file context menu actions."""
    
    def __init__(self):
        pass
        
    def get_file_context_actions(self, paths: List[str]) -> List[Any]:
        """Get actions for Python files."""
        # Only show for Python files
        if not all(path.endswith('.py') for path in paths):
            return []
            
        actions = []
        
        # Run script action
        run_action = QAction("Run Python Script", None)
        run_action.triggered.connect(lambda: self._run_script(paths[0]))
        actions.append(run_action)
        
        # Open in REPL action
        repl_action = QAction("Open in Python REPL", None)
        repl_action.triggered.connect(lambda: self._open_in_repl(paths[0]))
        actions.append(repl_action)
        
        return actions
        
    def get_directory_context_actions(self, paths: List[str]) -> List[Any]:
        """Get actions for directories."""
        actions = []
        
        # Check for Python project
        if any(os.path.exists(os.path.join(path, 'setup.py')) for path in paths):
            # Install dependencies action
            install_action = QAction("Install Python Dependencies", None)
            install_action.triggered.connect(lambda: self._install_dependencies(paths[0]))
            actions.append(install_action)
            
        return actions
        
    def get_background_context_actions(self, directory_path: str) -> List[Any]:
        """Get actions for background context."""
        actions = []
        
        # New Python file action in a submenu
        python_action = QAction("New Python Script", None)
        python_action.triggered.connect(lambda: self._create_python_file(directory_path))
        
        # We need to return a dict with the action and some metadata
        return [{'action': python_action, 'visible': True}]
        
    def _run_script(self, path: str):
        """Run a Python script."""
        # Implementation
        print(f"Running Python script: {path}")
        
    def _open_in_repl(self, path: str):
        """Open a file in the Python REPL."""
        # Implementation
        print(f"Opening in REPL: {path}")
        
    def _install_dependencies(self, path: str):
        """Install Python dependencies."""
        # Implementation
        print(f"Installing dependencies in: {path}")
        
    def _create_python_file(self, directory: str):
        """Create a new Python file."""
        # Implementation
        print(f"Creating Python file in: {directory}")
```

## Dynamic Menu Customization

### User Template System

The Explorer Context Menu can be extended with user-defined templates:

```python
class TemplateManager:
    """Manager for file templates."""
    
    def __init__(self, settings=None):
        self.settings = settings
        self.templates = []
        self._load_templates()
        
    def _load_templates(self):
        """Load templates from settings."""
        if self.settings:
            self.settings.beginGroup("explorer/templates")
            size = self.settings.beginReadArray("items")
            
            for i in range(size):
                self.settings.setArrayIndex(i)
                template = {
                    'name': self.settings.value("name"),
                    'description': self.settings.value("description"),
                    'icon': self.settings.value("icon"),
                    'content': self.settings.value("content", ""),
                    'extension': self.settings.value("extension")
                }
                self.templates.append(template)
                
            self.settings.endArray()
            self.settings.endGroup()
            
    def add_template(self, name, description, content, extension, icon=None):
        """Add a new template."""
        template = {
            'name': name,
            'description': description,
            'content': content,
            'extension': extension,
            'icon': icon
        }
        
        self.templates.append(template)
        self._save_templates()
        
        return template
        
    def remove_template(self, name):
        """Remove a template by name."""
        self.templates = [t for t in self.templates if t['name'] != name]
        self._save_templates()
        
    def get_templates(self):
        """Get all templates."""
        return self.templates
        
    def _save_templates(self):
        """Save templates to settings."""
        if not self.settings:
            return
            
        self.settings.beginGroup("explorer/templates")
        self.settings.beginWriteArray("items")
        
        for i, template in enumerate(self.templates):
            self.settings.setArrayIndex(i)
            self.settings.setValue("name", template['name'])
            self.settings.setValue("description", template['description'])
            self.settings.setValue("icon", template['icon'])
            self.settings.setValue("content", template['content'])
            self.settings.setValue("extension", template['extension'])
            
        self.settings.endArray()
        self.settings.endGroup()
```

### Integrating Templates with Context Menu

```python
def _add_new_item_templates(self, menu: QMenu):
    """Add file templates to the 'New' menu."""
    menu.addSeparator()
    
    if hasattr(self, 'template_manager'):
        # Add templates from the template manager
        templates = self.template_manager.get_templates()
        
        for template in templates:
            action = QAction(template['name'], self)
            if template.get('icon'):
                action.setIcon(QIcon(template['icon']))
            
            # Create a closure to capture the template
            def create_from_template(t=template):
                self._create_from_template(t)
            
            action.triggered.connect(create_from_template)
            menu.addAction(action)
    
    # Add option to manage templates
    menu.addSeparator()
    manage_action = QAction("Manage Templates...", self)
    manage_action.triggered.connect(self._manage_templates)
    menu.addAction(manage_action)

def _create_from_template(self, template):
    """Create a new file from a template."""
    target_dir = self._context_path
    
    # If context is a file, use its parent directory
    if not os.path.isdir(target_dir):
        target_dir = os.path.dirname(target_dir)
        
    # Get filename from user
    name, ok = QInputDialog.getText(
        self.parentWidget(),
        f"New {template['name']}",
        "Enter file name:",
        text=f"New{template['extension']}"
    )
    
    if ok and name:
        # Ensure extension is present
        if not name.endswith(template['extension']):
            name += template['extension']
            
        # Create the file
        path = os.path.join(target_dir, name)
        try:
            with open(path, 'w') as f:
                f.write(template['content'])
                
            # Record for undo/redo
            operation = FileOperation(
                operation_type='new_file',
                source_paths=[target_dir],
                target_path=path,
                timestamp=datetime.now(),
                is_undoable=True,
                undo_data={'created_path': path}
            )
            self.file_ops.undo_redo_manager.record_operation(operation)
            
        except IOError as e:
            QMessageBox.critical(
                self.parentWidget(),
                "Error",
                f"Could not create file: {str(e)}"
            )

def _manage_templates(self):
    """Open the template management dialog."""
    # This would open a dialog to manage templates
    # Implementation would depend on the application's UI framework
    pass
```

## Application-wide Shortcuts

The Explorer Context Menu can be integrated with the application's keyboard shortcut system:

```python
def setup_shortcuts(self, main_window):
    """Set up keyboard shortcuts for file operations."""
    # Copy shortcut
    copy_shortcut = QShortcut(QKeySequence.Copy, main_window)
    copy_shortcut.activated.connect(self._copy_selected)
    
    # Cut shortcut
    cut_shortcut = QShortcut(QKeySequence.Cut, main_window)
    cut_shortcut.activated.connect(self._cut_selected)
    
    # Paste shortcut
    paste_shortcut = QShortcut(QKeySequence.Paste, main_window)
    paste_shortcut.activated.connect(self._paste_to_context)
    
    # Delete shortcut
    delete_shortcut = QShortcut(QKeySequence.Delete, main_window)
    delete_shortcut.activated.connect(self._delete_selected)
    
    # Rename shortcut (F2)
    rename_shortcut = QShortcut(QKeySequence("F2"), main_window)
    rename_shortcut.activated.connect(self._rename_selected)
    
    # New folder shortcut
    new_folder_shortcut = QShortcut(QKeySequence("Ctrl+Shift+N"), main_window)
    new_folder_shortcut.activated.connect(self._create_new_folder)
```

## Event Handling and Notifications

The Explorer Context Menu can integrate with the application's event system for notifications:

```python
def __init__(self, parent=None, event_bus=None):
    super().__init__(parent)
    
    self.file_ops = FileOperationsService()
    self.event_bus = event_bus
    
    # Connect to file operations signals
    self.file_ops.operationCompleted.connect(self._on_operation_completed)
    self.file_ops.operationFailed.connect(self._on_operation_failed)
    
def _on_operation_completed(self, operation_type, source_paths, target_path):
    """Handle operation completion."""
    if self.event_bus:
        # Notify through the event bus
        self.event_bus.emit("file_operation_completed", {
            'operation': operation_type,
            'sources': source_paths,
            'target': target_path
        })
        
def _on_operation_failed(self, operation_type, source_paths, error):
    """Handle operation failure."""
    if self.event_bus:
        # Notify through the event bus
        self.event_bus.emit("file_operation_failed", {
            'operation': operation_type,
            'sources': source_paths,
            'error': error
        })
        
    # Show an error message
    QMessageBox.critical(
        self.parentWidget(),
        "Operation Failed",
        f"The {operation_type} operation failed: {error}"
    )
```

## Theming and Customization

The Explorer Context Menu can be styled to match the application's theme:

```python
def apply_theme(self, theme_manager):
    """Apply theme to the context menu."""
    if not theme_manager:
        return
        
    # Get theme colors
    background_color = theme_manager.get_color("menu.background")
    text_color = theme_manager.get_color("menu.foreground")
    selection_bg = theme_manager.get_color("menu.selectionBackground")
    selection_fg = theme_manager.get_color("menu.selectionForeground")
    
    # Apply styles
    stylesheet = f"""
    QMenu {{
        background-color: {background_color};
        color: {text_color};
        border: 1px solid {theme_manager.get_color("menu.border")};
    }}
    
    QMenu::item:selected {{
        background-color: {selection_bg};
        color: {selection_fg};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {theme_manager.get_color("menu.separator")};
        margin: 4px 8px;
    }}
    """
    
    self.setStyleSheet(stylesheet)
```

## Accessibility Considerations

The Explorer Context Menu should be accessible:

```python
def _setup_accessibility(self):
    """Set up accessibility features."""
    # Set object name for screen readers
    self.setObjectName("ExplorerContextMenu")
    
    # Ensure all actions have accessible names
    for action in self._actions.values():
        if action.shortcut():
            # Include shortcut in accessible name
            shortcut_text = action.shortcut().toString(QKeySequence.NativeText)
            action.setStatusTip(f"{action.text()} ({shortcut_text})")
        
        # Set accessibility description
        action.setWhatsThis(action.statusTip())
```

## Best Practices for Context Menu Extensions

1. **Keep It Focused**: Add only relevant actions to the context menu
2. **Group Related Items**: Use separators to group related actions
3. **Use Clear Labels**: Action labels should be concise and descriptive
4. **Provide Icons**: Use icons to help users identify actions quickly
5. **Support Keyboard**: Ensure all actions have keyboard shortcuts where appropriate
6. **Context Sensitivity**: Show actions only when they're relevant to the selection
7. **Consistent Placement**: Keep actions in consistent locations
8. **Performance**: Ensure menu generation is fast, especially for large selections
9. **Undo Support**: All operations should support undo/redo
10. **Feedback**: Provide clear feedback when operations succeed or fail

## Integration Testing Guidelines

When testing context menu integrations, focus on:

1. **Menu Generation**: Verify correct menu items appear for different selections
2. **Action Execution**: Test that each action performs as expected
3. **Error Handling**: Ensure proper error handling and feedback
4. **Undo/Redo**: Verify operations can be undone and redone
5. **Plugin Integration**: Test that plugins correctly extend the menu
6. **Keyboard Support**: Verify keyboard shortcuts work properly
7. **Theme Consistency**: Check menu appearance with different themes
8. **Performance**: Test with large selections and directories
9. **Accessibility**: Verify screen reader support
10. **Edge Cases**: Test with special files, network paths, long names, etc.
