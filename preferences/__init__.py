"""
PySide POEditor Plugin - Preferences System

This package provides a comprehensive preferences dialog system with:
- Modular preference pages
- Database-backed data persistence  
- Search and filtering capabilities
- Import/export functionality
- Plugin extension support
- Consistent UI components

Phase 1 Implementation: Common Components Foundation
- Core data models and workspace type integration
- Database infrastructure with SQLite and migrations
- Base UI components (paging, search, forms)
- Search integration with existing find/replace system
- Import/export service with multiple format support
- Main preferences dialog framework

Usage:
    from preferences import create_preferences_dialog
    
    dialog = create_preferences_dialog(parent)
    dialog.show()
"""

from .common.workspace_types import (
    FindReplaceScope, ReplacementCaseMatch, PagingMode, EmptyMode,
    FindReplaceRequest, FindReplaceResult, MatchInstance, MatchPair
)

from .common.data_models import (
    PreferenceSearchRequest, PreferenceSearchResult, PageInfo,
    ReplacementRecord, DatabasePORecord, TranslationRecord,
    PluginPreferenceTab, NavRecord
)

from .common.database import DatabaseManager, DatabaseMigration

from .common.base_components import (
    PreferenceSection, PreferencePage, FormLayoutHelper,
    PagedTableWidget, SearchableListWidget, EditableTableWidget,
    ValidationHelpers, PagingControlsWidget, SettingsGroupWidget
)

from .common.search_integration import (
    PreferenceFlagLineEdit, PreferenceSearchBar, SearchResultHighlighter,
    SearchNavigationWidget, PreferenceSearchService
)

from .common.import_export import (
    BaseFormatHandler, JsonHandler, CsvHandler, PlistHandler, YamlHandler,
    ImportExportService, ImportExportWidget
)

from .main_dialog import (
    PreferencesDialog, PreferencePageRegistry, 
    preference_page_registry, create_preferences_dialog
)

from lg import logger

# Version info
__version__ = "1.0.0"
__phase__ = "Phase 1: Common Components Foundation"

logger.info(f"Preferences system initialized - {__phase__} (v{__version__})")

# Public API exports
__all__ = [
    # Workspace types
    'FindReplaceScope', 'ReplacementCaseMatch', 'PagingMode', 'EmptyMode',
    'FindReplaceRequest', 'FindReplaceResult', 'MatchInstance', 'MatchPair',
    
    # Data models
    'PreferenceSearchRequest', 'PreferenceSearchResult', 'PageInfo',
    'ReplacementRecord', 'DatabasePORecord', 'TranslationRecord',
    'PluginPreferenceTab', 'NavRecord',
    
    # Database
    'DatabaseManager', 'DatabaseMigration',
    
    # Base components
    'PreferenceSection', 'PreferencePage', 'FormLayoutHelper',
    'PagedTableWidget', 'SearchableListWidget', 'EditableTableWidget',
    'ValidationHelpers', 'PagingControlsWidget', 'SettingsGroupWidget',
    
    # Search integration
    'PreferenceFlagLineEdit', 'PreferenceSearchBar', 'SearchResultHighlighter',
    'SearchNavigationWidget', 'PreferenceSearchService',
    
    # Import/Export
    'BaseFormatHandler', 'JsonHandler', 'CsvHandler', 'PlistHandler', 'YamlHandler',
    'ImportExportService', 'ImportExportWidget',
    
    # Main dialog
    'PreferencesDialog', 'PreferencePageRegistry', 
    'preference_page_registry', 'create_preferences_dialog'
]


def get_phase1_status():
    """Get Phase 1 implementation status."""
    return {
        'phase': 'Phase 1: Common Components Foundation',
        'version': __version__,
        'completed_components': [
            'Workspace type integration',
            'Core data models',
            'Database infrastructure',
            'Base UI components',
            'Search integration',
            'Import/Export service',
            'Preferences dialog framework'
        ],
        'next_phase': 'Phase 2: Text Replacements Panel',
        'ready_for_phase2': True
    }


def validate_phase1_installation():
    """Validate Phase 1 installation and dependencies."""
    issues = []
    
    try:
        # Test database creation
        db = DatabaseManager(":memory:")
        if not db.initialize_database():
            issues.append("Database initialization failed")
    except Exception as e:
        issues.append(f"Database error: {e}")
    
    try:
        # Test import/export service
        service = ImportExportService()
        formats = service.get_supported_formats()
        if not formats:
            issues.append("No import/export formats available")
    except Exception as e:
        issues.append(f"Import/Export service error: {e}")
    
    try:
        # Test dialog creation
        dialog = create_preferences_dialog()
        if not dialog:
            issues.append("Failed to create preferences dialog")
    except Exception as e:
        issues.append(f"Dialog creation error: {e}")
    
    if issues:
        logger.warning(f"Phase 1 validation issues: {issues}")
        return False, issues
    else:
        logger.info("Phase 1 validation passed successfully")
        return True, []
