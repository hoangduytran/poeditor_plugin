"""
Common components for preferences system.

This module contains shared infrastructure and UI components used across
all preference panels including base classes, data models, database
infrastructure, search functionality, and import/export services.
"""

# Import all common components for easy access
from .workspace_types import (
    FindReplaceScope, ReplacementCaseMatch, PagingMode, EmptyMode
)

from .data_models import (
    PageInfo, PreferenceSearchRequest, PreferenceSearchResult,
    MatchInstance, ReplacementRecord, DatabasePORecord,
    TranslationRecord, NavRecord
)

from .base_components import (
    PreferenceSection, PreferencePage, FormLayoutHelper,
    PagedTableWidget, SearchableListWidget, EditableTableWidget,
    ValidationHelpers, PagingControlsWidget, SettingsGroupWidget
)

from .database import (
    DatabaseManager, DatabaseMigration
)

from .search_integration import (
    PreferenceSearchBar, SearchResultHighlighter, 
    PreferenceSearchService
)

from .import_export import (
    ImportExportService, BaseFormatHandler,
    JsonHandler, CsvHandler, PlistHandler, YamlHandler
)

__all__ = [
    # Workspace types
    'FindReplaceScope', 'ReplacementCaseMatch', 'PagingMode', 'EmptyMode',
    
    # Data models
    'PageInfo', 'PreferenceSearchRequest', 'PreferenceSearchResult',
    'MatchInstance', 'ReplacementRecord', 'DatabasePORecord',
    'TranslationRecord', 'NavRecord',
    
    # Base UI components
    'PreferenceSection', 'PreferencePage', 'FormLayoutHelper',
    'PagedTableWidget', 'SearchableListWidget', 'EditableTableWidget',
    'ValidationHelpers', 'PagingControlsWidget', 'SettingsGroupWidget',
    
    # Database infrastructure
    'DatabaseManager', 'DatabaseMigration',
    
    # Search functionality
    'PreferenceSearchBar', 'SearchResultHighlighter', 
    'PreferenceSearchService',
    
    # Import/Export services
    'ImportExportService', 'BaseFormatHandler',
    'JsonHandler', 'CsvHandler', 'PlistHandler', 'YamlHandler'
]

__version__ = "1.0.0"
