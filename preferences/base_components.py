"""
Base UI components for preferences system.

This module provides reusable UI components that form the foundation
of the preferences dialog system, including paging, search, and layout helpers.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QCheckBox, QComboBox,
    QSpinBox, QGroupBox, QFrame, QSplitter, QTextEdit,
    QProgressBar, QToolButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QTimer, QObject
from PySide6.QtGui import QIcon, QFont

from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from lg import logger
from .data_models import PageInfo, PreferenceSearchRequest


class PreferenceSection(QGroupBox):
    """A styled group box for organizing preference controls."""
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(title, parent)
        self.setObjectName("PreferenceSection")
        self._setup_ui()
        logger.debug(f"PreferenceSection created: {title}")
    
    def _setup_ui(self):
        """Setup section UI styling."""
        self.setCheckable(False)
        # Theme-aware styling will be applied via QSS


class PreferencePage(QWidget):
    """Base class for preference pages with consistent layout."""
    
    # Signals
    data_changed = Signal()
    validation_failed = Signal(str)
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.title = title
        self.setObjectName("PreferencePage")
        self._is_modified = False
        self._validation_enabled = True
        self._setup_ui()
        logger.debug(f"PreferencePage created: {title}")
    
    def _setup_ui(self):
        """Setup base page layout."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
    
    def add_section(self, section: PreferenceSection):
        """Add a preference section to the page."""
        self.main_layout.addWidget(section)
    
    def mark_modified(self, modified: bool = True):
        """Mark page as modified."""
        if self._is_modified != modified:
            self._is_modified = modified
            self.data_changed.emit()
    
    def is_modified(self) -> bool:
        """Check if page has unsaved changes."""
        return self._is_modified
    
    def validate(self) -> bool:
        """Validate page data. Override in subclasses."""
        return True
    
    def save_changes(self) -> bool:
        """Save changes. Override in subclasses."""
        self.mark_modified(False)
        return True
    
    def reset_changes(self):
        """Reset to saved state. Override in subclasses."""
        self.mark_modified(False)


class FormLayoutHelper:
    """Helper for creating consistent form layouts."""
    
    @staticmethod
    def create_form_layout() -> QFormLayout:
        """Create a standardized form layout."""
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(5)
        return layout
    
    @staticmethod
    def add_field(layout: QFormLayout, label: str, widget: QWidget, 
                  tooltip: Optional[str] = None):
        """Add a labeled field to form layout."""
        label_widget = QLabel(label)
        if tooltip:
            label_widget.setToolTip(tooltip)
            widget.setToolTip(tooltip)
        layout.addRow(label_widget, widget)
    
    @staticmethod
    def add_checkbox(layout: QFormLayout, label: str, 
                     tooltip: Optional[str] = None) -> QCheckBox:
        """Add a checkbox field."""
        checkbox = QCheckBox()
        FormLayoutHelper.add_field(layout, label, checkbox, tooltip)
        return checkbox
    
    @staticmethod
    def add_text_field(layout: QFormLayout, label: str, 
                       placeholder: str = "", tooltip: Optional[str] = None) -> QLineEdit:
        """Add a text input field."""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        FormLayoutHelper.add_field(layout, label, line_edit, tooltip)
        return line_edit
    
    @staticmethod
    def add_combo_field(layout: QFormLayout, label: str, items: List[str],
                        tooltip: Optional[str] = None) -> QComboBox:
        """Add a combo box field."""
        combo = QComboBox()
        combo.addItems(items)
        FormLayoutHelper.add_field(layout, label, combo, tooltip)
        return combo


class PagedTableWidget(QTableWidget):
    """Table widget with built-in paging support."""
    
    # Signals
    page_changed = Signal(int)
    page_size_changed = Signal(int)
    data_requested = Signal(int, int)  # page, page_size
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("PagedTableWidget")
        self.page_info = PageInfo()
        self._setup_ui()
        self._setup_table()
        logger.debug("PagedTableWidget created")
    
    def _setup_ui(self):
        """Setup table UI and paging controls."""
        # Table settings
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        
        # Header settings
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    
    def _setup_table(self):
        """Setup table-specific configuration."""
        # Will be overridden by subclasses
        pass
    
    def set_page_info(self, page_info: PageInfo):
        """Update pagination information."""
        self.page_info = page_info
        logger.debug(f"Page info updated: {page_info}")
    
    def go_to_page(self, page: int):
        """Navigate to specific page."""
        if 1 <= page <= self.page_info.total_pages:
            self.page_info.current_page = page
            self.page_changed.emit(page)
            self.data_requested.emit(page, self.page_info.page_size)
    
    def next_page(self):
        """Go to next page."""
        if self.page_info.has_next_page:
            self.go_to_page(self.page_info.current_page + 1)
    
    def prev_page(self):
        """Go to previous page."""
        if self.page_info.has_prev_page:
            self.go_to_page(self.page_info.current_page - 1)
    
    def set_page_size(self, size: int):
        """Change page size."""
        if size != self.page_info.page_size:
            self.page_info.page_size = size
            self.page_size_changed.emit(size)
            self.go_to_page(1)  # Reset to first page


class SearchableListWidget(QWidget):
    """List widget with integrated search functionality."""
    
    # Signals
    search_requested = Signal(str)
    item_selected = Signal(object)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("SearchableListWidget")
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._setup_ui()
        logger.debug("SearchableListWidget created")
    
    def _setup_ui(self):
        """Setup search and list UI."""
        layout = QVBoxLayout(self)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search...")
        self.search_field.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.search_field)
        
        # List widget would go here
        # Subclasses will add specific list implementation
    
    def _on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing."""
        self._search_timer.stop()
        self._search_timer.start(300)  # 300ms debounce
    
    def _perform_search(self):
        """Perform the actual search."""
        query = self.search_field.text().strip()
        self.search_requested.emit(query)


class EditableTableWidget(PagedTableWidget):
    """Editable table widget with validation support."""
    
    # Signals
    cell_edited = Signal(int, int, object)  # row, column, new_value
    row_added = Signal(int)
    row_deleted = Signal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("EditableTableWidget")
        self._validators: Dict[int, Callable] = {}
        self.itemChanged.connect(self._on_item_changed)
        logger.debug("EditableTableWidget created")
    
    def set_column_validator(self, column: int, validator: Callable[[str], bool]):
        """Set validator for specific column."""
        self._validators[column] = validator
    
    def _on_item_changed(self, item: QTableWidgetItem):
        """Handle item changes with validation."""
        row = item.row()
        column = item.column()
        new_value = item.text()
        
        # Validate if validator exists
        if column in self._validators:
            if not self._validators[column](new_value):
                # Validation failed - could show error or revert
                logger.warning(f"Validation failed for column {column}: {new_value}")
                return
        
        self.cell_edited.emit(row, column, new_value)
    
    def add_row(self, data: List[Any]):
        """Add new row with data."""
        row = self.rowCount()
        self.insertRow(row)
        
        for col, value in enumerate(data):
            if col < self.columnCount():
                item = QTableWidgetItem(str(value))
                self.setItem(row, col, item)
        
        self.row_added.emit(row)
    
    def delete_selected_rows(self):
        """Delete selected rows."""
        rows = set()
        for item in self.selectedItems():
            rows.add(item.row())
        
        # Remove rows in reverse order to maintain indices
        for row in sorted(rows, reverse=True):
            self.removeRow(row)
            self.row_deleted.emit(row)


class ValidationHelpers:
    """Helper functions for data validation in preferences."""
    
    @staticmethod
    def validate_non_empty(value: str) -> bool:
        """Validate that value is not empty."""
        return bool(value.strip())
    
    @staticmethod
    def validate_regex(pattern: str) -> bool:
        """Validate that pattern is valid regex."""
        try:
            import re
            re.compile(pattern)
            return True
        except re.error:
            return False
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """Validate file path format."""
        try:
            from pathlib import Path
            Path(path)
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def create_required_validator(field_name: str) -> Callable[[str], bool]:
        """Create validator for required fields."""
        def validator(value: str) -> bool:
            if not ValidationHelpers.validate_non_empty(value):
                logger.warning(f"Required field '{field_name}' is empty")
                return False
            return True
        return validator


class PagingControlsWidget(QWidget):
    """Reusable paging controls widget."""
    
    # Signals
    page_changed = Signal(int)
    page_size_changed = Signal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("PagingControlsWidget")
        self.page_info = PageInfo()
        self._setup_ui()
        logger.debug("PagingControlsWidget created")
    
    def _setup_ui(self):
        """Setup paging controls UI."""
        layout = QHBoxLayout(self)
        
        # First/Previous buttons
        self.first_btn = QPushButton("⏮")
        self.first_btn.setMaximumWidth(30)
        self.first_btn.clicked.connect(lambda: self.page_changed.emit(1))
        
        self.prev_btn = QPushButton("⏴")
        self.prev_btn.setMaximumWidth(30)
        self.prev_btn.clicked.connect(self._prev_page)
        
        # Page info
        self.page_label = QLabel("Page 1 of 1")
        
        # Next/Last buttons
        self.next_btn = QPushButton("⏵")
        self.next_btn.setMaximumWidth(30)
        self.next_btn.clicked.connect(self._next_page)
        
        self.last_btn = QPushButton("⏭")
        self.last_btn.setMaximumWidth(30)
        self.last_btn.clicked.connect(self._last_page)
        
        # Page size selector
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["25", "50", "100", "200"])
        self.page_size_combo.setCurrentText("50")
        self.page_size_combo.currentTextChanged.connect(self._on_page_size_changed)
        
        # Layout
        layout.addWidget(self.first_btn)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.last_btn)
        layout.addStretch()
        layout.addWidget(QLabel("Page size:"))
        layout.addWidget(self.page_size_combo)
    
    def update_page_info(self, page_info: PageInfo):
        """Update page information and controls."""
        self.page_info = page_info
        
        # Update label
        self.page_label.setText(
            f"Page {page_info.current_page} of {page_info.total_pages} "
            f"({page_info.total_records} records)"
        )
        
        # Update button states
        self.first_btn.setEnabled(page_info.has_prev_page)
        self.prev_btn.setEnabled(page_info.has_prev_page)
        self.next_btn.setEnabled(page_info.has_next_page)
        self.last_btn.setEnabled(page_info.has_next_page)
    
    def _prev_page(self):
        if self.page_info.has_prev_page:
            self.page_changed.emit(self.page_info.current_page - 1)
    
    def _next_page(self):
        if self.page_info.has_next_page:
            self.page_changed.emit(self.page_info.current_page + 1)
    
    def _last_page(self):
        if self.page_info.total_pages > 0:
            self.page_changed.emit(self.page_info.total_pages)
    
    def _on_page_size_changed(self, size_text: str):
        try:
            size = int(size_text)
            self.page_size_changed.emit(size)
        except ValueError:
            logger.warning(f"Invalid page size: {size_text}")


class SettingsGroupWidget(PreferenceSection):
    """Grouped settings controls with validation."""
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(title, parent)
        self.setObjectName("SettingsGroupWidget")
        self._controls: Dict[str, QWidget] = {}
        self._setup_form()
        logger.debug(f"SettingsGroupWidget created: {title}")
    
    def _setup_form(self):
        """Setup form layout."""
        self.form_layout = FormLayoutHelper.create_form_layout()
        self.setLayout(self.form_layout)
    
    def add_setting(self, key: str, label: str, widget: QWidget, 
                    tooltip: Optional[str] = None):
        """Add a setting control."""
        self._controls[key] = widget
        FormLayoutHelper.add_field(self.form_layout, label, widget, tooltip)
    
    def get_value(self, key: str) -> Any:
        """Get value from control."""
        widget = self._controls.get(key)
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        return None
    
    def set_value(self, key: str, value: Any):
        """Set value to control."""
        widget = self._controls.get(key)
        if isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(str(value))
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value))
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all values as dictionary."""
        return {key: self.get_value(key) for key in self._controls.keys()}
    
    def set_all_values(self, values: Dict[str, Any]):
        """Set all values from dictionary."""
        for key, value in values.items():
            if key in self._controls:
                self.set_value(key, value)
