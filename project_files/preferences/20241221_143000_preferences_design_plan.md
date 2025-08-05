# Preferences Dialog Design Plan - Master Overview

## Overview

This document outlines the high-level design for a unified Preferences dialog system for the PySide POEditor Plugin. The design is broken down into multiple focused documents for better maintainability and implementation clarity.

## Document Structure

This master plan is supported by the following detailed design documents:

1. **[Common Components Design](20241221_143001_preferences_common_components.md)** - ✅ **COMPLETE** - Shared UI components and utilities
2. **[Text Replacements Panel Design](20241221_143002_preferences_text_replacements.md)** - ✅ **COMPLETE** - Replacement management functionality
3. **[Translation History Panel Design](20241221_143003_preferences_translation_history.md)** - ✅ **COMPLETE** - History database and search
4. **[Plugin API Design](20241221_143004_preferences_plugin_api.md)** - ✅ **COMPLETE** - Plugin extension system
5. **[Database Schema Design](20241221_143005_preferences_database_schema.md)** - ✅ **COMPLETE** - Data models and persistence

## Design Completion Status

### ✅ All Design Documents Complete

All five supporting design documents have been created and contain comprehensive specifications:

1. **Common Components (20241221_143001)**: 
   - PreferenceSection, PreferencePage, FormLayoutHelper
   - SearchableListWidget, EditableTableWidget, ValidationHelpers
   - Theme integration and change tracking systems

2. **Text Replacements (20241221_143002)**:
   - ReplacementRule and RuleCondition data models
   - ReplacementEngine with regex and text rule support
   - Multi-format import/export (JSON, CSV, PLIST, YAML, etc.)
   - Advanced UI with rule editor and testing capabilities

3. **Translation History (20241221_143003)**:
   - TranslationEntry and TranslationVersion models
   - Database service with SQLite persistence
   - Pagination and search with result navigation
   - Version management and metadata tracking

4. **Plugin API (20241221_143004)**:
   - Plugin lifecycle management and sandbox security
   - Extension points for preferences, context menus, processors
   - Plugin development kit and template system
   - Configuration UI builder for consistent plugin settings

5. **Database Schema (20241221_143005)**:
   - Complete SQLite schema for all data types
   - Migration system with versioning support
   - Repository pattern with Unit of Work
   - Performance optimizations and disaster recovery

## High-Level Architecture

### Main Dialog Structure
```
PreferencesDialog (QDialog)
├── TabWidget (QTabWidget)
│   ├── Text Replacements Tab (ReplacementManagementPanel)
│   ├── Translation History Tab (TranslationHistoryPanel)
│   └── [Plugin Tabs] (Dynamic registration)
├── Common Components
│   ├── PagedTableWidget (reusable table with paging)
│   ├── PreferenceSearchBar (FlagLineEdit + search logic)
│   ├── ImportExportWidget (file format handlers)
│   └── SettingsGroupWidget (common settings UI)
└── Dialog Controls (OK, Cancel, Apply, Reset)
```

### Core Principles

1. **Modular Design**: Each panel is self-contained with clear interfaces
2. **Reusable Components**: Common UI patterns are abstracted into shared widgets
3. **Plugin Extensibility**: Well-defined API for plugin-contributed preference tabs
4. **Consistent UX**: Unified search, paging, and interaction patterns across all tabs
5. **Performance**: Efficient handling of large datasets through paging and lazy loading

### Integration with Plugin Architecture

- **SettingsManager**: Unified settings persistence across all preference panels
- **ThemeManager**: Consistent theming and styling
- **Plugin API**: Extension points for custom preference tabs and functionality
- **Database Layer**: Centralized data access with plugin hooks

## Implementation Phases

### Phase 1: Common Components Foundation
- Implement shared UI components (paging, search, import/export)
- Create base classes for preference panels
- Set up database infrastructure and migrations
- **Target**: Reusable foundation ready for panel implementation

### Phase 2: Text Replacements Panel
- Implement replacement record management
- Add format handlers for import/export
- Create advanced search and filtering
- **Target**: Fully functional replacement management

### Phase 3: Translation History Panel  
- Implement history database integration
- Add advanced search with multiple criteria
- Create version management and navigation
- **Target**: Complete translation history functionality

### Phase 4: Plugin Integration & Polish
- Implement plugin preference API
- Add example plugin with preferences
- Performance optimization and testing
- **Target**: Production-ready preferences system

## Cross-Panel Dependencies

### Shared Data Models
- `PreferenceSearchRequest` - Common search interface
- `PreferenceSearchResult` - Unified search results
- `PageInfo` - Pagination state management
- `PluginPreferenceTab` - Plugin tab interface

### Shared Services
- `PreferenceDataService` - Database abstraction layer
- `PreferenceSearchService` - Unified search functionality
- `ImportExportService` - File format handling
- `PreferenceValidationService` - Data validation

### UI Component Library
- `PagedTableWidget` - Table with built-in paging
- `PreferenceSearchBar` - Advanced search interface
- `SettingsGroupWidget` - Grouped settings controls
- `ImportExportWidget` - File operations interface

## Design Consistency Guidelines

### Search Functionality
- All tables support unified search interface via `PreferenceSearchBar`
- Consistent highlighting and navigation across search results
- Real-time filtering with debounced updates
- Export functionality for search results

### Paging Strategy
- Consistent page size (default 50 items)
- Unified navigation controls and keyboard shortcuts
- Efficient data loading with lazy pagination
- Search results maintain separate paging state

### Import/Export Patterns
- Consistent file format support across relevant panels
- Unified progress reporting and error handling
- Backup creation before destructive operations
- Drag-and-drop support where applicable

### Plugin Integration Points
- Clear API contracts for plugin-contributed tabs
- Consistent settings persistence patterns
- Theme integration for plugin UI components
- Extension points for custom data providers

## Ready for Implementation

With all design documents complete, the project is ready to move into the implementation phase. The designs provide:

- **Clear Architecture**: Modular design with well-defined interfaces
- **Comprehensive Specifications**: Detailed class definitions and database schemas
- **Integration Patterns**: Consistent approaches across all components
- **Extension Points**: Plugin API for future enhancements
- **Performance Considerations**: Pagination, caching, and optimization strategies

## Next Steps

1. **✅ Design Phase Complete** - All design documents created
2. **🔄 Ready for Implementation** - Begin with Phase 1: Common Components Foundation
3. **📋 Implementation Order**:
   - Phase 1: Core infrastructure and shared components
   - Phase 2: Text replacements panel with database integration
   - Phase 3: Translation history panel with advanced search
   - Phase 4: Plugin integration and testing

The comprehensive design documentation ensures smooth implementation with minimal design decisions needed during development.

---

## Find/Replace Integration & Search Support

### Find/Replace Types Integration (from workspace/find_replace_types.py)

The preferences will integrate with the existing find/replace system:

```python
# Integration with workspace find/replace types
from workspace.find_replace_types import (
    FindReplaceRequest,          # 40 references
    FindReplaceResult,           # 296 references  
    MatchInstance,               # 32 references
    MatchPair,                   # 16 references
    ReplacementCaseMatch,        # 66 references
    FindReplaceScope,            # 12 references
    PagingMode,                  # 19 references
    EmptyMode                    # 35 references
)

# Enhanced search request for preferences
class PreferenceSearchRequest(FindReplaceRequest):
    """Extended search request for preference dialogs."""
    def __init__(self, query: str, scope: FindReplaceScope = FindReplaceScope.ALL,
                 case_match: ReplacementCaseMatch = ReplacementCaseMatch.IGNORE,
                 use_regex: bool = False, table_type: str = "replacement"):
        super().__init__(query, scope, case_match, use_regex)
        self.table_type = table_type  # "replacement" or "history"
        self.date_filter = None
        self.context_filter = None

# Search result for preferences with highlighting
class PreferenceSearchResult(FindReplaceResult):
    """Search result for preference tables with match highlighting."""
    def __init__(self, record_id: int, record: any, 
                 match_instances: List[MatchInstance]):
        super().__init__(record_id, record, match_instances)
        self.table_row = None
        self.display_text = ""
        self.relevance_score = 0.0
```

### Search Bar with FlagLineEdit (from workspace/find_replace_bar.py)

Both preference tabs will include advanced search capabilities:

```python
# Preference search bar component (adapted from FlagLineEdit - 4 references)
class PreferenceFlagLineEdit(FlagLineEdit):
    """Search field for preferences with flag buttons for search options."""
    
    def __init__(self, parent=None, placeholder: str = "Search..."):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.search_flags = {
            'case_sensitive': False,
            'use_regex': False,
            'whole_word': False,
            'search_scope': FindReplaceScope.ALL
        }
        self._setup_flag_buttons()
    
    def _setup_flag_buttons(self):
        """Setup flag buttons for search options"""
        # Case sensitive toggle
        # Regex toggle  
        # Whole word toggle
        # Scope selector
    
    def get_search_request(self) -> PreferenceSearchRequest:
        """Get current search configuration as request object"""
        pass

# Preference search bar (adapted from FindReplaceBar - 16 references)
class PreferenceSearchBar(FindReplaceBar):
    """Enhanced search bar for preferences with find/replace functionality."""
    
    def __init__(self, parent=None, table_type: str = "replacement"):
        super().__init__(parent)
        self.table_type = table_type
        self.current_results = []  # List of PreferenceSearchResult
        self.current_match_index = 0
        self._setup_preference_specific_controls()
    
    def _setup_preference_specific_controls(self):
        """Add preference-specific search controls"""
        # Date range filter for history
        # Context filter for replacements
        # Export results button
    
    def search_in_table(self, query: str) -> List[PreferenceSearchResult]:
        """Perform search in preference table"""
        pass
    
    def highlight_current_match(self, result: PreferenceSearchResult):
        """Highlight current search match in table"""
        pass
```

## Tab 1: Text Replacements

### Purpose
Manage text replacement rules for automatic text transformation during translation editing, supporting multiple file formats and providing advanced search capabilities with paging support.

### Components

#### 1.1 Replacement Management Panel with Table Model & Paging
```python
# Replacement table model with paging support
class ReplacementTableModel(QAbstractTableModel):
    """Table model for replacement rules with paging and search support."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_records = []  # Complete list of ReplacementRecord
        self.filtered_records = []  # Filtered results
        self.current_page_records = []  # Current page data
        self.page_size = 50
        self.current_page = 1
        self.search_results = []  # List of PreferenceSearchResult
        self.headers = ["Enabled", "Find Text", "Replace Text", "Context", "Options"]
    
    def setRecords(self, records: List[ReplacementRecord]):
        """Set all replacement records"""
        pass
    
    def setPage(self, page: int, page_size: int = None):
        """Load specific page of data"""
        pass
    
    def applySearch(self, results: List[PreferenceSearchResult]):
        """Apply search results to table"""
        pass
    
    def getPageInfo(self) -> dict:
        """Get pagination information"""
        return {
            'current_page': self.current_page,
            'total_pages': self.get_total_pages(),
            'page_size': self.page_size,
            'total_records': len(self.filtered_records or self.all_records)
        }
```

#### 1.2 Search Integration with FlagLineEdit
- **PreferenceFlagLineEdit**: Advanced search field with flag buttons
- **Real-time filtering**: Filter replacement rules as user types
- **Regex support**: Pattern matching with ReplacementCaseMatch
- **Context filtering**: Filter by specific contexts
- **Highlight matches**: Visual highlighting of search matches in table

#### 1.3 Import/Export Support
Based on the old app analysis, support for multiple formats with dedicated handlers:

- **Supported Formats**:
  - `.plist` (macOS Property List) - PlistHandler (2 references)
  - `.json` (JSON format) - JsonHandler (2 references)
  - `.csv` (Comma-separated values) - CsvHandler (2 references)
  - `.yaml` (YAML format) - YamlHandler (3 references)
  - `.ahk` (AutoHotkey format) - AHKHandler (2 references)
  - `.acl` (ACL format) - AclHandler (2 references)
  - `.sqlite` (SQLite database) - SqliteHandler (3 references)
  - `.m17n` (M17n database format) - M17nHandler (2 references)
  - Bamboo Macro format - BambooMacroHandler (2 references)

#### 1.4 Advanced Features
- **Pattern Matching**: Support for regex patterns in replacement rules
- **Context-Sensitive**: Apply rules based on msgid context or file type
- **Case Handling**: Intelligent case preservation (ReplacementCaseMatch - 66 references)
- **Backup/Restore**: Automatic backup before major changes
- **Plugin Integration**: Allow plugins to register custom replacement handlers
- **Paging Navigation**: Navigate through large datasets efficiently

### Database Schema for Replacements
```sql
CREATE TABLE replacement_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    find_text TEXT NOT NULL,
    replace_text TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    case_sensitive BOOLEAN DEFAULT 0,
    use_regex BOOLEAN DEFAULT 0,
    context TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_replacement_find ON replacement_rules(find_text);
CREATE INDEX idx_replacement_context ON replacement_rules(context);
CREATE INDEX idx_replacement_enabled ON replacement_rules(enabled);
```

### Key Classes (Adapted from old design)
```python
# Core replacement system with database integration and paging
class ReplacementEngine:
    """Main engine to import/export across multiple formats with database persistence."""
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self._get_default_db_path()
        self.handlers = {}  # Format handlers registry
        self.table_model = ReplacementTableModel()
        self._init_database()
        self._register_default_handlers()
    
    def import_file(self, file_path: str) -> List[ReplacementRecord]
    def export_file(self, file_path: str, records: List[ReplacementRecord])
    def get_all_records(self) -> List[ReplacementRecord]
    def get_page_records(self, page: int, page_size: int) -> List[ReplacementRecord]
    def search_records(self, request: PreferenceSearchRequest) -> List[PreferenceSearchResult]
    def save_record(self, record: ReplacementRecord) -> bool
    def delete_record(self, record_id: int) -> bool

class ReplacementActions:
    """UI action handling with database operations and search support."""
    def __init__(self, engine: ReplacementEngine):
        self.engine = engine
        self.search_bar = PreferenceSearchBar(table_type="replacement")
        self.current_search_results = []
        self.current_page = 1
    
    def import_file(self, file_path: str)
    def export_current(self, file_path: str)
    def save_edit(self, record: ReplacementRecord)
    def delete_selected(self, record_ids: List[int])
    def on_search_requested(self, request: PreferenceSearchRequest)
    def on_page_changed(self, page: int)
    def on_search_navigation(self, direction: str)  # "next", "prev"

# Plugin integration
class ReplacementPluginAPI:
    def register_format_handler(self, extension: str, handler: BaseHandler)
    def register_replacement_provider(self, provider: ReplacementProvider)
    def register_search_provider(self, provider: SearchProvider)
```

## Tab 2: Translation History

### Purpose
Manage translation history database, view/search historical translations, and configure history retention policies with plugin extensibility and advanced paging/search support.

### Components

#### 2.1 Database Management Panel
- **Database Location**: Path to SQLite database file
- **Database Size**: Current size and record count display using DatabasePORecord
- **Maintenance Tools**: Vacuum, reindex, integrity check
- **Import/Export**: Backup and restore database functionality
- **Clear Options**: Clear by date range, project, or complete reset

#### 2.2 History View & Search Panel with Table Model & Paging
```python
# History table model with paging support (adapted from HistoryTableModel - 3 references)
class HistoryTableModel(QAbstractTableModel):
    """Table model for displaying translation history with paging and search support."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_records = []  # Complete list of DatabasePORecord
        self.filtered_records = []  # Filtered results
        self.current_page_records = []  # Current page data
        self.page_size = 50
        self.current_page = 1
        self.search_results = []  # List of PreferenceSearchResult
        self.headers = ["ID", "Message ID", "Context", "Translation", "Source", "Modified"]
        self.paging_mode = PagingMode.DATABASE  # or PagingMode.SEARCH
    
    def setRecords(self, records: List[DatabasePORecord]):
        """Set all history records"""
        pass
    
    def setPage(self, page: int, page_size: int = None):
        """Load specific page of data"""
        pass
    
    def applySearch(self, results: List[PreferenceSearchResult]):
        """Apply search results to table"""
        self.search_results = results
        self.paging_mode = PagingMode.SEARCH
        self._refresh_current_page()
    
    def setPagingMode(self, mode: PagingMode):
        """Switch between database and search paging modes"""
        pass
    
    def getPageInfo(self) -> dict:
        """Get pagination information"""
        return {
            'current_page': self.current_page,
            'total_pages': self.get_total_pages(),
            'page_size': self.page_size,
            'total_records': len(self.filtered_records or self.all_records),
            'paging_mode': self.paging_mode
        }
```

#### 2.3 Advanced Search with FlagLineEdit
- **PreferenceFlagLineEdit**: Advanced search field for history
- **Multi-field search**: Search in msgid, msgstr, context simultaneously
- **Date range filtering**: Filter by creation/modification dates
- **Source filtering**: Filter by translation source (manual, auto, import)
- **Fuzzy status filtering**: Filter by fuzzy flag status
- **Advanced highlighting**: Visual highlighting with MatchInstance support

#### 2.4 History Settings Panel
- **Retention Policy**: Configure how long to keep history
- **Auto-cleanup**: Automatic cleanup of old records
- **Storage Limits**: Maximum database size limits
- **Sync Settings**: Synchronization with external services (plugin-extensible)

### Database Schema for Translation History
```sql
-- Main translation entries table
CREATE TABLE translation_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msgid TEXT NOT NULL,
    msgctxt TEXT,
    current_msgstr TEXT,
    fuzzy BOOLEAN DEFAULT 0,
    line_number INTEGER,
    source_file TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(msgid, msgctxt)
);

-- Translation versions/history table
CREATE TABLE translation_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER REFERENCES translation_entries(id),
    msgstr TEXT NOT NULL,
    source TEXT DEFAULT 'manual',  -- 'manual', 'auto', 'import', etc.
    version_number INTEGER DEFAULT 1,
    confidence_score REAL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT 0
);

-- File references table
CREATE TABLE file_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER REFERENCES translation_entries(id),
    file_path TEXT NOT NULL,
    line_number INTEGER,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_translation_msgid ON translation_entries(msgid);
CREATE INDEX idx_translation_msgctxt ON translation_entries(msgctxt);
CREATE INDEX idx_translation_modified ON translation_entries(modified_date);
CREATE INDEX idx_translation_fuzzy ON translation_entries(fuzzy);
CREATE INDEX idx_version_entry ON translation_versions(entry_id);
CREATE INDEX idx_version_current ON translation_versions(is_current);
CREATE INDEX idx_version_source ON translation_versions(source);
CREATE INDEX idx_file_ref_entry ON file_references(entry_id);
```

### Key Classes (Adapted from old design)
```python
# Core history system with enhanced database support and paging
class TranslationDB:
    """Encapsulates all SQLite logic for translation history storage with plugin hooks."""
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self._get_default_db_path()
        self.connection = None
        self.storage_providers = {}  # Plugin storage providers
        self.table_model = HistoryTableModel()
        self._ensure_schema()
    
    def get_entry(self, msgid: str, msgctxt: str = None) -> DatabasePORecord
    def add_entry(self, record: DatabasePORecord) -> int
    def update_entry(self, record: DatabasePORecord) -> bool
    def delete_entry(self, entry_id: int) -> bool
    def list_entries_page(self, page: int, page_size: int) -> List[DatabasePORecord]
    def search_entries(self, request: PreferenceSearchRequest) -> List[PreferenceSearchResult]
    def get_entry_versions(self, entry_id: int) -> List[TranslationRecord]
    def add_version(self, entry_id: int, record: TranslationRecord) -> bool
    def get_total_records(self) -> int

class TranslationHistoryDialog:
    """Main UI component with database integration, search support, and paging."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = TranslationDB()
        self.table_model = self.db.table_model
        self.search_bar = PreferenceSearchBar(table_type="history")
        self.current_search_results = []
        self.nav_records = []  # List of NavRecord for navigation
        self.current_page = 1
        self._create_widgets()
        self._connect_signals()
    
    def _load_database_page(self, page: int, page_size: int = 50):
        """Load specific page from database"""
        records = self.db.list_entries_page(page, page_size)
        self.table_model.setPage(page, page_size)
        self.table_model.setRecords(records)
        self._build_nav_records(records)
    
    def _load_search_page(self, search_results: List[PreferenceSearchResult]):
        """Load search results with paging"""
        self.table_model.applySearch(search_results)
        self.current_search_results = search_results
        self._build_nav_records_from_search(search_results)
    
    def _on_search_requested(self, request: PreferenceSearchRequest):
        """Handle search request"""
        results = self.db.search_entries(request)
        self._load_search_page(results)
        self.search_bar.setResultsCount(len(results))
    
    def _on_page_navigation(self, page: int):
        """Handle page navigation"""
        if self.table_model.paging_mode == PagingMode.SEARCH:
            self._navigate_search_page(page)
        else:
            self._load_database_page(page)
    
    def _update_translation_editor_with_record(self, record: DatabasePORecord):
        """Update editor with selected record"""
        pass
    
    def _build_nav_records(self, records: List[DatabasePORecord]) -> List[NavRecord]:
        """Build navigation records for current page"""
        pass

# Plugin integration  
class HistoryPluginAPI:
    def register_storage_provider(self, provider: StorageProvider)
    def register_sync_service(self, service: SyncService)
    def register_export_format(self, format: ExportFormat)
    def register_search_provider(self, provider: SearchProvider)
```

## Additional Record Classes for Navigation & Search

### Search and Navigation Support
```python
# Enhanced search request with database integration
class HistorySearchRequest(PreferenceSearchRequest):
    """Search parameters for translation history."""
    def __init__(self, query: str, search_in: str = "both", 
                 case_match: ReplacementCaseMatch = ReplacementCaseMatch.IGNORE,
                 use_regex: bool = False, date_from: datetime = None, 
                 date_to: datetime = None, context_filter: str = None,
                 source_filter: str = None, fuzzy_filter: bool = None):
        super().__init__(query, FindReplaceScope.ALL, case_match, use_regex, "history")
        self.search_in = search_in  # "msgid", "msgstr", "both"
        self.date_from = date_from
        self.date_to = date_to
        self.context_filter = context_filter
        self.source_filter = source_filter
        self.fuzzy_filter = fuzzy_filter

# Enhanced navigation with page support
class HistoryNavigation:
    """Manages navigation state for translation history with paging modes."""
    def __init__(self, db: TranslationDB):
        self.db = db
        self.current_page = 1
        self.page_size = 50
        self.total_records = 0
        self.nav_records = []  # List of NavRecord
        self.paging_mode = PagingMode.DATABASE
        self.search_results = []  # List of PreferenceSearchResult
        self.current_search_request = None
    
    def go_to_page(self, page: int) -> List[DatabasePORecord]:
        """Navigate to specific page based on current mode"""
        if self.paging_mode == PagingMode.SEARCH:
            return self._navigate_search_page(page)
        else:
            return self._navigate_database_page(page)
    
    def search(self, request: HistorySearchRequest) -> List[PreferenceSearchResult]:
        """Perform search and switch to search paging mode"""
        results = self.db.search_entries(request)
        self.search_results = results
        self.paging_mode = PagingMode.SEARCH
        self.current_search_request = request
        return results
    
    def build_navigation(self, records: List[DatabasePORecord]) -> List[NavRecord]:
        """Build navigation records for current page"""
        pass
    
    def get_page_info(self) -> dict:
        """Get pagination information for current mode"""
        if self.paging_mode == PagingMode.SEARCH:
            total_records = len(self.search_results)
        else:
            total_records = self.db.get_total_records()
        
        return {
            'current_page': self.current_page,
            'total_pages': (total_records + self.page_size - 1) // self.page_size,
            'page_size': self.page_size,
            'total_records': total_records,
            'paging_mode': self.paging_mode
        }
```

## Plugin Extension System

### Plugin Preference API with Database Support

```python
class PreferencePluginAPI:
    """API for plugins to register preference tabs with database integration."""
    
    def register_preference_tab(self, 
                               tab_name: str, 
                               tab_widget: QWidget,
                               icon: Optional[QIcon] = None,
                               position: int = -1) -> bool:
        """Register a new preference tab"""
        
    def get_plugin_settings(self, plugin_id: str) -> dict:
        """Get settings for a specific plugin"""
        
    def set_plugin_settings(self, plugin_id: str, settings: dict) -> bool:
        """Save settings for a specific plugin"""
        
    def register_data_provider(self, provider: DataProvider) -> bool:
        """Register custom data providers for replacements or history"""
        
    def get_database_connection(self, db_type: str) -> Any:
        """Get database connection for plugin use"""
```

## Implementation Strategy

### Phase 1: Core Infrastructure & Data Models
1. Create base database record classes (ReplacementRecord, DatabasePORecord, etc.)
2. Implement table models with paging support (ReplacementTableModel, HistoryTableModel)
3. Create search integration with FlagLineEdit and find/replace types
4. Implement database schemas and migration system
5. Create base PreferencesDialog framework
6. Set up plugin preference API structure

### Phase 2: Text Replacements Tab with Table Model & Search
1. Port and enhance ReplacementEngine with database persistence and paging
2. Implement ReplacementTableModel with search and paging support
3. Create PreferenceFlagLineEdit for advanced search
4. Implement all format handlers (Plist, JSON, CSV, etc.)
5. Create ReplacementsDialog as embeddable widget with table model integration
6. Add plugin extension points for custom handlers and search providers

### Phase 3: Translation History Tab with Enhanced Table Model & Search
1. Port and enhance TranslationDB with plugin hooks and paging
2. Implement HistoryTableModel with dual paging modes (database/search)
3. Create advanced search with date/source/fuzzy filtering
4. Implement all record classes (DatabasePORecord, TranslationRecord, etc.)
5. Create TranslationHistoryDialog with advanced search and navigation
6. Add plugin extension points for storage providers and sync services

### Phase 4: Plugin Integration & Advanced Features
1. Implement plugin preference registration with database support
2. Add plugin-specific settings management with proper data models
3. Create example plugin with preferences, table models, and search integration
4. Document plugin preference API and database access patterns
5. Add export functionality for search results
6. Implement advanced navigation with NavRecord support

## Data Migration Strategy

### From Old App to New System
1. **Replacement Data**: Migrate existing replacement rules to new database schema
2. **History Data**: Port translation history with version preservation
3. **Settings Migration**: Convert old settings format to new unified system
4. **Backup Strategy**: Create backup before migration with rollback capability

### Database Versioning
```python
class DatabaseMigration:
    """Handle database schema migrations."""
    CURRENT_VERSION = 1
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def migrate_to_current(self) -> bool
    def get_current_version(self) -> int
    def backup_database(self, backup_path: str) -> bool
    def restore_from_backup(self, backup_path: str) -> bool
```

---

## Conclusion

This enhanced design provides a comprehensive, plugin-extensible preferences system that builds upon the proven functionality and data models of the old PO app. The inclusion of proper POJO-like record classes (ReplacementRecord, DatabasePORecord, TranslationRecord, etc.) combined with advanced table models supporting paging, sophisticated search capabilities with FlagLineEdit integration, and find/replace types from the workspace ensures both robust data management and excellent user experience.

The integration of table models with paging support, search functionality with highlighting, and navigation controls provides a professional-grade interface that can handle large datasets efficiently while maintaining responsive UI performance. The plugin API and database abstraction ensure future extensibility and customization while preserving the modular architecture principles.
