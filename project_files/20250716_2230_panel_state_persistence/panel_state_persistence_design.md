# Sidebar Panel State Persistence Design
**Date**: July 16, 2025  
**Status**: Design Phase  
**Priority**: High  

## Overview

Design a comprehensive state persistence system for all sidebar panels (Explorer, Search, Preferences, Extensions, Account) that remembers their states across application restarts, including directory history, search patterns, and other panel-specific settings.

## Core Requirements

### Explorer Panel State Persistence
- **Directory History**: Remember visited directories with prev/next navigation
- **Current Location**: Restore last viewed directory on startup
- **Recent Locations**: Maintain list of recently accessed directories
- **View Settings**: Remember view mode, hidden files visibility, sorting preferences
- **Selection State**: Restore last selected files/folders (if still exist)

### Search Panel State Persistence
- **Search History**: Remember previous search patterns
- **Search Options**: Persist search scope, case sensitivity, regex options
- **Keyboard Navigation**: Ctrl+Up/Down to navigate search history
- **Recent Searches**: Maintain chronological list of searches

### Other Panels State Persistence
- **Preferences Panel**: Remember last viewed preference category, settings
- **Extensions Panel**: Remember filter states, installation preferences
- **Account Panel**: Remember login states, user preferences

## Technical Architecture

### Settings Structure
```python
# Using QSettings with hierarchical structure
settings = QSettings("POEditor", "PanelStates")

# Explorer settings
settings.setValue("explorer/current_location", "/path/to/directory")
settings.setValue("explorer/history", ["/path1", "/path2", "/path3"])
settings.setValue("explorer/recent_locations", [...])
settings.setValue("explorer/show_hidden", False)
settings.setValue("explorer/sort_by", "name")

# Search settings  
settings.setValue("search/history", ["pattern1", "pattern2"])
settings.setValue("search/case_sensitive", False)
settings.setValue("search/use_regex", False)

# Other panels...
```

### Core Components

#### 1. PanelStateManager (Base Class)
```python
class PanelStateManager:
    """Base class for managing panel state persistence"""
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        self.settings = QSettings("POEditor", "PanelStates")
    
    def save_state(self, state_data: dict) -> None
    def load_state(self) -> dict
    def clear_state(self) -> None
    def get_setting(self, key: str, default=None)
    def set_setting(self, key: str, value) -> None
```

#### 2. ExplorerStateManager
```python
class ExplorerStateManager(PanelStateManager):
    """Manages Explorer panel state persistence"""
    def save_location_history(self, history: List[str]) -> None
    def load_location_history(self) -> List[str]
    def add_recent_location(self, path: str) -> None
    def get_recent_locations(self) -> List[str]
    def save_view_settings(self, settings: dict) -> None
    def load_view_settings(self) -> dict
```

#### 3. SearchStateManager
```python
class SearchStateManager(PanelStateManager):
    """Manages Search panel state persistence"""
    def save_search_history(self, history: List[str]) -> None
    def load_search_history(self) -> List[str]
    def add_search_pattern(self, pattern: str) -> None
    def get_search_pattern_at_index(self, index: int) -> str
    def save_search_options(self, options: dict) -> None
    def load_search_options(self) -> dict
```

### Navigation History Implementation

#### Directory Navigation History
```python
class DirectoryHistory:
    def __init__(self, state_manager: ExplorerStateManager):
        self.state_manager = state_manager
        self.history = []
        self.current_index = -1
        self.max_history = 50
    
    def add_location(self, path: str) -> None
    def can_go_back(self) -> bool
    def can_go_forward(self) -> bool
    def go_back(self) -> Optional[str]
    def go_forward(self) -> Optional[str]
    def save_to_settings(self) -> None
    def load_from_settings(self) -> None
```

#### Search Pattern History
```python
class SearchHistory:
    def __init__(self, state_manager: SearchStateManager):
        self.state_manager = state_manager
        self.patterns = []
        self.current_index = -1
        self.max_patterns = 50
    
    def add_pattern(self, pattern: str) -> None
    def get_previous_pattern(self) -> Optional[str]
    def get_next_pattern(self) -> Optional[str]
    def handle_key_navigation(self, key: Qt.Key) -> Optional[str]
    def save_to_settings(self) -> None
    def load_from_settings(self) -> None
```

## Implementation Plan

### Phase 1: Core State Management Infrastructure
1. **Create PanelStateManager base class**
   - Implement QSettings integration
   - Add common state management methods
   - Create settings hierarchy structure

2. **Implement panel-specific state managers**
   - ExplorerStateManager for directory/file operations
   - SearchStateManager for search patterns and options
   - Create state managers for other panels

### Phase 2: Explorer Panel Enhancement
1. **Directory History System**
   - Implement DirectoryHistory class
   - Add prev/next navigation buttons/shortcuts
   - Integrate with existing explorer navigation

2. **State Persistence Integration**
   - Save current location on directory changes
   - Restore last location on panel activation
   - Maintain recent locations list

3. **Enhanced Settings**
   - View preferences (hidden files, sorting)
   - Selection state management
   - Custom explorer preferences

### Phase 3: Search Panel Enhancement
1. **Search History System**
   - Implement SearchHistory class
   - Add Ctrl+Up/Down keyboard navigation
   - Visual indicators for history navigation

2. **Search State Persistence**
   - Save search patterns and options
   - Restore last search state
   - Maintain search results context

### Phase 4: Other Panels Integration
1. **Preferences Panel State**
   - Remember last viewed category
   - Save panel-specific settings
   - User preference persistence

2. **Extensions Panel State**
   - Filter states and view modes
   - Installation preferences
   - Extension management settings

3. **Account Panel State**
   - Login states and user data
   - Account-specific preferences
   - Session management

## User Experience Features

### Explorer Panel
- **Seamless Navigation**: Pick up exactly where user left off
- **Breadcrumb History**: Visual navigation through recent paths
- **Quick Access**: Recently accessed directories in context menu
- **Keyboard Shortcuts**: Alt+Left/Right for history navigation

### Search Panel  
- **Smart Completion**: Auto-complete from search history
- **Pattern Cycling**: Ctrl+Up/Down to cycle through previous searches
- **Context Preservation**: Remember search scope and options
- **Quick Filters**: One-click access to recent search patterns

### All Panels
- **Instant Restoration**: No loading delays on panel switches
- **Persistent State**: Settings survive application restarts
- **User Control**: Options to clear history/reset states
- **Memory Management**: Automatic cleanup of old history entries

## Data Management

### Settings Organization
```
POEditor/PanelStates/
├── explorer/
│   ├── current_location
│   ├── history_list
│   ├── recent_locations
│   ├── view_settings/
│   └── selection_state/
├── search/
│   ├── pattern_history
│   ├── search_options
│   └── recent_patterns
├── preferences/
│   ├── last_category
│   └── panel_settings
├── extensions/
│   ├── filter_states
│   └── view_preferences
└── account/
    ├── login_state
    └── user_preferences
```

### Performance Considerations
- **Lazy Loading**: Load state only when panels are activated
- **Incremental Saves**: Save state on meaningful changes, not every keystroke
- **Size Limits**: Maximum history entries to prevent unbounded growth
- **Cleanup**: Automatic removal of invalid/old entries

## Security & Privacy
- **Sensitive Data**: Encrypt login credentials and sensitive settings
- **Path Validation**: Verify directory paths still exist before restoration
- **User Control**: Options to disable state persistence per panel
- **Data Export**: Allow users to backup/restore panel states

## Testing Strategy
- **State Persistence Tests**: Verify save/restore functionality
- **History Navigation Tests**: Test prev/next and keyboard navigation
- **Edge Cases**: Handle invalid paths, corrupted settings
- **Performance Tests**: Ensure fast state loading/saving
- **User Workflow Tests**: End-to-end panel usage scenarios

## Implementation Files
- `services/panel_state_service.py` - Core state management
- `panels/state_managers/` - Panel-specific state managers
- `panels/history/` - History management classes
- Enhanced existing panel files with state integration

## Success Criteria
1. ✅ All panels remember their state across restarts
2. ✅ Explorer navigation history works with prev/next
3. ✅ Search history accessible via Ctrl+Up/Down
4. ✅ Settings persist correctly without data loss
5. ✅ Performance impact is minimal
6. ✅ User experience is seamless and intuitive
