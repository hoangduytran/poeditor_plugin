# Preferences System Architecture

This document describes the modular architecture of the preferences system, organized for maintainability and extensibility.

## Directory Structure

```
preferences/
├── __init__.py                 # Main module interface and API
├── main_dialog.py              # Core preferences dialog
├── common/                     # Shared infrastructure components
│   ├── __init__.py
│   ├── workspace_types.py      # Foundation types and enums
│   ├── data_models.py          # Shared data structures
│   ├── database.py             # SQLite database infrastructure
│   ├── base_components.py      # Base UI components and widgets
│   ├── search_integration.py   # Search functionality
│   └── import_export.py        # File format handlers
├── text_replacements/          # Phase 2: Text Replacements Panel
│   └── __init__.py             # (Placeholder for Phase 2)
├── translation_history/        # Phase 3: Translation History Panel
│   └── __init__.py             # (Placeholder for Phase 3)
└── plugin_api/                 # Phase 4: Plugin integration
    └── __init__.py             # (Placeholder for Phase 4)
```

## Architecture Principles

### 1. **Modular Design**
- Each panel is self-contained with clear interfaces
- Common functionality is shared via the `common/` module
- Panels can be developed and tested independently

### 2. **Separation of Concerns**
- **Common**: Shared infrastructure (database, UI components, search)
- **Panels**: Specific functionality (replacements, history, plugins)
- **Main Dialog**: Coordination and integration

### 3. **Progressive Implementation**
- **Phase 1 (✅ Complete)**: Common infrastructure foundation
- **Phase 2 (🔄 Future)**: Text replacements management
- **Phase 3 (🔄 Future)**: Translation history management  
- **Phase 4 (🔄 Future)**: Plugin integration system

## Common Infrastructure (Phase 1)

### Core Components

#### `workspace_types.py`
- Foundation enums and types
- Integration with existing find/replace system
- Provides: `FindReplaceScope`, `ReplacementCaseMatch`, `PagingMode`

#### `data_models.py`  
- Data structures and record classes
- Provides: `PageInfo`, `PreferenceSearchRequest`, `ReplacementRecord`

#### `database.py`
- SQLite database infrastructure with migrations
- Provides: `DatabaseManager`, `DatabaseMigration`

#### `base_components.py`
- Reusable UI components and widgets
- Provides: `PreferencePage`, `PagedTableWidget`, `FormLayoutHelper`

#### `search_integration.py`
- Advanced search with highlighting and navigation
- Provides: `PreferenceSearchBar`, `SearchResultHighlighter`

#### `import_export.py`
- Multi-format file handling (JSON, CSV, PLIST, YAML)
- Provides: `ImportExportService`, format handlers

## Benefits of This Structure

### ✅ **Maintainability**
- Clear module boundaries reduce coupling
- Easy to modify one panel without affecting others
- Shared code is centralized and reusable

### ✅ **Testability**
- Each panel can be unit tested independently
- Common components have focused test suites
- Integration tests validate panel interactions

### ✅ **Extensibility**
- New panels follow established patterns
- Plugin system can register additional panels
- Common infrastructure supports all panels

### ✅ **Development Workflow**
- Teams can work on different panels simultaneously
- Phases can be implemented incrementally
- Clear API contracts between modules

## Usage Examples

### Basic Import
```python
from preferences import create_preferences_dialog

dialog = create_preferences_dialog(parent)
dialog.show()
```

### Using Common Components
```python
from preferences.common import (
    DatabaseManager, PagedTableWidget, 
    ImportExportService, PreferenceSearchBar
)

# Create database connection
db = DatabaseManager("path/to/preferences.db")

# Create paged table for large datasets
table = PagedTableWidget()

# Handle file imports/exports
service = ImportExportService()
service.export_data(data, "export.json")
```

### Panel-Specific Access (Future)
```python
# Phase 2: Text Replacements
from preferences.text_replacements import ReplacementPanel

# Phase 3: Translation History  
from preferences.translation_history import HistoryPanel

# Phase 4: Plugin API
from preferences.plugin_api import register_plugin_panel
```

## Migration from Flat Structure

The reorganization maintains backward compatibility through the main `__init__.py` file, which re-exports all common components. Existing code will continue to work without changes.

## Next Steps

1. **Phase 2**: Implement text_replacements panel with rule management
2. **Phase 3**: Implement translation_history panel with database integration
3. **Phase 4**: Implement plugin_api with extensibility framework

This architecture provides a solid foundation for the complete preferences system while maintaining clear separation of concerns and supporting future expansion.
