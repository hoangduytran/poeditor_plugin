# Menu Specification Analysis and Migration Plan

## Specifications Comparison

### Structure Differences:
1. **gvar.MAIN_GUI_ACTION_SPECS**: 4-tuple format `(action_key, label, callback_name, shortcut)`
2. **MAIN_APP_MENU_SPECS**: 5-tuple format `(action_key, label, callback_name, shortcut, context_group)`

### Content Analysis:

#### Actions in MAIN_APP_MENU_SPECS but NOT in gvar.MAIN_GUI_ACTION_SPECS:
- `new` - New file action
- `close_tab` - Close tab action  
- `toggle_sidebar` - Toggle sidebar visibility
- `plugin_manager` - Plugin Manager dialog
- `settings` - Settings dialog (vs `prefs` in gvar)
- `documentation` - Documentation viewer
- `about` - About dialog

#### Actions in gvar.MAIN_GUI_ACTION_SPECS but NOT in MAIN_APP_MENU_SPECS:
- `load_startup` - Load last file at startup
- `prefs` - Preferences (vs `settings` in MAIN_APP_MENU_SPECS)

#### Callback Name Differences:
- **gvar format**: `on_open_file`, `on_save_file`, etc. (standard action names)
- **MAIN_APP format**: `_on_open_file`, `_on_save_file`, etc. (private method names)

#### Context Groups in MAIN_APP_MENU_SPECS:
- `always_enabled`: Actions always available
- `poeditor_tab_enabled`: Actions available when POEditor tab is active
- `any_tab_enabled`: Actions available when any tab is open

## Migration Strategy

### Decision: Use gvar.MAIN_GUI_ACTION_SPECS as Primary
**Rationale**: 
1. MenuManager already uses this specification
2. More comprehensive POEditor-specific actions
3. Established integration with main_actions.py

### Migration Steps:
1. **Add missing actions** from MAIN_APP_MENU_SPECS to gvar.MAIN_GUI_ACTION_SPECS
2. **Add context group information** to gvar specification (extend to 5-tuple)
3. **Update MenuManager** to handle context groups
4. **Remove MAIN_APP_MENU_SPECS** from MainAppWindow
5. **Update action handlers** to match unified specification

## Context Group Mapping Strategy

### MenuManager Context → Action Context Mapping:
- `ALWAYS_ENABLED` → `always_enabled`
- `POEDITOR_TAB_ENABLED` → `poeditor_tab_enabled` 
- `ANY_TAB_ENABLED` → `any_tab_enabled`
- `FILE_OPENED` → `poeditor_tab_enabled` (merged for simplicity)
- `HAS_SELECTION` → `poeditor_tab_enabled` (context-dependent)
- `HAS_UNDO`/`HAS_REDO` → `poeditor_tab_enabled` (context-dependent)
- `HAS_CLIPBOARD` → `poeditor_tab_enabled` (context-dependent)

### Action-Level Context Assignment:
- **File operations**: `open`, `new` → `always_enabled`
- **Save operations**: `save`, `saveas` → `poeditor_tab_enabled`
- **Edit operations**: `copy`, `paste`, `undo`, `redo` → `poeditor_tab_enabled`
- **Navigation**: All `goto_*` actions → `poeditor_tab_enabled`
- **View operations**: `toggle_sidebar`, `toggle_minimalistic` → `always_enabled`
- **Tools**: `plugin_manager`, `settings` → `always_enabled`
- **Tab operations**: `close_tab` → `any_tab_enabled`

## Implementation Plan

### Step 1: Extend gvar.MAIN_GUI_ACTION_SPECS
Add missing actions and context groups to create unified specification.

### Step 2: Update MenuManager 
Modify MenuManager to handle 5-tuple format with context groups.

### Step 3: Remove MAIN_APP_MENU_SPECS
Clean up MainAppWindow by removing duplicate specification.

### Step 4: Update Action Handlers
Ensure all actions have proper handlers in MainAppWindow.

This approach will create a single, comprehensive menu specification while preserving all functionality from both systems.
