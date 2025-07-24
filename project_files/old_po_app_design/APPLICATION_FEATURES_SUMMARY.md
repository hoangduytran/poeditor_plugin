# PySide PO Editor - Application Features Summary

## Overview
A comprehensive PO (Portable Object) file editor built with PySide6/Qt, designed for translating and managing GNU gettext translation files. The application provides professional translation workflow capabilities with advanced features for translators and localization teams.

## Core Architecture

### Main Components
- **Main Window** (`main_gui.py`) - Primary application interface with table-based editor
- **Global State** (`gvar.py`) - Application-wide state management and configuration
- **Action System** (`main_actions.py`, `main_utils/actions_factory.py`) - Command handling and business logic
- **Translation Database** (`pref/tran_history/`) - SQLite-based translation history and suggestions

## File Management

### Supported Operations
- **Open/Save PO Files** - Full support for GNU gettext PO file format
- **Import/Export** - Multiple format support for translation data
- **Auto-save and Recovery** - Automatic saving with crash recovery
- **File Association** - Native OS integration for PO file opening
- **Drag & Drop** - File loading via drag and drop interface

### File Format Support
- **PO Files** - Primary format (GNU gettext Portable Object)
- **Translation Memory** - JSON/CSV export/import for reusability
- **Backup Files** - Automatic backup creation before saves

## Translation Interface

### Main Editor Components
1. **Translation Table** - Main editing interface with columns:
   - Message ID (msgid) - Source text
   - Context (msgctxt) - Translation context
   - Translation (msgstr) - Target text
   - Fuzzy Flag - Translation status indicator
   - Line Number - Source file reference

2. **Editor Panels**
   - **Source Text Panel** - Read-only display of original text
   - **Translation Editor** - Rich text editor with replacement support
   - **Comments Panel** - Translator and extracted comments
   - **Fuzzy Toggle** - Mark translations as fuzzy/confirmed

3. **Suggestion System**
   - **Translation History** - Previous translations for same text
   - **Machine Translation** - Integrated translation suggestions
   - **Version Management** - Multiple translation versions per entry

## Advanced Editing Features

### Text Replacement System
- **Smart Replacements** (`pref/repl/`) - Configurable text substitutions
- **Shortcut Expansion** - Abbreviation expansion during typing
- **Pattern Matching** - Regex-based replacements
- **Import/Export Rules** - Shareable replacement configurations

### Translation Memory
- **SQLite Database** - Persistent translation storage
- **Version History** - Track all translation changes
- **Smart Suggestions** - Context-aware translation recommendations
- **Fuzzy Matching** - Similar text detection and suggestions

## Find and Replace System

### Search Capabilities
- **Multi-field Search** - Search across msgid, msgstr, and context
- **Regex Support** - Advanced pattern matching
- **Case-sensitive/Insensitive** - Flexible matching options
- **Scope Selection** - Search specific fields or all fields

### Replace Operations
- **Single Replace** - Replace individual matches
- **Replace All** - Batch replacement operations
- **Preview Mode** - Review changes before applying
- **Undo Support** - Revert changes if needed

### Find/Replace Dialog Types
1. **Inline Bar** - Quick search within main window
2. **Standalone Dialog** - Advanced search in separate window
3. **Results Dialog** - Dedicated results viewer with paging

## Navigation and Workflow

### Table Navigation
- **Keyboard Shortcuts** - Full keyboard navigation support
- **Paged Navigation** - Handle large files efficiently
- **Smart Scrolling** - Enhanced scrollbar with markers
- **Row Selection** - Multi-row operations support

### Specialized Navigation
- **Go to Line/Row** - Direct navigation to specific entries
- **Fuzzy Navigation** - Jump to fuzzy/untranslated entries
- **Issue Navigation** - Navigate to entries with problems
- **Search Results** - Navigate through find results

### Workflow Modes
- **Editor Mode** - Standard translation editing
- **Search Mode** - Focus on search results
- **Issues Mode** - Review and fix translation problems

## Translation Quality Assurance

### Issue Detection System
- **Configurable Rules** - Enable/disable specific issue types
- **Real-time Detection** - Issues highlighted as you type
- **Issue Types Supported**:
  - Empty translations
  - Fuzzy entries
  - Untranslated entries (msgid == msgstr)
  - Missing context
  - Placeholder mismatches
  - Formatting issues
  - Custom validation rules

### Visual Indicators
- **Pink Highlighting** - Issues highlighted in translation column
- **Status Messages** - Issue counts in status bar
- **Sort by Issues** - Move problematic entries to top

## Preferences and Customization

### Settings Categories
1. **Fonts and Languages** (`pref/kbd/font_settings.py`)
   - Message ID font configuration
   - Translation text font settings
   - Table display font
   - Comment text font
   - Suggestion panel font
   - Control elements font
   - Target language selection

2. **Keyboard Mappings** (`pref/kbd/keyboard_settings.py`)
   - Customizable keyboard shortcuts
   - Menu action shortcuts
   - Table navigation shortcuts
   - Editor shortcuts
   - Find/replace shortcuts

3. **Text Replacements** (`pref/repl/replacement_settings.py`)
   - Custom text substitutions
   - Abbreviation expansions
   - Import/export replacement rules
   - Pattern matching configuration

4. **Translation History** (`pref/tran_history/`)
   - Database management
   - History viewing and editing
   - Export/import translation memory
   - Version management

5. **Editor Settings** (`pref/settings/editor_settings_widget.py`)
   - Page size configuration
   - Scrollbar behavior
   - Font preferences
   - Navigation settings

6. **Translation/PO Settings** (`pref/settings/translation_settings_widget.py`)
   - Issue detection configuration
   - Quality assurance rules
   - Validation settings

### Additional Settings Tabs
- **General Settings** - Application-wide preferences
- **Appearance Settings** - Theme and visual customization
- **Network Settings** - Translation service configuration
- **Advanced Settings** - Power-user options

## User Interface Components

### Main Window Layout
- **Menu Bar** - Traditional application menus
- **Toolbar/Taskbar** - Quick access buttons
- **Main Table** - Central translation interface
- **Editor Panels** - Source, translation, and comments
- **Suggestion Panel** - Translation history and suggestions
- **Status Bar** - Progress and status information

### Dialog Windows
- **Preferences Dialog** - Tabbed settings interface
- **Find/Replace Dialog** - Advanced search interface
- **Translation History** - Database browser and editor
- **Issue Dialog** - Problem entries viewer
- **File Dialogs** - Open/save file operations

### Specialized Components
- **Paged Navigation** - Handle large datasets efficiently
- **Version Selector** - Choose between translation versions
- **Fuzzy Toggle** - Quick fuzzy flag management
- **Progress Indicators** - Long operation feedback

## Menu System

### File Menu
- Open, Save, Save As
- Import PO files
- Recent files
- Preferences
- Exit

### Edit Menu
- Standard editing operations (Copy, Paste, Undo, Redo)
- **Go to** submenu:
  - Navigation commands (Start, End, Next/Previous page)
  - Specialized navigation (Fuzzy, Untranslated, Issues)
  - Row/column jumping
- **Find/Replace** submenu:
  - Local find/replace
  - Standalone find/replace dialog
- **Sort** submenu:
  - Sort by various criteria
  - Sort by issues/problems
- **Issue** submenu:
  - Show/hide issue highlighting
  - Navigate to problem entries

### View Menu
- Display options
- Panel visibility toggles
- Zoom controls

### Tools Menu
- Taskbar toggle
- Additional utilities

## Keyboard Shortcuts

### Navigation Shortcuts
- `Ctrl+Home/End` - Go to start/end
- `Ctrl+Page Up/Down` - Previous/next page
- `Ctrl+Up/Down` - Go to previous/next entry
- `Ctrl+G` - Go to specific row/column

### Editing Shortcuts
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+,` - Preferences
- `Ctrl+F` - Find/Replace
- `Ctrl+Shift+F` - Standalone Find/Replace

### Specialized Navigation
- `Ctrl+Shift+F` - Next fuzzy entry
- `Ctrl+Shift+U` - Next untranslated entry
- `Ctrl+Shift+I` - Next entry with issues
- `Ctrl+Alt+E` - Go to last edit position

### Quality Assurance
- `Ctrl+Shift+H` - Toggle issue highlighting
- `Ctrl+I` - Show issues dialog

## Technical Architecture

### Framework and Libraries
- **PySide6** - Qt6 Python bindings for GUI
- **SQLite** - Translation database backend
- **polib** - PO file parsing and manipulation
- **Python 3.11+** - Core runtime

### Database Schema
- **english_text** - Source text storage
- **tran_text** - Translation versions with metadata
- **Indexes** - Optimized for search performance

### Plugin Architecture
- **Modular Design** - Separate components for different features
- **Settings System** - QSettings-based configuration
- **Signal/Slot System** - Event-driven communication

## Development and Testing

### Code Organization
- **Main Application** - Core GUI and business logic
- **Preferences** - Settings and configuration
- **Subcmp** - Reusable UI components
- **Workspace** - Advanced features and dialogs
- **Tests** - Comprehensive test suite
- **Examples** - Component demonstrations

### Testing Infrastructure
- **Unit Tests** - Component-level testing
- **Integration Tests** - Feature workflow testing
- **Demo Applications** - Standalone component testing
- **Manual Test Cases** - User workflow validation

## Deployment and Distribution

### Platform Support
- **macOS** - Native application with proper integration
- **Cross-platform** - Qt6 ensures Linux/Windows compatibility
- **File Associations** - Register as default PO file handler

### Build System
- **Makefile** - Build automation
- **Setup Scripts** - Installation and configuration
- **Requirements** - Dependency management

## Future Extensibility

### Planned Features (from codebase structure)
- **Network Integration** - Cloud translation services
- **Plugin System** - Third-party extensions
- **Advanced Appearance** - Themes and customization
- **Collaboration** - Multi-user translation support

### Architecture Benefits
- **Modular Design** - Easy to extend and maintain
- **Settings Framework** - User customization support
- **Database Backend** - Scalable data management
- **Signal/Slot System** - Loose coupling between components

## Summary

This PO Editor represents a professional-grade translation tool with comprehensive features for managing GNU gettext localization workflows. It combines traditional PO file editing with modern features like translation memory, quality assurance, advanced search/replace, and extensive customization options. The modular architecture and extensive test coverage make it suitable for both individual translators and large localization teams.

Key strengths include:
- **Comprehensive PO file support** with all standard features
- **Advanced translation memory** with SQLite backend
- **Powerful search and replace** with multiple dialog types
- **Quality assurance tools** with configurable issue detection
- **Extensive customization** through tabbed preferences
- **Professional workflow support** with specialized navigation
- **Modern Qt6 interface** with responsive design
- **Cross-platform compatibility** with native OS integration
