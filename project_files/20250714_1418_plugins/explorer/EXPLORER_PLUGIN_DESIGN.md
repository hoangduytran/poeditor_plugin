# Explorer Plugin Design

## Overview
The Explorer plugin provides file system navigation and workspace management for the POEditor application. It implements a VS Code-like file explorer with support for PO file detection, project management, and integration with the tab system.

## Architecture

### Core Components

#### 1. ExplorerPlugin (plugin.py)
**Purpose:** Main plugin entry point and registration

**Key Features:**
- Plugin registration with sidebar panel
- Command registration for file operations
- Event handling for file system changes
- Integration with core services

**Interface:**
```python
def register(api: PluginAPI) -> None
def unregister(api: PluginAPI) -> None
```

#### 2. ExplorerPanel (explorer_panel.py)
**Purpose:** Main UI panel displayed in the sidebar

**Key Features:**
- File tree view with workspace root
- Toolbar with navigation and actions
- Status bar with file counts
- Context menu integration
- Drag and drop support

**Interface:**
```python
class ExplorerPanel(QWidget):
    file_opened = Signal(str)
    folder_changed = Signal(str)
    
    def __init__(self, api: PluginAPI)
    def set_workspace_root(self, path: str) -> None
    def refresh_tree(self) -> None
    def get_selected_files(self) -> List[str]
    def expand_to_path(self, path: str) -> None
```

#### 3. FileSystemModel (models/filesystem_model.py)
**Purpose:** File system data model with PO file support

**Key Features:**
- Hierarchical file system representation
- PO file detection and metadata
- File filtering and search
- Lazy loading for performance
- File watching for auto-refresh

**Interface:**
```python
class FileSystemModel(QAbstractItemModel):
    def __init__(self, root_path: str)
    def set_root_path(self, path: str) -> None
    def get_file_info(self, index: QModelIndex) -> FileInfo
    def is_po_file(self, path: str) -> bool
    def get_po_file_stats(self, path: str) -> Dict
```

#### 4. ExplorerTreeView (widgets/tree_view.py)
**Purpose:** Specialized tree view for file navigation

**Key Features:**
- Custom rendering for file types
- PO file status indicators
- Keyboard navigation
- Context menu support
- Multi-selection support

**Interface:**
```python
class ExplorerTreeView(QTreeView):
    def __init__(self, model: FileSystemModel)
    def setup_context_menu(self) -> None
    def handle_double_click(self, index: QModelIndex) -> None
    def get_selected_paths(self) -> List[str]
```

#### 5. ExplorerToolbar (widgets/toolbar.py)
**Purpose:** Navigation and action toolbar

**Key Features:**
- Navigation buttons (back, forward, up, home)
- Refresh and search buttons
- View mode toggles
- New file/folder actions

**Interface:**
```python
class ExplorerToolbar(QToolBar):
    def __init__(self, api: PluginAPI)
    def update_navigation_state(self, can_go_back: bool, can_go_forward: bool) -> None
    def set_current_path(self, path: str) -> None
```

### Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Explorer Panel                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                          Toolbar                                        │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     ┌─────────────────────┐   │
│  │  ←  │ │  →  │ │  ↑  │ │ 🏠  │ │  ⟳  │     │  🔍 Search...       │   │
│  │Back │ │Fwd  │ │ Up  │ │Home │ │Refr │     │                     │   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘     └─────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                        File Tree View                                   │
│  📁 workspace_root/                                                     │
│  ├── 📁 locales/                                                        │
│  │   ├── 📄 messages.po        [📊 85% translated]                      │
│  │   ├── 📄 errors.po          [⚠️  45% translated]                      │
│  │   └── 📄 ui.pot             [📝 template]                            │
│  ├── 📁 src/                                                            │
│  │   ├── 📄 main.py                                                     │
│  │   └── 📄 utils.py                                                    │
│  ├── 📄 README.md                                                       │
│  └── 📄 requirements.txt                                                │
├─────────────────────────────────────────────────────────────────────────┤
│                         Status Bar                                      │
│  25 files │ 8 folders │ 3 PO files │ 2 modified                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Initialization:**
   - ExplorerPlugin registers with PluginAPI
   - Creates ExplorerPanel and adds to sidebar
   - Sets up file system model and tree view
   - Registers commands and event handlers

2. **File Navigation:**
   - User clicks folder → Tree expands/collapses
   - User double-clicks file → Opens in appropriate tab
   - User navigates with toolbar → Updates tree view

3. **PO File Integration:**
   - File system model detects PO files
   - Loads PO file metadata (translation progress)
   - Displays status indicators in tree view

4. **Workspace Management:**
   - Saves/restores workspace root
   - Manages project-specific settings
   - Handles workspace switching

### Configuration

The Explorer plugin uses the following configuration keys in the `explorer` namespace:

```python
DEFAULT_CONFIG = {
    "workspace_root": "",
    "show_hidden_files": False,
    "auto_refresh": True,
    "file_filters": ["*.po", "*.pot", "*.py", "*.md"],
    "tree_expanded_state": {},
    "selected_files": [],
    "navigation_history": [],
    "navigation_index": 0,
    "toolbar_visible": True,
    "status_bar_visible": True,
    "icon_size": 16,
    "show_po_progress": True
}
```

### Commands

The Explorer plugin registers the following commands:

- `explorer.open_file`: Open file in appropriate editor
- `explorer.open_folder`: Open folder in system file manager
- `explorer.refresh`: Refresh file tree
- `explorer.new_file`: Create new file
- `explorer.new_folder`: Create new folder
- `explorer.delete`: Delete selected files/folders
- `explorer.rename`: Rename selected item
- `explorer.copy_path`: Copy file path to clipboard
- `explorer.reveal_in_explorer`: Show file in system explorer
- `explorer.set_workspace_root`: Set workspace root directory

### Events

The Explorer plugin emits and listens for these events:

**Emitted:**
- `explorer.file_opened`: When file is opened
- `explorer.folder_changed`: When current folder changes
- `explorer.workspace_changed`: When workspace root changes
- `explorer.selection_changed`: When file selection changes

**Listened:**
- `tab.file_saved`: Update file status when saved
- `tab.file_modified`: Update file status when modified
- `workspace.opened`: Switch to new workspace

### Integration Points

#### With Tab System
- Opens PO files in POEditor tabs
- Opens other files in appropriate viewers
- Syncs with active tab to highlight current file

#### With Search Plugin
- Provides file context for search results
- Allows navigation to search result files

#### With File Service
- Uses file watching for auto-refresh
- Leverages file operation utilities

#### With Configuration Service
- Stores workspace and view preferences
- Restores panel state on startup

### Performance Considerations

#### Lazy Loading
- Only loads visible tree nodes
- Defers PO file analysis until needed
- Uses background threads for file operations

#### File Watching
- Efficient file system monitoring
- Batched update notifications
- Configurable watch patterns

#### Caching
- Caches file metadata and icons
- Stores PO file translation statistics
- Invalidates cache on file changes

### Error Handling

#### File System Errors
- Graceful handling of permission errors
- Recovery from network drive disconnections
- User-friendly error messages

#### PO File Errors
- Handles corrupted PO files
- Shows warning indicators for invalid files
- Continues operation with degraded functionality

### Testing Strategy

#### Unit Tests
- FileSystemModel data operations
- Navigation history management
- PO file detection and analysis
- Configuration management

#### Integration Tests
- Plugin registration and lifecycle
- File operations and tab integration
- Event handling and communication

#### UI Tests
- Tree view interactions
- Context menu functionality
- Toolbar button actions

### Future Enhancements

#### Advanced Features
- Git integration showing file status
- Project templates for PO workflows
- Advanced search and filtering
- Bookmark management
- Multi-workspace support

#### Performance Optimizations
- Virtual tree view for large directories
- Incremental PO file analysis
- Smarter file watching
- Background metadata loading

### Migration from Old Code

The Explorer plugin reuses and adapts components from:

**old_codes/workspace/**
- File system navigation utilities
- Workspace management logic
- File operation handlers

**old_codes/toolbars/explorer/**
- Explorer toolbar components
- Navigation history management
- UI layout and styling

### Dependencies

**Core Services:**
- ConfigurationService: Settings management
- FileService: File operations and watching
- EventService: Inter-plugin communication

**Qt Components:**
- QTreeView: File tree display
- QFileSystemModel: Base file system model
- QToolBar: Navigation toolbar
- QFileSystemWatcher: File change monitoring

**External Libraries:**
- polib: PO file analysis and statistics
- pathlib: Path manipulation utilities
