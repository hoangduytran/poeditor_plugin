# Preferences Panel Implementation Plans

## Overview

This document provides detailed implementation plans for each of the four main preference panels, building on the foundational components defined in the Basic Components Design. Each panel leverages the unified pagination framework and shared components.

## 1. Replacement Rules Panel Implementation Plan

### 1.1 Panel Structure

**File:** `panels/preferences/replacement_rules_panel.py`

**Purpose:** Manage find/replace text rules with advanced search, filtering, and bulk operations.

**Layout Design:**
```
┌─ Replacement Rules Management ──────────────────────────────────────┐
│ ┌─ Database Pagination Controls ──────────────────────────────────┐ │
│ │ [Search: ____________] [Clear]                                   │ │
│ │ Filter: [All Rules ▼] Sort: [Find Text ▼] [▲]                  │ │
│ │ Page Size: [22 ▼] Page: [◀] [1] [2] [3] [▶] Total: 245 items    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Rules Table ───────────────────────────────────────────────────┐ │
│ │ [☑] │ ID │ Find Text    │ Replace Text │ Notes    │ Modified   │ │
│ │ ─────┼────┼──────────────┼──────────────┼──────────┼──────────── │ │
│ │ ☑   │ 1  │ %s          │ {0}          │ Format   │ 2025-08-04 │ │
│ │ ☐   │ 2  │ oldword     │ newword      │ Simple   │ 2025-08-03 │ │
│ │ ☑   │ 3  │ regex:(\d+) │ num_\1       │ Numbers  │ 2025-08-02 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Bulk Operations ───────────────────────────────────────────────┐ │
│ │ Selected: 2 rules                                               │ │
│ │ [Enable Selected] [Disable Selected] [Delete Selected]         │ │
│ │ [Export Selected] [Import Rules] [Clear All Filters]           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Rule Editor ───────────────────────────────────────────────────┐ │
│ │ Find Text:    [________________________] [Regex] [Case Sens.] │ │
│ │ Replace Text: [________________________]                       │ │
│ │ Notes:        [________________________]                       │ │
│ │ Enabled:      [☑] Active                                        │ │
│ │ [Add New Rule] [Update Selected] [Test Replace] [Clear Form]   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Implementation Details

**Core Components:**
1. **ReplacementRulesTable** - Enhanced table view with checkboxes and context menu
2. **RuleEditorWidget** - Form for adding/editing rules with validation
3. **BulkOperationsWidget** - Tools for batch operations on selected rules
4. **ReplacementRulesService** - Database service extending BaseDatabaseService

**Service Integration:**
```python
class ReplacementRulesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.rules_service = ReplacementRulesService("replacement_rules.db")
        self.settings_manager = PreferencesPagingSettingsManager()
        
        # Setup pagination factory
        self.pagination_factory = PreferencesPaginationFactory()
        
        # Create main table
        self.rules_table = ReplacementRulesTable()
        
        # Create pagination controller
        self.pagination_controller = self.pagination_factory.create_database_pagination(
            table_widget=self.rules_table,
            database_service=self.rules_service,
            component_name="replacement_table",
            settings_manager=self.settings_manager,
            parent=self
        )
        
        # Create enhanced pagination widget
        self.pagination_widget = self.pagination_factory.create_database_pagination_widget(
            controller=self.pagination_controller,
            show_filters=True,
            show_sort=True,
            parent=self
        )
        
        self._setup_ui()
        self._connect_signals()
```

**Key Features:**
- **Real-time search** with debounced input (300ms delay)
- **Advanced filtering** by status (enabled/disabled), creation date, rule type
- **Bulk operations** for enabling/disabling/deleting multiple rules
- **Rule validation** with regex testing and preview
- **Import/Export** functionality for rule sets
- **Column sorting** with persistent sort preferences
- **Context menu** with rule-specific actions

### 1.3 Database Schema

**Table: replacement_rules**
```sql
CREATE TABLE replacement_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    find_text TEXT NOT NULL,
    replace_text TEXT NOT NULL,
    is_regex BOOLEAN DEFAULT FALSE,
    case_sensitive BOOLEAN DEFAULT FALSE,
    enabled BOOLEAN DEFAULT TRUE,
    notes TEXT DEFAULT '',
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    last_used_date DATETIME NULL
);

CREATE INDEX idx_replacement_find_text ON replacement_rules(find_text);
CREATE INDEX idx_replacement_enabled ON replacement_rules(enabled);
CREATE INDEX idx_replacement_modified ON replacement_rules(modified_date);
```

## 2. Translation History Panel Implementation Plan

### 2.1 Panel Structure

**File:** `panels/preferences/translation_history_panel.py`

**Purpose:** Browse and manage translation history with search capabilities and cleanup tools.

**Layout Design:**
```
┌─ Translation History Browser ───────────────────────────────────────┐
│ ┌─ Database Pagination Controls ──────────────────────────────────┐ │
│ │ [Search: ____________] [Clear]                                   │ │
│ │ Filter: [All Translations ▼] Sort: [Date ▼] [▼]                │ │
│ │ Date Range: [2025-07-01] to [2025-08-04]                       │ │
│ │ Page Size: [22 ▼] Page: [◀] [1] [2] [3] [▶] Total: 1,247 items │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ History Table ─────────────────────────────────────────────────┐ │
│ │ [☑] │ Date/Time    │ Original Text  │ Translation    │ Action   │ │
│ │ ─────┼──────────────┼────────────────┼────────────────┼───────── │ │
│ │ ☑   │ 08-04 14:32  │ Hello world   │ Hola mundo     │ Added    │ │
│ │ ☐   │ 08-04 14:30  │ Good morning  │ Buenos días    │ Modified │ │
│ │ ☑   │ 08-04 14:25  │ Thank you     │ Gracias        │ Added    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ History Management ────────────────────────────────────────────┐ │
│ │ Selected: 2 entries                                             │ │
│ │ [Delete Selected] [Export Selected] [Clear Old Entries]        │ │
│ │ Auto-cleanup: [☑] Delete entries older than [30] days          │ │
│ │ [Cleanup Now] [Export All] [Clear All History] [Statistics]   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Entry Details ─────────────────────────────────────────────────┐ │
│ │ Selected Entry: #1247 (2025-08-04 14:32:15)                    │ │
│ │ Original:     [Hello world_________________________]            │ │
│ │ Translation:  [Hola mundo__________________________]            │ │
│ │ File Context: /project/messages.po:line 45                     │ │
│ │ User Action:  Added new translation                             │ │
│ │ [Restore This] [Copy Original] [Copy Translation]              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Implementation Details

**Core Components:**
1. **TranslationHistoryTable** - Table view with date/time formatting and action icons
2. **HistoryManagementWidget** - Cleanup tools and bulk operations
3. **EntryDetailsWidget** - Detailed view of selected history entry
4. **TranslationHistoryService** - Database service with date range filtering

**Service Integration:**
```python
class TranslationHistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.history_service = TranslationHistoryService("translation_history.db")
        self.settings_manager = PreferencesPagingSettingsManager()
        
        # Setup pagination with date range support
        self.pagination_controller = self.pagination_factory.create_database_pagination(
            table_widget=self.history_table,
            database_service=self.history_service,
            component_name="history_table",
            settings_manager=self.settings_manager,
            parent=self
        )
        
        # Create pagination widget with date range controls
        self.pagination_widget = self.pagination_factory.create_database_pagination_widget(
            controller=self.pagination_controller,
            show_filters=True,
            show_sort=True,
            show_date_range=True,
            parent=self
        )
```

**Key Features:**
- **Date range filtering** with calendar widget selection
- **Full-text search** across original and translated text
- **Action filtering** (added, modified, deleted, restored)
- **Bulk deletion** with confirmation dialogs
- **Auto-cleanup** with configurable retention period
- **Export functionality** for selected entries or date ranges
- **Entry restoration** to undo changes
- **Statistics view** showing translation activity

### 2.3 Database Schema

**Table: translation_history**
```sql
CREATE TABLE translation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    original_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    file_path TEXT DEFAULT '',
    line_number INTEGER DEFAULT 0,
    action_type TEXT NOT NULL, -- 'added', 'modified', 'deleted', 'restored'
    user_notes TEXT DEFAULT '',
    context_hash TEXT DEFAULT '', -- For matching related entries
    previous_translation TEXT DEFAULT '' -- For tracking changes
);

CREATE INDEX idx_history_timestamp ON translation_history(timestamp);
CREATE INDEX idx_history_original ON translation_history(original_text);
CREATE INDEX idx_history_action ON translation_history(action_type);
CREATE INDEX idx_history_context ON translation_history(context_hash);
```

## 3. Font Settings Panel Implementation Plan

### 3.1 Panel Structure

**File:** `panels/preferences/font_settings_panel.py`

**Purpose:** Configure fonts for different UI components with live preview.

**Layout Design:**
```
┌─ Font Settings Configuration ───────────────────────────────────────┐
│ ┌─ Font Categories ───────────────────────────────────────────────┐ │
│ │ ┌─ msgid (Source Text) ────────────────────────────────────────┐ │ │
│ │ │ Family: [Arial ▼] Size: [15] [Apply] [Reset]                │ │ │
│ │ │ Preview: [AaBbCc msgid: Original source text for translation] │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─ msgstr (Translation Text) ──────────────────────────────────┐ │ │
│ │ │ Family: [Times New Roman ▼] Size: [24] [Apply] [Reset]      │ │ │
│ │ │ Preview: [AaBbCc msgstr: Translated text in target language] │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─ Table Content ──────────────────────────────────────────────┐ │ │
│ │ │ Family: [Segoe UI ▼] Size: [13] [Apply] [Reset]             │ │ │
│ │ │ Preview: [AaBbCc Table Row | Column Header | Data Cell]      │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─ Comments & Notes ───────────────────────────────────────────┐ │ │
│ │ │ Family: [Courier New ▼] Size: [15] [Apply] [Reset]          │ │ │
│ │ │ Preview: [AaBbCc # Translator comment or note]               │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─ Suggestions ────────────────────────────────────────────────┐ │ │
│ │ │ Family: [Calibri ▼] Size: [13] [Apply] [Reset]              │ │ │
│ │ │ Preview: [AaBbCc Translation suggestion from memory]         │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─ UI Controls ────────────────────────────────────────────────┐ │ │
│ │ │ Family: [System Font ▼] Size: [12] [Apply] [Reset]          │ │ │
│ │ │ Preview: [AaBbCc Button Label | Menu Item | Dialog Title]    │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Global Font Actions ───────────────────────────────────────────┐ │
│ │ [Apply All Changes] [Reset All to Defaults] [Load Font Preset] │ │
│ │ [Save Current as Preset] [Import Font Config] [Export Config]  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Font Preview Window ───────────────────────────────────────────┐ │
│ │ Sample Text: [msgid] msgid "Hello, world!"                     │ │
│ │ Translation: [msgstr] msgstr "¡Hola, mundo!"                   │ │
│ │ Comment:     [comment] # Greeting message                       │ │
│ │ Table Data:  [table] ID | Source | Target | Status             │ │
│ │ Suggestion:  [suggestion] Suggestion: "Hola mundo"             │ │
│ │ UI Element:  [control] [Save Changes] [Cancel] [Apply]         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation Details

**Core Components:**
1. **FontCategoryWidget** - Individual font selector for each component type
2. **GlobalFontPreviewWidget** - Comprehensive preview showing all fonts together
3. **FontPresetManager** - Save/load font configurations as presets
4. **FontApplicationService** - Apply fonts throughout the application

**Service Integration:**
```python
class FontSettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.font_service = FontApplicationService()
        self.preset_manager = FontPresetManager()
        
        # Create font selectors for each component
        self.font_selectors = {}
        component_configs = self.font_service.get_font_component_configs()
        
        for component_name, config in component_configs.items():
            selector = FontSelectorWidget(
                component_name=component_name,
                display_name=self._get_display_name(component_name),
                default_size=config["default_size"],
                parent=self
            )
            selector.fontApplied.connect(self._on_font_applied)
            self.font_selectors[component_name] = selector
        
        # Create global preview
        self.global_preview = GlobalFontPreviewWidget()
        
        self._setup_ui()
        self._connect_signals()
        self._load_current_fonts()
```

**Key Features:**
- **Live preview** updates as fonts are selected
- **Component-specific** font configuration
- **Font presets** for quick switching between configurations
- **Import/Export** font configurations
- **Global preview** showing all fonts in context
- **Instant application** with rollback capability
- **System font detection** and recommendations

### 3.3 Font Component Mapping

**Component Categories:**
- **msgid (Source Text):** 15pt default, used for original text display
- **msgstr (Translation Text):** 24pt default, larger for better editing visibility  
- **Table Content:** 13pt default, compact for table views
- **Comments & Notes:** 15pt default, monospace preferred for code-like text
- **Suggestions:** 13pt default, subtle secondary text
- **UI Controls:** 12pt default, system font for consistency

## 4. Editor Settings Panel Implementation Plan

### 4.1 Panel Structure

**File:** `panels/preferences/editor_settings_panel.py`

**Purpose:** Configure editor behavior, appearance, and functionality.

**Layout Design:**
```
┌─ Editor Configuration ──────────────────────────────────────────────┐
│ ┌─ Editor Appearance ─────────────────────────────────────────────┐ │
│ │ Theme:           [Dark Theme ▼]                                 │ │
│ │ Line Numbers:    [☑] Show line numbers                          │ │
│ │ Word Wrap:       [☑] Enable word wrapping                       │ │
│ │ Syntax Highlight:[☑] Enable syntax highlighting                 │ │
│ │ Current Line:    [☑] Highlight current line                     │ │
│ │ Matching Braces: [☑] Highlight matching brackets/parentheses    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Editor Behavior ───────────────────────────────────────────────┐ │
│ │ Tab Size:        [4] spaces                                     │ │
│ │ Indent:          [☑] Use spaces [☐] Use tabs                    │ │
│ │ Auto Indent:     [☑] Auto-indent new lines                      │ │
│ │ Auto Complete:   [☑] Enable auto-completion                     │ │
│ │ Auto Save:       [☑] Auto-save every [5] minutes                │ │
│ │ Trim Whitespace: [☑] Remove trailing whitespace on save         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Translation Assistance ────────────────────────────────────────┐ │
│ │ Spell Check:     [☑] Enable spell checking                      │ │
│ │ Dictionary:      [English (US) ▼] [Add Language]               │ │
│ │ Suggestions:     [☑] Show translation suggestions               │ │
│ │ Fuzzy Matching:  [☑] Enable fuzzy string matching               │ │
│ │ Translation Memory: [☑] Use translation memory                  │ │
│ │ Max Suggestions: [5] per translation                            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Keyboard Shortcuts ────────────────────────────────────────────┐ │
│ │ Save:            [Ctrl+S]                    [Edit]             │ │
│ │ Find:            [Ctrl+F]                    [Edit]             │ │
│ │ Replace:         [Ctrl+H]                    [Edit]             │ │
│ │ Next Entry:      [Ctrl+Down]                 [Edit]             │ │
│ │ Previous Entry:  [Ctrl+Up]                   [Edit]             │ │
│ │ Toggle Fuzzy:    [Ctrl+U]                    [Edit]             │ │
│ │ [Reset to Defaults] [Import Shortcuts] [Export Shortcuts]      │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Advanced Settings ─────────────────────────────────────────────┐ │
│ │ Encoding:        [UTF-8 ▼]                                      │ │
│ │ Line Endings:    [Auto-detect ▼]                               │ │
│ │ Backup Files:    [☑] Create backup files (.bak)                │ │
│ │ Recent Files:    Keep [10] recent files in menu                 │ │
│ │ Plugin Support:  [☑] Enable plugin extensions                   │ │
│ │ Debug Mode:      [☐] Enable debug logging                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ ┌─ Settings Actions ──────────────────────────────────────────────┐ │
│ │ [Apply All Settings] [Reset to Defaults] [Import Settings]     │ │
│ │ [Export Settings] [Test Configuration] [Restore Backup]        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Implementation Details

**Core Components:**
1. **SettingsGroupWidget** - Collapsible group of related settings
2. **ShortcutEditorWidget** - Keyboard shortcut configuration
3. **ThemePreviewWidget** - Live theme preview
4. **EditorSettingsService** - Settings persistence and validation

**Service Integration:**
```python
class EditorSettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.settings_service = EditorSettingsService()
        self.theme_manager = ThemeManager()
        self.shortcut_manager = ShortcutManager()
        
        # Create settings groups
        self.appearance_group = SettingsGroupWidget("Editor Appearance")
        self.behavior_group = SettingsGroupWidget("Editor Behavior") 
        self.assistance_group = SettingsGroupWidget("Translation Assistance")
        self.shortcuts_group = SettingsGroupWidget("Keyboard Shortcuts")
        self.advanced_group = SettingsGroupWidget("Advanced Settings")
        
        self._setup_ui()
        self._connect_signals()
        self._load_current_settings()
```

**Key Features:**
- **Collapsible groups** for organized settings layout
- **Live preview** for theme and appearance changes
- **Keyboard shortcut** customization with conflict detection
- **Settings validation** with error highlighting
- **Import/Export** settings configurations
- **Backup/Restore** settings functionality
- **Plugin integration** settings
- **Auto-save** with configurable intervals

### 4.3 Settings Storage

**Configuration Categories:**
- **Appearance:** Theme, colors, fonts, visual indicators
- **Behavior:** Indentation, auto-complete, auto-save, file handling
- **Translation:** Spell checking, suggestions, memory, fuzzy matching
- **Shortcuts:** Customizable keyboard bindings
- **Advanced:** Encoding, line endings, plugins, debugging

## 5. Integration and Testing Strategy

### 5.1 Component Integration

**Shared Services:**
- All panels use `PreferencesPagingSettingsManager` for consistent pagination
- Font panels integrate with `FontApplicationService` for immediate application
- Database panels use `BaseDatabaseService` with pagination support
- Settings panels use centralized `QSettings` with grouped keys

**Cross-Panel Communication:**
- Settings changes emit signals for real-time updates
- Font changes immediately apply to all visible components
- Database operations trigger refresh signals
- Pagination settings sync across related panels

### 5.2 Testing Approach

**Unit Tests:**
- Test each service class independently
- Mock database connections for service tests
- Validate pagination controller integration
- Test font application and rollback

**Integration Tests:**
- Test panel initialization with all services
- Verify pagination widget connectivity
- Test settings persistence and loading
- Validate cross-panel signal communication

**UI Tests:**
- Test user interaction flows
- Verify responsive layouts
- Test keyboard shortcuts
- Validate accessibility features

This comprehensive implementation plan provides the detailed roadmap for building each preferences panel while maintaining consistency and leveraging the existing pagination framework effectively.
