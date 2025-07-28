===============================
Explorer Context Menu Reference
===============================

Overview
========

The Explorer Context Menu provides a convenient way to perform common operations on files and folders directly in the POEditor interface. With Phase 4 enhancements, it now includes full accessibility support, advanced keyboard navigation, and theme integration.

.. contents:: Table of Contents
   :depth: 2
   :local:

Features
========

The Explorer Context Menu offers different options depending on the selection context:

Selection-Based Menus
--------------------

* **File Selection**
  
  When one or more files are selected, the following options are available:
  
  * **Open** - Opens the file with its default application
  * **Open With...** - Choose which application to use to open the file
  * **Cut** - Mark files for moving to another location (Ctrl+X)
  * **Copy** - Copy files to clipboard (Ctrl+C)
  * **Paste** - Only available when pasting into a folder (Ctrl+V)
  * **Duplicate** - Create a copy in the same location (Ctrl+D)
  * **Rename** - Only for single file selection (F2)
  * **Delete** - Move to trash with confirmation (Delete key)
  
* **Folder Selection**
  
  When one or more folders are selected, the following options are available:
  
  * **Open** - Navigate to the folder in Explorer
  * **Open in New Window** - Open folder in a separate window
  * **Cut/Copy/Paste** - Similar to file operations
  * **Open Terminal Here** - Launch terminal at this location
  * **Find in Folder** - Search for files within selected folder
  
* **Background (No Selection)**
  
  When clicking on empty space in the explorer, these options appear:
  
  * **New File** - Create a new empty file (Ctrl+N)
  * **New Folder** - Create a new directory (Ctrl+Shift+N)
  * **Paste** - Available when clipboard has files/folders
  * **Open Terminal Here** - Open terminal in current directory
  * **Refresh** - Update the directory listing

Key Operations
=============

Refresh Operation
----------------

The Refresh operation updates the file listing to reflect the current state of the file system.

When to use:
  * After files have been added/removed by external applications
  * When the Explorer view appears out of sync with the file system
  * After performing operations that might change directory contents

How it works:
  * Right-click on empty space in Explorer
  * Select "Refresh" from the context menu
  * The view will update to show the latest files and directories

File Operations
--------------

Cut, Copy and Paste
~~~~~~~~~~~~~~~~~~

These operations allow moving and copying files between locations:

1. **Cut**: Marks files for moving
   * Select one or more files/folders
   * Right-click and select "Cut" (or press Ctrl+X)
   * Files will be moved when you paste

2. **Copy**: Copies files to clipboard
   * Select one or more files/folders
   * Right-click and select "Copy" (or press Ctrl+C)
   * Files will be duplicated when you paste

3. **Paste**: Places files from clipboard
   * Navigate to destination location
   * Right-click and select "Paste" (or press Ctrl+V)
   * Files will appear in the new location

Delete Operation
~~~~~~~~~~~~~~

Safely removes files with a confirmation prompt:

1. Select one or more files/folders
2. Right-click and select "Delete" (or press Del key)
3. Confirm deletion when prompted
4. Files are moved to trash/recycle bin

Integration Features
==================

Terminal Integration
------------------

Open a terminal window at the current location:

* For directories: Right-click folder and select "Open Terminal Here"
* For background: Right-click empty space and select "Open Terminal Here"

The terminal type depends on your operating system:
  * **Windows**: Opens Command Prompt
  * **macOS**: Opens Terminal app
  * **Linux**: Opens default terminal emulator

File Properties
-------------

View detailed information about files and folders:

* Select one or more items
* Right-click and select "Properties"
* View information such as:
  * Size and creation date
  * Permissions
  * Type and location
  * Custom metadata (when available)

Configuration
===========

The context menu behavior can be customized through the application settings:

* **Menu Style**: Standard or compact
* **Default Actions**: Configure primary actions
* **Custom Commands**: Add your own menu items
* **Keyboard Shortcuts**: Customize shortcut keys

See the :ref:`application_settings` section for details on configuring these options.

Keyboard Shortcuts
================

The context menu fully supports keyboard navigation and shortcuts:

+-------------------+-----------------+---------------------------+
| Shortcut          | Menu Equivalent | Description               |
+===================+=================+===========================+
| Ctrl+X            | Cut             | Cut selected files        |
+-------------------+-----------------+---------------------------+
| Ctrl+C            | Copy            | Copy selected files       |
+-------------------+-----------------+---------------------------+
| Ctrl+V            | Paste           | Paste from clipboard      |
+-------------------+-----------------+---------------------------+
| Ctrl+D            | Duplicate       | Duplicate selected files  |
+-------------------+-----------------+---------------------------+
| F2                | Rename          | Rename selected item      |
+-------------------+-----------------+---------------------------+
| Delete            | Delete          | Move to trash             |
+-------------------+-----------------+---------------------------+
| Ctrl+N            | New File        | Create new file           |
+-------------------+-----------------+---------------------------+
| Ctrl+Shift+N      | New Folder      | Create new folder         |
+-------------------+-----------------+---------------------------+
| F5                | Refresh         | Update directory listing  |
+-------------------+-----------------+---------------------------+

Advanced Keyboard Navigation
==========================

The context menu supports advanced keyboard navigation features:

Arrow Key Navigation
------------------

* **Up/Down Arrows**: Navigate between menu items
* **Enter/Space**: Activate the selected menu item
* **Escape**: Close the menu

First-Letter Navigation
---------------------

Type the first letter of a menu item to quickly jump to it:

* Type **"c"** to jump to "Copy"
* Type **"n"** to jump to "New File" or "New Folder"
* Type **"d"** to jump to "Delete" or "Duplicate"

This feature works even when multiple items start with the same letter - continued typing will cycle through them.

Accessibility Features
====================

The Explorer Context Menu is fully accessible with screen reader support:

Screen Reader Support
--------------------

* **ARIA Labels**: All menu items have descriptive labels for screen readers
* **Operation Announcements**: Screen readers announce the results of operations like "Cut 3 items" or "Copied 1 file"
* **Status Updates**: Users are informed when operations complete or fail

Focus Management
--------------

* **Focus Tracking**: The menu remembers which widget had focus before opening
* **Focus Restoration**: When the menu closes, focus returns to the original widget
* **Keyboard Focus**: Clear visual indicators show which menu item is selected

Visual Accessibility
------------------

* **High Contrast**: Menu items maintain proper color contrast
* **Clear Visual Focus**: Selected items are clearly highlighted
* **Theme Integration**: Menu appearance adapts to application themes

Troubleshooting
=============

Common Issues
-----------

* **Menu items are disabled**
  
  This usually indicates that the operation is not valid for the current selection.
  For example, "Rename" is only available for single-item selections.

* **Paste option not available**
  
  Make sure you have previously copied or cut files to the clipboard.
  The paste option only appears when clipboard contains valid file data.

* **Operations fail silently**
  
  Check the application log for error messages. Most operations will log errors
  when they encounter problems.
