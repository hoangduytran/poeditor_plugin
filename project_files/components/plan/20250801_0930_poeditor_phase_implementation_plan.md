# POEditor Phase Implementation Plan

**Date**: August 1, 2025  
**Component**: POEditor Plugin - Phase Implementation  
**Status**: Planning

## 1. Current Status Assessment

Based on the master plan and existing components, we have identified the following implementation status:

| Component | Status | Notes |
|-----------|--------|-------|
| Plugin Framework | Complete | Base plugin architecture is implemented |
| Tab Management | Partial | Basic integration exists but POEditor tab needs work |
| POEditor UI | Not Started | Main focus of next phase |
| Translation DB | Partial | Schema defined but integration incomplete |
| Settings Panels | Partial | Framework exists, POEditor panels needed |
| Quality Assurance | Not Started | To be implemented in later phases |

## 2. Phase Priority Adjustments

Given the current state of the project, we recommend the following adjusted phase priorities:

### Phase 2A: Core POEditor UI Component (4 weeks)
**Focus**: Implement the main POEditor interface with table view and translation editor

**Key Deliverables**:
1. POEditorTab component with split layout (table view + editor)
2. Integration with existing table model and entry delegate
3. Translation editor with formatting capabilities
4. Navigation controls for moving between entries
5. Status display and metadata panel
6. Unit tests for UI components

### Phase 2B: File Operations Integration (2 weeks)
**Focus**: Connect the POEditor with file operations

**Key Deliverables**:
1. Open/Save/Save As functionality for PO files
2. File format validation and error handling
3. Export options (filtered exports, formats)
4. New file creation and templates
5. Auto-save and recovery features

### Phase 3: Translation Database Integration (3 weeks)
**Focus**: Complete the integration with the translation database service

**Key Deliverables**:
1. Complete DatabaseService implementation
2. Translation history panel in the editor
3. Suggestion mechanism based on previous translations
4. Translation memory integration
5. Statistics and reporting capabilities
6. Performance optimization for large databases

## 3. Component Integration Specifications

### 3.1 POEditor Tab Component

The POEditor Tab will serve as the main interface for translation work. Based on the screenshot and old application, it requires:

#### Layout Structure
```
POEditorTab
├── TopToolbar (file operations, navigation, filter)
├── SplitView
│   ├── UpperPane: POFileTableView
│   │   ├── Column: Source Text
│   │   ├── Column: Translation
│   │   ├── Column: Context
│   │   └── Column: Status
│   └── LowerPane: TranslationEditorPanel
│       ├── SourceTextDisplay
│       ├── TranslationEditor
│       ├── MetadataPanel (context, comments)
│       └── SuggestionPanel
└── StatusBar (statistics, current entry info)
```

#### Integration Points
- Connect to TabManager for lifecycle management
- Connect to FileSystem service for open/save operations
- Connect to DatabaseService for translation history
- Connect to QA service for validation
- Connect to Settings service for preferences

#### UI Component Interactions
1. Table Selection → Update Editor Content
2. Editor Changes → Update Model Data → Mark File Modified
3. Navigation Controls → Change Table Selection
4. Filter Controls → Update Table Model Filter

### 3.2 Translation Database Service Integration

The database service needs to be tightly integrated with the POEditor:

#### Data Flow Integration
```
POEditor Component → DatabaseService Interface
├── Load Entry → Query Similar Translations
├── Save Entry → Store New Translation
├── Browse History → Query Version History
└── Search → Perform Database Search
```

#### Implementation Requirements
1. Asynchronous database operations to prevent UI freezing
2. Caching layer for frequently accessed translations
3. Batch operations for performance
4. Versioning for translation history
5. Connection pooling for concurrent access

### 3.3 Settings Integration

The POEditor will have several settings panels:

#### Editor Settings Panel
- Table display options (columns, fonts, colors)
- Default window layout
- Editor behavior (auto-save, validation)
- Navigation behavior

#### Translation Settings Panel
- Quality checks configuration
- Auto-translation services
- Translation memory settings
- Terminology management

#### Integration Requirements
1. QSettings storage for persistent settings
2. Live updates when settings change
3. Default values for first-time setup
4. Export/Import of settings profiles

## 4. Technical Implementation Details

### 4.1 POEditor Tab Implementation

The POEditorTab will be implemented as a QWidget subclass that implements the TabInterface:

```python
class POEditorTab(QWidget, TabInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_path = None
        self._is_modified = False
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Toolbar
        self.toolbar = POEditorToolbar()
        main_layout.addWidget(self.toolbar)
        
        # Splitter for table and editor
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
        
        # Add splitter to layout
        main_layout.addWidget(self.splitter)
        
        # Status bar
        self.status_bar = POEditorStatusBar()
        main_layout.addWidget(self.status_bar)
        
    def _connect_signals(self):
        # Connect table selection to editor update
        self.table_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        
        # Connect editor changes to model update
        self.editor_panel.translationChanged.connect(
            self._on_translation_changed
        )
        
        # Connect toolbar actions
        self.toolbar.saveRequested.connect(self.save_file)
        self.toolbar.nextEntryRequested.connect(self._go_to_next_entry)
        self.toolbar.prevEntryRequested.connect(self._go_to_prev_entry)
        
    # TabInterface implementation
    def file_path(self):
        return self._file_path
    
    def set_file_path(self, path):
        self._file_path = path
        self.status_bar.setFilePath(path)
    
    def is_modified(self):
        return self._is_modified
    
    def save(self):
        if self._file_path:
            return self._save_to_path(self._file_path)
        return False
    
    def save_as(self, path):
        return self._save_to_path(path)
    
    def load_file(self, path):
        try:
            self.table_model.loadFromFile(path)
            self.set_file_path(path)
            self._is_modified = False
            return True
        except Exception as e:
            lg.error(f"Failed to load file: {e}")
            return False
```

### 4.2 Translation Database Service Implementation

The database service needs to handle translation history and suggestions:

```python
class TranslationDatabaseService(QObject):
    suggestionsFetched = Signal(list)  # Signal for async operations
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._db_connection = None
        self._initialize_database()
        
    def _initialize_database(self):
        db_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        db_path = os.path.join(db_path, "translations.db")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._db_connection = QSqlDatabase.addDatabase("QSQLITE")
        self._db_connection.setDatabaseName(db_path)
        
        if not self._db_connection.open():
            lg.error(f"Failed to open database: {self._db_connection.lastError().text()}")
            return
            
        self._create_tables_if_needed()
    
    def _create_tables_if_needed(self):
        query = QSqlQuery(self._db_connection)
        
        # Translations table
        query.exec_("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                translation TEXT NOT NULL,
                context TEXT,
                project TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                username TEXT
            )
        """)
        
        # Create indexes
        query.exec_("CREATE INDEX IF NOT EXISTS idx_source ON translations(source)")
        query.exec_("CREATE INDEX IF NOT EXISTS idx_context ON translations(context)")
    
    def store_translation(self, source, translation, context=None, file_path=None):
        query = QSqlQuery(self._db_connection)
        query.prepare("""
            INSERT INTO translations (source, translation, context, file_path, username)
            VALUES (?, ?, ?, ?, ?)
        """)
        
        query.addBindValue(source)
        query.addBindValue(translation)
        query.addBindValue(context or "")
        query.addBindValue(file_path or "")
        query.addBindValue(QSettings().value("user/username", ""))
        
        if not query.exec_():
            lg.error(f"Failed to store translation: {query.lastError().text()}")
            return False
            
        return True
    
    def get_suggestions(self, source, context=None, limit=5):
        query = QSqlQuery(self._db_connection)
        
        if context:
            # Search by source and context
            query.prepare("""
                SELECT translation, COUNT(*) as frequency
                FROM translations
                WHERE source = ? AND context = ?
                GROUP BY translation
                ORDER BY frequency DESC, timestamp DESC
                LIMIT ?
            """)
            query.addBindValue(source)
            query.addBindValue(context)
            query.addBindValue(limit)
        else:
            # Search by source only
            query.prepare("""
                SELECT translation, COUNT(*) as frequency
                FROM translations
                WHERE source = ?
                GROUP BY translation
                ORDER BY frequency DESC, timestamp DESC
                LIMIT ?
            """)
            query.addBindValue(source)
            query.addBindValue(limit)
        
        suggestions = []
        if query.exec_():
            while query.next():
                translation = query.value(0)
                frequency = query.value(1)
                suggestions.append({
                    "translation": translation,
                    "frequency": frequency
                })
        else:
            lg.error(f"Failed to get suggestions: {query.lastError().text()}")
        
        return suggestions
    
    def get_suggestions_async(self, source, context=None, limit=5):
        # Run the query in a separate thread to avoid blocking UI
        thread = QThread(self)
        worker = DatabaseWorker(self, source, context, limit)
        worker.moveToThread(thread)
        
        thread.started.connect(worker.process)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        worker.suggestions_ready.connect(self._handle_suggestions_ready)
        
        thread.start()
    
    def _handle_suggestions_ready(self, suggestions):
        self.suggestionsFetched.emit(suggestions)
```

## 5. Migration Strategy for Existing Code

For each component from the old application, we will follow this migration process:

1. **Extract**: Isolate the component from the old codebase
2. **Refactor**: Update to use Qt6/PySide6 and modern Python features
3. **Integrate**: Connect to the plugin architecture
4. **Test**: Verify functionality matches or exceeds the original

### Migration Plan for Key Components

#### POFileTableModel Migration
1. Copy the original model implementation
2. Update Qt imports to PySide6
3. Remove window/app-specific dependencies
4. Add signals for plugin communication
5. Enhance with new features (filtering, sorting)
6. Write unit tests to verify functionality

#### TranslationEditor Migration
1. Extract the editor widget from old codebase
2. Update to PySide6 and refactor as needed
3. Create a cleaner interface for plugin integration
4. Add support for rich text formatting
5. Implement suggestions display
6. Integrate with settings service

#### Database Integration Migration
1. Extract database schema and queries
2. Refactor to use QSqlDatabase instead of direct SQLite
3. Create a service-oriented API
4. Implement asynchronous operations
5. Add caching for performance
6. Create migration path for existing databases

## 6. Next Steps and Timeline

### Immediate Next Steps (Next 2 Weeks)
1. Create POEditorTab skeleton class
2. Implement basic table view integration
3. Create translation editor component
4. Set up basic file operations

### Short-term Goals (2-4 Weeks)
1. Complete POEditor UI implementation
2. Integrate with file operations
3. Connect to settings system
4. Implement basic navigation

### Mid-term Goals (1-2 Months)
1. Complete database service integration
2. Implement suggestions mechanism
3. Add quality assurance features
4. Create additional settings panels

### Long-term Goals (2-3 Months)
1. Implement advanced features (search, filters)
2. Add translation memory capabilities
3. Optimize performance for large files
4. Add batch operations and automation

## 7. Conclusion

This implementation plan provides a detailed roadmap for completing the POEditor plugin integration. By focusing on the core UI component first, we create a solid foundation for the remaining features. The integration strategy ensures that valuable code from the old application is preserved while taking advantage of the modern plugin architecture.
