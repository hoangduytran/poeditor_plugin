# Enhanced Explorer Changelog

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
