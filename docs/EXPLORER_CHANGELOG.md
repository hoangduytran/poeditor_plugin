# Enhanced Explorer Changelog

## Version 3.0.0 - July 28, 2025

### Phase 4: Accessibility & Advanced Navigation

**Major New Features:**
- **Accessibility Support**: Full screen reader integration with ARIA attributes
- **Enhanced Keyboard Navigation**: Advanced keyboard shortcuts and navigation patterns
- **Theme Integration**: CSS-based styling with theme manager integration
- **Performance Optimizations**: Improved icon loading and menu creation

**Accessibility Features:**
- Added MenuAccessibilityManager for screen reader support
- Implemented ARIA labels and descriptions for all menu items
- Added keyboard-only navigation with arrow keys and first-letter selection
- Screen reader announcements for file operations (cut, copy, paste, delete)
- Enhanced focus management with proper focus restoration
- Accessibility-compliant color contrast and visual indicators

**Enhanced Keyboard Navigation:**
- Added MenuKeyboardNavigator for advanced keyboard event handling
- Implemented first-letter navigation (type 'c' to jump to "Copy", etc.)
- Enhanced arrow key navigation with proper wraparound
- Added Enter/Space key activation for menu items
- Improved keyboard shortcut display and handling
- Context-sensitive keyboard shortcuts (F2 for rename, Delete for delete, etc.)

**Theme Integration:**
- CSS-based menu styling that adapts to application themes
- Theme-aware icon loading with graceful fallback
- Consistent visual styling across all menu items
- Support for custom themes through CSS selectors

**Performance Optimizations:**
- Optimized icon loading with cached empty icons for missing SVG files
- Improved menu creation performance with lazy loading
- Enhanced memory management for menu lifecycle
- Reduced file system access through intelligent caching

**Integration Improvements:**
- Full integration with SimpleExplorerWidget for right-click operations
- Enhanced signal connections between context menu and file view
- Improved selection handling for multiple items
- Better error handling and user feedback

**Documentation:**
- Updated RST documentation for accessibility features
- Added keyboard navigation usage guide
- Updated developer documentation with Phase 4 architecture
- Comprehensive test documentation with 27+ test cases

## Version 2.0.0 - July 28, 2025

### Phase 3: Drag & Drop Integration

**New Features:**
- Added comprehensive drag and drop support for files and directories
- Implemented DragDropService for handling drag and drop operations
- Added visual feedback for drag operations and drop targets
- Support for dragging files to external applications
- Support for receiving files from external applications
- Added copy/move behavior based on modifier keys (Ctrl/Cmd for copy)
- Directory highlighting when dragging over potential drop targets

**Enhancements:**
- Optimized MIME data handling for better compatibility
- Added file URL support for cross-application drag and drop
- Improved path resolution for drop targets

**Documentation:**
- Added drag and drop usage guide in user documentation
- Added DragDropService API documentation
- Technical design documentation for drag and drop implementation

## Version 1.5.0 - July 25, 2025

### Phase 2: Context Menu Implementation

**New Features:**
- Added context menu support for files and directories
- Implemented ExplorerContextMenu component
- Added file operation menu items (copy, cut, paste, delete, rename)
- Implemented context-aware menus based on selection type
- Added "New File" and "New Folder" menu items
- Added "Properties" and "Open With" menu items
- Added support for multiple file selection operations

**Enhancements:**
- Integrated with FileOperationsService for file management
- Added UndoRedoManager for operation history
- Added FileNumberingService for naming conflict resolution
- Improved selection handling with QItemSelectionModel

**Bug Fixes:**
- Fixed issue with selection model flags
- Fixed issue with menu positioning
- Fixed deletion confirmation dialog
- Addressed file path encoding issues

**Documentation:**
- Added context menu usage guide
- Added API documentation for new components
- Added technical design documentation

## Version 1.0.0 - July 20, 2025

### Initial Explorer Implementation

**Features:**
- Basic file and directory browsing
- File and directory navigation
- Search/filter functionality
- Simple file operations
- Persistent settings for recent locations

**Components:**
- SimpleFileView for file display
- SimpleSearchBar for text filtering
- Directory navigation controls
- Basic file system model integration
