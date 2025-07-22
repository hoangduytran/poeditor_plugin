# POEditor Plugin Design

## Overview
The POEditor plugin provides specialized editing capabilities for GNU gettext PO (Portable Object) files. It offers a comprehensive translation interface with support for plurals, context, comments, and translation validation, integrated seamlessly with the POEditor application's tab system.

## Architecture

### Core Components

#### 1. POEditorPlugin (plugin.py)
**Purpose:** Main plugin entry point and tab registration

**Key Features:**
- Plugin registration with tab system
- PO file type association
- Command registration for PO operations
- Integration with translation services

**Interface:**
```python
def register(api: PluginAPI) -> None
def unregister(api: PluginAPI) -> None
def create_tab(file_path: str) -> POEditorTab
```

#### 2. POEditorTab (po_editor_tab.py)
**Purpose:** Main tab widget for PO file editing

**Key Features:**
- Split view with entry list and editor
- Translation progress tracking
- Real-time validation and statistics
- Undo/redo support
- Auto-save functionality

**Interface:**
```python
class POEditorTab(QWidget):
    translation_changed = Signal(POEntry, str)
    entry_selected = Signal(POEntry)
    file_modified = Signal(bool)
    
    def __init__(self, file_path: str, api: PluginAPI)
    def load_po_file(self, file_path: str) -> None
    def save_file(self) -> bool
    def get_current_entry(self) -> POEntry
    def navigate_to_entry(self, entry_id: str) -> None
    def set_filter(self, filter_type: EntryFilter) -> None
```

#### 3. POFileManager (models/po_file_manager.py)
**Purpose:** PO file loading, parsing, and management

**Key Features:**
- PO file parsing with polib
- Metadata management
- Entry indexing and searching
- File format validation
- Backup and recovery

**Interface:**
```python
class POFileManager(QObject):
    file_loaded = Signal(POFile)
    entry_updated = Signal(POEntry)
    file_saved = Signal(str)
    
    def __init__(self)
    def load_file(self, file_path: str) -> POFile
    def save_file(self, po_file: POFile, file_path: str) -> bool
    def validate_file(self, po_file: POFile) -> ValidationResult
    def get_statistics(self, po_file: POFile) -> POStatistics
```

#### 4. EntryListWidget (widgets/entry_list.py)
**Purpose:** List view of PO entries with filtering and navigation

**Key Features:**
- Paginated entry display
- Multi-level filtering (status, context, source)
- Search within entries
- Sort by various criteria
- Entry status indicators

**Interface:**
```python
class EntryListWidget(QListWidget):
    entry_selected = Signal(POEntry)
    filter_changed = Signal(EntryFilter)
    
    def __init__(self, po_file: POFile)
    def set_entries(self, entries: List[POEntry]) -> None
    def apply_filter(self, filter_obj: EntryFilter) -> None
    def find_entry(self, search_text: str) -> POEntry
    def get_selected_entry(self) -> POEntry
```

#### 5. TranslationEditor (widgets/translation_editor.py)
**Purpose:** Rich text editor for translation content

**Key Features:**
- Source text display with highlighting
- Translation input with validation
- Plural form handling
- Context and comment display
- Fuzzy status management

**Interface:**
```python
class TranslationEditor(QWidget):
    translation_updated = Signal(str)
    fuzzy_changed = Signal(bool)
    
    def __init__(self)
    def set_entry(self, entry: POEntry) -> None
    def get_translation(self) -> str
    def set_fuzzy(self, is_fuzzy: bool) -> None
    def validate_translation(self) -> ValidationResult
    def show_plural_forms(self, forms: List[str]) -> None
```

#### 6. POToolbar (widgets/po_toolbar.py)
**Purpose:** PO-specific editing toolbar

**Key Features:**
- Navigation controls (previous, next, go to)
- Filter shortcuts (untranslated, fuzzy, translated)
- Translation tools (copy source, clear, validate)
- Save and export functions

**Interface:**
```python
class POToolbar(QToolBar):
    def __init__(self, api: PluginAPI)
    def set_entry_navigation(self, current: int, total: int) -> None
    def update_filter_buttons(self, active_filter: EntryFilter) -> None
    def set_save_state(self, has_changes: bool) -> None
```

#### 7. ValidationService (services/validation_service.py)
**Purpose:** Translation validation and quality checks

**Key Features:**
- Format string validation
- Consistency checking
- Completeness verification
- Custom validation rules
- Real-time feedback

**Interface:**
```python
class ValidationService:
    def validate_entry(self, entry: POEntry) -> List[ValidationIssue]
    def validate_format_strings(self, source: str, translation: str) -> bool
    def check_consistency(self, po_file: POFile) -> List[ConsistencyIssue]
    def validate_plurals(self, entry: POEntry) -> List[ValidationIssue]
```

### Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         POEditor Tab                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                          Toolbar                                        │
│  ┌─────┐ ┌─────┐ ┌─────────┐ │ ┌─────┐ ┌─────┐ ┌─────┐ │ ┌─────┐ ┌─────┐ │
│  │  ←  │ │  →  │ │ Go to.. │ │ │ All │ │ ❌  │ │ ✅  │ │ │ 💾  │ │ ⚙️  │ │
│  │Prev │ │Next │ │         │ │ │     │ │Fuzz │ │Done │ │ │Save │ │Opts │ │
│  └─────┘ └─────┘ └─────────┘ │ └─────┘ └─────┘ └─────┘ │ └─────┘ └─────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                      Main Content Area                                  │
│ ┌─────────────────────────────┬─────────────────────────────────────────┐ │
│ │        Entry List           │           Translation Editor            │ │
│ │                             │                                         │ │
│ │ 🔍 [Search entries...]      │ ┌─────────────────────────────────────┐ │ │
│ │                             │ │             Source Text             │ │ │
│ │ ┌─────────────────────────┐ │ │  "Hello {name}, welcome to our app" │ │ │
│ │ │ [42/156] Welcome message│✅│ │                                     │ │ │
│ │ │ Context: greeting       │ │ │ └─────────────────────────────────────┘ │ │
│ │ └─────────────────────────┘ │ │                                         │ │
│ │ ┌─────────────────────────┐ │ │ ┌─────────────────────────────────────┐ │ │
│ │ │ [43/156] Error message  │❌│ │ │           Translation               │ │ │
│ │ │ Context: error          │ │ │ │  "Hola {name}, bienvenido a..."     │ │ │
│ │ └─────────────────────────┘ │ │ │                                     │ │ │
│ │ ┌─────────────────────────┐ │ │ └─────────────────────────────────────┘ │ │
│ │ │ [44/156] Button label   │⚠️ │ │                                         │ │ │
│ │ │ Context: ui             │ │ │ ☑️ Fuzzy   📝 Comments   🔗 References  │ │ │
│ │ └─────────────────────────┘ │ │                                         │ │ │
│ │                             │ │ ┌─────────────────────────────────────┐ │ │
│ │ Filters: ● All ○ Todo ○ Done│ │ │            Comments                 │ │ │
│ │                             │ │ │ #. Greeting shown on app start      │ │ │
│ │                             │ │ │ #: src/main.py:42                   │ │ │
│ │                             │ │ └─────────────────────────────────────┘ │ │
│ └─────────────────────────────┴─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                         Status Bar                                      │
│ 📊 Progress: 98/156 (63%) │ ⚠️ 12 fuzzy │ ❌ 46 untranslated │ 🔄 Modified │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Models

#### POEntry Enhancement
```python
@dataclass
class POEntryMetadata:
    index: int
    is_translated: bool
    is_fuzzy: bool
    is_obsolete: bool
    has_plurals: bool
    validation_issues: List[ValidationIssue]
    last_modified: datetime
    translator: str
```

#### EntryFilter
```python
@dataclass
class EntryFilter:
    status: EntryStatus = EntryStatus.ALL
    search_text: str = ""
    search_scope: SearchScope = SearchScope.ALL
    has_context: bool = None
    has_comments: bool = None
    fuzzy_only: bool = False
    untranslated_only: bool = False
```

#### ValidationIssue
```python
@dataclass
class ValidationIssue:
    type: IssueType
    severity: IssueSeverity
    message: str
    suggestion: str = None
    line_number: int = None
    column: int = None
```

### Workflow Patterns

#### Translation Workflow
1. **File Loading:**
   - User opens PO file via Explorer or File menu
   - POFileManager parses file with polib
   - Entry list populated with metadata
   - Statistics calculated and displayed

2. **Navigation and Filtering:**
   - User applies filters to focus on specific entries
   - Search functionality to find specific content
   - Keyboard shortcuts for quick navigation
   - Bookmarking for important entries

3. **Translation Process:**
   - User selects entry from list
   - Source text displayed with context
   - Translation editor focused for input
   - Real-time validation feedback
   - Auto-save on entry change

4. **Quality Assurance:**
   - Validation runs on translation changes
   - Consistency checks across file
   - Format string verification
   - Completeness tracking

#### File Management
1. **Auto-save:** Changes saved automatically with configurable interval
2. **Backup:** Original file backed up before modifications
3. **Export:** Multiple format support (PO, POT, MO)
4. **Version Control:** Integration with git for change tracking

### Configuration

The POEditor plugin uses configuration in the `poeditor` namespace:

```python
DEFAULT_CONFIG = {
    "auto_save_interval": 30,  # seconds
    "backup_enabled": True,
    "backup_location": "backups/po/",
    "validation_enabled": True,
    "real_time_validation": True,
    "show_line_numbers": True,
    "wrap_text": True,
    "font_family": "Source Code Pro",
    "font_size": 11,
    "highlight_fuzzy": True,
    "highlight_untranslated": True,
    "entry_list_page_size": 100,
    "remember_filter_state": True,
    "auto_copy_source": False,
    "plurals_side_by_side": True,
    "show_statistics": True,
    "export_formats": ["po", "pot", "mo"],
    "translator_name": "",
    "translator_email": "",
    "validation_rules": {
        "check_format_strings": True,
        "check_trailing_spaces": True,
        "check_consistency": True,
        "check_accelerators": True
    }
}
```

### Commands

The POEditor plugin registers these commands:

- `poeditor.open_file`: Open PO file in POEditor tab
- `poeditor.save_file`: Save current PO file
- `poeditor.save_as`: Save PO file with new name
- `poeditor.export_mo`: Export to binary MO format
- `poeditor.next_entry`: Navigate to next entry
- `poeditor.previous_entry`: Navigate to previous entry
- `poeditor.next_untranslated`: Jump to next untranslated entry
- `poeditor.next_fuzzy`: Jump to next fuzzy entry
- `poeditor.copy_source`: Copy source text to translation
- `poeditor.clear_translation`: Clear current translation
- `poeditor.toggle_fuzzy`: Toggle fuzzy status
- `poeditor.validate_file`: Run full file validation
- `poeditor.show_statistics`: Display translation statistics
- `poeditor.filter_untranslated`: Filter to show only untranslated
- `poeditor.filter_fuzzy`: Filter to show only fuzzy entries
- `poeditor.filter_all`: Show all entries

### Events

**Emitted:**
- `poeditor.file_opened`: When PO file is opened
- `poeditor.entry_changed`: When translation is modified
- `poeditor.file_saved`: When PO file is saved
- `poeditor.validation_completed`: When validation finishes
- `poeditor.statistics_updated`: When stats change
- `poeditor.filter_applied`: When entry filter changes

**Listened:**
- `search.result_selected`: Navigate to search result in PO file
- `file.external_change`: Reload PO file if changed externally
- `config.changed`: Update editor settings

### Integration Points

#### With Search Plugin
- Global search across PO file content
- Find and replace in translations
- Context-aware search results

#### With Explorer Plugin
- File tree shows PO file status
- Quick open from file tree
- Project-wide translation statistics

#### With Translation Services
- Integration with translation APIs
- Auto-translation suggestions
- Translation memory lookup

#### With Version Control
- Track translation changes
- Collaborative translation workflows
- Merge conflict resolution

### Performance Optimizations

#### Large File Handling
- Lazy loading of entries
- Virtual scrolling for entry list
- Pagination for massive files
- Background file processing

#### Memory Management
- Efficient PO file parsing
- Entry caching strategies
- Garbage collection optimization
- Resource cleanup on tab close

#### UI Responsiveness
- Background validation
- Async file operations
- Progressive loading indicators
- Debounced auto-save

### Error Handling

#### File Format Errors
- Graceful handling of corrupted PO files
- Recovery suggestions for format issues
- Validation error reporting
- Safe fallback modes

#### Translation Errors
- Format string mismatch detection
- Encoding issue handling
- Plural form validation
- Context preservation

### Testing Strategy

#### Unit Tests
- PO file parsing and writing
- Validation rule implementation
- Filter and search logic
- Translation memory operations

#### Integration Tests
- Plugin lifecycle management
- Tab system integration
- Event handling verification
- File system interaction

#### UI Tests
- Entry navigation functionality
- Translation editor behavior
- Toolbar action verification
- Filter and search UI

### Migration from Old Code

The POEditor plugin incorporates functionality from:

**old_codes/main_utils/**
- po_ed_table_model.py: PO entry data modeling
- table_widgets.py: UI components for entry display

**old_codes/subcmp/**
- translation_edit_widget.py: Translation editor logic
- translation_editor_base.py: Base editor functionality
- versioned_translation_widget.py: Version control integration

**old_codes/pref/**
- Preference management for POEditor settings
- User configuration persistence

### Advanced Features

#### Translation Memory
- Automatic translation suggestions
- Context-based matching
- Translation reuse tracking
- Import/export TM databases

#### Quality Assurance
- Advanced validation rules
- Consistency checking across files
- Terminology management
- Review and approval workflows

#### Collaboration
- Multi-user editing support
- Change tracking and attribution
- Comment and review system
- Project-wide coordination

#### Automation
- Batch processing capabilities
- Script integration for custom workflows
- API for external tool integration
- Import/export automation

### Dependencies

**Core Services:**
- ConfigurationService: Settings and preferences
- FileService: File operations and monitoring
- EventService: Inter-plugin communication

**Qt Components:**
- QSplitter: Main layout management
- QListWidget: Entry list display
- QTextEdit: Translation editor
- QToolBar: Action toolbar
- QStatusBar: Progress and status display

**External Libraries:**
- polib: PO file parsing and manipulation
- chardet: Character encoding detection
- babel: Locale and pluralization support
