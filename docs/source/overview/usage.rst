Usage
=====

Getting Started
-------------

After launching the POEditor Plugin application, you'll see the main interface with several components:

* **Activity Bar**: Left sidebar with icons for different activities
* **Side Panel**: Shows content for the selected activity
* **Main Area**: Central workspace area

Basic Navigation
--------------

1. **Switching Activities**:
   
   Click on icons in the Activity Bar to switch between different activities:
   
   * Explorer: File navigation and management
   * Search: Find text across files
   * Account: User account settings
   * Extensions: Browse and manage extensions
   * Preferences: Application settings

2. **File Operations**:
   
   In the Explorer activity:
   
   * Navigate directories in the file tree
   * Filter files using the search bar at the top
   * Clear filters with the clear button (✕) to restore all files
   * Right-click files for a context menu with operations:
     - Copy
     - Cut
     - Paste
     - Delete
     - Rename
     - Duplicate
   * Use drag and drop for file movement

3. **Undo/Redo Operations**:
   
   * Use Ctrl+Z (Cmd+Z on Mac) to undo operations
   * Use Ctrl+Y (Cmd+Shift+Z on Mac) to redo operations

4. **Keyboard Shortcuts**:
   
   * Ctrl+C: Copy selected files
   * Ctrl+X: Cut selected files
   * Ctrl+V: Paste files
   * Delete: Delete selected files
   * F2: Rename selected file

File Filtering and Search
-----------------------

The Explorer provides powerful filtering capabilities to help you find files quickly:

1. **Filter Bar**:
   
   * Type in the filter box at the top of the Explorer to filter files by name
   * Filtering is case-insensitive and uses partial matching
   * Directories are always shown first, even when filtering

2. **Clear Button**:
   
   * A clear button (✕) appears when you have entered filter text
   * Click the clear button to instantly remove the filter and show all files
   * The button is automatically enabled/disabled based on filter text

3. **Filter Modes**:
   
   * Right-click the filter bar to access different filter modes:
     - **Filter Files**: Show/hide files based on name patterns (default)
     - **Search Text In Files**: Search file contents (future feature)

4. **Filter Examples**:
   
   * Type "test" to show files containing "test" in their name
   * Type ".py" to show Python files
   * Type "README" to find readme files

Working with Translations
-----------------------

1. **Opening Translation Files**:
   
   * Navigate to a .po file in the Explorer
   * Double-click to open in the editor

2. **Editing Translations**:
   
   * Browse through translation entries
   * Edit the target language text
   * Save changes with Ctrl+S

3. **Search Functionality**:
   
   * Click the Search icon in the Activity Bar
   * Enter text to search across translation files
   * Click on search results to navigate to specific entries

4. **Translation Memory**:
   
   * Previous translations are suggested as you type
   * Access the translation history for each entry

Customizing the Interface
----------------------

1. **Changing Themes**:
   
   * Go to Preferences activity
   * Select Appearance
   * Choose between Light or Dark theme
   * Apply custom themes if available

2. **Panel Layout**:
   
   * Resize panels by dragging the dividers
   * Some panels can be detached into separate windows

3. **Application Settings**:
   
   * Go to Preferences activity
   * Configure various application options
   * Changes are applied immediately

Plugin Management
--------------

1. **Browsing Available Plugins**:
   
   * Go to Extensions activity
   * Browse available plugins
   * Click on plugins to see details

2. **Installing Plugins**:
   
   * Click "Install" on plugin cards
   * Follow any additional setup instructions
   * Restart the application if required

3. **Managing Plugins**:
   
   * Enable/disable installed plugins
   * Configure plugin settings
   * Uninstall plugins when no longer needed

Troubleshooting
-------------

If you encounter issues:

1. Check the application log file (application.log)
2. Ensure all dependencies are correctly installed
3. Try restarting the application
4. Check for configuration issues in the preferences
