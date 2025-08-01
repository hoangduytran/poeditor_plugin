# POEditor Tab Widget Design

## Overview
This document details the design for the POEditorTab widget, which is a refactored version of the original POEditorWindow that can be used as a tab in the plugin-based architecture.

## Current Implementation Analysis
Based on the old_codes/main_gui.py, the current POEditor implementation has:
- Complex table-based editing interface
- Find/replace functionality
- Translation editing with text widgets
- Database integration for PO entries
- Taskbar and navigation components

## POEditorTab Design

### Class Structure
```python
class POEditorTab(QWidget):
    """
    A tab widget for editing PO files, refactored from POEditorWindow
    """
    # Signals
    modified_changed = Signal(bool)
    title_changed = Signal(str)
    status_changed = Signal(str)
    
    def __init__(self, file_path: str, parent: Optional[QWidget] = None)
    def setup_ui(self) -> None
    def load_po_file(self, file_path: str) -> bool
    def save(self) -> bool
    def save_as(self, file_path: str) -> bool
    def can_close(self) -> bool
    def get_modified(self) -> bool
    def set_modified(self, modified: bool) -> None
```

### Core Components

#### 1. PO File Model
```python
class POEditorModel(QAbstractTableModel):
    """
    Table model for PO entries with support for:
    - Source text display
    - Translation editing
    - Entry status (translated, fuzzy, untranslated)
    - Comments and context
    """
    def __init__(self, po_file_path: str)
    def get_entry(self, index: QModelIndex) -> Optional[POEntry]
    def update_translation(self, row: int, translation: str) -> None
    def mark_entry_fuzzy(self, row: int, fuzzy: bool) -> None
```

#### 2. Main Layout Components
```python
def setup_ui(self) -> None:
    """
    Creates the main layout with:
    - Top toolbar for file operations
    - Main splitter (horizontal)
      - Left: Entry table view
      - Right: Translation editor panel
    - Bottom status bar
    """
```

#### 3. Entry Table View
```python
class POEntryTableView(QTableView):
    """
    Specialized table view for PO entries with:
    - Custom rendering for entry status
    - Context menu for entry operations
    - Keyboard navigation
    - Search highlighting
    """
    entry_selected = Signal(int)  # row index
    
    def __init__(self, model: POEditorModel)
    def select_entry(self, row: int) -> None
    def get_selected_entry(self) -> Optional[int]
    def contextMenuEvent(self, event: QContextMenuEvent) -> None
```

#### 4. Translation Editor Panel
```python
class TranslationEditorPanel(QWidget):
    """
    Right panel for editing translations with:
    - Source text display (read-only)
    - Translation text editor
    - Entry metadata (context, comments)
    - Entry status controls
    """
    translation_changed = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None)
    def set_entry(self, entry: Optional[POEntry]) -> None
    def get_translation(self) -> str
    def set_translation(self, text: str) -> None
```

### Integration Points

#### 1. Plugin API Integration
```python
def register_poeditor_tab_type(api: PluginAPI):
    """Register POEditor as a tab type that can be created by plugins"""
    
    def create_po_tab(file_path: str) -> POEditorTab:
        return POEditorTab(file_path)
    
    api.register_tab_type("po_editor", create_po_tab, [".po", ".pot"])
```

#### 2. Service Dependencies
- **DatabaseService**: For PO file loading and saving
- **ConfigService**: For editor preferences
- **SearchService**: For find/replace operations
- **TranslationService**: For auto-translation features

#### 3. Event Integration
```python
# Events emitted by POEditorTab
api.emit_event("po_editor.file_opened", file_path=self.file_path)
api.emit_event("po_editor.entry_selected", entry_id=entry.msgid)
api.emit_event("po_editor.translation_updated", entry_id=entry.msgid, new_text=translation)
api.emit_event("po_editor.file_modified", file_path=self.file_path, modified=True)

# Events subscribed by POEditorTab
api.subscribe_event("search.find_in_file", self.handle_find_request)
api.subscribe_event("search.replace_in_file", self.handle_replace_request)
```

### Reusable Components from Old Code

#### 1. POFileTableModel
Location: `old_codes/main_utils/po_ed_table_model.py`
- Reuse with minimal modifications
- Add plugin API integration
- Ensure thread safety

#### 2. TranslationEditorWidget
Location: `old_codes/subcmp/translation_edit_widget.py`
- Refactor to work as a component
- Remove window dependencies
- Add signal-based communication

#### 3. Find/Replace Components
Location: `old_codes/main_utils/find_replace_action.py`
- Extract into separate service
- Make accessible via plugin API
- Add event-based integration

#### 4. Database Components
Location: `old_codes/main_utils/`
- Refactor into database service
- Provide async loading capabilities
- Add caching support

### Tab Lifecycle

#### 1. Creation
```python
def __init__(self, file_path: str, parent: Optional[QWidget] = None):
    super().__init__(parent)
    self.file_path = file_path
    self.is_modified = False
    self.po_entries = []
    
    self.setup_ui()
    self.load_po_file(file_path)
    self.connect_signals()
```

#### 2. File Loading
```python
def load_po_file(self, file_path: str) -> bool:
    try:
        # Use database service to load PO file
        db_service = self.api.get_service("database")
        self.po_entries = db_service.load_po_file(file_path)
        
        # Update model
        self.model.set_entries(self.po_entries)
        
        # Update UI state
        self.set_modified(False)
        self.title_changed.emit(os.path.basename(file_path))
        
        return True
    except Exception as e:
        logger.error(f"Failed to load PO file {file_path}: {e}")
        return False
```

#### 3. Saving
```python
def save(self) -> bool:
    if not self.file_path:
        return self.save_as()
    
    try:
        # Use database service to save
        db_service = self.api.get_service("database")
        db_service.save_po_file(self.file_path, self.po_entries)
        
        self.set_modified(False)
        self.api.emit_event("po_editor.file_saved", file_path=self.file_path)
        
        return True
    except Exception as e:
        logger.error(f"Failed to save PO file {self.file_path}: {e}")
        return False
```

#### 4. Closing
```python
def can_close(self) -> bool:
    if not self.is_modified:
        return True
    
    # Show save dialog
    from PySide6.QtWidgets import QMessageBox
    
    reply = QMessageBox.question(
        self,
        "Unsaved Changes",
        f"Save changes to {os.path.basename(self.file_path)}?",
        QMessageBox.StandardButton.Save | 
        QMessageBox.StandardButton.Discard | 
        QMessageBox.StandardButton.Cancel
    )
    
    if reply == QMessageBox.StandardButton.Save:
        return self.save()
    elif reply == QMessageBox.StandardButton.Discard:
        return True
    else:
        return False
```

### Advanced Features

#### 1. Find and Replace Integration
```python
def handle_find_request(self, find_request: FindReplaceRequest):
    """Handle find/replace requests from search plugin"""
    
    results = []
    for i, entry in enumerate(self.po_entries):
        # Search in source text
        if find_request.scope.include_source:
            matches = find_matches(entry.msgid, find_request.pattern)
            for match in matches:
                results.append(FindReplaceResult(
                    file_path=self.file_path,
                    line_number=i,
                    column=match.start,
                    match_text=match.text,
                    context="source"
                ))
        
        # Search in translation
        if find_request.scope.include_translation:
            matches = find_matches(entry.msgstr, find_request.pattern)
            for match in matches:
                results.append(FindReplaceResult(
                    file_path=self.file_path,
                    line_number=i,
                    column=match.start,
                    match_text=match.text,
                    context="translation"
                ))
    
    # Emit results
    self.api.emit_event("search.results_found", results=results)
```

#### 2. Auto-Translation Integration
```python
def setup_auto_translation(self):
    """Setup auto-translation features using translation service"""
    
    translation_service = self.api.get_service("translation")
    if not translation_service:
        return
    
    # Add auto-translate button to translation editor
    def auto_translate_current():
        entry = self.get_current_entry()
        if entry and not entry.msgstr:
            translated = translation_service.translate(
                entry.msgid,
                source_lang="en",
                target_lang=self.get_target_language()
            )
            self.set_current_translation(translated)
    
    self.translation_editor.add_auto_translate_button(auto_translate_current)
```

#### 3. Version History Integration
```python
def setup_version_history(self):
    """Setup integration with translation history service"""
    
    history_service = self.api.get_service("translation_history")
    if not history_service:
        return
    
    def on_translation_changed(entry_id: str, new_translation: str):
        # Save to history
        history_service.save_translation_version(
            file_path=self.file_path,
            entry_id=entry_id,
            translation=new_translation,
            timestamp=datetime.now()
        )
    
    self.translation_changed.connect(on_translation_changed)
```

### Error Handling

#### 1. File Loading Errors
- Graceful handling of corrupted PO files
- User-friendly error messages
- Fallback to read-only mode if needed

#### 2. Save Errors
- Backup creation before saving
- Retry mechanisms
- User notification and options

#### 3. Service Unavailability
- Graceful degradation when services unavailable
- Basic functionality without optional services
- Clear user feedback about limited functionality

### Performance Considerations

#### 1. Large File Handling
- Lazy loading of PO entries
- Virtual table view for large files
- Background loading with progress indication

#### 2. Memory Management
- Efficient model updates
- Proper cleanup on tab close
- Weak references where appropriate

#### 3. UI Responsiveness
- Non-blocking file operations
- Progress feedback for long operations
- Background processing where possible

### Testing Strategy

#### 1. Unit Tests
- POEditorModel functionality
- Translation editor components
- File loading and saving logic

#### 2. Integration Tests
- Plugin API integration
- Service interaction
- Event handling

#### 3. UI Tests
- User interaction scenarios
- Keyboard navigation
- Context menu functionality

### Migration Path

#### Phase 1: Core Widget
1. Extract and refactor POEditorWindow to POEditorTab
2. Remove window-specific dependencies
3. Add basic plugin API integration

#### Phase 2: Service Integration
1. Integrate with database service
2. Add search service integration
3. Connect to configuration service

#### Phase 3: Advanced Features
1. Add auto-translation support
2. Integrate version history
3. Add performance optimizations

#### Phase 4: Polish
1. Comprehensive testing
2. Documentation
3. Performance tuning
