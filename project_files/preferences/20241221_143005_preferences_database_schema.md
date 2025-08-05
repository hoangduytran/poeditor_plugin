# Preferences System: Database Schema

## Overview
This document defines the database schema and data models for the preferences system, providing a comprehensive design for data persistence across the application.

## Database Architecture

The preferences system uses SQLite as its primary database technology for:

1. Application settings storage
2. Translation history database
3. Text replacement rules
4. Plugin data persistence
5. Usage statistics and telemetry

## Core Schema Design

### Settings Database

The main settings database is stored in `settings.db` with the following tables:

#### Settings Table
Stores all application settings using a key-value pattern:

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    type TEXT,
    scope TEXT DEFAULT 'app',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `key`: Setting identifier (dot notation for namespacing)
- `value`: Setting value stored as JSON or simple types
- `type`: Data type (string, boolean, integer, float, json)
- `scope`: Namespace for settings (app, plugin:id, etc.)
- `updated_at`: Last modification timestamp

#### Schemas Table
Defines structure for complex settings objects:

```sql
CREATE TABLE schemas (
    id TEXT PRIMARY KEY,
    schema TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    description TEXT
);
```

- `id`: Schema identifier 
- `schema`: JSON Schema definition
- `version`: Schema version number
- `description`: Human-readable description

### Translation History Database

The translation history database is stored in `translation_history.db` with these tables:

#### Entries Table
Stores source text entries:

```sql
CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    source_text TEXT NOT NULL,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_id TEXT,
    source_lang TEXT DEFAULT 'en',
    UNIQUE(source_text, context, source_lang)
);

CREATE INDEX idx_entries_text ON entries(source_text);
CREATE INDEX idx_entries_context ON entries(context);
CREATE INDEX idx_entries_project ON entries(project_id);
CREATE INDEX idx_entries_accessed ON entries(last_accessed);
```

#### Versions Table
Stores translation versions for entries:

```sql
CREATE TABLE versions (
    id TEXT PRIMARY KEY,
    entry_id TEXT NOT NULL,
    translation TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    fuzzy BOOLEAN DEFAULT 0,
    source TEXT DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
);

CREATE INDEX idx_versions_entry ON versions(entry_id);
CREATE INDEX idx_versions_target_lang ON versions(target_lang);
```

#### Metadata Table
Stores additional metadata for entries and versions:

```sql
CREATE TABLE metadata (
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL, -- 'entry' or 'version'
    key TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY(target_id, target_type, key)
);

CREATE INDEX idx_metadata_target ON metadata(target_id, target_type);
```

### Text Replacements Database

The text replacements database is stored in `replacements.db` with these tables:

#### Rules Table
Stores text replacement rules:

```sql
CREATE TABLE rules (
    id TEXT PRIMARY KEY,
    pattern TEXT NOT NULL,
    replacement TEXT NOT NULL,
    is_regex BOOLEAN DEFAULT 0,
    case_sensitive BOOLEAN DEFAULT 1,
    enabled BOOLEAN DEFAULT 1,
    category TEXT DEFAULT 'General',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority INTEGER DEFAULT 0
);

CREATE INDEX idx_rules_category ON rules(category);
CREATE INDEX idx_rules_enabled ON rules(enabled);
```

#### Rule Conditions Table
Stores conditions for when rules apply:

```sql
CREATE TABLE rule_conditions (
    rule_id TEXT NOT NULL,
    condition_type TEXT NOT NULL, -- 'source_lang', 'target_lang', 'project', 'file'
    value TEXT NOT NULL,
    FOREIGN KEY(rule_id) REFERENCES rules(id) ON DELETE CASCADE,
    PRIMARY KEY(rule_id, condition_type, value)
);

CREATE INDEX idx_conditions_rule ON rule_conditions(rule_id);
```

### Plugin Data Storage

Each plugin gets its own database file named `plugin_{id}.db` to prevent conflicts.

#### Plugin Settings Table
Stores plugin-specific settings:

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    type TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Plugin-Specific Tables
Plugins may create their own tables for data storage following naming conventions:

```sql
-- Example: Plugin-specific data table
CREATE TABLE plugin_data (
    id TEXT PRIMARY KEY,
    data_type TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Data Models

### Core Data Models

#### Setting
Represents an individual application setting:

```python
class Setting:
    """A single application setting."""
    
    def __init__(self, key: str, value: Any, type_name: str = None, scope: str = "app"):
        self.key = key
        self._value = value
        self.type = type_name or self._infer_type(value)
        self.scope = scope
        self.updated_at = datetime.now()
        
    @property
    def value(self) -> Any:
        """Get the typed value."""
        return self._convert_from_storage(self._value, self.type)
        
    @value.setter
    def value(self, new_value: Any) -> None:
        """Set and convert the value for storage."""
        self._value = self._convert_to_storage(new_value, self.type)
        self.updated_at = datetime.now()
        
    def _infer_type(self, value: Any) -> str:
        """Infer the type from the value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, (dict, list)):
            return "json"
        else:
            return "string"
        
    def _convert_to_storage(self, value: Any, type_name: str) -> str:
        """Convert a value to string for storage."""
        if type_name == "json":
            return json.dumps(value)
        return str(value)
        
    def _convert_from_storage(self, value: str, type_name: str) -> Any:
        """Convert a stored value to its native type."""
        if type_name == "boolean":
            return value.lower() in ("true", "1", "yes", "y")
        elif type_name == "integer":
            return int(value)
        elif type_name == "float":
            return float(value)
        elif type_name == "json":
            return json.loads(value)
        return value
```

#### Schema
Defines the structure for complex settings:

```python
class Schema:
    """JSON Schema definition for complex settings."""
    
    def __init__(self, id: str, schema: dict, version: int = 1, description: str = ""):
        self.id = id
        self.schema = schema
        self.version = version
        self.description = description
        
    def validate(self, data: Any) -> tuple[bool, list[str]]:
        """Validate data against this schema."""
        # Use jsonschema library to validate
        # Return (is_valid, [error_messages])
        
    @classmethod
    def from_file(cls, file_path: str) -> 'Schema':
        """Create a schema from a JSON Schema file."""
```

### Translation History Models

#### TranslationEntry
Represents a source text and its translations:

```python
class TranslationEntry:
    """A source text entry in the translation history."""
    
    def __init__(self, 
                 source_text: str,
                 context: Optional[str] = None,
                 id: Optional[str] = None,
                 project_id: Optional[str] = None,
                 source_lang: str = "en"):
        self.id = id or str(uuid.uuid4())
        self.source_text = source_text
        self.context = context
        self.created_at = datetime.now()
        self.last_accessed = self.created_at
        self.project_id = project_id
        self.source_lang = source_lang
        self.versions = []  # List[TranslationVersion]
        self.metadata = {}  # Dict[str, Any]
        
    def add_version(self, 
                    translation: str,
                    target_lang: str,
                    fuzzy: bool = False,
                    source: str = "manual") -> 'TranslationVersion':
        """Add a new translation version."""
        version = TranslationVersion(
            translation=translation,
            target_lang=target_lang,
            fuzzy=fuzzy,
            source=source
        )
        version.entry_id = self.id
        self.versions.append(version)
        return version
        
    def latest_version(self, target_lang: Optional[str] = None) -> Optional['TranslationVersion']:
        """Get the most recent version, optionally filtered by language."""
        if not self.versions:
            return None
            
        if target_lang:
            lang_versions = [v for v in self.versions if v.target_lang == target_lang]
            return max(lang_versions, key=lambda v: v.created_at) if lang_versions else None
        
        return max(self.versions, key=lambda v: v.created_at)
        
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
```

#### TranslationVersion
Represents a single translation of a source text:

```python
class TranslationVersion:
    """A specific translation version."""
    
    def __init__(self,
                 translation: str,
                 target_lang: str,
                 fuzzy: bool = False,
                 source: str = "manual",
                 id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.entry_id = None  # Set when added to an entry
        self.translation = translation
        self.target_lang = target_lang
        self.fuzzy = fuzzy
        self.source = source
        self.created_at = datetime.now()
        self.metadata = {}  # Dict[str, Any]
        
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
```

### Text Replacement Models

#### ReplacementRule
Represents a text replacement rule:

```python
class ReplacementRule:
    """A rule for automatic text replacement."""
    
    def __init__(self,
                 pattern: str,
                 replacement: str,
                 is_regex: bool = False,
                 case_sensitive: bool = True,
                 enabled: bool = True,
                 category: str = "General",
                 description: str = "",
                 id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.pattern = pattern
        self.replacement = replacement
        self.is_regex = is_regex
        self.case_sensitive = case_sensitive
        self.enabled = enabled
        self.category = category
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.priority = 0
        self.conditions = []  # List[RuleCondition]
        
    def add_condition(self, condition_type: str, value: str) -> 'RuleCondition':
        """Add a condition for when this rule applies."""
        condition = RuleCondition(condition_type, value)
        self.conditions.append(condition)
        return condition
        
    def applies_to(self, context: dict) -> bool:
        """Check if this rule applies in the given context."""
        # If no conditions, rule applies everywhere
        if not self.conditions:
            return True
            
        # Group conditions by type
        by_type = {}
        for condition in self.conditions:
            if condition.condition_type not in by_type:
                by_type[condition.condition_type] = []
            by_type[condition.condition_type].append(condition.value)
        
        # Check each condition type
        for cond_type, values in by_type.items():
            if cond_type in context:
                # If any value matches for this condition type, it passes
                if context[cond_type] not in values:
                    return False
            else:
                return False
                
        return True
        
    def apply(self, text: str) -> tuple[str, int]:
        """Apply this rule to text and return (result, count)."""
        if not self.enabled:
            return text, 0
            
        if self.is_regex:
            pattern = re.compile(self.pattern, 
                               0 if self.case_sensitive else re.IGNORECASE)
            result, count = re.subn(pattern, self.replacement, text)
            return result, count
        else:
            if self.case_sensitive:
                result = text.replace(self.pattern, self.replacement)
                count = (len(text) - len(result)) // (len(self.pattern) - len(self.replacement)) if len(self.pattern) != len(self.replacement) else 0
                if count == 0 and text != result:
                    count = 1
            else:
                pattern = re.compile(re.escape(self.pattern), re.IGNORECASE)
                result, count = re.subn(pattern, self.replacement, text)
                
            return result, count
        
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
```

#### RuleCondition
Represents a condition for when a rule applies:

```python
class RuleCondition:
    """A condition for when a replacement rule applies."""
    
    def __init__(self, condition_type: str, value: str):
        self.condition_type = condition_type  # 'source_lang', 'target_lang', etc.
        self.value = value
        
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "condition_type": self.condition_type,
            "value": self.value
        }
```

## Database Service Layer

### Database Manager
Central manager for database connections:

```python
class DatabaseManager:
    """Manages database connections and access."""
    
    def __init__(self, app_data_dir: str):
        self._app_data_dir = app_data_dir
        self._connections = {}  # Dict[str, sqlite3.Connection]
        self._ensure_data_dir()
        
    def _ensure_data_dir(self) -> None:
        """Create the application data directory if needed."""
        os.makedirs(self._app_data_dir, exist_ok=True)
        
    def get_connection(self, db_name: str) -> sqlite3.Connection:
        """Get a database connection, creating if needed."""
        if db_name in self._connections:
            return self._connections[db_name]
            
        db_path = os.path.join(self._app_data_dir, f"{db_name}.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        self._connections[db_name] = conn
        return conn
        
    def close_all(self) -> None:
        """Close all database connections."""
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()
        
    def close(self, db_name: str) -> None:
        """Close a specific database connection."""
        if db_name in self._connections:
            self._connections[db_name].close()
            del self._connections[db_name]
```

### Settings Database Service

```python
class SettingsDatabaseService:
    """Service for accessing the settings database."""
    
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager
        self._conn = self._db_manager.get_connection("settings")
        self._ensure_schema()
        
    def _ensure_schema(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self._conn.cursor()
        
        # Create settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                type TEXT,
                scope TEXT DEFAULT 'app',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create schemas table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schemas (
                id TEXT PRIMARY KEY,
                schema TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                description TEXT
            )
        """)
        
        self._conn.commit()
        
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting by key."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT value, type FROM settings WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        
        if not row:
            return default
            
        setting = Setting(key, row["value"], row["type"])
        return setting.value
        
    def set_setting(self, key: str, value: Any, scope: str = "app") -> None:
        """Set or update a setting."""
        setting = Setting(key, value, scope=scope)
        
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO settings (key, value, type, scope, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (setting.key, setting._value, setting.type, setting.scope, 
             setting.updated_at.isoformat())
        )
        self._conn.commit()
        
    def get_settings_by_scope(self, scope: str) -> dict:
        """Get all settings for a scope."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT key, value, type FROM settings WHERE scope = ?",
            (scope,)
        )
        
        result = {}
        for row in cursor.fetchall():
            setting = Setting(row["key"], row["value"], row["type"], scope)
            result[row["key"]] = setting.value
            
        return result
        
    def register_schema(self, schema: Schema) -> None:
        """Register or update a schema."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO schemas (id, schema, version, description)
            VALUES (?, ?, ?, ?)
            """,
            (schema.id, json.dumps(schema.schema), schema.version, schema.description)
        )
        self._conn.commit()
        
    def get_schema(self, schema_id: str) -> Optional[Schema]:
        """Get a schema by ID."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT schema, version, description FROM schemas WHERE id = ?",
            (schema_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
            
        return Schema(
            id=schema_id,
            schema=json.loads(row["schema"]),
            version=row["version"],
            description=row["description"]
        )
```

### Transaction Support

For complex operations, services support transactions:

```python
class TransactionManager:
    """Helper for database transactions."""
    
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self._active = False
        
    def __enter__(self) -> sqlite3.Connection:
        """Start a transaction."""
        self._conn.execute("BEGIN TRANSACTION")
        self._active = True
        return self._conn
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """End a transaction, committing or rolling back."""
        if exc_type is None and self._active:
            self._conn.commit()
        else:
            self._conn.rollback()
            
        self._active = False
```

## Data Access Patterns

### Repository Pattern
Each data type has a repository class:

```python
class TranslationEntryRepository:
    """Repository for translation entries."""
    
    def __init__(self, db_service):
        self._db_service = db_service
        
    def get(self, id: str) -> Optional[TranslationEntry]:
        """Get an entry by ID."""
        
    def find_by_source(self, source_text: str, context: Optional[str] = None) -> Optional[TranslationEntry]:
        """Find an entry by source text and context."""
        
    def add(self, entry: TranslationEntry) -> TranslationEntry:
        """Add a new entry."""
        
    def update(self, entry: TranslationEntry) -> bool:
        """Update an existing entry."""
        
    def delete(self, id: str) -> bool:
        """Delete an entry by ID."""
        
    def list(self, page: int = 1, page_size: int = 50, 
            sort_by: str = "last_accessed", 
            sort_dir: str = "DESC") -> tuple[list[TranslationEntry], int]:
        """List entries with pagination and sorting."""
        
    def search(self, query: str, options: dict = None) -> list[TranslationEntry]:
        """Search for entries matching a query."""
```

### Unit of Work Pattern
For complex operations spanning multiple repositories:

```python
class TranslationUnitOfWork:
    """Coordinates operations across multiple repositories."""
    
    def __init__(self, db_service):
        self._db_service = db_service
        self._transaction = None
        
    def __enter__(self):
        """Start a transaction."""
        self._transaction = TransactionManager(self._db_service.connection)
        self._transaction.__enter__()
        
        # Create repositories with the active connection
        self.entries = TranslationEntryRepository(self._db_service)
        self.versions = TranslationVersionRepository(self._db_service)
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the transaction."""
        self._transaction.__exit__(exc_type, exc_val, exc_tb)
        self._transaction = None
```

## Migration System

Database migrations are handled via versioned SQL scripts:

```python
class MigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager
        
    def _get_current_version(self, db_name: str) -> int:
        """Get the current database version."""
        conn = self._db_manager.get_connection(db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT version FROM _migrations ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return 0
            
    def _ensure_migrations_table(self, conn: sqlite3.Connection) -> None:
        """Create migrations tracking table if needed."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
    def run_migrations(self, db_name: str, migrations_dir: str) -> int:
        """Run all pending migrations and return count."""
        conn = self._db_manager.get_connection(db_name)
        self._ensure_migrations_table(conn)
        
        current_version = self._get_current_version(db_name)
        applied_count = 0
        
        # Find all migration scripts
        migration_files = sorted([
            f for f in os.listdir(migrations_dir)
            if f.endswith('.sql') and f.startswith('v')
        ])
        
        # Apply each migration in order
        for migration_file in migration_files:
            try:
                version = int(migration_file.split('_')[0][1:])
                if version > current_version:
                    # Apply this migration
                    with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                        sql = f.read()
                        
                    with TransactionManager(conn):
                        conn.executescript(sql)
                        conn.execute(
                            "INSERT INTO _migrations (version) VALUES (?)",
                            (version,)
                        )
                        
                    applied_count += 1
            except Exception as e:
                logger.error(f"Migration failed: {migration_file} - {e}")
                raise
                
        return applied_count
```

## Performance Optimizations

1. **Connection Pooling**: Reuse database connections
2. **Prepared Statements**: Cache and reuse prepared SQL statements
3. **Bulk Operations**: Use executemany for bulk inserts/updates
4. **Indexing Strategy**: Create indexes for common query patterns
5. **Result Caching**: Cache frequent query results in memory
6. **Lazy Loading**: Defer loading related objects until needed
7. **Batch Processing**: Process large datasets in manageable chunks

## Implementation Plan

1. **Phase 1: Core Schema**
   - Implement basic settings database
   - Create schema validation system
   - Build database manager foundation

2. **Phase 2: Model Layer**
   - Implement data models
   - Build repository pattern classes
   - Add transaction support

3. **Phase 3: Migration System**
   - Create migration manager
   - Add versioning to database schemas
   - Implement upgrade path for existing users

4. **Phase 4: Advanced Features**
   - Implement caching layer
   - Add performance optimizations
   - Build backup and restore system

## Security Considerations

1. **Data Encryption**: Sensitive values are encrypted at rest
2. **Input Validation**: All database inputs are validated and sanitized
3. **Parametrized Queries**: Use bind parameters to prevent SQL injection
4. **Access Control**: Plugin data is isolated in separate databases
5. **Backup Protection**: Database backups are encrypted

## Disaster Recovery

1. **Automatic Backups**: Schedule regular database backups
2. **Integrity Checks**: Periodically verify database integrity
3. **Repair Tools**: Include database repair utilities
4. **Corrupt Detection**: Detect and report database corruption
5. **Recovery Procedures**: Document recovery steps

## Future Enhancements

1. **Cloud Sync**: Synchronize databases across devices
2. **Distributed Storage**: Support for remote database backends
3. **Replication**: Real-time replication for multi-user environments
4. **Conflict Resolution**: Smart merging of conflicting changes
5. **Data Analytics**: Extract insights from usage patterns
