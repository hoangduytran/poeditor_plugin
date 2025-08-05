"""
Database infrastructure for preferences system.

This module provides SQLite database support with schema migrations,
connection management, and data access patterns for the preferences system.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from contextlib import contextmanager

from lg import logger
from .data_models import ReplacementRecord, DatabasePORecord, TranslationRecord


class DatabaseManager:
    """Manages SQLite database connections and schema for preferences."""
    
    CURRENT_VERSION = 1
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with optional custom path."""
        self.db_path = db_path or self._get_default_db_path()
        self.connection: Optional[sqlite3.Connection] = None
        logger.info(f"DatabaseManager initialized with path: {self.db_path}")
    
    def _get_default_db_path(self) -> str:
        """Get default database path in application data directory."""
        # Create preferences data directory if it doesn't exist
        app_dir = Path.home() / ".poeditor_plugin"
        app_dir.mkdir(exist_ok=True)
        return str(app_dir / "preferences.db")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def initialize_database(self) -> bool:
        """Initialize database with current schema."""
        try:
            logger.info("Initializing preferences database schema")
            with self.get_connection() as conn:
                self._create_schema(conn)
                self._set_database_version(conn, self.CURRENT_VERSION)
                conn.commit()
            logger.info("Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def _create_schema(self, conn: sqlite3.Connection):
        """Create database schema tables."""
        logger.debug("Creating database schema tables")
        
        # Replacement rules table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS replacement_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                find_text TEXT NOT NULL,
                replace_text TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                case_sensitive BOOLEAN DEFAULT 0,
                use_regex BOOLEAN DEFAULT 0,
                context TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Translation entries table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translation_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msgid TEXT NOT NULL,
                msgctxt TEXT,
                current_msgstr TEXT,
                fuzzy BOOLEAN DEFAULT 0,
                line_number INTEGER,
                source_file TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(msgid, msgctxt)
            )
        """)
        
        # Translation versions/history table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translation_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER REFERENCES translation_entries(id),
                msgstr TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                version_number INTEGER DEFAULT 1,
                confidence_score REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_current BOOLEAN DEFAULT 0
            )
        """)
        
        # File references table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER REFERENCES translation_entries(id),
                file_path TEXT NOT NULL,
                line_number INTEGER,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Database metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS database_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self._create_indexes(conn)
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance."""
        logger.debug("Creating database indexes")
        
        # Replacement rules indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_replacement_find ON replacement_rules(find_text)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_replacement_context ON replacement_rules(context)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_replacement_enabled ON replacement_rules(enabled)")
        
        # Translation entries indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_translation_msgid ON translation_entries(msgid)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_translation_msgctxt ON translation_entries(msgctxt)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_translation_modified ON translation_entries(modified_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_translation_fuzzy ON translation_entries(fuzzy)")
        
        # Translation versions indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_version_entry ON translation_versions(entry_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_version_current ON translation_versions(is_current)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_version_source ON translation_versions(source)")
        
        # File references indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_ref_entry ON file_references(entry_id)")
    
    def _set_database_version(self, conn: sqlite3.Connection, version: int):
        """Set database version in metadata."""
        conn.execute(
            "INSERT OR REPLACE INTO database_metadata (key, value) VALUES (?, ?)",
            ("schema_version", str(version))
        )
    
    def get_database_version(self) -> int:
        """Get current database schema version."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM database_metadata WHERE key = ?",
                    ("schema_version",)
                )
                row = cursor.fetchone()
                return int(row["value"]) if row else 0
        except Exception as e:
            logger.warning(f"Could not get database version: {e}")
            return 0
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create backup of database."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False
    
    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space and optimize."""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                conn.commit()
            logger.info("Database vacuum completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.get_connection() as conn:
                # Get table counts
                stats = {}
                tables = ['replacement_rules', 'translation_entries', 'translation_versions', 'file_references']
                
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()["count"]
                
                # Get database size
                stats["database_size"] = os.path.getsize(self.db_path)
                stats["database_path"] = self.db_path
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}


class DatabaseMigration:
    """Handle database schema migrations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        logger.info("DatabaseMigration initialized")
    
    def migrate_to_current(self) -> bool:
        """Migrate database to current version."""
        current_version = self.db_manager.get_database_version()
        target_version = DatabaseManager.CURRENT_VERSION
        
        logger.info(f"Database migration: current={current_version}, target={target_version}")
        
        if current_version == target_version:
            logger.info("Database is already at current version")
            return True
        
        if current_version == 0:
            # New database, initialize with current schema
            return self.db_manager.initialize_database()
        
        # Future: Add migration steps here
        # if current_version < 2:
        #     self._migrate_to_v2()
        
        logger.info("Database migration completed successfully")
        return True
    
    def _migrate_to_v2(self):
        """Example migration to version 2 (placeholder)."""
        logger.info("Migrating to database version 2")
        # Add new columns, tables, indexes, etc.
        pass
