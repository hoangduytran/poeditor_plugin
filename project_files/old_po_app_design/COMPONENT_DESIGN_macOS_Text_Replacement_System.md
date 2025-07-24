# Component Design: macOS Text Replacement Import System with Table View and Paging

## 1. Component Overview

The macOS Text Replacement Import System is a sophisticated GUI component that provides comprehensive management of text replacement rules with support for importing macOS plist files. The system features a table view with advanced search capabilities, paging mechanisms, and full CRUD operations for text substitution rules.

### 1.1 Core Purpose
- **macOS Integration**: Native support for importing macOS Text Replacement plist files
- **Cross-Platform Compatibility**: Unified interface for managing text replacements across operating systems
- **Advanced Search**: Multi-scope search with regex, case sensitivity, and word boundary options
- **Table Management**: Sortable two-column table with intelligent display and navigation
- **Real-time Processing**: Live text substitution during typing with undo support

### 1.2 Key Components
- **ReplacementsDialog**: Main GUI widget with table view and editing panels
- **ReplacementActions**: Business logic controller for all operations
- **ReplacementEngine**: Multi-format import/export engine with handlers
- **Search System**: Advanced search with scope selection and pattern matching
- **Text Integration**: Real-time replacement in text editors

## 2. Architecture Design

### 2.1 Component Hierarchy

```
macOS Text Replacement System
├── ReplacementsDialog (QWidget)
│   ├── Import/Export Section
│   │   ├── Import Button (plist, JSON, CSV)
│   │   └── Export Button (multiple formats)
│   ├── Advanced Search Interface
│   │   ├── Scope Selector (Both/Shortcut/Replacement)
│   │   ├── Search Modifiers (Case/Word/Regex)
│   │   ├── Search Field (ReplacementLineEdit)
│   │   └── Navigation Controls (Find/Prev/Next)
│   ├── Replacement Table (QTableWidget)
│   │   ├── Sortable Headers (Shortcut/Replacement)
│   │   ├── Row Selection Mode
│   │   └── Highlighting System
│   └── Edit Panel
│       ├── Input Fields (Shortcut/Replacement)
│       └── Action Buttons (Add/Delete/Save)
├── ReplacementActions (Controller)
│   ├── Search Logic
│   ├── Navigation Management
│   └── CRUD Operations
└── ReplacementEngine (Import/Export)
    ├── PlistHandler (macOS native)
    ├── JsonHandler (cross-platform)
    └── CsvHandler (interoperability)
```

### 2.2 Data Flow Architecture

```
macOS plist Files → Import Engine → Internal Storage → Table Display → User Interaction
                                         ↓                    ↑
System Integration ← Export Engine ← QSettings Backend ← Edit Operations
```

### 2.3 Integration Points

- **QSettings Storage**: Cross-platform persistent storage using "TextReplacements" key
- **Text Editor Integration**: Real-time replacement in ReplacementLineEdit and ReplacementTextEdit
- **File System Integration**: Drag-and-drop support for importing plist and other formats
- **macOS System Integration**: Direct import from `~/Library/Preferences/com.apple.TextReplacement.plist`

## 3. Core Components Detail

### 3.1 ReplacementsDialog (Main GUI)

**Purpose**: Primary user interface for managing text replacement rules with comprehensive editing capabilities.

**Key Features**:
```python
class ReplacementsDialog(QWidget):
    SHORTCUT = 0        # Column indices for sorting
    REPLACEMENT = 1
    
    # Core properties
    column_type: int                # Current sort column
    sort_descending: bool          # Sort direction
    current_edit_row: int          # Currently edited row index
```

**Layout Structure**:
1. **Import/Export Section**: File operations at the top
2. **Advanced Search Interface**: Comprehensive search controls
3. **Replacement Table**: Main data display with sorting
4. **Edit Panel**: Input fields and action buttons

### 3.2 Advanced Search Interface

**Purpose**: Provide sophisticated search capabilities with multiple options and real-time feedback.

**Search Scope Selector**:
```python
self.scope_combo = QComboBox()
self.scope_combo.addItems(["Both", "Shortcut", "Replacement"])
```

**Search Modifiers**:
- **Match Case ("Aa")**: Toggle case-sensitive searching
- **Whole Word ("ab" underlined)**: Match complete words only
- **Regular Expression (".*")**: Enable regex pattern matching
- **Real-time Updates**: Search results update as options change

**Navigation Controls**:
- **Find Button**: Execute search with current criteria
- **Previous/Next ("↑"/"↓")**: Navigate through search results
- **Auto-enable**: Buttons activate only when search has results

### 3.3 Replacement Table with Paging

**Purpose**: Display and manage replacement rules in a sortable, navigable table view.

**Table Configuration**:
```python
self.table = QTableWidget(0, 2)
self.table.setHorizontalHeaderLabels(["Shortcut", "Replacement"])
header = self.table.horizontalHeader()
header.setSectionResizeMode(0, QHeaderView.Stretch)
header.setSectionResizeMode(1, QHeaderView.Stretch)
```

**Features**:
- **Two-column Layout**: Clear shortcut → replacement mapping
- **Stretch Headers**: Columns automatically resize to available space
- **Row Selection Mode**: Select entire replacement rule
- **Sort Functionality**: Click headers to sort by column
- **No Direct Editing**: Prevents accidental modifications
- **Search Highlighting**: Visual highlighting of search matches

**Paging Mechanism**:
- **Virtual Scrolling**: Efficient handling of large datasets
- **Search Result Navigation**: Step through filtered results
- **Smooth Scrolling**: Automatic scrolling to highlighted matches
- **Match Highlighting**: Yellow background for current search match

### 3.4 macOS plist Import Engine

**Purpose**: Native support for importing macOS Text Replacement plist files with fallback compatibility.

**PlistHandler Implementation**:
```python
class PlistHandler(BaseHandler):
    @staticmethod
    def import_file(path: str) -> List[ReplacementRecord]:
        with open(path, 'rb') as f:
            data = plistlib.load(f)
        try:
            # Standard format: 'replace' and 'with' keys
            rep_list = [ReplacementRecord(item['replace'], item['with']) for item in data]
        except Exception:
            # Fallback format: 'shortcut' and 'phrase' keys
            rep_list = [ReplacementRecord(item['shortcut'], item['phrase']) for item in data]
        return rep_list
```

**Default Import Paths**:
- **macOS**: `~/Library/Preferences/com.apple.TextReplacement.plist`
- **Windows**: AutoHotkey script format (`text_replacements.ahk`)
- **Linux**: ibus-bamboo macro format (`~/.config/ibus-bamboo/ibus-bamboo.macro.text`)

### 3.5 Multi-Format Export System

**Purpose**: Export replacement rules to various formats for cross-platform compatibility.

**Export Targets**:
```python
def _default_export_target():
    system = sys.platform
    if system == 'darwin':
        return 'plist', os.path.join(user, 'Library/Preferences/com.apple.TextReplacement.plist')
    elif system.startswith('win'):
        return 'ahk', os.path.join(user, 'text_replacements.ahk')
    else:
        return 'macro', os.path.join(user, '.config/ibus-bamboo/ibus-bamboo.macro.text')
```

**Supported Formats**:
- **plist**: Native macOS format
- **JSON**: Cross-platform structured data
- **CSV**: Spreadsheet compatibility
- **YAML**: Human-readable configuration
- **SQLite**: Database storage for large datasets
- **AutoHotkey**: Windows automation scripts
- **ibus-bamboo**: Linux input method macros

## 4. Search and Navigation System

### 4.1 Advanced Search Implementation

**Multi-Scope Search**:
```python
def on_search_text_changed(self, text: str, scope: str = "both", 
                          match_case: bool = False, boundary: bool = False, 
                          regex: bool = False):
    # Determine search columns based on scope
    if scope == "shortcut":
        cols = [0]
    elif scope == "replacement":
        cols = [1]
    else:  # both
        cols = [0, 1]
```

**Pattern Matching Modes**:
- **Literal Text**: Direct string matching with optional case sensitivity
- **Word Boundary**: Match complete words using word splitting
- **Regular Expression**: Full regex support with error handling
- **Real-time Validation**: Immediate feedback on pattern validity

### 4.2 Search Result Navigation

**Match Management**:
```python
class ReplacementActions:
    def __init__(self, dialog):
        self.matches = []           # List of matching row indices
        self.match_index = -1       # Current position in matches
```

**Navigation Controls**:
- **Find**: Jump to first match and start navigation
- **Previous/Next**: Step through matches with wraparound
- **Visual Highlighting**: Yellow background for current match
- **Auto-scroll**: Automatically scroll table to show current match

### 4.3 Highlighting System

**Visual Feedback**:
```python
def _highlight_match(self):
    # Clear all highlighting
    for row in range(self.dialog.table.rowCount()):
        self.dialog.table.item(row, 0).setBackground(Qt.white)
        self.dialog.table.item(row, 1).setBackground(Qt.white)
    
    # Highlight current match
    if 0 <= self.match_index < len(self.matches):
        row = self.matches[self.match_index]
        self.dialog.table.item(row, 0).setBackground(QColor(255, 255, 0))
        self.dialog.table.item(row, 1).setBackground(QColor(255, 255, 0))
```

## 5. Data Management and Storage

### 5.1 Internal Data Model

**ReplacementRecord Structure**:
```python
class ReplacementRecord:
    def __init__(self, trigger: str, replacement: str):
        self.trigger = trigger          # Shortcut text to trigger replacement
        self.replacement = replacement  # Text to replace with
    
    def to_dict(self) -> dict:
        return {'replace': self.trigger, 'with': self.replacement}
```

**QSettings Integration**:
```python
SETTINGS_KEY = "TextReplacements"

# Storage format: Array of dictionaries
[
    {"replace": "shortcut1", "with": "replacement1"},
    {"replace": "shortcut2", "with": "replacement2"}
]
```

### 5.2 Sorting and Organization

**Table Sorting**:
```python
def _replacement_refresh_table(self):
    raw = self.settings.value(SETTINGS_KEY, [])
    rows = [(e.get('replace'), e.get('with')) for e in raw 
            if e.get('replace') and e.get('with')]
    rows.sort(key=lambda x: x[self.column_type], reverse=self.sort_descending)
```

**Sort Options**:
- **By Shortcut**: Alphabetical sorting of trigger text
- **By Replacement**: Alphabetical sorting of replacement text
- **Ascending/Descending**: Toggle sort direction
- **Persistent State**: Sort preferences maintained during session

## 6. Text Editor Integration

### 6.1 Real-time Replacement

**Live Processing**:
- **Word Boundary Detection**: Trigger replacements at appropriate boundaries
- **Context Awareness**: Apply rules based on current editing context
- **Undo Integration**: Replacements can be undone like normal edits

**Integration Components**:
- **ReplacementLineEdit**: Single-line editor with replacement support
- **ReplacementTextEdit**: Multi-line editor with replacement support
- **ReplacementBase**: Shared base class for replacement logic

### 6.2 Replacement Logic

**Processing Flow**:
1. **Keystroke Detection**: Monitor for replacement triggers
2. **Boundary Validation**: Ensure proper word boundaries
3. **Rule Matching**: Find applicable replacement rules
4. **Text Substitution**: Replace trigger with replacement text
5. **Cursor Positioning**: Maintain proper cursor position

## 7. Import/Export Operations

### 7.1 File Format Handlers

**Handler Registry**:
```python
HANDLERS = {
    'plist': PlistHandler,
    'json': JsonHandler,
    'csv': CsvHandler,
    'yaml': YamlHandler,
    'sqlite': SqliteHandler,
    'ahk': AutoHotkeyHandler,
    'macro': BambooMacroHandler
}
```

**Dynamic Format Detection**:
- **Extension-based**: Automatic format detection from file extension
- **Content Analysis**: Fallback content-based format detection
- **Error Handling**: Graceful degradation with informative error messages

### 7.2 Cross-Platform Export

**Platform-Specific Formats**:
- **macOS**: Export to system Text Replacement plist
- **Windows**: Generate AutoHotkey script for text expansion
- **Linux**: Create ibus-bamboo macro file for input method

**Export Features**:
- **Backup Creation**: Automatic backup of existing files
- **Format Conversion**: Convert between different replacement formats
- **Batch Operations**: Export multiple rule sets simultaneously

## 8. User Experience Features

### 8.1 Progressive Disclosure

**Complexity Management**:
- **Basic Operations**: Simple add/delete operations prominently displayed
- **Advanced Search**: Collapsible search options with visual indicators
- **Expert Features**: Import/export and regex options available but not overwhelming

### 8.2 Immediate Feedback

**Real-time Updates**:
- **Live Search**: Results appear instantly as user types
- **Selection Feedback**: Clicked rules immediately populate edit fields
- **Status Indication**: Button states clearly indicate available actions
- **Progress Indicators**: Visual feedback during import/export operations

### 8.3 Error Prevention and Recovery

**Input Validation**:
- **Empty Field Prevention**: Validate shortcut and replacement text
- **Duplicate Detection**: Warn when adding duplicate shortcuts
- **Format Validation**: Check file formats before import

**Recovery Mechanisms**:
- **Undo Support**: Reversible operations with clear undo paths
- **Backup Creation**: Automatic backups before major operations
- **Error Messages**: Clear, actionable error descriptions

## 9. Performance Optimization

### 9.1 Large Dataset Handling

**Efficient Operations**:
- **Lazy Loading**: Load replacement rules on demand
- **Incremental Search**: Search only visible table rows when possible
- **Memory Management**: Efficient storage of large rule sets

### 9.2 Search Performance

**Optimization Strategies**:
- **Scope Limiting**: Search only selected columns to reduce workload
- **Regex Caching**: Cache compiled regular expressions
- **Early Termination**: Stop searching when maximum results reached

## 10. Configuration and Customization

### 10.1 User Preferences

**Configurable Options**:
- **Default Import Path**: User-specified default import location
- **Auto-export**: Automatic export to system on changes
- **Search Behavior**: Default search scope and options
- **Table Display**: Column widths and sort preferences

### 10.2 Advanced Settings

**Expert Configuration**:
- **Replacement Engine**: Custom replacement processing rules
- **File Format Priorities**: Preferred import/export formats
- **Performance Tuning**: Search and display optimization settings

## 11. Integration Patterns

### 11.1 Application Integration

**Embedding in Preferences**:
```python
# Integration into main application preferences
preferences_dialog = PreferencesDialog()
replacements_panel = ReplacementsDialog()
preferences_dialog.add_panel("Text Replacements", replacements_panel)
```

### 11.2 Standalone Usage

**Independent Operation**:
- **Self-contained Widget**: Can operate independently of main application
- **Drag-and-Drop Support**: Accept dropped plist files for import
- **System Integration**: Direct access to macOS Text Replacement system

## 12. Future Enhancements

### 12.1 Advanced Features

**Planned Improvements**:
- **Conditional Replacements**: Context-sensitive replacement rules
- **Rule Categories**: Organize replacements into themed groups
- **Macro Support**: More complex text expansion with variables
- **Cloud Sync**: Synchronize replacement rules across devices

### 12.2 AI Integration

**Machine Learning Features**:
- **Smart Suggestions**: AI-powered replacement recommendations
- **Usage Analytics**: Track and optimize replacement patterns
- **Natural Language Processing**: Context-aware replacement logic

This comprehensive text replacement system provides seamless integration with macOS while offering powerful cross-platform functionality. The combination of advanced search, intelligent paging, and robust import/export capabilities makes it a professional-grade solution for text substitution management in translation and productivity workflows.
