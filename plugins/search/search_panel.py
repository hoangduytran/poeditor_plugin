"""
Search Panel for the POEditor application.

This panel provides advanced search capabilities including file name search,
content search, and pattern matching with search history.
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QCheckBox, QComboBox,
    QTextEdit, QSplitter, QGroupBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

from lg import logger
from core.file_filter import FileFilter
from core.directory_model import DirectoryModel


class SearchWorker(QThread):
    """Worker thread for performing searches without blocking UI."""

    # Signals
    result_found = Signal(str, str, int, str)  # file_path, file_name, line_num, line_content
    search_finished = Signal(int)  # total_results
    progress_updated = Signal(int, int)  # current, total

    def __init__(self, search_term: str, search_path: str, search_options: Dict[str, Any]):
        super().__init__()
        self.search_term = search_term
        self.search_path = search_path
        self.search_options = search_options
        self.should_stop = False

    def run(self) -> None:
        """Execute the search operation."""
        try:
            if self.search_options.get('content_search', False):
                self.search_in_content()
            else:
                self.search_file_names()
        except Exception as e:
            logger.error(f"Search worker error: {e}")

    def search_file_names(self) -> None:
        """Search for files by name."""
        results_count = 0
        file_filter = FileFilter(
            self.search_term,
            self.search_options.get('include_hidden', False)
        )

        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(self.search_path):
                if self.should_stop:
                    break

                # Filter directories if needed
                if not self.search_options.get('include_hidden', False):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file_name in files:
                    if self.should_stop:
                        break

                    if file_filter.matches(file_name, False):
                        file_path = os.path.join(root, file_name)
                        self.result_found.emit(file_path, file_name, 0, "")
                        results_count += 1

            self.search_finished.emit(results_count)

        except Exception as e:
            logger.error(f"File name search error: {e}")

    def search_in_content(self) -> None:
        """Search for content within files."""
        results_count = 0
        pattern = None

        try:
            # Compile regex pattern if using regex
            if self.search_options.get('use_regex', False):
                flags = re.IGNORECASE if not self.search_options.get('case_sensitive', False) else 0
                pattern = re.compile(self.search_term, flags)

            # Walk through directory tree
            for root, dirs, files in os.walk(self.search_path):
                if self.should_stop:
                    break

                # Filter directories
                if not self.search_options.get('include_hidden', False):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file_name in files:
                    if self.should_stop:
                        break

                    file_path = os.path.join(root, file_name)

                    # Skip binary files
                    if not self.is_text_file(file_path):
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if self.should_stop:
                                    break

                                # Search in line
                                if self.search_in_line(line, pattern):
                                    self.result_found.emit(
                                        file_path, file_name, line_num, line.strip()
                                    )
                                    results_count += 1

                    except Exception as e:
                        logger.debug(f"Error reading file {file_path}: {e}")
                        continue

            self.search_finished.emit(results_count)

        except Exception as e:
            logger.error(f"Content search error: {e}")

    def search_in_line(self, line: str, pattern: Optional[re.Pattern]) -> bool:
        """Check if search term matches in the line."""
        if pattern:
            return pattern.search(line) is not None
        else:
            # Simple text search
            if self.search_options.get('case_sensitive', False):
                return self.search_term in line
            else:
                return self.search_term.lower() in line.lower()

    def is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file."""
        try:
            # Check file extension
            text_extensions = {
                '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md',
                '.rst', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log'
            }

            ext = Path(file_path).suffix.lower()
            if ext in text_extensions:
                return True

            # Check file content (read first few bytes)
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' not in chunk

        except Exception:
            return False

    def stop(self) -> None:
        """Stop the search operation."""
        self.should_stop = True


class SearchPanel(QWidget):
    """
    Advanced search panel with file name and content search capabilities.

    Features:
    - File name pattern search
    - Content search within files
    - Regular expression support
    - Case sensitivity options
    - Search history
    - Progress indication
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core components
        self.current_path = str(Path.home())
        self.search_worker: Optional[SearchWorker] = None
        self.search_history: List[str] = []

        # UI components
        self.search_input: Optional[QComboBox] = None
        self.search_button: Optional[QPushButton] = None
        self.stop_button: Optional[QPushButton] = None
        self.clear_button: Optional[QPushButton] = None
        self.content_search_cb: Optional[QCheckBox] = None
        self.case_sensitive_cb: Optional[QCheckBox] = None
        self.regex_cb: Optional[QCheckBox] = None
        self.hidden_files_cb: Optional[QCheckBox] = None
        self.results_list: Optional[QListWidget] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None

        # Initialize UI
        self.setup_ui()

        logger.info("SearchPanel initialized")

    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Search input group
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)

        # Search input with history
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_input.lineEdit().returnPressed.connect(self.start_search)
        search_layout.addWidget(self.search_input)

        # Search options
        options_layout = QVBoxLayout()

        self.content_search_cb = QCheckBox("Search in file content")
        self.content_search_cb.setChecked(True)
        options_layout.addWidget(self.content_search_cb)

        self.case_sensitive_cb = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_cb)

        self.regex_cb = QCheckBox("Use regular expressions")
        options_layout.addWidget(self.regex_cb)

        self.hidden_files_cb = QCheckBox("Include hidden files")
        options_layout.addWidget(self.hidden_files_cb)

        search_layout.addLayout(options_layout)

        # Search buttons
        button_layout = QHBoxLayout()

        self.search_button = QPushButton("🔍 Search")
        self.search_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.search_button)

        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.clear_button = QPushButton("🗑 Clear")
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)

        search_layout.addLayout(button_layout)
        layout.addWidget(search_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to search")
        self.status_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.status_label)

        # Results list
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)

        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_double_clicked)
        results_layout.addWidget(self.results_list)

        layout.addWidget(results_group)

        logger.debug("SearchPanel UI setup complete")

    def start_search(self) -> None:
        """Start a new search operation."""
        search_term = self.search_input.currentText().strip()
        if not search_term:
            return

        # Add to history
        if search_term not in self.search_history:
            self.search_history.append(search_term)
            self.search_input.addItem(search_term)

        # Clear previous results
        self.results_list.clear()

        # Prepare search options
        search_options = {
            'content_search': self.content_search_cb.isChecked(),
            'case_sensitive': self.case_sensitive_cb.isChecked(),
            'use_regex': self.regex_cb.isChecked(),
            'include_hidden': self.hidden_files_cb.isChecked()
        }

        # Update UI state
        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Searching for '{search_term}'...")

        # Start search worker
        self.search_worker = SearchWorker(search_term, self.current_path, search_options)
        self.search_worker.result_found.connect(self.on_result_found)
        self.search_worker.search_finished.connect(self.on_search_finished)
        self.search_worker.start()

        logger.info(f"Started search for: {search_term}")

    def stop_search(self) -> None:
        """Stop the current search operation."""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.stop()
            self.search_worker.wait(3000)  # Wait up to 3 seconds

        self.on_search_finished(self.results_list.count())
        logger.info("Search stopped by user")

    def clear_results(self) -> None:
        """Clear search results."""
        self.results_list.clear()
        self.status_label.setText("Ready to search")
        logger.debug("Search results cleared")

    def on_result_found(self, file_path: str, file_name: str, line_num: int, line_content: str) -> None:
        """Handle a search result."""
        if line_num > 0:
            # Content search result
            display_text = f"📄 {file_name}:{line_num} - {line_content[:100]}..."
        else:
            # File name search result
            display_text = f"📄 {file_name}"

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, {'path': file_path, 'line': line_num})
        item.setToolTip(file_path)

        self.results_list.addItem(item)

    def on_search_finished(self, total_results: int) -> None:
        """Handle search completion."""
        # Update UI state
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        # Update status
        if total_results == 0:
            self.status_label.setText("No results found")
        elif total_results == 1:
            self.status_label.setText("1 result found")
        else:
            self.status_label.setText(f"{total_results} results found")

        logger.info(f"Search completed: {total_results} results")

    def on_result_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on search result."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            file_path = data['path']
            line_num = data.get('line', 0)
            logger.info(f"Opening file: {file_path} at line {line_num}")
            # TODO: Integrate with tab manager to open file

    def set_search_path(self, path: str) -> None:
        """Set the search root path."""
        self.current_path = path
        logger.debug(f"Search path set to: {path}")

    # Public API methods for commands
    def find_in_files(self, search_term: str) -> None:
        """Start a find in files operation."""
        self.search_input.setCurrentText(search_term)
        self.content_search_cb.setChecked(True)
        self.start_search()
