# Preferences Plugin Integration Plan

## Phase 1: Core Foundation and Basic Components

### 1.1 Essential Utility Classes

These high-usage utility classes form the foundation of the preferences system:

| Class Name | Original Path | Usage Count | Purpose |
|------------|---------------|-------------|---------|
| `ReplacementBase` | `subcmp/replacement_base.py` | 8 | Base implementation for text replacement functionality |
| `ReplacementRecord` | `pref/repl/replacement_engine.py` | 36 | Data model for text replacement pairs |
| `TablePagerBase` | `subcmp/table_nav_widget.py` | 4 | Pagination controller for table views |

### 1.2 Core GUI Components

These components are essential building blocks for the preferences UI:

| Class Name | Original Path | Usage Count | Purpose |
|------------|---------------|-------------|---------|
| `PreferencesDialog` | `pref/preferences.py` | 5 | Main tabbed preferences dialog |
| `EditorSettingsWidget` | `pref/settings/editor_settings_widget.py` | 12 | Editor-specific settings panel |
| `TranslationSettingsWidget` | `pref/settings/translation_settings_widget.py` | 5 | Translation settings panel |
| `ReplacementSettingsTab` | `pref/repl/replacement_settings.py` | 3 | Text replacement configuration panel |
| `FontSettingsTab` | `pref/kbd/font_settings.py` | 3 | Font configuration panel |
| `KeyboardSettingsTab` | `pref/kbd/keyboard_settings.py` | 3 | Keyboard shortcuts configuration panel |

### 1.3 Implementation Strategy for Phase 1

1. **Create Plugin Structure**
   - Implement `PreferencesPlugin` class that registers with the plugin system
   - Define clear API interfaces for settings access

2. **Design New Component Hierarchy**
   - Create base `SettingsPanel` class that all panels will inherit from
   - Implement settings storage/retrieval through a centralized `SettingsManager`

3. **Refactor Replacement System**
   - Modernize `ReplacementBase` and `ReplacementRecord` for the new architecture
   - Use PySide6 signals/slots for improved communication

4. **Build Core Preferences Dialog**
   - Implement tabbed interface with dynamic panel loading
   - Create plugin extension point for other plugins to add their settings panels

## Phase 2: Additional Settings Panels and Enhanced Features

### 2.1 Secondary Settings Panels

These panels complete the preferences UI but are lower priority:

| Class Name | Original Path | Usage Count | Purpose |
|------------|---------------|-------------|---------|
| `AdvancedSettingsWidget` | `pref/settings/advanced_settings_widget.py` | 4 | Advanced configuration options |
| `AppearanceSettingsWidget` | `pref/settings/appearance_settings_widget.py` | 4 | Theme and visual settings |
| `GeneralSettingsWidget` | `pref/settings/general_settings_widget.py` | 4 | General application settings |
| `NetworkSettingsWidget` | `pref/settings/network_settings_widget.py` | 4 | Network configuration options |
| `HistorySettingsWidget` | `pref/settings/history_settings_widget.py` | 6 | Translation history configuration |

### 2.2 Support Components

These components enhance the functionality of the preferences system:

| Class Name | Original Path | Usage Count | Purpose |
|------------|---------------|-------------|---------|
| `ReplacementsDialog` | `pref/repl/replacement_gui.py` | 20 | UI for managing text replacements |
| `KeyboardSettingsWidget` | `pref/settings/keyboard_settings_widget.py` | 2 | Enhanced keyboard shortcut editor |

## Phase 3: Advanced Features and Integration

### 3.1 Translation History Components

These components add translation history management:

| Class Name | Original Path | Usage Count | Purpose |
|------------|---------------|-------------|---------|
| `TranslationDB` | `pref/tran_history/translation_db.py` | 20 | Database for translation history |
| `DatabasePORecord` | `pref/tran_history/tran_db_record.py` | 82 | Data model for PO entries with history |
| `TranslationHistoryDialog` | `pref/tran_history/translation_db_gui.py` | 12 | UI for managing translation history |

### 3.2 Integration Components

These components help integrate the preferences system with the main application:

| Class Name | Original Path | Usage Count | Purpose |
|------------|---------------|-------------|---------|
| `VersionedTranslationWidget` | `subcmp/versioned_translation_widget.py` | 29 | Editor for translation versions |
| `TranslationEditorWidget` | `subcmp/translation_edit_widget.py` | 27 | Base editor for translations |
