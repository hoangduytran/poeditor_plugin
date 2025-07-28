Services Architecture
====================

.. raw:: html

   <div style="text-align: center; margin: 20px 0;">
      <img src="../_static/images/services_architecture.svg" alt="Services Architecture Diagram" style="width: 100%; max-width: 600px; height: auto;"/>
   </div>

Overview
--------

The application uses a service-oriented architecture where specialized services handle different aspects of functionality. This modular approach provides clean separation of concerns and makes the codebase more maintainable.

Core Services
-------------

File Operations Service
~~~~~~~~~~~~~~~~~~~~~~~

**Location**: ``services/file_operations.py``

The FileOperationsService handles all file system operations including:

- File creation, deletion, moving, and copying
- Directory operations and navigation
- File type detection and filtering
- Clipboard integration for cut/copy/paste operations
- Drag and drop functionality
- Undo/redo operations for file changes

**Key Features**:

.. code-block:: python

    class FileOperationsService:
        def copy_files(self, source_paths, destination_dir)
        def move_files(self, source_paths, destination_dir)
        def delete_files(self, file_paths)
        def create_directory(self, parent_dir, name)
        def rename_item(self, old_path, new_name)

Theme Manager
~~~~~~~~~~~~~

**Location**: ``services/theme_manager.py``

The ThemeManager provides comprehensive theming capabilities:

- Light and dark theme switching
- Custom CSS loading and application
- Theme persistence across sessions
- Dynamic theme updates without restart
- Resource-based and file-based theme loading

**Key Features**:

.. code-block:: python

    class ThemeManager:
        def apply_theme(self, theme_name)
        def load_css_from_file(self, css_file_path)
        def load_css_from_resource(self, resource_path)
        def get_available_themes(self)

Undo/Redo Manager
~~~~~~~~~~~~~~~~~

**Location**: ``services/undo_redo_manager.py``

Provides comprehensive undo/redo functionality:

- Command pattern implementation
- Undoable file operations
- Redo capability for reversed operations
- History management and limits
- Integration with file operations service

**Key Features**:

.. code-block:: python

    class UndoRedoManager:
        def execute_command(self, command)
        def undo(self)
        def redo(self)
        def clear_history(self)

File Numbering Service
~~~~~~~~~~~~~~~~~~~~~~

**Location**: ``services/file_numbering_service.py``

Handles automatic file numbering and conflict resolution:

- Automatic numbering for duplicate files
- Sequential numbering (file.txt, file(1).txt, file(2).txt)
- Directory-aware numbering
- Customizable numbering patterns

Drag Drop Service
~~~~~~~~~~~~~~~~~

Manages drag and drop operations:

- File dragging from external applications
- Internal file reordering
- Drop validation and feedback
- Integration with file operations service

Icon Manager
~~~~~~~~~~~~

Handles icon loading and caching:

- File type-specific icons
- Theme-aware icon selection
- Icon caching for performance
- SVG and bitmap icon support

CSS Manager
~~~~~~~~~~~

Manages CSS styling and themes:

- CSS compilation and minification
- Theme-specific CSS loading
- Runtime CSS updates
- Resource management

Data Layer Integration
----------------------

The services layer integrates with various data storage mechanisms:

File System API
~~~~~~~~~~~~~~~

Direct file system operations using Qt's QFileInfo, QDir, and QFile classes.

QSettings (Configuration)
~~~~~~~~~~~~~~~~~~~~~~~~~

Persistent storage for:

- User preferences
- Theme selections
- Window layouts
- Plugin configurations

Qt Resources (CSS/Icons)
~~~~~~~~~~~~~~~~~~~~~~~~

Embedded resources for:

- Default themes and CSS
- Application icons
- UI elements

System Clipboard
~~~~~~~~~~~~~~~~

Integration with system clipboard for:

- File path copying
- Cross-application file operations
- Text and file content copying

Service Coordination
-------------------

Services are designed to work together seamlessly:

1. **File Operations ↔ Undo/Redo**: All file operations are wrapped in undoable commands
2. **Theme Manager ↔ CSS Manager**: Theme changes trigger CSS reloading
3. **File Operations ↔ Icon Manager**: File changes trigger icon cache updates
4. **Drag Drop ↔ File Operations**: Drop operations delegate to file operations service

Service Lifecycle
-----------------

Services follow a consistent lifecycle:

1. **Initialization**: Services are created at application startup
2. **Registration**: Services register with the main application
3. **Configuration**: Services load their configuration from QSettings
4. **Operation**: Services handle requests from UI components
5. **Cleanup**: Services save state and cleanup resources on shutdown

Error Handling
--------------

Services implement comprehensive error handling:

- Exception catching and logging
- User-friendly error messages
- Rollback capabilities for failed operations
- Error reporting to the main application

This architecture ensures that the application is robust, maintainable, and extensible while providing a clear separation between UI logic and business operations.
