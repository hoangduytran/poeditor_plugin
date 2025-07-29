# Column Management System Design

**Date**: July 29, 2025, 08:30  
**Component**: Column Management System  
**Status**: Technical Design  
**Priority**: High

## Overview

This document defines the Column Management System for the Explorer Header Navigation, providing comprehensive column configuration, display management, and user customization capabilities for the file explorer interface.

## System Architecture

### Core Components

```
Column Management System
├── ColumnConfigurationService     # Core column configuration logic
├── ColumnDefinitionRegistry      # Available column types registry
├── ColumnLayoutManager          # Layout and positioning logic
├── ColumnManagerDialog          # UI for column management
├── ColumnHeaderWidget          # Enhanced column headers
└── ColumnPersistenceManager    # Settings persistence
```

## 1. ColumnConfigurationService

### 1.1 Core Configuration Service

```python
from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import json
from pathlib import Path

class ColumnAlignment(Enum):
    """Column text alignment options."""
    LEFT = "left"
    CENTER = "center" 
    RIGHT = "right"

class ColumnDataType(Enum):
    """Column data type for formatting."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    SIZE = "size"
    BOOLEAN = "boolean"

@dataclass
class ColumnDefinition:
    """Complete definition of a column."""
    id: str
    display_name: str
    description: str
    data_type: ColumnDataType
    can_hide: bool = True
    can_resize: bool = True
    can_sort: bool = True
    default_visible: bool = True
    default_width: int = 120
    min_width: int = 50
    max_width: int = 500
    alignment: ColumnAlignment = ColumnAlignment.LEFT
    format_function: Optional[Callable] = None
    icon: Optional[str] = None
    category: str = "General"
    sort_priority: int = 0  # For default sort order

@dataclass
class ColumnState:
    """Current state of a column in the display."""
    column_id: str
    visible: bool
    width: int
    position: int  # Display position (0-based)
    sort_order: Optional[str] = None  # 'asc', 'desc', or None

class ColumnConfigurationService(QObject):
    """
    Service for managing column configurations and display settings.
    """
    
    # Signals
    column_visibility_changed = Signal(str, bool)  # column_id, visible
    column_width_changed = Signal(str, int)  # column_id, width
    column_position_changed = Signal(str, int)  # column_id, position
    column_configuration_reset = Signal()
    columns_reordered = Signal(list)  # new order list
    
    def __init__(self):
        super().__init__()
        self._column_definitions = {}
        self._column_states = {}
        self._settings_file = Path.home() / ".poeditor_columns.json"
        
        # Initialize with default columns
        self._initialize_default_columns()
        self._load_configuration()
        
    def _initialize_default_columns(self):
        """Initialize default column definitions."""
        default_columns = [
            ColumnDefinition(
                id="name",
                display_name="Name",
                description="File or folder name",
                data_type=ColumnDataType.STRING,
                can_hide=False,  # Name column always visible
                default_width=200,
                min_width=100,
                max_width=400,
                icon="📄",
                category="Basic",
                sort_priority=1
            ),
            ColumnDefinition(
                id="size",
                display_name="Size", 
                description="File size in bytes",
                data_type=ColumnDataType.SIZE,
                default_visible=True,
                default_width=80,
                min_width=60,
                max_width=120,
                alignment=ColumnAlignment.RIGHT,
                format_function=self._format_size,
                icon="📏",
                category="Basic",
                sort_priority=2
            ),
            ColumnDefinition(
                id="modified",
                display_name="Modified",
                description="Last modification date",
                data_type=ColumnDataType.DATE,
                default_visible=True,
                default_width=140,
                min_width=100,
                max_width=200,
                format_function=self._format_date,
                icon="📅",
                category="Basic",
                sort_priority=3
            ),
            ColumnDefinition(
                id="type",
                display_name="Type",
                description="File type or extension",
                data_type=ColumnDataType.STRING,
                default_visible=True,
                default_width=100,
                min_width=80,
                max_width=150,
                icon="🏷️",
                category="Basic",
                sort_priority=4
            ),
            ColumnDefinition(
                id="created",
                display_name="Created",
                description="Creation date",
                data_type=ColumnDataType.DATE,
                default_visible=False,
                default_width=140,
                min_width=100,
                max_width=200,
                format_function=self._format_date,
                icon="🆕",
                category="Extended"
            ),
            ColumnDefinition(
                id="permissions",
                display_name="Permissions",
                description="File permissions",
                data_type=ColumnDataType.STRING,
                default_visible=False,
                default_width=100,
                min_width=80,
                max_width=120,
                format_function=self._format_permissions,
                icon="🔒",
                category="Extended"
            ),
            ColumnDefinition(
                id="owner",
                display_name="Owner",
                description="File owner",
                data_type=ColumnDataType.STRING,
                default_visible=False,
                default_width=100,
                min_width=80,
                max_width=150,
                icon="👤",
                category="Extended"
            ),
            ColumnDefinition(
                id="extension",
                display_name="Extension",
                description="File extension",
                data_type=ColumnDataType.STRING,
                default_visible=False,
                default_width=80,
                min_width=60,
                max_width=100,
                icon="📎",
                category="Extended"
            ),
            ColumnDefinition(
                id="path",
                display_name="Path",
                description="Full file path",
                data_type=ColumnDataType.STRING,
                default_visible=False,
                default_width=300,
                min_width=150,
                max_width=600,
                icon="🗂️",
                category="Extended"
            )
        ]
        
        for column in default_columns:
            self._column_definitions[column.id] = column
            
        # Initialize default states
        for column in default_columns:
            self._column_states[column.id] = ColumnState(
                column_id=column.id,
                visible=column.default_visible,
                width=column.default_width,
                position=column.sort_priority
            )
    
    # Column Definition Management
    def get_all_column_definitions(self) -> List[ColumnDefinition]:
        """Get all available column definitions."""
        return list(self._column_definitions.values())
        
    def get_column_definition(self, column_id: str) -> Optional[ColumnDefinition]:
        """Get definition for a specific column."""
        return self._column_definitions.get(column_id)
        
    def register_column_definition(self, column_def: ColumnDefinition):
        """Register a new column definition (for plugins)."""
        self._column_definitions[column_def.id] = column_def
        
        # Create default state if not exists
        if column_def.id not in self._column_states:
            self._column_states[column_def.id] = ColumnState(
                column_id=column_def.id,
                visible=column_def.default_visible,
                width=column_def.default_width,
                position=len(self._column_states)
            )
            
    def unregister_column_definition(self, column_id: str) -> bool:
        """Unregister a column definition."""
        if column_id in self._column_definitions and self._column_definitions[column_id].can_hide:
            del self._column_definitions[column_id]
            self._column_states.pop(column_id, None)
            return True
        return False
        
    # Column State Management
    def get_visible_columns(self) -> List[ColumnDefinition]:
        """Get currently visible columns in display order."""
        visible_states = [
            state for state in self._column_states.values() 
            if state.visible
        ]
        
        # Sort by position
        visible_states.sort(key=lambda s: s.position)
        
        # Return corresponding definitions
        return [
            self._column_definitions[state.column_id]
            for state in visible_states
            if state.column_id in self._column_definitions
        ]
        
    def get_column_state(self, column_id: str) -> Optional[ColumnState]:
        """Get current state for a column."""
        return self._column_states.get(column_id)
        
    def set_column_visibility(self, column_id: str, visible: bool) -> bool:
        """Set column visibility."""
        if column_id not in self._column_definitions:
            return False
            
        column_def = self._column_definitions[column_id]
        if not visible and not column_def.can_hide:
            return False  # Cannot hide required columns
            
        if column_id in self._column_states:
            old_visible = self._column_states[column_id].visible
            self._column_states[column_id].visible = visible
            
            if old_visible != visible:
                self._save_configuration()
                self.column_visibility_changed.emit(column_id, visible)
                
            return True
        return False
        
    def set_column_width(self, column_id: str, width: int) -> bool:
        """Set column width."""
        if column_id not in self._column_definitions:
            return False
            
        column_def = self._column_definitions[column_id]
        if not column_def.can_resize:
            return False
            
        # Constrain width to valid range
        width = max(column_def.min_width, min(column_def.max_width, width))
        
        if column_id in self._column_states:
            old_width = self._column_states[column_id].width
            self._column_states[column_id].width = width
            
            if old_width != width:
                self._save_configuration()
                self.column_width_changed.emit(column_id, width)
                
            return True
        return False
        
    def set_column_position(self, column_id: str, position: int) -> bool:
        """Set column display position."""
        if column_id not in self._column_states:
            return False
            
        old_position = self._column_states[column_id].position
        self._column_states[column_id].position = position
        
        if old_position != position:
            self._save_configuration()
            self.column_position_changed.emit(column_id, position)
            
        return True
        
    def reorder_columns(self, column_order: List[str]) -> bool:
        """Reorder columns according to provided list."""
        # Validate all columns exist
        for column_id in column_order:
            if column_id not in self._column_states:
                return False
                
        # Update positions
        for i, column_id in enumerate(column_order):
            self._column_states[column_id].position = i
            
        self._save_configuration()
        self.columns_reordered.emit(column_order)
        return True
        
    # Bulk Operations
    def show_columns(self, column_ids: List[str]):
        """Show multiple columns."""
        for column_id in column_ids:
            self.set_column_visibility(column_id, True)
            
    def hide_columns(self, column_ids: List[str]):
        """Hide multiple columns."""
        for column_id in column_ids:
            self.set_column_visibility(column_id, False)
            
    def reset_column_widths(self):
        """Reset all column widths to defaults."""
        for column_id, column_def in self._column_definitions.items():
            if column_id in self._column_states:
                self._column_states[column_id].width = column_def.default_width
                
        self._save_configuration()
        
    def reset_to_defaults(self):
        """Reset all column settings to defaults."""
        for column_id, column_def in self._column_definitions.items():
            self._column_states[column_id] = ColumnState(
                column_id=column_id,
                visible=column_def.default_visible,
                width=column_def.default_width,
                position=column_def.sort_priority
            )
            
        self._save_configuration()
        self.column_configuration_reset.emit()
        
    # Formatting Functions
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
            
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"
            
    def _format_date(self, date_obj) -> str:
        """Format date in user-friendly format."""
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime("%b %d, %Y %H:%M")
        return str(date_obj)
        
    def _format_permissions(self, permissions) -> str:
        """Format file permissions."""
        if isinstance(permissions, int):
            # Convert octal permissions to string
            return oct(permissions)[2:]
        return str(permissions)
        
    # Categories and Grouping
    def get_column_categories(self) -> List[str]:
        """Get all column categories."""
        categories = set()
        for column_def in self._column_definitions.values():
            categories.add(column_def.category)
        return sorted(categories)
        
    def get_columns_by_category(self, category: str) -> List[ColumnDefinition]:
        """Get columns in a specific category."""
        return [
            column_def for column_def in self._column_definitions.values()
            if column_def.category == category
        ]
        
    # Persistence
    def _load_configuration(self):
        """Load column configuration from file."""
        if not self._settings_file.exists():
            return
            
        try:
            with open(self._settings_file, 'r') as f:
                data = json.load(f)
                
            column_states = data.get('column_states', {})
            
            for column_id, state_data in column_states.items():
                if column_id in self._column_states:
                    self._column_states[column_id] = ColumnState(
                        column_id=state_data['column_id'],
                        visible=state_data['visible'],
                        width=state_data['width'],
                        position=state_data['position'],
                        sort_order=state_data.get('sort_order')
                    )
                    
        except (json.JSONDecodeError, KeyError, IOError) as e:
            from lg import logger
            logger.error(f"Failed to load column configuration: {e}")
            
    def _save_configuration(self):
        """Save column configuration to file."""
        try:
            data = {
                'version': '1.0',
                'column_states': {
                    column_id: {
                        'column_id': state.column_id,
                        'visible': state.visible,
                        'width': state.width,
                        'position': state.position,
                        'sort_order': state.sort_order
                    }
                    for column_id, state in self._column_states.items()
                }
            }
            
            # Ensure parent directory exists
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._settings_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except (OSError, IOError) as e:
            from lg import logger
            logger.error(f"Failed to save column configuration: {e}")
```

## 2. ColumnManagerDialog

### 2.1 Column Management UI

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QCheckBox, QSpinBox, QComboBox, QLabel, QGroupBox,
    QTabWidget, QWidget, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QDrag, QMimeData

class ColumnManagerDialog(QDialog):
    """
    Dialog for managing column visibility, order, and properties.
    """
    
    # Signals
    columns_changed = Signal()
    
    def __init__(self, column_service: ColumnConfigurationService, parent=None):
        super().__init__(parent)
        self.column_service = column_service
        self.setWindowTitle("Column Manager")
        self.setModal(True)
        self.resize(600, 400)
        
        self._setup_ui()
        self._load_current_configuration()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Visibility tab
        self._create_visibility_tab()
        
        # Order tab 
        self._create_order_tab()
        
        # Properties tab
        self._create_properties_tab()
        
        # Button box
        self._create_button_box()
        layout.addWidget(self.button_box)
        
    def _create_visibility_tab(self):
        """Create column visibility management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Category grouping
        self.category_groups = {}
        categories = self.column_service.get_column_categories()
        
        for category in categories:
            group_box = QGroupBox(category)
            group_layout = QVBoxLayout(group_box)
            
            columns = self.column_service.get_columns_by_category(category)
            category_checkboxes = {}
            
            for column in columns:
                checkbox = QCheckBox(column.display_name)
                checkbox.setToolTip(column.description)
                checkbox.setEnabled(column.can_hide)
                
                if not column.can_hide:
                    checkbox.setStyleSheet("color: gray;")
                    
                category_checkboxes[column.id] = checkbox
                group_layout.addWidget(checkbox)
                
            self.category_groups[category] = {
                'group_box': group_box,
                'checkboxes': category_checkboxes
            }
            
            layout.addWidget(group_box)
            
        # Add stretch
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Visibility")
        
    def _create_order_tab(self):
        """Create column order management tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Available columns list
        available_group = QGroupBox("Available Columns")
        available_layout = QVBoxLayout(available_group)
        
        self.available_list = QListWidget()
        self.available_list.setDragDropMode(QListWidget.DragOnly)
        available_layout.addWidget(self.available_list)
        
        # Visible columns list (reorderable)
        visible_group = QGroupBox("Visible Columns (Drag to Reorder)")
        visible_layout = QVBoxLayout(visible_group)
        
        self.visible_list = QListWidget()
        self.visible_list.setDragDropMode(QListWidget.DragDrop)
        self.visible_list.setDefaultDropAction(Qt.MoveAction)
        visible_layout.addWidget(self.visible_list)
        
        # Control buttons
        controls_layout = QVBoxLayout()
        self.add_button = QPushButton("→")
        self.remove_button = QPushButton("←")
        self.move_up_button = QPushButton("↑")
        self.move_down_button = QPushButton("↓")
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.add_button)
        controls_layout.addWidget(self.remove_button)
        controls_layout.addSeparator()
        controls_layout.addWidget(self.move_up_button)
        controls_layout.addWidget(self.move_down_button)
        controls_layout.addStretch()
        
        # Layout assembly
        layout.addWidget(available_group)
        layout.addLayout(controls_layout)
        layout.addWidget(visible_group)
        
        self.tab_widget.addTab(widget, "Order")
        
    def _create_properties_tab(self):
        """Create column properties management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Column selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Column:"))
        
        self.column_selector = QComboBox()
        selection_layout.addWidget(self.column_selector)
        selection_layout.addStretch()
        
        layout.addLayout(selection_layout)
        
        # Properties table
        self.properties_table = QTableWidget(0, 2)
        self.properties_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.properties_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.properties_table)
        
        self.tab_widget.addTab(widget, "Properties")
        
    def _create_button_box(self):
        """Create dialog button box."""
        self.button_box = QWidget()
        layout = QHBoxLayout(self.button_box)
        
        # Reset buttons
        self.reset_widths_button = QPushButton("Reset Widths")
        self.reset_all_button = QPushButton("Reset All")
        
        layout.addWidget(self.reset_widths_button)
        layout.addWidget(self.reset_all_button)
        layout.addStretch()
        
        # Standard buttons
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")
        
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.apply_button)
        
    def _load_current_configuration(self):
        """Load current column configuration into UI."""
        # Load visibility checkboxes
        for category, group_data in self.category_groups.items():
            columns = self.column_service.get_columns_by_category(category)
            
            for column in columns:
                if column.id in group_data['checkboxes']:
                    checkbox = group_data['checkboxes'][column.id]
                    state = self.column_service.get_column_state(column.id)
                    if state:
                        checkbox.setChecked(state.visible)
                        
        # Load order lists
        self._update_order_lists()
        
        # Load properties selector
        self._update_properties_selector()
        
    def _update_order_lists(self):
        """Update the order management lists."""
        self.available_list.clear()
        self.visible_list.clear()
        
        visible_columns = self.column_service.get_visible_columns()
        all_columns = self.column_service.get_all_column_definitions()
        
        # Add visible columns to visible list
        for column in visible_columns:
            item = QListWidgetItem(column.display_name)
            item.setData(Qt.UserRole, column.id)
            if not column.can_hide:
                item.setFlags(item.flags() & ~Qt.ItemIsDragEnabled)
                item.setBackground(Qt.lightGray)
            self.visible_list.addItem(item)
            
        # Add non-visible columns to available list
        visible_ids = {col.id for col in visible_columns}
        for column in all_columns:
            if column.id not in visible_ids:
                item = QListWidgetItem(column.display_name)
                item.setData(Qt.UserRole, column.id)
                self.available_list.addItem(item)
                
    def _update_properties_selector(self):
        """Update the properties column selector."""
        self.column_selector.clear()
        
        for column in self.column_service.get_all_column_definitions():
            self.column_selector.addItem(column.display_name, column.id)
            
    def _connect_signals(self):
        """Connect UI signals to handlers."""
        # Visibility tab
        for category, group_data in self.category_groups.items():
            for checkbox in group_data['checkboxes'].values():
                checkbox.toggled.connect(self._on_visibility_changed)
                
        # Order tab
        self.add_button.clicked.connect(self._add_column_to_visible)
        self.remove_button.clicked.connect(self._remove_column_from_visible)
        self.move_up_button.clicked.connect(self._move_column_up)
        self.move_down_button.clicked.connect(self._move_column_down)
        
        # Properties tab
        self.column_selector.currentTextChanged.connect(self._update_properties_display)
        
        # Buttons
        self.reset_widths_button.clicked.connect(self._reset_widths)
        self.reset_all_button.clicked.connect(self._reset_all)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self._apply_changes)
        
    def _on_visibility_changed(self):
        """Handle visibility checkbox changes."""
        self._update_order_lists()
        
    def _add_column_to_visible(self):
        """Add selected column to visible list."""
        current_item = self.available_list.currentItem()
        if current_item:
            column_id = current_item.data(Qt.UserRole)
            column_def = self.column_service.get_column_definition(column_id)
            
            if column_def:
                # Add to visible list
                new_item = QListWidgetItem(column_def.display_name)
                new_item.setData(Qt.UserRole, column_id)
                self.visible_list.addItem(new_item)
                
                # Remove from available list
                self.available_list.takeItem(self.available_list.row(current_item))
                
                # Update corresponding checkbox
                self._update_checkbox_state(column_id, True)
                
    def _remove_column_from_visible(self):
        """Remove selected column from visible list."""
        current_item = self.visible_list.currentItem()
        if current_item:
            column_id = current_item.data(Qt.UserRole)
            column_def = self.column_service.get_column_definition(column_id)
            
            if column_def and column_def.can_hide:
                # Add to available list
                new_item = QListWidgetItem(column_def.display_name)
                new_item.setData(Qt.UserRole, column_id)
                self.available_list.addItem(new_item)
                
                # Remove from visible list
                self.visible_list.takeItem(self.visible_list.row(current_item))
                
                # Update corresponding checkbox
                self._update_checkbox_state(column_id, False)
                
    def _move_column_up(self):
        """Move selected column up in order."""
        current_row = self.visible_list.currentRow()
        if current_row > 0:
            item = self.visible_list.takeItem(current_row)
            self.visible_list.insertItem(current_row - 1, item)
            self.visible_list.setCurrentRow(current_row - 1)
            
    def _move_column_down(self):
        """Move selected column down in order."""
        current_row = self.visible_list.currentRow()
        if current_row < self.visible_list.count() - 1:
            item = self.visible_list.takeItem(current_row)
            self.visible_list.insertItem(current_row + 1, item)
            self.visible_list.setCurrentRow(current_row + 1)
            
    def _update_checkbox_state(self, column_id: str, checked: bool):
        """Update checkbox state for a column."""
        column_def = self.column_service.get_column_definition(column_id)
        if column_def:
            category_data = self.category_groups.get(column_def.category)
            if category_data and column_id in category_data['checkboxes']:
                checkbox = category_data['checkboxes'][column_id]
                checkbox.setChecked(checked)
                
    def _update_properties_display(self):
        """Update the properties display for selected column."""
        column_id = self.column_selector.currentData()
        if not column_id:
            return
            
        column_def = self.column_service.get_column_definition(column_id)
        column_state = self.column_service.get_column_state(column_id)
        
        if not column_def or not column_state:
            return
            
        # Clear and populate properties table
        self.properties_table.setRowCount(0)
        
        properties = [
            ("Display Name", column_def.display_name),
            ("Description", column_def.description),
            ("Data Type", column_def.data_type.value),
            ("Category", column_def.category),
            ("Can Hide", "Yes" if column_def.can_hide else "No"),
            ("Can Resize", "Yes" if column_def.can_resize else "No"),
            ("Can Sort", "Yes" if column_def.can_sort else "No"),
            ("Current Width", f"{column_state.width}px"),
            ("Min Width", f"{column_def.min_width}px"),
            ("Max Width", f"{column_def.max_width}px"),
            ("Alignment", column_def.alignment.value),
            ("Visible", "Yes" if column_state.visible else "No"),
            ("Position", str(column_state.position))
        ]
        
        for i, (prop_name, prop_value) in enumerate(properties):
            self.properties_table.insertRow(i)
            self.properties_table.setItem(i, 0, QTableWidgetItem(prop_name))
            self.properties_table.setItem(i, 1, QTableWidgetItem(str(prop_value)))
            
    def _reset_widths(self):
        """Reset all column widths to defaults."""
        self.column_service.reset_column_widths()
        self._update_properties_display()
        
    def _reset_all(self):
        """Reset all column settings to defaults."""
        self.column_service.reset_to_defaults()
        self._load_current_configuration()
        
    def _apply_changes(self):
        """Apply current changes without closing dialog."""
        # Apply visibility changes
        for category, group_data in self.category_groups.items():
            columns = self.column_service.get_columns_by_category(category)
            
            for column in columns:
                if column.id in group_data['checkboxes']:
                    checkbox = group_data['checkboxes'][column.id]
                    self.column_service.set_column_visibility(column.id, checkbox.isChecked())
                    
        # Apply order changes
        visible_order = []
        for i in range(self.visible_list.count()):
            item = self.visible_list.item(i)
            column_id = item.data(Qt.UserRole)
            visible_order.append(column_id)
            
        self.column_service.reorder_columns(visible_order)
        
        self.columns_changed.emit()
        
    def accept(self):
        """Accept dialog and apply changes."""
        self._apply_changes()
        super().accept()
```

## 3. Integration with Explorer Panel

### 3.1 Enhanced Header Widget

```python
class ExplorerHeaderWidget(QHeaderView):
    """
    Enhanced header widget with column management integration.
    """
    
    # Signals
    column_manager_requested = Signal()
    column_settings_requested = Signal(str)  # column_id
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.column_service = None
        self._setup_context_menu()
        
    def _setup_context_menu(self):
        """Set up header context menu."""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _show_context_menu(self, position):
        """Show header context menu."""
        if not self.column_service:
            return
            
        # Get column at position
        logical_index = self.logicalIndexAt(position)
        
        menu = QMenu(self)
        
        if logical_index >= 0:
            # Column-specific actions
            visible_columns = self.column_service.get_visible_columns()
            if logical_index < len(visible_columns):
                column = visible_columns[logical_index]
                
                menu.addAction(f"Sort by {column.display_name} ↑")
                menu.addAction(f"Sort by {column.display_name} ↓")
                menu.addSeparator()
                
                if column.can_hide:
                    hide_action = menu.addAction(f"Hide {column.display_name}")
                    hide_action.triggered.connect(
                        lambda: self.column_service.set_column_visibility(column.id, False)
                    )
                    
                settings_action = menu.addAction(f"{column.display_name} Settings...")
                settings_action.triggered.connect(
                    lambda: self.column_settings_requested.emit(column.id)
                )
                
                menu.addSeparator()
                
        # General actions
        manager_action = menu.addAction("Column Manager...")
        manager_action.triggered.connect(self.column_manager_requested.emit)
        
        menu.addAction("Reset Column Widths").triggered.connect(
            self.column_service.reset_column_widths
        )
        
        menu.addAction("Reset to Defaults").triggered.connect(
            self.column_service.reset_to_defaults
        )
        
        menu.exec_(self.mapToGlobal(position))
        
    def set_column_service(self, service: ColumnConfigurationService):
        """Set the column configuration service."""
        self.column_service = service
```

This comprehensive Column Management System provides a complete solution for column configuration, display management, and user customization within the Explorer Header Navigation system.
