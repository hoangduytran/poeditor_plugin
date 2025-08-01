# Translation Database Service Design

**Date**: July 24, 2025  
**Component**: Translation Database Service  
**Status**: Design  
**Dependencies**: Core Services Framework

## 1. Overview

The Translation Database Service provides a centralized repository for storing, retrieving, and managing translation history across multiple PO files. It maintains a persistent SQLite database of translations with version tracking, enabling powerful features such as translation suggestions, fuzzy matching, and comprehensive search capabilities.

This service is a core component of the POEditor plugin, providing critical functionality for improving translation quality and consistency while building an ever-growing knowledge base of translations.

## 2. Core Architecture

### 2.1 Component Structure

```
Translation Database Service
├── Database Layer
│   ├── Schema Management
│   ├── Connection Pooling
│   └── Query Optimization
├── Data Model Layer
│   ├── DatabasePORecord
│   └── Translation Version
├── Service Interface
│   ├── Suggestion Provider
│   ├── Search Interface
│   └── Version Management
└── Integration Layer
    ├── Plugin API Adapter
    ├── Settings Integration
    └── Event System
```

### 2.2 Database Schema

**english_text Table (Source Text Repository)**
```sql
CREATE TABLE english_text (
    unique_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    en_text     TEXT NOT NULL,              -- Source message (msgid)
    context     TEXT,                       -- Optional context (msgctxt)
    UNIQUE(en_text, context)                -- No duplicate source/context pairs
);
```

**tran_text Table (Translation Versions)**
```sql
CREATE TABLE tran_text (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_id   INTEGER NOT NULL,           -- Foreign key to english_text
    version_id  INTEGER NOT NULL,           -- Version number for this translation
    tran_text   TEXT NOT NULL,              -- Translation text
    source      TEXT DEFAULT '',            -- Source/origin of translation
    changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(unique_id) REFERENCES english_text(unique_id) ON DELETE CASCADE,
    UNIQUE(unique_id, version_id),          -- One version per entry
    UNIQUE(unique_id, tran_text)            -- No duplicate translations per entry
);
```

**Performance Indexes**
```sql
CREATE INDEX idx_english_text_en_text ON english_text(en_text);
CREATE INDEX idx_english_text_context ON english_text(context);
CREATE INDEX idx_tran_text_tran_text ON tran_text(tran_text);
CREATE INDEX idx_tran_text_unique_id ON tran_text(unique_id);
CREATE INDEX idx_tran_text_version ON tran_text(unique_id, version_id);
```

### 2.3 Core Service Interface

```python
class TranslationDatabaseService(Service):
    """Service for managing translation history database."""
    
    def __init__(self, api: PluginAPI):
        super().__init__(api)
        self._db_path = self._get_db_path()
        self._conn = None
        self._setup_database()
    
    # Core service methods
    def get_suggestions(self, msgid: str, context: str = None) -> List[DatabasePORecord]:
        """Get translation suggestions for a source text."""
        pass
        
    def add_translation(self, msgid: str, msgstr: str, context: str = None, 
                       source: str = "manual") -> bool:
        """Add a new translation to the database."""
        pass
        
    def search_translations(self, query: dict) -> List[DatabasePORecord]:
        """Search translations with multiple criteria."""
        pass
        
    def import_po_file(self, file_path: str, source: str = "file") -> int:
        """Import translations from a PO file into the database."""
        pass
        
    def export_po_file(self, file_path: str, filter_query: dict = None) -> int:
        """Export translations from database to a PO file."""
        pass
```

## 3. Data Model Components

### 3.1 DatabasePORecord

```python
@dataclass
class DatabasePORecord:
    """In-memory representation of a translation entry with version history."""
    
    unique_id: Optional[int] = None
    msgid: str = ""
    msgctxt: Optional[str] = None
    msgstr_versions: List[Tuple[int, str, str]] = field(default_factory=list)  # (version_id, text, source)
    
    def add_version(self, translation: str, source: str = "") -> bool:
        """Add a new translation version if it doesn't exist."""
        # Check for duplicates
        for _, text, _ in self.msgstr_versions:
            if text == translation:
                return False
                
        # Determine next version number
        next_version = 1
        if self.msgstr_versions:
            next_version = max(v[0] for v in self.msgstr_versions) + 1
            
        # Add new version
        self.msgstr_versions.append((next_version, translation, source))
        return True
    
    def get_latest_version(self) -> Optional[Tuple[int, str, str]]:
        """Get the most recent translation version."""
        if not self.msgstr_versions:
            return None
        return max(self.msgstr_versions, key=lambda v: v[0])
    
    def is_virtually_same(self, other_msgid: str, other_msgctxt: str = None) -> bool:
        """Check if this record is virtually the same as the given parameters."""
        # Simple case: exact match
        if self.msgid == other_msgid and self.msgctxt == other_msgctxt:
            return True
            
        # Fuzzy matching for similar content
        similarity = self._calculate_similarity(other_msgid, self.msgid)
        if similarity > 0.9:  # 90% similarity threshold
            return self.msgctxt == other_msgctxt
            
        return False
```

### 3.2 Translation Sources

```python
class TranslationSource(Enum):
    """Enum representing different sources of translations."""
    
    MANUAL = "manual"       # Manually entered by user
    FILE = "file"           # Imported from PO file
    WEB = "web"             # From translation service (Google, etc.)
    MEMORY = "memory"       # From translation memory
    MACHINE = "machine"     # From machine translation
    
    @classmethod
    def get_display_name(cls, source: str) -> str:
        """Get a user-friendly display name for the source."""
        mapping = {
            cls.MANUAL.value: "User Input",
            cls.FILE.value: "Imported File",
            cls.WEB.value: "Web Service",
            cls.MEMORY.value: "Translation Memory",
            cls.MACHINE.value: "Machine Translation"
        }
        return mapping.get(source, source)
```

## 4. Key Workflows

### 4.1 Getting Translation Suggestions

```python
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
        return sorted(fuzzy_records, key=lambda r: self._calculate_similarity(msgid, r.msgid), reverse=True)
    except Exception as e:
        from lg import logger
        logger.error(f"Error getting translation suggestions: {e}", exc_info=True)
        return []
```

### 4.2 Adding Translations

```python
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
```

### 4.3 Importing PO Files

```python
def import_po_file(self, file_path: str, source: str = "file") -> int:
    """Import translations from a PO file into the database."""
    try:
        # Open PO file
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
```

### 4.4 Advanced Search

```python
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
```

## 5. Implementation Details

### 5.1 Database Connection Management

```python
def _get_connection(self):
    """Get a connection to the database, creating it if needed."""
    if self._conn is None:
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        
        # Add custom functions
        self._conn.create_function("REGEXP", 2, self._regexp)
        
    return self._conn
    
def _setup_database(self):
    """Ensure the database schema exists."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS english_text (
            unique_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            en_text     TEXT NOT NULL,
            context     TEXT,
            UNIQUE(en_text, context)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tran_text (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_id   INTEGER NOT NULL,
            version_id  INTEGER NOT NULL,
            tran_text   TEXT NOT NULL,
            source      TEXT DEFAULT '',
            changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(unique_id) REFERENCES english_text(unique_id) ON DELETE CASCADE,
            UNIQUE(unique_id, version_id),
            UNIQUE(unique_id, tran_text)
        )
    """)
    
    # Create indexes if they don't exist
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_english_text_en_text ON english_text(en_text)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_english_text_context ON english_text(context)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tran_text_tran_text ON tran_text(tran_text)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tran_text_unique_id ON tran_text(unique_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tran_text_version ON tran_text(unique_id, version_id)")
    
    conn.commit()
```

### 5.2 Record Management Operations

```python
def _get_exact_match(self, msgid: str, context: str = None) -> Optional[DatabasePORecord]:
    """Get an exact match for the source text and context."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT e.unique_id, e.en_text, e.context, 
               t.version_id, t.tran_text, t.source
        FROM english_text e
        LEFT JOIN tran_text t ON e.unique_id = t.unique_id
        WHERE e.en_text = ? AND (e.context IS ? OR e.context = ?)
        ORDER BY t.version_id DESC
    """
    
    cursor.execute(query, (msgid, context, context))
    rows = cursor.fetchall()
    
    if not rows:
        return None
        
    # Create record
    record = DatabasePORecord(
        unique_id=rows[0]['unique_id'],
        msgid=rows[0]['en_text'],
        msgctxt=rows[0]['context']
    )
    
    # Add versions
    for row in rows:
        if row['version_id'] is not None:
            record.msgstr_versions.append((
                row['version_id'],
                row['tran_text'],
                row['source']
            ))
            
    return record

def _create_record(self, record: DatabasePORecord) -> bool:
    """Create a new record in the database."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO english_text (en_text, context) VALUES (?, ?)",
        (record.msgid, record.msgctxt)
    )
    
    record.unique_id = cursor.lastrowid
    conn.commit()
    return True

def _save_version(self, unique_id: int, translation: str, source: str) -> bool:
    """Save a new translation version."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    # Get next version number
    cursor.execute(
        "SELECT MAX(version_id) FROM tran_text WHERE unique_id = ?",
        (unique_id,)
    )
    result = cursor.fetchone()
    next_version = 1
    if result[0] is not None:
        next_version = result[0] + 1
    
    # Insert new version
    cursor.execute(
        "INSERT INTO tran_text (unique_id, version_id, tran_text, source) VALUES (?, ?, ?, ?)",
        (unique_id, next_version, translation, source)
    )
    
    conn.commit()
    return True
```

### 5.3 Fuzzy Matching Implementation

```python
def _get_fuzzy_matches(self, msgid: str, context: str = None, threshold: float = 0.7) -> List[DatabasePORecord]:
    """Get fuzzy matches for the source text."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    # Get all potential candidates
    # This is a naive approach - for production we'd use more sophisticated methods
    cursor.execute("SELECT unique_id, en_text, context FROM english_text")
    candidates = cursor.fetchall()
    
    # Filter by similarity
    results = []
    for candidate in candidates:
        similarity = self._calculate_similarity(msgid, candidate['en_text'])
        if similarity >= threshold:
            # Context match increases score
            if context is not None and context == candidate['context']:
                similarity += 0.1
                
            # Get record with all versions
            record = self._get_record_by_id(candidate['unique_id'])
            if record:
                results.append((similarity, record))
                
    # Sort by similarity and return records
    return [record for _, record in sorted(results, key=lambda x: x[0], reverse=True)]

def _calculate_similarity(self, text1: str, text2: str) -> float:
    """Calculate similarity between two strings."""
    if not text1 or not text2:
        return 0.0
        
    # Simple Levenshtein distance ratio
    from difflib import SequenceMatcher
    return SequenceMatcher(None, text1, text2).ratio()
```

## 6. Integration with Plugin Architecture

### 6.1 Service Registration

```python
class TranslationDatabasePlugin:
    """Plugin that provides the Translation Database Service."""
    
    def register(self, api: PluginAPI):
        # Register service
        service = TranslationDatabaseService(api)
        api.register_service("translation_db", service)
        
        # Register settings panel
        api.register_settings_panel(
            "Translation History",
            lambda: TranslationHistoryPanel(service),
            ":/icons/history.svg"
        )
        
        # Register commands
        api.register_command(
            "translation_db.import",
            "Import Translations from PO File",
            self._import_translations
        )
        
        api.register_command(
            "translation_db.export",
            "Export Translation Database to PO File",
            self._export_translations
        )
        
    def _import_translations(self):
        # Implementation of import command
        pass
        
    def _export_translations(self):
        # Implementation of export command
        pass
```

### 6.2 Event System Integration

```python
# In TranslationDatabaseService.__init__
def __init__(self, api: PluginAPI):
    super().__init__(api)
    
    # Subscribe to events
    api.subscribe_event("poeditor.translation_updated", self._on_translation_updated)
    api.subscribe_event("settings.changed.translation_db", self._on_settings_changed)
    
def _on_translation_updated(self, event_data: dict):
    """Handle translation updated event."""
    msgid = event_data.get("entry_id")
    msgstr = event_data.get("text")
    context = event_data.get("context")
    
    if msgid and msgstr:
        self.add_translation(msgid, msgstr, context, "manual")
```

### 6.3 Settings Integration

```python
def _get_fuzzy_threshold(self) -> float:
    """Get fuzzy matching threshold from settings."""
    settings = QSettings("POEditor", "Settings")
    return float(settings.value("translation_db/fuzzy_threshold", 0.7))
    
def _get_db_path(self) -> str:
    """Get database path from settings."""
    settings = QSettings("POEditor", "Settings")
    default_path = os.path.join(
        os.path.expanduser("~"),
        ".poeditor",
        "translation_db.sqlite"
    )
    return settings.value("translation_db/db_path", default_path)
    
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

## 7. Performance Optimizations

### 7.1 Connection Pooling

```python
class ConnectionPool:
    """Simple connection pool for SQLite."""
    
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.available = []
        self.in_use = set()
        self._lock = threading.Lock()
        
    def get_connection(self):
        """Get a connection from the pool."""
        with self._lock:
            if self.available:
                conn = self.available.pop()
            elif len(self.in_use) < self.max_connections:
                conn = self._create_connection()
            else:
                # Wait for a connection to become available
                raise Exception("Connection pool exhausted")
                
            self.in_use.add(conn)
            return conn
            
    def release_connection(self, conn):
        """Return a connection to the pool."""
        with self._lock:
            self.in_use.remove(conn)
            self.available.append(conn)
            
    def _create_connection(self):
        """Create a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
```

### 7.2 Query Optimization

```python
def _optimize_database(self):
    """Optimize database performance."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    # Analyze for query optimization
    cursor.execute("ANALYZE")
    
    # Optimize indexes
    cursor.execute("REINDEX")
    
    # Compact the database
    cursor.execute("VACUUM")
    
    conn.commit()
```

### 7.3 Caching Mechanisms

```python
class LRUCache:
    """Simple LRU cache implementation."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        
    def get(self, key):
        """Get item from cache."""
        if key not in self.cache:
            return None
            
        # Move to the end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value
        
    def put(self, key, value):
        """Put item in cache."""
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Remove oldest item
            self.cache.popitem(last=False)
            
        self.cache[key] = value
        
# In TranslationDatabaseService
def __init__(self, api: PluginAPI):
    # ... other initialization
    self._exact_match_cache = LRUCache(100)
    self._record_id_cache = LRUCache(500)
    
def _get_exact_match(self, msgid: str, context: str = None) -> Optional[DatabasePORecord]:
    """Get an exact match for the source text and context, using cache."""
    cache_key = f"{msgid}|{context}"
    cached_result = self._exact_match_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
        
    # Fetch from database
    record = self._fetch_exact_match(msgid, context)
    
    # Cache result
    self._exact_match_cache.put(cache_key, record)
    return record
```

## 8. Error Handling and Recovery

### 8.1 Transaction Management

```python
def _execute_with_transaction(self, callback):
    """Execute operations within a transaction."""
    conn = self._get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        
        result = callback(cursor)
        
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        from lg import logger
        logger.error(f"Transaction error: {e}", exc_info=True)
        raise
```

### 8.2 Database Error Recovery

```python
def _ensure_database_integrity(self):
    """Check and repair database integrity."""
    conn = self._get_connection()
    cursor = conn.cursor()
    
    try:
        # Check integrity
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        if result != "ok":
            from lg import logger
            logger.error(f"Database integrity check failed: {result}")
            
            # Create backup
            self._create_backup()
            
            # Try to recover
            cursor.execute("PRAGMA integrity_check(1)")
            errors = cursor.fetchall()
            
            # Log specific errors
            for error in errors:
                logger.error(f"Database integrity error: {error[0]}")
                
            # Attempt recovery operations
            cursor.execute("VACUUM")
            
            return False
        
        return True
    except Exception as e:
        from lg import logger
        logger.error(f"Database integrity check error: {e}", exc_info=True)
        return False
        
def _create_backup(self):
    """Create a backup of the database."""
    try:
        backup_path = self._db_path + f".backup_{int(time.time())}"
        shutil.copy2(self._db_path, backup_path)
        
        from lg import logger
        logger.info(f"Created database backup: {backup_path}")
        return True
    except Exception as e:
        from lg import logger
        logger.error(f"Error creating database backup: {e}", exc_info=True)
        return False
```

## 9. User Interface Integration

### 9.1 Translation History Panel

```python
class TranslationHistoryPanel(QWidget):
    """Settings panel for managing translation history."""
    
    def __init__(self, db_service: TranslationDatabaseService):
        super().__init__()
        self.db_service = db_service
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Import/Export buttons
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import PO File")
        self.export_button = QPushButton("Export to PO File")
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search translations...")
        layout.addWidget(self.search_bar)
        
        # Table view
        self.table = QTableView()
        self.table_model = TranslationTableModel()
        self.table.setModel(self.table_model)
        layout.addWidget(self.table)
        
        # Status bar
        self.status_label = QLabel("0 entries in database")
        layout.addWidget(self.status_label)
        
    def _connect_signals(self):
        """Connect UI signals."""
        self.import_button.clicked.connect(self._on_import_clicked)
        self.export_button.clicked.connect(self._on_export_clicked)
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        self.table.doubleClicked.connect(self._on_table_double_clicked)
        
    def _on_import_clicked(self):
        """Handle import button click."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("PO Files (*.po);;All Files (*)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec() == QFileDialog.Accepted:
            files = file_dialog.selectedFiles()
            if files:
                file_path = files[0]
                count = self.db_service.import_po_file(file_path)
                QMessageBox.information(
                    self,
                    "Import Complete",
                    f"Imported {count} translations from {os.path.basename(file_path)}."
                )
                self._update_table()
```

### 9.2 Suggestions UI Integration

```python
class SuggestionsPanel(QWidget):
    """Panel for displaying translation suggestions."""
    
    suggestion_selected = Signal(str)
    
    def __init__(self, db_service: TranslationDatabaseService, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self._current_msgid = ""
        self._current_context = None
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("Suggestions")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Table
        self.table = QTableView()
        self.table_model = SuggestionTableModel()
        self.table.setModel(self.table_model)
        layout.addWidget(self.table)
        
    def _connect_signals(self):
        """Connect UI signals."""
        self.table.doubleClicked.connect(self._on_table_double_clicked)
        
    def update_suggestions(self, msgid: str, context: str = None):
        """Update suggestions for the given msgid and context."""
        self._current_msgid = msgid
        self._current_context = context
        
        suggestions = self.db_service.get_suggestions(msgid, context)
        self.table_model.set_suggestions(suggestions)
        
    def _on_table_double_clicked(self, index):
        """Handle double click on table."""
        if index.isValid():
            row = index.row()
            text = self.table_model.get_translation_at(row)
            self.suggestion_selected.emit(text)
```

## 10. Testing Strategy

### 10.1 Unit Tests

```python
class TestTranslationDatabaseService(unittest.TestCase):
    """Unit tests for the Translation Database Service."""
    
    def setUp(self):
        """Set up the test environment."""
        # Use in-memory database for testing
        self.api_mock = MagicMock()
        self.service = TranslationDatabaseService(self.api_mock)
        self.service._db_path = ":memory:"
        self.service._setup_database()
        
    def test_add_translation(self):
        """Test adding a translation."""
        # Add translation
        result = self.service.add_translation("test", "test_translation", None, "test")
        self.assertTrue(result)
        
        # Verify it was added
        suggestions = self.service.get_suggestions("test")
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].msgid, "test")
        self.assertEqual(len(suggestions[0].msgstr_versions), 1)
        self.assertEqual(suggestions[0].msgstr_versions[0][1], "test_translation")
        
    def test_get_suggestions_fuzzy(self):
        """Test getting fuzzy matches."""
        # Add some translations
        self.service.add_translation("hello world", "hola mundo", None, "test")
        self.service.add_translation("hello everyone", "hola a todos", None, "test")
        self.service.add_translation("goodbye world", "adiós mundo", None, "test")
        
        # Get fuzzy matches
        suggestions = self.service.get_suggestions("hello there")
        
        # Should match "hello world" and "hello everyone" but not "goodbye world"
        self.assertEqual(len(suggestions), 2)
        self.assertTrue(any(s.msgid == "hello world" for s in suggestions))
        self.assertTrue(any(s.msgid == "hello everyone" for s in suggestions))
```

### 10.2 Integration Tests

```python
class TestTranslationDatabaseIntegration(unittest.TestCase):
    """Integration tests for the Translation Database Service."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        # Mock plugin API
        self.api_mock = MagicMock()
        
        # Create service instance
        self.service = TranslationDatabaseService(self.api_mock)
        self.service._db_path = self.temp_db.name
        self.service._setup_database()
        
    def tearDown(self):
        """Clean up after tests."""
        # Close connection
        if self.service._conn:
            self.service._conn.close()
            
        # Remove temporary database file
        os.unlink(self.temp_db.name)
        
    def test_import_export(self):
        """Test importing and exporting PO files."""
        # Create temporary PO file
        with tempfile.NamedTemporaryFile(suffix='.po', delete=False) as f:
            po_file = polib.POFile()
            
            # Add some entries
            entry1 = polib.POEntry(msgid="test1", msgstr="test1_translation")
            entry2 = polib.POEntry(msgid="test2", msgstr="test2_translation", msgctxt="context")
            po_file.append(entry1)
            po_file.append(entry2)
            
            po_file.save(f.name)
            
            # Import the file
            count = self.service.import_po_file(f.name, "test")
            self.assertEqual(count, 2)
            
        # Export to another file
        with tempfile.NamedTemporaryFile(suffix='.po', delete=False) as f:
            export_count = self.service.export_po_file(f.name)
            self.assertEqual(export_count, 2)
            
            # Load exported file
            exported_po = polib.pofile(f.name)
            self.assertEqual(len(exported_po), 2)
            
            # Check entries
            self.assertTrue(any(e.msgid == "test1" and e.msgstr == "test1_translation" for e in exported_po))
            self.assertTrue(any(e.msgid == "test2" and e.msgstr == "test2_translation" and e.msgctxt == "context" for e in exported_po))
```

## 11. Future Enhancements

### 11.1 Advanced Features

- **Neural Fuzzy Matching**: Use embeddings for better similarity detection
- **Translation Memory Exchange**: Support for TMX format import/export
- **Quality Scoring**: Rate translations based on usage patterns and feedback
- **Terminology Management**: Integrated glossary for consistent translations
- **Multi-user Support**: Collaborative database access with user attribution

### 11.2 Performance Improvements

- **Full-text Search**: SQLite FTS5 for more efficient text searching
- **Incremental Indexing**: Smart indexing strategies for large databases
- **Distributed Architecture**: Support for shared remote databases
- **Batch Processing**: Optimized bulk operations for large imports

### 11.3 Integration Expansions

- **Cloud Sync**: Synchronization with cloud-based translation memories
- **Machine Translation**: Direct integration with translation services
- **Version Control**: Git-like branching and merging of translations
- **Analytics Dashboard**: Usage statistics and quality metrics

## 12. Conclusion

The Translation Database Service provides a powerful, persistent translation memory system that enhances the POEditor plugin with advanced suggestions, version tracking, and comprehensive search capabilities. By leveraging an efficient SQLite database with optimized queries and a well-designed service interface, this component delivers excellent performance while maintaining compatibility with the plugin architecture.

The service's modular design enables easy integration with other components like the POEditor Tab and Settings panels, while its extensible architecture supports future enhancements such as neural fuzzy matching and cloud synchronization. Through careful error handling and performance optimization, the Translation Database Service ensures reliable operation even with large translation databases.
