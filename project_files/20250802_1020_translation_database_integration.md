# Translation Database Integration Design

**Date**: August 2, 2025  
**Component**: Translation Database Service  
**Status**: Design Phase  
**Priority**: HIGH

## 1. Overview
Integrate legacy translation history database with the new plugin-based architecture, providing a unified translation memory system with plugin-extensible storage backends.

## 2. Legacy System Analysis

### 2.1 Current Components
- `pref/tran_history` - Legacy history storage
- `services/translation_db_service.py` - New service framework
- Translation memory and suggestions system
- Historical translation lookup

### 2.2 Legacy Database Schema (from old_codes analysis)
```sql
-- Legacy translation_history table structure
CREATE TABLE translation_history (
    id INTEGER PRIMARY KEY,
    source_text TEXT,
    target_text TEXT,
    language_pair TEXT,
    timestamp DATETIME,
    source_file TEXT,
    confidence REAL
);
```

## 3. Unified Database Architecture

### 3.1 Enhanced Schema Design
```sql
-- New unified translation database
CREATE TABLE translation_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    context TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT,
    line_number INTEGER,
    confidence REAL DEFAULT 1.0,
    provider TEXT DEFAULT 'manual',
    metadata JSON
);

CREATE TABLE translation_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    translation_unit_id INTEGER,
    suggested_text TEXT NOT NULL,
    provider TEXT NOT NULL,
    confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (translation_unit_id) REFERENCES translation_units(id)
);

CREATE INDEX idx_source_text ON translation_units(source_text);
CREATE INDEX idx_language_pair ON translation_units(source_language, target_language);
CREATE INDEX idx_source_file ON translation_units(source_file);
```

### 3.2 Plugin-Extensible Storage
```python
class TranslationStoragePlugin(PluginBase):
    """Base class for translation storage backends"""
    
    def store_translation(self, unit: TranslationUnit) -> bool:
        """Store a translation unit"""
        pass
    
    def search_translations(self, query: SearchQuery) -> List[TranslationUnit]:
        """Search for similar translations"""
        pass
    
    def get_suggestions(self, source_text: str, language_pair: str) -> List[Suggestion]:
        """Get translation suggestions"""
        pass
```

## 4. Service Integration

### 4.1 Enhanced Translation DB Service
```python
class TranslationDatabaseService:
    """Unified translation database service"""
    
    def __init__(self):
        self.storage_backends: List[TranslationStoragePlugin] = []
        self.primary_backend: TranslationStoragePlugin = None
        
    def register_storage_backend(self, backend: TranslationStoragePlugin):
        """Register a storage backend plugin"""
        
    def migrate_legacy_data(self) -> MigrationResult:
        """Migrate data from legacy systems"""
        
    def fuzzy_search(self, source_text: str, threshold: float = 0.8) -> List[Match]:
        """Perform fuzzy matching for translation suggestions"""
        
    def bulk_import(self, source: ImportSource) -> ImportResult:
        """Import translations from external sources"""
```

### 4.2 Migration Framework
```python
class DatabaseMigrator:
    """Handles migration between database versions"""
    
    def detect_legacy_data(self) -> List[LegacySource]:
        """Detect existing legacy translation data"""
        
    def create_migration_plan(self, sources: List[LegacySource]) -> MigrationPlan:
        """Create step-by-step migration plan"""
        
    def execute_migration(self, plan: MigrationPlan) -> MigrationResult:
        """Execute migration with progress tracking"""
        
    def rollback_migration(self, checkpoint: str) -> bool:
        """Rollback to previous state if migration fails"""
```

## 5. Search and Matching Capabilities

### 5.1 Fuzzy Matching Algorithm
- Levenshtein distance for character-level similarity
- N-gram matching for phrase similarity
- Context-aware matching using surrounding text
- Language-specific matching rules

### 5.2 Search Interface
```python
class TranslationSearchQuery:
    source_text: str
    source_language: str
    target_language: str
    context: Optional[str]
    fuzzy_threshold: float = 0.8
    max_results: int = 10
    include_suggestions: bool = True
```

## 6. Performance Optimization

### 6.1 Indexing Strategy
- Full-text search indices for source and target text
- Language pair indices for quick filtering
- Composite indices for common query patterns

### 6.2 Caching Layer
```python
class TranslationCache:
    """Multi-level caching for translation lookups"""
    
    def __init__(self):
        self.memory_cache = {}  # LRU cache for frequent lookups
        self.disk_cache = {}    # Persistent cache for session data
        
    def get_cached_suggestions(self, query: SearchQuery) -> Optional[List[Suggestion]]:
        """Get cached suggestions if available"""
        
    def cache_suggestions(self, query: SearchQuery, suggestions: List[Suggestion]):
        """Cache suggestions for future use"""
```

## 7. Plugin Integration Points

### 7.1 External Translation Memory
- TMX file import/export
- Translation memory server integration
- Cloud-based translation storage

### 7.2 AI/ML Integration
- Machine learning suggestion ranking
- Context-aware translation scoring
- Continuous learning from user corrections

## 8. Implementation Phases

### Phase 1: Core Database Setup
- Implement enhanced database schema
- Create migration framework
- Basic CRUD operations

### Phase 2: Legacy Migration
- Analyze legacy data structures
- Implement data migration tools
- Validate migrated data integrity

### Phase 3: Search and Matching
- Implement fuzzy search algorithms
- Add indexing and optimization
- Create caching layer

### Phase 4: Plugin Framework
- Design storage plugin interface
- Implement plugin registration
- Add external service connectors

## 9. Success Criteria
- 100% successful migration of legacy translation data
- Search performance under 100ms for typical queries
- Plugin extensibility demonstrated with sample backends
- Memory usage optimized for large translation databases
- Backward compatibility maintained

## 10. Testing Strategy
- Unit tests for all database operations
- Integration tests with legacy data sources
- Performance benchmarks with large datasets
- Migration testing with real user data

## 11. Dependencies
- SQLite/database backend
- Plugin registration system
- Settings framework for configuration
- Legacy code analysis completion

## 12. Next Steps
1. Complete legacy database schema analysis
2. Implement core database migration framework
3. Design and test fuzzy search algorithms
4. Create plugin interface specifications
