"""
Explorer Panel for the POEditor application.

This panel provides file and directory exploration capabilities using the clean
architecture from Phase 1. It integrates with the core file filtering and directory
model systems.
"""

import os
from pathlib import Path
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QCheckBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from lg import logger
from core.file_filter import FileFilter
from core.directory_model import DirectoryModel, FileInfo


class ExplorerPanel(QWidget):
    """
    File explorer panel using clean Phase 1 architecture.

    Features:
    - Directory browsing with tree view
    - File filtering with patterns
    - Hidden file toggle
    - Clean separation of concerns
    - Integration with core filtering system
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Core components (direct access as per rules)
        self.current_path = str(Path.home())
        self.file_filter = FileFilter()
        self.directory_model = DirectoryModel(self.current_path)

        # Timer for debounced filtering
        self._filter_timer = QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self.load_directory)

        # UI components - will be initialized in setup_ui()

        # Initialize UI
        self.setup_ui()
        self.load_directory()

        logger.info("ExplorerPanel initialized")

    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Header with current path
        self.path_label = QLabel(self.current_path)
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(self.path_label)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(4)

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter files (e.g., *.txt, *.py)")
        self.filter_input.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_input)

        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setMaximumWidth(30)
        self.refresh_button.setToolTip("Refresh directory")
        self.refresh_button.clicked.connect(self.refresh)
        filter_layout.addWidget(self.refresh_button)

        layout.addLayout(filter_layout)

        # Hidden files checkbox
        self.hidden_checkbox = QCheckBox("Show hidden files")
        self.hidden_checkbox.toggled.connect(self.on_hidden_toggled)
        layout.addWidget(self.hidden_checkbox)

        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Modified"])
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.file_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.file_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.file_tree)

        logger.debug("ExplorerPanel UI setup complete")

    def load_directory(self) -> None:
        """Load and display the current directory contents."""
        try:
            logger.debug(f"Loading directory: {self.current_path}")

            # Update path label
            self.path_label.setText(self.current_path)

            # Update directory model
            self.directory_model = DirectoryModel(
                self.current_path,
                self.hidden_checkbox.isChecked()
            )

            # Load files
            files = self.directory_model.load()

            # Clear and populate tree
            self.file_tree.clear()

            # Add parent directory item if not at root
            if self.current_path != str(Path(self.current_path).anchor):
                parent_item = QTreeWidgetItem(["📁 ..", "", ""])
                parent_item.setData(0, Qt.ItemDataRole.UserRole, str(Path(self.current_path).parent))
                self.file_tree.addTopLevelItem(parent_item)

            # Filter and add files
            filtered_files = self.filter_files(files)
            for file_info in filtered_files:
                self.add_file_item(file_info)

            logger.info(f"Loaded {len(filtered_files)} files from {self.current_path}")

        except Exception as e:
            logger.error(f"Failed to load directory {self.current_path}: {e}")

    def filter_files(self, files: List[FileInfo]) -> List[FileInfo]:
        """Filter files using the file filter."""
        filtered = []
        for file_info in files:
            if self.file_filter.matches(file_info.name, file_info.is_directory):
                filtered.append(file_info)
        return filtered

    def add_file_item(self, file_info: FileInfo) -> None:
        """Add a file item to the tree."""
        # Format file size
        size_text = ""
        if not file_info.is_directory:
            if file_info.size < 1024:
                size_text = f"{file_info.size} B"
            elif file_info.size < 1024 * 1024:
                size_text = f"{file_info.size // 1024} KB"
            else:
                size_text = f"{file_info.size // (1024 * 1024)} MB"

        # Format modified time
        modified_text = file_info.modified.strftime("%Y-%m-%d %H:%M")

        # Create item
        icon = "📁" if file_info.is_directory else "📄"
        name_text = f"{icon} {file_info.name}"

        item = QTreeWidgetItem([name_text, size_text, modified_text])
        item.setData(0, Qt.ItemDataRole.UserRole, file_info.path)

        # Style hidden files
        if file_info.is_hidden:
            font = item.font(0)
            font.setItalic(True)
            item.setFont(0, font)

        self.file_tree.addTopLevelItem(item)

    def on_filter_changed(self, pattern: str) -> None:
        """Handle filter pattern change."""
        self.file_filter = FileFilter(pattern, self.hidden_checkbox.isChecked())

        # Debounce the reload
        self._filter_timer.start(300)  # 300ms delay

        logger.debug(f"Filter changed to: {pattern}")

    def on_hidden_toggled(self, checked: bool) -> None:
        """Handle hidden files checkbox toggle."""
        self.file_filter = FileFilter(self.filter_input.text(), checked)
        self.load_directory()
        logger.debug(f"Show hidden files: {checked}")

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item double-click for navigation."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.isdir(file_path):
            self.navigate_to(file_path)

    def navigate_to(self, path: str) -> None:
        """Navigate to a specific directory."""
        try:
            resolved_path = str(Path(path).resolve())
            if os.path.isdir(resolved_path):
                self.current_path = resolved_path
                self.load_directory()
                logger.info(f"Navigated to: {resolved_path}")
            else:
                logger.warning(f"Invalid directory: {path}")
        except Exception as e:
            logger.error(f"Failed to navigate to {path}: {e}")

    # Public API methods for commands
    def refresh(self) -> None:
        """Refresh the current directory."""
        logger.info("Refreshing explorer")
        self.load_directory()

    def toggle_hidden_files(self) -> None:
        """Toggle hidden files visibility."""
        self.hidden_checkbox.setChecked(not self.hidden_checkbox.isChecked())

    def set_filter_pattern(self, pattern: str) -> None:
        """Set the filter pattern."""
        self.filter_input.setText(pattern)
