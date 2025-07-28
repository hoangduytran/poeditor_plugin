Enhanced Explorer Panel
=====================

.. module:: panels.enhanced_explorer_panel

Overview
--------

The Enhanced Explorer Panel extends the standard Explorer panel with context menu
functionality and drag & drop capabilities for intuitive file management.

.. autoclass:: panels.enhanced_explorer_panel.EnhancedExplorerPanel
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
   * - ``file_opened(str)``
     - Emitted when a file is opened. Parameter is the file path.
   * - ``location_changed(str)``
     - Emitted when the current directory changes. Parameter is the directory path.

Usage Example
------------

.. code-block:: python

   from panels.enhanced_explorer_panel import EnhancedExplorerPanel
   
   # Create the panel
   explorer_panel = EnhancedExplorerPanel()
   
   # Connect to panel signals
   explorer_panel.file_opened.connect(on_file_opened)
   explorer_panel.location_changed.connect(on_location_changed)
   
   # Add the panel to your layout
   layout.addWidget(explorer_panel)
