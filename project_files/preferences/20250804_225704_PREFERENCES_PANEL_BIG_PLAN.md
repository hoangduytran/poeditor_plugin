# Preferences Sidebar Panel - BIG Implementation Plan

## Executive Summary

This document outlines a comprehensive plan for implementing the Preferences sidebar panel based on the analysis of the old preferences system (`project_files/old_po_app_design/old_codes/pref/preferences.py`) and current architecture. The plan prioritizes shared components and the unified paging mechanism for database operations, replacement management, and translation history.

## 1. Architecture Overview

### 1.1 Current Old System Analysis

From the old code analysis, the preferences system consisted of:

**Main Tabs Structure:**
- **Fonts and Languages** (`FontSettingsTab`) - msgid, msgstr, table, comment, suggestion, control fonts
- **Replacements** (`ReplacementSettingsTab`) - Text replacement rules with database operations  
- **Keyboard Mappings** (`KeyboardSettingsTab`) - Shortcut configurations
- **Translation History** (`TranslationHistoryDialog`) - Database with paging mechanism
- **Editor** (`EditorSettingsWidget`) - Page sizes, font settings, table navigation settings
- **Translation/PO** (`TranslationSettingsWidget`) - Translation validation rules
- **Appearance** (`AppearanceSettingsWidget`) - Theme/styling settings (placeholder)
- **Network** (`NetworkSettingsWidget`) - Network configurations (placeholder)
- **Advanced** (`AdvancedSettingsWidget`) - Advanced configurations (placeholder)

**Key Shared Components Identified:**
1. **Unified Pagination System** - Existing comprehensive pagination framework from `/project_files/20240731_pagination/`
2. **Font Management System** - Common font handling for all UI components
3. **Database Import/Export** - Plist operations for replacements & history with fast import
4. **Settings Persistence** - QSettings integration
5. **Common UI Layouts** - Form layouts, group boxes, validation

### 1.2 Target Architecture

The preferences system integrates with the existing **Unified Pagination Framework** documented in `/project_files/20240731_pagination/`. This provides:

- **PaginationController** - Base controller for database and model pagination
- **PaginationWidget** - Standard UI components (navigation buttons, page size selector, go-to-page)
- **DatabasePaginationController** - Specialized controller for database operations
- **TablePagerBase** - Existing table pagination abstraction
- **IPaginationWidget** - Interface for consistent pagination UI

```
PreferencesPanel (Sidebar Panel)
├── Shared Components (Phase 1 - Priority) 
│   ├── ExistingPaginationIntegration
│   │   ├── DatabasePaginationController (from unified system)
│   │   ├── PaginationWidget (from unified system)
│   │   ├── CompactPaginationControls (from unified system)
│   │   └── PreferencesPagingSettingsManager (preferences-specific)
│   ├── FontManagementSystem  
│   │   ├── FontSelectorWidget
│   │   ├── FontPreviewWidget
│   │   └── FontApplicationService
│   ├── DatabaseOperations
│   │   ├── PlistImportExportService
│   │   ├── DatabaseConnectionManager
│   │   ├── FastImportService (1,000+ entries/second)
│   │   └── BackupRestoreService
│   └── CommonUIComponents
│       ├── SettingsGroupWidget
│       ├── ValidationInputWidget
│       └── PreviewPanelWidget
├── Core Panels (Phase 2)
│   ├── ReplacementPanel (Database + Existing Pagination)
│   ├── TranslationHistoryPanel (Database + Existing Pagination)
│   ├── FontSettingsPanel
│   └── EditorSettingsPanel (Pagination Settings Management)
└── Extended Panels (Phase 3)
    ├── KeyboardPanel
    ├── AppearancePanel
    ├── TranslationValidationPanel
    └── AdvancedPanel
```

## 2. Phase 1: Shared Components Implementation (Days 1-7)

### 2.1 Integration with Existing Pagination System (Days 1-3)

**Goal:** Integrate with the existing unified pagination framework from `/project_files/20240731_pagination/` rather than creating new components.

**Existing Components to Use:**
- **PaginationController** - Base controller class
- **DatabasePaginationController** - Database-specific controller  
- **PaginationWidget** - Standard pagination UI with navigation buttons
- **CompactPaginationControls** - Minimal space pagination UI
- **IPaginationWidget** - Interface for consistent pagination behavior

**Preferences-Specific Extensions:**
```python
# services/preferences_paging_service.py
class PreferencesPagingSettingsManager(QObject):
    """Manages pagination settings specific to preferences panels"""
    
    def get_replacement_page_size(self) -> int:
        # Returns: replacement_table_page_size (default: 22)
    
    def get_history_page_size(self) -> int:
        # Returns: history_table_page_size (default: 22)
    
    def get_main_table_page_size(self) -> int:
        # Returns: main_table_page_size (default: 50) 
    
    def get_scroller_pages(self, component_name: str) -> int:
        # Returns: scroller_pages setting for component (default: 15)
        
# widgets/preferences/preferences_pagination_factory.py
class PreferencesPaginationFactory:
    """Factory for creating pagination components for preferences panels"""
    
    @staticmethod
    def create_database_pagination(table_widget, database_service, 
                                 component_name: str) -> DatabasePaginationController:
        # Creates configured pagination controller for database operations
        
    @staticmethod  
    def create_pagination_widget(controller, compact: bool = False) -> IPaginationWidget:
        # Creates appropriate pagination widget (full or compact)
```

**Implementation Steps:**
1. **Day 1:** Create `PreferencesPagingSettingsManager` extending existing pagination settings
2. **Day 2:** Implement `PreferencesPaginationFactory` for preferences-specific pagination
3. **Day 3:** Create integration layer between existing pagination and preferences database operations

### 2.2 Font Management System (Days 4-5)

**Goal:** Centralized font management for all preference components.

**Key Components:**
```python
# widgets/shared/font_selector_widget.py
class FontSelectorWidget(QWidget):
    """Unified font selector with family/size/preview"""
    
    fontChanged = Signal(QFont)
    
    def __init__(self, component_name: str, default_size: int = 12):
        # QFontComboBox for family
        # QSpinBox for size
        # Preview label
        # Settings integration
        
# widgets/shared/font_preview_widget.py
class FontPreviewWidget(QLabel):
    """Standardized font preview with sample text"""
    
    def update_preview(self, font: QFont):
        # Updates preview with font
        # Shows sample text: "AaBbCc 123 !@#"
        
# services/font_application_service.py
class FontApplicationService(QObject):
    """Service for applying fonts throughout application"""
    
    def apply_component_font(self, component_name: str, font: QFont):
        # Applies font to specific component types
        # Handles: msgid, msgstr, table, comment, suggestion, control
        
    def load_font_settings(self) -> Dict[str, QFont]:
        # Loads all font settings from QSettings
        
    def save_font_settings(self, fonts: Dict[str, QFont]):
        # Saves font settings to QSettings
```

**Font Components from Old System:**
```python
FONT_COMPONENTS = [
    {"name": "msgid", "display": "Message ID (msgid)", "default_size": 15},
    {"name": "msgstr", "display": "Translation (msgstr)", "default_size": 24},
    {"name": "table", "display": "Table", "default_size": 13},
    {"name": "comment", "display": "Comments", "default_size": 15},
    {"name": "suggestion", "display": "Suggestions", "default_size": 13},
    {"name": "control", "display": "Controls (Buttons, Labels, Headers)", "default_size": 12}
]
```

### 2.3 Database Operations Service (Days 6-7)

**Goal:** Unified database operations for replacements and translation history with fast import capabilities.

**Database Architecture Overview:**

The preferences system manages **two completely separate databases**:

1. **Replacement Rules Database** - Simple table for text replacements
2. **Translation History Database** - Complex schema with versioning and fast import

**Key Components:**
```python
# services/database_service.py
class DatabaseService(QObject):
    """Unified database operations service for both databases"""
    
    def __init__(self):
        # Manages separate connections for replacement and translation DBs
        # Transaction handling for each database
        # Error handling and recovery
        
    def execute_paged_query(self, 
                           query: str, 
                           page: int, 
                           page_size: int,
                           database: str = "replacements") -> Tuple[List, int]:
        # Returns: (results, total_count)
        # Supports both replacement and translation databases
        
    def import_from_plist(self, file_path: str, database: str, table_name: str):
        # Import data from plist file to specific database
        
    def export_to_plist(self, file_path: str, database: str, table_name: str):
        # Export data to plist file from specific database

# services/replacement_database_service.py
class ReplacementDatabaseService(QObject):
    """Service for replacement rules database operations"""
    
    def __init__(self, db_path: str = "replacements.db"):
        # Simple database with single table:
        # replacements(id, find_text, replace_text, enabled, notes, created, modified)
        
    def add_replacement(self, find_text: str, replace_text: str, enabled: bool = True, notes: str = ""):
        # Add new replacement rule
        
    def update_replacement(self, rule_id: int, **kwargs):
        # Update existing replacement rule
        
    def delete_replacement(self, rule_id: int):
        # Delete replacement rule
        
    def search_replacements(self, search_text: str, page: int = 0, page_size: int = 22):
        # Paginated search in replacement rules
        
    def import_from_plist(self, file_path: str):
        # Import replacement rules from plist file
        
    def export_to_plist(self, file_path: str):
        # Export replacement rules to plist file

# services/translation_history_database_service.py
class TranslationHistoryDatabaseService(QObject):
    """Service for translation history database operations"""
    
    def __init__(self, db_path: str = "translation_history.db"):
        # Complex schema with two main tables:
        # english_text(unique_id, msgid, context)
        # tran_text(unique_id, version_id, tran_text, source, timestamp)
        
    def add_translation(self, msgid: str, translation: str, context: str = None, source: str = "manual"):
        # Add new translation entry with versioning
        
    def update_translation(self, unique_id: int, translation: str, source: str = "manual"):
        # Add new version of existing translation
        
    def search_translations(self, 
                          search_text: str = "",
                          context: str = None,
                          date_from: QDate = None,
                          date_to: QDate = None,
                          page: int = 0,
                          page_size: int = 22) -> Tuple[List, int]:
        # Advanced paginated search with multiple criteria
        
    def fast_import_po(self, file_path: str, dict_type: str = "project") -> int:
        """Fast bulk import algorithm for large PO files"""
        # 1. Bulk insert source texts (INSERT OR IGNORE for deduplication)
        # 2. Create msgid->unique_id mapping in memory
        # 3. Batch insert translations with version management
        # 4. Source attribution for tracking import origin
        # Performance: 1,000+ entries/second for batch imports
        
    def bulk_import(self, source_data: List[Dict], source: str = "bulk") -> ImportResult:
        """Bulk import with progress tracking"""
        # Uses fast_import_po algorithm internally
        # Progress callbacks for UI updates
        # Transaction management for data integrity
        
    def export_po(self, file_path: str, filter_query: Dict = None) -> int:
        # Export complete database as standard PO file
        # Uses latest translation version for each entry
        # Preserves msgctxt and metadata
        
    def import_from_plist(self, file_path: str):
        # Import translation history from plist file
        
    def export_to_plist(self, file_path: str):
        # Export translation history to plist file

# services/plist_import_export_service.py
class PlistImportExportService(QObject):
    """Unified plist import/export operations for both databases"""
    
    importProgress = Signal(int, str)  # progress, message
    exportProgress = Signal(int, str)  # progress, message
    
    def __init__(self):
        self.replacement_service = ReplacementDatabaseService()
        self.translation_service = TranslationHistoryDatabaseService()
    
    def import_replacements(self, file_path: str):
        # Import replacement rules from plist
        # Delegates to ReplacementDatabaseService
        
    def export_replacements(self, file_path: str):
        # Export replacement rules to plist
        
    def import_translation_history(self, file_path: str):
        # Import translation history from plist
        # Delegates to TranslationHistoryDatabaseService
        
    def export_translation_history(self, file_path: str):
        # Export translation history to plist
        
    def fast_import_translations(self, file_path: str, source_type: str = "project"):
        # High-performance import using fast_import_po algorithm
        # Progress tracking and UI updates
        # Error handling and rollback capabilities
```

**Database Schemas:**

**Replacement Rules Database:**
```sql
CREATE TABLE replacements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    find_text TEXT NOT NULL,
    replace_text TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    notes TEXT DEFAULT '',
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_replacements_find_text ON replacements(find_text);
CREATE INDEX idx_replacements_enabled ON replacements(enabled);
```

**Translation History Database:**
```sql
-- Source texts table
CREATE TABLE english_text (
    unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
    msgid TEXT NOT NULL,
    context TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Translation versions table
CREATE TABLE tran_text (
    unique_id INTEGER NOT NULL,
    version_id INTEGER NOT NULL,
    tran_text TEXT NOT NULL,
    source TEXT DEFAULT 'manual',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (unique_id, version_id),
    FOREIGN KEY (unique_id) REFERENCES english_text(unique_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_english_msgid ON english_text(msgid);
CREATE INDEX idx_english_context ON english_text(context);
CREATE INDEX idx_tran_text_source ON tran_text(source);
CREATE INDEX idx_tran_text_timestamp ON tran_text(timestamp);
CREATE INDEX idx_tran_text_content ON tran_text(tran_text);
```

**Fast Import Performance Features:**
- **Bulk Insert Operations**: Uses INSERT OR IGNORE for deduplication
- **In-Memory Mapping**: Creates msgid->unique_id mapping for speed
- **Batch Processing**: Groups operations for transaction efficiency
- **Progress Tracking**: Real-time progress updates for UI
- **Source Attribution**: Tracks import source for all entries
- **Version Management**: Handles duplicate translations as versions
- **Error Recovery**: Transaction rollback on failure

## 3. Phase 2: Core Panels Implementation (Days 8-14)

### 3.1 Replacement Panel (Days 8-10)

**Goal:** Replacement rules management with separate database operations using existing pagination framework.

**Database Details:**
- **Separate Database File**: `replacements.db`
- **Simple Schema**: Single table with find/replace text pairs
- **Fast Operations**: Optimized for quick CRUD operations
- **Plist Export/Import**: Compatible with macOS text replacement format
- **Pagination Integration**: Uses existing `DatabasePaginationController`

**Features from Old System:**
- Add/Edit/Delete replacement rules
- Import/Export from/to plist files (macOS text replacement format)
- Search and filter functionality
- Paged table with 22 items per page (configurable via existing pagination settings)
- Preview of replacement effects
- Enable/disable individual rules
- Notes and metadata for each rule

**Key Components:**
```python
# panels/preferences/replacement_panel.py
class ReplacementPanel(QWidget):
    """Replacement rules management panel using existing pagination framework"""
    
    def __init__(self):
        # Table widget with existing pagination integration
        # Add/Edit/Delete buttons
        # Import/Export buttons (macOS plist support)
        # Search/Filter controls
        # Preview area
        # Enable/disable toggle
        
    def setup_ui(self):
        # Main layout with table + controls
        # Existing PaginationWidget at bottom
        # Toolbar with actions (Add, Edit, Delete, Import, Export)
        # Search box with real-time filtering
        
    def setup_pagination(self):
        # Use existing DatabasePaginationController
        # Connect to ReplacementDatabaseService
        # Load page size from PreferencesPagingSettingsManager (default: 22)
        self.pagination_controller = PreferencesPaginationFactory.create_database_pagination(
            self.table_widget, self.database_service, "replacement_table")
        self.pagination_widget = PreferencesPaginationFactory.create_pagination_widget(
            self.pagination_controller, compact=False)
        
    def setup_database_operations(self):
        # Connect to ReplacementDatabaseService
        # Handle import/export progress
        # Manage transactions and error handling
        
    def import_from_plist(self):
        # Import macOS text replacement plist files
        # Progress dialog for large imports
        # Conflict resolution options
        
    def export_to_plist(self):
        # Export to macOS-compatible plist format
        # Filter options (enabled only, date range, etc.)
        
    def fast_import_bulk_data(self, data_list: List[Dict]):
        # High-performance bulk import
        # Progress tracking and cancellation
        # Validation and error reporting
        
# models/replacement_model.py
class ReplacementTableModel(QAbstractTableModel):
    """Model for replacement rules table with pagination support"""
    
    # Columns: ID, Find Text, Replace Text, Enabled, Notes, Created, Modified
    # Supports sorting and filtering
    # Integrates with existing pagination framework
    # Real-time search capability
    # Implements TableDataProvider interface from unified pagination
    
# services/replacement_database_service.py
class ReplacementDatabaseService(QObject):
    """Dedicated service for replacement database operations"""
    
    def __init__(self, db_path: str = "replacements.db"):
        # Initialize replacement-specific database
        # Simple, fast schema optimized for text replacement
        # Implements PaginationDataProvider interface
        
    def get_paged_replacements(self, page: int, page_size: int, 
                              search_filter: str = "") -> Tuple[List, int]:
        # Paginated query with optional search filter
        # Compatible with existing DatabasePaginationController
        # Optimized for fast display
        
    def bulk_import_replacements(self, replacements: List[Dict], 
                               progress_callback=None) -> int:
        # High-performance bulk import
        # Progress tracking for UI updates
        # Transaction management
```

**Database Schema (Replacement Rules):**
```sql
CREATE TABLE replacements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    find_text TEXT NOT NULL UNIQUE,
    replace_text TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    notes TEXT DEFAULT '',
    usage_count INTEGER DEFAULT 0,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_replacements_find_text ON replacements(find_text);
CREATE INDEX idx_replacements_enabled ON replacements(enabled);
CREATE INDEX idx_replacements_modified ON replacements(modified);
```

### 3.2 Translation History Panel (Days 11-12)

**Goal:** Translation history database with advanced pagination, search, and fast import capabilities using existing pagination framework.

**Database Details:**
- **Separate Database File**: `translation_history.db`
- **Complex Schema**: Two-table design with versioning support
- **Advanced Features**: Version management, source attribution, fast bulk import
- **Performance**: Optimized for large datasets (100,000+ entries)
- **Pagination Integration**: Uses existing `DatabasePaginationController` with advanced filtering

**Features from Old System:**
- View translation history records with full version history
- Advanced search by source text, translation, timestamp, context
- Paged display with 22 items per page (configurable via existing pagination settings)
- Export history to plist and PO files
- Import from multiple sources (PO files, TMX, plist)
- Fast bulk import with progress tracking (1,000+ entries/second)
- Statistics and analytics dashboard
- Source attribution and conflict resolution

**Key Components:**
```python
# panels/preferences/translation_history_panel.py  
class TranslationHistoryPanel(QWidget):
    """Translation history management panel using existing pagination framework"""
    
    def __init__(self):
        # History table with existing advanced pagination
        # Search and filter controls
        # Statistics display
        # Import/Export functionality
        # Fast import capabilities
        
    def setup_ui(self):
        # Main layout with search controls at top
        # Statistics panel (total entries, sources, versions)
        # Table with existing PaginationWidget at bottom
        # Import/Export toolbar with progress indicators
        
    def setup_search_controls(self):
        # Search by text, date range, project, source
        # Advanced filtering options (context, version, etc.)
        # Search result navigation with existing pagination
        # Real-time search with debouncing
        
    def setup_pagination(self):
        # Use existing DatabasePaginationController for complex queries
        # Advanced filtering support through pagination data provider
        # Load page size from PreferencesPagingSettingsManager (default: 22)
        self.pagination_controller = PreferencesPaginationFactory.create_database_pagination(
            self.table_widget, self.history_database_service, "history_table")
        # Enhanced pagination widget with filter support
        self.pagination_widget = DatabasePaginationWidget(
            self.pagination_controller, 
            show_filters=True, show_sort=True)
        
    def setup_import_export(self):
        # Fast import from PO files using fast_import_po algorithm
        # Import from plist files (translation memory)
        # Import from TMX files (translation memory exchange)
        # Export to PO files with filtering options
        # Export to plist for backup/exchange
        # Progress tracking and cancellation support
        
    def fast_import_po_files(self, file_paths: List[str]):
        # High-performance import using bulk operations
        # Progress dialog with detailed statistics
        # Error handling and rollback capabilities
        # Source attribution for imported data
        
    def bulk_import_with_progress(self, source_data: List[Dict], source: str):
        # Bulk import with real-time progress updates
        # Conflict resolution for duplicate entries
        # Version management for existing translations
        
# services/translation_history_service.py
class TranslationHistoryService(QObject):
    """Service for translation history operations with pagination data provider interface"""
    
    def __init__(self, db_path: str = "translation_history.db"):
        # Initialize complex translation database
        # Setup performance optimizations  
        # Configure connection pooling
        # Implements PaginationDataProvider for complex filtering
    
    def search_history(self, 
                      search_text: str = "",
                      context: str = None,
                      date_from: QDate = None,
                      date_to: QDate = None,
                      source_filter: str = None,
                      page: int = 0,
                      page_size: int = 22) -> Tuple[List, int]:
        # Advanced paginated search with multiple criteria
        # Compatible with existing DatabasePaginationController
        # Full-text search in translations
        # Context-aware filtering
        # Date range queries with optimization
        
    def fast_import_po(self, file_path: str, dict_type: str = "project") -> ImportResult:
        """Fast bulk import algorithm from old system"""
        # 1. Bulk insert source texts (INSERT OR IGNORE for deduplication)
        # 2. Create msgid->unique_id mapping in memory
        # 3. Batch insert translations with version management
        # 4. Source attribution for tracking import origin
        # Performance: 1,000+ entries/second for batch imports
        
    def get_translation_statistics(self) -> Dict:
        # Total entries, versions, sources
        # Import history and statistics
        # Most active translation pairs
        # Performance metrics
        
    def get_version_history(self, unique_id: int) -> List[Dict]:
        # Get all versions of a specific translation
        # Include source attribution and timestamps
        # Support for version comparison
        
    def export_filtered_data(self, filter_criteria: Dict, 
                           export_format: str = "po") -> str:
        # Export with complex filtering
        # Support multiple formats (PO, plist, TMX)
        # Include metadata and source attribution

# models/translation_history_model.py
class TranslationHistoryTableModel(QAbstractTableModel):
    """Model for translation history table with advanced pagination support"""
    
    # Columns: ID, Source Text, Translation, Context, Version, Source, Timestamp
    # Supports complex sorting and filtering
    # Version grouping and expansion
    # Real-time search integration
    # Lazy loading for performance
    # Implements TableDataProvider interface from unified pagination
    
# widgets/preferences/database_pagination_widget.py  
class DatabasePaginationWidget(PaginationWidget):
    """Enhanced pagination widget with database-specific features for preferences"""
    
    def __init__(self, controller, show_filters=True, show_sort=True, **kwargs):
        # Extends existing PaginationWidget from unified pagination
        # Adds database-specific filter and sort controls
        # Integrated search functionality
        
    def _add_filter_controls(self):
        # Filter combo with options like "Has Issues", "Fuzzy Only", "Empty Translation"
        # Date range selectors
        # Source filter options
        
    def _add_sort_controls(self):
        # Sort by column selection
        # Ascending/descending toggle
        # Multiple sort criteria support
```

**Database Schema (Translation History):**
```sql
-- Source texts table
CREATE TABLE english_text (
    unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
    msgid TEXT NOT NULL,
    context TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT,
    import_batch TEXT
);

-- Translation versions table  
CREATE TABLE tran_text (
    unique_id INTEGER NOT NULL,
    version_id INTEGER NOT NULL,
    tran_text TEXT NOT NULL,
    source TEXT DEFAULT 'manual',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT,
    import_batch TEXT,
    confidence_score REAL DEFAULT 1.0,
    PRIMARY KEY (unique_id, version_id),
    FOREIGN KEY (unique_id) REFERENCES english_text(unique_id) ON DELETE CASCADE
);

-- Performance indexes
CREATE INDEX idx_english_msgid ON english_text(msgid);
CREATE INDEX idx_english_context ON english_text(context);
CREATE INDEX idx_english_created ON english_text(created);
CREATE INDEX idx_tran_text_content ON tran_text(tran_text);
CREATE INDEX idx_tran_text_source ON tran_text(source);
CREATE INDEX idx_tran_text_timestamp ON tran_text(timestamp);
CREATE INDEX idx_tran_text_batch ON tran_text(import_batch);

-- Full-text search support
CREATE VIRTUAL TABLE msgid_fts USING fts5(msgid, content='english_text', content_rowid='unique_id');
CREATE VIRTUAL TABLE translation_fts USING fts5(tran_text, content='tran_text', content_rowid='unique_id');
```

**Fast Import Algorithm Details:**
```python
def fast_import_po(self, file_path: str, dict_type: str = "project") -> ImportResult:
    """Implementation of fast import from old system"""
    
    import_batch = f"{dict_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    with self.db.transaction():
        # Step 1: Bulk insert source texts with deduplication
        source_data = []
        for entry in po_file:
            source_data.append((entry.msgid, entry.msgctxt, import_batch))
        
        self.cursor.executemany(
            "INSERT OR IGNORE INTO english_text (msgid, context, import_batch) VALUES (?, ?, ?)",
            source_data
        )
        
        # Step 2: Create msgid->unique_id mapping
        msgid_mapping = {}
        for msgid, context in msgid_context_pairs:
            unique_id = self.cursor.execute(
                "SELECT unique_id FROM english_text WHERE msgid = ? AND context = ?",
                (msgid, context)
            ).fetchone()[0]
            msgid_mapping[(msgid, context)] = unique_id
        
        # Step 3: Batch insert translations
        translation_data = []
        for entry in po_file:
            if entry.msgstr:  # Only import non-empty translations
                unique_id = msgid_mapping[(entry.msgid, entry.msgctxt)]
                version_id = self.get_next_version_id(unique_id)
                translation_data.append((unique_id, version_id, entry.msgstr, dict_type, import_batch))
        
        self.cursor.executemany(
            "INSERT INTO tran_text (unique_id, version_id, tran_text, source, import_batch) VALUES (?, ?, ?, ?, ?)",
            translation_data
        )
        
    return ImportResult(
        imported_count=len(translation_data),
        duplicate_count=len(source_data) - len(translation_data),
        import_batch=import_batch,
        performance_stats={"entries_per_second": len(translation_data) / elapsed_time}
    )
```

### 3.3 Font Settings Panel (Days 13)

**Goal:** Comprehensive font configuration using shared font components.

**Features:**
- Font selectors for all 6 component types
- Live preview for each font type
- Target language selection  
- Apply fonts button with immediate effect
- Font settings persistence

**Implementation:**
```python
# panels/preferences/font_settings_panel.py
class FontSettingsPanel(QWidget):
    """Font configuration panel using shared components"""
    
    def __init__(self):
        # Use FontSelectorWidget for each component
        # Use FontPreviewWidget for previews
        # Target language selector
        # Apply button
        
    def create_font_section(self, component_config):
        # Creates font selector + preview for component
        # Uses shared FontSelectorWidget
        # Connects to FontApplicationService
```

### 3.4 Editor Settings Panel (Days 14)

**Goal:** Editor configuration including table pagination settings that control the existing unified pagination system.

**Features from Old System:**
- Main table page size (5-500, default: 50) - Controls existing TablePagerBase implementations
- Main table scroller pages (5-100, default: 15) - Controls scrollbar navigation behavior  
- History table page size (5-500, default: 22) - Controls translation history pagination
- History table scroller pages (5-100, default: 15) - Controls history scrollbar behavior
- Font family and size settings

**Pagination Settings Integration:**
The Editor Settings Panel serves as the **central configuration point** for all pagination behavior throughout the application, including:

- **Main PO Editor Table**: Controls page size for primary translation table using existing `TablePagerBase`
- **Translation History Panel**: Controls page size for the new translation history database pagination  
- **Replacement Rules Panel**: Controls page size for replacement rules database pagination
- **Search Results**: Controls pagination for search result displays
- **Explorer Panels**: Controls file system pagination settings

**Implementation:**
```python
# panels/preferences/editor_settings_panel.py
class EditorSettingsPanel(QWidget):
    """Editor configuration panel - Central pagination settings control"""
    
    def __init__(self):
        # Navigation settings section (primary focus)
        # Font settings section
        # Preview/apply functionality
        
    def setup_navigation_settings(self):
        # Main table page size/scroller pages (affects existing TablePagerBase)
        # History table page size/scroller pages (affects new translation history)
        # Replacement table page size (affects new replacement panel)
        # Search results page size (affects existing search pagination)
        # Connect to PreferencesPagingSettingsManager
        
        # Real-time application of changes
        self.main_page_size_spinbox.valueChanged.connect(self._apply_main_pagination_settings)
        self.history_page_size_spinbox.valueChanged.connect(self._apply_history_pagination_settings)
        
    def _apply_main_pagination_settings(self):
        """Apply main table pagination settings to all existing TablePagerBase instances"""
        # Update settings in QSettings
        # Emit signals to update active table pagination controllers
        # Refresh existing main editor tables
        
    def _apply_history_pagination_settings(self):
        """Apply history table pagination settings to translation history panels"""
        # Update settings for translation history database pagination
        # Refresh active history panels
        
    def setup_font_settings(self):
        # Use shared FontSelectorWidget for each component
        # Existing font management system integration
        
# Integration with Existing Pagination Framework
class PaginationSettingsManager(QObject):
    """Extended settings manager that bridges editor settings with existing pagination"""
    
    # Signals emitted when pagination settings change
    mainTablePageSizeChanged = Signal(int)
    historyTablePageSizeChanged = Signal(int)
    replacementTablePageSizeChanged = Signal(int)
    scrollerPagesChanged = Signal(str, int)  # component_name, pages
    
    def apply_main_table_settings(self, page_size: int, scroller_pages: int):
        """Apply settings to all existing TablePagerBase instances throughout application"""
        # Find and update all active main table pagers
        # Update POFileTableModel pagination settings
        # Refresh table displays
        
    def apply_history_table_settings(self, page_size: int, scroller_pages: int):
        """Apply settings to translation history database pagination"""
        # Update translation history pagination controllers
        # Refresh history panel displays
```

**Settings Schema:**
```python
PAGINATION_SETTINGS = {
    "main_table_page_size": {"min": 5, "max": 500, "default": 50},
    "main_table_scroller_pages": {"min": 5, "max": 100, "default": 15},
    "history_table_page_size": {"min": 5, "max": 500, "default": 22},
    "history_table_scroller_pages": {"min": 5, "max": 100, "default": 15},
    "replacement_table_page_size": {"min": 5, "max": 500, "default": 22},
    "search_results_page_size": {"min": 5, "max": 250, "default": 20},
}
```

## 4. Phase 3: Extended Panels (Days 15-21)

### 4.1 Keyboard Panel (Days 15-16)

**Features:**
- Keyboard shortcut configuration table
- Conflict detection and resolution
- Restore defaults functionality
- Search and filter shortcuts

### 4.2 Appearance Panel (Days 17-18)

**Features:**
- Theme selection (Dark/Light/Colorful)
- Color customization
- UI scaling options
- Preview changes

### 4.3 Translation Validation Panel (Days 19-20)

**Features from Old System:**
- Translation issue detection settings
- Enable/disable specific validation rules:
  - Fuzzy entries
  - Empty translations
  - Untranslated entries
  - Obsolete entries
  - Missing fields
  - Unresolved placeholders
  - Warnings
  - Plural forms issues
  - Formatting issues
  - Custom rules

### 4.4 Advanced Panel (Days 21)

**Features:**
- Network settings
- Cache management
- Debug options
- Performance tuning

## 5. Integration with Current Architecture

### 5.1 Sidebar Integration

```python
# panels/preferences_panel.py
class PreferencesPanel(QWidget):
    """Main preferences panel for sidebar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("preferences_panel")
        
        # Tab widget containing all preference panels
        self.tab_widget = QTabWidget()
        
        # Add all panels
        self.setup_panels()
        
    def setup_panels(self):
        # Phase 2 panels (core functionality)
        self.replacement_panel = ReplacementPanel()
        self.history_panel = TranslationHistoryPanel()
        self.font_panel = FontSettingsPanel()
        self.editor_panel = EditorSettingsPanel()
        
        # Add tabs
        self.tab_widget.addTab(self.replacement_panel, "Replacements")
        self.tab_widget.addTab(self.history_panel, "Translation History")
        self.tab_widget.addTab(self.font_panel, "Fonts & Languages")
        self.tab_widget.addTab(self.editor_panel, "Editor")
        
        # Phase 3 panels (extended functionality)
        # Add when implemented
```

### 5.2 Activity Bar Integration

```python
# models/core_activities.py
# Add preferences activity
PREFERENCES_ACTIVITY = ActivityModel(
    id="preferences",
    name="Preferences", 
    icon_active="preferences_active.svg",
    icon_inactive="preferences_inactive.svg",
    panel_class="panels.preferences_panel.PreferencesPanel",
    description="Application preferences and settings"
)
```

### 5.3 Existing Pagination Framework Integration

**Unified Pagination Framework** (`/project_files/20240731_pagination/`) provides:

1. **PaginationController** - Base controller that preferences panels will extend
2. **DatabasePaginationController** - Specialized for database operations (replacement & history)
3. **PaginationWidget** - Standard UI components with navigation, page size selection, go-to-page
4. **CompactPaginationControls** - Minimal space pagination for constrained layouts
5. **TablePagerBase** - Existing abstraction used throughout application

**Integration Strategy:**
- **Replacement Panel**: Uses `DatabasePaginationController` with `ReplacementDatabaseService`
- **Translation History Panel**: Uses `DatabasePaginationController` with advanced filtering
- **Editor Settings Panel**: Controls pagination settings for entire application
- **Existing Tables**: Continue using `TablePagerBase` but controlled by Editor Settings

### 5.4 Theme Integration

The preferences panel will use existing theme system with specific styling:

```css
/* Preferences panel specific styles */
QWidget#preferences_panel {
    background-color: var(--panel-bg);
    color: var(--fg-main);
}

/* Tab widget styling */
QTabWidget#preferences_tabs {
    background-color: var(--panel-bg);
}

/* Existing pagination widget styling integration */
QWidget.pagination_widget {
    background-color: var(--btn-bg);
    border: 1px solid var(--panel-border);
    border-radius: 4px;
    padding: 4px;
}

/* Database pagination widget styling */
QWidget.database_pagination_widget {
    background-color: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 6px;
    padding: 6px;
}

/* Font preview styling */
QLabel.font_preview {
    background-color: var(--editor-bg);
    border: 1px solid var(--panel-border);
    border-radius: 2px;
    padding: 8px;
    color: var(--fg-main);
}
```

## 6. Testing Strategy

### 6.1 Phase 1 Testing (Shared Components)

**Pagination Testing:**
- Test with different page sizes (10, 22, 50, 100, 250)
- Test navigation (First/Prev/Next/Last)
- Test goto page functionality
- Performance testing with large datasets (1000+ records)
- Settings persistence testing

**Font Management Testing:**
- Test font selection and preview
- Test font application to different components
- Test settings save/load
- Test with different system fonts
- Test preview updates

**Database Operations Testing:**
- Test plist import/export functionality
- Test database pagination queries
- Test transaction handling
- Test error scenarios and recovery

### 6.2 Phase 2 Testing (Core Panels)

**Replacement Panel Testing:**
- Test CRUD operations for replacement rules
- Test import/export with real plist files  
- Test search and filtering
- Test pagination with replacement data
- Test preview functionality

**Translation History Testing:**
- Test history data display and pagination
- Test search functionality across large datasets
- Test date range filtering
- Test export functionality
- Test performance with 10,000+ history records

### 6.3 Integration Testing

**Sidebar Integration:**
- Test panel switching and state preservation
- Test theme application to preferences panels
- Test responsive layout with different sidebar widths
- Test activity bar integration

**Settings Persistence:**
- Test settings save/load across application restarts
- Test migration from old settings format
- Test settings validation and error handling

## 7. Performance Considerations

### 7.1 Database Optimization

- Use indexed queries for pagination
- Implement query result caching
- Lazy loading for large datasets
- Connection pooling for database operations

### 7.2 UI Responsiveness  

- Use worker threads for database operations
- Implement progress indicators for long operations
- Debounce search input to avoid excessive queries
- Optimize table rendering for large page sizes

### 7.3 Memory Management

- Implement proper cleanup for pagination controllers
- Cache management for font previews
- Efficient model updates for table widgets
- Resource cleanup on panel switching

## 8. Migration from Old System

### 8.1 Settings Migration

```python
# services/settings_migration_service.py
class SettingsMigrationService(QObject):
    """Migrate settings from old preferences system"""
    
    def migrate_old_settings(self):
        # Migrate font settings
        # Migrate pagination settings
        # Migrate keyboard shortcuts
        # Migrate replacement rules
        # Migrate translation history
```

### 8.2 Data Migration

- Migrate existing replacement rules database
- Migrate translation history database
- Convert old plist formats if needed
- Backup old settings before migration

## 9. Implementation Timeline

**Phase 1 (Days 1-7): Integration with Existing Pagination System**
- Day 1-3: Integrate with Existing Unified Pagination Framework  
- Day 4-5: Font Management System  
- Day 6-7: Database Operations Service

**Phase 2 (Days 8-14): Core Panels with Existing Pagination**
- Day 8-10: Replacement Panel (using DatabasePaginationController)
- Day 11-12: Translation History Panel (using DatabasePaginationController)
- Day 13: Font Settings Panel
- Day 14: Editor Settings Panel (Central Pagination Control)

**Phase 3 (Days 15-21): Extended Panels**
- Day 15-16: Keyboard Panel
- Day 17-18: Appearance Panel
- Day 19-20: Translation Validation Panel
- Day 21: Advanced Panel

**Integration & Testing (Days 22-25)**
- Day 22-23: Sidebar and activity bar integration
- Day 24: Comprehensive testing with existing pagination system
- Day 25: Documentation and refinement

## 10. Success Criteria

### 10.1 Functional Requirements

✅ **Existing Pagination Integration:** All database tables use the existing unified pagination framework
✅ **Database Operations:** Import/export to/from plist files works correctly with fast import capabilities
✅ **Font Management:** All 6 font types (msgid, msgstr, table, comment, suggestion, control) configurable
✅ **Settings Persistence:** All settings save/load correctly with QSettings
✅ **Search & Filter:** Advanced search works in replacement and history panels with existing pagination
✅ **Performance:** Pagination handles 10,000+ records smoothly using existing framework
✅ **Central Control:** Editor Settings Panel controls pagination behavior throughout application

### 10.2 Technical Requirements

✅ **Architecture:** Clean integration with existing unified pagination framework
✅ **Theme Integration:** Preferences panel respects current theme settings
✅ **Responsive UI:** Panels work correctly at different sidebar widths
✅ **Error Handling:** Graceful handling of database and file operation errors
✅ **Testing Coverage:** Comprehensive test coverage for all components
✅ **Pagination Consistency:** All paged components use same underlying framework

### 10.3 User Experience Requirements

✅ **Consistency:** All paged tables use the existing unified pagination framework
✅ **Responsiveness:** UI remains responsive during long operations
✅ **Intuitive Navigation:** Clear and consistent navigation patterns using existing pagination UI
✅ **Immediate Feedback:** Font and theme changes apply immediately
✅ **Data Safety:** Import/export operations include validation and backup
✅ **Familiar Interface:** Users familiar with existing pagination will find consistent behavior

This comprehensive plan ensures that the Preferences sidebar panel will be a robust, well-integrated component that leverages the existing unified pagination system for optimal maintainability and user experience. By building upon the established pagination framework documented in `/project_files/20240731_pagination/`, we ensure consistency across the entire application while providing powerful new functionality for preferences management.
