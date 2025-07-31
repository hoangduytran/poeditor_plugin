"""
# Column Header Context Menu Technical Implementation Guide

## Overview

This technical guide provides specific implementation steps to integrate the column header context menu functionality in the Explorer panel, focusing on column management capabilities while preserving existing navigation features.

## Implementation Components

### 1. Create the Column Manager Service

First, we need to implement a service to handle column-related operations:

```python
# services/column_manager_service.py
from typing import Dict, List, Tuple, Optional, Any
from core.explorer_settings import ExplorerSettings
from lg import logger

class ColumnManagerService:
    """Service for managing explorer columns visibility and properties."""
    
    def __init__(self):
        self.settings = ExplorerSettings()
        self._initialize_columns()
        
    def _initialize_columns(self) -> None:
        """Initialize column definitions and load settings."""
        # Define available columns with their properties
        self._columns = {
            "name": {
                "display": "Name",
                "required": True,
                "default_width": 250,
                "model_column": 0
            },
            "size": {
                "display": "Size",
                "required": False,
                "default_width": 100,
                "model_column": 1
            },
            "type": {
                "display": "Type",
                "required": False,
                "default_width": 120,
                "model_column": 2
            },
            "modified": {
                "display": "Modified Date",
                "required": False,
                "default_width": 180,
                "model_column": 3
            }
        }
        
        # Load visibility settings or use defaults
        self._visible_columns = self.settings.get(
            "explorer_visible_columns", 
            ["name", "size", "type", "modified"]
        )
        
        # Ensure required columns are always visible
        for col_id, col_info in self._columns.items():
            if col_info.get("required", False) and col_id not in self._visible_columns:
                self._visible_columns.append(col_id)
                
        # Load content fitting setting
        self._fit_content = self.settings.get("explorer_fit_column_content", False)
        
        # Load custom column widths
        self._column_widths = self.settings.get("explorer_column_widths", {})
        
        logger.debug(f"Column manager initialized with {len(self._visible_columns)} visible columns")
        
    def get_available_columns(self) -> Dict[str, Dict[str, Any]]:
        """Get dictionary of all available columns with their properties."""
        return self._columns
        
    def get_column_info(self, column_id: str) -> Dict[str, Any]:
        """Get information about a specific column."""
        return self._columns.get(column_id, {})
        
    def get_visible_columns(self) -> List[str]:
        """Get list of visible column IDs."""
        return self._visible_columns.copy()
        
    def is_column_visible(self, column_id: str) -> bool:
        """Check if a column is currently visible."""
        return column_id in self._visible_columns
        
    def set_column_visibility(self, column_id: str, visible: bool) -> bool:
        """
        Set column visibility.
        
        Args:
            column_id: The column identifier
            visible: Whether the column should be visible
            
        Returns:
            bool: True if visibility was changed, False otherwise
        """
        # Check if column exists
        if column_id not in self._columns:
            logger.warning(f"Cannot set visibility for unknown column: {column_id}")
            return False
            
        # Check if column is required
        if self._columns[column_id].get("required", False) and not visible:
            logger.warning(f"Cannot hide required column: {column_id}")
            return False
            
        # Update visibility
        was_visible = column_id in self._visible_columns
        
        if visible and not was_visible:
            self._visible_columns.append(column_id)
            self._save_visible_columns()
            return True
        elif not visible and was_visible:
            self._visible_columns.remove(column_id)
            self._save_visible_columns()
            return True
            
        return False
        
    def _save_visible_columns(self) -> None:
        """Save visible columns to settings."""
        self.settings.set("explorer_visible_columns", self._visible_columns)
        
    def get_fit_content_enabled(self) -> bool:
        """Check if fit content to values is enabled."""
        return self._fit_content
        
    def set_fit_content_enabled(self, enabled: bool) -> None:
        """Set fit content to values setting."""
        self._fit_content = enabled
        self.settings.set("explorer_fit_column_content", enabled)
        
    def get_column_width(self, column_id: str) -> int:
        """Get column width (custom or default)."""
        if column_id in self._column_widths:
            return self._column_widths[column_id]
        return self._columns.get(column_id, {}).get("default_width", 100)
        
    def set_column_width(self, column_id: str, width: int) -> None:
        """Save custom column width."""
        self._column_widths[column_id] = width
        self.settings.set("explorer_column_widths", self._column_widths)
        
    def reset_column_widths(self) -> None:
        """Reset all column widths to defaults."""
        self._column_widths = {}
        self.settings.set("explorer_column_widths", {})
        
    def get_model_column(self, column_id: str) -> int:
        """Get the model column index for the given column ID."""
        return self._columns.get(column_id, {}).get("model_column", 0)
```

### 2. Update HeaderNavigationWidget

Extend the existing `HeaderNavigationWidget` to include column management functionality:

```python
# widgets/explorer/explorer_header_bar.py

from services.column_manager_service import ColumnManagerService

class HeaderNavigationWidget(QHeaderView):
    # Existing code...
    
    def inject_services(
        self,
        navigation_service: NavigationService,
        history_service: NavigationHistoryService,
        location_manager: LocationManager,
        completion_service: PathCompletionService,
        column_manager: Optional[ColumnManagerService] = None
    ) -> None:
        """
        Inject services into the header.
        
        Args:
            navigation_service: Core navigation service
            history_service: Navigation history service
            location_manager: Location and bookmark manager
            completion_service: Path completion service
            column_manager: Column management service
        """
        self._navigation_service = navigation_service
        self._history_service = history_service
        self._location_manager = location_manager
        self._completion_service = completion_service
        self._column_manager = column_manager
        
        # Connect to navigation service signals
        if self._navigation_service:
            self._navigation_service.current_path_changed.connect(self._on_path_changed)
            
    def _populate_navigation_menu(self, menu: QMenu) -> None:
        """
        Populate the navigation context menu with actions.
        
        Args:
            menu: The menu to populate
        """
        logger.info("Populating navigation menu")
        
        # Column Management Section (Phase 4 implementation)
        if self._column_manager:
            self._add_column_management_section(menu)
            menu.addSeparator()
            
        # Current path section
        current_path = self._get_current_path()
        logger.info(f"Current path: {current_path}")
        if current_path:
            path_action = QAction(f"📁 {current_path}", self)
            path_action.setEnabled(False)  # Just for display
            menu.addAction(path_action)
            menu.addSeparator()
            
        # Navigation actions
        logger.info("Adding navigation actions")
        self._add_navigation_actions(menu)
        menu.addSeparator()
        
        # Rest of existing navigation menu implementation...
        
    def _add_column_management_section(self, menu: QMenu) -> None:
        """
        Add column management section to the context menu.
        
        Args:
            menu: The menu to add the section to
        """
        if not self._column_manager:
            return
            
        # Create submenu for column management
        columns_menu = menu.addMenu("📊 Column Management")
        
        # Add column visibility options
        available_columns = self._column_manager.get_available_columns()
        for col_id, col_info in available_columns.items():
            action = QAction(col_info["display"], self)
            action.setCheckable(True)
            action.setChecked(self._column_manager.is_column_visible(col_id))
            
            # Disable toggling for required columns
            if col_info.get("required", False):
                action.setToolTip("This column cannot be hidden")
                # Keep it enabled for consistent UX, but it won't actually hide
                # when clicked due to logic in column manager service
                
            # Connect action
            action.triggered.connect(
                lambda checked, c_id=col_id: self._toggle_column_visibility(c_id, checked)
            )
            
            columns_menu.addAction(action)
            
        # Add separator
        columns_menu.addSeparator()
        
        # Add fit content option
        fit_action = QAction("Fit Content to Values", self)
        fit_action.setCheckable(True)
        fit_action.setChecked(self._column_manager.get_fit_content_enabled())
        fit_action.triggered.connect(self._toggle_fit_content)
        fit_action.setToolTip("Automatically resize columns to fit their content")
        columns_menu.addAction(fit_action)
        
        # Add reset widths option
        reset_action = QAction("Reset Column Widths", self)
        reset_action.setToolTip("Reset all columns to their default widths")
        reset_action.triggered.connect(self._reset_column_widths)
        columns_menu.addAction(reset_action)
        
        logger.debug("Column management section added to context menu")
        
    def _toggle_column_visibility(self, column_id: str, visible: bool) -> None:
        """
        Toggle column visibility.
        
        Args:
            column_id: Column identifier
            visible: New visibility state
        """
        if not self._column_manager:
            return
            
        # Try to update visibility (this may fail for required columns)
        changed = self._column_manager.set_column_visibility(column_id, visible)
        
        if changed:
            # Update column visibility in the view
            self._update_column_visibility()
            logger.debug(f"Column '{column_id}' visibility changed to: {visible}")
            
    def _update_column_visibility(self) -> None:
        """Update column visibility in the view based on settings."""
        if not self._column_manager:
            return
            
        # Get visible column IDs
        visible_columns = self._column_manager.get_visible_columns()
        
        # Update column visibility in the header
        for col_id, col_info in self._column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns
            
            if visible:
                self.parent().showSection(model_column)
            else:
                self.parent().hideSection(model_column)
                
        logger.debug(f"Updated column visibility: {visible_columns}")
        
    def _toggle_fit_content(self, enabled: bool) -> None:
        """
        Toggle fit content setting.
        
        Args:
            enabled: Whether content fitting should be enabled
        """
        if not self._column_manager:
            return
            
        self._column_manager.set_fit_content_enabled(enabled)
        
        if enabled:
            # Resize columns to fit content
            self._resize_columns_to_fit_content()
        else:
            # Restore saved column widths
            self._restore_saved_column_widths()
            
        logger.debug(f"Fit content setting changed to: {enabled}")
        
    def _resize_columns_to_fit_content(self) -> None:
        """Resize all columns to fit their content."""
        # Implementation note: We use the parent() here which is the QTreeView
        if self.parent():
            self.parent().resizeColumnsToContents()
            logger.debug("Resized columns to fit content")
            
    def _restore_saved_column_widths(self) -> None:
        """Restore saved column widths."""
        if not self._column_manager or not self.parent():
            return
            
        # Apply saved widths for each column
        for col_id, col_info in self._column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            width = self._column_manager.get_column_width(col_id)
            self.parent().setColumnWidth(model_column, width)
            
        logger.debug("Restored saved column widths")
        
    def _reset_column_widths(self) -> None:
        """Reset all column widths to defaults."""
        if not self._column_manager:
            return
            
        # Reset widths in the manager
        self._column_manager.reset_column_widths()
        
        # Apply default widths
        for col_id, col_info in self._column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            default_width = col_info.get("default_width", 100)
            
            if self.parent():
                self.parent().setColumnWidth(model_column, default_width)
                
        logger.debug("Reset column widths to defaults")
        
    def handle_section_resize(self, logical_index: int, old_size: int, new_size: int) -> None:
        """
        Handle column resizing to save custom widths.
        
        Args:
            logical_index: Index of the resized section
            old_size: Old section size
            new_size: New section size
        """
        if not self._column_manager:
            return
            
        # Find column ID for the logical index
        for col_id, col_info in self._column_manager.get_available_columns().items():
            if col_info.get("model_column", 0) == logical_index:
                # Save the new width
                self._column_manager.set_column_width(col_id, new_size)
                logger.debug(f"Saved custom width for column '{col_id}': {new_size}px")
                break

    # Connect to sectionResized signal in __init__ or after services are injected
    def _connect_section_resize_signal(self) -> None:
        """Connect to sectionResized signal to track column width changes."""
        self.sectionResized.connect(self.handle_section_resize)
```

### 3. Update Enhanced File View

Update the file view to handle column management:

```python
# widgets/enhanced_file_view.py

# Add to import section
from services.column_manager_service import ColumnManagerService

class EnhancedFileView(SimpleFileView):
    # Existing code...
    
    def setup_context_menu(self, file_operations_service: FileOperationsService, 
                         undo_redo_manager: UndoRedoManager,
                         column_manager: Optional[ColumnManagerService] = None):
        """
        Set up the context menu manager and services.
        
        Args:
            file_operations_service: Service for file operations
            undo_redo_manager: Manager for undo/redo operations
            column_manager: Column management service
        """
        self.file_operations_service = file_operations_service
        self.undo_redo_manager = undo_redo_manager
        self.column_manager = column_manager
        
        # Create context menu manager
        self.context_menu_manager = ExplorerContextMenu(
            file_operations_service, 
            undo_redo_manager
        )
        
        # Create drag and drop service
        self.drag_drop_service = DragDropService(file_operations_service)
        
        # Connect context menu signal
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Connect context menu signals
        self.context_menu_manager.show_properties.connect(self._show_properties)
        self.context_menu_manager.show_open_with.connect(self._show_open_with)
        self.context_menu_manager.refresh_requested.connect(self._refresh_view)
        
        # Set up header with column manager
        header = self.header()
        if isinstance(header, HeaderNavigationWidget) and self.column_manager:
            # Inject column manager into header
            header.inject_column_manager(self.column_manager)
            
            # Apply initial column visibility and widths
            self._apply_initial_column_settings()
            
    def _apply_initial_column_settings(self) -> None:
        """Apply initial column settings from the column manager."""
        if not self.column_manager:
            return
            
        # Get visible columns
        visible_columns = self.column_manager.get_visible_columns()
        
        # Show/hide columns based on settings
        for col_id, col_info in self.column_manager.get_available_columns().items():
            model_column = col_info.get("model_column", 0)
            visible = col_id in visible_columns
            
            if visible:
                self.showColumn(model_column)
            else:
                self.hideColumn(model_column)
                
        # Apply column widths
        if self.column_manager.get_fit_content_enabled():
            # If fit content is enabled, resize columns to fit content
            self.resizeColumnsToContents()
        else:
            # Otherwise apply saved/default widths
            for col_id, col_info in self.column_manager.get_available_columns().items():
                model_column = col_info.get("model_column", 0)
                width = self.column_manager.get_column_width(col_id)
                self.setColumnWidth(model_column, width)
                
        logger.debug("Applied initial column settings")
```

### 4. Update Enhanced Explorer Widget

Update the main explorer widget to create and use the column manager service:

```python
# widgets/enhanced_explorer_widget.py

# Add to imports
from services.column_manager_service import ColumnManagerService

class EnhancedExplorerWidget(QWidget):
    # Existing code...
    
    def _create_services(self):
        """Create and initialize the required services."""
        # Existing services...
        
        # Create column manager service
        self.column_manager_service = ColumnManagerService()
        
        logger.debug("Explorer services initialized")
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Existing setup code...
        
        # Set up context menu with column manager
        self.file_view.setup_context_menu(
            self.file_operations_service,
            self.undo_redo_manager,
            self.column_manager_service
        )
```

### 5. Create or Update Header Navigation Widget

Ensure the HeaderNavigationWidget class supports injection of the column manager service:

```python
# widgets/explorer/explorer_header_bar.py

class HeaderNavigationWidget(QHeaderView):
    # Existing code...
    
    def inject_column_manager(self, column_manager: ColumnManagerService) -> None:
        """
        Inject column manager service.
        
        Args:
            column_manager: Column management service
        """
        self._column_manager = column_manager
        
        # Connect section resize signal
        self._connect_section_resize_signal()
        
        logger.debug("Column manager injected into header navigation widget")
```

## Integration Steps

1. **Create new column manager service** in the services directory
2. **Update HeaderNavigationWidget** to handle column management in context menu
3. **Update EnhancedFileView** to use column manager settings
4. **Update EnhancedExplorerWidget** to create and pass the column manager service

## Testing Strategy

1. **Column Visibility Tests**
   - Test showing/hiding columns via context menu
   - Verify that required columns (Name) cannot be hidden
   - Check that column visibility persists between application restarts

2. **Content Fitting Tests**
   - Test enabling/disabling fit content option
   - Verify that columns resize properly when fit content is enabled
   - Check that custom widths are preserved when fit content is disabled

3. **Column Width Tests**
   - Test saving custom column widths
   - Verify that reset column widths restores default widths
   - Check that column widths persist between application restarts

4. **Integration Tests**
   - Test that column management and navigation functions coexist properly
   - Verify that all context menu features work as expected
   - Check that changing directories preserves column settings

## Code Sample: Column Manager Test

```python
# tests/explorer/test_cases/column_manager_test.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

# Add project root to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from services.column_manager_service import ColumnManagerService

class ColumnManagerTestWindow(QMainWindow):
    """Test window for column manager functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Column Manager Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create and set up the explorer widget
        self.explorer = EnhancedExplorerWidget()
        self.setCentralWidget(self.explorer)
        
        # Run test sequence after a short delay
        QTimer.singleShot(1000, self.run_test_sequence)
        
    def run_test_sequence(self):
        """Run a sequence of tests for column management."""
        logger.info("Starting column management test sequence")
        
        # Get column manager service
        column_manager = self.explorer.column_manager_service
        
        # Test 1: Print current column visibility
        logger.info(f"Initial visible columns: {column_manager.get_visible_columns()}")
        
        # Test 2: Hide the size column
        column_manager.set_column_visibility("size", False)
        logger.info(f"After hiding size: {column_manager.get_visible_columns()}")
        
        # Test 3: Toggle fit content
        logger.info(f"Initial fit content setting: {column_manager.get_fit_content_enabled()}")
        column_manager.set_fit_content_enabled(True)
        logger.info(f"After enabling fit content: {column_manager.get_fit_content_enabled()}")
        
        # Test 4: Reset column widths
        logger.info("Resetting column widths")
        column_manager.reset_column_widths()
        
        logger.info("Test sequence completed")

def main():
    app = QApplication(sys.argv)
    window = ColumnManagerTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```
"""
