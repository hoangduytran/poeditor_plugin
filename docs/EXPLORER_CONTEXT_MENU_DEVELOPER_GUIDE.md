# Explorer Context Menu Developer Guide

This guide explains how to work with and extend the Explorer Context Menu functionality in the POEditor application.

## Architecture Overview

The Explorer Context Menu system follows a signal-based architecture with clear separation between:

1. **User Interface Components**: The context menu itself
2. **Action Handling**: Operations triggered by menu items
3. **Service Integration**: Interactions with file operations services

## Core Components

### ExplorerContextMenu Class

The `ExplorerContextMenu` class serves as a context menu manager that:

- Generates appropriate menu items based on selection state
- Triggers actions through connected signals
- Integrates with file operations services

### Signals and Events

Rather than direct function calls, the menu uses signals to communicate with parent components:

- `show_properties`: Triggered when user requests item properties
- `show_open_with`: Triggered when user wants to choose an application
- `refresh_requested`: Triggered when user requests a view refresh

This signal-based approach ensures loose coupling between components.

## Extending the Context Menu

### Adding New Menu Items

To add a new menu item to a specific section:

1. Define a new action in the appropriate `_add_*_operations` method
2. Create a handler method to process the action
3. Connect the action's triggered signal to your handler

### Creating a New Section

To add an entirely new section of menu items:

1. Create a new `_add_custom_section` method
2. Call it from the `create_menu` method
3. Add a separator before or after your section as needed

### Integrating with Plugins

The context menu is designed to be extensible through plugins:

1. Plugins can register custom actions
2. The menu manager can dynamically include these plugin actions
3. Actions can be filtered based on selection state

## Best Practices

### Signal-Based Communication

Always use signals rather than direct method calls when communicating between components. This allows for:

- Easy replacement of components
- Unit testing with mock objects
- Loose coupling between UI and business logic

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
