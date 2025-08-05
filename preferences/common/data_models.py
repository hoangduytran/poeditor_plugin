"""
Core data models for the preferences system.

This module provides the foundational data structures for preference dialogs,
including search requests, results, and pagination support.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Union
from datetime import datetime
from enum import Enum

from .workspace_types import (
    FindReplaceRequest, FindReplaceResult, MatchInstance, MatchPair,
    FindReplaceScope, ReplacementCaseMatch, PagingMode
)
from lg import logger


@dataclass
class PreferenceSearchRequest(FindReplaceRequest):
    """Extended search request for preference dialogs."""
    
    def __init__(self, query: str, scope: FindReplaceScope = FindReplaceScope.ALL,
                 case_match: ReplacementCaseMatch = ReplacementCaseMatch.IGNORE,
                 use_regex: bool = False, table_type: str = "replacement"):
        super().__init__(query, scope, case_match, use_regex)
        self.table_type = table_type  # "replacement" or "history"
        self.date_filter: Optional[datetime] = None
        self.context_filter: Optional[str] = None
        self.enabled_filter: Optional[bool] = None


@dataclass
class PreferenceSearchResult(FindReplaceResult):
    """Search result for preference tables with match highlighting."""
    
    def __init__(self, record_id: int, record: Any, 
                 match_instances: List[MatchInstance]):
        super().__init__(record_id, record, match_instances)
        self.table_row: Optional[int] = None
        self.display_text: str = ""
        self.relevance_score: float = 0.0


@dataclass
class PageInfo:
    """Pagination state management."""
    current_page: int = 1
    page_size: int = 50
    total_pages: int = 0
    total_records: int = 0
    paging_mode: PagingMode = PagingMode.DATABASE
    
    @property
    def has_next_page(self) -> bool:
        return self.current_page < self.total_pages
    
    @property
    def has_prev_page(self) -> bool:
        return self.current_page > 1
    
    @property
    def start_record(self) -> int:
        return (self.current_page - 1) * self.page_size + 1
    
    @property
    def end_record(self) -> int:
        return min(self.current_page * self.page_size, self.total_records)


@dataclass
class ReplacementRecord:
    """Data model for text replacement rules."""
    id: Optional[int] = None
    find_text: str = ""
    replace_text: str = ""
    enabled: bool = True
    case_sensitive: bool = False
    use_regex: bool = False
    context: str = ""
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    
    def __post_init__(self):
        now = datetime.now()
        if self.created_date is None:
            self.created_date = now
        if self.modified_date is None:
            self.modified_date = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'find_text': self.find_text,
            'replace_text': self.replace_text,
            'enabled': self.enabled,
            'case_sensitive': self.case_sensitive,
            'use_regex': self.use_regex,
            'context': self.context,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReplacementRecord':
        """Create from dictionary (e.g., from database)."""
        return cls(**data)


@dataclass
class DatabasePORecord:
    """Data model for translation history entries."""
    id: Optional[int] = None
    msgid: str = ""
    msgctxt: str = ""
    current_msgstr: str = ""
    fuzzy: bool = False
    line_number: Optional[int] = None
    source_file: str = ""
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    
    def __post_init__(self):
        now = datetime.now()
        if self.created_date is None:
            self.created_date = now
        if self.modified_date is None:
            self.modified_date = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'msgid': self.msgid,
            'msgctxt': self.msgctxt,
            'current_msgstr': self.current_msgstr,
            'fuzzy': self.fuzzy,
            'line_number': self.line_number,
            'source_file': self.source_file,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabasePORecord':
        """Create from dictionary (e.g., from database)."""
        return cls(**data)


@dataclass
class TranslationRecord:
    """Data model for translation versions/history."""
    id: Optional[int] = None
    entry_id: int = 0
    msgstr: str = ""
    source: str = "manual"  # 'manual', 'auto', 'import', etc.
    version_number: int = 1
    confidence_score: Optional[float] = None
    created_date: Optional[datetime] = None
    is_current: bool = False
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'msgstr': self.msgstr,
            'source': self.source,
            'version_number': self.version_number,
            'confidence_score': self.confidence_score,
            'created_date': self.created_date,
            'is_current': self.is_current
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationRecord':
        """Create from dictionary (e.g., from database)."""
        return cls(**data)


@dataclass
class PluginPreferenceTab:
    """Interface for plugin-contributed preference tabs."""
    tab_name: str
    tab_widget: Any  # QWidget
    plugin_id: str
    icon: Optional[Any] = None  # QIcon
    position: int = -1
    enabled: bool = True
    
    def validate(self) -> bool:
        """Validate tab configuration."""
        if not self.tab_name or not self.tab_widget or not self.plugin_id:
            logger.error(f"Invalid plugin preference tab: {self.tab_name}")
            return False
        return True


# Navigation record for search results
@dataclass
class NavRecord:
    """Navigation record for building navigation lists."""
    record_id: int
    row_index: int
    display_text: str
    record_type: str = "replacement"  # "replacement" or "history"
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.record_type}:{self.record_id}:{self.display_text[:50]}"
