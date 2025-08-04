# Preferences Basic Components Design Plan

## Overview

This document outlines the detailed design for building the foundational components that will be shared across all preference panels. These components integrate with the existing unified pagination framework and provide common functionality.

## 1. Pagination Integration Components

### 1.1 PreferencesPagingSettingsManager

**Purpose:** Central manager for pagination settings specific to preferences panels, extending existing pagination framework.

**File:** `services/preferences_paging_service.py`

**Design:**
```python
from PySide6.QtCore import QObject, Signal, QSettings
from typing import Dict, Optional

class PreferencesPagingSettingsManager(QObject):
    """Manages pagination settings specific to preferences panels"""
    
    # Signals for real-time updates
    pageSettingsChanged = Signal(str, int)  # component_name, page_size
    scrollerSettingsChanged = Signal(str, int)  # component_name, scroller_pages
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.settings = QSettings("POEditor", "PreferencesPagination")
        self._component_defaults = {
            "replacement_table": {"page_size": 22, "scroller_pages": 15},
            "history_table": {"page_size": 22, "scroller_pages": 15},
            "main_table": {"page_size": 50, "scroller_pages": 15},
            "search_results": {"page_size": 20, "scroller_pages": 10},
        }
        
    def get_page_size(self, component_name: str) -> int:
        """Get page size for specific component"""
        key = f"{component_name}_page_size"
        default = self._component_defaults.get(component_name, {}).get("page_size", 22)
        return int(self.settings.value(key, default))
    
    def set_page_size(self, component_name: str, page_size: int):
        """Set page size for specific component"""
        key = f"{component_name}_page_size"
        self.settings.setValue(key, page_size)
        self.pageSettingsChanged.emit(component_name, page_size)
        
    def get_scroller_pages(self, component_name: str) -> int:
        """Get scroller pages for specific component"""
        key = f"{component_name}_scroller_pages"
        default = self._component_defaults.get(component_name, {}).get("scroller_pages", 15)
        return int(self.settings.value(key, default))
    
    def set_scroller_pages(self, component_name: str, scroller_pages: int):
        """Set scroller pages for specific component"""
        key = f"{component_name}_scroller_pages"
        self.settings.setValue(key, scroller_pages)
        self.scrollerSettingsChanged.emit(component_name, scroller_pages)
        
    def get_all_settings(self) -> Dict[str, Dict[str, int]]:
        """Get all pagination settings"""
        settings = {}
        for component in self._component_defaults:
            settings[component] = {
                "page_size": self.get_page_size(component),
                "scroller_pages": self.get_scroller_pages(component)
            }
        return settings
    
    def reset_to_defaults(self, component_name: Optional[str] = None):
        """Reset settings to defaults"""
        if component_name:
            defaults = self._component_defaults.get(component_name, {})
            if defaults:
                self.set_page_size(component_name, defaults["page_size"])
                self.set_scroller_pages(component_name, defaults["scroller_pages"])
        else:
            # Reset all components
            for comp_name, defaults in self._component_defaults.items():
                self.set_page_size(comp_name, defaults["page_size"])
                self.set_scroller_pages(comp_name, defaults["scroller_pages"])
```

### 1.2 PreferencesPaginationFactory

**Purpose:** Factory for creating pagination components configured for preferences panels.

**File:** `widgets/preferences/preferences_pagination_factory.py`

**Design:**
```python
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject
from typing import Optional, List

# Import existing pagination framework
from common.pagination.pagination_controller import DatabasePaginationController
from common.pagination.pagination_widget import PaginationWidget
from common.pagination.compact_pagination_controls import CompactPaginationControls
from common.pagination.interfaces import IPaginationWidget

class PreferencesPaginationFactory:
    """Factory for creating pagination components for preferences panels"""
    
    @staticmethod
    def create_database_pagination(table_widget, database_service, 
                                 component_name: str,
                                 settings_manager: PreferencesPagingSettingsManager,
                                 parent: Optional[QObject] = None) -> DatabasePaginationController:
        """Creates configured pagination controller for database operations"""
        
        # Get settings for this component
        page_size = settings_manager.get_page_size(component_name)
        
        # Create controller with existing framework
        controller = DatabasePaginationController(
            table_widget=table_widget,
            data_provider=database_service,  # Service implements PaginationDataProvider
            page_size=page_size,
            parent=parent
        )
        
        # Connect to settings changes for real-time updates
        settings_manager.pageSettingsChanged.connect(
            lambda comp, size: controller.set_page_size(size) if comp == component_name else None
        )
        
        return controller
        
    @staticmethod  
    def create_pagination_widget(controller: DatabasePaginationController, 
                               compact: bool = False,
                               page_sizes: Optional[List[int]] = None,
                               parent: Optional[QWidget] = None) -> IPaginationWidget:
        """Creates appropriate pagination widget (full or compact)"""
        
        if page_sizes is None:
            page_sizes = [10, 22, 50, 100, 250]
            
        if compact:
            widget = CompactPaginationControls(parent=parent)
        else:
            widget = PaginationWidget(
                controller=controller,
                page_sizes=page_sizes,
                show_page_size=True,
                show_goto=True,
                show_status=True,
                parent=parent
            )
            
        # Connect widget to controller
        widget.connect_paginator(controller)
        
        return widget
        
    @staticmethod
    def create_database_pagination_widget(controller: DatabasePaginationController,
                                        show_filters: bool = True,
                                        show_sort: bool = True,
                                        parent: Optional[QWidget] = None):
        """Creates enhanced pagination widget with database-specific features"""
        
        from widgets.preferences.database_pagination_widget import DatabasePaginationWidget
        
        widget = DatabasePaginationWidget(
            controller=controller,
            show_filters=show_filters,
            show_sort=show_sort,
            parent=parent
        )
        
        return widget
```

### 1.3 DatabasePaginationWidget

**Purpose:** Enhanced pagination widget with database-specific features for advanced filtering and sorting.

**File:** `widgets/preferences/database_pagination_widget.py`

**Design:**
```python
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QPushButton, QLabel, QLineEdit, QDateEdit, QFrame)
from PySide6.QtCore import Signal, QDate, Qt

# Import existing pagination framework
from common.pagination.pagination_widget import PaginationWidget

class DatabasePaginationWidget(PaginationWidget):
    """Enhanced pagination widget with database-specific features for preferences"""
    
    # Additional signals for database operations
    filterChanged = Signal(str, str)  # filter_type, filter_value
    sortChanged = Signal(str, bool)   # column, ascending
    searchRequested = Signal(str)     # search_text
    dateRangeChanged = Signal(QDate, QDate)  # from_date, to_date
    
    def __init__(self, controller, 
                 show_filters: bool = True,
                 show_sort: bool = True,
                 show_search: bool = True,
                 show_date_range: bool = False,
                 parent=None):
        super().__init__(controller, parent=parent)
        
        self.show_filters = show_filters
        self.show_sort = show_sort
        self.show_search = show_search
        self.show_date_range = show_date_range
        
        self._setup_database_controls()
        
    def _setup_database_controls(self):
        """Add database-specific controls above standard pagination"""
        
        # Create container for database controls
        db_controls_frame = QFrame()
        db_controls_frame.setObjectName("database_controls_frame")
        db_controls_layout = QVBoxLayout(db_controls_frame)
        db_controls_layout.setContentsMargins(4, 4, 4, 4)
        db_controls_layout.setSpacing(4)
        
        # Add search controls if requested
        if self.show_search:
            search_layout = self._create_search_controls()
            db_controls_layout.addLayout(search_layout)
            
        # Add filter controls if requested
        if self.show_filters:
            filter_layout = self._create_filter_controls()
            db_controls_layout.addLayout(filter_layout)
            
        # Add sort controls if requested
        if self.show_sort:
            sort_layout = self._create_sort_controls()
            db_controls_layout.addLayout(sort_layout)
            
        # Add date range controls if requested
        if self.show_date_range:
            date_layout = self._create_date_range_controls()
            db_controls_layout.addLayout(date_layout)
            
        # Insert at top of main layout
        self.main_layout.insertWidget(0, db_controls_frame)
        
    def _create_search_controls(self) -> QHBoxLayout:
        """Create search input controls"""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(4)
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self._on_search_changed)
        
        clear_search_btn = QPushButton("Clear")
        clear_search_btn.clicked.connect(self._clear_search)
        clear_search_btn.setMaximumWidth(60)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(clear_search_btn)
        search_layout.addStretch()
        
        return search_layout
        
    def _create_filter_controls(self) -> QHBoxLayout:
        """Create filter dropdown controls"""
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(4)
        
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Records",
            "Enabled Only",
            "Disabled Only", 
            "Recently Modified",
            "Has Notes"
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        
        return filter_layout
        
    def _create_sort_controls(self) -> QHBoxLayout:
        """Create sorting controls"""
        sort_layout = QHBoxLayout()
        sort_layout.setSpacing(4)
        
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "ID",
            "Find Text", 
            "Replace Text",
            "Created Date",
            "Modified Date"
        ])
        self.sort_combo.currentTextChanged.connect(self._on_sort_column_changed)
        
        self.sort_order_btn = QPushButton("▲")
        self.sort_order_btn.setMaximumWidth(30)
        self.sort_order_btn.setToolTip("Click to change sort order")
        self.sort_order_btn.clicked.connect(self._toggle_sort_order)
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addWidget(self.sort_order_btn)
        sort_layout.addStretch()
        
        return sort_layout
        
    def _create_date_range_controls(self) -> QHBoxLayout:
        """Create date range selection controls"""
        date_layout = QHBoxLayout()
        date_layout.setSpacing(4)
        
        date_label = QLabel("Date range:")
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.dateChanged.connect(self._on_date_range_changed)
        
        to_label = QLabel("to")
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.dateChanged.connect(self._on_date_range_changed)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.from_date)
        date_layout.addWidget(to_label)
        date_layout.addWidget(self.to_date)
        date_layout.addStretch()
        
        return date_layout
        
    def _on_search_changed(self, text: str):
        """Handle search text changes with debouncing"""
        # Implement debouncing to avoid excessive database queries
        if hasattr(self, '_search_timer'):
            self._search_timer.stop()
            
        from PySide6.QtCore import QTimer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(lambda: self.searchRequested.emit(text))
        self._search_timer.start(300)  # 300ms delay
        
    def _clear_search(self):
        """Clear search input"""
        self.search_input.clear()
        
    def _on_filter_changed(self, filter_text: str):
        """Handle filter selection changes"""
        self.filterChanged.emit("status", filter_text)
        
    def _on_sort_column_changed(self, column_text: str):
        """Handle sort column changes"""
        ascending = self.sort_order_btn.text() == "▲"
        self.sortChanged.emit(column_text, ascending)
        
    def _toggle_sort_order(self):
        """Toggle sort order between ascending/descending"""
        ascending = self.sort_order_btn.text() == "▲"
        new_ascending = not ascending
        self.sort_order_btn.setText("▲" if new_ascending else "▼")
        
        # Emit sort change with new order
        column = self.sort_combo.currentText()
        self.sortChanged.emit(column, new_ascending)
        
    def _on_date_range_changed(self):
        """Handle date range changes"""
        from_date = self.from_date.date()
        to_date = self.to_date.date()
        self.dateRangeChanged.emit(from_date, to_date)
        
    def get_current_filters(self) -> dict:
        """Get current filter state"""
        filters = {}
        
        if self.show_search and hasattr(self, 'search_input'):
            filters['search'] = self.search_input.text()
            
        if self.show_filters and hasattr(self, 'filter_combo'):
            filters['status_filter'] = self.filter_combo.currentText()
            
        if self.show_sort and hasattr(self, 'sort_combo'):
            filters['sort_column'] = self.sort_combo.currentText()
            filters['sort_ascending'] = self.sort_order_btn.text() == "▲"
            
        if self.show_date_range and hasattr(self, 'from_date'):
            filters['date_from'] = self.from_date.date()
            filters['date_to'] = self.to_date.date()
            
        return filters
        
    def set_filter_options(self, filter_options: list):
        """Update filter dropdown options"""
        if hasattr(self, 'filter_combo'):
            current = self.filter_combo.currentText()
            self.filter_combo.clear()
            self.filter_combo.addItems(filter_options)
            
            # Restore selection if still available
            index = self.filter_combo.findText(current)
            if index >= 0:
                self.filter_combo.setCurrentIndex(index)
                
    def set_sort_options(self, sort_options: list):
        """Update sort dropdown options"""
        if hasattr(self, 'sort_combo'):
            current = self.sort_combo.currentText()
            self.sort_combo.clear()
            self.sort_combo.addItems(sort_options)
            
            # Restore selection if still available
            index = self.sort_combo.findText(current)
            if index >= 0:
                self.sort_combo.setCurrentIndex(index)
```

## 2. Font Management Components

### 2.1 FontSelectorWidget

**Purpose:** Unified font selector with family/size/preview for all font components.

**File:** `widgets/shared/font_selector_widget.py`

**Design:**
```python
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                               QFontComboBox, QSpinBox, QPushButton)
from PySide6.QtCore import Signal, QSettings
from PySide6.QtGui import QFont
from typing import Optional

class FontSelectorWidget(QWidget):
    """Unified font selector with family/size/preview"""
    
    fontChanged = Signal(QFont)
    fontApplied = Signal(str, QFont)  # component_name, font
    
    def __init__(self, component_name: str, 
                 display_name: str,
                 default_size: int = 12,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.component_name = component_name
        self.display_name = display_name
        self.default_size = default_size
        self.settings = QSettings("POEditor", "FontSettings")
        
        self._setup_ui()
        self._load_font_settings()
        
    def _setup_ui(self):
        """Setup the font selector UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Component label
        title_label = QLabel(self.display_name)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        # Font controls layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        # Font family selector
        family_label = QLabel("Family:")
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._on_font_changed)
        
        # Font size selector
        size_label = QLabel("Size:")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(6, 72)
        self.size_spinbox.setValue(self.default_size)
        self.size_spinbox.valueChanged.connect(self._on_font_changed)
        
        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_font)
        self.apply_btn.setMaximumWidth(60)
        
        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset_font)
        self.reset_btn.setMaximumWidth(60)
        
        controls_layout.addWidget(family_label)
        controls_layout.addWidget(self.font_combo, 1)
        controls_layout.addWidget(size_label)
        controls_layout.addWidget(self.size_spinbox)
        controls_layout.addWidget(self.apply_btn)
        controls_layout.addWidget(self.reset_btn)
        
        layout.addLayout(controls_layout)
        
        # Preview widget
        from widgets.shared.font_preview_widget import FontPreviewWidget
        self.preview_widget = FontPreviewWidget(parent=self)
        layout.addWidget(self.preview_widget)
        
    def _load_font_settings(self):
        """Load font settings from QSettings"""
        font_family = self.settings.value(f"{self.component_name}_family", "")
        font_size = int(self.settings.value(f"{self.component_name}_size", self.default_size))
        
        if font_family:
            font = QFont(font_family, font_size)
            self.font_combo.setCurrentFont(font)
        
        self.size_spinbox.setValue(font_size)
        self._update_preview()
        
    def _save_font_settings(self, font: QFont):
        """Save font settings to QSettings"""
        self.settings.setValue(f"{self.component_name}_family", font.family())
        self.settings.setValue(f"{self.component_name}_size", font.pointSize())
        
    def _on_font_changed(self):
        """Handle font family or size changes"""
        self._update_preview()
        current_font = self.get_current_font()
        self.fontChanged.emit(current_font)
        
    def _update_preview(self):
        """Update the font preview"""
        current_font = self.get_current_font()
        self.preview_widget.update_preview(current_font)
        
    def _apply_font(self):
        """Apply the current font settings"""
        current_font = self.get_current_font()
        self._save_font_settings(current_font)
        self.fontApplied.emit(self.component_name, current_font)
        
    def _reset_font(self):
        """Reset font to default"""
        # Get system default font
        default_font = QFont()
        default_font.setPointSize(self.default_size)
        
        self.font_combo.setCurrentFont(default_font)
        self.size_spinbox.setValue(self.default_size)
        
        self._save_font_settings(default_font)
        self.fontApplied.emit(self.component_name, default_font)
        
    def get_current_font(self) -> QFont:
        """Get currently selected font"""
        font = self.font_combo.currentFont()
        font.setPointSize(self.size_spinbox.value())
        return font
        
    def set_font(self, font: QFont):
        """Set the font programmatically"""
        self.font_combo.setCurrentFont(font)
        self.size_spinbox.setValue(font.pointSize())
        self._update_preview()
```

### 2.2 FontPreviewWidget

**Purpose:** Standardized font preview with sample text.

**File:** `widgets/shared/font_preview_widget.py`

**Design:**
```python
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional

class FontPreviewWidget(QLabel):
    """Standardized font preview with sample text"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setObjectName("font_preview")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(60)
        self.setMaximumHeight(100)
        
        # Set default preview text
        self.preview_text = "AaBbCc 123 !@# Sample Text Preview"
        self.setText(self.preview_text)
        
        # Apply styling
        self.setStyleSheet("""
            QLabel#font_preview {
                background-color: var(--editor-bg, #ffffff);
                border: 1px solid var(--panel-border, #cccccc);
                border-radius: 4px;
                padding: 8px;
                color: var(--fg-main, #000000);
                margin: 4px;
            }
        """)
        
    def update_preview(self, font: QFont):
        """Update preview with new font"""
        self.setFont(font)
        
        # Update text to show font info
        font_info = f"{font.family()}, {font.pointSize()}pt"
        full_text = f"{self.preview_text}\n{font_info}"
        self.setText(full_text)
        
    def set_preview_text(self, text: str):
        """Set custom preview text"""
        self.preview_text = text
        current_font = self.font()
        self.update_preview(current_font)
        
    def set_component_specific_text(self, component_name: str):
        """Set component-specific preview text"""
        component_texts = {
            "msgid": "msgid: Original source text for translation",
            "msgstr": "msgstr: Translated text in target language", 
            "table": "Table Row | Column Header | Data Cell",
            "comment": "# Translator comment or note",
            "suggestion": "Translation suggestion from memory",
            "control": "Button Label | Menu Item | Dialog Title"
        }
        
        text = component_texts.get(component_name, self.preview_text)
        self.set_preview_text(text)
```

### 2.3 FontApplicationService

**Purpose:** Service for applying fonts throughout the application.

**File:** `services/font_application_service.py`

**Design:**
```python
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from typing import Dict, Optional, List

class FontApplicationService(QObject):
    """Service for applying fonts throughout application"""
    
    fontsApplied = Signal(dict)  # fonts applied
    fontError = Signal(str, str)  # component_name, error_message
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self.settings = QSettings("POEditor", "FontSettings")
        self.component_configs = {
            "msgid": {"default_size": 15, "targets": ["msgid_labels", "source_text_display"]},
            "msgstr": {"default_size": 24, "targets": ["msgstr_editors", "translation_display"]},
            "table": {"default_size": 13, "targets": ["table_views", "table_headers"]},
            "comment": {"default_size": 15, "targets": ["comment_editors", "comment_display"]},
            "suggestion": {"default_size": 13, "targets": ["suggestion_lists", "suggestion_display"]},
            "control": {"default_size": 12, "targets": ["buttons", "labels", "headers", "menus"]}
        }
        
    def apply_component_font(self, component_name: str, font: QFont) -> bool:
        """Apply font to specific component types"""
        try:
            config = self.component_configs.get(component_name)
            if not config:
                self.fontError.emit(component_name, f"Unknown component: {component_name}")
                return False
                
            # Apply to target widget types
            success = True
            for target in config["targets"]:
                if not self._apply_to_target(target, font):
                    success = False
                    
            if success:
                # Save font settings
                self.settings.setValue(f"{component_name}_family", font.family())
                self.settings.setValue(f"{component_name}_size", font.pointSize())
                
            return success
            
        except Exception as e:
            self.fontError.emit(component_name, str(e))
            return False
            
    def _apply_to_target(self, target: str, font: QFont) -> bool:
        """Apply font to specific target widget types"""
        try:
            app = QApplication.instance()
            if not app:
                return False
                
            # Find widgets by object name patterns
            widgets = self._find_widgets_by_target(target)
            
            for widget in widgets:
                widget.setFont(font)
                
            return True
            
        except Exception as e:
            return False
            
    def _find_widgets_by_target(self, target: str) -> List:
        """Find widgets matching target pattern"""
        widgets = []
        app = QApplication.instance()
        
        if not app:
            return widgets
            
        # Define object name patterns for each target
        patterns = {
            "msgid_labels": ["msgid_*", "*_msgid_*", "*source_text*"],
            "msgstr_editors": ["msgstr_*", "*_msgstr_*", "*translation_edit*"],
            "table_views": ["*_table", "*_table_view", "*TableView"],
            "table_headers": ["*_header", "*TableHeader*"],
            "comment_editors": ["*comment*", "*_comment_*"],
            "comment_display": ["*comment_display*", "*comment_label*"],
            "suggestion_lists": ["*suggestion*", "*_suggestion_*"],
            "suggestion_display": ["*suggestion_display*"],
            "buttons": ["*Button", "*_button", "*_btn"],
            "labels": ["*Label", "*_label"],
            "headers": ["*Header*", "*_header"],
            "menus": ["*Menu*", "*_menu"]
        }
        
        target_patterns = patterns.get(target, [])
        
        for widget in app.allWidgets():
            object_name = widget.objectName()
            if object_name:
                for pattern in target_patterns:
                    if self._matches_pattern(object_name, pattern):
                        widgets.append(widget)
                        break
                        
        return widgets
        
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Check if name matches wildcard pattern"""
        import fnmatch
        return fnmatch.fnmatch(name.lower(), pattern.lower())
        
    def load_font_settings(self) -> Dict[str, QFont]:
        """Load all font settings from QSettings"""
        fonts = {}
        
        for component_name, config in self.component_configs.items():
            family = self.settings.value(f"{component_name}_family", "")
            size = int(self.settings.value(f"{component_name}_size", config["default_size"]))
            
            if family:
                font = QFont(family, size)
            else:
                # Use system default with configured size
                font = QFont()
                font.setPointSize(size)
                
            fonts[component_name] = font
            
        return fonts
        
    def save_font_settings(self, fonts: Dict[str, QFont]):
        """Save font settings to QSettings"""
        for component_name, font in fonts.items():
            self.settings.setValue(f"{component_name}_family", font.family())
            self.settings.setValue(f"{component_name}_size", font.pointSize())
            
    def apply_all_fonts(self, fonts: Optional[Dict[str, QFont]] = None):
        """Apply all font settings"""
        if fonts is None:
            fonts = self.load_font_settings()
            
        applied_fonts = {}
        
        for component_name, font in fonts.items():
            if self.apply_component_font(component_name, font):
                applied_fonts[component_name] = font
                
        self.fontsApplied.emit(applied_fonts)
        
    def reset_all_fonts(self):
        """Reset all fonts to defaults"""
        default_fonts = {}
        
        for component_name, config in self.component_configs.items():
            font = QFont()
            font.setPointSize(config["default_size"])
            default_fonts[component_name] = font
            
        self.apply_all_fonts(default_fonts)
        self.save_font_settings(default_fonts)
        
    def get_font_component_configs(self) -> Dict:
        """Get font component configurations"""
        return self.component_configs.copy()
```

## 3. Database Operations Components

### 3.1 Base Database Service

**Purpose:** Base class for database operations with pagination support.

**File:** `services/base_database_service.py`

**Design:**
```python
from PySide6.QtCore import QObject, Signal
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from typing import Tuple, List, Dict, Optional, Any
import sqlite3
import os

# Import pagination interface
from common.pagination.interfaces import PaginationDataProvider

class BaseDatabaseService(QObject, PaginationDataProvider):
    """Base class for database operations with pagination support"""
    
    dataChanged = Signal()
    error = Signal(str)
    
    def __init__(self, db_path: str, db_name: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self.db_path = db_path
        self.db_name = db_name
        self.connection = None
        
        self._current_filter = ""
        self._current_sort_column = "id"
        self._current_sort_ascending = True
        
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create connection
            self.connection = QSqlDatabase.addDatabase("QSQLITE", self.db_name)
            self.connection.setDatabaseName(self.db_path)
            
            if not self.connection.open():
                raise Exception(f"Failed to open database: {self.connection.lastError().text()}")
                
            # Create tables (implemented by subclasses)
            self._create_tables()
            
        except Exception as e:
            self.error.emit(f"Database initialization error: {str(e)}")
            
    def _create_tables(self):
        """Create database tables (implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement _create_tables")
        
    def _execute_query(self, sql: str, params: Tuple = ()) -> QSqlQuery:
        """Execute SQL query with parameters"""
        if not self.connection or not self.connection.isOpen():
            raise Exception("Database connection not available")
            
        query = QSqlQuery(self.connection)
        
        if params:
            query.prepare(sql)
            for param in params:
                query.addBindValue(param)
            success = query.exec()
        else:
            success = query.exec(sql)
            
        if not success:
            error_text = query.lastError().text()
            raise Exception(f"Query execution failed: {error_text}")
            
        return query
        
    def get_total_count(self) -> int:
        """Get total number of records (for pagination)"""
        try:
            sql = self._build_count_query()
            query = self._execute_query(sql, self._get_filter_params())
            
            if query.next():
                return query.value(0)
            return 0
            
        except Exception as e:
            self.error.emit(f"Error getting total count: {str(e)}")
            return 0
            
    def get_page_items(self, start_index: int, count: int) -> List[Dict]:
        """Get items for specific page (for pagination)"""
        try:
            sql = self._build_select_query(start_index, count)
            query = self._execute_query(sql, self._get_filter_params())
            
            items = []
            while query.next():
                item = self._query_to_dict(query)
                items.append(item)
                
            return items
            
        except Exception as e:
            self.error.emit(f"Error getting page items: {str(e)}")
            return []
            
    def _build_count_query(self) -> str:
        """Build count query with current filters"""
        base_table = self._get_base_table()
        where_clause = self._build_where_clause()
        
        sql = f"SELECT COUNT(*) FROM {base_table}"
        if where_clause:
            sql += f" WHERE {where_clause}"
            
        return sql
        
    def _build_select_query(self, start_index: int, count: int) -> str:
        """Build select query with pagination and sorting"""
        base_table = self._get_base_table()
        columns = self._get_select_columns()
        where_clause = self._build_where_clause()
        order_clause = self._build_order_clause()
        
        sql = f"SELECT {columns} FROM {base_table}"
        
        if where_clause:
            sql += f" WHERE {where_clause}"
            
        if order_clause:
            sql += f" ORDER BY {order_clause}"
            
        sql += f" LIMIT {count} OFFSET {start_index}"
        
        return sql
        
    def _get_base_table(self) -> str:
        """Get base table name (implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement _get_base_table")
        
    def _get_select_columns(self) -> str:
        """Get columns for select query (implemented by subclasses)"""
        return "*"
        
    def _build_where_clause(self) -> str:
        """Build WHERE clause based on current filters"""
        conditions = []
        
        if self._current_filter:
            search_conditions = self._build_search_conditions(self._current_filter)
            if search_conditions:
                conditions.append(search_conditions)
                
        # Add additional filters from subclasses
        additional_conditions = self._get_additional_where_conditions()
        if additional_conditions:
            conditions.extend(additional_conditions)
            
        return " AND ".join(conditions) if conditions else ""
        
    def _build_search_conditions(self, search_text: str) -> str:
        """Build search conditions (implemented by subclasses)"""
        return ""
        
    def _get_additional_where_conditions(self) -> List[str]:
        """Get additional WHERE conditions (implemented by subclasses)"""
        return []
        
    def _build_order_clause(self) -> str:
        """Build ORDER BY clause"""
        direction = "ASC" if self._current_sort_ascending else "DESC"
        return f"{self._current_sort_column} {direction}"
        
    def _get_filter_params(self) -> Tuple:
        """Get parameters for filter conditions"""
        params = []
        
        if self._current_filter:
            # Add search parameters
            search_params = self._get_search_params(self._current_filter)
            params.extend(search_params)
            
        return tuple(params)
        
    def _get_search_params(self, search_text: str) -> List:
        """Get search parameters (implemented by subclasses)"""
        return []
        
    def _query_to_dict(self, query: QSqlQuery) -> Dict:
        """Convert query result to dictionary (implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement _query_to_dict")
        
    def set_filter(self, filter_text: str):
        """Set search filter"""
        self._current_filter = filter_text
        self.dataChanged.emit()
        
    def set_sort(self, column: str, ascending: bool = True):
        """Set sort column and direction"""
        self._current_sort_column = column
        self._current_sort_ascending = ascending
        self.dataChanged.emit()
        
    def clear_filter(self):
        """Clear all filters"""
        self._current_filter = ""
        self.dataChanged.emit()
        
    def refresh(self):
        """Refresh data"""
        self.dataChanged.emit()
        
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.isOpen():
            self.connection.close()
            QSqlDatabase.removeDatabase(self.db_name)
```

This design provides a solid foundation for building the preferences components. Each component is designed to integrate seamlessly with the existing pagination framework while providing the specific functionality needed for preferences management.

The next step would be to create specific implementation plans for each panel (Replacement Panel, Translation History Panel, etc.) building on these foundational components.
