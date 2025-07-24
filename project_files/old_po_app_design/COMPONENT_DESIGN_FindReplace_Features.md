# FindReplace Component Design Specification

## Overview
The FindReplace system in the PySide PO Editor provides comprehensive search and replacement functionality across multiple contexts: main application (Standalone/Local), preferences (pref/tran_history), and text replacements. This document describes the architecture, components, and integration patterns of this multi-layered search system.

## Core Architecture

### Component Hierarchy
```
FindReplace System
├── Main Application (Standalone/Local)
│   ├── Inline FindReplace Bar (workspace/find_replace_bar.py)
│   ├── Standalone Results Dialog (workspace/find_replace_results_dialog.py)
│   └── Main GUI Integration (main_gui.py)
├── Translation History (pref/tran_history)
│   ├── Database Search Integration (translation_db_gui.py)
│   ├── Search Navigation Bar (tran_search_nav_bar.py)
│   └── Paged Search Navigation (paged_search_nav_bar.py)
├── Text Replacements (pref/repl)
│   ├── Replacement Rules Management (replacement_gui.py)
│   └── Real-time Text Substitution
└── Cross-Component Integration
    ├── Find/Replace Manager (subcmp/find_replace_manager.py)
    ├── Shared Types (workspace/find_replace_types.py)
    └── Common Actions (main_utils/find_replace_action.py)
```

### Data Model Architecture
```python
# Core data structures shared across all components
@dataclass
class FindReplaceRequest:
    msgid_pattern: str = ""
    msgid_match_case: bool = False
    msgid_word_boundary: bool = False
    msgid_regex: bool = False
    msgid_negation: bool = False
    msgid_empty: bool = False
    msgid_empty_mode: EmptyMode = EmptyMode.DO_NOT_ALLOW_EMPTY
    msgstr_pattern: str = ""
    msgstr_match_case: bool = False
    msgstr_word_boundary: bool = False
    msgstr_regex: bool = False
    msgstr_negation: bool = False
    msgstr_empty: bool = False
    msgstr_empty_mode: EmptyMode = EmptyMode.DO_NOT_ALLOW_EMPTY
    context: str = ""
    and_logic: bool = True
    replace_with: str = ""
```

## Main Application FindReplace (Standalone/Local)

### 1. Inline FindReplace Bar
**Location**: `workspace/find_replace_bar.py`
**Purpose**: Primary search interface embedded in the main window

#### Key Features
- **Multi-field Search**: Simultaneous search across msgid, msgstr, and context fields
- **Advanced Options**: Regex, case sensitivity, word boundaries, negation
- **Flag Integration**: Visual flag buttons within search fields
- **Real-time Feedback**: Live search result counting and navigation
- **Empty Field Detection**: Special handling for empty translations

#### Component Structure
```python
class FindReplaceBar(QWidget):
    # Search configuration
    find_requested = Signal(FindReplaceRequest)
    replace_one_requested = Signal(FindReplaceRequest)
    replace_all_requested = Signal(FindReplaceRequest)
    jump_requested = Signal(str)  # "prev" or "next"
    
    # Visual elements
    - FlagLineEdit for msgid search (with flag buttons)
    - FlagLineEdit for msgstr search (with flag buttons)
    - Context combo box
    - Replace field with buttons
    - Navigation controls (prev/next/count)
```

#### Flag System
- **Case Sensitivity (Aa)**: Toggle case-sensitive matching
- **Word Boundary (𝗮𝗯)**: Match whole words only
- **Regex (.*)**: Enable regular expression mode
- **Negation (≠)**: Find entries that don't match pattern
- **Empty (∅)**: Special empty field detection with three modes:
  - `DO_NOT_ALLOW_EMPTY`: Ignore empty fields
  - `EMPTY_ONLY`: Match only empty fields
  - `EMPTY_INCLUSIVE`: Match both empty and non-empty fields

### 2. Standalone Results Dialog
**Location**: `workspace/find_replace_results_dialog.py`
**Purpose**: Dedicated window for viewing and navigating search results

#### Key Features
- **Paged Results**: Handle large result sets with pagination
- **Detailed View**: Show match context, line numbers, and match types
- **Integrated Editor**: View and edit selected entries inline
- **Cross-navigation**: Jump to main window entry from results
- **Match Highlighting**: Visual emphasis on matched text spans

#### Table Structure
```python
FIND_REPLACE_TABLE_COLUMNS = [
    ("Index", QHeaderView.Fixed),
    ("Message ID", QHeaderView.Stretch),
    ("Translation", QHeaderView.Stretch),
    ("Context", QHeaderView.Interactive),
    ("Match", QHeaderView.Interactive),  # Shows which field matched
    ("Line No", QHeaderView.Fixed),
]
```

### 3. Main GUI Integration
**Location**: `main_gui.py`
**Purpose**: Core integration point for search functionality

#### Search Modes
```python
class POEditorWindow:
    # Search state management
    search_mode: bool = False
    _search_results: List[FindReplaceResult] = []
    _search_indices: List[int] = []
    _current_search: int = -1
    _all_match_instances: List[MatchInstance] = []
    _current_instance: int = -1
    _use_instance_navigation: bool = False
```

#### Key Operations
- **Search Execution**: Process find requests and filter table view
- **Navigation Management**: Move between search results with keyboard shortcuts
- **State Transitions**: Switch between normal and search modes
- **Editor Integration**: Highlight matches in translation editors

## Translation History FindReplace (pref/tran_history)

### 1. Database Search Integration
**Location**: `pref/tran_history/translation_db_gui.py`
**Purpose**: Search within translation memory database

#### Features
- **SQL-based Search**: Direct database queries for performance
- **Version-aware Search**: Search across all translation versions
- **Source Filtering**: Filter by translation source/origin
- **Batch Operations**: Replace across multiple database entries

#### Search Implementation
```python
class TranslationHistoryDialog:
    # Database search components
    find_bar: FindReplaceBar
    paging_mode: PagingMode  # DATABASE_VIEW or FIND_REPLACE_VIEW
    search_results: List[FindReplaceResult]
    
    # Advanced navigation
    _all_match_instances: List[MatchInstance]
    _current_instance: int
    _use_instance_navigation: bool
```

### 2. Search Navigation Components
**Location**: `pref/tran_history/tran_search_nav_bar.py`, `paged_search_nav_bar.py`
**Purpose**: Specialized navigation for database search results

#### Navigation Patterns
- **Database Paging**: Navigate through all database records
- **Search Result Paging**: Navigate only through search matches
- **Instance Navigation**: Move between specific match instances within entries
- **Paired Navigation**: Synchronize msgid/msgstr matches for AND operations

### 3. Advanced Search Features
- **Fuzzy Matching**: Find similar but not identical translations
- **Similarity Scoring**: Rank matches by relevance
- **Context Filtering**: Search within specific translation contexts
- **Version Comparison**: Compare search results across versions

## Text Replacements System (pref/repl)

### 1. Replacement Rules Management
**Location**: `pref/repl/replacement_gui.py`
**Purpose**: Manage text substitution rules and patterns

#### Interface Components
```python
class ReplacementsDialog(QWidget):
    # Search interface
    scope_combo: QComboBox  # "Both", "Shortcut", "Replacement"
    match_case_cb: QCheckBox  # Case sensitivity
    match_boundary_cb: QCheckBox  # Word boundaries
    match_regex_cb: QCheckBox  # Regular expressions
    search_field: ReplacementLineEdit
    
    # Navigation controls
    find_btn: QPushButton
    prev_btn: QPushButton  # ↑
    next_btn: QPushButton  # ↓
    
    # Rule management
    table: QTableWidget  # Shortcut -> Replacement mapping
    edit_panel: QWidget  # Rule editing interface
```

#### Search Capabilities
- **Scoped Search**: Search within shortcuts, replacements, or both
- **Pattern Matching**: Support for regex patterns in rule definitions
- **Real-time Filtering**: Filter rules as user types
- **Navigation Support**: Move between matching rules

### 2. Real-time Text Substitution
**Integration**: Embedded in text editor components
**Purpose**: Automatic text replacement during typing

#### Features
- **Live Processing**: Replace text as user types
- **Word Boundary Detection**: Trigger replacements at appropriate boundaries
- **Undo Integration**: Replacements can be undone like normal edits
- **Context Awareness**: Apply rules based on current editing context

## Cross-Component Integration

### 1. Find/Replace Manager
**Location**: `subcmp/find_replace_manager.py`
**Purpose**: Unified pagination and search result management

#### Key Features
```python
class FindReplaceManager:
    # Dual-mode operation
    pagination_mode: PaginationMode  # DATABASE or SEARCH
    
    # Search result management
    search_results: List[FindReplaceResult]
    database_pager: DatabasePager
    
    # Navigation interface
    def go_first() -> None
    def go_prev() -> None
    def go_next() -> None
    def go_last() -> None
    def set_search_results(results: List) -> None
    def clear_search_results() -> None
```

### 2. Shared Type System
**Location**: `workspace/find_replace_types.py`
**Purpose**: Common data structures across all components

#### Core Types
```python
# Search configuration
class FindReplaceRequest
class FindReplaceResult
class MatchInstance
class MatchPair

# Operational modes
class PagingMode(Enum)
class EmptyMode(Enum)
class FindReplaceScope(Enum)
class FindReplaceOperation(Enum)
class ReplacementCaseMatch(Enum)
```

### 3. Common Actions
**Location**: `main_utils/find_replace_action.py`
**Purpose**: Shared search and replace logic

#### Core Functions
```python
def match_field(pattern, value, match_case, word_boundary, regex, negation)
def do_replace(text, pattern, repl, match_case, word_boundary, regex)
def find_po_entries(entries, find_request: FindReplaceRequest)
def replace_one(entries, model, search_indices, current_search, find_request)
def replace_all(entries, model, find_request: FindReplaceRequest)
```

## User Experience Design

### 1. Search Workflow Patterns

#### Inline Search (Main Application)
1. **Trigger**: Ctrl+F or show findbar action
2. **Configure**: Set search patterns and options
3. **Execute**: Press Find button or Enter in search field
4. **Navigate**: Use Prev/Next buttons or keyboard shortcuts
5. **Replace**: Single replace or replace all operations
6. **Exit**: Escape key or close findbar

#### Database Search (Translation History)
1. **Access**: Open Translation History dialog
2. **Search**: Use embedded findbar within dialog
3. **Mode Switch**: Automatic switch from database to search pagination
4. **Navigate**: Page through search results or use instance navigation
5. **Edit**: Select entries and modify in integrated editor
6. **Export**: Save search results to external files

#### Text Replacement Management
1. **Configure**: Define shortcut → replacement mappings
2. **Search Rules**: Find existing rules with advanced filters
3. **Edit Rules**: Modify shortcuts and replacement text
4. **Test**: Real-time application in text editors
5. **Share**: Import/export rule configurations

### 2. Visual Feedback System

#### Search State Indicators
- **Mode Badges**: Clear indication of current search mode
- **Result Counters**: "Match X of Y" display
- **Progress Indicators**: For long-running searches
- **Match Highlighting**: Visual emphasis on found text

#### Navigation Aids
- **Keyboard Shortcuts**: F3/Shift+F3 for next/previous
- **Button States**: Enabled/disabled based on navigation possibility
- **Page Information**: Current page and total page display
- **Jump Indicators**: Visual feedback when moving between matches

## Technical Implementation

### 1. Performance Optimization

#### Search Algorithms
- **Incremental Search**: Build results progressively for large datasets
- **Index-based Lookup**: Use database indexes for fast searching
- **Lazy Loading**: Load search results on demand
- **Caching Strategy**: Cache recent search results for quick access

#### Memory Management
- **Paged Results**: Limit memory usage with pagination
- **Result Cleanup**: Automatic cleanup of old search data
- **Weak References**: Prevent memory leaks in cross-component communication

### 2. Error Handling

#### Search Validation
- **Pattern Validation**: Check regex patterns before execution
- **Empty Result Handling**: Graceful handling of no-match scenarios
- **Performance Timeouts**: Limit search execution time
- **Recovery Mechanisms**: Restore state after search errors

#### User Feedback
- **Error Messages**: Clear description of search problems
- **Status Updates**: Real-time feedback on search progress
- **Fallback Options**: Alternative search methods when primary fails

### 3. Extension Points

#### Plugin Architecture
- **Search Providers**: Custom search algorithm implementations
- **Result Processors**: Post-process search results
- **UI Extensions**: Add custom search interface elements
- **Export Handlers**: Custom export formats for search results

#### Configuration System
- **Search Preferences**: User-configurable search behavior
- **Performance Tuning**: Adjustable search parameters
- **Interface Customization**: Configurable UI layouts
- **Keyboard Mapping**: Customizable keyboard shortcuts

## Integration Patterns

### 1. Signal/Slot Communication
```python
# Cross-component communication
find_bar.find_requested.connect(main_window.perform_search)
find_bar.replace_one_requested.connect(main_window.replace_current)
find_bar.jump_requested.connect(main_window.navigate_results)

# Result feedback
search_engine.results_ready.connect(results_dialog.update_results)
search_engine.progress_updated.connect(status_bar.update_progress)
```

### 2. State Synchronization
```python
# Maintain consistency across components
class SearchStateManager:
    def sync_search_mode(self, enabled: bool):
        self.main_window.set_search_mode(enabled)
        self.results_dialog.set_search_mode(enabled)
        self.find_bar.set_search_mode(enabled)
```

### 3. Data Flow Architecture
```
User Input → FindReplaceBar → FindReplaceRequest → SearchEngine
    ↓
SearchEngine → FindReplaceResult → ResultsProcessor → UI Update
    ↓
UI Components → Navigation Events → State Management → User Feedback
```

## Future Enhancements

### 1. Advanced Search Features
- **Fuzzy Search**: Approximate string matching
- **Semantic Search**: Context-aware search using AI
- **Multi-file Search**: Search across multiple PO files
- **Search Templates**: Saved search configurations

### 2. Collaboration Features
- **Shared Searches**: Team-wide search configurations
- **Search History**: Remember and replay previous searches
- **Annotation Support**: Add notes to search results
- **Review Workflows**: Collaborative review of search findings

### 3. Performance Improvements
- **Background Search**: Non-blocking search execution
- **Parallel Processing**: Multi-threaded search operations
- **Smart Indexing**: Pre-index content for faster searches
- **Result Prediction**: Predict search results as user types

This comprehensive FindReplace system provides powerful search and replacement capabilities across all contexts of the PO Editor application, from quick inline searches to advanced database queries and automated text substitutions. The modular architecture ensures consistency while allowing each component to specialize for its specific use case.
