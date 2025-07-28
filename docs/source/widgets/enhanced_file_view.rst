Enhanced File View
================

.. module:: widgets.enhanced_file_view

Overview
--------

The Enhanced File View extends the Simple File View with context menu and drag & drop
capabilities. It provides a rich interface for file management operations.

.. autoclass:: widgets.enhanced_file_view.EnhancedFileView
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Key Features
-----------

1. **Context Menu Support**: Right-click context menu with file operations
2. **Drag & Drop**: Intuitive drag and drop for files and directories
3. **Service Integration**: Integration with file operations services

Event Handlers
-------------

The Enhanced File View implements several event handlers for drag & drop:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Event Handler
     - Description
   * - ``mousePressEvent(QMouseEvent)``
     - Handles mouse press events to initiate drag operations
   * - ``mouseMoveEvent(QMouseEvent)``
     - Handles mouse move events to start drag if threshold exceeded
   * - ``dragEnterEvent(QDragEnterEvent)``
     - Validates incoming drag data
   * - ``dragMoveEvent(QDragMoveEvent)``
     - Provides visual feedback for drop targets
   * - ``dropEvent(QDropEvent)``
     - Processes the dropped data

Usage Example
------------

.. code-block:: python

   from widgets.enhanced_file_view import EnhancedFileView
   from services.file_operations_service import FileOperationsService
   from services.undo_redo_service import UndoRedoManager
   
   # Create services
   file_operations = FileOperationsService()
   undo_redo = UndoRedoManager()
   
   # Create the file view
   file_view = EnhancedFileView()
   file_view.setup_context_menu(file_operations, undo_redo)
   
   # Connect to file view signals
   file_view.file_activated.connect(on_file_activated)
   file_view.directory_changed.connect(on_directory_changed)
