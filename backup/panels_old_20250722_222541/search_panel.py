"""
Search panel for the PySide POEditor plugin.

This module contains the Search panel implementation.
"""

from lg import logger
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QToolBar, QPushButton, QComboBox, QTreeView, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QThreadPool
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem

from models.activity_models import SEARCH_ACTIVITY
from panels.panel_interface import PanelInterface

# Import typography and theme system
from themes.typography import get_typography_manager, FontRole, get_font
from themes.theme_manager import get_theme_manager


class SearchWorker:
    """Worker for performing searches in the background."""

    def __init__(self, search_query, search_path, file_patterns, case_sensitive):
        """
        Initialize the search worker.

        Args:
            search_query: The text to search for
            search_path: The directory path to search in
            file_patterns: File patterns to include
            case_sensitive: Whether the search is case sensitive
        """
        self.search_query = search_query
        self.search_path = search_path
        self.file_patterns = file_patterns
        self.case_sensitive = case_sensitive

    def run(self, result_callback):
        """
        Run the search operation.

        Args:
            result_callback: Callback to receive results
        """
        # Placeholder for actual search implementation
        # In a real implementation, this would search files
        import os
        import re
        import fnmatch
        from PySide6.QtCore import QCoreApplication

        results = []
        pattern = re.compile(self.search_query,
                            0 if self.case_sensitive else re.IGNORECASE)

        # Create a list of file patterns
        patterns = self.file_patterns.split(',')
        patterns = [p.strip() for p in patterns]

        # Walk through directories
        try:
            for root, _, files in os.walk(self.search_path):
                for file in files:
                    # Process events to keep UI responsive
                    QCoreApplication.processEvents()

                    # Check if file matches any pattern
                    if not any(fnmatch.fnmatch(file, p) for p in patterns):
                        continue

                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                if pattern.search(line):
                                    results.append({
                                        'file': file_path,
                                        'line': i,
                                        'text': line.strip(),
                                        'match': self.search_query
                                    })
                    except Exception as e:
                        logger.error(f"Error searching file {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error during search: {e}")

        # Return results
        result_callback(results)


class SearchPanel(PanelInterface):
    """
    Search panel for searching in translation files.
    """

    result_selected = Signal(dict)

    def __init__(self, parent=None, panel_id=None):
        """
        Initialize the search panel.

        Args:
            parent: The parent widget
            panel_id: The ID of this panel
        """
        super().__init__(parent)
        self.panel_id = panel_id
        self.api = None
        self.search_results = []
        self.thread_pool = QThreadPool()

        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()

        self._setup_ui()

        # Connect to typography and theme signals
        self._connect_typography_signals()

        # Apply initial typography and theme
        self.apply_typography()
        self.apply_theme()

        logger.info("SearchPanel initialized with typography integration")

    def _setup_ui(self):
        """Set up the user interface."""
        logger.info("Setting up Search panel UI")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title
        self.title_label = QLabel("SEARCH")
        self.title_label.setObjectName("panel_title")
        self.title_label.setAlignment(Qt.AlignLeft)
        # Remove hardcoded styling - will be applied via typography system

        # Search input area
        search_layout = QVBoxLayout()
        search_layout.setSpacing(5)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search term...")
        self.search_input.returnPressed.connect(self._perform_search)

        # Search path
        path_layout = QHBoxLayout()
        self.path_label = QLabel("In folder:")
        path_layout.addWidget(self.path_label)
        self.path_input = QLineEdit()
        self.path_input.setText(".")  # Current directory
        path_layout.addWidget(self.path_input)
        self.browse_button = QPushButton("...")
        self.browse_button.setMaximumWidth(30)
        self.browse_button.clicked.connect(self._browse_for_folder)
        path_layout.addWidget(self.browse_button)

        # Search options
        options_layout = QHBoxLayout()

        # File patterns
        options_layout.addWidget(QLabel("Files:"))
        self.file_pattern_input = QLineEdit()
        self.file_pattern_input.setText("*.po,*.pot,*.mo")
        options_layout.addWidget(self.file_pattern_input)

        # Case sensitive checkbox
        self.case_sensitive_check = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_check)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)
        options_layout.addWidget(self.search_button)

        # Results model and view
        self.results_model = QStandardItemModel()
        self.results_model.setHorizontalHeaderLabels(["File", "Line", "Text"])

        self.results_view = QTreeView()
        self.results_view.setModel(self.results_model)
        self.results_view.setUniformRowHeights(True)
        self.results_view.setAlternatingRowColors(True)
        self.results_view.doubleClicked.connect(self._result_double_clicked)

        # Status bar
        self.status_label = QLabel("Ready")

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addLayout(search_layout)
        search_layout.addWidget(self.search_input)
        search_layout.addLayout(path_layout)
        search_layout.addLayout(options_layout)
        layout.addWidget(self.results_view)
        layout.addWidget(self.status_label)

    def set_api(self, api):
        """
        Set the API for this panel.

        Args:
            api: The API instance
        """
        self.api = api

    def _browse_for_folder(self):
        """Open dialog to browse for a folder."""
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(
            self, "Select Search Directory", self.path_input.text()
        )
        if folder:
            self.path_input.setText(folder)

    def _perform_search(self):
        """Perform the search operation."""
        search_query = self.search_input.text()
        if not search_query:
            self.status_label.setText("Please enter a search term")
            return

        search_path = self.path_input.text()
        file_patterns = self.file_pattern_input.text()
        case_sensitive = self.case_sensitive_check.isChecked()

        # Clear previous results
        self.results_model.clear()
        self.results_model.setHorizontalHeaderLabels(["File", "Line", "Text"])
        self.search_results = []

        # Update status
        self.status_label.setText(f"Searching for '{search_query}'...")
        self.search_button.setEnabled(False)

        # Create and run worker
        worker = SearchWorker(search_query, search_path, file_patterns, case_sensitive)

        # Use a lambda to handle the results
        def handle_results(results):
            self._process_search_results(results)

        # Run in thread pool
        self.thread_pool.start(lambda: worker.run(handle_results))

    def _process_search_results(self, results):
        """
        Process and display search results.

        Args:
            results: List of search result dictionaries
        """
        # Store results
        self.search_results = results

        # Clear previous results
        self.results_model.clear()
        self.results_model.setHorizontalHeaderLabels(["File", "Line", "Text"])

        # Add results to model
        for result in results:
            file_item = QStandardItem(result['file'])
            line_item = QStandardItem(str(result['line']))
            text_item = QStandardItem(result['text'])

            self.results_model.appendRow([file_item, line_item, text_item])

        # Auto-size columns
        for i in range(3):
            self.results_view.resizeColumnToContents(i)

        # Update status
        count = len(results)
        self.status_label.setText(f"Found {count} result{'s' if count != 1 else ''}")
        self.search_button.setEnabled(True)

        # Log results
        logger.info(f"Search completed with {count} results")

    def _result_double_clicked(self, index):
        """
        Handle double-click on a search result.

        Args:
            index: The model index that was clicked
        """
        # Get the row of the clicked item
        row = index.row()

        if 0 <= row < len(self.search_results):
            result = self.search_results[row]

            # Emit signal with result info
            self.result_selected.emit(result)

            # Notify via API
            if self.api:
                self.api.emit_event("search_result_selected", result)

    def _connect_typography_signals(self):
        """Connect to typography and theme change signals."""
        try:
            # Connect to typography manager signals
            self.typography_manager.fonts_changed.connect(self._on_typography_changed)

            # Connect to theme manager signals
            self.theme_manager.theme_changed.connect(self._on_theme_changed)

            logger.info("SearchPanel connected to typography and theme change signals")
        except Exception as e:
            logger.error(f"Failed to connect to typography signals in SearchPanel: {e}")

    def apply_typography(self):
        """Public method to apply typography to the search panel.

        This method is part of the typography integration public API.
        It applies the current typography settings to all components.
        """
        self._apply_typography()

    def apply_theme(self):
        """Public method to apply theme styling to the search panel.

        This method is part of the theme integration public API.
        It applies the current theme styles to all components.
        """
        self._apply_theme_styling()

    def _apply_typography(self):
        """Apply typography to all search panel components."""
        try:
            logger.info("Applying typography to SearchPanel")

            # Apply title font (PANEL_TITLE role)
            self.title_label.setFont(get_font(FontRole.PANEL_TITLE))

            # Apply label fonts (SMALL role for form labels)
            self.path_label.setFont(get_font(FontRole.SMALL))

            # Create and apply file pattern label font if needed
            file_labels = self.findChildren(QLabel)
            for label in file_labels:
                if label.text() == "Files:":
                    label.setFont(get_font(FontRole.SMALL))

            # Apply input field fonts (BODY role for main inputs)
            self.search_input.setFont(get_font(FontRole.BODY))
            self.path_input.setFont(get_font(FontRole.BODY))
            self.file_pattern_input.setFont(get_font(FontRole.BODY))

            # Apply button font (BUTTON role)
            self.browse_button.setFont(get_font(FontRole.BUTTON))
            self.search_button.setFont(get_font(FontRole.BUTTON))

            # Apply checkbox font (SMALL role for options)
            self.case_sensitive_check.setFont(get_font(FontRole.SMALL))

            # Apply results view font (BODY role for content)
            self.results_view.setFont(get_font(FontRole.BODY))

            # Apply status label font (CAPTION role for status text)
            self.status_label.setFont(get_font(FontRole.CAPTION))

            logger.info("Typography applied successfully to SearchPanel")

        except Exception as e:
            logger.error(f"Failed to apply typography to SearchPanel: {e}")

    def _apply_theme_styling(self):
        """Apply theme-based styling to search panel components."""
        try:
            logger.info("Applying theme styling to SearchPanel")

            # Set object names for CSS targeting
            self.title_label.setObjectName("panel_title")
            self.search_input.setObjectName("search_input")
            self.path_input.setObjectName("search_input")
            self.file_pattern_input.setObjectName("search_input")
            self.browse_button.setObjectName("primary_button")
            self.search_button.setObjectName("primary_button")
            self.results_view.setObjectName("tree_view")
            self.status_label.setObjectName("status_label")

            # Clear any existing stylesheets to ensure global theme takes precedence
            self.title_label.setStyleSheet("")
            self.search_input.setStyleSheet("")
            self.path_input.setStyleSheet("")
            self.file_pattern_input.setStyleSheet("")
            self.browse_button.setStyleSheet("")
            self.search_button.setStyleSheet("")
            self.results_view.setStyleSheet("")
            self.status_label.setStyleSheet("")

            logger.info("Theme styling applied successfully to SearchPanel")

        except Exception as e:
            logger.error(f"Failed to apply theme styling to SearchPanel: {e}")

    def _on_typography_changed(self):
        """Handle typography change events."""
        logger.info("SearchPanel typography changed, updating")
        self._apply_typography()

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change events."""
        logger.info(f"SearchPanel theme changed to {theme_name}, updating styling")
        self._apply_theme_styling()
