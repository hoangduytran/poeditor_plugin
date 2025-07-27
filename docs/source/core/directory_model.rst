Directory Model
==============

.. automodule:: core.directory_model
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Directory Model provides a file system model implementation for the application's file explorer component. It represents the directory structure and file hierarchy in a format that can be easily displayed in tree views and other UI components.

Class Reference
-------------

DirectoryModel
~~~~~~~~~~~~

Main model class that represents the directory structure:

.. code-block:: python

    class DirectoryModel(QAbstractItemModel):
        def __init__(self, root_path=None, parent=None):
            super().__init__(parent)
            self.root_item = DirectoryItem()
            self.root_path = root_path
            
            if root_path:
                self.set_root_path(root_path)
                
        def set_root_path(self, root_path):
            """Set the root path for the model."""
            self.beginResetModel()
            self.root_path = root_path
            self.root_item = DirectoryItem(root_path)
            self._populate_root()
            self.endResetModel()
            
        def _populate_root(self):
            """Populate the root item with immediate children."""
            if not self.root_path or not os.path.exists(self.root_path):
                return
                
            entries = os.listdir(self.root_path)
            for entry in sorted(entries):
                path = os.path.join(self.root_path, entry)
                child = DirectoryItem(path, self.root_item)
                self.root_item.add_child(child)
                
        # Standard model implementation methods
        def index(self, row, column, parent=QModelIndex()):
            if not self.hasIndex(row, column, parent):
                return QModelIndex()
                
            if not parent.isValid():
                parent_item = self.root_item
            else:
                parent_item = parent.internalPointer()
                
            child_item = parent_item.child(row)
            if child_item:
                return self.createIndex(row, column, child_item)
            return QModelIndex()
            
        def parent(self, index):
            if not index.isValid():
                return QModelIndex()
                
            child_item = index.internalPointer()
            parent_item = child_item.parent()
            
            if parent_item == self.root_item:
                return QModelIndex()
                
            return self.createIndex(parent_item.row(), 0, parent_item)
            
        def rowCount(self, parent=QModelIndex()):
            if parent.column() > 0:
                return 0
                
            if not parent.isValid():
                parent_item = self.root_item
            else:
                parent_item = parent.internalPointer()
                
            return parent_item.child_count()
            
        def columnCount(self, parent=QModelIndex()):
            return 1
            
        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid():
                return None
                
            item = index.internalPointer()
            
            if role == Qt.DisplayRole:
                return item.name()
            elif role == Qt.DecorationRole:
                return item.icon()
                
            return None

DirectoryItem
~~~~~~~~~~~

Class representing an item in the directory structure:

.. code-block:: python

    class DirectoryItem:
        def __init__(self, path=None, parent=None):
            self.path = path
            self._parent = parent
            self._children = []
            self._children_loaded = False
            
        def name(self):
            """Get the name of this item."""
            if not self.path:
                return ""
            return os.path.basename(self.path) or self.path
            
        def icon(self):
            """Get the icon for this item."""
            if not self.path:
                return None
                
            if os.path.isdir(self.path):
                return QIcon.fromTheme("folder")
            else:
                return QIcon.fromTheme("text-x-generic")
                
        def child_count(self):
            """Get the number of children."""
            if not self._children_loaded:
                self._load_children()
            return len(self._children)
            
        def child(self, row):
            """Get child at row."""
            if not self._children_loaded:
                self._load_children()
            if 0 <= row < len(self._children):
                return self._children[row]
            return None
            
        def parent(self):
            """Get parent item."""
            return self._parent
            
        def row(self):
            """Get row in parent."""
            if self._parent:
                return self._parent._children.index(self)
            return 0
            
        def add_child(self, child):
            """Add a child item."""
            self._children.append(child)
            
        def _load_children(self):
            """Load children from filesystem."""
            if not self.path or not os.path.isdir(self.path):
                return
                
            try:
                entries = os.listdir(self.path)
                for entry in sorted(entries):
                    path = os.path.join(self.path, entry)
                    child = DirectoryItem(path, self)
                    self.add_child(child)
            except:
                pass
                
            self._children_loaded = True

Usage Examples
------------

Creating a Directory Model
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Create a directory model for a specific directory
    from core.directory_model import DirectoryModel
    from PySide6.QtWidgets import QTreeView
    
    # Create model
    model = DirectoryModel("/path/to/project")
    
    # Create view and set model
    tree_view = QTreeView()
    tree_view.setModel(model)

Working with the Model
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Connect to tree view signals
    tree_view.clicked.connect(on_item_clicked)
    
    def on_item_clicked(index):
        # Get the directory item
        item = index.internalPointer()
        
        # Get the full path
        path = item.path
        
        # Check if it's a file or directory
        if os.path.isfile(path):
            # Open the file
            open_file(path)
        else:
            # Expand/collapse the directory
            if tree_view.isExpanded(index):
                tree_view.collapse(index)
            else:
                tree_view.expand(index)

Customizing the Model
~~~~~~~~~~~~~~~~~~

The model can be extended to support additional functionality:

.. code-block:: python

    class CustomDirectoryModel(DirectoryModel):
        def __init__(self, root_path=None, parent=None):
            super().__init__(root_path, parent)
            self.file_filter = FileFilter()
            
        def data(self, index, role=Qt.DisplayRole):
            # Get base implementation result
            result = super().data(index, role)
            
            # Add custom behavior
            if role == Qt.ForegroundRole:
                item = index.internalPointer()
                if item.path and self.file_filter.is_translation_file(item.path):
                    return QColor(0, 120, 215)  # Highlight translation files
                    
            return result
            
        def _populate_root(self):
            """Override to filter certain files."""
            super()._populate_root()
            # Additional custom logic here

File Type Detection
----------------

The directory model can be extended to detect specific file types:

.. code-block:: python

    def get_file_type(self, path):
        """Determine the file type from path."""
        ext = os.path.splitext(path)[1].lower()
        
        if ext == ".po":
            return "translation"
        elif ext in [".txt", ".md"]:
            return "text"
        elif ext in [".py", ".js", ".ts"]:
            return "code"
        elif ext in [".jpg", ".png", ".svg"]:
            return "image"
        else:
            return "unknown"
