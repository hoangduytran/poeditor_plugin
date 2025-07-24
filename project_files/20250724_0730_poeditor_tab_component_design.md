# POEditor Tab Component Design

**Date**: July 24, 2025  
**Component**: POEditor Tab Widget  
**Status**: Design  

## 1. Overview

The POEditor Tab Component is the central editor interface for PO files, designed to be embedded within the tab system of the new plugin architecture. This component provides the core translation editing experience, integrating table-based entry navigation with rich text editing capabilities.

## 2. Component Architecture

### 2.1 Class Hierarchy

```
POEditorTab (QWidget)
├── POFileTableView (QTableView)
│   └── POFileTableModel (QAbstractTableModel)
├── TranslationEditorPanel (QWidget)
│   ├── SourceTextDisplay (QTextBrowser)
│   ├── TranslationEditor (QTextEdit with enhancements)
│   ├── FuzzyToggle (QCheckBox)
│   └── CommentsEditor (QTextEdit)
├── FindReplaceBar (QWidget)
│   └── Advanced search controls
└── NavigationBar (QWidget)
    └── Paging and navigation controls
```

### 2.2 Primary Interfaces

```python
class POEditorTab(QWidget):
    # Signals
    modified_changed = Signal(bool)
    title_changed = Signal(str)
    status_changed = Signal(str)
    
    def __init__(self, file_path: str, api: PluginAPI, parent: Optional[QWidget] = None)
    def load_file(self, file_path: str) -> bool
    def save(self) -> bool
    def save_as(self, file_path: str) -> bool
    def is_modified(self) -> bool
    def can_close(self) -> bool
    def handle_find_request(self, request: FindReplaceRequest) -> None
    def handle_entry_selected(self, index: QModelIndex) -> None
```

## 3. Component Layout Design

### 3.1 Main Layout Structure

```
+-----------------------------------------------------------------------+
| +-------------------------------------------------------------------+ |
| | Find/Replace Bar (hidden by default)                              | |
| +-------------------------------------------------------------------+ |
| +-------------------+-------------------------------------------+     |
| |                   |                                           |     |
| |                   | Source Text Panel                         |     |
| |                   | +-----------------------------------------+     |
| | Translation Table | Translation Editor                         |     |
| |                   | +-----------------------------------------+     |
| |                   | Fuzzy Toggle | Comments Editor            |     |
| |                   |                                           |     |
| +-------------------+-------------------------------------------+     |
| +-------------------------------------------------------------------+ |
| | Navigation Bar                                                    | |
| +-------------------------------------------------------------------+ |
```

### 3.2 Layout Implementation

```python
def setup_layout(self):
    # Main layout
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Find/Replace bar (initially hidden)
    self.find_replace_bar = FindReplaceBar(self)
    self.find_replace_bar.setVisible(False)
    main_layout.addWidget(self.find_replace_bar)
    
    # Main splitter
    self.main_splitter = QSplitter(Qt.Horizontal)
    
    # Table view
    self.table_view = POFileTableView(self.model, self)
    self.main_splitter.addWidget(self.table_view)
    
    # Editor panel
    self.editor_panel = TranslationEditorPanel(self)
    self.main_splitter.addWidget(self.editor_panel)
    
    # Set initial splitter sizes (40/60 split)
    self.main_splitter.setSizes([400, 600])
    main_layout.addWidget(self.main_splitter)
    
    # Navigation bar
    self.navigation_bar = NavigationBar(self)
    main_layout.addWidget(self.navigation_bar)
```

## 4. Key Components Detail

### 4.1 POFileTableModel

**Purpose**: Provides data model for displaying and managing PO entries in a table view.

**Key Features**:
- Custom column structure for PO entries
- Display formatting for different entry states
- Editing support for translation text
- Fuzzy flag toggling
- Issue highlighting

**Column Structure**:
1. **Index**: Entry position in file
2. **Message ID**: Source text (msgid)
3. **Translation**: Target text (msgstr)
4. **Context**: Optional msgctxt field
5. **Fuzzy**: Translation status flag
6. **Line No**: Source file line reference

**Implementation Details**:
```python
class POFileTableModel(QAbstractTableModel):
    # Column indices
    COL_INDEX = 0
    COL_MSGID = 1
    COL_MSGSTR = 2
    COL_CONTEXT = 3
    COL_FUZZY = 4
    COL_LINENO = 5
    
    def __init__(self, parent: Optional[QObject] = None)
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any
    def flags(self, index: QModelIndex) -> Qt.ItemFlags
    
    # Custom methods
    def load_entries(self, entries: List[POEntry]) -> None
    def get_entry(self, index: QModelIndex) -> Optional[POEntry]
    def update_translation(self, row: int, translation: str) -> None
    def set_fuzzy(self, row: int, fuzzy: bool) -> None
    def has_issues(self, row: int) -> bool
```

### 4.2 POFileTableView

**Purpose**: Displays and allows interaction with PO entries in a tabular format.

**Key Features**:
- Custom delegates for specialized cell rendering
- Selection tracking and change handling
- Context menu for common operations
- Keyboard navigation support
- Visual indicators for issues and current entry

**Implementation Details**:
```python
class POFileTableView(QTableView):
    entry_selected = Signal(QModelIndex)
    
    def __init__(self, model: POFileTableModel, parent: Optional[QWidget] = None)
    def setup_appearance(self) -> None
    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None
    def contextMenuEvent(self, event: QContextMenuEvent) -> None
    def keyPressEvent(self, event: QKeyEvent) -> None
    
    # Navigation methods
    def select_next_entry(self) -> bool
    def select_previous_entry(self) -> bool
    def select_first_entry(self) -> bool
    def select_last_entry(self) -> bool
    def select_entry(self, row: int) -> bool
    
    # Custom selection methods
    def select_next_untranslated(self) -> bool
    def select_next_fuzzy(self) -> bool
    def select_next_with_issues(self) -> bool
```

### 4.3 TranslationEditorPanel

**Purpose**: Provides the interface for editing translations with source text reference.

**Key Features**:
- Side-by-side display of source and translation
- Rich text editing with syntax highlighting
- Fuzzy flag toggle for marking uncertain translations
- Comments editor for translator notes
- Text replacement integration
- Spell checking with underlines
- Real-time validation

**Implementation Details**:
```python
class TranslationEditorPanel(QWidget):
    translation_changed = Signal(str)
    fuzzy_changed = Signal(bool)
    comments_changed = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None)
    def setup_ui(self) -> None
    
    def set_entry(self, entry: Optional[POEntry]) -> None
    def get_translation(self) -> str
    def set_translation(self, text: str) -> None
    def get_fuzzy(self) -> bool
    def set_fuzzy(self, fuzzy: bool) -> None
    def get_comments(self) -> str
    def set_comments(self, text: str) -> None
    
    # Event handlers
    def on_translation_edited(self) -> None
    def on_fuzzy_toggled(self, checked: bool) -> None
    def on_comments_edited(self) -> None
```

### 4.4 NavigationBar

**Purpose**: Provides paging and navigation controls for the PO entry table.

**Key Features**:
- Page navigation controls (First, Previous, Next, Last)
- Current page indicator
- Page size configuration
- Entry count display
- Visual progress indicator

**Implementation Details**:
```python
class NavigationBar(QWidget):
    page_changed = Signal(int)
    page_size_changed = Signal(int)
    
    def __init__(self, parent: Optional[QWidget] = None)
    def setup_ui(self) -> None
    
    # Navigation methods
    def go_to_first_page(self) -> None
    def go_to_previous_page(self) -> None
    def go_to_next_page(self) -> None
    def go_to_last_page(self) -> None
    def go_to_page(self, page: int) -> None
    
    # State management
    def set_total_entries(self, count: int) -> None
    def set_page_size(self, size: int) -> None
    def update_page_info(self) -> None
```

### 4.5 FindReplaceBar

**Purpose**: Provides search and replace functionality within the PO file.

**Key Features**:
- Search in source text, translation, or both
- Regular expression support
- Case sensitivity toggle
- Word boundary matching
- Replace operations (single/all)
- Search result navigation

**Implementation Details**:
```python
class FindReplaceBar(QWidget):
    find_requested = Signal(FindReplaceRequest)
    replace_requested = Signal(FindReplaceRequest)
    replace_all_requested = Signal(FindReplaceRequest)
    close_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None)
    def setup_ui(self) -> None
    
    # Search operations
    def find_next(self) -> None
    def find_previous(self) -> None
    def replace_current(self) -> None
    def replace_all(self) -> None
    
    # State management
    def update_result_count(self, count: int) -> None
    def clear_search(self) -> None
```

## 5. Workflow Scenarios

### 5.1 File Loading Workflow

1. User triggers file open (via command or explorer)
2. POEditorTab constructor called with file path
3. `load_file()` method reads PO file
4. POFileTableModel populated with entries
5. Select first entry and update editor panel
6. Update navigation bar with page information
7. Set modified state to false

### 5.2 Entry Editing Workflow

1. User selects entry in table
2. TranslationEditorPanel populated with entry data
3. User edits translation in editor
4. translation_changed signal emitted
5. Model updated with new translation
6. Set modified state to true
7. Entry row highlighted to show changes

### 5.3 Save Workflow

1. User triggers save command
2. `save()` method called
3. Modified entries written to file
4. Set modified state to false
5. Update status information

### 5.4 Find/Replace Workflow

1. User triggers find command (Ctrl+F)
2. FindReplaceBar shown at top of tab
3. User enters search criteria
4. find_requested signal emitted
5. Search results processed and highlighted
6. User navigates between matches
7. Replace operations update entries and model

## 6. Integration Points

### 6.1 Plugin API Integration

```python
# In POEditor plugin registration
def register(api: PluginAPI) -> None:
    # Register tab type for PO files
    api.register_tab_type(
        file_extensions=[".po", ".pot"],
        create_tab=lambda path: POEditorTab(path, api),
        icon=QIcon(":/icons/poeditor.svg"),
        tab_type="poeditor"
    )
    
    # Register commands
    api.register_command("poeditor.find", lambda: show_find_dialog())
    api.register_command("poeditor.save", lambda: save_current_tab())
    api.register_command("poeditor.next_untranslated", lambda: goto_next_untranslated())
```

### 6.2 Service Integration

```python
# In POEditorTab constructor
def __init__(self, file_path: str, api: PluginAPI, parent: Optional[QWidget] = None):
    super().__init__(parent)
    self.api = api
    self.file_path = file_path
    
    # Get required services
    self.db_service = api.get_service("translation_db")
    self.replacement_service = api.get_service("text_replacement")
    self.qa_service = api.get_service("quality_assurance")
```

### 6.3 Settings Integration

```python
# Loading settings in POEditorTab
def load_settings(self) -> None:
    settings = QSettings("POEditor", "Settings")
    
    # Editor settings
    self.page_size = settings.value("editor/page_size", 50, int)
    self.navigation_bar.set_page_size(self.page_size)
    
    # Font settings
    msgid_font = QFont()
    msgid_font.fromString(settings.value("fonts/msgid_font", ""))
    self.editor_panel.set_source_font(msgid_font)
    
    msgstr_font = QFont()
    msgstr_font.fromString(settings.value("fonts/msgstr_font", ""))
    self.editor_panel.set_translation_font(msgstr_font)
```

### 6.4 Event System Integration

```python
# Subscribe to events
self.api.subscribe_event("settings.changed", self.on_settings_changed)
self.api.subscribe_event("search.find_in_tab", self.on_find_in_tab)
self.api.subscribe_event("qa.check_requested", self.on_qa_check_requested)

# Emit events
self.api.emit_event("poeditor.entry_selected", entry_id=entry.msgid)
self.api.emit_event("poeditor.translation_updated", entry_id=entry.msgid, text=text)
```

## 7. Quality Assurance Integration

### 7.1 Issue Detection

**Issue Types**:
1. Empty translations
2. Fuzzy translations
3. Untranslated entries (msgid == msgstr)
4. Missing context fields
5. Unresolved placeholders
6. Format string mismatches
7. Custom validation rules

**Integration**:
```python
# In POEditorTab
def check_issues(self) -> None:
    qa_service = self.api.get_service("quality_assurance")
    if not qa_service:
        return
    
    for row in range(self.model.rowCount()):
        entry = self.model.get_entry_by_row(row)
        issues = qa_service.check_entry(entry)
        
        # Update model with issue status
        if issues:
            self.model.set_issues(row, issues)
```

### 7.2 Visual Indicators

1. Pink highlighting for entries with issues
2. Status bar information about issue counts
3. Issue tooltips with problem descriptions
4. Navigation to next/previous issue

## 8. Performance Considerations

### 8.1 Lazy Loading

For large PO files, implement lazy loading of entries:

```python
class LazyPOFileLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.total_entries = 0
        self.loaded = False
        
    def get_entry_count(self) -> int:
        if not self.total_entries:
            self._count_entries()
        return self.total_entries
        
    def load_page(self, page: int, page_size: int) -> List[POEntry]:
        # Load only entries for the current page
        start_idx = page * page_size
        end_idx = start_idx + page_size
        return self._load_entries_range(start_idx, end_idx)
```

### 8.2 Background Processing

```python
class BackgroundTask(QRunnable):
    def __init__(self, callback, *args, **kwargs):
        super().__init__()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            result = self.callback(*self.args, **self.kwargs)
            QMetaObject.invokeMethod(
                self.parent, "handle_task_result",
                Qt.QueuedConnection, Q_ARG(object, result)
            )
        except Exception as e:
            QMetaObject.invokeMethod(
                self.parent, "handle_task_error",
                Qt.QueuedConnection, Q_ARG(Exception, e)
            )

# In POEditorTab
def load_file_async(self, file_path: str) -> None:
    task = BackgroundTask(self._load_file_worker, file_path)
    QThreadPool.globalInstance().start(task)
```

## 9. Error Handling

### 9.1 File Operation Errors

```python
def load_file(self, file_path: str) -> bool:
    try:
        # File loading logic
        return True
    except FileNotFoundError:
        self.show_error("File not found", f"The file {file_path} could not be found.")
        return False
    except Exception as e:
        self.show_error("Error loading file", f"Failed to load {file_path}: {str(e)}")
        logger.error(f"Error loading PO file: {e}", exc_info=True)
        return False
```

### 9.2 UI Error Feedback

```python
def show_error(self, title: str, message: str) -> None:
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.critical(self, title, message)
```

## 10. Settings and Configuration

### 10.1 Editor Settings

- **Page Size**: Number of entries per page
- **Table Column Widths**: Customizable column sizes
- **Table Font**: Font for table display
- **Auto-save**: Enable/disable automatic saving
- **Entry Display**: Control what fields are visible

### 10.2 Editing Settings

- **Source Font**: Font for source text display
- **Translation Font**: Font for translation editor
- **Spell Checking**: Enable/disable spell checking
- **Auto-replacement**: Enable/disable text replacement
- **Validation**: Control real-time validation

### 10.3 Navigation Settings

- **Skip Empty**: Skip empty entries during navigation
- **Default Navigation**: Set preferred navigation mode
- **Selection Behavior**: Row vs. cell selection
- **Navigation Controls**: Show/hide navigation bar

## 11. Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| Find | Ctrl+F | Show find bar |
| Save | Ctrl+S | Save current file |
| Next Entry | Ctrl+Down | Move to next entry |
| Previous Entry | Ctrl+Up | Move to previous entry |
| Next Page | Ctrl+PageDown | Move to next page |
| Previous Page | Ctrl+PageUp | Move to previous page |
| Next Untranslated | Ctrl+U | Jump to next untranslated entry |
| Next Fuzzy | Ctrl+F | Jump to next fuzzy entry |
| Next Issue | Ctrl+I | Jump to next entry with issues |
| Toggle Fuzzy | Ctrl+Shift+F | Toggle fuzzy flag for current entry |
| Focus Translation | F2 | Focus the translation editor |
| Focus Source | F1 | Focus the source text display |

## 12. Future Enhancements

### 12.1 Advanced Editing Features

- Side-by-side diff view for version comparison
- In-context preview of translated strings
- Machine translation integration
- Translation memory suggestions

### 12.2 Collaboration Features

- Comment threads for translator notes
- Change tracking with attribution
- Shared translation memory
- Export/import for team sharing

### 12.3 Quality Improvements

- Custom validation rule editor
- Visual quality score indicators
- Automated consistency checking
- Linguistic validation tools

## 13. Testing Strategy

### 13.1 Unit Tests

- Model data handling and updates
- Navigation logic
- Find/replace operations
- File loading and saving

### 13.2 Integration Tests

- Plugin API integration
- Settings persistence
- Event handling
- Service interaction

### 13.3 UI Tests

- User interaction flows
- Keyboard navigation
- Visual feedback
- Accessibility testing

## 14. Conclusion

The POEditor Tab Component provides a comprehensive, efficient interface for PO file translation that integrates seamlessly with the plugin-based architecture. By leveraging the robust functionality of the original POEditor while adapting it to the new plugin system, this component delivers a professional translation experience with advanced editing features, quality assurance tools, and performance optimizations.
