"""
Column Header Context Menu Integration Fix

This document describes the fix applied to the column header context menu functionality.

## Issue Description

When right-clicking on a column header and selecting the "Fit Content" option, the columns were not
automatically resizing to fit their content. 

## Root Cause

The `HeaderNavigationWidgetIntegration` class was missing a method to handle the resizing of columns
when the "Fit Content" option was toggled. Although the setting was being saved correctly, no actual
column resizing was happening.

## Fix Applied

Added the missing `_resize_columns_to_fit_content` method to the `HeaderNavigationWidgetIntegration` class
in `widgets/explorer_header_navigation_integration.py`:

```python
def _resize_columns_to_fit_content(self) -> None:
    """Resize all columns to fit their content."""
    # Get the tree view (parent)
    tree_view = self.parent()
    if not tree_view or not isinstance(tree_view, QTreeView):
        logger.warning("Cannot resize columns - parent is not a tree view")
        return
        
    # Resize each column
    for section in range(self.count()):
        tree_view.resizeColumnToContents(section)
        
    logger.debug(f"Resized {self.count()} columns to fit content")
```

Also updated the `_toggle_fit_content` method to call this new method when fit content is enabled:

```python
def _toggle_fit_content(self, enabled: bool) -> None:
    """
    Toggle fit content mode.
    
    Args:
        enabled: Whether fit content should be enabled
    """
    if not self._column_manager:
        return
        
    self._column_manager.set_fit_content_enabled(enabled)
    
    if enabled:
        # If enabled, resize columns to fit content now
        self._resize_columns_to_fit_content()
    
    logger.debug(f"Fit content {'enabled' if enabled else 'disabled'}")
```

## Testing

Created a test case (`tests/explorer/test_cases/column_header_fit_content_test.py`) that:
1. Creates a simple explorer widget with column menu
2. Toggles the fit content setting
3. Verifies that columns are properly resized

The test confirmed that the fix is working correctly.

## Additional Notes

- The setting was being saved correctly; it was just the actual resizing that wasn't happening.
- The same issue would affect manually resizing or reset column width functionality if they relied on this method.
