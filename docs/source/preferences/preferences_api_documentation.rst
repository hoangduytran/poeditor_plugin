=======================================
Preferences System API Documentation
=======================================

:Date: August 5, 2025
:Component: Preferences System
:Version: 1.0.0 (Phase 1)
:Status: Production

Overview
========

The Preferences System provides a comprehensive foundation for managing application settings and user preferences. Phase 1 implements the core infrastructure that all preference panels will build upon.

The system is organized into a modular architecture with common components in ``preferences/common/`` and panel-specific implementations in separate directories.

Architecture
============

Core Components
---------------

The preferences system consists of six foundational modules:

1. **workspace_types.py** - Core enumerations and type definitions
2. **data_models.py** - Data structures and record classes
3. **database.py** - SQLite persistence layer with migrations
4. **base_components.py** - Reusable UI components
5. **search_integration.py** - Advanced search functionality
6. **import_export.py** - File format handlers (JSON, CSV, PLIST, YAML)

Directory Structure
-------------------

.. code-block:: text

   preferences/
   ├── common/              # Shared infrastructure (Phase 1)
   │   ├── workspace_types.py
   │   ├── data_models.py
   │   ├── database.py
   │   ├── base_components.py
   │   ├── search_integration.py
   │   └── import_export.py
   ├── text_replacements/   # Placeholder for Phase 2
   ├── translation_history/ # Placeholder for Phase 3
   ├── plugin_api/         # Placeholder for Phase 4
   └── main_dialog.py      # Main preferences dialog

API Reference
=============

Workspace Types Module
----------------------

.. automodule:: preferences.common.workspace_types
   :members:
   :undoc-members:
   :show-inheritance:

Core Enumerations
~~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.workspace_types.SortOrder
   :members:
   :undoc-members:

.. autoclass:: preferences.common.workspace_types.FilterType
   :members:
   :undoc-members:

.. autoclass:: preferences.common.workspace_types.SearchScope
   :members:
   :undoc-members:

.. autoclass:: preferences.common.workspace_types.ExportFormat
   :members:
   :undoc-members:

.. autoclass:: preferences.common.workspace_types.ImportValidationLevel
   :members:
   :undoc-members:

Data Models Module
------------------

.. automodule:: preferences.common.data_models
   :members:
   :undoc-members:
   :show-inheritance:

Core Data Structures
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.data_models.PageInfo
   :members:
   :undoc-members:

   Manages pagination state for table widgets and search results.

   **Key Features:**
   
   - Automatic calculation of total pages
   - Navigation state tracking (has_next_page, has_prev_page)
   - Page size management with validation

.. autoclass:: preferences.common.data_models.PreferenceRecord
   :members:
   :undoc-members:

   Base class for all preference record types.

   **Design Pattern:**
   
   This follows the Data Transfer Object (DTO) pattern, providing a clean
   interface between the UI layer and persistence layer.

.. autoclass:: preferences.common.data_models.PreferenceSearchRequest
   :members:
   :undoc-members:

   Encapsulates search parameters for preference queries.

   **Usage Example:**
   
   .. code-block:: python
   
      search_request = PreferenceSearchRequest(
          query="find text",
          search_scope=SearchScope.ALL,
          filter_type=FilterType.CONTAINS,
          page=1,
          page_size=50
      )

Database Module
---------------

.. automodule:: preferences.common.database
   :members:
   :undoc-members:
   :show-inheritance:

Database Manager
~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.database.PreferencesDatabaseManager
   :members:
   :undoc-members:

   **Connection Management:**
   
   The database manager handles SQLite connections with automatic transaction
   management and proper resource cleanup.

   **Migration System:**
   
   Supports incremental schema updates:
   
   .. code-block:: python
   
      # Check current schema version
      version = db_manager.get_schema_version()
      
      # Apply pending migrations
      db_manager.ensure_schema_current()

   **Thread Safety:**
   
   Uses connection pooling and proper locking to support multi-threaded access.

Base Components Module
----------------------

.. automodule:: preferences.common.base_components
   :members:
   :undoc-members:
   :show-inheritance:

UI Foundation Classes
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.base_components.PreferenceSection
   :members:
   :undoc-members:

   Styled group box for organizing related preference controls.

.. autoclass:: preferences.common.base_components.PreferencePage
   :members:
   :undoc-members:

   Base class for all preference pages with consistent layout and behavior.

   **State Management:**
   
   - Tracks modification state
   - Provides validation framework
   - Handles save/reset operations

.. autoclass:: preferences.common.base_components.FormLayoutHelper
   :members:
   :undoc-members:

   Static helper methods for creating consistent form layouts.

   **Usage Pattern:**
   
   .. code-block:: python
   
      layout = FormLayoutHelper.create_form_layout()
      
      # Add various field types
      text_field = FormLayoutHelper.add_text_field(
          layout, "Name:", "Enter name", "Name tooltip"
      )
      
      checkbox = FormLayoutHelper.add_checkbox(
          layout, "Enabled:", "Enable this feature"
      )

Advanced UI Components
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.base_components.PagedTableWidget
   :members:
   :undoc-members:

   Table widget with built-in pagination support.

   **Signals:**
   
   - ``page_changed(int)`` - Emitted when page navigation occurs
   - ``page_size_changed(int)`` - Emitted when page size changes
   - ``data_requested(int, int)`` - Emitted when new data is needed

.. autoclass:: preferences.common.base_components.EditableTableWidget
   :members:
   :undoc-members:

   Editable table with validation and change tracking.

   **Validation Framework:**
   
   .. code-block:: python
   
      table = EditableTableWidget()
      
      # Set column validators
      table.set_column_validator(0, ValidationHelpers.validate_non_empty)
      table.set_column_validator(1, ValidationHelpers.validate_regex)

.. autoclass:: preferences.common.base_components.SearchableListWidget
   :members:
   :undoc-members:

   List widget with integrated search functionality and debouncing.

.. autoclass:: preferences.common.base_components.PagingControlsWidget
   :members:
   :undoc-members:

   Reusable pagination controls with navigation buttons and page size selector.

.. autoclass:: preferences.common.base_components.SettingsGroupWidget
   :members:
   :undoc-members:

   Grouped settings controls with automatic value management.

   **Example Usage:**
   
   .. code-block:: python
   
      group = SettingsGroupWidget("Display Settings")
      
      # Add various controls
      group.add_setting("font_size", "Font Size:", QSpinBox())
      group.add_setting("theme", "Theme:", QComboBox())
      
      # Get/set values
      values = group.get_all_values()
      group.set_all_values({"font_size": 12, "theme": "Dark"})

Validation Helpers
~~~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.base_components.ValidationHelpers
   :members:
   :undoc-members:

   Collection of common validation functions for preference data.

Search Integration Module
-------------------------

.. automodule:: preferences.common.search_integration
   :members:
   :undoc-members:
   :show-inheritance:

Search Service
~~~~~~~~~~~~~~

.. autoclass:: preferences.common.search_integration.PreferenceSearchService
   :members:
   :undoc-members:

   **Search Capabilities:**
   
   - Full-text search across preference data
   - Advanced filtering with multiple criteria
   - Result ranking and relevance scoring
   - Pagination support for large result sets

   **Performance Features:**
   
   - Query result caching
   - Debounced search execution
   - Lazy loading of search results

.. autoclass:: preferences.common.search_integration.SearchResultItem
   :members:
   :undoc-members:

   Represents a single search result with relevance scoring.

.. autoclass:: preferences.common.search_integration.SearchCache
   :members:
   :undoc-members:

   Manages search result caching for improved performance.

Import/Export Module
--------------------

.. automodule:: preferences.common.import_export
   :members:
   :undoc-members:
   :show-inheritance:

File Format Handlers
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: preferences.common.import_export.PreferenceImportExportService
   :members:
   :undoc-members:

   **Supported Formats:**
   
   - JSON (complete structure preservation)
   - CSV (tabular data with headers)
   - PLIST (Apple property list format)
   - YAML (human-readable configuration)

   **Validation Levels:**
   
   - STRICT: Full validation with error on any issue
   - LENIENT: Warnings for issues, continue processing
   - PERMISSIVE: Best-effort import, skip problematic entries

   **Usage Example:**
   
   .. code-block:: python
   
      service = PreferenceImportExportService()
      
      # Export preferences
      success = service.export_preferences(
          preferences_data,
          "/path/to/export.json",
          ExportFormat.JSON
      )
      
      # Import with validation
      result = service.import_preferences(
          "/path/to/import.json",
          ImportValidationLevel.STRICT
      )

.. autoclass:: preferences.common.import_export.ImportResult
   :members:
   :undoc-members:

   Contains results and validation information from import operations.

Main Dialog
-----------

.. automodule:: preferences.main_dialog
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: preferences.main_dialog.PreferencesDialog
   :members:
   :undoc-members:

   **Plugin Integration:**
   
   The dialog provides extension points for plugins to add custom preference panels:
   
   .. code-block:: python
   
      dialog = PreferencesDialog()
      
      # Plugin registration (future Phase 4)
      dialog.register_plugin_panel(MyCustomPanel())

Usage Examples
==============

Basic Preference Page
---------------------

Creating a simple preference page:

.. code-block:: python

   from preferences.common.base_components import (
       PreferencePage, PreferenceSection, FormLayoutHelper
   )
   from PySide6.QtWidgets import QLineEdit, QCheckBox

   class MyPreferencePage(PreferencePage):
       def __init__(self, parent=None):
           super().__init__("My Settings", parent)
           self._setup_content()
       
       def _setup_content(self):
           # Create a settings section
           section = PreferenceSection("General Settings")
           
           # Create form layout
           layout = FormLayoutHelper.create_form_layout()
           
           # Add form fields
           self.name_field = FormLayoutHelper.add_text_field(
               layout, "Name:", "Enter your name"
           )
           
           self.enabled_checkbox = FormLayoutHelper.add_checkbox(
               layout, "Enabled:", "Enable this feature"
           )
           
           section.setLayout(layout)
           self.add_section(section)
       
       def save_changes(self):
           # Save logic here
           name = self.name_field.text()
           enabled = self.enabled_checkbox.isChecked()
           # ... save to database
           return True

Database Integration
--------------------

Working with the database layer:

.. code-block:: python

   from preferences.common.database import PreferencesDatabaseManager
   from preferences.common.data_models import PreferenceRecord

   # Initialize database
   db_manager = PreferencesDatabaseManager()
   
   # Create a preference record
   record = PreferenceRecord(
       category="ui",
       key="theme",
       value="dark",
       description="UI theme preference"
   )
   
   # Save to database
   with db_manager.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute("""
           INSERT INTO preferences (category, key, value, description)
           VALUES (?, ?, ?, ?)
       """, (record.category, record.key, record.value, record.description))
       conn.commit()

Search Integration
------------------

Implementing search functionality:

.. code-block:: python

   from preferences.common.search_integration import PreferenceSearchService
   from preferences.common.data_models import PreferenceSearchRequest
   from preferences.common.workspace_types import SearchScope, FilterType

   # Create search service
   search_service = PreferenceSearchService()
   
   # Build search request
   request = PreferenceSearchRequest(
       query="theme",
       search_scope=SearchScope.ALL,
       filter_type=FilterType.CONTAINS,
       page=1,
       page_size=50
   )
   
   # Perform search
   results = search_service.search_preferences(request)
   
   for item in results:
       print(f"Found: {item.title} (score: {item.relevance_score})")

Import/Export Operations
------------------------

Handling preference import/export:

.. code-block:: python

   from preferences.common.import_export import PreferenceImportExportService
   from preferences.common.workspace_types import ExportFormat, ImportValidationLevel

   service = PreferenceImportExportService()
   
   # Export current preferences
   preferences_data = get_all_preferences()  # Your data source
   
   success = service.export_preferences(
       preferences_data,
       "/Users/user/Desktop/my_preferences.json",
       ExportFormat.JSON
   )
   
   if success:
       print("Export completed successfully")
   
   # Import preferences with validation
   result = service.import_preferences(
       "/Users/user/Desktop/imported_preferences.csv",
       ImportValidationLevel.LENIENT
   )
   
   if result.success:
       print(f"Imported {len(result.imported_records)} records")
       if result.warnings:
           print(f"Warnings: {result.warnings}")
   else:
       print(f"Import failed: {result.error_message}")

Best Practices
==============

Development Guidelines
----------------------

1. **Component Inheritance**
   
   Always inherit from the base components when creating new UI elements:
   
   .. code-block:: python
   
      # Good
      class MyCustomPage(PreferencePage):
          pass
      
      # Avoid creating from scratch
      class MyPage(QWidget):  # Don't do this
          pass

2. **Database Transactions**
   
   Use the context manager for database operations:
   
   .. code-block:: python
   
      # Good
      with db_manager.get_connection() as conn:
          # Database operations here
          conn.commit()
      
      # Avoid manual connection management

3. **Validation Integration**
   
   Use the built-in validation framework:
   
   .. code-block:: python
   
      # Use provided validators
      validator = ValidationHelpers.create_required_validator("Name")
      table.set_column_validator(0, validator)

4. **Signal Connections**
   
   Connect to component signals for reactive updates:
   
   .. code-block:: python
   
      # React to data changes
      page.data_changed.connect(self.on_data_modified)
      table.cell_edited.connect(self.on_cell_changed)

Error Handling
--------------

1. **Database Errors**
   
   Handle database exceptions gracefully:
   
   .. code-block:: python
   
      try:
          with db_manager.get_connection() as conn:
              # Database operations
              pass
      except DatabaseError as e:
          logger.error(f"Database operation failed: {e}")
          # Show user-friendly error message

2. **Import/Export Errors**
   
   Check import results for validation issues:
   
   .. code-block:: python
   
      result = service.import_preferences(file_path, validation_level)
      
      if not result.success:
          # Handle import failure
          show_error_dialog(result.error_message)
      elif result.warnings:
          # Show warnings to user
          show_warning_dialog(result.warnings)

Performance Considerations
--------------------------

1. **Pagination Usage**
   
   Always use pagination for large data sets:
   
   .. code-block:: python
   
      # Good for large tables
      table = PagedTableWidget()
      table.page_info.page_size = 50
      
      # Avoid loading all data at once

2. **Search Debouncing**
   
   The search system includes automatic debouncing:
   
   .. code-block:: python
   
      # SearchableListWidget automatically debounces
      search_widget = SearchableListWidget()
      search_widget.search_requested.connect(self.perform_search)

3. **Cache Management**
   
   Use the search cache appropriately:
   
   .. code-block:: python
   
      # Cache is automatically managed
      # Clear when data changes
      search_service.clear_cache()

Testing
=======

The preferences system includes comprehensive test coverage. Tests are located in:

- ``tests/preferences/test_phase1.py`` - Integration tests
- ``tests/preferences/`` - Component-specific tests

Running Tests
-------------

.. code-block:: bash

   # Run all preference tests
   python -m pytest tests/preferences/
   
   # Run specific test file
   python -m pytest tests/preferences/test_phase1.py

Extension Points
================

Phase 1 provides the foundation for future phases:

Phase 2: Text Replacements
--------------------------

Will use the common infrastructure to implement:

- Find/replace rule management
- Pattern-based text transformations
- Rule validation and testing

Phase 3: Translation History
----------------------------

Will build upon the database layer for:

- Translation tracking and history
- Change detection and comparison
- Export/import of translation data

Phase 4: Plugin API
--------------------

Will extend the base components for:

- Plugin registration system
- Custom preference panel integration
- API versioning and compatibility

Troubleshooting
===============

Common Issues
-------------

1. **Database Connection Errors**
   
   - Ensure database file has proper permissions
   - Check if database schema is current
   - Verify connection string format

2. **Import/Export Failures**
   
   - Validate file format matches expected structure
   - Check file permissions for read/write access
   - Review validation level settings

3. **UI Layout Issues**
   
   - Ensure proper parent-child widget relationships
   - Use FormLayoutHelper for consistent layouts
   - Check theme CSS for widget styling

Migration Guide
===============

Future Compatibility
--------------------

When Phase 1 evolves:

1. **Database Schema Changes**
   
   The migration system will handle schema updates automatically.

2. **API Changes**
   
   Breaking changes will be deprecated gradually with clear migration paths.

3. **Component Updates**
   
   New features will be added as optional parameters to maintain compatibility.

See Also
========

- :doc:`enhanced_explorer_technical_design` - Related UI patterns
- :doc:`api_documentation_guide` - Documentation standards
- :doc:`developer_reference` - Quick reference guide

For questions or support, check the application log at ``application.log`` or review the source code in ``preferences/common/``.
