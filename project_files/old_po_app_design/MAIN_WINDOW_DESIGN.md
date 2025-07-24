# Main Window and Core Actions Design Specification

## Overview
The main window serves as the central hub of the PO Editor application, providing a comprehensive interface for translation editing with advanced features including search/replace, quality assurance, version control, and workflow management. The architecture follows a modular design with clear separation between UI components, business logic, and data management.

## Core Architecture

### Main Window Structure (`POEditorWindow`)
**Purpose**: Primary application interface providing centralized access to all translation functionality

**Design Philosophy**: 
- **Split-panel Layout**: Horizontal division between editing area and assistance panels
- **Responsive Sizing**: All panels are resizable and collapsible for workflow optimization
- **Context-aware UI**: Interface adapts based on current mode (editing, searching, issue review)
- **State Preservation**: Maintains user preferences and session state across restarts

## Main Interface Components

### 1. Primary Table Interface
**Purpose**: Central translation editing table with pagination and advanced navigation

**Layout Configuration**:
- **Table Model**: `POFileTableModel` with live data binding to PO entries
- **Column Structure**:
  - **Index**: Entry position in file (auto-sizing)
  - **Message ID**: Source text (msgid) - stretchable
  - **Translation**: Target text (msgstr) - stretchable with issue highlighting
  - **Context**: Optional msgctxt field (auto-sizing)
  - **Fuzzy**: Translation status flag (fixed width)
  - **Line No**: Source file line reference (content-sizing)

**Advanced Features**:
- **Paged Navigation**: Configurable page size (default: 50 entries)
- **Smart Scrollbar**: `TransparentMarkerScrollbar` with visual navigation aids
- **Selection Modes**: Single row selection with keyboard navigation
- **Edit Triggers**: Double-click, selected-click, keyboard editing
- **Issue Highlighting**: Pink highlighting for problematic translations

### 2. Translation Editor Panel
**Purpose**: Comprehensive editing interface for translation work

**Component Structure**:
- **Source Text Display**: Read-only msgid with syntax highlighting
- **Translation Editor**: `TranslationEditorWidget` with advanced features:
  - Multi-line text editing with word wrap
  - Real-time replacement processing
  - Undo/redo functionality
  - Spell checking integration
- **Fuzzy Toggle**: Checkbox for marking translation status
- **Vertical Splitter**: Resizable between source and translation areas

**Integration Points**:
- **Real-time Validation**: Immediate issue detection during typing
- **Suggestion Integration**: Auto-complete from translation history
- **Replacement System**: Automatic text expansions and substitutions

### 3. Suggestions Panel
**Purpose**: Translation memory and version management interface

**Components**:
- **Suggestions Table**: `VersionTableModel` displaying translation history
  - Version ID column
  - Translation text column with word wrapping
  - Source attribution column
- **Context Menu**: Copy, paste, view operations
- **Version Navigation**: Select and apply previous translations
- **Database Integration**: Live connection to SQLite translation memory

**Workflow Features**:
- **Double-click Insert**: Apply suggestion to current translation
- **Version Comparison**: Visual diff between translation versions
- **Source Tracking**: Attribution of translation origins (files, users, systems)

### 4. Comments and Metadata Panel
**Purpose**: Translator and extractor comments management

**Features**:
- **Multi-line Comments**: Full text editing for translator notes
- **Extracted Comments**: Display of source code comments
- **Reference Information**: Source file locations and line numbers
- **Formatting Support**: Basic rich text for organization

### 5. Find/Replace Bar
**Purpose**: Advanced search and replacement functionality

**Search Capabilities**:
- **Multi-field Search**: Across msgid, msgstr, and context
- **Search Modes**: Text, regex, whole word, case-sensitive
- **Scope Selection**: Current page, entire file, selected entries
- **Real-time Results**: Live search result highlighting

**Replace Operations**:
- **Single Replace**: Individual match replacement
- **Replace All**: Batch operations with confirmation
- **Pattern Replace**: Regex-based substitutions
- **Preview Mode**: Review changes before applying

### 6. Status and Navigation Bar
**Purpose**: Information display and quick navigation controls

**Information Display**:
- **Current Position**: Row/column indicators
- **File Status**: Modified state, entry counts
- **Search Status**: Match counts, navigation position
- **Issue Summary**: Problem count and types

**Quick Actions**:
- **Page Navigation**: First, previous, next, last buttons
- **Jump to Position**: Direct row/column input
- **Issue Navigation**: Jump to problematic entries
- **Search Navigation**: Move between search results

## Menu System Architecture

### File Menu
**Core Operations**:
- **File Management**: Open, Save, Save As with full error handling
- **Import/Export**: PO file operations with format validation
- **Recent Files**: Quick access to previously opened files
- **Application Settings**: Access to comprehensive preferences

**Technical Implementation**:
- **Drag & Drop**: File loading via drag and drop interface
- **Auto-save**: Configurable automatic saving
- **Backup Creation**: Automatic backup before save operations
- **Error Recovery**: Graceful handling of file corruption

### Edit Menu
**Standard Operations**:
- **Clipboard**: Copy, paste, cut with format preservation
- **Undo System**: Multi-level undo/redo with action descriptions
- **Text Manipulation**: Standard editing operations

**Advanced Navigation (`Go to` Submenu)**:
- **Position Navigation**: Start, end, specific row/column
- **Page Navigation**: Next/previous page with smooth transitions
- **Content-based Navigation**: 
  - Fuzzy entries (needs review)
  - Untranslated entries (missing translations)
  - Translated entries (completed work)
  - Issue entries (problematic translations)
  - Modified entries (recent changes)
- **Context Navigation**: Last edit position, last search result

**Search Operations (`Find/Replace` Submenu)**:
- **Local Search**: In-page search with highlighting
- **Global Search**: File-wide search with results dialog
- **Advanced Replace**: Pattern-based replacements
- **Search History**: Previous search terms and results

**Sorting Options (`Sort` Submenu)**:
- **Content-based Sorting**: By translation status, content
- **Position-based Sorting**: By line number, entry ID
- **Issue-based Sorting**: Problematic entries first

**Quality Assurance (`Issue` Submenu)**:
- **Issue Display**: Toggle highlighting of problematic entries
- **Issue Navigation**: Jump between different issue types
- **Issue Filtering**: Show only entries with specific problems

### View Menu
**Interface Customization**:
- **Panel Visibility**: Show/hide suggestions, comments, find bar
- **Display Options**: Font sizes, color schemes, layout modes
- **Minimalistic Mode**: Streamlined interface for focused work

### Tools Menu
**Utility Functions**:
- **Taskbar Toggle**: Show/hide quick action toolbar
- **External Tools**: Integration with external editors
- **Workflow Tools**: Batch operations, automation scripts

## Core Action System

### File Operations
**Open File Action (`on_open_file`)**:
- **File Dialog**: Standard OS file picker with PO filter
- **Format Validation**: Verify PO file structure before loading
- **Error Handling**: Graceful failure with user feedback
- **Window Title**: Update with filename for context

**Save Operations (`on_save_file`, `on_save_file_as`)**:
- **Format Preservation**: Maintain PO file structure and metadata
- **Backup Creation**: Automatic backup before overwriting
- **Modification Tracking**: Clear modified entry markers
- **Status Feedback**: User notification of save completion

### Navigation Actions
**Position Navigation**:
- **Absolute Positioning**: Jump to specific row/column coordinates
- **Relative Navigation**: Move by pages, entries, or search results
- **Context Preservation**: Maintain focus and selection state
- **Page Management**: Automatic page switching for distant navigation

**Content-based Navigation**:
- **Filter Integration**: Work with table filtering and search modes
- **Wrap-around Logic**: Seamless navigation from end to beginning
- **Status Reporting**: User feedback on navigation results
- **Focus Management**: Proper focus handling for editing workflow

### Search and Replace Actions
**Search Functionality**:
- **Multi-mode Search**: Text, regex, and pattern matching
- **Scope Management**: Page, file, or selection-based searching
- **Result Highlighting**: Visual indication of matches
- **Navigation Integration**: Move between search results

**Replace Operations**:
- **Validation**: Verify replacement patterns before applying
- **Preview Mode**: Show changes before committing
- **Batch Processing**: Handle multiple replacements efficiently
- **Undo Integration**: Ensure all changes are reversible

### Quality Assurance Actions
**Issue Detection**:
- **Real-time Analysis**: Continuous checking during editing
- **Configurable Rules**: User-defined quality criteria
- **Performance Optimization**: Efficient checking algorithms
- **Visual Feedback**: Clear indication of problem areas

**Issue Navigation**:
- **Filtered Views**: Show only entries with specific issues
- **Priority Ordering**: Sort by issue severity or type
- **Batch Resolution**: Tools for fixing common problems
- **Progress Tracking**: Monitor improvement over time

## State Management

### Search Mode State
**Mode Switching**:
- **Entry Conditions**: Triggered by Ctrl+F or search actions
- **State Preservation**: Save current position and selection
- **UI Adaptation**: Show search-specific interface elements
- **Exit Conditions**: ESC key or explicit mode switching

**Search State Variables**:
- **Result Storage**: List of `FindReplaceResult` objects
- **Navigation Tracking**: Current position in search results
- **Instance Management**: Detailed match-level navigation
- **Highlight Coordination**: Visual indication of current match

### Edit Position Tracking
**Last Edit Position**:
- **Automatic Tracking**: Record position on every edit operation
- **Page Calculation**: Store page information for navigation
- **Quick Return**: Ctrl+Alt+E for instant return to last edit
- **Persistence**: Maintain across search operations and mode changes

### Modification Tracking
**Changed Entry Management**:
- **Modified Set**: Track all changed entries for save optimization
- **Visual Indicators**: Mark changed entries in interface
- **Save Coordination**: Only save modified entries for performance
- **Conflict Resolution**: Handle concurrent modification scenarios

## Integration Architecture

### Translation Memory Integration
**Database Connection**:
- **SQLite Backend**: Persistent storage of translation history
- **Version Control**: Track all translation changes over time
- **Suggestion Engine**: Provide context-aware translation suggestions
- **Import/Export**: Sync with external translation memories

### Replacement System Integration
**Text Processing**:
- **Rule Engine**: Apply user-defined text replacements
- **Context Awareness**: Smart replacements based on content
- **Performance Optimization**: Efficient pattern matching
- **User Feedback**: Visual indication of applied replacements

### Quality Assurance Integration
**Issue Detection Engine**:
- **Rule-based Validation**: Configurable quality checks
- **Real-time Processing**: Immediate feedback during editing
- **Batch Analysis**: File-wide quality assessment
- **Reporting System**: Detailed issue reports and statistics

## Technical Specifications

### Performance Optimization
**Memory Management**:
- **Lazy Loading**: Load only visible table rows
- **Efficient Rendering**: Optimized table drawing and updates
- **Background Processing**: Non-blocking operations for large files
- **Cache Management**: Intelligent caching of frequently accessed data

### Error Handling
**Robust Error Management**:
- **Exception Catching**: Graceful handling of all error conditions
- **User Feedback**: Clear error messages with recovery suggestions
- **State Recovery**: Restore application state after errors
- **Logging Integration**: Comprehensive error logging for debugging

### Extensibility Framework
**Plugin Architecture**:
- **Action Framework**: Pluggable action system for extensions
- **Widget Framework**: Custom widget integration points
- **Event System**: Comprehensive event handling for plugins
- **API Access**: Programmatic interface for external tools

This comprehensive design provides a professional-grade translation editing environment that combines powerful editing capabilities with advanced workflow features, quality assurance tools, and extensible architecture for long-term maintainability and enhancement.
