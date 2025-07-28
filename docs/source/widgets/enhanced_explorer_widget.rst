Enhanced Explorer Widget
=====================

.. module:: widgets.enhanced_explorer_widget

Overview
--------

The Enhanced Explorer Widget provides a fully-featured file explorer with context menu
and drag & drop support. It integrates with multiple services to provide a complete
file management experience.

.. autoclass:: widgets.enhanced_explorer_widget.EnhancedExplorerWidget
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Key Components
-------------

The Enhanced Explorer Widget integrates several components:

- **File View**: An enhanced file view with context menu and drag & drop support
- **Search Bar**: A search bar for filtering files
- **Services**:
  - File Operations Service: Handles file operations like copy, cut, paste, delete
  - Undo/Redo Manager: Provides undo/redo functionality for file operations
  - File Numbering Service: Handles file name conflicts
  - Drag & Drop Service: Manages drag and drop operations

Usage Example
------------

.. code-block:: python

   from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
   
   # Create the widget
   explorer_widget = EnhancedExplorerWidget()
   
   # Connect to widget signals
   explorer_widget.file_view.file_activated.connect(on_file_activated)
   explorer_widget.file_view.directory_changed.connect(on_directory_changed)
   
   # Add the widget to your layout
   layout.addWidget(explorer_widget)
