# Advanced Search Service Design

**Date**: July 24, 2025  
**Component**: Advanced Search Service  
**Status**: Design  
**Dependencies**: POEditor Plugin Core, Translation Database Service

## 1. Overview

The Advanced Search Service provides comprehensive search capabilities for the POEditor plugin, enabling users to efficiently locate and manipulate translations across PO files and the translation database. This service integrates with the POEditor Tab and other components to offer powerful search functionality that extends beyond simple text matching.

## 2. Core Features

### 2.1 Search Capabilities

- **Basic Text Search**: Simple substring matching across msgid and msgstr fields
- **Regular Expression Search**: Advanced pattern matching with full regex support
- **Multi-Field Search**: Search across msgid, msgstr, comments, and context fields
- **Combined Search**: Logical combinations of search criteria (AND, OR, NOT)
- **Filtered Search**: Limit searches to specific entry statuses (fuzzy, translated, untranslated)
- **Saved Searches**: Store and recall complex search queries

### 2.2 Search Result Management

- **Result Navigation**: Move between search results in document or across files
- **Result Highlighting**: Highlight matching text in the editor
- **Results Panel**: Display all matches in a separate panel for easy navigation
- **Search History**: Track recent searches for quick re-execution

### 2.3 Replacement Capabilities

- **Single Replacement**: Replace individual matches
- **Batch Replacement**: Replace all matches at once
- **Conditional Replacement**: Replace only matches that meet specific criteria
- **Preview Replacement**: See the effect of replacements before applying them

## 3. Architecture

### 3.1 Component Diagram

```
+----------------------+     +----------------------+     +----------------------+
| POEditor Tab         |     | Translation DB       |     | Find/Replace Bar     |
|                      |     | Service              |     |                      |
+----------+-----------+     +----------+-----------+     +----------+-----------+
           |                            |                            |
           v                            v                            v
+----------+-----------+     +----------+-----------+     +----------+-----------+
| Advanced Search      |<--->| Search Results       |<--->| Search History       |
| Engine               |     | Manager              |     | Manager              |
+----------+-----------+     +----------+-----------+     +----------------------+
           |                            ^
           v                            |
+----------+-----------+                |
| Pattern Matching     |                |
| Engine               |                |
+----------+-----------+                |
           |                            |
           v                            |
+----------+-----------+                |
| Replacement          |----------------+
| Engine               |
+----------------------+
```

### 3.2 Class Diagram

```
+-------------------+     +-------------------+     +-------------------+
| AdvancedSearchSvc |     | SearchPattern     |     | SearchResults     |
+-------------------+     +-------------------+     +-------------------+
| - api: PluginAPI  |     | - pattern: str    |     | - matches: list   |
| - history: list   |     | - is_regex: bool  |     | - current_idx: int|
+-------------------+     | - case_sensitive  |     +-------------------+
| + search()        |     | - whole_word      |     | + get_match()     |
| + replace()       |     +-------------------+     | + next_match()    |
| + find_next()     |     | + compile()       |     | + prev_match()    |
| + find_previous() |     | + matches()       |     | + goto_match()    |
+-------------------+     +-------------------+     +-------------------+
        |                          ^                        ^
        v                          |                        |
+-------------------+     +-------------------+     +-------------------+
| SearchHistory     |     | RegexPattern      |     | ModelAdapter      |
+-------------------+     +-------------------+     +-------------------+
| - recent: list    |     | - regex: Pattern  |     | - model: QAbsModel|
| - saved: dict     |     | - flags: int      |     | - columns: dict   |
+-------------------+     +-------------------+     +-------------------+
| + add()           |     | + compile()       |     | + get_text()      |
| + get_recent()    |     | + matches()       |     | + set_text()      |
| + save()          |     +-------------------+     | + get_count()     |
| + get_saved()     |                               +-------------------+
+-------------------+
```

## 4. Interface Definition

### 4.1 Primary Interface

```python
class AdvancedSearchService(Service):
    """Service providing advanced search capabilities."""
    
    def __init__(self, api: PluginAPI):
        """Initialize the search service."""
        super().__init__(api)
        self._history = SearchHistory()
        self._results = SearchResults()
        self._last_search = None
    
    def search(self, model: QAbstractItemModel, text: str, options: dict) -> List[SearchMatch]:
        """
        Perform a search in the model with the given options.
        
        Args:
            model: The model to search in
            text: The text pattern to search for
            options: Search options dict with keys:
                   - regex: bool, use regex matching
                   - case_sensitive: bool, case sensitivity
                   - whole_words: bool, match whole words only
                   - scope: str, scope of search ('all', 'source', 'translation', etc.)
                   - status_filter: str, filter by entry status ('all', 'fuzzy', etc.)
        
        Returns:
            List of search match results
        """
        # Implementation
    
    def replace(self, model: QAbstractItemModel, find_text: str, 
               replace_text: str, options: dict) -> int:
        """
        Replace occurrences of find_text with replace_text.
        
        Args:
            model: The model to perform replacements in
            find_text: The text to find
            replace_text: The text to replace with
            options: Search and replace options
        
        Returns:
            Number of replacements made
        """
        # Implementation
    
    def find_next(self) -> Optional[SearchMatch]:
        """Go to next search result."""
        # Implementation
    
    def find_previous(self) -> Optional[SearchMatch]:
        """Go to previous search result."""
        # Implementation
    
    def get_search_history(self) -> List[str]:
        """Get recent search history."""
        # Implementation
    
    def save_search(self, name: str, query: dict) -> bool:
        """Save a search query for future use."""
        # Implementation
    
    def get_saved_searches(self) -> Dict[str, dict]:
        """Get all saved searches."""
        # Implementation
```

### 4.2 Data Structures

```python
class SearchMatch:
    """Represents a single search match result."""
    
    def __init__(self, model_index: QModelIndex, match_start: int, match_end: int,
                match_text: str, field_name: str):
        """
        Initialize a search match.
        
        Args:
            model_index: The model index where the match was found
            match_start: Start position of match in the text
            match_end: End position of match in the text
            match_text: The matched text
            field_name: The field name where match was found
        """
        self.model_index = model_index
        self.match_start = match_start
        self.match_end = match_end
        self.match_text = match_text
        self.field_name = field_name
        
class SearchResults:
    """Manages search result navigation."""
    
    def __init__(self):
        """Initialize search results container."""
        self.matches = []
        self.current_index = -1
        
    def set_matches(self, matches: List[SearchMatch]):
        """Set the search matches and reset current index."""
        self.matches = matches
        self.current_index = 0 if matches else -1
        
    def get_current_match(self) -> Optional[SearchMatch]:
        """Get the current search match."""
        if not self.matches or self.current_index < 0:
            return None
        return self.matches[self.current_index]
        
    def next_match(self) -> Optional[SearchMatch]:
        """Go to next match and return it."""
        if not self.matches:
            return None
            
        self.current_index = (self.current_index + 1) % len(self.matches)
        return self.get_current_match()
        
    def previous_match(self) -> Optional[SearchMatch]:
        """Go to previous match and return it."""
        if not self.matches:
            return None
            
        self.current_index = (self.current_index - 1) % len(self.matches)
        return self.get_current_match()
        
    def get_match_count(self) -> int:
        """Get the total number of matches."""
        return len(self.matches)
```

### 4.3 Search Pattern Classes

```python
class SearchPattern:
    """Base class for search patterns."""
    
    def __init__(self, pattern: str, case_sensitive: bool = False,
                whole_word: bool = False):
        """
        Initialize a search pattern.
        
        Args:
            pattern: The text pattern to search for
            case_sensitive: Whether to match case
            whole_word: Whether to match whole words only
        """
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        
    def matches(self, text: str) -> List[Tuple[int, int]]:
        """
        Find all matches in the given text.
        
        Args:
            text: The text to search in
            
        Returns:
            List of (start, end) tuples for each match
        """
        if not text or not self.pattern:
            return []
            
        search_text = text
        search_pattern = self.pattern
        
        if not self.case_sensitive:
            search_text = search_text.lower()
            search_pattern = search_pattern.lower()
            
        results = []
        start = 0
        
        while True:
            pos = search_text.find(search_pattern, start)
            if pos == -1:
                break
                
            if self.whole_word:
                # Check if it's a whole word
                is_whole_word = True
                if pos > 0 and search_text[pos - 1].isalnum():
                    is_whole_word = False
                if (pos + len(search_pattern) < len(search_text) and 
                    search_text[pos + len(search_pattern)].isalnum()):
                    is_whole_word = False
                    
                if not is_whole_word:
                    start = pos + 1
                    continue
                    
            results.append((pos, pos + len(search_pattern)))
            start = pos + 1
            
        return results
        
class RegexPattern(SearchPattern):
    """Regular expression search pattern."""
    
    def __init__(self, pattern: str, case_sensitive: bool = False):
        """Initialize regex search pattern."""
        super().__init__(pattern, case_sensitive)
        self.regex = None
        self._compile()
        
    def _compile(self):
        """Compile the regex pattern."""
        flags = 0
        if not self.case_sensitive:
            flags = re.IGNORECASE
            
        try:
            self.regex = re.compile(self.pattern, flags)
        except re.error:
            self.regex = None
            
    def matches(self, text: str) -> List[Tuple[int, int]]:
        """Find all regex matches in the given text."""
        if not text or not self.regex:
            return []
            
        return [(match.start(), match.end()) for match in self.regex.finditer(text)]
```

## 5. Implementation Details

### 5.1 Search Algorithm

```python
def search(self, model: QAbstractItemModel, text: str, options: dict) -> List[SearchMatch]:
    """Perform search across model."""
    if not text or not model:
        return []
        
    # Create appropriate pattern matcher
    if options.get('regex', False):
        pattern = RegexPattern(text, options.get('case_sensitive', False))
    else:
        pattern = SearchPattern(
            text, 
            options.get('case_sensitive', False),
            options.get('whole_words', False)
        )
        
    # Create model adapter for the specific model type
    adapter = self._create_model_adapter(model)
    
    # Track matches
    matches = []
    
    # Determine search scope
    scope = options.get('scope', 'all')
    fields = self._get_fields_for_scope(scope)
    
    # Apply status filter if needed
    status_filter = options.get('status_filter', 'all')
    
    # Search in model
    for row in range(adapter.get_row_count()):
        # Skip rows that don't match status filter
        if status_filter != 'all' and not self._match_status_filter(adapter, row, status_filter):
            continue
            
        # Search in specified fields
        for field in fields:
            field_text = adapter.get_text(row, field)
            if not field_text:
                continue
                
            # Find matches in this field
            for start, end in pattern.matches(field_text):
                match_text = field_text[start:end]
                
                # Create model index for this match
                model_index = adapter.get_index(row, field)
                
                # Add to results
                matches.append(SearchMatch(
                    model_index=model_index,
                    match_start=start,
                    match_end=end,
                    match_text=match_text,
                    field_name=field
                ))
                
    # Store results for navigation
    self._results.set_matches(matches)
    
    # Add to search history
    if matches and text.strip():
        self._history.add(text)
        
    # Save last search parameters
    self._last_search = {
        'text': text,
        'options': options.copy()
    }
    
    return matches
```

### 5.2 Replacement Implementation

```python
def replace(self, model: QAbstractItemModel, find_text: str, 
           replace_text: str, options: dict) -> int:
    """Replace matches in the model."""
    # First perform search to get matches
    matches = self.search(model, find_text, options)
    if not matches:
        return 0
        
    # Group matches by row and field
    grouped_matches = {}
    for match in matches:
        key = (match.model_index.row(), match.field_name)
        if key not in grouped_matches:
            grouped_matches[key] = []
        grouped_matches[key].append(match)
        
    # Apply replacements
    adapter = self._create_model_adapter(model)
    replaced_count = 0
    
    for (row, field), field_matches in grouped_matches.items():
        # Sort matches in reverse to avoid position shifts
        field_matches.sort(key=lambda m: m.match_start, reverse=True)
        
        # Get original text
        original_text = adapter.get_text(row, field)
        if not original_text:
            continue
            
        # Apply replacements
        modified_text = original_text
        for match in field_matches:
            modified_text = (
                modified_text[:match.match_start] + 
                replace_text + 
                modified_text[match.match_end:]
            )
            replaced_count += 1
            
        # Update model with modified text
        adapter.set_text(row, field, modified_text)
        
    return replaced_count
```

### 5.3 Model Adapter Implementation

```python
class ModelAdapter:
    """Base adapter for interacting with different model types."""
    
    def __init__(self, model: QAbstractItemModel):
        """Initialize with a model."""
        self.model = model
        
    def get_row_count(self) -> int:
        """Get total row count."""
        return self.model.rowCount()
        
    def get_text(self, row: int, field: str) -> str:
        """Get text from specified row and field."""
        raise NotImplementedError("Subclasses must implement get_text")
        
    def set_text(self, row: int, field: str, text: str) -> bool:
        """Set text for specified row and field."""
        raise NotImplementedError("Subclasses must implement set_text")
        
    def get_index(self, row: int, field: str) -> QModelIndex:
        """Get model index for row and field."""
        raise NotImplementedError("Subclasses must implement get_index")
        
class POFileModelAdapter(ModelAdapter):
    """Adapter for POFileTableModel."""
    
    def __init__(self, model: QAbstractItemModel):
        """Initialize adapter."""
        super().__init__(model)
        self.column_map = {
            'msgid': self.model.SourceTextRole,
            'msgstr': self.model.TranslationRole,
            'comment': self.model.CommentRole,
            'context': self.model.ContextRole,
        }
        
    def get_text(self, row: int, field: str) -> str:
        """Get text from specified row and field."""
        if field not in self.column_map:
            return ""
            
        index = self.model.index(row, 0)
        return self.model.data(index, self.column_map[field]) or ""
        
    def set_text(self, row: int, field: str, text: str) -> bool:
        """Set text for specified row and field."""
        if field not in self.column_map:
            return False
            
        index = self.model.index(row, 0)
        return self.model.setData(index, text, self.column_map[field])
        
    def get_index(self, row: int, field: str) -> QModelIndex:
        """Get model index for row and field."""
        # For PO model, we use column 0 with a role
        return self.model.index(row, 0)
```

### 5.4 Search History Implementation

```python
class SearchHistory:
    """Manages search history."""
    
    def __init__(self, max_recent: int = 20):
        """Initialize search history."""
        self.max_recent = max_recent
        self.recent = []  # Recent searches
        self.saved = {}   # Named saved searches
        
    def add(self, text: str):
        """Add search to history."""
        # Remove if exists (to move it to front)
        if text in self.recent:
            self.recent.remove(text)
            
        # Add to front
        self.recent.insert(0, text)
        
        # Trim if needed
        if len(self.recent) > self.max_recent:
            self.recent = self.recent[:self.max_recent]
            
    def get_recent(self) -> List[str]:
        """Get recent searches."""
        return self.recent.copy()
        
    def save(self, name: str, query: dict) -> bool:
        """Save a named search query."""
        if not name or not query:
            return False
            
        self.saved[name] = query.copy()
        return True
        
    def get_saved(self) -> Dict[str, dict]:
        """Get all saved searches."""
        return self.saved.copy()
        
    def get_saved_query(self, name: str) -> Optional[dict]:
        """Get a saved query by name."""
        return self.saved.get(name)
        
    def delete_saved(self, name: str) -> bool:
        """Delete a saved search."""
        if name in self.saved:
            del self.saved[name]
            return True
        return False
```

## 6. Integration with UI Components

### 6.1 Find/Replace Bar Integration

```python
class FindReplaceBar(QWidget):
    """Search bar for the POEditor tab."""
    
    find_requested = Signal(object)
    replace_requested = Signal(object)
    replace_all_requested = Signal(object)
    
    def __init__(self, parent=None):
        """Initialize find/replace bar."""
        super().__init__(parent)
        self.search_service = None
        self._setup_ui()
        self._connect_signals()
        
    def set_search_service(self, service: AdvancedSearchService):
        """Set the search service."""
        self.search_service = service
        
    def _setup_ui(self):
        """Setup UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        
        # Find field
        self.find_field = QLineEdit()
        self.find_field.setPlaceholderText("Find")
        layout.addWidget(self.find_field)
        
        # Replace field (hidden by default)
        self.replace_field = QLineEdit()
        self.replace_field.setPlaceholderText("Replace with")
        self.replace_field.setVisible(False)
        layout.addWidget(self.replace_field)
        
        # Options button
        self.options_btn = QPushButton()
        self.options_btn.setIcon(QIcon.fromTheme("configure"))
        self.options_btn.setToolTip("Search Options")
        layout.addWidget(self.options_btn)
        
        # Navigation buttons
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.prev_btn.setToolTip("Previous Match (Shift+F3)")
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton()
        self.next_btn.setIcon(QIcon.fromTheme("go-next"))
        self.next_btn.setToolTip("Next Match (F3)")
        layout.addWidget(self.next_btn)
        
        # Replace button
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.setVisible(False)
        layout.addWidget(self.replace_btn)
        
        # Replace All button
        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.setVisible(False)
        layout.addWidget(self.replace_all_btn)
        
        # Mode toggle
        self.mode_btn = QPushButton("Replace")
        layout.addWidget(self.mode_btn)
        
        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon.fromTheme("dialog-close"))
        layout.addWidget(self.close_btn)
        
        # Result label
        self.result_label = QLabel()
        layout.addWidget(self.result_label)
        
        # Options popup menu
        self.options_menu = QMenu(self)
        self.case_action = self.options_menu.addAction("Case sensitive")
        self.case_action.setCheckable(True)
        
        self.whole_word_action = self.options_menu.addAction("Whole words only")
        self.whole_word_action.setCheckable(True)
        
        self.regex_action = self.options_menu.addAction("Regular expression")
        self.regex_action.setCheckable(True)
        
        self.options_menu.addSeparator()
        
        # Search scope menu
        self.scope_menu = self.options_menu.addMenu("Search scope")
        self.scope_all = self.scope_menu.addAction("All fields")
        self.scope_all.setCheckable(True)
        self.scope_all.setChecked(True)
        
        self.scope_msgid = self.scope_menu.addAction("Source text only")
        self.scope_msgid.setCheckable(True)
        
        self.scope_msgstr = self.scope_menu.addAction("Translation text only")
        self.scope_msgstr.setCheckable(True)
        
    def _connect_signals(self):
        """Connect widget signals."""
        # Button clicks
        self.next_btn.clicked.connect(self._on_find_next)
        self.prev_btn.clicked.connect(self._on_find_previous)
        self.options_btn.clicked.connect(self._show_options_menu)
        self.close_btn.clicked.connect(self.hide)
        self.mode_btn.clicked.connect(self._toggle_replace_mode)
        self.replace_btn.clicked.connect(self._on_replace)
        self.replace_all_btn.clicked.connect(self._on_replace_all)
        
        # Text field signals
        self.find_field.returnPressed.connect(self._on_find_next)
        self.find_field.textChanged.connect(self._on_find_text_changed)
        
        # Option actions
        self.scope_all.triggered.connect(lambda: self._set_scope("all"))
        self.scope_msgid.triggered.connect(lambda: self._set_scope("msgid"))
        self.scope_msgstr.triggered.connect(lambda: self._set_scope("msgstr"))
        
    def update_result_count(self, count: int):
        """Update the result count display."""
        if count == 0:
            self.result_label.setText("No matches")
        elif count == 1:
            self.result_label.setText("1 match")
        else:
            self.result_label.setText(f"{count} matches")
            
    def _get_search_options(self) -> dict:
        """Get current search options."""
        return {
            'case_sensitive': self.case_action.isChecked(),
            'whole_words': self.whole_word_action.isChecked(),
            'regex': self.regex_action.isChecked(),
            'scope': self._get_current_scope()
        }
        
    def _get_current_scope(self) -> str:
        """Get the current search scope."""
        if self.scope_msgid.isChecked():
            return "msgid"
        elif self.scope_msgstr.isChecked():
            return "msgstr"
        else:
            return "all"
            
    def _set_scope(self, scope: str):
        """Set the search scope."""
        self.scope_all.setChecked(scope == "all")
        self.scope_msgid.setChecked(scope == "msgid")
        self.scope_msgstr.setChecked(scope == "msgstr")
        
    def _on_find_next(self):
        """Handle find next button click."""
        text = self.find_field.text()
        if not text:
            return
            
        # Create search request
        request = SearchRequest(
            text=text,
            options=self._get_search_options(),
            direction="forward"
        )
        
        self.find_requested.emit(request)
        
    def _on_find_previous(self):
        """Handle find previous button click."""
        text = self.find_field.text()
        if not text:
            return
            
        # Create search request
        request = SearchRequest(
            text=text,
            options=self._get_search_options(),
            direction="backward"
        )
        
        self.find_requested.emit(request)
        
    def _on_replace(self):
        """Handle replace button click."""
        find_text = self.find_field.text()
        replace_text = self.replace_field.text()
        
        if not find_text:
            return
            
        # Create replace request
        request = ReplaceRequest(
            text=find_text,
            replacement=replace_text,
            options=self._get_search_options()
        )
        
        self.replace_requested.emit(request)
        
    def _on_replace_all(self):
        """Handle replace all button click."""
        find_text = self.find_field.text()
        replace_text = self.replace_field.text()
        
        if not find_text:
            return
            
        # Create replace all request
        request = ReplaceRequest(
            text=find_text,
            replacement=replace_text,
            options=self._get_search_options(),
            replace_all=True
        )
        
        self.replace_all_requested.emit(request)
```

### 6.2 Advanced Search Dialog

```python
class AdvancedSearchDialog(QDialog):
    """Dialog for advanced search operations."""
    
    search_requested = Signal(object)
    
    def __init__(self, search_service: AdvancedSearchService, parent=None):
        """Initialize advanced search dialog."""
        super().__init__(parent)
        self.search_service = search_service
        self._setup_ui()
        self._connect_signals()
        self._load_history()
        
    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("Advanced Search")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Search query builder
        query_group = QGroupBox("Search Query")
        query_layout = QGridLayout(query_group)
        
        query_layout.addWidget(QLabel("Search Text:"), 0, 0)
        self.search_text = QLineEdit()
        query_layout.addWidget(self.search_text, 0, 1, 1, 2)
        
        # Field selection
        query_layout.addWidget(QLabel("Search Fields:"), 1, 0)
        self.field_combo = QComboBox()
        self.field_combo.addItems(["All Fields", "Source Text", "Translation", 
                                  "Comments", "Context"])
        query_layout.addWidget(self.field_combo, 1, 1)
        
        # Status filter
        query_layout.addWidget(QLabel("Status Filter:"), 2, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Entries", "Untranslated Only", 
                                   "Translated Only", "Fuzzy Only"])
        query_layout.addWidget(self.status_combo, 2, 1)
        
        # Options
        query_layout.addWidget(QLabel("Options:"), 3, 0)
        option_layout = QHBoxLayout()
        
        self.case_check = QCheckBox("Case Sensitive")
        option_layout.addWidget(self.case_check)
        
        self.whole_word_check = QCheckBox("Whole Words")
        option_layout.addWidget(self.whole_word_check)
        
        self.regex_check = QCheckBox("Regular Expression")
        option_layout.addWidget(self.regex_check)
        
        query_layout.addLayout(option_layout, 3, 1, 1, 2)
        
        layout.addWidget(query_group)
        
        # Search history
        history_group = QGroupBox("Search History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        history_button_layout = QHBoxLayout()
        self.use_history_btn = QPushButton("Use Selected")
        history_button_layout.addWidget(self.use_history_btn)
        
        self.save_search_btn = QPushButton("Save Current")
        history_button_layout.addWidget(self.save_search_btn)
        
        self.delete_search_btn = QPushButton("Delete Selected")
        history_button_layout.addWidget(self.delete_search_btn)
        
        history_layout.addLayout(history_button_layout)
        layout.addWidget(history_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        layout.addWidget(button_box)
        
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        
    def _connect_signals(self):
        """Connect widget signals."""
        # Button clicks
        self.use_history_btn.clicked.connect(self._on_use_history)
        self.save_search_btn.clicked.connect(self._on_save_search)
        self.delete_search_btn.clicked.connect(self._on_delete_search)
        
        # List selection
        self.history_list.itemDoubleClicked.connect(self._on_history_double_clicked)
        
        # Option checkboxes
        self.regex_check.toggled.connect(self._on_regex_toggled)
        
    def _load_history(self):
        """Load search history."""
        if not self.search_service:
            return
            
        # Load recent searches
        recent = self.search_service.get_search_history()
        for search_text in recent:
            self.history_list.addItem(search_text)
            
        # Load saved searches
        saved = self.search_service.get_saved_searches()
        for name, query in saved.items():
            item = QListWidgetItem(f"📌 {name}")
            item.setData(Qt.UserRole, query)
            self.history_list.addItem(item)
            
    def _get_search_options(self) -> dict:
        """Get current search options from UI."""
        # Get field scope
        field_map = {
            0: "all",
            1: "msgid",
            2: "msgstr",
            3: "comment",
            4: "context"
        }
        scope = field_map.get(self.field_combo.currentIndex(), "all")
        
        # Get status filter
        status_map = {
            0: "all",
            1: "untranslated",
            2: "translated",
            3: "fuzzy"
        }
        status = status_map.get(self.status_combo.currentIndex(), "all")
        
        # Create options dictionary
        return {
            'case_sensitive': self.case_check.isChecked(),
            'whole_words': self.whole_word_check.isChecked(),
            'regex': self.regex_check.isChecked(),
            'scope': scope,
            'status_filter': status
        }
        
    def _on_accept(self):
        """Handle dialog accept."""
        search_text = self.search_text.text()
        if not search_text:
            QMessageBox.warning(self, "Missing Text", "Please enter search text.")
            return
            
        # Create search request
        request = SearchRequest(
            text=search_text,
            options=self._get_search_options(),
            from_dialog=True
        )
        
        # Emit signal with request
        self.search_requested.emit(request)
        
        # Accept dialog
        self.accept()
        
    def _on_use_history(self):
        """Apply selected history item to search fields."""
        item = self.history_list.currentItem()
        if not item:
            return
            
        # Check if this is a saved search (has user data)
        query = item.data(Qt.UserRole)
        if query:
            # Apply saved search settings
            self.search_text.setText(query.get('text', ''))
            
            # Set options
            options = query.get('options', {})
            self.case_check.setChecked(options.get('case_sensitive', False))
            self.whole_word_check.setChecked(options.get('whole_words', False))
            self.regex_check.setChecked(options.get('regex', False))
            
            # Set field combo
            scope_map = {
                "all": 0,
                "msgid": 1, 
                "msgstr": 2,
                "comment": 3,
                "context": 4
            }
            self.field_combo.setCurrentIndex(
                scope_map.get(options.get('scope', 'all'), 0)
            )
            
            # Set status combo
            status_map = {
                "all": 0,
                "untranslated": 1,
                "translated": 2,
                "fuzzy": 3
            }
            self.status_combo.setCurrentIndex(
                status_map.get(options.get('status_filter', 'all'), 0)
            )
        else:
            # Just use the text
            self.search_text.setText(item.text())
            
    def _on_save_search(self):
        """Save current search settings."""
        # Get search text
        search_text = self.search_text.text()
        if not search_text:
            QMessageBox.warning(self, "Missing Text", "Please enter search text.")
            return
            
        # Ask for a name
        name, ok = QInputDialog.getText(
            self, "Save Search", "Enter a name for this search:"
        )
        
        if not ok or not name:
            return
            
        # Create query dictionary
        query = {
            'text': search_text,
            'options': self._get_search_options()
        }
        
        # Save query
        if self.search_service.save_search(name, query):
            # Add to list
            item = QListWidgetItem(f"📌 {name}")
            item.setData(Qt.UserRole, query)
            self.history_list.addItem(item)
            
    def _on_delete_search(self):
        """Delete selected saved search."""
        item = self.history_list.currentItem()
        if not item:
            return
            
        # Get item text
        text = item.text()
        
        # Check if this is a saved search
        if text.startswith("📌"):
            name = text[2:].strip()
            
            # Confirm deletion
            confirm = QMessageBox.question(
                self, "Delete Saved Search",
                f"Are you sure you want to delete the saved search '{name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Delete from service
                if self.search_service.delete_saved(name):
                    # Remove from list
                    row = self.history_list.row(item)
                    self.history_list.takeItem(row)
        else:
            # Can't delete regular history items
            QMessageBox.information(
                self, "Cannot Delete",
                "Only saved searches can be deleted."
            )
            
    def _on_history_double_clicked(self, item):
        """Handle double click on history item."""
        self._on_use_history()
        
    def _on_regex_toggled(self, checked):
        """Handle regex checkbox toggle."""
        # Disable whole words when regex is enabled
        if checked:
            self.whole_word_check.setChecked(False)
            self.whole_word_check.setEnabled(False)
        else:
            self.whole_word_check.setEnabled(True)
```

### 6.3 Results Panel Integration

```python
class SearchResultsPanel(QWidget):
    """Panel for displaying search results."""
    
    result_selected = Signal(SearchMatch)
    
    def __init__(self, search_service: AdvancedSearchService, parent=None):
        """Initialize search results panel."""
        super().__init__(parent)
        self.search_service = search_service
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with search info and controls
        header_layout = QHBoxLayout()
        
        self.results_label = QLabel("Search Results")
        header_layout.addWidget(self.results_label)
        
        header_layout.addStretch()
        
        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon.fromTheme("dialog-close"))
        self.close_btn.setToolTip("Close Results Panel")
        header_layout.addWidget(self.close_btn)
        
        layout.addLayout(header_layout)
        
        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Text", "Field", "Context"])
        self.results_tree.setColumnWidth(0, 300)
        self.results_tree.setColumnWidth(1, 100)
        layout.addWidget(self.results_tree)
        
    def _connect_signals(self):
        """Connect widget signals."""
        self.close_btn.clicked.connect(self.hide)
        self.results_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        
    def display_results(self, matches: List[SearchMatch], query_text: str):
        """Display search results."""
        self.results_tree.clear()
        
        if not matches:
            self.results_label.setText("No matches found")
            return
            
        # Set header text
        self.results_label.setText(f"Search Results: {len(matches)} matches for '{query_text}'")
        
        # Group by model row for better organization
        grouped_matches = {}
        for match in matches:
            row = match.model_index.row()
            if row not in grouped_matches:
                grouped_matches[row] = []
            grouped_matches[row].append(match)
            
        # Add results to tree
        for row, row_matches in sorted(grouped_matches.items()):
            # Get source text for this row (first match)
            first_match = row_matches[0]
            entry_text = first_match.model_index.model().data(
                first_match.model_index, Qt.DisplayRole
            )
            
            # Create parent item for this entry
            parent_item = QTreeWidgetItem(self.results_tree)
            parent_item.setText(0, f"Entry {row + 1}: {entry_text[:50]}")
            parent_item.setExpanded(True)
            
            # Add each match as a child item
            for match in row_matches:
                child_item = QTreeWidgetItem(parent_item)
                
                # Show match with context
                before = match.match_text[:match.match_start]
                highlight = match.match_text[match.match_start:match.match_end]
                after = match.match_text[match.match_end:]
                
                display_text = f"{before[:20]}[{highlight}]{after[:20]}"
                
                child_item.setText(0, display_text)
                child_item.setText(1, match.field_name)
                
                # Store the match in the item
                child_item.setData(0, Qt.UserRole, match)
                
        # Make panel visible
        self.show()
        
    def _on_item_double_clicked(self, item, column):
        """Handle double click on result item."""
        # Get stored match
        match = item.data(0, Qt.UserRole)
        if match:
            self.result_selected.emit(match)
```

## 7. Error Handling

### 7.1 Error Handling Strategy

1. **Graceful Degradation**:
   - Handle service unavailability with informative messages
   - Provide basic search functionality even when advanced features fail

2. **Input Validation**:
   - Validate search patterns before execution
   - Handle invalid regex patterns gracefully
   - Provide feedback for invalid search parameters

3. **Transaction Safety**:
   - Ensure batch operations are transactional when possible
   - Provide undo support for batch replacements
   - Report partial failures clearly

### 7.2 Error Handling Implementation

```python
def _safe_regex_compile(self, pattern: str, flags: int = 0) -> Optional[Pattern]:
    """Safely compile regex pattern with error handling."""
    try:
        return re.compile(pattern, flags)
    except re.error as e:
        from lg import logger
        logger.warning(f"Invalid regex pattern: {e}", exc_info=True)
        
        # Report error to user
        self.api.show_notification(
            "Invalid Regular Expression", 
            f"Error in pattern '{pattern}': {str(e)}",
            "warning"
        )
        return None
        
def _handle_model_error(self, operation: str, error: Exception) -> None:
    """Handle errors when interacting with model."""
    from lg import logger
    logger.error(f"Error in {operation}: {error}", exc_info=True)
    
    # Report error to user
    self.api.show_notification(
        f"Search Error", 
        f"Error during {operation}: {str(error)}",
        "error"
    )
```

## 8. Performance Optimization

### 8.1 Performance Considerations

1. **Large File Handling**:
   - Use paginated search for large files
   - Implement background search for complex queries
   - Add cancellation support for long-running operations

2. **Efficient Algorithms**:
   - Use optimized text search algorithms for non-regex searches
   - Cache compiled regex patterns
   - Implement early termination strategies

3. **Memory Management**:
   - Limit result set size for very large files
   - Use lazy loading for search results display
   - Implement result pagination

### 8.2 Performance Optimization Implementation

```python
def _optimize_search(self, model: QAbstractItemModel, options: dict) -> dict:
    """Optimize search strategy based on model size and options."""
    # Get model size
    size = model.rowCount()
    
    # Default options
    optimized = options.copy()
    
    # For very large files (>10000 entries), enable pagination
    if size > 10000:
        optimized['paginated'] = True
        optimized['page_size'] = 1000
        
    # For regex searches on large files, use background processing
    if options.get('regex', False) and size > 5000:
        optimized['background'] = True
        
    return optimized
    
def _create_pattern_key(self, pattern: str, options: dict) -> str:
    """Create a cache key for pattern."""
    key_parts = [pattern]
    
    if options.get('case_sensitive'):
        key_parts.append('case')
        
    if options.get('whole_words'):
        key_parts.append('word')
        
    if options.get('regex'):
        key_parts.append('regex')
        
    return ":".join(key_parts)
    
def _get_cached_pattern(self, pattern: str, options: dict) -> Optional[SearchPattern]:
    """Get pattern from cache or create new."""
    key = self._create_pattern_key(pattern, options)
    
    if key in self._pattern_cache:
        return self._pattern_cache[key]
        
    # Create new pattern
    if options.get('regex', False):
        pattern_obj = RegexPattern(pattern, options.get('case_sensitive', False))
    else:
        pattern_obj = SearchPattern(
            pattern, 
            options.get('case_sensitive', False),
            options.get('whole_words', False)
        )
        
    # Cache pattern (limit cache size)
    if len(self._pattern_cache) > 50:
        # Remove oldest item (Python 3.7+ guarantees insertion order)
        self._pattern_cache.pop(next(iter(self._pattern_cache)))
        
    self._pattern_cache[key] = pattern_obj
    return pattern_obj
```

## 9. Testing Strategy

### 9.1 Unit Testing

```python
class TestAdvancedSearchService(unittest.TestCase):
    """Unit tests for the Advanced Search Service."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_mock = MagicMock()
        self.service = AdvancedSearchService(self.api_mock)
        
        # Create test model
        self.model = QStandardItemModel()
        for i in range(5):
            self.model.appendRow(QStandardItem(f"Test item {i}"))
            
    def test_basic_search(self):
        """Test basic text search functionality."""
        # Create adapter mock
        adapter_mock = MagicMock()
        adapter_mock.get_row_count.return_value = 3
        adapter_mock.get_text.side_effect = lambda row, field: {
            (0, 'msgid'): 'Hello world',
            (1, 'msgid'): 'Hello universe',
            (2, 'msgid'): 'Goodbye world',
        }.get((row, field), '')
        
        # Mock adapter creation
        self.service._create_model_adapter = MagicMock(return_value=adapter_mock)
        
        # Test search
        results = self.service.search(self.model, 'Hello', {'scope': 'msgid'})
        
        # Should find two matches
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].match_text, 'Hello world')
        self.assertEqual(results[1].match_text, 'Hello universe')
        
    def test_regex_search(self):
        """Test regex search functionality."""
        # Create adapter mock
        adapter_mock = MagicMock()
        adapter_mock.get_row_count.return_value = 3
        adapter_mock.get_text.side_effect = lambda row, field: {
            (0, 'msgid'): 'Hello world',
            (1, 'msgid'): 'Hello universe',
            (2, 'msgid'): 'Goodbye world',
        }.get((row, field), '')
        
        # Mock adapter creation
        self.service._create_model_adapter = MagicMock(return_value=adapter_mock)
        
        # Test regex search
        results = self.service.search(self.model, r'H\w+o', {
            'scope': 'msgid',
            'regex': True
        })
        
        # Should find two matches
        self.assertEqual(len(results), 2)
        
    def test_replace(self):
        """Test replace functionality."""
        # Create adapter mock
        adapter_mock = MagicMock()
        adapter_mock.get_row_count.return_value = 3
        adapter_mock.get_text.side_effect = lambda row, field: {
            (0, 'msgid'): 'Hello world',
            (1, 'msgid'): 'Hello universe',
            (2, 'msgid'): 'Goodbye world',
        }.get((row, field), '')
        
        # Mock adapter creation
        self.service._create_model_adapter = MagicMock(return_value=adapter_mock)
        
        # Test replace
        count = self.service.replace(
            self.model, 'Hello', 'Hi', {'scope': 'msgid'}
        )
        
        # Should replace in two rows
        self.assertEqual(count, 2)
        adapter_mock.set_text.assert_any_call(0, 'msgid', 'Hi world')
        adapter_mock.set_text.assert_any_call(1, 'msgid', 'Hi universe')
        
    def test_search_history(self):
        """Test search history functionality."""
        # Add some searches
        self.service.search(self.model, "test1", {})
        self.service.search(self.model, "test2", {})
        self.service.search(self.model, "test3", {})
        
        # Get history
        history = self.service.get_search_history()
        
        # Check history
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], "test3")  # Most recent first
        self.assertEqual(history[1], "test2")
        self.assertEqual(history[2], "test1")
```

### 9.2 Integration Testing

```python
class TestAdvancedSearchIntegration(unittest.TestCase):
    """Integration tests for the Advanced Search Service."""
    
    def setUp(self):
        """Set up test environment."""
        # Create real API implementation
        self.app = QApplication([])
        self.api = PluginAPI()
        
        # Register and initialize service
        self.service = AdvancedSearchService(self.api)
        self.api.register_service("advanced_search", self.service)
        
        # Create a test POEditor tab
        self.tab = POEditorTab(None, self.api)
        
        # Mock PO file loading
        po_mock = MagicMock()
        po_mock.__iter__ = MagicMock(return_value=iter([
            MagicMock(msgid="Hello world", msgstr="Hola mundo"),
            MagicMock(msgid="Goodbye world", msgstr="Adiós mundo"),
            MagicMock(msgid="Hello universe", msgstr="Hola universo"),
        ]))
        
        # Load mock entries into tab
        self.tab.model.load_entries(po_mock)
        
    def tearDown(self):
        """Clean up after tests."""
        self.app.quit()
        
    def test_tab_search_integration(self):
        """Test search integration with tab."""
        # Set up find/replace bar
        self.tab.find_replace_bar.set_search_service(self.service)
        
        # Create a search request
        request = SearchRequest(
            text="Hello",
            options={'scope': 'msgid'},
            direction="forward"
        )
        
        # Connect signal to capture results
        results_captured = []
        
        def capture_results(match):
            results_captured.append(match)
            
        self.tab.find_replace_bar.find_requested.connect(
            lambda req: capture_results(self.service.search(self.tab.model, req.text, req.options))
        )
        
        # Emit signal
        self.tab.find_replace_bar.find_requested.emit(request)
        
        # Check results
        self.assertEqual(len(results_captured), 1)
        self.assertEqual(len(results_captured[0]), 2)  # Should find "Hello world" and "Hello universe"
        
    def test_replace_integration(self):
        """Test replace integration with tab."""
        # Set up find/replace bar
        self.tab.find_replace_bar.set_search_service(self.service)
        
        # Create a replace request
        request = ReplaceRequest(
            text="Hello",
            replacement="Hi",
            options={'scope': 'msgid'},
            replace_all=True
        )
        
        # Connect signal to perform replacement
        self.tab.find_replace_bar.replace_all_requested.connect(
            lambda req: self.service.replace(self.tab.model, req.text, req.replacement, req.options)
        )
        
        # Emit signal
        self.tab.find_replace_bar.replace_all_requested.emit(request)
        
        # Check model was updated
        self.assertEqual(self.tab.model.data(self.tab.model.index(0, 0), self.tab.model.SourceTextRole), "Hi world")
        self.assertEqual(self.tab.model.data(self.tab.model.index(2, 0), self.tab.model.SourceTextRole), "Hi universe")
```

## 10. Future Enhancements

### 10.1 Advanced Features

1. **Semantic Search**
   - Implement semantic similarity search using embeddings
   - Add fuzzy matching capabilities
   - Support synonyms and related terms

2. **Search Templates**
   - Create predefined search templates for common use cases
   - Support parameterized templates
   - Allow template sharing between users

3. **Cross-file Search**
   - Implement search across multiple files
   - Create a global search index
   - Support project-wide search and replace

### 10.2 Performance Enhancements

1. **Search Indexing**
   - Implement background indexing for opened files
   - Create persistent search indexes
   - Support incremental index updates

2. **Parallel Processing**
   - Use worker threads for complex searches
   - Implement parallel matching algorithms
   - Add progress feedback for long-running operations

## 11. Conclusion

The Advanced Search Service provides a powerful and flexible search infrastructure for the POEditor plugin. By combining robust search algorithms with an intuitive UI, it enables translators to efficiently locate and modify content across their translation files. The service architecture balances performance with functionality through careful algorithm selection and optimization techniques.

The modular design allows for easy integration with the POEditor Tab component and the Translation Database Service, while providing a foundation for future enhancements like semantic search and cross-file operations. Through comprehensive error handling and extensive testing, the service ensures reliable operation even with large translation files.