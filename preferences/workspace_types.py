"""
Workspace find/replace types for preference integration.

This module creates a compatibility bridge between the existing workspace find/replace
system and the new preferences system. Since we don't have access to the actual
workspace directory, we'll define compatible types here that match the design specification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Any, Dict, Union
from datetime import datetime

from lg import logger


class FindReplaceScope(Enum):
    """Scope for find/replace operations."""
    ALL = "all"
    CURRENT = "current"
    SELECTION = "selection"


class ReplacementCaseMatch(Enum):
    """Case handling for replacements."""
    IGNORE = "ignore"
    MATCH = "match"
    SMART = "smart"
    PRESERVE = "preserve"


class PagingMode(Enum):
    """Paging modes for navigation."""
    DATABASE = "database"
    SEARCH = "search"


class EmptyMode(Enum):
    """Handling of empty fields."""
    DO_NOT_ALLOW_EMPTY = "do_not_allow_empty"
    EMPTY_ONLY = "empty_only"
    EMPTY_INCLUSIVE = "empty_inclusive"


@dataclass
class FindReplaceRequest:
    """Base request for find/replace operations."""
    query: str = ""
    scope: FindReplaceScope = FindReplaceScope.ALL
    case_match: ReplacementCaseMatch = ReplacementCaseMatch.IGNORE
    use_regex: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class MatchInstance:
    """Represents a single match instance for precise navigation."""
    start: int
    end: int
    text: str
    field: str = ""
    line_number: int = 0
    column: int = 0
    
    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass 
class MatchPair:
    """Represents a synchronized pair of msgid/msgstr matches for AND navigation."""
    msgid_match: Optional[MatchInstance] = None
    msgstr_match: Optional[MatchInstance] = None
    context_match: Optional[MatchInstance] = None
    
    @property
    def has_matches(self) -> bool:
        return any([self.msgid_match, self.msgstr_match, self.context_match])


@dataclass
class FindReplaceResult:
    """Base result for find/replace operations."""
    record_id: int
    record: Any
    match_instances: List[MatchInstance]
    relevance_score: float = 0.0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def has_matches(self) -> bool:
        return len(self.match_instances) > 0
