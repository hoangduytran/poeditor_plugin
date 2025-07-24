# Translation History Panel Design Specification

## Overview
The Translation History panel serves as a comprehensive translation memory database management interface, allowing users to store, search, edit, and manage translation versions across multiple projects. This panel provides a centralized repository for translation data with full version control, import/export capabilities, and advanced search functionality.

## Core Architecture

### Database Backend
- **SQLite Database**: Persistent storage with optimized schema
  - `english_text` table: Source text with unique IDs and context
  - `tran_text` table: Translation versions with versioning and source tracking
  - Foreign key constraints with cascade operations
  - Optimized indexes for search performance

### Data Model
- **DatabasePORecord**: In-memory representation of translation entries
  - `unique_id`: Database primary key
  - `msgid`: Source text (English message)
  - `msgctxt`: Optional context information
  - `msgstr_versions`: List of (version_id, translation_text, source) tuples

## Main Interface Components

### 1. Database Table View
**Purpose**: Primary display of all translation entries with sortable columns

**Layout**:
- **ID Column**: Unique identifier (auto-sizing)
- **Message Column**: Source text display (stretchable)
- **Latest Translation Column**: Most recent translation version (stretchable)
- **Context Column**: Optional context information (auto-sizing)
- **Source Column**: Translation source indicator (auto-sizing)

**Features**:
- Multi-column sorting with ascending/descending order
- Header-based column resizing and reordering
- Row selection with keyboard navigation
- Paginated display with configurable page size (default: 30 entries)

### 2. Translation Editor Panel
**Purpose**: Multi-version translation editing with visual comparison

**Components**:
- **Source Text Display**: Read-only msgid with syntax highlighting
- **Version Selector**: Dropdown showing all translation versions
- **Translation Text Editor**: Rich text input with undo/redo
- **Version Management**:
  - Add new version button
  - Delete version button
  - Version comparison view
  - Source attribution display

**Features**:
- Real-time validation and spell checking
- Auto-save with change detection
- Version labeling with source information
- Side-by-side comparison between versions

### 3. Navigation Controls
**Purpose**: Efficient browsing through large translation datasets

**Components**:
- **Page Navigation**: First/Previous/Next/Last buttons
- **Page Size Selector**: 10, 30, 50, 100 entries per page
- **Current Page Indicator**: "Page X of Y" display
- **Quick Jump**: Direct page number input

**Features**:
- Keyboard shortcuts (Ctrl+Left/Right for page navigation)
- Smooth transitions with loading indicators
- Memory of current position when switching views

### 4. Search and Filter Bar
**Purpose**: Advanced search capabilities across both source and translation text

**Components**:
- **Search Input Field**: Pattern entry with regex support
- **Search Scope Selection**:
  - Source text (msgid) only
  - Translation text (msgstr) only
  - Both source and translation
- **Search Options**:
  - Case sensitivity toggle
  - Whole word matching
  - Regular expression mode
  - Negation (NOT) search

**Advanced Features**:
- **Context Filtering**: Filter by specific contexts
- **Source Filtering**: Filter by translation source (imported files)
- **Empty Entry Detection**: Find entries with missing translations
- **Duplicate Detection**: Identify similar or identical translations

### 5. Import/Export Operations
**Purpose**: Integration with external PO files and translation workflows

**Import Features**:
- **Multi-source Import**: Support for different dictionary types
  - Project-specific PO files
  - External translation memories
  - Custom file selection
- **Conflict Resolution**: Handle duplicate entries intelligently
- **Version Management**: Create new versions for existing entries
- **Source Tracking**: Tag imports with source information
- **Batch Processing**: Progress indicators for large files

**Export Features**:
- **Full Database Export**: Complete translation memory as PO file
- **Filtered Export**: Export based on current search/filter criteria
- **Version Selection**: Choose specific translation versions
- **Format Options**: Standard PO format with metadata preservation

### 6. Database Management
**Purpose**: Administrative operations for database maintenance

**Operations**:
- **Clear Database**: Remove all entries with confirmation
- **Vacuum Database**: Optimize storage and reset counters
- **Statistics Display**: Entry counts, version statistics
- **Backup/Restore**: Database file operations
- **Index Rebuilding**: Performance optimization

## Data Operations

### 1. Entry Management
**Create New Entry**:
- Manual entry creation with source text and context
- Initial translation version optional
- Automatic unique ID assignment
- Validation for duplicate source/context pairs

**Edit Existing Entry**:
- Modify source text and context (with impact warnings)
- Update translations while preserving version history
- Bulk editing operations for similar entries

**Delete Operations**:
- Individual entry deletion with cascade to all versions
- Version-specific deletion with renumbering
- Bulk deletion with confirmation dialogs

### 2. Version Control System
**Version Creation**:
- Automatic versioning for new translations
- Manual version creation for alternatives
- Source attribution for tracking translation origin
- Timestamp recording for change history

**Version Management**:
- Compare versions side-by-side
- Merge similar versions with user approval
- Promote specific versions as primary
- Archive outdated versions

### 3. Search Engine
**Pattern Matching**:
- Simple text search with case options
- Regular expression support with syntax validation
- Word boundary detection for precise matching
- Fuzzy matching for similar entries

**Result Processing**:
- Highlighted matches in both source and translation text
- Paginated search results with consistent navigation
- Search result statistics and performance metrics
- Export search results to external formats

## User Experience Features

### 1. Keyboard Shortcuts
- **Ctrl+F**: Open search bar
- **F3/Shift+F3**: Find next/previous
- **Ctrl+N**: New entry
- **Ctrl+E**: Edit current entry
- **Delete**: Delete selected entry
- **Ctrl+S**: Save current changes
- **Ctrl+I**: Import PO file
- **Ctrl+Shift+E**: Export database

### 2. Drag and Drop
- **File Drop**: Import PO files by dragging onto the interface
- **Entry Export**: Drag entries to external applications as PO data
- **Reordering**: Drag columns to rearrange table layout

### 3. Context Menus
- **Right-click Entry**: Edit, delete, export, view versions
- **Right-click Header**: Column visibility, sorting options
- **Right-click Search**: Search history, saved searches

### 4. Visual Feedback
- **Status Bar**: Current operation progress and statistics
- **Loading Indicators**: For long-running operations
- **Highlight System**: Search matches, modified entries, validation errors
- **Color Coding**: Different sources, entry states, version indicators

## Integration Points

### 1. Main Application Integration
- **Translation Suggestions**: Provide suggestions based on similarity
- **Auto-completion**: Offer translations from history during editing
- **Quality Assurance**: Flag inconsistent translations across entries
- **Project Sync**: Synchronize with current project's translation state

### 2. Editor Integration
- **Context Awareness**: Show relevant translations based on current editing context
- **Quick Insert**: Insert translations from history with keyboard shortcuts
- **Similarity Detection**: Highlight potential matches while editing
- **Validation Support**: Cross-reference translations for consistency

### 3. File Operations
- **Automatic Import**: Import translations when opening PO files
- **Background Sync**: Update history when saving project files
- **Conflict Resolution**: Handle conflicts between project and history
- **Version Tracking**: Maintain connection between file versions and history entries

## Technical Specifications

### Performance Optimization
- **Lazy Loading**: Load entries on-demand for large databases
- **Indexed Search**: Optimized database queries with proper indexing
- **Caching Strategy**: Memory caching for frequently accessed entries
- **Background Operations**: Non-blocking import/export operations

### Data Integrity
- **Transaction Management**: Atomic operations for data consistency
- **Validation Rules**: Ensure data quality and prevent corruption
- **Backup System**: Automatic backups before major operations
- **Recovery Mechanisms**: Handle database corruption gracefully

### Extensibility
- **Plugin Architecture**: Support for custom import/export formats
- **API Access**: Programmatic interface for external tools
- **Custom Fields**: Support for additional metadata per entry
- **Theming Support**: Customizable appearance and layout

## Configuration Options

### Database Settings
- **Location**: Custom database file path
- **Cache Size**: Memory allocation for performance
- **Auto-vacuum**: Automatic database optimization schedule
- **Backup Frequency**: Automated backup configuration

### Interface Preferences
- **Default Page Size**: Number of entries per page
- **Column Visibility**: Show/hide specific columns
- **Sort Preferences**: Default sorting column and order
- **Search Behavior**: Default search options and scope

### Import/Export Settings
- **Default Encoding**: Character encoding for file operations
- **Conflict Resolution**: Default behavior for duplicate entries
- **Source Naming**: Automatic source attribution patterns
- **File Associations**: Supported file types and handlers

This design provides a comprehensive translation memory management system that integrates seamlessly with the main PO Editor application while offering powerful standalone functionality for translation database management.
