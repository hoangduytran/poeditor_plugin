Tab Manager
===========

.. automodule:: core.tab_manager
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Tab Manager is responsible for managing the application's content tabs in the main workspace area. It handles creating, organizing, and switching between tabs that display file content or other functionality.

Class Reference
-------------

TabManager
~~~~~~~~~

Main class that manages the tab components:

.. code-block:: python

    class TabManager(QObject):
        tab_added = Signal(str, QWidget)
        tab_closed = Signal(str)
        tab_activated = Signal(str)
        
        def __init__(self, tab_widget, parent=None):
            super().__init__(parent)
            self.tab_widget = tab_widget
            self.tabs = {}
            self.tab_ids = []
            
            # Connect tab widget signals
            self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
            self.tab_widget.currentChanged.connect(self._on_current_changed)
            
        def add_tab(self, tab_id, title, widget, icon=None):
            """Add a new tab to the manager."""
            if tab_id in self.tabs:
                return False
                
            index = self.tab_widget.addTab(widget, title)
            if icon:
                self.tab_widget.setTabIcon(index, icon)
                
            self.tabs[tab_id] = {
                "widget": widget,
                "index": index,
                "title": title
            }
            self.tab_ids.append(tab_id)
            
            self.tab_added.emit(tab_id, widget)
            return True
            
        def close_tab(self, tab_id):
            """Close a tab by ID."""
            if tab_id not in self.tabs:
                return False
                
            index = self.tabs[tab_id]["index"]
            self.tab_widget.removeTab(index)
            
            # Update indices of remaining tabs
            for id in self.tab_ids:
                if id != tab_id and self.tabs[id]["index"] > index:
                    self.tabs[id]["index"] -= 1
            
            # Remove tab from tracking
            self.tab_ids.remove(tab_id)
            del self.tabs[tab_id]
            
            self.tab_closed.emit(tab_id)
            return True
            
        def activate_tab(self, tab_id):
            """Activate a tab by ID."""
            if tab_id not in self.tabs:
                return False
                
            index = self.tabs[tab_id]["index"]
            self.tab_widget.setCurrentIndex(index)
            return True
            
        def get_active_tab_id(self):
            """Get the ID of the currently active tab."""
            current_index = self.tab_widget.currentIndex()
            for tab_id, tab_info in self.tabs.items():
                if tab_info["index"] == current_index:
                    return tab_id
            return None
            
        def _on_tab_close_requested(self, index):
            """Handle tab close request from the tab widget."""
            for tab_id, tab_info in self.tabs.items():
                if tab_info["index"] == index:
                    self.close_tab(tab_id)
                    break
                    
        def _on_current_changed(self, index):
            """Handle tab selection change."""
            for tab_id, tab_info in self.tabs.items():
                if tab_info["index"] == index:
                    self.tab_activated.emit(tab_id)
                    break

Usage Examples
------------

Creating a Tab Manager
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # In the main application
    from PySide6.QtWidgets import QMainWindow, QTabWidget
    from core.tab_manager import TabManager
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Create tab widget
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.setMovable(True)
            
            # Create tab manager
            self.tab_manager = TabManager(self.tab_widget)
            
            # Set as central widget
            self.setCentralWidget(self.tab_widget)

Adding Tabs
~~~~~~~~~

.. code-block:: python

    # Create and add a tab
    editor_widget = TextEditor()
    tab_manager.add_tab(
        "file:///path/to/file.txt",  # Unique ID
        "file.txt",                  # Display title
        editor_widget,               # Widget to display
        QIcon(":/icons/text_file.svg")  # Optional icon
    )
    
    # Add another tab
    preview_widget = DocumentPreview()
    tab_manager.add_tab(
        "preview:///path/to/file.txt",
        "Preview: file.txt",
        preview_widget
    )

Working with Tabs
~~~~~~~~~~~~~~~

.. code-block:: python

    # Activate a specific tab
    tab_manager.activate_tab("file:///path/to/file.txt")
    
    # Close a tab
    tab_manager.close_tab("preview:///path/to/file.txt")
    
    # Get the active tab ID
    active_tab_id = tab_manager.get_active_tab_id()
    
    # Connect to tab signals
    tab_manager.tab_added.connect(on_tab_added)
    tab_manager.tab_closed.connect(on_tab_closed)
    tab_manager.tab_activated.connect(on_tab_activated)

Integration with File Operations
-----------------------------

The Tab Manager integrates with the FileOperationsService to handle file-related operations:

.. code-block:: python

    # Open a file in a new tab
    def open_file(file_path):
        # Check if already open
        tab_id = f"file://{file_path}"
        if tab_id in tab_manager.tabs:
            tab_manager.activate_tab(tab_id)
            return
            
        # Create appropriate editor based on file type
        file_name = os.path.basename(file_path)
        if file_path.endswith('.po'):
            editor = POEditor(file_path)
        else:
            editor = TextEditor(file_path)
            
        # Add tab
        tab_manager.add_tab(
            tab_id,
            file_name,
            editor,
            get_icon_for_file_type(file_path)
        )
