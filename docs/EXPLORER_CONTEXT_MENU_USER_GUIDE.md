# Explorer User Guide

## Overview

The POEditor Plugin Explorer provides a comprehensive file management experience with intuitive navigation, filtering, and file operations. This guide covers all user-facing features of the explorer interface.

## Interface Components

### Navigation Bar
- **Up Button (↑ Up)**: Navigate to the parent directory
- **Path Display**: Shows the current directory path

### Filter Bar
- **Search/Filter Input**: Type to filter files by name in real-time
- **Clear Button (✕)**: Remove filter and show all files
- **Filter Mode Menu**: Right-click to switch between filter modes

### File View
- **Tree Structure**: Hierarchical display of directories and files
- **Directory-First Sorting**: Folders always appear before files
- **Double-Click Navigation**: Double-click folders to enter, files to open
- **Column Layout**: Multiple sortable columns:
  - **Name**: File/folder names (default sort, ascending)
  - **Size**: File size in human-readable format
  - **Type**: File type based on extension
  - **Modified Date**: Last modification date in localized format
- **Column Sorting**: Click column headers to sort by different criteria

## Filter and Search Features

### Basic Filtering

1. **Type to Filter**:
   - Start typing in the filter box to narrow down visible files
   - Filtering is case-insensitive
   - Uses partial string matching

2. **Clear Filter**:
   - Click the clear button (✕) to instantly remove the filter
   - Button appears only when filter text is present
   - Restores full file listing immediately

3. **Filter Examples**:
   - Type "test" → Shows files containing "test"
   - Type ".py" → Shows Python files
   - Type "README" → Shows readme files

### Filter Modes

Right-click the filter bar to access different modes:

- **Filter Files** (Default): Show/hide files based on name patterns
- **Search Text In Files**: Search within file contents (future feature)

**Advanced Options** (available when enabled):
- **Case Sensitive**: Match exact letter case
- **Whole Word**: Match complete words only
- **Regular Expression**: Use regex patterns for complex searches

### Search and Filter History

- **History Recall**: Use Ctrl+Up/Down to cycle through previous searches
- **Separate History**: Filter and search histories are stored separately
- **Persistent Storage**: History is maintained across application sessions

### Visual Feedback

- Clear button automatically enables when typing begins
- Button disables when filter is empty
- Tooltip provides helpful guidance
- Directory-first sorting maintained during filtering

## Column Management and Sorting

### Available Columns

The explorer provides multiple sortable columns for detailed file information:

1. **Name Column**:
   - Shows file and folder names with icons
   - Default sort column (ascending order)
   - Supports alphabetical sorting

2. **Size Column**:
   - Displays file sizes in human-readable format (KB, MB, GB)
   - Folders show their total size when calculated
   - Useful for identifying large files

3. **Type Column**:
   - Shows file type based on extension
   - Groups similar file types together when sorted
   - Helpful for finding specific file formats

4. **Modified Date Column**:
   - Displays last modification date and time
   - Uses localized date format
   - Enables chronological file organization

### Sorting Features

- **Click Column Headers**: Click any column header to sort by that column
- **Sort Direction**: Click again to toggle between ascending/descending
- **Visual Indicators**: Column headers show sort direction with arrows
- **Persistent Sorting**: Last sort preference is remembered between sessions

## File Operations

### Context Menu

Right-click on files or folders to access operations:

#### File Operations
- **Copy** (Ctrl+C): Copy selected items to clipboard
- **Cut** (Ctrl+X): Cut selected items for moving
- **Paste** (Ctrl+V): Paste clipboard items to current location
- **Delete** (Delete): Remove selected items
- **Rename** (F2): Rename the selected item
- **Duplicate**: Create a copy with incremented name

#### Folder Operations
- **New File** (Ctrl+N): Create a new file in current directory
- **New Folder** (Ctrl+Shift+N): Create a new folder
- **Properties**: View item properties
- **Open in Terminal**: Open terminal at current location

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+C | Copy selected items |
| Ctrl+X | Cut selected items |
| Ctrl+V | Paste items |
| Delete | Delete selected items |
| F2 | Rename selected item |
| Ctrl+N | New file |
| Ctrl+Shift+N | New folder |
| F5 | Refresh view |

### Advanced Keyboard Navigation

#### Quick Navigation
- **Arrow Keys**: Navigate through the file tree
- **Home/End**: Jump to first/last item in current directory
- **Page Up/Page Down**: Navigate by page in large directories
- **Enter**: Open selected file or enter selected directory
- **Backspace**: Navigate to parent directory
- **Space**: Select/deselect items for multi-selection

#### Search and Filter Shortcuts
- **Ctrl+F**: Focus the filter box for quick searching
- **Esc**: Clear current filter and return focus to file view
- **Tab**: Cycle between filter box and file view
- **Shift+Tab**: Reverse cycle between interface elements
- **Ctrl+Up/Down**: Navigate through search/filter history

#### Selection Operations
- **Ctrl+A**: Select all visible items
- **Ctrl+Click**: Add/remove individual items from selection
- **Shift+Click**: Select range of items
- **Shift+Arrow Keys**: Extend selection in direction of arrow

#### Power User Features
- **Ctrl+D**: Duplicate selected items quickly
- **Alt+Enter**: Show properties for selected items
- **Ctrl+Shift+C**: Copy full path of selected items to clipboard
- **F6**: Switch focus between panels in multi-panel view

### Drag and Drop

- Drag files/folders to move them between directories
- Hold Ctrl while dragging to copy instead of move
- Drop targets are highlighted during drag operations

## Settings and Persistence

### Automatic Settings
- Last visited directory is remembered between sessions
- Filter state is reset when changing directories
- Window size and layout preferences are saved
- Column widths and sort order are preserved
- Search and filter history is maintained separately

### Manual Configuration
Access preferences through the main application settings to configure:
- Default file view options
- Column visibility and order
- Search and filter behavior
- Advanced search options (case sensitivity, regex, etc.)
- Keyboard shortcut customization
- Theme and appearance settings

## Tips and Best Practices

### Efficient Navigation
1. Use the filter to quickly find files in large directories
2. Double-click folders for fast navigation
3. Use the up button to navigate to parent directories
4. Remember that directories always appear first for easy browsing

### Filter Tips
1. Use the clear button for instant filter removal
2. Combine multiple keywords for more specific filtering
3. File extensions work well as filter terms
4. Filtering preserves directory structure and sorting
5. Use Ctrl+Up/Down to recall previous searches
6. Enable regex mode for complex pattern matching
7. Toggle case sensitivity for exact matches

### Advanced Search Tips
1. Use regular expressions for complex pattern matching
2. Enable "Whole Word" to avoid partial matches
3. Case sensitivity helps when working with code files
4. Search history is kept separate from filter history
5. Right-click the search bar to access advanced options

### Keyboard Efficiency
1. Learn the keyboard shortcuts for common operations
2. Use F5 to refresh if files don't appear immediately
3. F2 for quick renaming is faster than right-click menu
4. Ctrl combinations work consistently across operations

## Troubleshooting

### Common Issues

**Filter not working**:
- Ensure you're typing in the filter box, not elsewhere
- Check that the clear button appears when typing
- Try clearing the filter and starting fresh

**Files not appearing**:
- Press F5 to refresh the view
- Check if a filter is applied (clear button visible)
- Verify you're in the correct directory

**Context menu not showing**:
- Ensure you're right-clicking directly on files/folders
- Try clicking once to select, then right-clicking
- Check that the explorer has focus

**Navigation issues**:
- Use the up button if double-click navigation fails
- Check the path display to confirm current location
- Restart the application if navigation becomes unresponsive