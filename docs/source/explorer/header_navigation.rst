Header Navigation
=================

The Header Navigation feature provides enhanced functionality for the explorer's column
headers, combining traditional sorting capabilities with powerful navigation tools and
column management.

Overview
--------

The HeaderNavigationWidget extends Qt's QHeaderView to provide an integrated navigation
and column management experience in the table header. This allows users to:

* **Navigate directories** through header context menus
* **Sort columns** by clicking on headers
* **Manage column visibility** and layout
* **Access navigation history** and bookmarks
* **Quick directory navigation** with path completion

Key Features
------------

Context Menu Navigation
~~~~~~~~~~~~~~~~~~~~~~~

Right-clicking on any column header opens a comprehensive navigation menu:

**Navigation Actions**
   * **Back** - Return to previous directory in navigation history
   * **Forward** - Move forward in navigation history
   * **Up** - Navigate to parent directory
   * **Home** - Go to user's home directory
   * **Go to Path** - Open dialog for direct path navigation with completion

**Quick Locations**
   * **Recent Locations** - Recently visited directories
   * **Bookmarks** - User-saved favorite locations
   * **Bookmark Manager** - Add, edit, and organize bookmarks

**Column Management**
   * **Show/Hide Columns** - Toggle visibility of specific columns
   * **Fit Content** - Auto-resize columns to content width
   * **Reset Columns** - Restore default column layout

Column Sorting
~~~~~~~~~~~~~~

Standard sorting functionality enhanced with visual feedback:

* **Click header** - Sort by column (ascending/descending toggle)
* **Visual indicators** - Clear sort direction arrows
* **Multi-column sorting** - Hold Ctrl while clicking for secondary sorts
* **Sort persistence** - Remembers sort preferences per directory

Column Management
~~~~~~~~~~~~~~~~~

Advanced column layout control:

* **Drag to reorder** - Rearrange column positions
* **Resize columns** - Drag column borders to adjust width
* **Auto-fit content** - Right-click menu option to size columns optimally
* **Column visibility** - Show/hide columns based on user preference

Architecture
------------

Service Integration
~~~~~~~~~~~~~~~~~~~

The HeaderNavigationWidget integrates with multiple services:

.. code-block:: python

   # Service dependencies
   navigation_service: NavigationService       # Core navigation operations
   history_service: NavigationHistoryService   # Navigation history tracking
   location_manager: LocationManager           # Bookmarks and quick locations
   completion_service: PathCompletionService   # Path auto-completion
   column_manager: ColumnManagerService        # Column layout management

Signal Communication
~~~~~~~~~~~~~~~~~~~~

The widget communicates through Qt signals:

.. code-block:: python

   # Navigation signals
   navigation_requested.emit(path)      # Request to navigate to path
   path_changed.emit(new_path)         # Current path has changed
   
   # Column management signals
   column_visibility_changed.emit(visible_columns)  # Column visibility changed

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~

The HeaderNavigationWidget is typically integrated into file views:

.. code-block:: python

   from widgets.explorer.explorer_header_bar import HeaderNavigationWidget
   from PySide6.QtCore import Qt
   
   # Create header with navigation
   header = HeaderNavigationWidget(Qt.Horizontal, parent=tree_view)
   tree_view.setHeader(header)
   
   # Inject required services
   header.inject_services(
       navigation_service=nav_service,
       history_service=history_service,
       location_manager=location_mgr,
       completion_service=completion_service,
       column_manager=column_mgr
   )

Service Configuration
~~~~~~~~~~~~~~~~~~~~~

Configure the navigation services for full functionality:

.. code-block:: python

   # Setup navigation service
   nav_service = NavigationService()
   nav_service.set_current_path("/initial/path")
   
   # Setup history tracking
   history_service = NavigationHistoryService()
   history_service.set_max_history_size(50)
   
   # Setup location management
   location_mgr = LocationManager()
   location_mgr.load_bookmarks()
   
   # Connect signals
   header.navigation_requested.connect(nav_service.navigate_to)
   nav_service.current_path_changed.connect(header._on_path_changed)

User Interface
--------------

Context Menu Structure
~~~~~~~~~~~~~~~~~~~~~~

The header context menu is organized into logical sections:

.. code-block:: text

   Navigation Menu
   ├── Back                    (with history tooltip)
   ├── Forward                 (with history tooltip)
   ├── Up                      (to parent directory)
   ├── Home                    (to user home)
   ├── ─────────────          (separator)
   ├── Go to Path...           (opens path dialog)
   ├── ─────────────          (separator)
   ├── Recent Locations ►      (submenu with recent paths)
   ├── Bookmarks ►             (submenu with bookmarks)
   ├── Bookmark Manager...     (opens bookmark dialog)
   ├── ─────────────          (separator)
   ├── Columns ►               (submenu for column management)
   │   ├── ☑ Name             (toggle column visibility)
   │   ├── ☑ Size             (toggle column visibility)
   │   ├── ☑ Modified         (toggle column visibility)
   │   ├── ☐ Type             (toggle column visibility)
   │   ├── ─────────────      (separator)
   │   ├── Fit Content        (auto-resize columns)
   │   └── Reset Layout       (restore defaults)

Visual Feedback
~~~~~~~~~~~~~~~

The header provides clear visual feedback:

* **Sort indicators** - Up/down arrows show sort direction
* **Hover effects** - Headers highlight on mouse over
* **Active column** - Currently sorted column has distinct styling
* **Context menu icons** - Clear icons for all navigation actions

Keyboard Shortcuts
~~~~~~~~~~~~~~~~~~~

Header navigation supports keyboard shortcuts:

* **Ctrl+B** - Show bookmarks menu
* **Ctrl+H** - Navigate to home directory
* **Ctrl+↑** - Navigate to parent directory
* **Ctrl+G** - Open "Go to Path" dialog
* **F5** - Refresh current directory

Configuration
-------------

Column Management
~~~~~~~~~~~~~~~~~

Column behavior can be configured:

.. code-block:: python

   # Set default visible columns
   column_manager.set_visible_columns(['name', 'size', 'modified'])
   
   # Configure column properties
   column_manager.set_column_width('name', 200)
   column_manager.set_column_resizable('name', True)
   column_manager.set_column_sortable('size', True)

Navigation Settings
~~~~~~~~~~~~~~~~~~~

Navigation behavior can be customized:

.. code-block:: python

   # Configure history
   history_service.set_max_history_size(100)
   history_service.set_save_history(True)
   
   # Configure bookmarks
   location_manager.set_bookmarks_file("~/.config/app/bookmarks.json")
   location_manager.set_auto_save(True)

Performance Considerations
--------------------------

The HeaderNavigationWidget is optimized for performance:

* **Lazy menu creation** - Context menus built on demand
* **Efficient signal handling** - Minimal overhead for navigation events
* **Column caching** - Column state cached for quick access
* **Service injection** - Lightweight dependency management

The header navigation integrates seamlessly with the explorer's file operations and
provides a consistent, powerful interface for navigation and column management.

Related Components
------------------

* :doc:`../widgets/enhanced_file_view` - Main file view implementation
* :doc:`../widgets/explorer_context_menu` - File/folder context menus
* :doc:`../services/navigation_service` - Core navigation service
* :doc:`../services/column_manager_service` - Column management service

For developer information, see :doc:`header_navigation_dev`.
