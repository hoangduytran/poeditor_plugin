# Explorer Context Menu Developer Guide

This guide explains how to work with and extend the Explorer Context Menu functionality in the POEditor application, including the Phase 4 accessibility and advanced navigation features.

## Architecture Overview

The Explorer Context Menu system follows a signal-based architecture with clear separation between:

1. **User Interface Components**: The context menu itself with accessibility support
2. **Action Handling**: Operations triggered by menu items
3. **Service Integration**: Interactions with file operations services
4. **Accessibility Layer**: Screen reader support and keyboard navigation
5. **Theme Integration**: CSS-based styling system

## Core Components

### ExplorerContextMenu Class

The `ExplorerContextMenu` class serves as a context menu manager that:

- Generates appropriate menu items based on selection state
- Triggers actions through connected signals
- Integrates with file operations services
- Manages keyboard shortcuts and accessibility features
- Handles theme-aware icon loading

### Phase 4 Components

#### MenuAccessibilityManager

The accessibility manager provides:

- ARIA label management for screen readers
- Focus tracking and restoration
- Screen reader announcements for operations
- Keyboard navigation enhancements

```python
# Example usage
menu_accessibility_manager.add_accessibility_to_menu(menu)
menu_accessibility_manager.announce_to_screen_reader("Cut 3 items")
menu_accessibility_manager.track_focus(focused_widget)
```

#### MenuKeyboardNavigator

The keyboard navigator handles:

- First-letter navigation (type 'c' for "Copy")
- Enhanced arrow key navigation
- Menu item activation via keyboard
- Event filtering for menu-specific shortcuts

```python
# Example integration
setup_menu_keyboard_navigation(menu)
```

### Signals and Events

Rather than direct function calls, the menu uses signals to communicate with parent components:

- `show_properties`: Triggered when user requests item properties
- `show_open_with`: Triggered when user wants to choose an application
- `refresh_requested`: Triggered when user requests a view refresh

This signal-based approach ensures loose coupling between components.

## Phase 4 Development Features

### Accessibility Implementation

When adding new menu items, ensure accessibility compliance:

```python
def _add_custom_operation(self, menu: QMenu):
    action = QAction("Custom Operation", menu)
    
    # Add accessibility attributes
    action.setToolTip("Performs a custom operation on selected files")
    action.setStatusTip("Custom operation status")
    
    # Connect to handler
    action.triggered.connect(self._handle_custom_operation)
    menu.addAction(action)
    
    # Accessibility manager will automatically handle ARIA labels
```

### Keyboard Navigation Integration

New menu sections automatically inherit keyboard navigation:

```python
def _add_plugin_section(self, menu: QMenu):
    # Create menu items normally
    plugin_action = QAction("Plugin Operation", menu)
    menu.addAction(plugin_action)
    
    # Keyboard navigation is automatically applied
    # First-letter navigation will work for 'p' -> "Plugin Operation"
```

### Theme Integration

Menu items automatically inherit theme styling:

```python
def _load_custom_icons(self):
    # Icons adapt to current theme
    self.custom_icons = {
        "plugin": QIcon("icons/plugin.svg"),  # Will use theme colors
    }
    
    # Graceful fallback for missing icons
    if not os.path.exists("icons/plugin.svg"):
        self.custom_icons["plugin"] = QIcon()  # Empty icon
```

## Extending the Context Menu

### Adding New Menu Items

To add a new menu item to a specific section:

1. Define a new action in the appropriate `_add_*_operations` method
2. Create a handler method to process the action
3. Connect the action's triggered signal to your handler
4. The accessibility and keyboard navigation features will be automatically applied

### Creating a New Section

To add an entirely new section of menu items:

1. Create a new `_add_custom_section` method
2. Call it from the `create_menu` method
3. Add a separator before or after your section as needed
4. All Phase 4 features (accessibility, keyboard navigation, theme support) are inherited

### Integrating with Plugins

The context menu is designed to be extensible through plugins:

1. Plugins can register custom actions
2. The menu manager can dynamically include these plugin actions
3. Actions can be filtered based on selection state
4. Accessibility features work automatically for plugin items

## Best Practices

### Signal-Based Communication

Always use signals rather than direct method calls when communicating between components. This allows for:

- Easy replacement of components
- Unit testing with mock objects
- Loose coupling between UI and business logic
- Better accessibility support

### Accessibility-First Development

When implementing new features:

- Use descriptive action text and tooltips
- Provide status tips for complex operations
- Test with screen readers
- Ensure keyboard-only operation is possible
- Follow ARIA best practices

### Theme-Aware Development

- Use CSS selectors for styling rather than hardcoded colors
- Test with different themes (light, dark, high contrast)
- Provide fallbacks for missing theme resources
- Use semantic color names rather than specific hex values

### Selection-Aware Menu Items

Always check the selection state (single/multiple, files/folders) to determine:

- Which menu items to show
- Whether items should be enabled or disabled
- Which actions to trigger

### Error Handling

When implementing action handlers:

- Validate inputs before performing operations
- Provide clear feedback for successful operations
- Handle errors gracefully with informative messages
- Log important events and errors

### Refresh Handling

The refresh functionality works by:

1. Capturing user requests through the `refresh_requested` signal
2. Having view components listen for this signal
3. Reloading the current directory data when triggered

This approach keeps the context menu decoupled from the view implementation details.
