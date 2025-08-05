# Preferences System: Text Replacements

## Overview
The Text Replacements module provides powerful functionality for automatically replacing text patterns during translation, improving efficiency and consistency. This design document outlines the architecture and components for storing, managing, and applying text replacement rules in the preferences system.

## Panel Architecture

### Main Components

1. **Replacement Rules Table** - PagedTableWidget displaying rules with search/filter
2. **Rule Editor Form** - Form for adding/editing individual replacement rules  
3. **Bulk Operations Toolbar** - Tools for batch operations on selected rules
4. **Import/Export Section** - File format handlers for rule management
5. **Rule Validation Preview** - Live preview of rule application

### Layout Structure

```
┌─ Text Replacement Rules Management ─────────────────────────────────┐
│ ┌─ Search & Filter Controls ─────────────────────────────────────┐ │
│ │ [Search: find text, replace text, context...] [Clear] [Export] │ │
│ │ Filter: [All Rules ▼] Sort: [Find Text ▼] [↑↓] Show: [50 ▼]   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Rules Table ───────────────────────────────────────────────────┐ │
│ │ [☑] │ ID │ Find Text      │ Replace Text   │ Context │ Options │ │
│ │ ─────┼────┼────────────────┼────────────────┼─────────┼───────── │ │
│ │ ☑   │ 1  │ %s             │ {0}            │ Python  │ R       │ │
│ │ ☐   │ 2  │ oldword        │ newword        │ *       │ C       │ │
│ │ ☑   │ 3  │ (\d+)          │ num_\1         │ Regex   │ RC      │ │
│ │ ☑   │ 4  │ TODO:          │ # TODO:        │ Code    │         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Bulk Operations ───────────────────────────────────────────────┐ │
│ │ Selected: 2 rules  [Enable All] [Disable All] [Delete Selected]│ │
│ │ [Test Selected] [Export Selected] [Duplicate Selected]         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Rule Editor ───────────────────────────────────────────────────┐ │
│ │ Find Text:    [__________________________] [☑] Regex [☑] Case  │ │
│ │ Replace Text: [__________________________]                      │ │
│ │ Context:      [All contexts_____________▼] (optional filter)    │ │
│ │ Description:  [Short description of rule___________________]    │ │
│ │ Test Input:   [Sample text to test rule_________________]       │ │
│ │ Test Output:  [Result after applying rule_______________]       │ │
│ │ [Add Rule] [Update Selected] [Test Rule] [Clear Form] [Reset]  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Import/Export ─────────────────────────────────────────────────┐ │
│ │ Format: [JSON ▼] [Import File] [Export All] [Export Selected]  │ │
│ │ Supported: JSON, CSV, XML, SQLite, YAML, PList, AutoHotkey     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Models

### ReplacementRecord

**Purpose:** Core data model for replacement rules with validation and serialization.

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import re

@dataclass
class ReplacementRecord:
    """Data model for a text replacement rule."""
    
    # Core fields
    id: Optional[int] = None
    find_text: str = ""
    replace_text: str = ""
    enabled: bool = True
    
    # Options
    case_sensitive: bool = False
    use_regex: bool = False
    whole_word: bool = False
    
    # Metadata
    context: str = ""  # Optional context filter (file type, section, etc.)
    description: str = ""
    
    # Tracking
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    last_used_date: Optional[datetime] = None
    
    # Computed properties
    @property
    def options_string(self) -> str:
        """Get compact options string for display."""
        options = []
        if self.use_regex:
            options.append("R")
        if self.case_sensitive:
            options.append("C")
        if self.whole_word:
            options.append("W")
        return "".join(options)
    
    @property
    def is_valid(self) -> bool:
        """Check if rule is valid."""
        if not self.find_text:
            return False
            
        if self.use_regex:
            try:
                re.compile(self.find_text)
                return True
            except re.error:
                return False
                
        return True
    
    def test_replacement(self, input_text: str) -> str:
        """Test rule against input text and return result."""
        if not self.is_valid or not input_text:
            return input_text
            
        try:
            if self.use_regex:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                if self.whole_word:
                    pattern = r'\b' + self.find_text + r'\b'
                else:
                    pattern = self.find_text
                return re.sub(pattern, self.replace_text, input_text, flags=flags)
            else:
                if self.case_sensitive:
                    search_text = self.find_text
                    target_text = input_text
                else:
                    search_text = self.find_text.lower()
                    target_text = input_text.lower()
                    
                if self.whole_word:
                    # Simple whole word matching for non-regex
                    words = target_text.split()
                    for i, word in enumerate(words):
                        if word == search_text:
                            words[i] = self.replace_text
                    return " ".join(words)
                else:
                    return input_text.replace(self.find_text, self.replace_text)
        except Exception:
            return input_text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'find_text': self.find_text,
            'replace_text': self.replace_text,
            'enabled': self.enabled,
            'case_sensitive': self.case_sensitive,
            'use_regex': self.use_regex,
            'whole_word': self.whole_word,
            'context': self.context,
            'description': self.description,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None,
            'usage_count': self.usage_count,
            'last_used_date': self.last_used_date.isoformat() if self.last_used_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReplacementRecord':
        """Create instance from dictionary."""
        # Handle datetime fields
        created_date = None
        if data.get('created_date'):
            created_date = datetime.fromisoformat(data['created_date'])
            
        modified_date = None
        if data.get('modified_date'):
            modified_date = datetime.fromisoformat(data['modified_date'])
            
        last_used_date = None
        if data.get('last_used_date'):
            last_used_date = datetime.fromisoformat(data['last_used_date'])
        
        return cls(
            id=data.get('id'),
            find_text=data.get('find_text', ''),
            replace_text=data.get('replace_text', ''),
            enabled=data.get('enabled', True),
            case_sensitive=data.get('case_sensitive', False),
            use_regex=data.get('use_regex', False),
            whole_word=data.get('whole_word', False),
            context=data.get('context', ''),
            description=data.get('description', ''),
            created_date=created_date or datetime.now(),
            modified_date=modified_date or datetime.now(),
            usage_count=data.get('usage_count', 0),
            last_used_date=last_used_date
        )
```

## Database Service

### ReplacementRulesService

**Purpose:** Database operations and business logic for replacement rules.

**File:** `services/replacement_rules_service.py`

```python
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from lg import logger
from .replacement_record import ReplacementRecord
from workspace.find_replace_types import PreferenceSearchRequest, PreferenceSearchResult, MatchInstance

class ReplacementRulesService:
    """Service for managing replacement rules in database."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists with proper schema."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables if they don't exist
            self._create_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize replacement rules database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS replacement_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            find_text TEXT NOT NULL,
            replace_text TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            case_sensitive BOOLEAN DEFAULT 0,
            use_regex BOOLEAN DEFAULT 0,
            whole_word BOOLEAN DEFAULT 0,
            context TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            last_used_date TIMESTAMP NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_replacement_find_text ON replacement_rules(find_text);
        CREATE INDEX IF NOT EXISTS idx_replacement_context ON replacement_rules(context);
        CREATE INDEX IF NOT EXISTS idx_replacement_enabled ON replacement_rules(enabled);
        CREATE INDEX IF NOT EXISTS idx_replacement_modified ON replacement_rules(modified_date);
        """
        
        self.connection.executescript(create_sql)
        self.connection.commit()
    
    def get_all_records(self) -> List[ReplacementRecord]:
        """Get all replacement records."""
        try:
            cursor = self.connection.execute(
                "SELECT * FROM replacement_rules ORDER BY modified_date DESC"
            )
            records = []
            for row in cursor.fetchall():
                records.append(self._row_to_record(row))
            return records
        except Exception as e:
            logger.error(f"Failed to get replacement records: {e}")
            return []
    
    def get_page_records(self, page: int, page_size: int, 
                        enabled_only: bool = False,
                        context_filter: str = None) -> List[ReplacementRecord]:
        """Get paginated replacement records."""
        try:
            offset = (page - 1) * page_size
            
            where_conditions = []
            params = []
            
            if enabled_only:
                where_conditions.append("enabled = ?")
                params.append(True)
                
            if context_filter and context_filter != "All":
                where_conditions.append("context = ?")
                params.append(context_filter)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            sql = f"""
            SELECT * FROM replacement_rules 
            {where_clause}
            ORDER BY modified_date DESC 
            LIMIT ? OFFSET ?
            """
            
            params.extend([page_size, offset])
            
            cursor = self.connection.execute(sql, params)
            records = []
            for row in cursor.fetchall():
                records.append(self._row_to_record(row))
            return records
        except Exception as e:
            logger.error(f"Failed to get page records: {e}")
            return []
    
    def search_records(self, request: PreferenceSearchRequest) -> List[PreferenceSearchResult]:
        """Search replacement records with highlighting."""
        try:
            query = request.query.lower() if request.case_match.name == "IGNORE" else request.query
            
            # Build search SQL
            search_conditions = []
            params = []
            
            if request.use_regex:
                # For regex, we'll do the matching in Python
                cursor = self.connection.execute("SELECT * FROM replacement_rules")
                all_records = [self._row_to_record(row) for row in cursor.fetchall()]
                
                results = []
                for record in all_records:
                    matches = self._find_regex_matches(record, request)
                    if matches:
                        result = PreferenceSearchResult(
                            record_id=record.id,
                            record=record,
                            match_instances=matches
                        )
                        results.append(result)
                return results
            else:
                # Simple text search
                search_fields = ["find_text", "replace_text", "context", "description"]
                for field in search_fields:
                    if request.case_match.name == "IGNORE":
                        search_conditions.append(f"LOWER({field}) LIKE ?")
                        params.append(f"%{query}%")
                    else:
                        search_conditions.append(f"{field} LIKE ?")
                        params.append(f"%{query}%")
                
                where_clause = " OR ".join(search_conditions)
                sql = f"SELECT * FROM replacement_rules WHERE {where_clause}"
                
                cursor = self.connection.execute(sql, params)
                results = []
                for row in cursor.fetchall():
                    record = self._row_to_record(row)
                    matches = self._find_text_matches(record, request)
                    result = PreferenceSearchResult(
                        record_id=record.id,
                        record=record,
                        match_instances=matches
                    )
                    results.append(result)
                return results
                
        except Exception as e:
            logger.error(f"Failed to search records: {e}")
            return []
    
    def save_record(self, record: ReplacementRecord) -> bool:
        """Save or update a replacement record."""
        try:
            record.modified_date = datetime.now()
            
            if record.id is None:
                # Insert new record
                sql = """
                INSERT INTO replacement_rules (
                    find_text, replace_text, enabled, case_sensitive, use_regex, 
                    whole_word, context, description, created_date, modified_date,
                    usage_count, last_used_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    record.find_text, record.replace_text, record.enabled,
                    record.case_sensitive, record.use_regex, record.whole_word,
                    record.context, record.description, record.created_date,
                    record.modified_date, record.usage_count, record.last_used_date
                )
                
                cursor = self.connection.execute(sql, params)
                record.id = cursor.lastrowid
            else:
                # Update existing record
                sql = """
                UPDATE replacement_rules SET
                    find_text = ?, replace_text = ?, enabled = ?, case_sensitive = ?,
                    use_regex = ?, whole_word = ?, context = ?, description = ?,
                    modified_date = ?, usage_count = ?, last_used_date = ?
                WHERE id = ?
                """
                params = (
                    record.find_text, record.replace_text, record.enabled,
                    record.case_sensitive, record.use_regex, record.whole_word,
                    record.context, record.description, record.modified_date,
                    record.usage_count, record.last_used_date, record.id
                )
                
                self.connection.execute(sql, params)
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save record: {e}")
            return False
    
    def delete_record(self, record_id: int) -> bool:
        """Delete a replacement record."""
        try:
            self.connection.execute("DELETE FROM replacement_rules WHERE id = ?", (record_id,))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete record {record_id}: {e}")
            return False
    
    def delete_records(self, record_ids: List[int]) -> int:
        """Delete multiple records and return count of deleted records."""
        try:
            placeholders = ",".join("?" * len(record_ids))
            sql = f"DELETE FROM replacement_rules WHERE id IN ({placeholders})"
            cursor = self.connection.execute(sql, record_ids)
            deleted_count = cursor.rowcount
            self.connection.commit()
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to delete records: {e}")
            return 0
    
    def get_total_count(self, enabled_only: bool = False, context_filter: str = None) -> int:
        """Get total count of records."""
        try:
            where_conditions = []
            params = []
            
            if enabled_only:
                where_conditions.append("enabled = ?")
                params.append(True)
                
            if context_filter and context_filter != "All":
                where_conditions.append("context = ?")
                params.append(context_filter)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            sql = f"SELECT COUNT(*) FROM replacement_rules {where_clause}"
            cursor = self.connection.execute(sql, params)
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            return 0
    
    def get_available_contexts(self) -> List[str]:
        """Get list of all available contexts."""
        try:
            cursor = self.connection.execute(
                "SELECT DISTINCT context FROM replacement_rules WHERE context != '' ORDER BY context"
            )
            contexts = ["All"]  # Add "All" option
            contexts.extend([row[0] for row in cursor.fetchall()])
            return contexts
        except Exception as e:
            logger.error(f"Failed to get contexts: {e}")
            return ["All"]
    
    def update_usage_count(self, record_id: int):
        """Update usage count and last used date for a rule."""
        try:
            sql = """
            UPDATE replacement_rules SET
                usage_count = usage_count + 1,
                last_used_date = ?
            WHERE id = ?
            """
            self.connection.execute(sql, (datetime.now(), record_id))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to update usage count for record {record_id}: {e}")
    
    def _row_to_record(self, row) -> ReplacementRecord:
        """Convert database row to ReplacementRecord."""
        created_date = datetime.fromisoformat(row['created_date']) if row['created_date'] else datetime.now()
        modified_date = datetime.fromisoformat(row['modified_date']) if row['modified_date'] else datetime.now()
        last_used_date = datetime.fromisoformat(row['last_used_date']) if row['last_used_date'] else None
        
        return ReplacementRecord(
            id=row['id'],
            find_text=row['find_text'],
            replace_text=row['replace_text'],
            enabled=bool(row['enabled']),
            case_sensitive=bool(row['case_sensitive']),
            use_regex=bool(row['use_regex']),
            whole_word=bool(row['whole_word']),
            context=row['context'] or '',
            description=row['description'] or '',
            created_date=created_date,
            modified_date=modified_date,
            usage_count=row['usage_count'] or 0,
            last_used_date=last_used_date
        )
    
    def _find_text_matches(self, record: ReplacementRecord, request: PreferenceSearchRequest) -> List[MatchInstance]:
        """Find text matches in record for highlighting."""
        matches = []
        query = request.query
        
        # Search in different fields
        search_fields = {
            'find_text': record.find_text,
            'replace_text': record.replace_text,
            'context': record.context,
            'description': record.description
        }
        
        for field_name, field_value in search_fields.items():
            if field_value and query in field_value:
                start_pos = field_value.find(query)
                match = MatchInstance(
                    start_pos=start_pos,
                    end_pos=start_pos + len(query),
                    matched_text=query,
                    field_name=field_name
                )
                matches.append(match)
        
        return matches
    
    def _find_regex_matches(self, record: ReplacementRecord, request: PreferenceSearchRequest) -> List[MatchInstance]:
        """Find regex matches in record for highlighting."""
        import re
        matches = []
        
        try:
            pattern = re.compile(request.query, re.IGNORECASE if request.case_match.name == "IGNORE" else 0)
            
            search_fields = {
                'find_text': record.find_text,
                'replace_text': record.replace_text,
                'context': record.context,
                'description': record.description
            }
            
            for field_name, field_value in search_fields.items():
                if field_value:
                    for match in pattern.finditer(field_value):
                        match_instance = MatchInstance(
                            start_pos=match.start(),
                            end_pos=match.end(),
                            matched_text=match.group(),
                            field_name=field_name
                        )
                        matches.append(match_instance)
        except re.error:
            # Invalid regex, return empty matches
            pass
        
        return matches
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
```

## UI Implementation

### ReplacementRulesPanel

**Purpose:** Main panel widget integrating all components.

**File:** `panels/preferences/replacement_rules_panel.py`

```python
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                               QPushButton, QComboBox, QLabel, QMessageBox)
from PySide6.QtCore import Signal, Qt
from typing import List, Optional
from lg import logger

from widgets.shared.paged_table_widget import PagedTableWidget
from widgets.shared.preference_search_bar import PreferenceSearchBar
from widgets.shared.import_export_widget import ImportExportWidget
from widgets.shared.settings_group_widget import SettingsGroupWidget
from services.replacement_rules_service import ReplacementRulesService
from .replacement_record import ReplacementRecord
from .replacement_editor_widget import ReplacementEditorWidget
from .replacement_bulk_operations_widget import ReplacementBulkOperationsWidget

class ReplacementRulesPanel(QWidget):
    """Text replacement rules management panel."""
    
    # Signals
    rulesChanged = Signal()
    ruleSelected = Signal(ReplacementRecord)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Initialize service
        self.rules_service = ReplacementRulesService("replacement_rules.db")
        
        # State
        self.current_page = 1
        self.page_size = 50
        self.current_filter = "All"
        self.search_query = ""
        
        self._setup_ui()
        self._setup_connections()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Setup the panel UI."""
        layout = QVBoxLayout(self)
        
        # Main splitter
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Top section: Table and controls
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Search and filter controls
        controls_layout = QHBoxLayout()
        
        # Search bar
        self.search_bar = PreferenceSearchBar(
            table_type="replacement rules",
            show_scope_selector=True,
            show_export_button=True
        )
        controls_layout.addWidget(self.search_bar, 1)
        
        # Context filter
        self.context_filter = QComboBox()
        self.context_filter.setMinimumWidth(120)
        controls_layout.addWidget(QLabel("Context:"))
        controls_layout.addWidget(self.context_filter)
        
        # Enabled filter
        self.enabled_filter = QComboBox()
        self.enabled_filter.addItems(["All Rules", "Enabled Only", "Disabled Only"])
        controls_layout.addWidget(QLabel("Show:"))
        controls_layout.addWidget(self.enabled_filter)
        
        top_layout.addLayout(controls_layout)
        
        # Rules table
        self.table_columns = [
            {'field': 'enabled', 'title': 'Enabled', 'width': 70, 'type': 'checkbox'},
            {'field': 'id', 'title': 'ID', 'width': 50},
            {'field': 'find_text', 'title': 'Find Text', 'width': 200},
            {'field': 'replace_text', 'title': 'Replace Text', 'width': 200},
            {'field': 'context', 'title': 'Context', 'width': 100},
            {'field': 'options_string', 'title': 'Options', 'width': 80},
            {'field': 'usage_count', 'title': 'Used', 'width': 60},
            {'field': 'modified_date', 'title': 'Modified', 'width': 120, 'type': 'datetime'}
        ]
        
        self.rules_table = PagedTableWidget(
            column_configs=self.table_columns,
            page_size=self.page_size,
            enable_search=False,  # We have our own search bar
            enable_export=True
        )
        top_layout.addWidget(self.rules_table)
        
        # Bulk operations
        self.bulk_operations = ReplacementBulkOperationsWidget()
        top_layout.addWidget(self.bulk_operations)
        
        splitter.addWidget(top_widget)
        
        # Bottom section: Rule editor and import/export
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Rule editor
        self.rule_editor = ReplacementEditorWidget()
        bottom_layout.addWidget(self.rule_editor)
        
        # Import/export
        self.import_export = ImportExportWidget(
            supported_formats=['json', 'csv', 'xml', 'yaml', 'sqlite'],
            enable_drag_drop=True,
            show_progress=True
        )
        bottom_layout.addWidget(self.import_export)
        
        splitter.addWidget(bottom_widget)
        
        # Set splitter proportions
        splitter.setSizes([600, 300])
        
    def _setup_connections(self):
        """Setup signal connections."""
        # Search and filter
        self.search_bar.searchTriggered.connect(self._on_search_triggered)
        self.search_bar.searchCleared.connect(self._on_search_cleared)
        self.context_filter.currentTextChanged.connect(self._on_filter_changed)
        self.enabled_filter.currentTextChanged.connect(self._on_filter_changed)
        
        # Table
        self.rules_table.itemSelected.connect(self._on_rule_selected)
        self.rules_table.itemsSelectionChanged.connect(self._on_selection_changed)
        self.rules_table.pageChanged.connect(self._on_page_changed)
        self.rules_table.contextMenuRequested.connect(self._on_context_menu)
        
        # Bulk operations
        self.bulk_operations.enableSelectedRequested.connect(self._on_enable_selected)
        self.bulk_operations.disableSelectedRequested.connect(self._on_disable_selected)
        self.bulk_operations.deleteSelectedRequested.connect(self._on_delete_selected)
        self.bulk_operations.testSelectedRequested.connect(self._on_test_selected)
        
        # Rule editor
        self.rule_editor.ruleAdded.connect(self._on_rule_added)
        self.rule_editor.ruleUpdated.connect(self._on_rule_updated)
        self.rule_editor.ruleCleared.connect(self._on_rule_cleared)
        
        # Import/export
        self.import_export.importRequested.connect(self._on_import_requested)
        self.import_export.exportRequested.connect(self._on_export_requested)
        
    def _load_initial_data(self):
        """Load initial data into the panel."""
        # Load contexts for filter
        contexts = self.rules_service.get_available_contexts()
        self.context_filter.addItems(contexts)
        
        # Load first page of rules
        self._refresh_table()
        
    def _refresh_table(self):
        """Refresh the table with current filters."""
        try:
            # Determine filter parameters
            context_filter = self.context_filter.currentText()
            enabled_only = self.enabled_filter.currentText() == "Enabled Only"
            disabled_only = self.enabled_filter.currentText() == "Disabled Only"
            
            if self.search_query:
                # Use search results
                from workspace.find_replace_types import PreferenceSearchRequest, FindReplaceScope, ReplacementCaseMatch
                
                search_request = PreferenceSearchRequest(
                    query=self.search_query,
                    scope=FindReplaceScope.ALL,
                    case_match=ReplacementCaseMatch.IGNORE,
                    use_regex=False,
                    table_type="replacement"
                )
                
                search_results = self.rules_service.search_records(search_request)
                
                # Convert search results to table data
                table_data = []
                for result in search_results:
                    record = result.record
                    if self._matches_filters(record, enabled_only, disabled_only, context_filter):
                        table_data.append(record.to_dict())
                
                self.rules_table.set_data(table_data, len(table_data))
                self.rules_table.apply_search_results(search_results)
            else:
                # Use paginated data
                records = self.rules_service.get_page_records(
                    page=self.current_page,
                    page_size=self.page_size,
                    enabled_only=enabled_only,
                    context_filter=context_filter if context_filter != "All" else None
                )
                
                # Filter disabled only if needed
                if disabled_only:
                    records = [r for r in records if not r.enabled]
                
                table_data = [record.to_dict() for record in records]
                total_count = self.rules_service.get_total_count(enabled_only, context_filter)
                
                self.rules_table.set_data(table_data, total_count)
                
        except Exception as e:
            logger.error(f"Failed to refresh table: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load replacement rules: {e}")
    
    def _matches_filters(self, record: ReplacementRecord, enabled_only: bool, 
                        disabled_only: bool, context_filter: str) -> bool:
        """Check if record matches current filters."""
        if enabled_only and not record.enabled:
            return False
        if disabled_only and record.enabled:
            return False
        if context_filter != "All" and record.context != context_filter:
            return False
        return True
    
    # Event handlers
    def _on_search_triggered(self, query: str, options: dict):
        """Handle search trigger."""
        self.search_query = query
        self.current_page = 1
        self._refresh_table()
        
    def _on_search_cleared(self):
        """Handle search clear."""
        self.search_query = ""
        self.current_page = 1
        self._refresh_table()
        
    def _on_filter_changed(self):
        """Handle filter changes."""
        self.current_page = 1
        self._refresh_table()
        
    def _on_page_changed(self, page: int):
        """Handle page changes."""
        self.current_page = page
        self._refresh_table()
        
    def _on_rule_selected(self, row: int, item_data: dict):
        """Handle rule selection."""
        try:
            record = ReplacementRecord.from_dict(item_data)
            self.rule_editor.set_record(record)
            self.ruleSelected.emit(record)
        except Exception as e:
            logger.error(f"Failed to handle rule selection: {e}")
            
    def _on_selection_changed(self, selected_items: List[dict]):
        """Handle selection changes."""
        self.bulk_operations.set_selected_count(len(selected_items))
        
    def _on_context_menu(self, row: int, item_data: dict):
        """Handle context menu request."""
        # Implementation for context menu actions
        pass
        
    def _on_enable_selected(self):
        """Enable selected rules."""
        selected_items = self.rules_table.get_selected_items()
        for item in selected_items:
            record = ReplacementRecord.from_dict(item)
            record.enabled = True
            self.rules_service.save_record(record)
        
        self._refresh_table()
        self.rulesChanged.emit()
        
    def _on_disable_selected(self):
        """Disable selected rules."""
        selected_items = self.rules_table.get_selected_items()
        for item in selected_items:
            record = ReplacementRecord.from_dict(item)
            record.enabled = False
            self.rules_service.save_record(record)
        
        self._refresh_table()
        self.rulesChanged.emit()
        
    def _on_delete_selected(self):
        """Delete selected rules."""
        selected_items = self.rules_table.get_selected_items()
        if not selected_items:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(selected_items)} rule(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            record_ids = [item['id'] for item in selected_items if item.get('id')]
            deleted_count = self.rules_service.delete_records(record_ids)
            
            if deleted_count > 0:
                self._refresh_table()
                self.rulesChanged.emit()
                
                QMessageBox.information(
                    self, "Rules Deleted",
                    f"Successfully deleted {deleted_count} rule(s)."
                )
                
    def _on_test_selected(self):
        """Test selected rules."""
        # Implementation for testing selected rules
        pass
        
    def _on_rule_added(self, record: ReplacementRecord):
        """Handle new rule addition."""
        if self.rules_service.save_record(record):
            self._refresh_table()
            self.rulesChanged.emit()
            logger.info(f"Added new replacement rule: {record.find_text} -> {record.replace_text}")
        else:
            QMessageBox.warning(self, "Error", "Failed to save replacement rule.")
            
    def _on_rule_updated(self, record: ReplacementRecord):
        """Handle rule update."""
        if self.rules_service.save_record(record):
            self._refresh_table()
            self.rulesChanged.emit()
            logger.info(f"Updated replacement rule: {record.find_text} -> {record.replace_text}")
        else:
            QMessageBox.warning(self, "Error", "Failed to update replacement rule.")
            
    def _on_rule_cleared(self):
        """Handle rule editor clear."""
        # Clear any highlighting or selection
        pass
        
    def _on_import_requested(self, file_path: str, options: dict):
        """Handle import request."""
        # Implementation for importing rules from file
        pass
        
    def _on_export_requested(self, file_path: str, format: str, options: dict):
        """Handle export request."""
        # Implementation for exporting rules to file
        pass
        
    # Public interface
    def get_selected_rules(self) -> List[ReplacementRecord]:
        """Get currently selected rules."""
        selected_items = self.rules_table.get_selected_items()
        return [ReplacementRecord.from_dict(item) for item in selected_items]
        
    def refresh_data(self):
        """Refresh all data in the panel."""
        self._refresh_table()
        
        # Refresh contexts
        contexts = self.rules_service.get_available_contexts()
        current_context = self.context_filter.currentText()
        self.context_filter.clear()
        self.context_filter.addItems(contexts)
        
        # Restore context selection if still available
        index = self.context_filter.findText(current_context)
        if index >= 0:
            self.context_filter.setCurrentIndex(index)
```

## File Format Support

### Import/Export Handlers

The panel supports multiple file formats for importing and exporting replacement rules:

1. **JSON** - Human-readable format with full metadata
2. **CSV** - Simple tabular format for spreadsheet compatibility  
3. **XML** - Structured format with validation support
4. **YAML** - Human-friendly format with comments support
5. **SQLite** - Database format for large rule sets
6. **AutoHotkey** - Direct compatibility with AutoHotkey scripts

Each format handler implements a standard interface for consistent behavior across formats.

## Testing Strategy

### Unit Tests

```python
class TestReplacementRecord(unittest.TestCase):
    """Test ReplacementRecord functionality."""
    
    def test_rule_validation(self):
        """Test rule validation logic."""
        # Valid rule
        rule = ReplacementRecord(find_text="test", replace_text="result")
        self.assertTrue(rule.is_valid)
        
        # Invalid regex
        rule = ReplacementRecord(find_text="[invalid", use_regex=True)
        self.assertFalse(rule.is_valid)
        
    def test_replacement_execution(self):
        """Test rule execution."""
        rule = ReplacementRecord(find_text="hello", replace_text="hi")
        result = rule.test_replacement("hello world")
        self.assertEqual(result, "hi world")

class TestReplacementRulesService(unittest.TestCase):
    """Test ReplacementRulesService functionality."""
    
    def setUp(self):
        self.service = ReplacementRulesService(":memory:")  # In-memory database
        
    def test_save_and_retrieve(self):
        """Test saving and retrieving records."""
        rule = ReplacementRecord(find_text="test", replace_text="result")
        self.assertTrue(self.service.save_record(rule))
        
        records = self.service.get_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].find_text, "test")
```

This design provides a comprehensive, feature-rich text replacement management system that integrates seamlessly with the overall preferences architecture while maintaining high performance and usability.
This design provides a comprehensive, feature-rich text replacement management system that integrates seamlessly with the overall preferences architecture while maintaining high performance and usability.
