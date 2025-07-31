"""
# Column Header Context Menu Integration for Explorer

## Overview

This document outlines the design for integrating column header context menu functionality in the Explorer panel. The implementation builds on the existing phase 1-3 foundations while adding specific column management capabilities requested in phase 4.

## Requirements

1. **Column Header Context Menu** - Implement right-click context menu on column headers (not within table view)
2. **Navigation Integration** - Maintain existing navigation functionality from previous phases
3. **Column Management** - Enable adding/removing columns via checkboxes in the context menu
4. **Default Columns** - Support the default 4 columns (Name, Size, Type, Modified Date)
5. **Content Fitting** - Add option to toggle automatic content fitting for columns
6. **Clean Integration** - Ensure the implementation respects existing functionality without duplication

## Design

### Component Structure

The column header context menu integration will build upon the existing `HeaderNavigationWidget` that already contains navigation functionality. We'll extend this implementation to add column management capabilities.

#### Class Extensions

1. **HeaderNavigationWidget** - Enhanced with column management capabilities
   - Add column visibility management methods
   - Add content fitting toggle functionality
   - Integrate checkbox menu items for column selection

2. **ColumnManager** (New Service) - Responsible for column management
   - Track available columns and their states
   - Handle column visibility changes
   - Manage column width settings and content fitting

3. **ColumnSettings** (New Model) - Store column configuration
   - Column identifiers and display names
   - Visibility status
   - Width settings
   - Content fitting preferences

### User Interface Design

The column header context menu will contain:

1. **Column Selection Section**
   - Checkbox items for each available column (Name, Size, Type, Modified Date)
   - Each column can be toggled on/off independently
   - "Name" column will be required and cannot be disabled

2. **Column Options Section**
   - "Fit Content" toggle option for automatic column width adjustment
   - "Reset Column Widths" to restore default widths

3. **Navigation Section** (Existing)
   - Maintain the existing navigation functionality

### Technical Implementation

#### Context Menu Structure

The context menu will be organized hierarchically:

```
[Column Management]
  ☑ Name Column
  ☑ Size Column
  ☑ Type Column
  ☑ Modified Date Column
  ─────────────────────
  ☑ Fit Content to Values
  → Reset Column Widths
[Navigation] (existing functionality)
  ...
```

#### Column Management Logic

1. **Column Toggling**
   - When a column checkbox is toggled, immediately update the view
   - Save state in the settings for persistence between sessions

2. **Content Fitting**
   - When enabled, automatically resize columns to fit their content
   - When disabled, columns maintain their manual or default widths

3. **Column Reset**
   - Restore all columns to their default widths
   - Maintain current visibility settings

### Integration with Existing Components

The implementation will extend the existing header navigation context menu rather than replacing it. This preserves all navigation functionality while adding column management capabilities.

## Implementation Plan

### 1. Update the `HeaderNavigationWidget` Class

Extend the existing `HeaderNavigationWidget` class to include column management:

```python
def _populate_navigation_menu(self, menu: QMenu) -> None:
    # Existing navigation menu population
    ...
    
    # Add column management section
    self._add_column_management_section(menu)
    
    ...

def _add_column_management_section(self, menu: QMenu) -> None:
    """Add column management section to the context menu."""
    # Create column management section
    columns_section = menu.addMenu("📊 Column Management")
    
    # Add column visibility checkboxes
    self._add_column_visibility_options(columns_section)
    
    # Add separator
    columns_section.addSeparator()
    
    # Add fit content option
    fit_action = QAction("Fit Content to Values", self)
    fit_action.setCheckable(True)
    fit_action.setChecked(self._get_fit_content_enabled())
    fit_action.triggered.connect(self._toggle_fit_content)
    columns_section.addAction(fit_action)
    
    # Add reset columns option
    reset_action = QAction("Reset Column Widths", self)
    reset_action.triggered.connect(self._reset_column_widths)
    columns_section.addAction(reset_action)
```

### 2. Create `ColumnManager` Service

Implement a service to manage column settings:

```python
class ColumnManager:
    """Service for managing column visibility and settings."""
    
    def __init__(self):
        self._settings = ExplorerSettings()
        self._available_columns = {
            "name": {"display": "Name", "required": True},
            "size": {"display": "Size", "required": False},
            "type": {"display": "Type", "required": False},
            "modified": {"display": "Modified Date", "required": False}
        }
        self._fit_content = self._settings.get("fit_column_content", False)
    
    def get_visible_columns(self) -> list:
        """Get list of currently visible columns."""
        visible = self._settings.get("visible_columns", ["name", "size", "type", "modified"])
        # Ensure name column is always included
        if "name" not in visible:
            visible.insert(0, "name")
        return visible
    
    def set_column_visibility(self, column_id: str, visible: bool) -> None:
        """Set column visibility."""
        current = self.get_visible_columns()
        
        if visible and column_id not in current:
            current.append(column_id)
        elif not visible and column_id in current and not self._is_required_column(column_id):
            current.remove(column_id)
            
        self._settings.set("visible_columns", current)
    
    def _is_required_column(self, column_id: str) -> bool:
        """Check if column is required."""
        column_info = self._available_columns.get(column_id, {})
        return column_info.get("required", False)
    
    def is_column_visible(self, column_id: str) -> bool:
        """Check if column is visible."""
        return column_id in self.get_visible_columns()
    
    def get_fit_content_enabled(self) -> bool:
        """Get whether fit content is enabled."""
        return self._fit_content
    
    def set_fit_content_enabled(self, enabled: bool) -> None:
        """Set whether fit content is enabled."""
        self._fit_content = enabled
        self._settings.set("fit_column_content", enabled)
```

### 3. Update Header View Implementation

Extend the header view to support column management:

```python
def _add_column_visibility_options(self, menu: QMenu) -> None:
    """Add column visibility checkboxes to the menu."""
    if not self._column_manager:
        return
        
    # Get available columns
    available_columns = self._column_manager.get_available_columns()
    
    # Add checkbox for each column
    for col_id, col_info in available_columns.items():
        action = QAction(col_info["display"], self)
        action.setCheckable(True)
        action.setChecked(self._column_manager.is_column_visible(col_id))
        
        # Disable toggling for required columns
        if col_info.get("required", False):
            action.setEnabled(False)
            
        # Connect action
        action.triggered.connect(
            lambda checked, c=col_id: self._toggle_column_visibility(c, checked)
        )
        
        menu.addAction(action)

def _toggle_column_visibility(self, column_id: str, visible: bool) -> None:
    """Toggle column visibility."""
    if self._column_manager:
        self._column_manager.set_column_visibility(column_id, visible)
        self._update_column_visibility()

def _toggle_fit_content(self, enabled: bool) -> None:
    """Toggle fit content setting."""
    if self._column_manager:
        self._column_manager.set_fit_content_enabled(enabled)
        self._update_column_fitting()

def _reset_column_widths(self) -> None:
    """Reset column widths to defaults."""
    # Implementation will reset column widths but maintain visibility
    header = self.parent()
    if header:
        for i in range(header.count()):
            header.resizeSection(i, header.defaultSectionSize())
```

### 4. Integration with File View

Update the file view to properly handle column changes:

```python
def _update_column_visibility(self) -> None:
    """Update column visibility based on settings."""
    if not self._column_manager:
        return
        
    visible_columns = self._column_manager.get_visible_columns()
    
    # Show/hide columns based on settings
    for i in range(self.model().columnCount()):
        column_id = self._get_column_id(i)
        visible = column_id in visible_columns
        if visible:
            self.showColumn(i)
        else:
            self.hideColumn(i)
            
def _update_column_fitting(self) -> None:
    """Update column fitting based on settings."""
    if not self._column_manager:
        return
        
    fit_enabled = self._column_manager.get_fit_content_enabled()
    
    if fit_enabled:
        # Resize columns to fit content
        self.resizeColumnsToContents()
    else:
        # Restore saved widths or defaults
        self._restore_column_widths()
```

## UI/UX Considerations

1. **Usability**
   - Column checkboxes provide immediate visual feedback when toggled
   - Fit Content option visibly resizes columns when enabled
   - Required columns are disabled to prevent accidental removal

2. **Visual Design**
   - Consistent with existing context menu styling
   - Clear grouping of related options
   - Uses checkboxes for boolean state options

3. **Responsiveness**
   - Column visibility changes take effect immediately
   - Column width adjustments are applied in real-time

## Persistence

Column settings will be persisted using the existing `ExplorerSettings` class:

- Visible columns list
- Content fitting preference
- Custom column widths

## Testing

1. **Column Visibility**
   - Verify columns can be shown/hidden via the context menu
   - Ensure required columns cannot be hidden

2. **Content Fitting**
   - Test that enabling fit content properly resizes columns
   - Verify that disabling fit content maintains manual column widths

3. **Navigation Integration**
   - Ensure existing navigation functionality remains intact
   - Verify no conflicts between navigation and column management

4. **Persistence**
   - Check that column settings persist between application sessions

## Conclusion

This design provides a complete solution for integrating column header context menu functionality in the Explorer panel, with both navigation and column management capabilities. The implementation builds upon existing foundations while adding the specific requirements for phase 4 column management.
"""
