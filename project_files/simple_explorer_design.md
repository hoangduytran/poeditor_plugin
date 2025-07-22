# Simple Explorer Design - Clean and Focused

## Overview
A streamlined file explorer focusing on essential functionality without complex proxy chains or fancy features. Emphasizes performance, simplicity, and user experience.

## Core Requirements

### Column Layout
- **Name** (sortable, default ascending)
- **Size** (sortable, human-readable format)
- **Type** (sortable, file extension based)
- **Modified Date** (sortable, localized format)

### Search/Filter System
- **Single text input box** for both filtering and searching
- **Right-click context menu** with options:
  - Filter Files (boolean, True by default)
  - Search Text In Files (boolean, False by default)
  - Advanced options (when enabled):
    - Case Sensitive (checkbox)
    - Whole Word (checkbox)
    - Regular Expression (checkbox)

### Navigation & History
- **Settings persistence** for last location
- **Search/filter history** stored separately
- **Keyboard navigation**: Ctrl+Up/Down for history recall based on current mode

## Design Principles

### Simplicity First
- No proxy models (direct QFileSystemModel)
- Minimal UI complexity
- Clear visual hierarchy
- Fast startup and response

### User Experience
- Intuitive right-click context
- Keyboard shortcuts for power users
- Visual feedback for current mode
- Persistent settings across sessions

## Architecture

### Components
1. **SimpleExplorerWidget** - Main container
2. **SimpleSearchBar** - Text input with mode indicator
3. **SimpleFileView** - QTreeView with direct model
4. **SimpleSettingsManager** - Lightweight persistence
5. **SimpleHistoryManager** - Separate filter/search history

### Data Flow
```
User Input → Search Bar → Mode Detection → File Model Filter → View Update
                     ↓
                Settings → History Storage → Keyboard Recall
```

### File Structure
```
panels/
  simple_explorer/
    __init__.py
    simple_explorer_widget.py    # Main widget
    simple_search_bar.py         # Search/filter input
    simple_file_view.py          # Tree view component
    simple_settings_manager.py   # Settings persistence
    simple_history_manager.py    # History management
```

## Implementation Details

### Search Bar Features
- Clean text input with placeholder
- Mode indicator (Filter/Search icon)
- Right-click context menu
- History dropdown on Ctrl+Up/Down

### File View Features
- Standard QTreeView with QFileSystemModel
- Default sorting by name (ascending)
- Click headers to sort by column
- Standard file icons and formatting

### Context Menu Options
```
┌─────────────────────────────┐
│ ☑ Filter Files             │
│ ☐ Search Text In Files     │
│ ─────────────────────────── │
│ ☐ Case Sensitive           │
│ ☐ Whole Word               │
│ ☐ Regular Expression       │
└─────────────────────────────┘
```

### Settings Storage
```json
{
  "last_location": "/path/to/folder",
  "filter_history": ["*.py", "README", "test"],
  "search_history": ["TODO", "function", "class"],
  "search_options": {
    "filter_files": true,
    "search_text_in_files": false,
    "case_sensitive": false,
    "whole_word": false,
    "regular_expression": false
  }
}
```

## Key Benefits

### Performance
- Direct model connection (no proxy overhead)
- Efficient filtering using QFileSystemModel
- Minimal memory footprint
- Fast search operations

### Maintainability
- Simple, focused codebase
- Clear separation of concerns
- Easy to test and debug
- Minimal dependencies

### User Experience
- Familiar file explorer feel
- Quick search/filter switching
- Persistent preferences
- Keyboard efficiency

## Future Enhancements (Optional)
- Custom file type icons
- Column width persistence
- Drag & drop support
- Folder bookmarks
- Recent locations menu

## Testing Strategy
1. **Unit Tests** - Individual components
2. **GUI Demo** - Visual testing application
3. **Performance Tests** - Large directory handling
4. **User Testing** - Workflow validation

This design prioritizes simplicity and performance while providing essential file explorer functionality with smart search/filter capabilities.
