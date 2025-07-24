# Translation Database Service Integration Plan

**Date**: August 1, 2025  
**Component**: Translation Database Service  
**Status**: Planning

## 1. Overview

This document details the plan for integrating the Translation Database Service into the POEditor plugin-based architecture. The service will provide translation history, versioning, suggestions, and advanced search capabilities, supporting both the POEditorTab and other components.

## 2. Objectives

- Provide a robust backend for translation history and suggestions
- Enable version management for translation entries
- Support efficient querying and search
- Integrate seamlessly with POEditorTab and plugin system
- Ensure data integrity and performance

## 3. Architecture

### 3.1 Service Location
- File: `services/translation_db_service.py`
- Exposed via plugin API for use by POEditor and other plugins

### 3.2 Database Backend
- SQLite database (file-based, per-project or global)
- Tables:
  - `translations`: id, po_file, entry_key, source_text, translation, user, timestamp, version
  - `history`: id, translation_id, old_translation, new_translation, changed_by, changed_at
  - (Optional) `suggestions`, `qa_issues`

### 3.3 Core Classes
- `TranslationDatabaseService`: Main service class
- `TranslationRecord`: Data model for translation entries
- `TranslationHistoryRecord`: Data model for history

## 4. Integration Points

- **POEditorTab**: Loads/saves translation history, fetches suggestions
- **Quality Assurance Service**: Reads/writes QA issues
- **Text Replacement Service**: May use database for rule storage
- **Settings Panels**: Configure database location, retention, etc.

## 5. Data Flow

1. **Entry Load**:
   - POEditorTab requests history for entry → Service queries DB → Returns history/suggestions
2. **Translation Edit**:
   - User edits translation → Service updates DB, creates history record
3. **Suggestion Application**:
   - User selects suggestion → Service updates translation, logs action
4. **Search**:
   - User searches translations → Service performs query, returns results

## 6. Implementation Steps

### Phase 1: Database Schema & Service Skeleton
- Define schema in `translation_db_service.py`
- Implement connection management
- Create basic CRUD operations

### Phase 2: Versioning & History
- Implement version tracking for translations
- Add history record creation on edit
- Expose API for retrieving history

### Phase 3: Suggestions & Search
- Implement suggestion retrieval (by key, fuzzy match, etc.)
- Add advanced search (by source, translation, user, date)

### Phase 4: Integration with POEditorTab
- Connect service to POEditorTab for history/suggestions
- Update tab to display and apply suggestions
- Mark file as modified on DB update

### Phase 5: Settings & Configuration
- Add settings for DB location, retention policy
- Integrate with settings panels

### Phase 6: Testing & Optimization
- Unit tests for all service methods
- Performance tests with large datasets
- Optimize queries and indexing

## 7. Risks & Mitigations

- **Performance**: Use indexes, optimize queries, paginate results
- **Data Integrity**: Use transactions, validate inputs
- **Migration**: Provide migration scripts for legacy data

## 8. Deliverables

- `services/translation_db_service.py` (service implementation)
- Database schema documentation
- Integration code in POEditorTab
- Unit and integration tests

## 9. Timeline

- Phase 1: 2 days
- Phase 2: 2 days
- Phase 3: 2 days
- Phase 4: 2 days
- Phase 5: 1 day
- Phase 6: 1 day

**Total**: 10 days

## 10. Next Steps

1. Review and approve this plan
2. Begin Phase 1 implementation
3. Schedule integration checkpoints with POEditorTab team
