Explorer Context Menu
=================

.. module:: widgets.explorer_context_menu

Overview
--------

The Explorer Context Menu manages the creation and configuration of context menus
for the Enhanced File View. It provides different menus based on the selection type.

.. autoclass:: widgets.explorer_context_menu.ExplorerContextMenu
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Signals
-------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Signal
     - Description
   * - ``show_properties(list)``
     - Emitted when the user selects the Properties menu item
   * - ``show_open_with(list)``
     - Emitted when the user selects the Open With menu item

Menu Creation
------------

The Explorer Context Menu creates different menus based on the selection type:

- **Single File**: File-specific operations like Open, Edit
- **Multiple Files**: Operations for multiple files like Copy, Cut
- **Directory**: Directory-specific operations like Open, Explore
- **Mixed Selection**: Operations that work on both files and directories

Usage Example
------------

.. code-block:: python

   from widgets.explorer_context_menu import ExplorerContextMenu
   from services.file_operations_service import FileOperationsService
   from services.undo_redo_service import UndoRedoManager
   
   # Create services
   file_operations = FileOperationsService()
   undo_redo = UndoRedoManager()
   
   # Create context menu manager
   context_menu = ExplorerContextMenu(file_operations, undo_redo)
   
   # Create a menu for a specific selection
   menu = context_menu.create_menu(["/path/to/file.txt"])
   
   # Show the menu
   menu.exec_(QCursor.pos())
