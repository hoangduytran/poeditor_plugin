=====================================
Preferences System Quick Reference
=====================================

:Date: August 5, 2025
:Component: Preferences System
:Version: 1.0.0 (Phase 1)
:Status: Production

Overview
========

Quick reference for the Phase 1 Preferences System common components.

Core Modules
============

Common Infrastructure (preferences/common/)
-------------------------------------------

**workspace_types.py**
   Core enumerations: SortOrder, FilterType, SearchScope, ExportFormat, ImportValidationLevel

**data_models.py**
   Data structures: PageInfo, PreferenceRecord, PreferenceSearchRequest

**database.py**
   SQLite persistence: PreferencesDatabaseManager with migration support

**base_components.py**
   UI components: PreferencePage, PagedTableWidget, FormLayoutHelper, validation helpers

**search_integration.py**
   Search functionality: PreferenceSearchService with caching and relevance scoring

**import_export.py**
   File handlers: JSON, CSV, PLIST, YAML import/export with validation

**main_dialog.py**
   Main preferences dialog with plugin extension points

Quick Usage
===========

Create a Preference Page
------------------------

.. code-block:: python

   from preferences.common.base_components import PreferencePage, PreferenceSection

   class MyPage(PreferencePage):
       def __init__(self):
           super().__init__("My Settings")
           section = PreferenceSection("General")
           self.add_section(section)

Database Operations
-------------------

.. code-block:: python

   from preferences.common.database import PreferencesDatabaseManager

   db = PreferencesDatabaseManager()
   with db.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute("SELECT * FROM preferences")
       results = cursor.fetchall()

Search Integration
-------------------

.. code-block:: python

   from preferences.common.search_integration import PreferenceSearchService
   from preferences.common.data_models import PreferenceSearchRequest

   service = PreferenceSearchService()
   request = PreferenceSearchRequest(query="theme", page=1, page_size=50)
   results = service.search_preferences(request)

Import/Export
-------------

.. code-block:: python

   from preferences.common.import_export import PreferenceImportExportService
   from preferences.common.workspace_types import ExportFormat

   service = PreferenceImportExportService()
   service.export_preferences(data, "prefs.json", ExportFormat.JSON)
   result = service.import_preferences("prefs.json", ImportValidationLevel.STRICT)

Key Classes
===========

Base Components
---------------

- **PreferencePage**: Base class for all preference pages
- **PreferenceSection**: Styled group box for organizing controls
- **FormLayoutHelper**: Static methods for consistent form layouts
- **PagedTableWidget**: Table with built-in pagination
- **EditableTableWidget**: Editable table with validation
- **ValidationHelpers**: Common validation functions

Data Models
-----------

- **PageInfo**: Pagination state management
- **PreferenceRecord**: Base preference data structure
- **PreferenceSearchRequest**: Search parameter encapsulation

Services
--------

- **PreferencesDatabaseManager**: SQLite operations with migrations
- **PreferenceSearchService**: Advanced search with caching
- **PreferenceImportExportService**: Multi-format file operations

Architecture Notes
==================

**Modular Design**: Common components in preferences/common/, panel-specific code in separate directories

**Extension Points**: Main dialog provides plugin registration for Phase 4

**Database**: SQLite with migration system, connection pooling, transaction management

**Search**: Full-text search with relevance scoring, caching, and pagination

**Import/Export**: Multiple format support with configurable validation levels

**UI Framework**: Consistent styling, form helpers, pagination controls

Future Phases
=============

- **Phase 2**: Text replacements panel using common infrastructure
- **Phase 3**: Translation history with database integration 
- **Phase 4**: Plugin API with extensibility framework

See Also
========

- Full API documentation: ``preferences_api_documentation.rst``
- Implementation examples in ``tests/preferences/``
- Design documents in ``project_files/preferences/``
