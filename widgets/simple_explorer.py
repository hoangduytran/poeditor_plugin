"""
Simple Explorer Widget

Clean file explorer widget with reliable filtering.
Uses simple list view instead of complex tree model chains.

Features:
- Breadcrumb navigation for easy directory browsing
- File filtering with pattern support
- Directories always displayed first in sorting (both in normal and filtered views)
- Clean, consistent appearance without alternating row colors
- Keyboard shortcuts (F5: refresh, Ctrl+L: focus filter, Alt+Up: parent directory)
- Theme integration via Qt stylesheet system
"""

import os
import sys
from typing import List
from pathlib import Path

# Ensure we can import core modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lg import logger

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                              QPushButton, QListWidget, QListWidgetItem, QLabel,
                              QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from core.file_filter import FileFilter
from core.directory_model import DirectoryModel, FileInfo
from core.explorer_settings import ExplorerSettings
from lg import logger


class SimpleExplorer(QWidget):
    """Clean file explorer widget."""

    # Signals
    file_opened = Signal(str)
    directory_changed = Signal(str)
    selection_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize settings
        self.settings = ExplorerSettings()

        # State
        self.current_path = self.settings.get("last_path", os.path.expanduser("~"))
        self.current_filter = FileFilter()

        # UI Components
        self.breadcrumb_scroll = QScrollArea()
        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = QHBoxLayout(self.breadcrumb_widget)
        self.path_label = QLabel()
        self.filter_input = QLineEdit()
        self.clear_button = QPushButton("Clear")
        self.file_list = QListWidget()
        self.status_label = QLabel()

        # Apply settings
        self._apply_settings()

        self._setup_ui()
        self._connect_signals()
        self._setup_keyboard_shortcuts()
        self.refresh()

        logger.info("SimpleExplorer initialized with breadcrumb navigation and settings")

    def _apply_settings(self):
        """Apply user settings to the widget."""
        # Apply font size
        font_size = self.settings.get("font_size", 11)
        font = QFont()
        font.setPointSize(font_size)
        self.setFont(font)

        # Show hidden files setting will be used in refresh
        logger.debug(f"Applied settings: font_size={font_size}")

    def save_settings(self):
        """Save current state to settings."""
        self.settings.set("last_path", self.current_path)
        self.settings.save()
        logger.debug("Settings saved")

    def _setup_ui(self):
        """Setup clean UI layout with breadcrumb navigation."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Breadcrumb navigation
        self._setup_breadcrumb_widget()
        layout.addWidget(self.breadcrumb_scroll)

        # Filter input row
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)

        self.filter_input.setPlaceholderText("Filter files (e.g., *.txt, *.py)")
        self.clear_button.setMaximumWidth(60)

        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_button)

        layout.addLayout(filter_layout)

        # File list with theme integration
        self.file_list.setObjectName("explorer_file_list")
        self.filter_input.setObjectName("search_input")
        self.clear_button.setObjectName("secondary_button")

        # Disable alternating row colors for a cleaner, more consistent appearance
        # This is an intentional design choice to maintain a uniform look
        # The theme system handles styling through CSS instead
        self.file_list.setAlternatingRowColors(False)
        layout.addWidget(self.file_list)

        # Status bar
        self.status_label.setProperty("class", "status-label")  # Use CSS class instead of hardcoded style
        layout.addWidget(self.status_label)

    def _setup_breadcrumb_widget(self):
        """Setup breadcrumb navigation widget."""
        # Configure scroll area
        self.breadcrumb_scroll.setWidget(self.breadcrumb_widget)
        self.breadcrumb_scroll.setWidgetResizable(True)
        self.breadcrumb_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.breadcrumb_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.breadcrumb_scroll.setMaximumHeight(40)
        self.breadcrumb_scroll.setProperty("class", "breadcrumb-scroll")  # Use CSS class instead of hardcoded style

        # Configure breadcrumb layout
        self.breadcrumb_layout.setContentsMargins(5, 5, 5, 5)
        self.breadcrumb_layout.setSpacing(0)
        self.breadcrumb_layout.addStretch()  # Push items to left initially

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better UX."""
        # Refresh shortcut (F5)
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh)

        # Focus filter shortcut (Ctrl+L)
        focus_filter_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_filter_shortcut.activated.connect(self.filter_input.setFocus)

        # Up directory shortcut (Alt+Up)
        up_shortcut = QShortcut(QKeySequence("Alt+Up"), self)
        up_shortcut.activated.connect(self._go_up_directory)

    def _connect_signals(self):
        """Connect UI signals."""
        self.filter_input.returnPressed.connect(self._apply_filter)
        self.clear_button.clicked.connect(self._clear_filter)
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.file_list.itemSelectionChanged.connect(self._on_selection_changed)

    def set_path(self, path: str):
        """Navigate to a directory."""
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            QMessageBox.warning(self, "Error", f"Path does not exist: {path}")
            return

        if not os.path.isdir(path):
            logger.warning(f"Path is not a directory: {path}")
            QMessageBox.warning(self, "Error", f"Path is not a directory: {path}")
            return

        self.current_path = path
        # Save path to settings
        self.settings.set("last_path", path)
        self.refresh()
        self.directory_changed.emit(path)
        logger.info(f"Navigated to: {path}")

    def _apply_filter(self):
        """
        Apply the filter and refresh the view.

        The filtered results will maintain proper sorting with directories
        displayed first, followed by files, both in alphabetical order.
        This preserves the consistent navigation experience regardless of filter state.
        """
        pattern = self.filter_input.text().strip()
        # Add to filter history
        if pattern:
            self.settings.add_to_filter_history(pattern)

        show_hidden = self.settings.get("show_hidden_files", False)
        self.current_filter = FileFilter(pattern, include_hidden=show_hidden)
        self.refresh()
        logger.info(f"Applied filter: '{pattern}'")

    def _clear_filter(self):
        """Clear the filter and show all files."""
        self.filter_input.clear()
        self.current_filter = FileFilter()
        self.refresh()
        logger.info("Filter cleared")

    def refresh(self):
        """
        Refresh the file list with current path and filter settings.

        This method implements a consistent sorting behavior:
        - Directories are always displayed first
        - Files are displayed after directories
        - Both groups are sorted alphabetically
        - This sorting applies to both normal and filtered views

        The explorer also maintains a clean visual appearance by:
        - Not using alternating row colors (setAlternatingRowColors(False))
        - Using consistent theme styling through Qt stylesheets
        """
        try:
            # Update breadcrumb navigation
            self._update_breadcrumb()

            # Load directory with settings
            show_hidden = self.settings.get("show_hidden_files", False)
            directory = DirectoryModel(self.current_path, include_hidden=show_hidden)
            files = directory.filter(self.current_filter)

            # Update UI
            self.file_list.clear()

            # Sort: directories first, then files, alphabetically
            sorted_files = sorted(files, key=lambda f: (not f.is_directory, f.name.lower()))

            for file_info in sorted_files:
                self._add_file_item(file_info)

            # Update status
            total_files = len([f for f in files if not f.is_directory])
            total_dirs = len([f for f in files if f.is_directory])

            if self.current_filter.is_empty():
                status = f"{total_dirs} folders, {total_files} files"
            else:
                status = f"{total_dirs} folders, {total_files} files (filtered)"

            self.status_label.setText(status)

            logger.debug(f"Refreshed view: {len(files)} items displayed")

        except Exception as e:
            logger.error(f"Error refreshing view: {e}")
            QMessageBox.critical(self, "Error", f"Error refreshing view: {e}")

    def _update_breadcrumb(self):
        """Update breadcrumb navigation buttons."""
        # Clear existing buttons
        for i in reversed(range(self.breadcrumb_layout.count())):
            item = self.breadcrumb_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        # Get path components
        path_obj = Path(self.current_path)
        parts = path_obj.parts

        current_path = ""
        for i, part in enumerate(parts):
            current_path = str(Path(current_path, part)) if current_path else part

            # Create breadcrumb button
            button = QPushButton(part if part != "/" else "Root")
            button.setFlat(True)
            button.setProperty("class", "breadcrumb-button")  # Use CSS class instead of hardcoded style

            # Store path in button for navigation
            button.setProperty("navigation_path", current_path)
            button.clicked.connect(lambda checked, path=current_path: self.set_path(path))

            self.breadcrumb_layout.addWidget(button)

            # Add separator (except for last item)
            if i < len(parts) - 1:
                separator = QLabel(" › ")
                separator.setProperty("class", "breadcrumb-separator")  # Use CSS class instead of hardcoded style
                self.breadcrumb_layout.addWidget(separator)

        # Add stretch to push items to the left
        self.breadcrumb_layout.addStretch()

    def _go_up_directory(self):
        """Navigate to parent directory."""
        parent = str(Path(self.current_path).parent)
        if parent != self.current_path:  # Don't go above root
            self.set_path(parent)

    def closeEvent(self, event):
        """Handle widget close event."""
        self.save_settings()
        super().closeEvent(event)

    def __del__(self):
        """Handle widget deletion."""
        # Settings are always initialized in __init__
        self.save_settings()

    def _add_file_item(self, file_info: FileInfo):
        """Add a file item to the list."""
        item = QListWidgetItem(file_info.name)
        item.setData(Qt.ItemDataRole.UserRole, file_info.path)
        item.setData(Qt.ItemDataRole.UserRole + 1, file_info.is_directory)

        # Set icon based on type
        if file_info.is_directory:
            try:
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
            except:
                # Fallback to a simple folder prefix
                item.setText(f"📁 {file_info.name}")
            item.setToolTip(f"Directory: {file_info.name}")
        else:
            try:
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
            except:
                # Fallback to a simple file prefix
                item.setText(f"📄 {file_info.name}")
            # Format size
            size_str = self._format_size(file_info.size)
            modified_str = file_info.modified.strftime("%Y-%m-%d %H:%M")
            item.setToolTip(f"File: {file_info.name}\\nSize: {size_str}\\nModified: {modified_str}")

        # Dim hidden files
        if file_info.is_hidden:
            font = item.font()
            font.setItalic(True)
            item.setFont(font)

        self.file_list.addItem(item)

    def _format_size(self, size: int) -> str:
        """Format file size in human readable format."""
        size_float = float(size)  # Convert to float for division
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} TB"

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on items."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        is_directory = item.data(Qt.ItemDataRole.UserRole + 1)

        if is_directory:
            self.set_path(file_path)
        else:
            self.file_opened.emit(file_path)
            logger.info(f"File opened: {file_path}")

    def _on_selection_changed(self):
        """Handle selection changes."""
        selected_items = self.file_list.selectedItems()
        selected_paths = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        self.selection_changed.emit(selected_paths)

    def get_current_path(self) -> str:
        """Get the current directory path."""
        return self.current_path

    def get_selected_files(self) -> List[str]:
        """Get list of selected file paths."""
        selected_items = self.file_list.selectedItems()
        return [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
