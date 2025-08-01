# POEditor Plugin Next Phase Master Plan

**Date**: July 24, 2025  
**Component**: POEditor Plugin Integration Next Phase  
**Status**: Planning  
**Dependencies**: Core Plugin Architecture, Sidebar System, Tab Management System

## 1. Overview

This document outlines the comprehensive next phase plan for the POEditor plugin integration into the new plugin-based architecture. Building on the existing designs and implementations, this plan focuses on bridging the gap between the legacy POEditor functionality and the new plugin architecture while providing a clear roadmap for development.

The next phase addresses several key areas:

1. **Complete POEditor Tab Implementation** - Finalize the core editor experience
2. **Service Layer Integration** - Implement and integrate essential services
3. **Settings System Implementation** - Create comprehensive configuration panels
4. **Advanced Feature Integration** - Bring advanced functionality from legacy code
5. **UI/UX Polishing** - Ensure visual consistency and optimal workflow

## 2. Current Status Assessment

### 2.1 Completed Components
- Core plugin architecture design
- Activity bar and sidebar management system
- Tab management framework
- Translation database service design
- POEditor tab component design
- High-level integration master plan

### 2.2 Gap Analysis
- **Implementation Gap**: Most designs remain theoretical without implementation
- **Integration Gap**: Connection points between components need defining
- **Service Layer Gap**: Core services need implementation
- **UI Gap**: Complete POEditor UI experience remains unimplemented
- **Migration Gap**: Legacy code assets need adaptation for new architecture

## 3. Development Roadmap

### Phase 1: Core POEditor Plugin Implementation (4 weeks)

#### Week 1: Plugin Structure and Framework
1. **Create Plugin Structure**
   - Implement POEditor plugin entry point
   - Register plugin with plugin manager
   - Define plugin configuration and dependencies
   - Implement basic event handling

2. **Basic Tab Type Registration**
   - Register PO file extensions with tab manager
   - Implement basic POEditorTab class
   - Create file loading and saving mechanism
   - Integrate with tab lifecycle events

#### Week 2: Table Model and Basic UI Implementation
1. **Table Model Implementation**
   - Implement POFileTableModel for entry display
   - Create POEntry data structure with version tracking
   - Implement table sorting and filtering capabilities
   - Add issue flagging system in table model

2. **POEditorTab Layout Implementation**
   - Create main splitter layout
   - Implement table view with custom delegates
   - Create basic editor panel structure
   - Implement navigation bar with paging

#### Week 3: Translation Editor and Core Functionality
1. **Translation Editor Implementation**
   - Implement source text display component
   - Create translation editor with rich text support
   - Add fuzzy toggle and basic comments editor
   - Implement basic keyboard shortcuts

2. **Core Editing Functionality**
   - Implement entry selection and editing workflow
   - Create save/load functionality for PO files
   - Add basic undo/redo support
   - Implement fuzzy flag toggling

#### Week 4: Navigation and Search
1. **Navigation System**
   - Implement paged navigation controls
   - Add keyboard navigation between entries
   - Create specialized navigation (fuzzy, untranslated)
   - Integrate with scroll position management

2. **Search Implementation**
   - Create find/replace bar component
   - Implement basic search functionality
   - Add highlight for search results
   - Implement result navigation

### Phase 2: Service Layer Implementation (4 weeks)

#### Week 1: Translation Database Service
1. **Database Service Core**
   - Implement SQLite database connection
   - Create schema management
   - Implement version tracking system
   - Add basic CRUD operations

2. **Translation Memory Integration**
   - Implement suggestion retrieval
   - Create fuzzy matching algorithms
   - Add database import/export functions
   - Implement version comparison

#### Week 2: Text Replacement Service
1. **Replacement Engine**
   - Implement text substitution engine
   - Create pattern matching system
   - Add rule priority handling
   - Implement context-aware replacements

2. **Integration with Editor**
   - Connect replacement service to editor
   - Implement real-time replacements
   - Add visual feedback for replacements
   - Create rule management system

#### Week 3: Quality Assurance Service
1. **Issue Detection Engine**
   - Implement rule-based validation system
   - Create standard validation rules
   - Add custom rule support
   - Implement performance optimization

2. **Integration with UI**
   - Connect QA service to table model
   - Implement issue highlighting
   - Add issue navigation
   - Create issue reporting interface

#### Week 4: Advanced Search Service
1. **Search Engine Implementation**
   - Create advanced search algorithms
   - Implement regex support
   - Add multi-field search capabilities
   - Create results management system

2. **Integration with UI**
   - Connect search service to find/replace bar
   - Implement advanced search dialog
   - Add result highlighting
   - Create search history system

### Phase 3: Settings System Implementation (3 weeks)

#### Week 1: Settings Framework
1. **Settings Architecture**
   - Implement settings manager service
   - Create settings persistence layer
   - Add settings change notification system
   - Implement settings panel registration

2. **Settings Dialog Implementation**
   - Create main settings dialog shell
   - Implement sidebar navigation
   - Add panel container
   - Create apply/cancel/restore logic

#### Week 2: Core Settings Panels
1. **Editor Settings Panel**
   - Create editor settings UI
   - Implement font configuration
   - Add page size settings
   - Implement table appearance options

2. **PO Settings Panel**
   - Create PO settings UI
   - Implement issue detection options
   - Add validation rule configuration
   - Create default values settings

#### Week 3: Advanced Settings Panels
1. **Font and Language Panel**
   - Create font settings UI
   - Implement font selector components
   - Add language selection
   - Implement preview capability

2. **Text Replacements Panel**
   - Create replacements UI
   - Implement rule editing interface
   - Add import/export functionality
   - Create rule testing capabilities

3. **Keyboard Mappings Panel**
   - Create keyboard settings UI
   - Implement shortcut editing
   - Add conflict detection
   - Create preset scheme support

### Phase 4: Advanced Features and Integration (3 weeks)

#### Week 1: Version Control and History
1. **History Panel**
   - Create translation history browser
   - Implement version comparison view
   - Add history search capabilities
   - Create version management UI

2. **Database Integration**
   - Integrate history panel with database service
   - Implement version retrieval and display
   - Add version application functionality
   - Create import/export tools

#### Week 2: Machine Translation Integration
1. **Translation Service Framework**
   - Create translation service interface
   - Implement provider management
   - Add authentication handling
   - Create request/response processing

2. **UI Integration**
   - Create translation suggestion panel
   - Implement service selection UI
   - Add result display and application
   - Create batch translation tools

#### Week 3: Final Integration
1. **Command System Integration**
   - Register all POEditor commands
   - Implement command handlers
   - Add keyboard shortcuts
   - Create command UI integration

2. **Menu Integration**
   - Implement POEditor menu structure
   - Add context menus
   - Create dynamic menu items
   - Implement menu state management

### Phase 5: Polishing and Optimization (2 weeks)

#### Week 1: UI Polish
1. **Visual Consistency**
   - Implement consistent styling
   - Add proper spacing and alignment
   - Create icon suite for POEditor
   - Implement theme support

2. **UX Improvements**
   - Add progress indicators
   - Implement status messages
   - Create tooltips and help text
   - Add visual feedback for actions

#### Week 2: Performance Optimization
1. **Table Performance**
   - Implement virtual scrolling
   - Add lazy loading for large files
   - Optimize rendering and painting
   - Create background loading

2. **Memory Management**
   - Implement memory-efficient data structures
   - Add cache management
   - Create resource cleanup
   - Implement background processing

## 4. Component Integration Architecture

### 4.1 Plugin Registration Flow

```
Plugin Manager
  ↓
POEditor Plugin
  ↓
  ├── Register Tab Type (PO files)
  ├── Register Services
  │   ├── Translation Database Service
  │   ├── Text Replacement Service
  │   ├── Quality Assurance Service
  │   └── Advanced Search Service
  ├── Register Settings Panels
  │   ├── Editor Settings Panel
  │   ├── PO Settings Panel
  │   ├── Font Settings Panel
  │   ├── Text Replacements Panel
  │   └── Keyboard Mappings Panel
  ├── Register Commands
  │   ├── File Operations
  │   ├── Edit Operations
  │   ├── Navigation Commands
  │   └── Tool Commands
  └── Register Sidebar Panels (optional)
      ├── Translation History Browser
      └── Issue Navigator
```

### 4.2 Tab Creation Flow

```
File Open Action
  ↓
Tab Manager (detects PO file)
  ↓
POEditor Plugin (creates tab)
  ↓
POEditorTab
  ↓
  ├── Create POFileTableModel
  ├── Create POFileTableView
  ├── Create TranslationEditorPanel
  ├── Create FindReplaceBar
  └── Create NavigationBar
```

### 4.3 Service Dependencies

```
POEditorTab
  ↓
  ├── Translation Database Service ← SQLite Database
  ├── Text Replacement Service
  ├── Quality Assurance Service
  └── Advanced Search Service
```

### 4.4 Settings Integration

```
Settings Dialog
  ↓
  ├── POEditor Category
  │   ├── Editor Settings Panel
  │   ├── PO Settings Panel
  │   ├── Font Settings Panel
  │   ├── Text Replacements Panel
  │   └── Keyboard Mappings Panel
  └── Apply/Cancel Logic → Settings Manager → QSettings
```

## 5. Key Implementation Details

### 5.1 POEditorTab Implementation

```python
class POEditorTab(QWidget):
    """Tab component for editing PO files."""
    
    # Signals
    modified_changed = Signal(bool)
    title_changed = Signal(str)
    
    def __init__(self, file_path: str, api: PluginAPI, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.file_path = file_path
        self.modified = False
        
        # Get required services
        self.translation_db = api.get_service("translation_db")
        self.replacement_service = api.get_service("text_replacement")
        self.qa_service = api.get_service("quality_assurance")
        self.search_service = api.get_service("advanced_search")
        
        # Setup UI components
        self._setup_ui()
        self._connect_signals()
        
        # Load file
        self.load_file(file_path)
        
    def _setup_ui(self):
        # Create layout structure
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create find/replace bar (hidden by default)
        self.find_replace_bar = FindReplaceBar(self)
        self.find_replace_bar.setVisible(False)
        main_layout.addWidget(self.find_replace_bar)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Create and add table view
        self.model = POFileTableModel(self)
        self.table_view = POFileTableView(self.model, self)
        self.main_splitter.addWidget(self.table_view)
        
        # Create and add editor panel
        self.editor_panel = TranslationEditorPanel(self)
        self.main_splitter.addWidget(self.editor_panel)
        
        # Set initial splitter sizes (40/60 split)
        self.main_splitter.setSizes([400, 600])
        main_layout.addWidget(self.main_splitter)
        
        # Create and add navigation bar
        self.navigation_bar = NavigationBar(self)
        main_layout.addWidget(self.navigation_bar)
        
    def _connect_signals(self):
        # Connect table signals
        self.table_view.entry_selected.connect(self._handle_entry_selected)
        
        # Connect editor signals
        self.editor_panel.translation_changed.connect(self._handle_translation_changed)
        self.editor_panel.fuzzy_changed.connect(self._handle_fuzzy_changed)
        self.editor_panel.comments_changed.connect(self._handle_comments_changed)
        
        # Connect find/replace signals
        self.find_replace_bar.find_requested.connect(self._handle_find_request)
        self.find_replace_bar.replace_requested.connect(self._handle_replace_request)
        
        # Connect navigation signals
        self.navigation_bar.page_changed.connect(self._handle_page_changed)
        
    def load_file(self, file_path: str) -> bool:
        try:
            # Load PO file using polib
            from polib import pofile
            po = pofile(file_path)
            
            # Update model with entries
            self.model.load_entries(po)
            
            # Update navigation bar
            self.navigation_bar.set_total_entries(len(po))
            self.navigation_bar.update_page_info()
            
            # Select first entry
            self.table_view.select_first_entry()
            
            # Update tab title
            self.title_changed.emit(os.path.basename(file_path))
            
            # Reset modified state
            self._set_modified(False)
            
            return True
        except Exception as e:
            from lg import logger
            logger.error(f"Error loading PO file: {e}", exc_info=True)
            return False
            
    def save(self) -> bool:
        try:
            # Save PO file using polib
            from polib import pofile
            po = pofile(self.file_path)
            
            # Update entries from model
            for i, entry in enumerate(po):
                model_entry = self.model.get_entry_by_row(i)
                if model_entry:
                    entry.msgstr = model_entry.msgstr
                    entry.flags = model_entry.flags
                    entry.tcomment = model_entry.tcomment
            
            # Save file
            po.save(self.file_path)
            
            # Reset modified state
            self._set_modified(False)
            
            return True
        except Exception as e:
            from lg import logger
            logger.error(f"Error saving PO file: {e}", exc_info=True)
            return False
            
    def _set_modified(self, modified: bool):
        if self.modified != modified:
            self.modified = modified
            self.modified_changed.emit(modified)
            
    def _handle_entry_selected(self, index: QModelIndex):
        # Get selected entry from model
        entry = self.model.get_entry(index)
        if entry:
            # Update editor panel with selected entry
            self.editor_panel.set_entry(entry)
            
            # Update suggestions if available
            if self.translation_db:
                suggestions = self.translation_db.get_suggestions(
                    entry.msgid, entry.msgctxt
                )
                self.editor_panel.set_suggestions(suggestions)
            
    def _handle_translation_changed(self, text: str):
        # Get current selection
        index = self.table_view.currentIndex()
        if index.isValid():
            # Update model with new translation
            self.model.update_translation(index.row(), text)
            
            # Add to translation database if available
            if self.translation_db:
                entry = self.model.get_entry(index)
                if entry:
                    self.translation_db.add_translation(
                        entry.msgid, text, entry.msgctxt, "manual"
                    )
            
            # Set modified state
            self._set_modified(True)
            
            # Emit event for other components
            self.api.emit_event(
                "poeditor.translation_updated", 
                entry_id=entry.msgid if entry else None,
                text=text
            )
            
    def _handle_fuzzy_changed(self, fuzzy: bool):
        # Get current selection
        index = self.table_view.currentIndex()
        if index.isValid():
            # Update model with new fuzzy state
            self.model.set_fuzzy(index.row(), fuzzy)
            
            # Set modified state
            self._set_modified(True)
            
    def _handle_comments_changed(self, text: str):
        # Get current selection
        index = self.table_view.currentIndex()
        if index.isValid():
            # Update model with new comments
            self.model.update_comments(index.row(), text)
            
            # Set modified state
            self._set_modified(True)
            
    def _handle_find_request(self, request):
        # Use search service if available
        if self.search_service:
            results = self.search_service.search(
                self.model, request.text, request.options
            )
            self.find_replace_bar.update_result_count(len(results))
            
            # Highlight first result if available
            if results:
                self._highlight_search_result(results[0])
                
    def _handle_replace_request(self, request):
        # Use search service if available
        if self.search_service:
            replaced = self.search_service.replace(
                self.model, request.text, request.replacement, request.options
            )
            if replaced:
                self._set_modified(True)
                
    def _handle_page_changed(self, page: int):
        # Update model page
        self.model.set_current_page(page)
        
        # Update table view
        self.table_view.reset()
        
        # Select first visible entry
        self.table_view.select_first_visible_entry()
```

### 5.2 Translation Database Service Implementation

```python
class TranslationDatabaseService(Service):
    """Service for managing translation history database."""
    
    def __init__(self, api: PluginAPI):
        super().__init__(api)
        self._db_path = self._get_db_path()
        self._conn = None
        self._setup_database()
        
        # Initialize caches
        self._exact_match_cache = LRUCache(100)
        self._record_id_cache = LRUCache(500)
        
        # Subscribe to events
        api.subscribe_event("poeditor.translation_updated", self._on_translation_updated)
        api.subscribe_event("settings.changed.translation_db", self._on_settings_changed)
    
    def get_suggestions(self, msgid: str, context: str = None) -> List[DatabasePORecord]:
        """Get translation suggestions for a source text."""
        try:
            # First, try exact match
            exact_record = self._get_exact_match(msgid, context)
            if exact_record:
                return [exact_record]
                
            # Then try fuzzy matches
            fuzzy_threshold = self._get_fuzzy_threshold()
            fuzzy_records = self._get_fuzzy_matches(msgid, context, fuzzy_threshold)
            
            # Sort by relevance (similarity score)
            return sorted(fuzzy_records, 
                         key=lambda r: self._calculate_similarity(msgid, r.msgid), 
                         reverse=True)
        except Exception as e:
            from lg import logger
            logger.error(f"Error getting translation suggestions: {e}", exc_info=True)
            return []
        
    def add_translation(self, msgid: str, msgstr: str, context: str = None, 
                       source: str = "manual") -> bool:
        """Add a new translation to the database."""
        try:
            # Skip empty translations
            if not msgid or not msgstr:
                return False
                
            # Get or create record
            record = self._get_exact_match(msgid, context)
            if not record:
                # Create new record
                record = DatabasePORecord(msgid=msgid, msgctxt=context)
                self._create_record(record)
                
            # Add new version if different
            if record.add_version(msgstr, source):
                # Save to database
                return self._save_version(record.unique_id, msgstr, source)
            
            return False
        except Exception as e:
            from lg import logger
            logger.error(f"Error adding translation: {e}", exc_info=True)
            return False
            
    def search_translations(self, query: dict) -> List[DatabasePORecord]:
        """Search translations with multiple criteria."""
        try:
            # Build SQL query based on criteria
            sql_parts = ["SELECT e.unique_id, e.en_text, e.context FROM english_text e"]
            params = []
            where_clauses = []
            
            # Join with translations if needed
            if query.get('msgstr_pattern'):
                sql_parts.append("INNER JOIN tran_text t ON e.unique_id = t.unique_id")
                
            # Source text condition
            if query.get('msgid_pattern'):
                pattern = query['msgid_pattern']
                if query.get('msgid_regex', False):
                    where_clauses.append("e.en_text REGEXP ?")
                else:
                    pattern = f"%{pattern}%"
                    where_clauses.append("e.en_text LIKE ?")
                params.append(pattern)
                
            # Translation text condition
            if query.get('msgstr_pattern'):
                pattern = query['msgstr_pattern']
                if query.get('msgstr_regex', False):
                    where_clauses.append("t.tran_text REGEXP ?")
                else:
                    pattern = f"%{pattern}%"
                    where_clauses.append("t.tran_text LIKE ?")
                params.append(pattern)
                
            # Context condition
            if query.get('context'):
                where_clauses.append("e.context LIKE ?")
                params.append(f"%{query['context']}%")
                
            # Build final query
            if where_clauses:
                sql_parts.append("WHERE " + " AND ".join(where_clauses))
                
            # Add order by
            sql_parts.append("ORDER BY e.unique_id")
            
            # Add limit
            if query.get('limit'):
                sql_parts.append("LIMIT ?")
                params.append(query['limit'])
                
            # Execute query
            sql = " ".join(sql_parts)
            records = self._execute_search(sql, params)
            
            return records
        except Exception as e:
            from lg import logger
            logger.error(f"Error searching translations: {e}", exc_info=True)
            return []
    
    def import_po_file(self, file_path: str, source: str = "file") -> int:
        """Import translations from a PO file into the database."""
        try:
            # Open PO file
            import polib
            po_file = polib.pofile(file_path)
            
            # Start transaction
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                count = 0
                for entry in po_file:
                    # Skip empty translations
                    if not entry.msgid or not entry.msgstr:
                        continue
                        
                    # Add to database
                    if self.add_translation(entry.msgid, entry.msgstr, entry.msgctxt, source):
                        count += 1
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                from lg import logger
                logger.info(f"Imported {count} translations from {file_path}")
                return count
        except Exception as e:
            from lg import logger
            logger.error(f"Error importing PO file: {e}", exc_info=True)
            return 0
            
    def export_po_file(self, file_path: str, filter_query: dict = None) -> int:
        """Export translations from database to a PO file."""
        try:
            # Create PO file
            import polib
            po_file = polib.POFile()
            po_file.metadata = {
                'Project-Id-Version': 'POEditor Export',
                'Report-Msgid-Bugs-To': '',
                'POT-Creation-Date': datetime.now().strftime('%Y-%m-%d %H:%M%z'),
                'PO-Revision-Date': datetime.now().strftime('%Y-%m-%d %H:%M%z'),
                'Last-Translator': '',
                'Language-Team': '',
                'MIME-Version': '1.0',
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Transfer-Encoding': '8bit',
            }
            
            # Get records from database
            records = self.search_translations(filter_query or {})
            
            # Add entries to PO file
            for record in records:
                latest = record.get_latest_version()
                if not latest:
                    continue
                    
                entry = polib.POEntry(
                    msgid=record.msgid,
                    msgstr=latest[1],  # translation text
                    msgctxt=record.msgctxt,
                    tcomment=f"Source: {latest[2]}"  # source as comment
                )
                po_file.append(entry)
                
            # Save file
            po_file.save(file_path)
            
            from lg import logger
            logger.info(f"Exported {len(po_file)} translations to {file_path}")
            return len(po_file)
        except Exception as e:
            from lg import logger
            logger.error(f"Error exporting PO file: {e}", exc_info=True)
            return 0
    
    def _on_translation_updated(self, event_data: dict):
        """Handle translation updated event."""
        msgid = event_data.get("entry_id")
        msgstr = event_data.get("text")
        context = event_data.get("context")
        
        if msgid and msgstr:
            self.add_translation(msgid, msgstr, context, "manual")
            
    def _on_settings_changed(self, event_data: dict):
        """Handle settings changed event."""
        if event_data.get("key") == "translation_db/db_path":
            # Close current connection
            if self._conn:
                self._conn.close()
                self._conn = None
                
            # Update path and reconnect
            self._db_path = self._get_db_path()
            self._setup_database()
```

### 5.3 Plugin Registration Implementation

```python
class POEditorPlugin:
    """Plugin for PO file editing functionality."""
    
    def register(self, api: PluginAPI):
        """Register plugin components with the application."""
        from lg import logger
        logger.info("Registering POEditor plugin")
        
        # Register tab type for PO files
        api.register_tab_type(
            file_extensions=[".po", ".pot"],
            create_tab=lambda path, api=api: POEditorTab(path, api),
            icon=QIcon(":/icons/poeditor.svg"),
            tab_type="poeditor"
        )
        
        # Register services
        self._register_services(api)
        
        # Register settings panels
        self._register_settings_panels(api)
        
        # Register commands
        self._register_commands(api)
        
        logger.info("POEditor plugin registered successfully")
        
    def _register_services(self, api: PluginAPI):
        """Register plugin services."""
        # Translation database service
        translation_db = TranslationDatabaseService(api)
        api.register_service("translation_db", translation_db)
        
        # Text replacement service
        replacement_service = TextReplacementService(api)
        api.register_service("text_replacement", replacement_service)
        
        # Quality assurance service
        qa_service = QualityAssuranceService(api)
        api.register_service("quality_assurance", qa_service)
        
        # Advanced search service
        search_service = AdvancedSearchService(api)
        api.register_service("advanced_search", search_service)
        
    def _register_settings_panels(self, api: PluginAPI):
        """Register settings panels."""
        # Editor settings panel
        api.register_settings_panel(
            "POEditor",
            "Editor",
            lambda: EditorSettingsPanel(api)
        )
        
        # PO settings panel
        api.register_settings_panel(
            "POEditor",
            "PO Files",
            lambda: POSettingsPanel(api)
        )
        
        # Font settings panel
        api.register_settings_panel(
            "POEditor",
            "Fonts & Languages",
            lambda: FontsLanguagesPanel(api)
        )
        
        # Text replacements panel
        api.register_settings_panel(
            "POEditor",
            "Text Replacements",
            lambda: TextReplacementsPanel(api)
        )
        
        # Translation history panel
        api.register_settings_panel(
            "POEditor",
            "Translation History",
            lambda: TranslationHistoryPanel(api)
        )
        
        # Keyboard mappings panel
        api.register_settings_panel(
            "POEditor",
            "Keyboard Mappings",
            lambda: KeyboardMappingsPanel(api)
        )
        
    def _register_commands(self, api: PluginAPI):
        """Register plugin commands."""
        # File operations
        api.register_command(
            "poeditor.open",
            "Open PO File",
            self._command_open_po_file
        )
        
        api.register_command(
            "poeditor.save",
            "Save PO File",
            self._command_save_po_file
        )
        
        # Navigation operations
        api.register_command(
            "poeditor.next_entry",
            "Go to Next Entry",
            self._command_next_entry
        )
        
        api.register_command(
            "poeditor.previous_entry",
            "Go to Previous Entry",
            self._command_previous_entry
        )
        
        api.register_command(
            "poeditor.next_untranslated",
            "Go to Next Untranslated Entry",
            self._command_next_untranslated
        )
        
        api.register_command(
            "poeditor.next_fuzzy",
            "Go to Next Fuzzy Entry",
            self._command_next_fuzzy
        )
        
        # Search operations
        api.register_command(
            "poeditor.find",
            "Find in PO File",
            self._command_find
        )
        
        api.register_command(
            "poeditor.find_replace",
            "Find and Replace in PO File",
            self._command_find_replace
        )
        
    def _get_current_poeditor_tab(self, api: PluginAPI) -> Optional[POEditorTab]:
        """Get the currently active POEditor tab, if any."""
        tab_manager = api.get_service("tab_manager")
        if tab_manager:
            current_tab = tab_manager.get_current_tab()
            if isinstance(current_tab, POEditorTab):
                return current_tab
        return None
        
    # Command implementations
    def _command_open_po_file(self):
        pass  # Implementation
        
    def _command_save_po_file(self):
        pass  # Implementation
        
    def _command_next_entry(self):
        pass  # Implementation
        
    def _command_previous_entry(self):
        pass  # Implementation
        
    def _command_next_untranslated(self):
        pass  # Implementation
        
    def _command_next_fuzzy(self):
        pass  # Implementation
        
    def _command_find(self):
        pass  # Implementation
        
    def _command_find_replace(self):
        pass  # Implementation
```

## 6. Settings Panel Implementation

### 6.1 Editor Settings Panel

```python
class EditorSettingsPanel(QWidget):
    """Settings panel for POEditor editor configuration."""
    
    def __init__(self, api: PluginAPI, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.settings = QSettings("POEditor", "Settings")
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        """Create the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Group: Table Display
        table_group = QGroupBox("Table Display")
        table_layout = QFormLayout(table_group)
        
        # Page size control
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 1000)
        self.page_size_spin.setSingleStep(10)
        table_layout.addRow("Entries per page:", self.page_size_spin)
        
        # Column visibility
        self.show_context_check = QCheckBox("Show Context Column")
        self.show_fuzzy_check = QCheckBox("Show Fuzzy Column")
        self.show_lineno_check = QCheckBox("Show Line Number Column")
        table_layout.addRow("", self.show_context_check)
        table_layout.addRow("", self.show_fuzzy_check)
        table_layout.addRow("", self.show_lineno_check)
        
        # Row height control
        self.row_height_spin = QSpinBox()
        self.row_height_spin.setRange(20, 100)
        self.row_height_spin.setSingleStep(5)
        table_layout.addRow("Row height:", self.row_height_spin)
        
        main_layout.addWidget(table_group)
        
        # Group: Editor Behavior
        editor_group = QGroupBox("Editor Behavior")
        editor_layout = QFormLayout(editor_group)
        
        # Auto-save control
        self.auto_save_check = QCheckBox("Enable Auto-save")
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(1, 60)
        self.auto_save_interval_spin.setSuffix(" minutes")
        editor_layout.addRow("", self.auto_save_check)
        editor_layout.addRow("Auto-save interval:", self.auto_save_interval_spin)
        
        # Editing behaviors
        self.auto_next_check = QCheckBox("Move to next entry after translation")
        self.confirm_fuzzy_check = QCheckBox("Confirm before marking as fuzzy")
        self.spellcheck_check = QCheckBox("Enable spell checking")
        editor_layout.addRow("", self.auto_next_check)
        editor_layout.addRow("", self.confirm_fuzzy_check)
        editor_layout.addRow("", self.spellcheck_check)
        
        main_layout.addWidget(editor_group)
        
        # Group: Navigation
        nav_group = QGroupBox("Navigation")
        nav_layout = QFormLayout(nav_group)
        
        # Navigation behaviors
        self.wrap_navigation_check = QCheckBox("Wrap around at end of file")
        self.skip_translated_check = QCheckBox("Skip translated entries in navigation")
        nav_layout.addRow("", self.wrap_navigation_check)
        layout.addRow("", self.skip_translated_check)
        
        main_layout.addWidget(nav_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
        
    def _load_settings(self):
        """Load current settings into UI."""
        # Table display settings
        self.page_size_spin.setValue(self.settings.value("editor/page_size", 50, int))
        self.show_context_check.setChecked(self.settings.value("editor/show_context", True, bool))
        self.show_fuzzy_check.setChecked(self.settings.value("editor/show_fuzzy", True, bool))
        self.show_lineno_check.setChecked(self.settings.value("editor/show_lineno", True, bool))
        self.row_height_spin.setValue(self.settings.value("editor/row_height", 30, int))
        
        # Editor behavior settings
        self.auto_save_check.setChecked(self.settings.value("editor/auto_save", False, bool))
        self.auto_save_interval_spin.setValue(self.settings.value("editor/auto_save_interval", 5, int))
        self.auto_next_check.setChecked(self.settings.value("editor/auto_next", True, bool))
        self.confirm_fuzzy_check.setChecked(self.settings.value("editor/confirm_fuzzy", False, bool))
        self.spellcheck_check.setChecked(self.settings.value("editor/spellcheck", True, bool))
        
        # Navigation settings
        self.wrap_navigation_check.setChecked(self.settings.value("editor/wrap_navigation", True, bool))
        self.skip_translated_check.setChecked(self.settings.value("editor/skip_translated", False, bool))
        
    def save_settings(self):
        """Save current UI state to settings."""
        # Table display settings
        self.settings.setValue("editor/page_size", self.page_size_spin.value())
        self.settings.setValue("editor/show_context", self.show_context_check.isChecked())
        self.settings.setValue("editor/show_fuzzy", self.show_fuzzy_check.isChecked())
        self.settings.setValue("editor/show_lineno", self.show_lineno_check.isChecked())
        self.settings.setValue("editor/row_height", self.row_height_spin.value())
        
        # Editor behavior settings
        self.settings.setValue("editor/auto_save", self.auto_save_check.isChecked())
        self.settings.setValue("editor/auto_save_interval", self.auto_save_interval_spin.value())
        self.settings.setValue("editor/auto_next", self.auto_next_check.isChecked())
        self.settings.setValue("editor/confirm_fuzzy", self.confirm_fuzzy_check.isChecked())
        self.settings.setValue("editor/spellcheck", self.spellcheck_check.isChecked())
        
        # Navigation settings
        self.settings.setValue("editor/wrap_navigation", self.wrap_navigation_check.isChecked())
        self.settings.setValue("editor/skip_translated", self.skip_translated_check.isChecked())
        
        # Emit settings changed event
        self.api.emit_event("settings.changed.editor", {})
```

## 7. Integration Testing Strategy

### 7.1 Component Testing

1. **POEditorTab Tests**
   - Test file loading and saving
   - Test entry selection and editing
   - Test navigation between entries
   - Test search functionality
   - Test fuzzy flag toggling

2. **TranslationDatabaseService Tests**
   - Test database initialization
   - Test suggestion retrieval
   - Test translation addition
   - Test search functionality
   - Test import/export operations

3. **Settings Panel Tests**
   - Test settings loading
   - Test settings saving
   - Test settings application to components
   - Test event emission on setting changes

### 7.2 Integration Tests

1. **Plugin Registration Tests**
   - Test plugin registration with API
   - Test service registration
   - Test settings panel registration
   - Test command registration

2. **Tab Creation Tests**
   - Test PO file detection
   - Test POEditorTab creation
   - Test tab lifecycle management
   - Test file loading workflow

3. **Service Integration Tests**
   - Test database service with editor
   - Test replacement service with editor
   - Test QA service with editor
   - Test search service with editor

4. **Settings Integration Tests**
   - Test settings application to components
   - Test live settings updates
   - Test settings persistence
   - Test settings panel navigation

## 8. Next Steps

1. **Create Detailed Implementation Schedule**
   - Break down tasks by week
   - Assign resources
   - Set milestones and deliverables

2. **Set Up Development Environment**
   - Configure project structure
   - Set up test framework
   - Prepare debugging environment

3. **Begin Phase 1 Implementation**
   - Create plugin structure
   - Implement basic tab functionality
   - Create table model

4. **Regular Progress Reviews**
   - Weekly status reviews
   - Adjust timeline as needed
   - Address blockers promptly

## 9. Risk Management

### 9.1 Identified Risks

1. **Performance with Large Files**
   - **Risk**: Poor performance with large PO files
   - **Mitigation**: Implement pagination and lazy loading
   - **Contingency**: Add background processing for large operations

2. **Legacy Code Integration Challenges**
   - **Risk**: Difficulty adapting legacy code to new architecture
   - **Mitigation**: Careful analysis and incremental adaptation
   - **Contingency**: Rewrite problematic components

3. **Service Dependency Management**
   - **Risk**: Complex service dependencies causing issues
   - **Mitigation**: Clear interface definitions and error handling
   - **Contingency**: Implement graceful degradation

4. **UI Consistency**
   - **Risk**: Inconsistent UI experience
   - **Mitigation**: Design style guide and component library
   - **Contingency**: Late-stage UI audit and refinement

### 9.2 Mitigation Strategies

1. **Incremental Development**
   - Implement core functionality first
   - Add advanced features incrementally
   - Test thoroughly at each stage

2. **Modular Architecture**
   - Maintain clear component boundaries
   - Use interfaces for service communication
   - Allow component replacement if needed

3. **Fallback Modes**
   - Implement basic functionality that works without services
   - Add graceful degradation for missing dependencies
   - Provide clear error messages for users

4. **Regular Testing**
   - Continuous integration with automated tests
   - Manual testing of complex workflows
   - Performance testing with large files

## 10. Conclusion

This next phase plan provides a comprehensive roadmap for implementing the POEditor plugin within the new architecture. By following a modular, phased approach with clear integration points, we can successfully migrate the legacy functionality while enhancing it with modern design patterns and improved user experience.

The plan addresses all key aspects of the implementation including core editing functionality, service layer, settings system, and advanced features. With careful attention to component integration and rigorous testing, we can deliver a robust, high-quality POEditor plugin that leverages the benefits of the new plugin architecture while preserving the powerful features of the original application.

The implementation will follow best practices outlined in the project guidelines, including modular architecture, clear API contracts, consistent coding standards, comprehensive testing, thorough documentation, proper error handling, and performance optimization. This ensures the resulting code will be maintainable, extensible, and reliable.
