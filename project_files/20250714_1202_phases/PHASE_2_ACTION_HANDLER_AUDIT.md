# Phase 2: Action Handler Audit Results

## Current Handler Status in MainAppWindow._handle_menu_action()

### ✅ IMPLEMENTED Handlers:
1. **open** → `_on_open_file()` 
2. **save** → `_on_save_file()`
3. **saveas** → `_on_save_as_file()`
4. **exit** → `self.close()`
5. **toggle_sidebar** → `_on_toggle_sidebar()`
6. **plugin_manager** → `_on_show_plugin_manager()`
7. **about** → `_on_about()`
8. **toggle_minimalistic** → `self.toggle_minimalistic_mode()`

### ❌ MISSING Handlers in MainAppWindow:

#### App-Level Actions (should be in MainAppWindow):
1. **new** → `on_new_file` (needs `_on_new_file()`)
2. **load_startup** → `on_load_file_startup` (needs `_on_load_startup()`)
3. **close_tab** → `on_close_tab` (needs `_on_close_tab()`)
4. **prefs** → `on_open_preferences` (needs `_on_open_preferences()`)
5. **toggle_taskbar** → `toggle_taskbar` (needs `_on_toggle_taskbar()`)
6. **settings** → `on_show_settings` (needs `_on_show_settings()`)
7. **documentation** → `on_show_documentation` (needs `_on_show_documentation()`)

#### POEditor Tab Actions (delegated to active tab):
- **copy, paste, undo, redo** → Already delegated via `_delegate_to_active_tab()`
- **goto_*** → Already delegated via `_delegate_to_active_tab()`
- **show_issues, view_issues_only** → Already delegated
- **find_replace_***, **sort_*** → Already delegated

## Handler Implementation Strategy

### Phase 2B Tasks:

1. **Implement App-Level Handlers**: Add missing methods to MainAppWindow
2. **Test Delegation System**: Ensure POEditor actions properly reach active tab
3. **Connect with main_actions.py**: Use existing action implementations where available
4. **Error Handling**: Ensure graceful fallback for missing implementations

## Delegation Flow Analysis

```
Menu Action → MenuManager → MainAppWindow._handle_menu_action() → 
    ├─ App-level: Handle directly
    └─ POEditor-specific: _delegate_to_active_tab() → POEditorTab
```

### Key Files:
- **main_actions.py**: Contains `get_actions()` with implementations
- **actions_factory.py**: Contains specific action implementations
- **MainAppWindow**: Needs app-level action handlers
- **POEditorTab**: Should receive delegated POEditor actions

## Next Steps:
1. Implement missing MainAppWindow handlers
2. Verify delegation mechanism works
3. Test file opening functionality
4. Check context-sensitive enable/disable
