# Fixed Activity Bar & Dockable Sidebar Design

**Date:** July 16, 2025
**Component:** MainAppWindow, ActivityBar, SidebarManager

## Overview
This design updates the UI so that the Activity Bar is always fixed on the left and cannot be moved or docked. The Sidebar (with all its panels/components) is dockable and can be positioned on the left or right. The Sidebar includes a small toolbar at the top with an arrow button to show/hide a menu for dock options.

## Layout Structure
```
MainAppWindow (QMainWindow)
├── MenuBar
├── ActivityBar (fixed, always left)
├── SidebarDockWidget (dockable left/right)
│   └── SidebarManager (panel container)
│   └── Toolbar (arrow button, dock menu)
├── TabManager
└── StatusBar
```

## Features
- **Activity Bar:**
  - Always fixed on the left
  - Cannot be moved, docked, or closed
- **Sidebar:**
  - Dockable to left or right
  - Contains all panels/components
  - Toolbar at top with arrow button
  - Arrow button toggles menu for dock options (left/right)
  - Prevent closing of SidebarDockWidget
- **User Interaction:**
  - Users can dock the sidebar left or right via toolbar menu
  - Sidebar panels can be shown/hidden

## Implementation Plan
1. **ActivityBar Widget**
   - Remains fixed on the left in MainAppWindow
   - No QDockWidget wrapper
2. **SidebarDockWidget**
   - Wraps SidebarManager
   - Contains toolbar with arrow button
   - Menu for dock options (left/right)
   - Prevent closing (override closeEvent)
3. **MainAppWindow**
   - Layout: [ActivityBar][SidebarDockWidget][TabManager]
   - On startup, ActivityBar is always leftmost
   - SidebarDockWidget is docked left or right based on user preference
   - Dock position changes via toolbar menu
4. **Testing**
   - Test dock position changes
   - Test menu functionality
   - Test prevention of closing ActivityBar and SidebarDockWidget

## Rules Compliance
- All new files in correct folders
- All test/demo files in correct positions
- Use 'mv' for file moves
- Commit messages and structure as per rules.md

## Migration Steps
1. Implement SidebarDockWidget with toolbar and menu
2. Update MainAppWindow to use fixed ActivityBar and dockable SidebarDockWidget
3. Add logic for dock position changes via toolbar menu
4. Prevent closing of ActivityBar and SidebarDockWidget
5. Add tests for dock position and menu functionality

