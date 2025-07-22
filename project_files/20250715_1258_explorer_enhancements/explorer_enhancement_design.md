# Explorer Plugin Enhancement Design

## Overview
This document outlines enhancements to the Explorer plugin to improve navigation, search functionality, and user experience with persistent settings and quick navigation features.

## Current State
The Explorer plugin currently provides basic file system navigation with a tree view. It lacks:
- Persistent location memory
- Search history
- Quick navigation to common locations
- Keyboard shortcuts for navigation

## Proposed Enhancements

### 1. Persistent Location Memory
**Goal:** Remember the last visited location across application sessions

**Implementation:**
- Store last visited path in application settings
- Restore to last location on startup
- Update setting whenever user navigates to new directory
- Fallback to user home directory if last location doesn't exist

**Settings Key:** `explorer.lastLocation`

### 2. Search History with Keyboard Navigation
**Goal:** Maintain search history with keyboard shortcuts for navigation

**Features:**
- Store last 50 search terms in chronological order
- Ctrl+Up Arrow: Navigate to previous search term
- Ctrl+Down Arrow: Navigate to next search term
- Clear history option in context menu
- Auto-complete dropdown showing recent searches

**Implementation:**
- Circular buffer for search history
- QCompleter integration for auto-complete
- Custom key event handling for navigation shortcuts

**Settings Key:** `explorer.searchHistory`

### 3. Quick Navigation System (Goto Button)
**Goal:** Replace simple Home button with comprehensive navigation system

**Features:**
- **Predefined Locations:**
  - Home Directory (`~`)
  - Root Directory (`/`)
  - Applications Directory (`/Applications` on macOS)
  - Documents Directory
  - Downloads Directory
  - Desktop Directory
  - Current Project Root
  - Recently Visited Directories (last 10)

- **Custom Path Input:**
  - Text field for manual path entry
  - Path validation and auto-completion
  - Bookmark favorite directories
  - Environment variable support (`$HOME`, `$USER`, etc.)

**UI Design:**
```
[Goto ▼] [Search Field] [Navigation Buttons]
```

Dropdown menu structure:
```
Quick Locations
├── Home                    (~)
├── Root                    (/)
├── Applications           (/Applications)
├── Documents              (~/Documents)
├── Downloads              (~/Downloads)
├── Desktop                (~/Desktop)
├── Project Root           (/path/to/project)
├── ─────────────────────
├── Recent Locations
├── → /path/to/recent1
├── → /path/to/recent2
├── ─────────────────────
├── Bookmarks
├── ★ /path/to/bookmark1
├── ★ /path/to/bookmark2
├── ─────────────────────
├── Go to Path...          (Ctrl+G)
└── Manage Bookmarks...
```

### 4. Additional Suggested Enhancements

#### 4.1 Path Breadcrumbs
- Visual breadcrumb navigation at top of explorer
- Click any segment to jump to that directory
- Right-click for directory-specific actions

#### 4.2 Enhanced Keyboard Navigation
- **Ctrl+L:** Focus path input for quick navigation
- **Ctrl+H:** Toggle hidden files visibility
- **Ctrl+R:** Refresh current directory
- **Ctrl+B:** Toggle bookmarks sidebar
- **F5:** Refresh directory contents
- **Backspace:** Go to parent directory

#### 4.3 File Operations Enhancements
- **Cut/Copy/Paste:** Standard file operations with Ctrl+X/C/V
- **Drag & Drop:** Support for file movement and copying
- **Context Menu:** Enhanced right-click menu with common operations
- **Quick Preview:** Spacebar for quick file preview (like macOS Finder)

#### 4.4 Search Enhancements
- **Search Scope Options:**
  - Current directory only
  - Current directory and subdirectories
  - Entire project
  - Custom scope selection

- **Search Filters:**
  - File type filters (.po, .pot, .py, etc.)
  - File size filters
  - Date modified filters
  - Content search within files

#### 4.5 Visual Enhancements
- **Directory Icons:** Custom icons for different directory types
- **File Type Icons:** Specific icons for .po, .pot, and other file types
- **Color Coding:** Different colors for modified, new, and unchanged files
- **Compact/Detail Views:** Toggle between compact and detailed list views

#### 4.6 Integration Features
- **Recent Files:** Show recently opened PO files at top
- **Modified Files:** Highlight files with unsaved changes
- **Project Integration:** Show project-specific file organization
- **Git Integration:** Show git status indicators for files

## Technical Implementation Details

### Settings Management
```python
class ExplorerSettings:
    def __init__(self, config_service):
        self.config = config_service
        
    def get_last_location(self) -> str:
        return self.config.get('explorer.lastLocation', str(Path.home()))
    
    def set_last_location(self, path: str):
        self.config.set('explorer.lastLocation', path)
    
    def get_search_history(self) -> List[str]:
        return self.config.get('explorer.searchHistory', [])
    
    def add_search_term(self, term: str):
        history = self.get_search_history()
        if term in history:
            history.remove(term)
        history.insert(0, term)
        history = history[:50]  # Keep only last 50
        self.config.set('explorer.searchHistory', history)
    
    def get_bookmarks(self) -> List[Dict[str, str]]:
        return self.config.get('explorer.bookmarks', [])
    
    def add_bookmark(self, name: str, path: str):
        bookmarks = self.get_bookmarks()
        bookmarks.append({'name': name, 'path': path})
        self.config.set('explorer.bookmarks', bookmarks)
```

### Quick Navigation Component
```python
class QuickNavigationWidget(QWidget):
    location_changed = Signal(str)
    
    def __init__(self, settings: ExplorerSettings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Goto dropdown button
        self.goto_button = QPushButton("Goto")
        self.goto_menu = self.create_goto_menu()
        self.goto_button.setMenu(self.goto_menu)
        
        # Path input with auto-complete
        self.path_input = QLineEdit()
        self.setup_path_autocomplete()
        
        layout.addWidget(self.goto_button)
        layout.addWidget(self.path_input)
        self.setLayout(layout)
    
    def create_goto_menu(self) -> QMenu:
        menu = QMenu()
        
        # Quick locations
        menu.addAction("Home", lambda: self.navigate_to(str(Path.home())))
        menu.addAction("Root", lambda: self.navigate_to("/"))
        menu.addAction("Applications", lambda: self.navigate_to("/Applications"))
        # ... more locations
        
        menu.addSeparator()
        
        # Recent locations
        recent_menu = menu.addMenu("Recent Locations")
        self.populate_recent_locations(recent_menu)
        
        menu.addSeparator()
        
        # Bookmarks
        bookmarks_menu = menu.addMenu("Bookmarks")
        self.populate_bookmarks(bookmarks_menu)
        
        menu.addSeparator()
        menu.addAction("Go to Path...", self.show_path_dialog)
        menu.addAction("Manage Bookmarks...", self.show_bookmark_manager)
        
        return menu
```

### Search History Component
```python
class SearchWidget(QWidget):
    search_requested = Signal(str)
    
    def __init__(self, settings: ExplorerSettings):
        super().__init__()
        self.settings = settings
        self.current_history_index = -1
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        
        # Setup auto-complete with history
        self.completer = QCompleter(self.settings.get_search_history())
        self.search_input.setCompleter(self.completer)
        
        # Custom key event handling
        self.search_input.keyPressEvent = self.handle_key_press
        
        layout.addWidget(self.search_input)
        self.setLayout(layout)
    
    def handle_key_press(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Up:
                self.navigate_history_up()
                return
            elif event.key() == Qt.Key_Down:
                self.navigate_history_down()
                return
        
        # Default handling
        super(QLineEdit, self.search_input).keyPressEvent(event)
    
    def navigate_history_up(self):
        history = self.settings.get_search_history()
        if history and self.current_history_index < len(history) - 1:
            self.current_history_index += 1
            self.search_input.setText(history[self.current_history_index])
    
    def navigate_history_down(self):
        history = self.settings.get_search_history()
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.search_input.setText(history[self.current_history_index])
        elif self.current_history_index == 0:
            self.current_history_index = -1
            self.search_input.clear()
```

## UI Mockup

### Enhanced Explorer Panel Layout
```
┌─────────────────────────────────────────────────────────────┐
│ [Goto ▼] [Search _______________] [🔍] [⚙️]                │
├─────────────────────────────────────────────────────────────┤
│ Home > Projects > MyProject > translations                  │
├─────────────────────────────────────────────────────────────┤
│ 📁 assets/                                                  │
│ 📁 docs/                                                    │
│ 📁 src/                                                     │
│ 📁 translations/                                            │
│   ├── 📄 en.po                                             │
│   ├── 📄 es.po                                             │
│   ├── 📄 fr.po                                             │
│   └── 📄 template.pot                                      │
│ 📄 README.md                                               │
│ 📄 requirements.txt                                        │
└─────────────────────────────────────────────────────────────┘
```

### Goto Menu Dropdown
```
┌─────────────────────────────┐
│ 🏠 Home                     │
│ 💽 Root                     │
│ 📱 Applications             │
│ 📁 Documents                │
│ 📥 Downloads                │
│ 🖥️  Desktop                 │
│ 📊 Project Root             │
├─────────────────────────────┤
│ Recent Locations            │
│ → /path/to/recent1          │
│ → /path/to/recent2          │
├─────────────────────────────┤
│ Bookmarks                   │
│ ★ Important Project         │
│ ★ Translation Files         │
├─────────────────────────────┤
│ ⌨️  Go to Path...           │
│ ⚙️  Manage Bookmarks...     │
└─────────────────────────────┘
```

## Implementation Priority

### Phase 1 (High Priority)
1. Persistent location memory
2. Basic search history with Ctrl+Up/Down navigation
3. Replace Home button with Goto dropdown
4. Add predefined quick locations

### Phase 2 (Medium Priority)
1. Bookmark management system
2. Recent locations tracking
3. Path breadcrumbs
4. Enhanced keyboard shortcuts

### Phase 3 (Lower Priority)
1. Advanced search filters
2. File operations (cut/copy/paste)
3. Drag & drop support
4. Visual enhancements and theming

## Questions for Discussion

1. **Search Scope:** Should search be limited to the current directory by default, or should it search the entire project?

2. **Bookmark Synchronization:** Should bookmarks be stored per-project or globally across all projects?

3. **Recent Locations:** How many recent locations should we store? Should they be global or per-project?

4. **Path Input:** Should the path input always be visible, or should it appear only when "Go to Path" is selected?

   **✅ RESOLVED (Phase 1 Implementation):** 
   - Path input appears only when "Enter Path..." is selected from Goto menu
   - This provides cleaner UI while keeping the functionality easily accessible
   - Modal dialog approach prevents UI clutter and provides focused path entry experience
   - Users can still quickly access via Ctrl+G shortcut (planned for Phase 2)

5. **Integration:** How should this integrate with existing workspace/project management features?

6. **Performance:** For large directories, should we implement lazy loading or pagination?

7. **Platform Differences:** Should we have platform-specific quick locations (e.g., different for Windows/macOS/Linux)?

## Additional Enhancement Ideas

1. **Smart Bookmarks:** Auto-bookmark frequently visited directories
2. **Workspace Integration:** Show workspace-specific navigation options
3. **File Relationships:** Show related files (e.g., .po and .pot files together)
4. **Quick Actions:** Context-sensitive quick actions for different file types
5. **Split View:** Option to show two directory trees side by side
6. **Terminal Integration:** "Open in Terminal" option
7. **External Editor:** "Open in External Editor" integration
8. **File Watching:** Real-time updates when files change
9. **Search Highlighting:** Highlight search terms in file names
10. **Thumbnail Previews:** Show thumbnails for image files

Would you like me to proceed with implementing any of these features, or would you prefer to discuss and refine the design further?
