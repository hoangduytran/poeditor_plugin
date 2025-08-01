# POEditor UI Design Specification

**Date**: August 1, 2025  
**Component**: POEditor Tab UI Design  
**Status**: Planning

## 1. Overview

This document outlines the detailed design specifications for the POEditor tab UI component. The POEditor tab serves as the main interface for translating PO files, providing a table view of entries alongside a powerful translation editor. The design aims to combine the proven usability of the original POEditor application with the flexibility of the new plugin architecture.

## 2. UI Layout

The POEditor tab uses a vertical split layout with the following main components:

```
┌─────────────────────────────────────────────────────────┐
│ Toolbar (File operations, Navigation, Filter)           │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ PO Entry Table                                      │ │
│ │ ┌───────┬────────────────┬────────────┬──────────┐ │ │
│ │ │ ID    │ Source Text    │ Translation │ Status   │ │ │
│ │ ├───────┼────────────────┼────────────┼──────────┤ │ │
│ │ │ 1     │ Hello World    │ Hola Mundo │ Approved │ │ │
│ │ │ 2     │ Goodbye        │ Adiós      │ Needs Rev│ │ │
│ │ │ ...   │ ...            │ ...        │ ...      │ │ │
│ │ └───────┴────────────────┴────────────┴──────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
│ <Splitter Handle>                                       │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Translation Editor Panel                            │ │
│ │ ┌─────────────────────────────────────────────────┐ │ │
│ │ │ Source: Hello World                             │ │ │
│ │ ├─────────────────────────────────────────────────┤ │ │
│ │ │ Translation:                                    │ │ │
│ │ │ ┌─────────────────────────────────────────────┐ │ │ │
│ │ │ │ Hola Mundo                                  │ │ │ │
│ │ │ └─────────────────────────────────────────────┘ │ │ │
│ │ ├─────────────────────────────────────────────────┤ │ │
│ │ │ Context: Main screen greeting                   │ │ │
│ │ │ Comments: Displayed on application startup      │ │ │
│ │ ├─────────────────────────────────────────────────┤ │ │
│ │ │ Suggestions:                                    │ │ │
│ │ │ 1. Hola Mundo (5 uses)                          │ │ │
│ │ │ 2. Saludos Mundo (2 uses)                       │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Status Bar (Statistics, Current Entry Info)             │
└─────────────────────────────────────────────────────────┘
```

## 3. Component Specifications

### 3.1 Toolbar

The toolbar provides quick access to common operations:

**Layout**: Horizontal icon-based toolbar with text labels
**Position**: Top of the POEditor tab
**Height**: 40px (with appropriate scaling)

**Elements**:
1. **File Operations Group**:
   - Open PO File
   - Save
   - Save As
   - Export (dropdown menu)

2. **Navigation Group**:
   - Previous Entry
   - Next Entry
   - Go to Entry... (input field)
   - First Untranslated

3. **Filter Group**:
   - Filter dropdown (All, Untranslated, Fuzzy, Approved)
   - Search field with options button

4. **Tools Group**:
   - Quality Check
   - Auto-translate
   - Translation Memory
   - Settings

**Implementation Class**: `POEditorToolbar(QToolBar)`

### 3.2 PO Entry Table

The table displays all translation entries in the PO file:

**Layout**: Table view with configurable columns
**Position**: Upper pane of splitter
**Default Height**: 60% of available space

**Columns**:
1. **ID**: Entry number/identifier
2. **Source**: Source text (with optional plural forms)
3. **Translation**: Translated text
4. **Context**: Optional context information
5. **Status**: Translation status (Untranslated, Needs Review, Approved)
6. **Comments**: Optional translator comments
7. **Flags**: Special flags for the entry

**Features**:
- Horizontal scrolling for long entries
- Custom delegates for different column types
- Color-coding based on translation status
- In-place editing for translation column
- Multi-selection capability
- Column visibility toggle
- Sorting by any column
- Custom filtering

**Implementation Classes**:
- `POFileTableView(QTableView)`
- `POFileTableModel(QAbstractTableModel)`
- `POEntryDelegate(QStyledItemDelegate)`

### 3.3 Translation Editor Panel

The editor panel provides detailed editing of the selected entry:

**Layout**: Vertical sections with expandable panels
**Position**: Lower pane of splitter
**Default Height**: 40% of available space

**Sections**:
1. **Source Text Display**:
   - Read-only display of source text
   - Syntax highlighting for format specifiers
   - Plural form tabs if applicable

2. **Translation Editor**:
   - Rich text editor for translation
   - Spell checking
   - Format specifier validation
   - Plural form tabs if applicable

3. **Metadata Panel**:
   - Context information
   - Translator comments
   - Source code references
   - Status selection

4. **Suggestions Panel**:
   - Translation memory suggestions
   - Previous translations
   - Machine translations

**Features**:
- Format specifier highlighting
- Keyboard shortcuts for navigation
- Text formatting controls
- Auto-completion
- Inline validation
- Click-to-insert suggestions

**Implementation Class**: `TranslationEditorPanel(QWidget)`

### 3.4 Status Bar

The status bar provides summary information about the file and current entry:

**Layout**: Horizontal bar with sections
**Position**: Bottom of POEditor tab
**Height**: 24px (with appropriate scaling)

**Sections**:
1. **File Information**: Filename, total entries
2. **Statistics**: Translated %, Needs review %, Untranslated %
3. **Current Entry**: Entry ID, status
4. **Validation Status**: Any issues with current entry

**Implementation Class**: `POEditorStatusBar(QStatusBar)`

## 4. Interaction Design

### 4.1 Table Selection

When a user selects an entry in the table:
1. The selected row is highlighted
2. Translation editor is populated with the entry data
3. Suggestions are asynchronously loaded
4. Current entry information is updated in status bar

### 4.2 Translation Editing

When a user edits a translation:
1. Changes are immediately reflected in the model
2. Format specifiers are validated in real-time
3. Status is updated (e.g., to "Needs Review")
4. File is marked as modified
5. History is recorded in the database

### 4.3 Navigation

Users can navigate between entries using:
1. Table selection (click)
2. Next/Previous buttons
3. Keyboard shortcuts (Tab, Shift+Tab, Alt+Up, Alt+Down)
4. Go to Entry field

### 4.4 Filtering and Sorting

Users can filter and sort entries:
1. Filter dropdown selects predefined filters
2. Search field filters by text content
3. Column headers allow sorting
4. Advanced filter dialog for complex conditions

## 5. Visual Design

### 5.1 Color Scheme

The POEditor uses a consistent color scheme that integrates with the application theme:

**Status Colors**:
- Untranslated: Light red background (#FFEEEE)
- Needs Review: Light yellow background (#FFFFEE)
- Approved: Light green background (#EEFFEE)

**Highlight Colors**:
- Format specifiers: Blue text (#0000CC)
- Errors: Red underline
- Selected row: Application highlight color

### 5.2 Typography

The POEditor uses consistent typography:

- Table: System font, 10pt (configurable)
- Source/Translation: Monospace font, 11pt (configurable)
- Metadata: System font, 9pt

### 5.3 Icons

The POEditor uses consistent iconography:

- Standard file operation icons from theme
- Navigation icons (arrows, markers)
- Status icons (check, warning, error)
- Custom icons for translation-specific operations

## 6. Implementation Details

### 6.1 POEditorTab Class

```python
class POEditorTab(QWidget, TabInterface):
    """Main POEditor tab component that implements the TabInterface."""
    
    fileModified = Signal()  # Emitted when file is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_path = None
        self._is_modified = False
        
        # Setup UI components
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = POEditorToolbar()
        layout.addWidget(self.toolbar)
        
        # Splitter
        self.splitter = QSplitter(Qt.Vertical)
        
        # Table view
        self.table_view = POFileTableView()
        self.table_model = POFileTableModel()
        self.table_view.setModel(self.table_model)
        
        # Editor panel
        self.editor_panel = TranslationEditorPanel()
        
        # Add to splitter
        self.splitter.addWidget(self.table_view)
        self.splitter.addWidget(self.editor_panel)
        
        # Set default sizes
        self.splitter.setSizes([int(self.height() * 0.6), int(self.height() * 0.4)])
        
        layout.addWidget(self.splitter)
        
        # Status bar
        self.status_bar = POEditorStatusBar()
        layout.addWidget(self.status_bar)
    
    def _connect_signals(self):
        # Connect selection changes
        self.table_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        
        # Connect editor changes
        self.editor_panel.translationChanged.connect(
            self._on_translation_changed
        )
        
        # Connect toolbar actions
        self.toolbar.openFileRequested.connect(self._on_open_file)
        self.toolbar.saveRequested.connect(self.save_file)
        self.toolbar.saveAsRequested.connect(self._on_save_as)
        self.toolbar.nextEntryRequested.connect(self._go_to_next_entry)
        self.toolbar.prevEntryRequested.connect(self._go_to_prev_entry)
        self.toolbar.filterChanged.connect(self._apply_filter)
        
        # Connect model signals
        self.table_model.dataChanged.connect(self._on_data_changed)
    
    # TabInterface implementation
    def file_path(self):
        return self._file_path
    
    def set_file_path(self, path):
        self._file_path = path
        file_name = os.path.basename(path) if path else "Untitled"
        self.status_bar.setFileName(file_name)
    
    def is_modified(self):
        return self._is_modified
    
    def save(self):
        if self._file_path:
            return self._save_to_path(self._file_path)
        return False
    
    def save_as(self, path):
        return self._save_to_path(path)
    
    # POEditor specific methods
    def load_file(self, path):
        try:
            self.table_model.loadFromFile(path)
            self.set_file_path(path)
            self._is_modified = False
            self._update_statistics()
            return True
        except Exception as e:
            lg.error(f"Failed to load file: {e}")
            return False
    
    def _save_to_path(self, path):
        try:
            self.table_model.saveToFile(path)
            self.set_file_path(path)
            self._is_modified = False
            return True
        except Exception as e:
            lg.error(f"Failed to save file: {e}")
            return False
    
    def _on_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            return
            
        # Get the row of the first selected item
        row = indexes[0].row()
        
        # Get the entry data
        entry = self.table_model.entry(row)
        if entry:
            # Update the editor panel
            self.editor_panel.setEntry(entry)
            
            # Update status bar
            self.status_bar.setCurrentEntry(row + 1, len(self.table_model))
            
            # Load suggestions asynchronously
            self._load_suggestions(entry)
    
    def _on_translation_changed(self, new_translation):
        indexes = self.table_view.selectionModel().selectedIndexes()
        if not indexes:
            return
            
        # Get the row of the first selected item
        row = indexes[0].row()
        
        # Update the model
        translation_index = self.table_model.index(row, 
                                                  POFileTableModel.COLUMN_TRANSLATION)
        self.table_model.setData(translation_index, new_translation)
    
    def _on_data_changed(self, topLeft, bottomRight):
        # Mark file as modified
        if not self._is_modified:
            self._is_modified = True
            self.fileModified.emit()
        
        # Update statistics
        self._update_statistics()
    
    def _update_statistics(self):
        stats = self.table_model.statistics()
        self.status_bar.setStatistics(stats)
    
    def _load_suggestions(self, entry):
        # Get database service from plugin manager
        db_service = plugin_manager.get_service("translation_database")
        if db_service:
            db_service.get_suggestions_async(
                entry.source,
                entry.context,
                5  # Limit to 5 suggestions
            )
            
            # Connect to suggestions result
            db_service.suggestionsFetched.connect(
                self.editor_panel.setSuggestions
            )
    
    def _go_to_next_entry(self):
        current = self.table_view.currentIndex()
        if not current.isValid():
            # Select first row if nothing selected
            self.table_view.selectRow(0)
            return
            
        next_row = current.row() + 1
        if next_row < self.table_model.rowCount():
            self.table_view.selectRow(next_row)
    
    def _go_to_prev_entry(self):
        current = self.table_view.currentIndex()
        if not current.isValid():
            return
            
        prev_row = current.row() - 1
        if prev_row >= 0:
            self.table_view.selectRow(prev_row)
```

### 6.2 POEditorToolbar Class

```python
class POEditorToolbar(QToolBar):
    """Toolbar for the POEditor tab."""
    
    openFileRequested = Signal()
    saveRequested = Signal()
    saveAsRequested = Signal()
    nextEntryRequested = Signal()
    prevEntryRequested = Signal()
    filterChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(16, 16))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self._setup_actions()
    
    def _setup_actions(self):
        # File operations
        self.open_action = QAction(
            QIcon.fromTheme("document-open"),
            "Open",
            self
        )
        self.open_action.triggered.connect(self.openFileRequested)
        
        self.save_action = QAction(
            QIcon.fromTheme("document-save"),
            "Save",
            self
        )
        self.save_action.triggered.connect(self.saveRequested)
        
        self.save_as_action = QAction(
            QIcon.fromTheme("document-save-as"),
            "Save As",
            self
        )
        self.save_as_action.triggered.connect(self.saveAsRequested)
        
        # Navigation
        self.prev_action = QAction(
            QIcon.fromTheme("go-previous"),
            "Previous",
            self
        )
        self.prev_action.triggered.connect(self.prevEntryRequested)
        
        self.next_action = QAction(
            QIcon.fromTheme("go-next"),
            "Next",
            self
        )
        self.next_action.triggered.connect(self.nextEntryRequested)
        
        # Filter
        self.filter_combo = QComboBox(self)
        self.filter_combo.addItem("All Entries")
        self.filter_combo.addItem("Untranslated")
        self.filter_combo.addItem("Needs Review")
        self.filter_combo.addItem("Translated")
        self.filter_combo.currentTextChanged.connect(self.filterChanged)
        
        # Add actions to toolbar
        self.addAction(self.open_action)
        self.addAction(self.save_action)
        self.addAction(self.save_as_action)
        self.addSeparator()
        self.addAction(self.prev_action)
        self.addAction(self.next_action)
        self.addSeparator()
        self.addWidget(self.filter_combo)
```

## 7. Configuration Options

The POEditor tab supports the following configuration options:

### 7.1 Table Display Options

- **Visible Columns**: Which columns to show in the table
- **Column Width**: Custom width for each column
- **Row Height**: Custom row height
- **Font**: Font family and size for table text
- **Status Colors**: Custom colors for different status types
- **Alternating Row Colors**: Toggle for alternating background colors

### 7.2 Editor Options

- **Font**: Font family and size for editor text
- **Spell Check**: Enable/disable spell checking
- **Auto-validation**: Enable/disable format specifier validation
- **Auto-suggestions**: Enable/disable automatic suggestions
- **Editor Height**: Default height for editor panel

### 7.3 Navigation Options

- **Auto-advance**: Automatically move to next entry after translation
- **Cycle Navigation**: Wrap around to first/last entry when navigating
- **Skip Translated**: Skip already translated entries when navigating

## 8. Integration Points

The POEditor tab integrates with several other components:

### 8.1 Plugin Manager

- Register file type associations for PO files
- Register commands for POEditor operations
- Get services (database, QA, settings)

### 8.2 Tab Manager

- Register as a tab provider
- Handle tab lifecycle events

### 8.3 Settings Manager

- Store and retrieve configuration options
- Listen for settings changes

### 8.4 File System Service

- Open and save PO files
- Handle file change notifications

### 8.5 Translation Database Service

- Store translations
- Retrieve translation suggestions
- Browse translation history

## 9. Testing Strategy

### 9.1 Unit Tests

- Test model data manipulation
- Test file loading/saving
- Test table filtering and sorting
- Test navigation functions

### 9.2 Integration Tests

- Test interaction between table and editor
- Test database integration
- Test settings integration
- Test plugin manager integration

### 9.3 UI Tests

- Test keyboard navigation
- Test mouse interactions
- Test accessibility features

## 10. Conclusion

This design document provides comprehensive specifications for implementing the POEditor tab UI component. By following this design, we ensure a consistent and powerful user experience that maintains compatibility with the original application while leveraging the new plugin architecture.
