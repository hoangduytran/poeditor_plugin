# Explorer Header Navigation Test Cases

This directory contains test cases and demos for the Phase 3 Enhanced Context Menu System implementation.

## Files Overview

### Demos
- **`header_navigation_demo.py`** - Complete integration demo showing the HeaderNavigationWidget with enhanced context menu
- **`phase3_feature_demo.py`** - Focused demo for testing individual Phase 3 features (Go to Path, Bookmark Manager)
- **`main_with_navigation.py`** - Alternative integration demo with navigation services

### Tests
- **`test_header_navigation.py`** - Unit test for HeaderNavigationWidget functionality

### Integration Examples
- **`integration_example.py`** - Code example showing how to integrate navigation widgets
- **`integration_guide.py`** - Detailed integration guide and examples

## Running the Demos

From the project root directory:

```bash
# Complete navigation demo with context menu
python tests/explorer/test_cases/header_navigation_demo.py

# Phase 3 feature testing
python tests/explorer/test_cases/phase3_feature_demo.py

# Alternative navigation demo
python tests/explorer/test_cases/main_with_navigation.py

# Unit tests
python tests/explorer/test_cases/test_header_navigation.py
```

## Phase 3 Features

The demos showcase the completed Phase 3 Enhanced Context Menu System:

1. **Navigation Actions Submenu**
   - Go to Path (Ctrl+G) - with auto-completion
   - Navigate Back/Forward
   - Recent Locations
   - Quick Locations
   - Bookmark Manager

2. **Column Management Submenu**
   - Show/Hide columns
   - Resize options
   - Sort controls

3. **Enhanced Context Menu Structure**
   - Organized sections with separators
   - 22+ total actions across 8 sections
   - Professional layout with icons and shortcuts

## Dependencies

All test files correctly resolve import paths to access:
- `services.navigation_service`
- `services.navigation_history_service` 
- `services.location_manager`
- `services.path_completion_service`
- `widgets.explorer.explorer_header_bar`
- Other project modules

The path resolution uses `Path(__file__).parents[3]` to correctly navigate from `tests/explorer/test_cases/` to the project root.
