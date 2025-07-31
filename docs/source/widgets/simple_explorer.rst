Simple Explorer Widget
====================

.. module:: widgets.simple_explorer_widget

Overview
--------

The Simple Explorer Widget provides a clean, focused file explorer with search/filter
functionality and settings persistence. It features a minimalist design following the
simple_explorer_design.md specifications with essential file browsing capabilities.

.. autoclass:: widgets.simple_explorer_widget.SimpleExplorerWidget
   :members:
   :undoc-members:
   :show-inheritance:

Key Components
-------------

The Simple Explorer Widget consists of several integrated components:

- **Navigation Bar**: Contains up button and current path display
- **Search/Filter Bar**: Text input for filtering files with clear button
- **File View**: Tree view with directory-first sorting
- **Settings Persistence**: Remembers last visited directory

Search and Filter Features
-------------------------

Filter Bar
~~~~~~~~~~

The search bar at the top of the explorer provides real-time file filtering:

* **Type to Filter**: Start typing to filter files by name
* **Wildcard Matching**: Uses partial string matching (e.g., "*.py" shows Python files)
* **Case Insensitive**: Filtering is not case-sensitive
* **Context Menu**: Right-click for filter mode options:

  - Filter Files: Show/hide files based on name patterns
  - Search Text In Files: Search file contents (future feature)

Clear Button
~~~~~~~~~~~~

A clear button (✕) appears at the end of the filter bar:

* **Automatic Activation**: Button becomes enabled when filter text is entered
* **One-Click Reset**: Click to clear the filter and restore all files
* **Tooltip Help**: Hover for "Clear filter and restore all files" tooltip
* **State Restoration**: Instantly returns to unfiltered view

Directory-First Sorting
~~~~~~~~~~~~~~~~~~~~~~

The file view maintains consistent sorting behavior:

* **Directories First**: Folders always appear before files
* **Alphabetical Within Groups**: Files and folders are sorted alphabetically within their respective groups
* **Filter Preservation**: Directory-first order is maintained even when filtering

Usage Example
------------

.. code-block:: python

   from widgets.simple_explorer_widget import SimpleExplorerWidget
   
   # Create the widget
   explorer = SimpleExplorerWidget()
   
   # Connect to signals
   explorer.file_opened.connect(on_file_opened)
   explorer.location_changed.connect(on_location_changed)
   
   # Set initial directory
   explorer.set_current_path("/path/to/directory")
   
   # Add to layout
   layout.addWidget(explorer)

Navigation Features
-----------------

Path Navigation
~~~~~~~~~~~~~~

* **Up Button**: Navigate to parent directory with single click
* **Path Display**: Current directory path shown in navigation bar
* **Double-click Navigation**: Double-click folders to navigate into them
* **Persistent History**: Last visited directory is remembered across sessions

Settings Integration
~~~~~~~~~~~~~~~~~~

The widget integrates with ExplorerSettings for configuration persistence:

* **Last Path**: Automatically remembers and restores the last visited directory
* **Window State**: Settings are saved on widget close
* **Cross-session Persistence**: State is maintained between application restarts

Signals and Events
-----------------

The Simple Explorer Widget emits several signals for integration:

* ``file_opened(str)``: Emitted when a file is double-clicked
* ``location_changed(str)``: Emitted when the current directory changes

Internal Components
------------------

SimpleSearchBar
~~~~~~~~~~~~~~

.. autoclass:: widgets.simple_explorer_widget.SimpleSearchBar
   :members:
   :undoc-members:

SimpleFileView
~~~~~~~~~~~~~

.. autoclass:: widgets.simple_explorer_widget.SimpleFileView
   :members:
   :undoc-members:

DirectoryFirstProxyModel
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: widgets.simple_explorer_widget.DirectoryFirstProxyModel
   :members:
   :undoc-members:
