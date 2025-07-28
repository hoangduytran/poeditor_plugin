=================================
Explorer Context Menu Development
=================================

This document provides technical details for developers working with the Explorer Context Menu system in POEditor.

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
  * Handling menu actions
  * Emitting signals for parent components
  * Integrating with file operation services

* **EnhancedFileView**
  
  A view component that:
  
  * Displays files and directories in a tree view
  * Handles context menu requests
  * Responds to selection changes
  * Manages drag-and-drop operations

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
