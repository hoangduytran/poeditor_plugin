# Explorer Context Menu Tests Documentation

**Date**: August 1, 2025  
**Component**: Explorer Context Menu  
**Status**: Implementation / Testing  
**Priority**: High

## Overview

This document describes the test suite for the Explorer Context Menu component implemented as part of the PySide6 POEditor plugin project. The tests validate that the context menu functionality works correctly when interacting with files and directories in the explorer panel.

## Test Structure

The test suite is designed to validate multiple aspects of the Explorer Context Menu:

1. **Selection Tests**
   - Single file selection
   - Multiple file selection
   - Directory selection
   - Mixed selection (files and directories)

2. **Menu Generation Tests**
   - Verify the correct menu items appear for different selection types
   - Check that menu item states (enabled/disabled) are correct based on context

3. **Operation Tests**
   - Copy operation
   - Cut operation
   - Paste operation
   - Delete operation
   - Rename operation

4. **Integration Tests**
   - File Operations Service integration
   - Undo/Redo Service integration
   - File Numbering Service integration

## Test Methodology

The tests use real components rather than mocks, following the project guidelines. This approach ensures that all components work together as expected in real-world scenarios.

Key methodology points:

- **File System Setup**: Creates a temporary directory structure with test files and directories
- **Component Initialization**: Initializes actual Explorer widget components
- **Event Simulation**: Uses QTest to simulate user interactions
- **Cleanup**: Ensures all temporary files are removed after tests

## Running the Tests

Execute the tests using the provided script:

```bash
./tests/run_tests.sh
```

This will run all UI tests and generate a log file with the results.

## Implementation Details

The test uses several helper methods:

- `_get_file_index()`: Retrieves model indexes for test files
- `_get_directory_index()`: Retrieves model indexes for test directories
- `_create_test_files()`: Creates temporary test files and directories
- `_clear_operations_log()`: Resets the operations tracking

## Expected Results

All tests should pass, indicating that:

1. The Explorer Context Menu correctly displays appropriate menu items based on selection
2. File operations (copy, cut, paste, delete, rename) function correctly
3. Context menu integration with services is working as expected

## Future Test Enhancements

Planned enhancements to the test suite include:

1. Performance testing for operations on large file sets
2. Additional edge cases (read-only files, special characters in filenames)
3. Integration with the main application window
4. Keyboard shortcut testing for context menu operations
