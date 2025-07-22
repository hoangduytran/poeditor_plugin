# Search Plugin Design

## Overview
The Search plugin provides global search and replace functionality across the workspace, integrated with the POEditor application's tab system. It offers powerful text search capabilities with special support for PO file content and translation workflows.

## Architecture

### Core Components

#### 1. SearchPlugin (plugin.py)
**Purpose:** Main plugin entry point and registration

**Key Features:**
- Plugin registration with sidebar panel
- Command registration for search operations
- Event handling for search-related actions
- Integration with editor tabs and file system

**Interface:**
```python
def register(api: PluginAPI) -> None
def unregister(api: PluginAPI) -> None
```

#### 2. SearchPanel (search_panel.py)
**Purpose:** Main search interface in the sidebar

**Key Features:**
- Search input with regex and case sensitivity options
- Replace functionality with preview
- Scope selection (workspace, folder, files)
- Results tree with file grouping
- Search history management

**Interface:**
```python
class SearchPanel(QWidget):
    search_requested = Signal(SearchRequest)
    replace_requested = Signal(ReplaceRequest)
    result_selected = Signal(SearchResult)
    
    def __init__(self, api: PluginAPI)
    def start_search(self, query: str) -> None
    def clear_results(self) -> None
    def set_search_scope(self, scope: SearchScope) -> None
    def show_replace_mode(self, enabled: bool) -> None
```

#### 3. SearchEngine (engine/search_engine.py)
**Purpose:** Core search logic and file processing

**Key Features:**
- Multi-threaded search execution
- Regex and plain text search
- File type-specific search (PO files)
- Search result ranking and filtering
- Progress reporting

**Interface:**
```python
class SearchEngine(QObject):
    progress_updated = Signal(int, int)
    result_found = Signal(SearchResult)
    search_completed = Signal(SearchSummary)
    
    def __init__(self)
    def start_search(self, request: SearchRequest) -> None
    def stop_search(self) -> None
    def search_in_file(self, file_path: str, query: str) -> List[SearchResult]
```

#### 4. SearchResultsView (widgets/results_view.py)
**Purpose:** Display and manage search results

**Key Features:**
- Hierarchical results (file → matches)
- Syntax highlighting for matches
- Context lines around matches
- Quick navigation to results
- Batch operations on results

**Interface:**
```python
class SearchResultsView(QTreeWidget):
    result_activated = Signal(SearchResult)
    results_selected = Signal(List[SearchResult])
    
    def __init__(self)
    def add_results(self, results: List[SearchResult]) -> None
    def clear_results(self) -> None
    def group_by_file(self, enabled: bool) -> None
    def filter_results(self, filter_text: str) -> None
```

#### 5. ReplaceManager (engine/replace_manager.py)
**Purpose:** Handle search and replace operations

**Key Features:**
- Preview replace operations
- Batch replace with confirmation
- Undo/redo support
- Backup creation for safety
- PO file-aware replacements

**Interface:**
```python
class ReplaceManager(QObject):
    replace_preview = Signal(List[ReplacePreview])
    replace_completed = Signal(ReplaceSummary)
    
    def __init__(self)
    def preview_replace(self, request: ReplaceRequest) -> None
    def execute_replace(self, previews: List[ReplacePreview]) -> None
    def create_backup(self, files: List[str]) -> str
```

#### 6. POSearchProvider (providers/po_search.py)
**Purpose:** Specialized search for PO files

**Key Features:**
- Search in msgid, msgstr, comments
- Translation status filtering
- Fuzzy/untranslated match detection
- Context-aware search
- Plural form handling

**Interface:**
```python
class POSearchProvider:
    def search_po_file(self, file_path: str, query: str, options: POSearchOptions) -> List[POSearchResult]
    def search_msgid(self, entry: POEntry, query: str) -> bool
    def search_msgstr(self, entry: POEntry, query: str) -> bool
    def search_comments(self, entry: POEntry, query: str) -> bool
```

### Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Search Panel                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                        Search Input                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🔍 Search for...                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ⟲ Replace with...                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Options: [Aa] Case  [.*] Regex  [💬] PO Content  [🌐] All Files       │
│                                                                         │
│  Scope: ● Workspace  ○ Folder  ○ Files  [📁 Browse...]                 │
├─────────────────────────────────────────────────────────────────────────┤
│                        Search Results                                   │
│  📄 messages.po (5 matches)                                             │
│  ├── Line 42: msgid "Hello {name}"                                      │
│  │             ^^^^^ ─────                                              │
│  ├── Line 86: msgstr "Hello {name}"                                     │
│  │              ^^^^^ ─────                                              │
│  └── Line 123: #. Greeting message                                      │
│               ^^^^^ ───────                                              │
│                                                                         │
│  📄 ui.po (2 matches)                                                   │
│  ├── Line 15: msgid "Hello world"                                       │
│  │             ^^^^^                                                    │
│  └── Line 34: #: src/main.py:hello_function                             │
│               ^^^^^                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                        Action Bar                                       │
│  🔍 Search  ⟲ Replace All  📋 Copy Results  💾 Save Results  ⚙️ Options │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Models

#### SearchRequest
```python
@dataclass
class SearchRequest:
    query: str
    case_sensitive: bool = False
    use_regex: bool = False
    whole_word: bool = False
    scope: SearchScope = SearchScope.WORKSPACE
    file_patterns: List[str] = None
    exclude_patterns: List[str] = None
    po_search_options: POSearchOptions = None
```

#### SearchResult
```python
@dataclass
class SearchResult:
    file_path: str
    line_number: int
    column_start: int
    column_end: int
    line_content: str
    match_text: str
    context_before: List[str] = None
    context_after: List[str] = None
    po_entry_context: POEntryContext = None
```

#### POSearchOptions
```python
@dataclass
class POSearchOptions:
    search_msgid: bool = True
    search_msgstr: bool = True
    search_comments: bool = False
    search_extracted_comments: bool = False
    only_fuzzy: bool = False
    only_untranslated: bool = False
    include_obsolete: bool = False
```

### Search Flow

1. **User Input:**
   - User enters search query and options
   - Selects search scope and file patterns
   - Clicks search button or presses Enter

2. **Search Execution:**
   - SearchEngine creates worker threads
   - Files are discovered based on scope
   - Each file is processed by appropriate provider
   - Results are collected and ranked

3. **Results Display:**
   - Results grouped by file
   - Syntax highlighting applied
   - Context lines shown
   - Progress and statistics updated

4. **Result Navigation:**
   - User clicks result → Opens file and navigates to match
   - Integration with tab system
   - Highlighting in editor

### Replace Flow

1. **Replace Request:**
   - User enters replacement text
   - Selects replace options
   - Chooses preview or direct replacement

2. **Preview Generation:**
   - ReplaceManager analyzes all matches
   - Shows before/after comparison
   - Allows selective replacement

3. **Execution:**
   - Creates backup of modified files
   - Applies replacements atomically
   - Updates open tabs
   - Provides undo capability

### Configuration

The Search plugin uses the following configuration in the `search` namespace:

```python
DEFAULT_CONFIG = {
    "case_sensitive": False,
    "use_regex": False,
    "whole_word": False,
    "max_results": 10000,
    "context_lines": 2,
    "search_history": [],
    "replace_history": [],
    "file_patterns": ["*.po", "*.pot", "*.py", "*.md", "*.txt"],
    "exclude_patterns": ["*.pyc", "__pycache__", ".git", "node_modules"],
    "auto_backup": True,
    "backup_location": "backups/",
    "po_search_enabled": True,
    "po_search_msgid": True,
    "po_search_msgstr": True,
    "po_search_comments": False,
    "highlight_color": "#ffff00",
    "max_file_size": 10485760,  # 10MB
    "thread_count": 4
}
```

### Commands

The Search plugin registers these commands:

- `search.show_panel`: Show search panel in sidebar
- `search.search_workspace`: Start workspace search
- `search.search_selection`: Search current selection
- `search.find_in_files`: Advanced find in files dialog
- `search.replace_in_files`: Replace in files with preview
- `search.next_result`: Navigate to next search result
- `search.previous_result`: Navigate to previous search result
- `search.clear_results`: Clear all search results
- `search.save_results`: Save results to file
- `search.load_results`: Load results from file

### Events

**Emitted:**
- `search.started`: When search begins
- `search.progress`: Search progress updates
- `search.completed`: When search finishes
- `search.result_selected`: When user selects a result
- `search.replace_started`: When replace operation begins
- `search.replace_completed`: When replace finishes

**Listened:**
- `tab.file_opened`: Update search context
- `editor.selection_changed`: Update search from selection
- `file.changed`: Re-search modified files if needed

### Integration Points

#### With Tab System
- Opens search results in appropriate tabs
- Highlights matches in open editors
- Syncs with active tab for context

#### With Explorer Plugin
- Uses file tree for scope selection
- Provides file context for results
- Integrates with workspace management

#### With POEditor Plugin
- Specialized PO file search
- Translation status integration
- Context-aware navigation

#### With Editor Services
- Text highlighting and navigation
- Selection-based search
- Replace operation integration

### Performance Optimizations

#### Parallel Processing
- Multi-threaded file processing
- Async result collection
- Background indexing for speed

#### Memory Management
- Streaming large file processing
- Result pagination for large result sets
- Efficient regex compilation

#### Caching
- File content caching for repeated searches
- Index caching for workspace
- Pattern compilation caching

### Error Handling

#### File Access Errors
- Graceful handling of permission issues
- Skip inaccessible files with warnings
- Continue search despite individual failures

#### Search Pattern Errors
- Validate regex patterns before search
- Provide helpful error messages
- Fallback to literal search on regex failure

#### Replace Operation Errors
- Atomic file operations
- Rollback capability on failures
- Comprehensive error reporting

### Testing Strategy

#### Unit Tests
- Search engine logic
- Pattern matching algorithms
- Replace operation correctness
- PO file-specific functionality

#### Integration Tests
- Plugin lifecycle and registration
- Inter-plugin communication
- File system integration

#### Performance Tests
- Large file handling
- Memory usage under load
- Search speed benchmarks

### Migration from Old Code

The Search plugin adapts functionality from:

**old_codes/search/**
- fast_search.py: Core search algorithms
- fast_search_open_ext_editor.py: External editor integration

**old_codes/subcmp/find_replace_manager.py**
- Replace operation management
- Preview and confirmation logic

### Advanced Features

#### Search Indexing
- Background workspace indexing
- Incremental index updates
- Fast symbol and reference search

#### Smart Search
- Auto-completion for search terms
- Suggested patterns based on context
- Machine learning for result ranking

#### Collaborative Features
- Shared search results
- Team search patterns
- Search result annotations

### Dependencies

**Core Services:**
- ConfigurationService: Settings and preferences
- FileService: File access and monitoring
- EventService: Inter-plugin communication

**Qt Components:**
- QTreeWidget: Results display
- QLineEdit: Search input
- QProgressBar: Search progress
- QSplitter: Panel layout

**External Libraries:**
- re: Regular expression processing
- threading: Parallel search execution
- polib: PO file parsing and analysis
