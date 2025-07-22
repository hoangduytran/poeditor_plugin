# Phase 3: Context System Integration & Plugin Compatibility

## Objective
Implement and test context-sensitive menu system with dynamic enable/disable states, POEditor tab integration, and plugin compatibility.

## Current Status: Phase 2 ✅ COMPLETE

### What We Have:
- ✅ Complete action handler coverage (35+ handlers)
- ✅ Smart action delegation system (MainAppWindow ↔ POEditor tabs)
- ✅ MenuManager with 5-tuple context support
- ✅ Application starts without errors
- ✅ All menus functional

### What We Need: Context-Sensitive Behavior

Currently menus are **static** - all items enabled all the time. Phase 3 makes them **dynamic** based on application state.

## Phase 3 Tasks

### Task 3A: Context State System
**Goal**: Implement centralized context tracking

#### 3A.1: Context State Manager
```python
# Add to MainAppWindow
class ContextState:
    """Tracks application context for menu enable/disable."""
    def __init__(self):
        self.has_active_tab = False
        self.tab_type = None  # 'POEditor', 'Explorer', etc.
        self.has_poeditor_data = False
        self.has_selection = False
        self.is_modified = False
        # ... more context flags

def _update_context_state(self):
    """Update context state and refresh menus."""
    active_tab = self.tab_manager.get_active_tab()
    
    # Update context
    self.context.has_active_tab = active_tab is not None
    self.context.tab_type = type(active_tab).__name__ if active_tab else None
    # ... update other flags
    
    # Refresh menu states
    self.menu_manager.update_context_state(self.context)
```

#### 3A.2: Context Update Triggers
- Tab activation/deactivation
- File load/save operations  
- Selection changes in POEditor
- Data modification states

### Task 3B: MenuManager Context Integration
**Goal**: Implement context-sensitive menu enable/disable

#### 3B.1: Context Group Mapping
```python
# In MenuManager
CONTEXT_GROUPS = {
    'file_ops': ['has_active_tab'],
    'edit_ops': ['has_active_tab', 'has_poeditor_data'],
    'navigation': ['has_poeditor_data'],
    'selection': ['has_selection'],
    'modified': ['is_modified']
}

def update_context_state(self, context_state):
    """Update menu enable/disable based on context."""
    for action_name, action in self.actions.items():
        context_group = self._get_action_context_group(action_name)
        enabled = self._should_enable_action(context_group, context_state)
        action.setEnabled(enabled)
```

#### 3B.2: Smart Enable/Disable Logic
- **File Operations**: Enabled when tabs exist
- **Edit Operations**: Enabled for POEditor tabs with data
- **Navigation**: Enabled for POEditor with entries
- **Selection Operations**: Enabled when text/entries selected

### Task 3C: POEditor Tab Integration
**Goal**: Ensure POEditor tabs properly integrate with context system

#### 3C.1: POEditor Context Signals
```python
# POEditor tab should emit context signals
class POEditorTab:
    def __init__(self):
        # Context signals
        self.data_loaded = Signal()
        self.selection_changed = Signal(bool)  # has_selection
        self.modification_changed = Signal(bool)  # is_modified
    
    def _emit_context_update(self):
        """Emit context update to MainAppWindow."""
        self.parent().update_context_from_tab(self)
```

#### 3C.2: Tab Context Integration
- Connect POEditor signals to MainAppWindow context updates
- Handle tab switching context changes
- Manage tab-specific context states

### Task 3D: Plugin Menu Integration
**Goal**: Ensure plugins properly integrate with context system

#### 3D.1: Plugin Context Compatibility
```python
# Plugin menu items should respect context
def register_plugin_menu(self, plugin_name, menu_items):
    """Register plugin menus with context support."""
    for item in menu_items:
        # Convert plugin 4-tuple to 5-tuple with context
        if len(item) == 4:
            name, shortcut, callback, tooltip = item
            context_group = self._infer_plugin_context(plugin_name, name)
            item = (name, shortcut, callback, tooltip, context_group)
        
        self._add_menu_item_with_context(item)
```

#### 3D.2: Plugin Action Context
- POEditor plugin actions: `'edit_ops'` context
- Explorer plugin actions: `'file_ops'` context  
- Settings plugin actions: Always enabled

## Implementation Strategy

### Step 1: Context State Foundation
1. Add `ContextState` class to MainAppWindow
2. Implement `_update_context_state()` method
3. Add context update triggers (tab changes, etc.)

### Step 2: MenuManager Context Support  
1. Enhance MenuManager with context group mapping
2. Implement `update_context_state()` method
3. Add action enable/disable logic

### Step 3: POEditor Integration
1. Review POEditor tab implementation
2. Add context signal emissions
3. Connect signals to MainAppWindow

### Step 4: Plugin System Testing
1. Test plugin menu registration
2. Verify context compatibility
3. Test POEditor plugin specifically

### Step 5: Integration Testing
1. Test tab switching scenarios
2. Verify menu states update correctly
3. Test edge cases (no tabs, multiple tabs, etc.)

## Success Criteria

### Functional Requirements:
- [ ] Menus enable/disable based on application state
- [ ] Context updates when switching tabs
- [ ] POEditor-specific actions only enabled for POEditor tabs
- [ ] Plugin menus respect context system

### Technical Requirements:
- [ ] Clean context state management
- [ ] Efficient menu update performance
- [ ] No regressions in existing functionality
- [ ] Plugin compatibility maintained

### User Experience Requirements:
- [ ] Intuitive menu behavior (disabled items are obvious)
- [ ] No confusing enabled items that don't work
- [ ] Smooth context transitions
- [ ] Consistent behavior across all menu types

## Context Groups Defined

Based on the 5-tuple format in `gvar.MAIN_GUI_ACTION_SPECS`:

```python
CONTEXT_GROUPS = {
    'always': [],                    # Always enabled (Help, About, Exit)
    'file_ops': ['has_tabs'],        # File operations  
    'edit_ops': ['has_poeditor'],    # Edit operations
    'navigation': ['has_poeditor'],  # Navigation actions
    'issues': ['has_poeditor'],      # Issue viewing
    'search': ['has_poeditor'],      # Find/Replace
    'sorting': ['has_poeditor'],     # Sorting operations
    'view_ops': ['has_app'],         # View toggles
    'tools': ['has_app']             # Tools and plugins
}
```

## Testing Plan

### Unit Tests:
- Context state updates
- Menu enable/disable logic
- Plugin menu integration

### Integration Tests:
- Tab switching scenarios
- File load/save context changes
- Plugin registration and context

### Manual Tests:
- User workflow testing
- Edge case scenarios
- Performance validation

## Risk Mitigation

### Potential Issues:
1. **Performance**: Frequent menu updates could slow UI
   - **Mitigation**: Debounce context updates, cache enabled states

2. **Context Complexity**: Too many context states could be confusing
   - **Mitigation**: Keep context groups simple and intuitive

3. **Plugin Compatibility**: Existing plugins might break
   - **Mitigation**: Backward compatibility with 4-tuple format

4. **POEditor Integration**: Might require POEditor tab modifications
   - **Mitigation**: Incremental approach, fallback to polling if needed

## Expected Timeline

- **Task 3A** (Context State): ~1-2 hours implementation
- **Task 3B** (MenuManager): ~2-3 hours implementation  
- **Task 3C** (POEditor Integration): ~1-2 hours (depends on existing code)
- **Task 3D** (Plugin Testing): ~1 hour testing
- **Integration Testing**: ~1-2 hours
- **Total Estimated**: 6-10 hours

## Next Phase Preview

**Phase 4: Final Testing & Validation**
- Comprehensive manual testing
- Real PO file workflow testing
- Performance optimization
- Documentation updates
- Production readiness validation

Phase 3 will transform the static menu system into a **dynamic, context-aware interface** that adapts to user workflow and application state.
