File Filter
==========

.. automodule:: core.file_filter
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The File Filter module provides utilities for filtering files based on various criteria such as file extensions, patterns, or content types. It's primarily used by the explorer and search components to limit the displayed files to those relevant for the user's current task.

Class Reference
-------------

FileFilter
~~~~~~~~~

Main class that implements file filtering functionality:

.. code-block:: python

    class FileFilter:
        def __init__(self):
            self.excluded_patterns = [
                "*.pyc", 
                "__pycache__/*",
                ".git/*", 
                ".vscode/*",
                "*.bak",
                "*.tmp"
            ]
            self.translation_extensions = [".po", ".pot", ".mo"]
            
        def is_excluded(self, path):
            """Check if a path should be excluded based on patterns."""
            path_str = str(path)
            for pattern in self.excluded_patterns:
                if fnmatch.fnmatch(path_str, pattern):
                    return True
            return False
            
        def is_translation_file(self, path):
            """Check if a file is a translation file."""
            ext = os.path.splitext(path)[1].lower()
            return ext in self.translation_extensions
            
        def filter_files(self, file_list, include_pattern=None):
            """Filter a list of files based on exclusion patterns."""
            result = [f for f in file_list if not self.is_excluded(f)]
            
            if include_pattern:
                result = [f for f in result if fnmatch.fnmatch(f, include_pattern)]
                
            return result

FileTypeRegistry
~~~~~~~~~~~~~~

Registry for managing file type associations:

.. code-block:: python

    class FileTypeRegistry:
        def __init__(self):
            self.type_extensions = {
                "translation": [".po", ".pot", ".mo"],
                "source": [".py", ".js", ".ts", ".html", ".css"],
                "document": [".txt", ".md", ".rst"],
                "image": [".png", ".jpg", ".jpeg", ".gif", ".svg"],
            }
            self.custom_matchers = {}
            
        def get_file_type(self, path):
            """Get the file type for a path."""
            # First try custom matchers
            for type_id, matcher in self.custom_matchers.items():
                if matcher(path):
                    return type_id
            
            # Then try extension matching
            ext = os.path.splitext(path)[1].lower()
            for type_id, extensions in self.type_extensions.items():
                if ext in extensions:
                    return type_id
                    
            return "unknown"
            
        def register_file_type(self, type_id, extensions=None, matcher=None):
            """Register a new file type with extensions or a matcher function."""
            if extensions:
                self.type_extensions[type_id] = extensions
            if matcher:
                self.custom_matchers[type_id] = matcher

Usage Examples
------------

Basic File Filtering
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Create a file filter
    from core.file_filter import FileFilter
    
    file_filter = FileFilter()
    
    # Check if a file should be excluded
    if not file_filter.is_excluded("/path/to/file.py"):
        # Process the file
        process_file("/path/to/file.py")
    
    # Filter a list of files
    all_files = ["/path/to/file1.py", "/path/to/file2.pyc", "/path/to/__pycache__/file3.py"]
    filtered_files = file_filter.filter_files(all_files)
    # filtered_files will contain only "/path/to/file1.py"

Working with File Types
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from core.file_filter import FileTypeRegistry
    
    # Create a registry
    registry = FileTypeRegistry()
    
    # Get file type
    file_type = registry.get_file_type("/path/to/translations.po")
    # file_type will be "translation"
    
    # Register a custom file type
    registry.register_file_type("config", [".json", ".yaml", ".ini"])
    
    # Register a file type with a custom matcher
    def is_database_file(path):
        return "database" in path.lower() or path.endswith(".db")
    
    registry.register_file_type("database", matcher=is_database_file)

Customizing Filters
----------------

The file filter can be customized for specific use cases:

.. code-block:: python

    # Create a specialized filter
    class ProjectFileFilter(FileFilter):
        def __init__(self, project_config):
            super().__init__()
            # Add project-specific exclusions
            if "excluded_paths" in project_config:
                self.excluded_patterns.extend(project_config["excluded_paths"])
                
        def should_include_for_search(self, path):
            """Check if file should be included in search results."""
            if self.is_excluded(path):
                return False
                
            # Additional filtering logic
            if os.path.getsize(path) > 10 * 1024 * 1024:  # Skip files larger than 10MB
                return False
                
            return True

Integration with Explorer
---------------------

File filters are typically used with the explorer component:

.. code-block:: python

    # In explorer component
    class ExplorerPanel(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            self.file_filter = FileFilter()
            self.directory_model = DirectoryModel()
            self.directory_model.set_file_filter(self.file_filter)
            
            # Create filter settings UI
            self.setup_filter_ui()
            
        def setup_filter_ui(self):
            self.filter_box = QGroupBox("Filters")
            layout = QVBoxLayout()
            
            # Show hidden files
            self.show_hidden_cb = QCheckBox("Show hidden files")
            self.show_hidden_cb.toggled.connect(self.update_filters)
            layout.addWidget(self.show_hidden_cb)
            
            # File type filter
            self.file_type_combo = QComboBox()
            self.file_type_combo.addItem("All Files", "")
            self.file_type_combo.addItem("Translation Files", "translation")
            self.file_type_combo.addItem("Source Code", "source")
            self.file_type_combo.currentIndexChanged.connect(self.update_filters)
            layout.addWidget(self.file_type_combo)
            
            self.filter_box.setLayout(layout)
            
        def update_filters(self):
            # Update file filter settings based on UI
            show_hidden = self.show_hidden_cb.isChecked()
            if not show_hidden:
                self.file_filter.excluded_patterns.append(".*")
            else:
                if ".*" in self.file_filter.excluded_patterns:
                    self.file_filter.excluded_patterns.remove(".*")
                    
            # Update model to apply new filters
            self.directory_model.refresh()
