# Preferences System: Translation History

## Overview
The Translation History module provides robust storage, search, and management of translation entries across projects. This design document outlines the architecture and components for storing, retrieving, and manipulating translation history in the preferences system.

## Architecture

### Core Components

1. **TranslationHistoryManager**: Central coordinator that manages access to translation history
2. **DatabaseService**: Low-level database access layer using SQLite
3. **SearchEngine**: Fast indexing and search capability for translation entries
4. **VersioningSystem**: Tracks multiple versions of translations for each entry
5. **TranslationHistoryPage**: Preferences UI for managing translation history

## Data Model

### Translation Entry
The core data model representing a translation unit:

```python
class TranslationEntry:
    """A complete translation entry with history tracking."""
    
    def __init__(self,
                 source_text: str,
                 context: Optional[str] = None,
                 id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.source_text = source_text
        self.context = context
        self.created_at = datetime.now()
        self.last_accessed = self.created_at
        self.versions = []  # List of TranslationVersion objects
        self.metadata = {}  # Additional metadata dict
        
    def add_version(self, translation: str, 
                    source: str = "manual", 
                    fuzzy: bool = False) -> TranslationVersion:
        """Add a new translation version."""
        # Creates and returns a new version
        
    def latest_version(self) -> Optional[TranslationVersion]:
        """Get the most recent version."""
        
    def version_by_id(self, version_id: str) -> Optional[TranslationVersion]:
        """Get a specific version by ID."""
```

### Translation Version
Represents a specific translated text variant for an entry:

```python
class TranslationVersion:
    """A specific version of a translation."""
    
    def __init__(self,
                 translation: str,
                 source: str = "manual",
                 fuzzy: bool = False,
                 id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.translation = translation
        self.source = source
        self.fuzzy = fuzzy
        self.created_at = datetime.now()
        self.metadata = {}  # Additional version-specific metadata
```

## Storage System

### Database Schema
The translation history uses SQLite for persistent storage with the following tables:

1. **entries**: Stores core translation entries
   - id (TEXT): Primary key
   - source_text (TEXT): Original text to be translated
   - context (TEXT): Optional context information
   - created_at (TIMESTAMP): When entry was first created
   - last_accessed (TIMESTAMP): When entry was last accessed/used

2. **versions**: Stores translation versions
   - id (TEXT): Primary key
   - entry_id (TEXT): Foreign key to entries table
   - translation (TEXT): The translated text
   - source (TEXT): Source of the translation (manual, machine, etc.)
   - fuzzy (BOOLEAN): Whether translation needs review
   - created_at (TIMESTAMP): When version was created
   
3. **metadata**: Stores additional metadata for entries and versions
   - target_id (TEXT): ID of entry or version
   - key (TEXT): Metadata key
   - value (TEXT): Metadata value

### Database Service
Provides clean interface for database operations:

```python
class TranslationDatabaseService:
    """Handles all database operations for translation history."""
    
    def __init__(self, db_path: str):
        self._connection = self._init_database(db_path)
        
    def _init_database(self, path: str) -> sqlite3.Connection:
        # Initialize database, create tables if needed
        
    def get_entry(self, id: str) -> Optional[TranslationEntry]:
        """Get an entry by ID with all versions."""
        
    def get_entry_by_text(self, text: str, context: Optional[str] = None) -> Optional[TranslationEntry]:
        """Find entry by source text and optional context."""
        
    def add_entry(self, entry: TranslationEntry) -> bool:
        """Add a new translation entry."""
        
    def update_entry(self, entry: TranslationEntry) -> bool:
        """Update an existing entry."""
        
    def add_version(self, entry_id: str, version: TranslationVersion) -> bool:
        """Add a version to an existing entry."""
        
    def delete_version(self, version_id: str) -> bool:
        """Delete a specific version."""
        
    def search_entries(self, query: str, search_translations: bool = True) -> list[TranslationEntry]:
        """Search for entries matching the query."""
        
    def get_entries_page(self, page: int, page_size: int, 
                         sort_field: str = "last_accessed",
                         sort_dir: str = "DESC") -> tuple[list[TranslationEntry], int]:
        """Get a paginated list of entries with total count."""
```

## Pagination and Search

### Paged Results Manager
Handles efficient navigation of large result sets:

```python
class TranslationHistoryPager:
    """Manages pagination of translation history entries."""
    
    def __init__(self, database: TranslationDatabaseService, page_size: int = 50):
        self._database = database
        self._page_size = page_size
        self._current_page = 1
        self._total_entries = 0
        self._current_entries = []
        self._sort_field = "last_accessed"
        self._sort_direction = "DESC"
        
    def load_page(self, page: int) -> list[TranslationEntry]:
        """Load a specific page of results."""
        
    def next_page(self) -> list[TranslationEntry]:
        """Go to next page if available."""
        
    def previous_page(self) -> list[TranslationEntry]:
        """Go to previous page if available."""
        
    def set_sort(self, field: str, direction: str = "ASC") -> None:
        """Set sorting parameters and reset pagination."""
        
    def refresh(self) -> None:
        """Refresh the current page data."""
        
    @property
    def total_pages(self) -> int:
        """Calculate total pages based on entry count."""
        
    @property
    def has_next(self) -> bool:
        """Check if next page is available."""
        
    @property
    def has_previous(self) -> bool:
        """Check if previous page is available."""
```

### Search Results Navigator
Specialized navigation for search results:

```python
class SearchResultsNavigator:
    """Navigates through search results with highlighting."""
    
    def __init__(self, search_results: list[TranslationEntry], page_size: int = 50):
        self._results = search_results
        self._page_size = page_size
        self._current_index = 0
        self._total_results = len(search_results)
        
    def current_item(self) -> Optional[TranslationEntry]:
        """Get the current search result."""
        
    def next_item(self) -> Optional[TranslationEntry]:
        """Move to and get the next result."""
        
    def previous_item(self) -> Optional[TranslationEntry]:
        """Move to and get the previous result."""
        
    def current_page_items(self) -> list[TranslationEntry]:
        """Get all items for the current page."""
        
    @property
    def has_next(self) -> bool:
        """Check if more results are available."""
        
    @property
    def has_previous(self) -> bool:
        """Check if previous results are available."""
```

## User Interface

### Translation History Preferences Page

```python
class TranslationHistoryPage(PreferencePage):
    """Preferences page for translation history management."""
    
    def __init__(self, parent=None):
        super().__init__("Translation History", QIcon(":/icons/history.svg"), parent)
        self._setup_ui()
        
    def _setup_ui(self):
        # Create search controls, history table, pagination, and editor
        
    def _connect_signals(self):
        # Connect search, navigation, and editing signals
        
    def _on_search_requested(self, query: str):
        # Handle search request and show results
        
    def _on_entry_selected(self, entry_id: str):
        # Load and display the selected entry
        
    def _on_version_selected(self, version_id: str):
        # Show the selected version in the editor
        
    def _on_save_changes(self):
        # Save changes to the current entry/version
        
    def apply_changes(self) -> bool:
        """Apply any pending changes."""
        # Commit any unsaved changes
        
    def reset_to_defaults(self) -> None:
        """Reset state, discard changes."""
```

### Translation Editor Component

```python
class VersionedTranslationEditor(QWidget):
    """Editor for managing translation entries and versions."""
    
    text_saved = Signal(str, str)  # version_id, text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_entry = None
        self._current_version = None
        self._setup_ui()
        
    def _setup_ui(self):
        # Create source and translation editors, version selector
        
    def set_entry(self, entry: TranslationEntry):
        """Set the current entry for editing."""
        
    def select_version(self, version_id: str) -> bool:
        """Select a specific version for editing."""
        
    def add_new_version(self) -> None:
        """Create a new version based on current text."""
        
    def save_current_version(self) -> bool:
        """Save changes to the current version."""
        
    def highlight_text(self, text: str) -> None:
        """Highlight search terms in the editors."""
```

### Navigation Component

```python
class TranslationHistoryNavigator(QWidget):
    """Navigation component for browsing history entries."""
    
    page_changed = Signal(int)  # Current page
    entry_selected = Signal(str)  # Entry ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pager = None
        self._setup_ui()
        
    def _setup_ui(self):
        # Create pagination controls and entry list
        
    def set_pager(self, pager: TranslationHistoryPager):
        """Connect to a pager instance."""
        
    def update_page_data(self, entries: list[TranslationEntry]):
        """Update the displayed entries."""
        
    def _on_next_page(self):
        # Handle next page navigation
        
    def _on_previous_page(self):
        # Handle previous page navigation
        
    def _on_entry_clicked(self, index):
        # Handle entry selection
```

## Integration with Core System

### TranslationHistoryManager Service

```python
class TranslationHistoryManager:
    """Central service for managing translation history."""
    
    entry_added = Signal(str)  # Entry ID
    entry_updated = Signal(str)  # Entry ID
    
    def __init__(self):
        self._db_service = TranslationDatabaseService(self._get_db_path())
        self._init_services()
        
    def _init_services(self):
        # Initialize related services
        
    def _get_db_path(self) -> str:
        # Get database path from settings
        
    def get_entry(self, id: str) -> Optional[TranslationEntry]:
        """Get an entry by ID."""
        
    def find_entry(self, source: str, context: Optional[str] = None) -> Optional[TranslationEntry]:
        """Find an entry by source and context."""
        
    def add_or_update_entry(self, source: str, translation: str, 
                           context: Optional[str] = None,
                           fuzzy: bool = False) -> TranslationEntry:
        """Add a new entry or update an existing one."""
        
    def search(self, query: str, options: dict = None) -> list[TranslationEntry]:
        """Search entries with options."""
        
    def create_pager(self, page_size: int = 50) -> TranslationHistoryPager:
        """Create a pager for browsing entries."""
```

### Integration with Editor

The translation history system integrates with the editor through:

1. **Automatic Capture**: When translations are saved in the editor, they are stored in history
2. **Suggestion Provider**: The history provides suggestions based on similar source texts
3. **Context Menu**: Editors can show history for the current text via context menu
4. **History Button**: Direct access to the translation history dialog

## Import/Export System

### Data Format
Translation history uses a JSON-based format for import/export:

```json
{
  "format_version": "1.0",
  "exported_at": "2024-12-21T15:45:00Z",
  "entries": [
    {
      "id": "uuid-1",
      "source_text": "Hello world",
      "context": "greeting",
      "created_at": "2024-12-01T10:00:00Z",
      "versions": [
        {
          "id": "vuuid-1",
          "translation": "Bonjour le monde",
          "source": "manual",
          "fuzzy": false,
          "created_at": "2024-12-01T10:01:00Z"
        }
      ]
    }
  ]
}
```

### Import/Export Methods

```python
class TranslationHistoryImportExport:
    """Handles import and export of translation history."""
    
    def __init__(self, db_service: TranslationDatabaseService):
        self._db_service = db_service
        
    def export_to_file(self, filepath: str, entries: list[str] = None) -> bool:
        """Export entries to a file."""
        # Export all entries or specified IDs
        
    def import_from_file(self, filepath: str, merge_strategy: str = "skip_existing") -> tuple[int, list[str]]:
        """Import entries from a file."""
        # Return count of imported entries and errors
        
    def import_from_po_file(self, filepath: str, merge_strategy: str = "skip_existing") -> tuple[int, list[str]]:
        """Import entries from a PO file."""
        # Parse PO file and import entries
```

## Implementation Plan

1. **Phase 1: Core Database**
   - Implement database schema and service
   - Basic CRUD operations for entries and versions
   - Unit tests for database operations

2. **Phase 2: Search and Navigation**
   - Implement search engine with indexing
   - Build pagination components
   - Search results navigation

3. **Phase 3: User Interface**
   - Translation history preferences page
   - Version editor component
   - Navigation and search UI

4. **Phase 4: Integration**
   - Editor integration
   - Import/Export functionality
   - Settings and configuration

## Performance Considerations

1. **Indexing**: Implement FTS (Full-Text Search) for search performance
2. **Caching**: Cache frequently accessed entries
3. **Pagination**: Always use pagination for large result sets
4. **Background Loading**: Load history in background threads when possible
5. **Batch Operations**: Use batch operations for imports

## Migration Strategy

For existing users, we'll provide:

1. **Import from Legacy Format**: Convert old history database
2. **Incremental Migration**: Migrate in background when app is idle
3. **Manual Import Option**: Allow users to manually import old history

## Future Enhancements

1. **Cloud Sync**: Synchronize translation history across devices
2. **Team Sharing**: Allow sharing selected entries with team members
3. **Statistical Analysis**: Analyze translation patterns and trends
4. **AI Integration**: Use history data to train custom machine translation models
5. **Context-Aware Suggestions**: Provide suggestions based on project context
