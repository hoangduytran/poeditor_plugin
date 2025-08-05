# Preferences System: Common UI Components and Utilities

## Overview
This document defines the shared UI components and utilities that will be used across the Preferences system. These reusable components ensure consistency in the UI, reduce code duplication, and simplify the implementation of new preference pages.

## Component Library

### PreferenceSection
A container for grouping related preferences with a header and collapsible content area.

```python
class PreferenceSection(QWidget):
    """A collapsible section for grouping related preferences."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._expanded = True
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the section UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with expand/collapse button
        self._header = self._create_header()
        layout.addWidget(self._header)
        
        # Content area
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        layout.addWidget(self._content_widget)
        
    def _create_header(self) -> QWidget:
        """Create the section header."""
        header = QWidget()
        header.setObjectName("sectionHeader")
        layout = QHBoxLayout(header)
        
        self._expand_button = QPushButton()
        self._expand_button.setObjectName("expandButton")
        self._expand_button.setFlat(True)
        self._expand_button.setFixedSize(16, 16)
        self._update_expand_button()
        layout.addWidget(self._expand_button)
        
        title_label = QLabel(self._title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        return header
        
    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the content area."""
        self._content_layout.addWidget(widget)
        
    def set_expanded(self, expanded: bool) -> None:
        """Set the expanded state."""
        self._expanded = expanded
        self._content_widget.setVisible(expanded)
        self._update_expand_button()
        
    def is_expanded(self) -> bool:
        """Check if the section is expanded."""
        return self._expanded
```

### PreferencePage
Base class for all preference pages, providing standard layout and navigation.

```python
class PreferencePage(QWidget):
    """Base class for all preference pages."""
    
    changed = Signal()
    
    def __init__(self, title: str, icon: QIcon = None, parent=None):
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._has_changes = False
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the page layout."""
        layout = QVBoxLayout(self)
        
        # Page header
        if self._title:
            header = self._create_header()
            layout.addWidget(header)
            
        # Content area
        self._content_area = QScrollArea()
        self._content_area.setWidgetResizable(True)
        self._content_area.setFrameStyle(QFrame.NoFrame)
        
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_area.setWidget(self._content_widget)
        
        layout.addWidget(self._content_area)
        
    def _create_header(self) -> QWidget:
        """Create the page header."""
        header = QWidget()
        header.setObjectName("pageHeader")
        layout = QHBoxLayout(header)
        
        if self._icon:
            icon_label = QLabel()
            icon_label.setPixmap(self._icon.pixmap(24, 24))
            layout.addWidget(icon_label)
            
        title_label = QLabel(self._title)
        title_label.setObjectName("pageTitle")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        return header
        
    def add_section(self, section: PreferenceSection) -> None:
        """Add a section to the page."""
        self._content_layout.addWidget(section)
        
    def add_widget(self, widget: QWidget) -> None:
        """Add a widget directly to the content area."""
        self._content_layout.addWidget(widget)
        
    def mark_changed(self) -> None:
        """Mark the page as having changes."""
        if not self._has_changes:
            self._has_changes = True
            self.changed.emit()
            
    def mark_saved(self) -> None:
        """Mark the page as saved."""
        self._has_changes = False
        
    def has_changes(self) -> bool:
        """Check if the page has unsaved changes."""
        return self._has_changes
        
    def apply_changes(self) -> bool:
        """Apply pending changes. Override in subclasses."""
        return True
        
    def reset_to_defaults(self) -> None:
        """Reset to default values. Override in subclasses."""
        pass
        
    def get_title(self) -> str:
        """Get the page title."""
        return self._title
        
    def get_icon(self) -> QIcon:
        """Get the page icon."""
        return self._icon
```

### FormLayoutHelper
Utility class to simplify creating form layouts with consistent spacing and alignment.

```python
class FormLayoutHelper:
    """Helper for creating consistent form layouts."""
    
    LABEL_WIDTH = 140
    ROW_SPACING = 8
    SECTION_SPACING = 16
    
    @staticmethod
    def create_form_row(label_text: str, widget: QWidget, 
                       tooltip: str = None) -> tuple[QLabel, QWidget]:
        """Create a label and widget pair with proper alignment and spacing."""
        label = QLabel(label_text)
        label.setFixedWidth(FormLayoutHelper.LABEL_WIDTH)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        if tooltip:
            label.setToolTip(tooltip)
            widget.setToolTip(tooltip)
            
        return label, widget
        
    @staticmethod
    def add_form_row_to_layout(layout: QLayout, label_text: str, 
                              widget: QWidget, tooltip: str = None) -> None:
        """Add a form row to a layout."""
        if isinstance(layout, QFormLayout):
            label = QLabel(label_text)
            if tooltip:
                label.setToolTip(tooltip)
                widget.setToolTip(tooltip)
            layout.addRow(label, widget)
        else:
            row_layout = QHBoxLayout()
            label, widget = FormLayoutHelper.create_form_row(label_text, widget, tooltip)
            row_layout.addWidget(label)
            row_layout.addWidget(widget)
            row_layout.addStretch()
            layout.addLayout(row_layout)
            
    @staticmethod
    def create_form_separator() -> QFrame:
        """Create a horizontal separator line."""
        separator = QFrame()
        separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        separator.setMaximumHeight(1)
        return separator
        
    @staticmethod
    def create_form_group(title: str, widgets: list[tuple[str, QWidget]]) -> QGroupBox:
        """Create a group box with form elements."""
        group = QGroupBox(title)
        layout = QFormLayout(group)
        
        for label_text, widget in widgets:
            layout.addRow(label_text, widget)
            
        return group
```

### SearchableListWidget
Extended QListWidget with built-in search functionality.

```python
class SearchableListWidget(QWidget):
    """List widget with integrated search capability."""
    
    itemSelected = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_items = []  # Store all items
        self._filtered_items = []  # Currently visible items
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the search and list UI."""
        layout = QVBoxLayout(self)
        
        # Search field
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("Search...")
        layout.addWidget(self._search_field)
        
        # List widget
        self._list_widget = QListWidget()
        layout.addWidget(self._list_widget)
        
    def _connect_signals(self):
        """Connect signals."""
        self._search_field.textChanged.connect(self._on_search_changed)
        self._list_widget.currentItemChanged.connect(self._on_item_selected)
        
    def add_item(self, text: str, data: Any = None) -> None:
        """Add an item to the list with associated data."""
        item_data = {'text': text, 'data': data}
        self._all_items.append(item_data)
        self._refresh_list()
        
    def clear(self) -> None:
        """Clear all items."""
        self._all_items.clear()
        self._filtered_items.clear()
        self._list_widget.clear()
        
    def set_items(self, items: list[tuple[str, Any]]) -> None:
        """Set all items at once."""
        self._all_items = [{'text': text, 'data': data} for text, data in items]
        self._refresh_list()
        
    def _on_search_changed(self, text: str) -> None:
        """Handle search text changes."""
        self.filter_items(text)
        
    def filter_items(self, search_text: str) -> None:
        """Filter items based on search text."""
        search_text = search_text.lower()
        
        if not search_text:
            self._filtered_items = self._all_items.copy()
        else:
            self._filtered_items = [
                item for item in self._all_items
                if search_text in item['text'].lower()
            ]
            
        self._refresh_list()
        
    def _refresh_list(self) -> None:
        """Refresh the list widget with filtered items."""
        self._list_widget.clear()
        
        for item_data in self._filtered_items:
            item = QListWidgetItem(item_data['text'])
            item.setData(Qt.UserRole, item_data['data'])
            self._list_widget.addItem(item)
            
    def _on_item_selected(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """Handle item selection."""
        if current:
            data = current.data(Qt.UserRole)
            self.itemSelected.emit(data)
```

### EditableTableWidget
Extended QTableWidget with inline editing capabilities and standard controls.

```python
class EditableTableWidget(QWidget):
    """Table widget with add/edit/delete controls."""
    
    dataChanged = Signal()
    itemSelected = Signal(int)  # Row index
    
    def __init__(self, headers: list[str], parent=None):
        super().__init__(parent)
        self._headers = headers
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the table and controls."""
        layout = QVBoxLayout(self)
        
        # Table widget
        self._table = QTableWidget()
        self._table.setColumnCount(len(self._headers))
        self._table.setHorizontalHeaderLabels(self._headers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self._add_button = QPushButton("Add")
        self._edit_button = QPushButton("Edit")
        self._delete_button = QPushButton("Delete")
        self._duplicate_button = QPushButton("Duplicate")
        
        button_layout.addWidget(self._add_button)
        button_layout.addWidget(self._edit_button)
        button_layout.addWidget(self._delete_button)
        button_layout.addWidget(self._duplicate_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _connect_signals(self):
        """Connect table and button signals."""
        self._table.itemChanged.connect(self._on_item_changed)
        self._table.currentRowChanged.connect(self._on_row_changed)
        
        self._add_button.clicked.connect(self._on_add_clicked)
        self._edit_button.clicked.connect(self._on_edit_clicked)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        self._duplicate_button.clicked.connect(self._on_duplicate_clicked)
        
    def add_row(self, data: list) -> None:
        """Add a row with the provided data."""
        row = self._table.rowCount()
        self._table.insertRow(row)
        
        for col, value in enumerate(data):
            if col < len(self._headers):
                item = QTableWidgetItem(str(value))
                self._table.setItem(row, col, item)
                
        self.dataChanged.emit()
        
    def get_all_data(self) -> list[list]:
        """Return all table data as a list of rows."""
        data = []
        for row in range(self._table.rowCount()):
            row_data = []
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data
        
    def get_selected_row(self) -> int:
        """Get the currently selected row index."""
        return self._table.currentRow()
        
    def set_data(self, data: list[list]) -> None:
        """Set all table data."""
        self._table.setRowCount(0)
        for row_data in data:
            self.add_row(row_data)
            
    def _on_add_clicked(self) -> None:
        """Handle add button click."""
        # Subclasses can override this
        empty_row = [""] * len(self._headers)
        self.add_row(empty_row)
        
    def _on_edit_clicked(self) -> None:
        """Handle edit button click."""
        row = self.get_selected_row()
        if row >= 0:
            # Enable editing for the selected row
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                if item:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    
    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        row = self.get_selected_row()
        if row >= 0:
            self._table.removeRow(row)
            self.dataChanged.emit()
            
    def _on_duplicate_clicked(self) -> None:
        """Handle duplicate button click."""
        row = self.get_selected_row()
        if row >= 0:
            row_data = []
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                row_data.append(item.text() if item else "")
            self.add_row(row_data)
```

### ValidationHelpers
Utilities for input validation with visual feedback.

```python
class ValidationHelpers:
    """UI validation utilities."""
    
    VALID_STYLE = ""
    INVALID_STYLE = "border: 2px solid red; background-color: rgba(255, 0, 0, 20);"
    WARNING_STYLE = "border: 2px solid orange; background-color: rgba(255, 165, 0, 20);"
    
    @staticmethod
    def set_validation_state(widget: QWidget, is_valid: bool, 
                           message: str = None, level: str = "error") -> None:
        """Update widget styling based on validation state."""
        if is_valid:
            widget.setStyleSheet(ValidationHelpers.VALID_STYLE)
            widget.setToolTip("")
        else:
            if level == "warning":
                widget.setStyleSheet(ValidationHelpers.WARNING_STYLE)
            else:
                widget.setStyleSheet(ValidationHelpers.INVALID_STYLE)
                
            if message:
                widget.setToolTip(message)
                
    @staticmethod
    def create_validator(pattern: str) -> QRegularExpressionValidator:
        """Create a validator for text inputs based on regex pattern."""
        regex = QRegularExpression(pattern)
        return QRegularExpressionValidator(regex)
        
    @staticmethod
    def validate_required(widget: QLineEdit, field_name: str = "Field") -> bool:
        """Validate that a required field is not empty."""
        text = widget.text().strip()
        is_valid = bool(text)
        
        ValidationHelpers.set_validation_state(
            widget, is_valid, 
            f"{field_name} is required" if not is_valid else None
        )
        
        return is_valid
        
    @staticmethod
    def validate_regex_pattern(widget: QLineEdit) -> bool:
        """Validate that a regex pattern is valid."""
        pattern = widget.text()
        
        if not pattern:
            ValidationHelpers.set_validation_state(widget, True)
            return True
            
        try:
            re.compile(pattern)
            ValidationHelpers.set_validation_state(widget, True)
            return True
        except re.error as e:
            ValidationHelpers.set_validation_state(
                widget, False, f"Invalid regex pattern: {e}"
            )
            return False
```

## Theming and Styling

### Style Constants
Central definition of spacing, colors, and font sizes for preferences UI.

```python
class PreferencesStyle:
    """Style constants for the preferences system."""
    
    # Spacing
    SECTION_SPACING = 16
    FORM_LABEL_WIDTH = 140
    FORM_ROW_SPACING = 8
    BUTTON_SPACING = 8
    PAGE_MARGINS = 12
    
    # Colors (these will be overridden by theme system)
    SECTION_BORDER_COLOR = "#E0E0E0"
    HEADER_BACKGROUND_COLOR = "#F5F5F5"
    SELECTION_COLOR = "#0078D4"
    ERROR_COLOR = "#FF4444"
    WARNING_COLOR = "#FFA500"
    
    # Fonts
    SECTION_HEADER_STYLE = "font-weight: bold; font-size: 14px;"
    PAGE_HEADER_STYLE = "font-weight: bold; font-size: 16px;"
    FORM_LABEL_STYLE = "font-weight: normal; font-size: 12px;"
    
    # Widget styles
    SECTION_HEADER_STYLE_SHEET = f"""
        QWidget#sectionHeader {{
            background-color: {HEADER_BACKGROUND_COLOR};
            border-bottom: 1px solid {SECTION_BORDER_COLOR};
            padding: 4px;
        }}
        QLabel#sectionTitle {{
            {SECTION_HEADER_STYLE}
        }}
        QPushButton#expandButton {{
            border: none;
            background: transparent;
        }}
    """
    
    PAGE_HEADER_STYLE_SHEET = f"""
        QWidget#pageHeader {{
            background-color: {HEADER_BACKGROUND_COLOR};
            border-bottom: 1px solid {SECTION_BORDER_COLOR};
            padding: 8px;
        }}
        QLabel#pageTitle {{
            {PAGE_HEADER_STYLE}
        }}
    """
    
    @staticmethod
    def apply_theme_colors(theme_colors: dict) -> None:
        """Update style colors based on theme."""
        if 'border' in theme_colors:
            PreferencesStyle.SECTION_BORDER_COLOR = theme_colors['border']
        if 'background_light' in theme_colors:
            PreferencesStyle.HEADER_BACKGROUND_COLOR = theme_colors['background_light']
        # Update other colors as needed
```

### Theme Integration
All components will respect the application's theme system via ThemeManager integration.

```python
class ThemeIntegration:
    """Handles theme integration for preference components."""
    
    def __init__(self, theme_manager):
        self._theme_manager = theme_manager
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
        
    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme changes."""
        theme_colors = self._theme_manager.get_current_colors()
        PreferencesStyle.apply_theme_colors(theme_colors)
        
        # Update all preference widgets
        self._update_all_preference_widgets()
        
    def _update_all_preference_widgets(self) -> None:
        """Update all preference widgets with new theme."""
        # Find all preference widgets and update their styles
        app = QApplication.instance()
        for widget in app.allWidgets():
            if isinstance(widget, (PreferencePage, PreferenceSection)):
                self._apply_theme_to_widget(widget)
                
    def _apply_theme_to_widget(self, widget: QWidget) -> None:
        """Apply current theme to a specific widget."""
        if isinstance(widget, PreferenceSection):
            widget._header.setStyleSheet(PreferencesStyle.SECTION_HEADER_STYLE_SHEET)
        elif isinstance(widget, PreferencePage):
            if hasattr(widget, '_header'):
                widget._header.setStyleSheet(PreferencesStyle.PAGE_HEADER_STYLE_SHEET)
```

## Interaction Patterns

### Changes Tracking
Components will track whether the user has made changes that need to be saved:

```python
class ChangeTracker:
    """Helper for tracking unsaved changes."""
    
    changed = Signal(bool)  # Emitted when changed state updates
    
    def __init__(self):
        self._has_unsaved_changes = False
        self._watchers = []  # List of widgets to watch for changes
        
    def add_watcher(self, widget: QWidget) -> None:
        """Add a widget to watch for changes."""
        self._watchers.append(widget)
        
        # Connect appropriate signals based on widget type
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self.mark_changed)
        elif isinstance(widget, QCheckBox):
            widget.toggled.connect(self.mark_changed)
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(self.mark_changed)
        elif isinstance(widget, QSpinBox):
            widget.valueChanged.connect(self.mark_changed)
        # Add more widget types as needed
        
    def mark_changed(self) -> None:
        """Mark as having unsaved changes."""
        if not self._has_unsaved_changes:
            self._has_unsaved_changes = True
            self.changed.emit(True)
            
    def mark_saved(self) -> None:
        """Mark as saved (no unsaved changes)."""
        if self._has_unsaved_changes:
            self._has_unsaved_changes = False
            self.changed.emit(False)
            
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self._has_unsaved_changes
        
    def reset(self) -> None:
        """Reset the change state."""
        self.mark_saved()
```

### Notifications
Standard notification display for success, warnings, and errors:

```python
class PreferencesNotifier:
    """Displays consistent notifications in the preferences dialog."""
    
    @staticmethod
    def show_success(message: str, parent: QWidget = None) -> None:
        """Show a success message that auto-dismisses."""
        # Create a temporary success notification
        notification = QLabel(message)
        notification.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        
        # Position and show notification
        if parent:
            notification.setParent(parent)
            # Position at top of parent widget
            notification.move(10, 10)
            
        notification.show()
        
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, notification.deleteLater)
        
    @staticmethod
    def show_warning(message: str, parent: QWidget = None) -> None:
        """Show a warning that requires acknowledgment."""
        QMessageBox.warning(
            parent, 
            "Warning", 
            message, 
            QMessageBox.Ok
        )
        
    @staticmethod
    def show_error(message: str, parent: QWidget = None) -> None:
        """Show an error that requires acknowledgment."""
        QMessageBox.critical(
            parent, 
            "Error", 
            message, 
            QMessageBox.Ok
        )
        
    @staticmethod
    def confirm_action(message: str, title: str = "Confirm", 
                      parent: QWidget = None) -> bool:
        """Show a confirmation dialog and return the result."""
        result = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return result == QMessageBox.Yes
```

## Integration with Settings System

Components will use a consistent approach to read/write preferences:

```python
class PreferencesAccess:
    """Unified access to the settings backend."""
    
    def __init__(self, settings_manager):
        self._settings_manager = settings_manager
        self._change_callbacks = {}  # key -> list of callbacks
        
    def get_value(self, key: str, default=None):
        """Retrieve a setting value with fallback."""
        return self._settings_manager.get_setting(key, default)
        
    def set_value(self, key: str, value) -> bool:
        """Store a setting value and return success status."""
        try:
            self._settings_manager.set_setting(key, value)
            
            # Notify change callbacks
            if key in self._change_callbacks:
                for callback in self._change_callbacks[key]:
                    try:
                        callback(key, value)
                    except Exception as e:
                        logger.warning(f"Setting change callback failed: {e}")
                        
            return True
        except Exception as e:
            logger.error(f"Failed to save setting {key}: {e}")
            return False
            
    def register_change_callback(self, key: str, callback: Callable) -> None:
        """Register a function to be called when a specific setting changes."""
        if key not in self._change_callbacks:
            self._change_callbacks[key] = []
        self._change_callbacks[key].append(callback)
        
    def unregister_change_callback(self, key: str, callback: Callable) -> None:
        """Unregister a change callback."""
        if key in self._change_callbacks:
            try:
                self._change_callbacks[key].remove(callback)
                if not self._change_callbacks[key]:
                    del self._change_callbacks[key]
            except ValueError:
                pass  # Callback wasn't registered
```

## Implementation Notes

1. **Code Style**: All components follow PEP 8 style and include complete type hints
2. **Testing**: Each component has unit tests in the tests/preferences/ directory
3. **Module Organization**: Components are implemented in the core/preferences/components module
4. **Internationalization**: All text is internationalization-ready using the translation system
5. **Accessibility**: Components support keyboard navigation and screen readers
6. **Inheritance**: Use inheritance appropriately to share code between similar components

## Future Enhancements

1. **Dark Mode**: Add dark mode specific styling variants
2. **Animations**: Implement smooth animations for section expanding/collapsing
3. **Keyboard Shortcuts**: Add comprehensive keyboard shortcuts for common actions
4. **Drag and Drop**: Support drag-and-drop for reordering items in lists and tables
5. **Advanced Search**: Implement fuzzy search and search result highlighting
6. **Responsive Layout**: Adapt layout based on available space

## Testing Strategy

1. **Unit Tests**: Test each component in isolation
2. **Integration Tests**: Test component interaction with settings system
3. **UI Tests**: Test user interactions and visual feedback
4. **Theme Tests**: Verify theme integration works correctly
5. **Accessibility Tests**: Ensure components work with screen readers

This comprehensive component library provides the foundation for building consistent, user-friendly preference dialogs throughout the application.
