# Explorer Changelog

## Version 3.1.0 - July 31, 2025

### Added
- **Clear Button for Filter**: Added a clear button (✕) at the end of the filter box in SimpleExplorerWidget
  - Button automatically enables/disables based on filter text presence
  - Single-click to clear filter and restore all files
  - Includes helpful tooltip: "Clear filter and restore all files"
  - Integrates seamlessly with existing filter functionality

### Improved
- Enhanced filter user experience with visual clear action
- Improved state management for filter operations

### Technical Details
- Added `clear_button` QPushButton component to SimpleExplorerWidget
- Implemented `_on_clear_button_clicked()` method for filter clearing
- Updated `_on_search_text_changed()` to manage button enabled state
- Modified UI layout to include clear button in search layout

## Previous Versions

### Version 3.0.0 - Phase 3 Implementation
- Core SimpleExplorerWidget implementation
- Directory-first sorting with DirectoryFirstProxyModel
- Search/filter functionality with SimpleSearchBar
- Context menu integration with ExplorerContextMenu
- Settings persistence with ExplorerSettings
- File operations support