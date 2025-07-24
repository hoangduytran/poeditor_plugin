# Google Translation Suggestion System Design Specification

## Overview
The Google Translation Suggestion System is an intelligent translation assistance component that provides real-time machine translation suggestions using Google's translate service. This system seamlessly integrates with the translation history database to save newly translated entries, offering translators immediate AI-powered suggestions while building a persistent knowledge base for future reference.

The system operates asynchronously to maintain UI responsiveness, automatically fetches translations when users navigate to new entries, handles network connectivity gracefully, and stores all successful translations in the database with proper versioning and source attribution.

## Core Architecture

### System Components
The translation suggestion system consists of three primary components working in coordination:

#### 1. Translation Service Layer (`sugg/translate.py`)
- **Google Translate API Integration**: Unofficial Google Translate REST API client
- **Network Connectivity Validation**: Internet availability checking before API calls
- **Asynchronous Task Processing**: QRunnable-based background translation requests
- **Error Handling and Recovery**: Comprehensive error management for network/API failures

#### 2. Suggestion Controller (`sugg/suggestion_controller.py`)
- **Row Change Management**: Handles table selection changes and state transitions
- **Database Integration**: Manages persistence of translations to translation history
- **UI State Synchronization**: Coordinates editor fields with translation data
- **Translation Memory Loading**: Retrieves existing translations from database

#### 3. Actions Integration (`main_utils/actions_factory.py`)
- **Signal Processing**: Handles translation results from background tasks
- **Database Record Management**: Creates and updates DatabasePORecord objects
- **UI Feedback**: Provides status messages and error notifications
- **Data Validation**: Ensures translation quality before saving

### Data Flow Architecture
```
User Navigation → SuggestionController → Database Lookup → UI Population
     ↓                     ↓                    ↓
Translation Request → TranslateTask → Google API → Translation Result
     ↓                     ↓                    ↓
Result Processing → DatabasePORecord → Database Save → UI Update
```

## Translation Service Implementation

### Google Translate API Client
**Location**: `sugg/translate.py`
**Purpose**: Provides unofficial Google Translate API access with error handling

#### Core Functions:
```python
def translate_text(text: str, target_lang: str) -> str:
    """
    Call Google Translate API to translate from English to target_lang.
    
    Parameters:
    - text: Source English text to translate
    - target_lang: Target language code (e.g., 'vi', 'fr', 'es')
    
    Returns:
    - Translated text string or error message
    
    Error Handling:
    - Network connectivity issues
    - API rate limiting
    - Malformed responses
    - Invalid language codes
    """
```

#### Network Validation:
```python
def is_internet_available(host="8.8.8.8", port=53, timeout=2) -> bool:
    """
    Check internet connectivity before making API requests.
    Uses DNS resolution to Google's public DNS as connectivity test.
    """
```

### Asynchronous Translation Tasks
**Class**: `TranslateTask(QRunnable)`
**Purpose**: Background translation processing without blocking the UI

#### Task Architecture:
```python
class TranslateTask(QRunnable):
    def __init__(self, text: str, target_language: str):
        super().__init__()
        self.text = text
        self.target_language = target_language
    
    def run(self):
        # 1. Validate internet connectivity
        # 2. Call Google Translate API
        # 3. Emit results via signal
        # 4. Handle errors gracefully
```

#### Signal Communication:
```python
class Suggestor(QObject):
    translation_received = Signal(str)  # Emits translated text
    
    def emit_translation(self, result: str):
        # Safe signal emission with error handling
```

### Translation Request Management
**Function**: `translate_suggestion(msgid: str)`
**Purpose**: Entry point for requesting translations

#### Implementation Strategy:
1. **Language Configuration**: Retrieves target language from QSettings
2. **Task Creation**: Instantiates TranslateTask with source text and target language
3. **Thread Pool Execution**: Submits task to global QThreadPool for background processing
4. **Result Handling**: Automatic signal connection routes results to processing functions

## Suggestion Controller System

### Controller Architecture
**Class**: `SuggestionController`
**Location**: `sugg/suggestion_controller.py`
**Purpose**: Central coordinator for translation suggestion workflow

#### Core Responsibilities:
- **Row Change Handling**: Manages table selection changes and state persistence
- **Editor Synchronization**: Keeps translation editors in sync with data model
- **Database Integration**: Loads and saves translation data to/from database
- **Translation Triggering**: Initiates background translation requests

### State Management System

#### Row Change Processing:
```python
def on_row_change(self, current: QModelIndex, previous: QModelIndex):
    """
    Main entry point for table row selection changes.
    
    Workflow:
    1. Commit previous suggestion edits to database
    2. Update global PO entry state tracking
    3. Load new entry data into editors and suggestion pane
    4. Trigger automatic translation request
    """
```

#### Previous State Persistence:
```python
def _commit_previous_suggestion(self, previous: QModelIndex):
    """
    Save user edits from suggestion pane back to database.
    
    Database Operations:
    - Insert new PO entry if doesn't exist
    - Add new translation version if text is unique
    - Update model with latest database record
    - Maintain version history and source attribution
    """
```

#### Editor Population Strategy:
```python
def _populate_editors(self, entry: POEntry):
    """
    Populate UI editors with POEntry data using signal blocking.
    
    Synchronized Fields:
    - Source text (read-only msgid display)
    - Translation editor (msgstr with change detection)
    - Fuzzy flag toggle (translation status indicator)
    - Comments editor (translator notes)
    """
```

### Database Integration Layer

#### Translation Memory Loading:
```python
def _load_new_entry(self, current: QModelIndex):
    """
    Load translation suggestions from database for selected entry.
    
    Process:
    1. Extract POEntry from current selection
    2. Query database for existing translations
    3. Create new record if none exists
    4. Populate suggestion model with version history
    5. Trigger automatic translation request
    """
```

#### Record Management:
- **Existing Records**: Load translation versions from database
- **New Records**: Create empty DatabasePORecord with msgid/msgctxt
- **Version History**: Display all translation versions with source attribution
- **Model Updates**: Refresh suggestion table with latest data

## Translation Result Processing

### Result Reception and Validation
**Function**: `on_suggestions_received(machine_text: str)`
**Location**: `main_utils/actions_factory.py`
**Purpose**: Process translation results from background tasks

#### Validation Pipeline:
```python
def on_suggestions_received(machine_text: str):
    """
    Process incoming translation results with comprehensive validation.
    
    Validation Steps:
    1. Check result validity (non-empty string)
    2. Detect error messages (network/API failures)
    3. Verify current selection context
    4. Validate translation quality (not identical to source)
    5. Update database record with new translation
    6. Refresh UI with updated suggestions
    """
```

#### Error Handling Strategies:
- **Network Errors**: Display status messages without saving
- **API Failures**: Show error details in status bar
- **Context Mismatches**: Ignore results for outdated selections
- **Quality Checks**: Reject translations identical to source text

### Database Integration Process

#### Record Retrieval and Creation:
```python
# Attempt to load existing database record
try:
    rec: DatabasePORecord = db.get_entry(msgid, msgctxt)
except Exception:
    # Create new record if none exists
    rec = DatabasePORecord(msgid=msgid, msgctxt=msgctxt)
```

#### Translation Versioning:
```python
# Add new translation version with source attribution
rec.add_version_mem(machine_text, source=DictType.WEB.name)

# Update suggestion model with new data
gv.suggestion_model.setRecord(rec)
```

#### Parent Relationship Validation:
```python
# Ensure translation belongs to current PO entry
if not rec.is_my_parent(gv.current_po_rec):
    return  # Ignore mismatched translations
```

## Database Record Management

### DatabasePORecord Integration
**Class**: `DatabasePORecord`
**Location**: `pref/tran_history/tran_db_record.py`
**Purpose**: In-memory representation of translation entries with version history

#### Core Properties:
- **unique_id**: Database primary key for persistent storage
- **msgid**: Source English text requiring translation
- **msgctxt**: Optional context information for disambiguation
- **msgstr_versions**: List of (version_id, translation_text, source) tuples

#### Version Management:
```python
def add_version_mem(self, translation: str, source: str = "") -> bool:
    """
    Add new translation version to in-memory record.
    
    Features:
    - Duplicate detection and prevention
    - Automatic version numbering
    - Source attribution tracking
    - Change detection for UI updates
    """
```

#### Parent Relationship Detection:
```python
def is_my_parent(self, other: POEntry) -> bool:
    """
    Verify if POEntry matches this record using SHA-256 hash comparison.
    Ensures translation suggestions belong to correct source entry.
    """
```

### Database Persistence Strategy

#### Automatic Persistence:
```python
def update_record_with_changes(self, fuzzy_threshold: Optional[float] = None) -> bool:
    """
    Apply in-memory changes to database with intelligent deduplication.
    
    Process:
    1. Filter empty and invalid translations
    2. Remove exact duplicates
    3. Optional fuzzy deduplication
    4. Database insertion or update
    5. Version renumbering and cleanup
    """
```

#### Source Attribution System:
- **WEB**: Google Translate API results
- **MANUAL**: User-entered translations
- **FILE**: Imported from PO files
- **MEMORY**: Translation memory matches

## User Interface Integration

### Suggestion Display System
**Component**: Suggestion version table
**Purpose**: Display translation history and new suggestions

#### Table Features:
- **Version Column**: Sequential version numbers for organization
- **Translation Column**: Full translation text with word wrapping
- **Source Column**: Attribution showing translation origin
- **Context Menu**: Copy, paste, delete, and edit operations

#### Selection Handling:
```python
def on_suggestion_selected(index: QModelIndex):
    """Handle user selection of specific translation version."""

def on_suggestion_double_click(index: QModelIndex):
    """Apply selected translation to current entry on double-click."""
```

### Editor Synchronization
**Component**: Translation editor fields
**Purpose**: Real-time synchronization between editors and data model

#### Synchronized Components:
- **Source Editor**: Read-only display of msgid
- **Translation Editor**: Editable msgstr with change detection
- **Fuzzy Toggle**: Translation status indicator
- **Comments Editor**: Translator notes and metadata

#### Signal Blocking Strategy:
```python
with QSignalBlocker(widget):
    widget.setValue(new_value)
    # Prevents recursive signal emissions during programmatic updates
```

## Error Handling and Recovery

### Network Error Management
**Strategy**: Graceful degradation with user feedback

#### Error Categories:
- **No Internet Connection**: Display connectivity message
- **API Rate Limiting**: Implement backoff and retry logic
- **Service Unavailable**: Fallback to offline translation memory
- **Malformed Responses**: Parse and validate API results

#### User Feedback:
```python
def show_status_message(message: str, timeout: int = 5000):
    """Display temporary status messages for error conditions."""
```

### Data Integrity Protection
**Strategy**: Comprehensive validation and rollback capabilities

#### Validation Points:
- **Input Sanitization**: Clean text before API calls
- **Result Validation**: Verify translation quality and relevance
- **Database Constraints**: Ensure referential integrity
- **Version Conflicts**: Handle concurrent modification scenarios

#### Recovery Mechanisms:
- **Transaction Rollback**: Automatic rollback on database errors
- **State Restoration**: Restore previous UI state on failures
- **Graceful Degradation**: Continue operation without network services
- **Manual Override**: Allow users to bypass automatic systems

## Configuration and Settings

### Language Configuration
**Storage**: QSettings with application-specific keys
**Key**: `targetLanguage` (default: "vi")

#### Supported Languages:
- Vietnamese (vi)
- French (fr)
- Spanish (es)
- German (de)
- Chinese (zh)
- Japanese (ja)
- And other Google Translate supported languages

### API Configuration
**Settings**: Google Translate service parameters

#### Configurable Options:
```python
TRANSLATE_API_BASE = "https://translate.googleapis.com/translate_a/single"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0
```

### Performance Settings
**Optimization**: Thread pool and caching configuration

#### Performance Parameters:
```python
THREAD_POOL_SIZE = 4  # Concurrent translation tasks
CACHE_SIZE = 100      # Recent translations cache
DEBOUNCE_DELAY = 500  # ms delay before triggering translation
```

## Performance Characteristics

### Asynchronous Processing Benefits
- **Non-blocking UI**: Translations fetch in background
- **Responsive Interface**: No freezing during API calls
- **Concurrent Requests**: Multiple translations can be processed simultaneously
- **Graceful Timeouts**: Automatic request cancellation after timeout

### Database Optimization
- **Indexed Queries**: Fast lookup of existing translations
- **Version Deduplication**: Prevent storage of identical translations
- **Batch Operations**: Efficient bulk data operations
- **Connection Pooling**: Reuse database connections for performance

### Memory Management
- **Lazy Loading**: Load translation versions on demand
- **Garbage Collection**: Automatic cleanup of completed tasks
- **Reference Management**: Proper object lifecycle management
- **Cache Limits**: Bounded caches to prevent memory leaks

## Security Considerations

### API Security
- **Request Validation**: Sanitize all user input before API calls
- **Rate Limiting**: Respect Google's API usage limits
- **Error Information**: Avoid exposing sensitive error details
- **SSL/TLS**: Secure communication with translation services

### Data Privacy
- **Local Processing**: Translation history stored locally
- **User Consent**: Clear indication of external API usage
- **Data Retention**: Configurable retention policies
- **Anonymization**: Remove personal information from logs

## Integration Points

### Main Application Integration
```python
# Automatic translation on row changes
controller.on_row_change(current_index, previous_index)

# Manual translation requests
translate_suggestion(selected_msgid)

# Result processing
on_suggestions_received(translation_result)
```

### Translation History Database
```python
# Load existing translations
record = db.get_entry(msgid, msgctxt)

# Save new translations
record.add_version_mem(translation, source="WEB")
record.update_record_with_changes()
```

### Editor System Integration
```python
# Populate editors with POEntry data
controller._populate_editors(po_entry)

# Apply suggestions to current translation
entry.msgstr = selected_translation
```

## Future Enhancement Opportunities

### Advanced Translation Features
- **Translation Confidence Scoring**: Rate translation quality automatically
- **Alternative Provider Support**: Integrate multiple translation services
- **Batch Translation**: Translate multiple entries simultaneously
- **Custom Terminology**: User-defined translation dictionaries

### Machine Learning Integration
- **Translation Learning**: Improve suggestions based on user corrections
- **Context Analysis**: Better translation based on surrounding text
- **Quality Prediction**: Predict translation accuracy before application
- **Personalization**: Adapt to individual translator preferences

### Performance Improvements
- **Intelligent Caching**: Cache translations with smart invalidation
- **Predictive Loading**: Pre-fetch translations for likely selections
- **Compression**: Reduce network bandwidth usage
- **Offline Mode**: Provide functionality without internet connection

### User Experience Enhancements
- **Translation Comparison**: Side-by-side comparison of multiple translations
- **Confidence Indicators**: Visual indicators of translation quality
- **Keyboard Shortcuts**: Quick access to translation functions
- **Customizable Interface**: User-configurable suggestion display options

This Google Translation Suggestion System provides intelligent, automated translation assistance that seamlessly integrates with the existing translation workflow. By combining real-time machine translation with persistent storage and version management, it creates a powerful tool for translators that becomes more valuable over time as the translation database grows with both human and machine-generated translations.
