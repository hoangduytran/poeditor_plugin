# Preferences Panel Consolidation Design

**Date**: August 2, 2025  
**Component**: Unified Preferences System  
**Status**: Design Phase  
**Priority**: HIGH

## 1. Overview
Consolidate all legacy preference panels into a unified, plugin-aware system that maintains the tabular arrangement users expect while leveraging the new QSettings architecture.

## 2. Legacy Preferences Audit

### Existing PANEL_DESIGN Documents Status:
- ✅ `PANEL_DESIGN_Editor_Settings.md` - Basic editor configuration
- ✅ `PANEL_DESIGN_Fonts.md` - Font selection and sizing
- ✅ `PANEL_DESIGN_Keyboard.md` - Keyboard shortcuts and hotkeys
- ✅ `PANEL_DESIGN_Text_Replacements.md` - Text replacement rules
- ✅ `PANEL_DESIGN_Translation_History.md` - History management
- ✅ `PANEL_DESIGN_PO_Settings.md` - PO file specific settings

### Legacy Code Analysis Required:
- `old_codes/preferences/` - Original preference implementations
- `old_codes/ui/preference_panels/` - UI panel implementations
- `old_codes/settings/` - Settings storage mechanisms

## 3. Unified Preferences Architecture

### 3.1 Tabular Layout Design
```
┌─────────────────────────────────────────────────────────┐
│ Preferences                                         × │
├─────────────┬───────────────────────────────────────────┤
│ Categories  │ Settings Panel                            │
│             │                                           │
│ □ Editor    │ ┌─────────────────────────────────────┐  │
│ □ Fonts     │ │                                     │  │
│ □ Keyboard  │ │     Active Settings Panel           │  │
│ □ Text Repl │ │                                     │  │
│ □ History   │ │                                     │  │
│ □ PO Files  │ │                                     │  │
│ □ Services  │ │                                     │  │
│             │ └─────────────────────────────────────┘  │
├─────────────┴───────────────────────────────────────────┤
│                 [Cancel]  [Apply]  [OK]                 │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Plugin Registration Pattern
```python
class PreferencesPanelPlugin(PluginBase):
    def register_preference_panels(self) -> List[PreferencePanel]:
        return [
            EditorSettingsPanel(),
            FontSettingsPanel(),
            KeyboardSettingsPanel(),
            # ... other panels
        ]
```

## 4. Implementation Strategy

### 4.1 QSettings Migration
- Map legacy preference storage to QSettings keys
- Implement automatic migration on first run
- Provide rollback mechanism for failed migrations

### 4.2 Panel Validation
- Implement input validation per panel
- Cross-panel dependency checking
- Real-time preview for applicable settings

### 4.3 Plugin Integration Points
- Allow plugins to register additional preference panels
- Provide settings change notification system
- Enable plugin-specific settings sections

## 5. Technical Implementation

### 5.1 Core Classes
```python
class UnifiedPreferencesDialog:
    """Main preferences dialog coordinating all panels"""
    
class PreferencePanelRegistry:
    """Registry for all preference panels"""
    
class SettingsMigrator:
    """Handles migration from legacy settings"""
    
class PreferencePanelValidator:
    """Validates settings across panels"""
```

### 5.2 Settings Schema
```yaml
preferences:
  editor:
    auto_save: bool
    line_numbers: bool
    word_wrap: bool
  fonts:
    family: str
    size: int
    antialiasing: bool
  keyboard:
    shortcuts: dict
  text_replacements:
    rules: list
  history:
    max_entries: int
    auto_cleanup: bool
  po_files:
    backup_enabled: bool
    validation_level: str
```

## 6. Migration Strategy

### 6.1 Phase 1: Framework Setup
- Implement base preferences dialog
- Create panel registration system
- Set up QSettings infrastructure

### 6.2 Phase 2: Panel Migration
- Migrate each legacy panel individually
- Implement settings validation
- Add real-time preview capabilities

### 6.3 Phase 3: Integration Testing
- Test cross-panel dependencies
- Validate migration from legacy settings
- Performance testing with large preference sets

## 7. Success Criteria
- All legacy preferences accessible through new system
- Settings migration successful for 100% of test cases
- Performance equal or better than legacy system
- Plugin extensibility demonstrated
- User experience maintains familiarity

## 8. Next Steps
1. Begin legacy code analysis in `old_codes/preferences/`
2. Implement base preferences framework
3. Create settings migration utilities
4. Design panel validation system

## 9. Dependencies
- QSettings infrastructure (existing)
- Plugin registration system (existing)
- UI framework components (existing)

## 10. Risks and Mitigation
- **Data Loss**: Implement robust backup before migration
- **Performance**: Profile each panel for responsiveness
- **Compatibility**: Maintain API compatibility for plugins
