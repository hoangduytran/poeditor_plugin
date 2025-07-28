# Context Menu UI Design

**Date**: July 28, 2025, 07:32  
**Component**: Explorer Context Menu - UI Design  
**Status**: Technical Design  
**Priority**: High

## Overview

This document describes the design of the context menu user interface for the Explorer panel. The context menu will provide users with quick access to file operations and will be contextually aware of the selected items.

## Design Principles

1. **Consistency**: Match system conventions for context menus
2. **Clarity**: Clear organization with visual separators between groups
3. **Efficiency**: Optimize for common operations and include keyboard shortcuts
4. **Contextual Awareness**: Show only relevant operations for selected items
5. **Extensibility**: Support plugin contributions to the context menu

## Menu Structure

The context menu will be organized into logical sections, separated by dividers:

### 1. Primary Operations

These are the most common operations that appear at the top of the menu:

- **Open** (default action when double-clicking)
- **Open With...** (submenu with registered applications)
- **Open in New Window** (for folders)

### 2. Edit Operations

Standard editing operations:

- **Cut** (Ctrl+X)
- **Copy** (Ctrl+C)
- **Paste** (Ctrl+V)
- **Duplicate** (Ctrl+D)
- **Rename** (F2)
- **Delete** (Del)

### 3. Creation Operations

Operations for creating new items:

- **New File**
- **New Folder**
- **New From Template...** (submenu with available templates)

### 4. Advanced Operations

Less common but important operations:

- **Properties**
- **Open Terminal Here** (for folders)
- **Find in Folder** (for folders)
- **Add to Favorites**

### 5. Plugin Operations

Custom operations contributed by plugins:

- (Dynamic based on registered plugins)

## Visual Design

### Menu Appearance

- Use application's current theme for consistency
- Standard indentation and padding for menu items
- Icons on the left side of each menu item
- Keyboard shortcuts displayed on the right side
- Dividers between logical sections
- Disabled appearance for unavailable actions

### Icons

- Use standard file operation icons for recognition
- Icons should be theme-aware (light/dark mode compatible)
- Size: 16x16 pixels for menu items

## Interaction Design

### Triggering the Context Menu

- Right-click on file or folder
- Context menu key on keyboard
- Long-press on touch devices

### Selection Handling

- Single selection: Show all applicable operations
- Multi-selection: Show operations that can work on multiple items
- Mixed selection (files and folders): Show only operations that work on both

### Operation Feedback

- Visual feedback when operations are in progress
- Success/failure notifications for completed operations
- Progress indicators for long-running operations

## Conditional Logic

The context menu will adapt based on various conditions:

| Condition | Menu Adaptation |
|-----------|----------------|
| File selected | Show file-specific operations |
| Folder selected | Show folder-specific operations |
| Multiple items selected | Show only multi-item compatible operations |
| Read-only location | Disable write operations |
| Special file types | Show type-specific operations |

## Implementation Considerations

### Menu Construction

```python
def create_context_menu(selected_items):
    menu = QMenu()
    
    # Primary operations
    add_primary_operations(menu, selected_items)
    menu.addSeparator()
    
    # Edit operations
    add_edit_operations(menu, selected_items)
    menu.addSeparator()
    
    # Creation operations (only shown when appropriate)
    if can_create_items(selected_items):
        add_creation_operations(menu, selected_items)
        menu.addSeparator()
    
    # Advanced operations
    add_advanced_operations(menu, selected_items)
    
    # Plugin operations
    add_plugin_operations(menu, selected_items)
    
    return menu
```

### Action Handling

Actions will be connected to handlers in the FileOperationsService:

```python
def add_edit_operations(menu, selected_items):
    cut_action = menu.addAction(QIcon("icons/cut.svg"), "Cut")
    cut_action.setShortcut(QKeySequence.Cut)
    cut_action.triggered.connect(lambda: file_operations_service.cut(selected_items))
    cut_action.setEnabled(can_cut(selected_items))
    
    # Similar pattern for other actions
```

## Accessibility Considerations

- All menu items should be keyboard navigable
- Ensure proper screen reader support
- High-contrast mode compatibility
- Keyboard shortcuts for common operations

## Testing Requirements

- Test menu appearance with different themes
- Test with various selection scenarios
- Test keyboard accessibility
- Test with screen readers
- Test plugin integration

## Open Questions

1. Should we include custom icons for special file types?
2. How many levels of submenus are appropriate for the "Open With" functionality?
3. Should we implement a "Recent Operations" section?
4. How should we handle very large numbers of selected items?
