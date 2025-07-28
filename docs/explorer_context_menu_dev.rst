=================================
Explorer Context Menu Development
=================================

This document provides technical details for developers working with the Explorer Context Menu system in POEditor, including the Phase 4 accessibility and advanced navigation features.

.. contents:: Table of Contents
   :depth: 2
   :local:

Architecture
===========

Component Overview
----------------

The Explorer Context Menu system consists of several interconnected components:

* **ExplorerContextMenu**
  
  The core class responsible for:
  
  * Creating appropriate menu items based on selection state
  * Handling menu actions with accessibility support
  * Emitting signals for parent components
  * Integrating with file operation services
  * Managing keyboard shortcuts and navigation

* **MenuAccessibilityManager**
  
  Provides accessibility features including:
  
  * Screen reader integration with ARIA attributes
  * Focus tracking and restoration
  * Operation announcements
  * Keyboard navigation enhancements

* **MenuKeyboardNavigator**
  
  Handles advanced keyboard navigation:
  
  * First-letter navigation
  * Enhanced arrow key navigation
  * Event filtering for keyboard shortcuts
  * Menu item activation via keyboard

* **SimpleFileView**
  
  A view component that:
  
  * Displays files and directories in a tree view
  * Handles context menu requests
  * Responds to selection changes
  * Manages drag-and-drop operations
  * Integrates with ExplorerContextMenu

* **FileOperationsService**
  
  A service that:
  
  * Performs actual file system operations
  * Handles undo/redo functionality
  * Manages clipboard operations
  * Provides consistent error handling

Signal-Based Communication
------------------------

The system uses a signal-based architecture for communication between components:

* **Signal Flow**

  1. User initiates context menu request
  2. View captures context and selection state
  3. Context menu manager creates appropriate menu
  4. User selects an action
  5. Action triggers a signal
  6. Signal connects to appropriate handler
  7. Handler performs the requested operation

* **Key Signals**

  * **show_properties**: Requests property display for selected items
  * **show_open_with**: Requests application chooser for selected files
  * **refresh_requested**: Indicates view refresh is needed
  * **file_activated**: Emitted when a file is opened
  * **directory_changed**: Emitted when navigation occurs

Phase 4 Features
===============

Accessibility Implementation
--------------------------

The Phase 4 accessibility system provides comprehensive support for users with disabilities:

* **MenuAccessibilityManager**
  
  * Manages ARIA attributes for screen readers
  * Tracks focus state before menu opens
  * Announces operation results to screen readers
  * Provides keyboard navigation enhancements

* **Screen Reader Integration**
  
  * All menu items have descriptive ARIA labels
  * Operation results are announced (e.g., "Cut 3 items")
  * Menu structure is properly exposed to assistive technologies

* **Focus Management**
  
  * Remembers which widget had focus before menu opened
  * Restores focus when menu closes
  * Provides clear visual focus indicators

Advanced Keyboard Navigation
--------------------------

The Phase 4 keyboard navigation system includes:

* **MenuKeyboardNavigator**
  
  * Handles first-letter navigation
  * Manages enhanced arrow key navigation
  * Filters keyboard events for menu-specific shortcuts
  * Provides smooth navigation experience

* **First-Letter Navigation**
  
  * Type any letter to jump to menu items starting with that letter
  * Repeated typing cycles through matching items
  * Works seamlessly with screen readers

* **Enhanced Arrow Navigation**
  
  * Up/Down arrows with proper wraparound
  * Enter/Space activation
  * Escape to close menu

Theme Integration
---------------

Phase 4 includes comprehensive theme support:

* **CSS-Based Styling**
  
  * Menu appearance adapts to application themes
  * Consistent visual styling across all components
  * Support for custom themes through CSS selectors

* **Icon Management**
  
  * Graceful fallback for missing icon files
  * Theme-aware icon loading
  * Performance optimizations for icon caching

Performance Optimizations
------------------------

Phase 4 includes several performance improvements:

* **Lazy Menu Creation**
  
  * Menu items only created when needed
  * Reduced memory usage for large file lists
  * Faster menu display times

* **Optimized Icon Loading**
  
  * Cached empty icons for missing SVG files
  * Reduced file system access for icon operations
  * Improved startup performance

* **Enhanced Signal Handling**
  
  * More efficient signal connections
  * Reduced overhead for menu operations
  * Better resource cleanup

Implementation Guide
==================

Adding New Menu Items
-------------------

To add a new menu item to the context menu:

1. **Define the Action**
   
   * Determine which menu section is appropriate
   * Create a descriptive label and optional icon
   * Consider keyboard shortcuts for common operations

2. **Implement the Handler**
   
   * Create a method to handle the action
   * Consider error handling and feedback
   * Document the method's purpose and parameters

3. **Connect the Action**
   
   * Use the triggered signal to connect to the handler
   * Consider whether to use direct function call or signals
   * Add appropriate conditions for when the action should be available

Example for a "Compress" Action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's how you would add a new compression action:

1. Identify the appropriate menu section (likely advanced operations)
2. Create a handler method for compressing files
3. Add the menu item to the appropriate section method
4. Connect the action to the handler method
5. Test with various selection states

Menu Section Guidelines
---------------------

Each menu section should follow these guidelines:

* **Primary Operations**
  
  * Most common actions users perform
  * Should appear at the top of the menu
  * Include open, open with, etc.

* **Edit Operations**
  
  * File manipulation actions
  * Include cut, copy, paste, rename, delete
  * Consider selection state for availability

* **Creation Operations**
  
  * Actions that create new items
  * Include new file, new folder
  * Only show when appropriate

* **Advanced Operations**
  
  * Less common but important actions
  * Include properties, terminal, find, etc.
  * May involve more complex interactions

Handling Selection States
-----------------------

Menu items should adapt to selection context:

* **Single vs. Multiple Selection**
  
  * Some operations only make sense for single items (rename)
  * Others work with multiple items (delete, copy)
  * Use the `single_item` parameter to check

* **Files vs. Directories**
  
  * Some operations are specific to files (open with)
  * Others are specific to directories (open terminal)
  * Use the `only_dirs` and `only_files` parameters to check

* **No Selection (Background)**
  
  * Show creation and clipboard operations
  * Provide navigation options
  * Include refresh functionality

Best Practices
============

Code Organization
---------------

* **Separate Menu Creation from Action Handling**
  
  Keep menu creation methods separate from the methods that perform actions.
  This improves code readability and makes testing easier.

* **Group Related Functionality**
  
  Organize menu items into logical sections rather than creating one long menu.
  This improves usability and code maintenance.

* **Use Descriptive Names**
  
  Use clear method and signal names that describe their purpose rather than
  their implementation details.

Error Handling
------------

* **Validate Inputs**
  
  Check that paths exist and have appropriate permissions before attempting operations.

* **Provide User Feedback**
  
  Always inform the user about the result of their actions, especially for failures.

* **Use Logging**
  
  Log important events and errors for troubleshooting without exposing technical
  details to end users.

Performance Considerations
-----------------------

* **Lazy Menu Creation**
  
  Only create menu items when needed, not in advance.

* **Avoid Blocking Operations**
  
  Use asynchronous operations for potentially slow file operations.

* **Minimize File System Access**
  
  Cache information when possible rather than repeatedly querying the file system.

Testing Guidelines
---------------

* **Test Different Selection States**
  
  Verify menu behavior with:
  * Single file selected
  * Multiple files selected
  * Single directory selected
  * Multiple directories selected
  * Mixed files and directories
  * No selection (background)

* **Test Error Conditions**
  
  Verify proper handling of:
  * Permission errors
  * File not found
  * Invalid operations
  * Disk full conditions

* **Test Platform Specifics**
  
  Ensure operations work correctly on:
  * Windows
  * macOS
  * Linux
