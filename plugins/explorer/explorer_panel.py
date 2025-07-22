"""
Explorer Panel for the POEditor application.

This panel provides file and directory exploration capabilities using the clean
architecture from Phase 1. It integrates with the core file filtering and directory
model systems.
"""

import os
from pathlib import Path
from typing import Optional, List
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
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Core components (direct access as per rules)
        self.current_path = str(Path.home())
        self.file_filter = FileFilter()
        self.directory_model = DirectoryModel(self.current_path)
        
        # UI components
        self.path_label: Optional[QLabel] = None
        self.filter_input: Optional[QLineEdit] = None
        self.hidden_checkbox: Optional[QCheckBox] = None
        self.refresh_button: Optional[QPushButton] = None
        self.file_tree: Optional[QTreeWidget] = None
        
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
        if not hasattr(self, '_filter_timer'):
            self._filter_timer = QTimer()
            self._filter_timer.setSingleShot(True)
            self._filter_timer.timeout.connect(self.load_directory)
        
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

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog, QLabel, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from lg import logger

# Import the clean core components
from core.file_filter import FileFilter
from core.directory_model import DirectoryModel

# Import theme system
from themes.typography import get_font, FontRole


class ExplorerPanel(QWidget):
    """
    File explorer panel with clean architecture.
    
    Uses the proven filtering system from Phase 1.
    """
    
    # Signals
    file_selected = Signal(str)  # Emitted when user selects a file
    directory_changed = Signal(str)  # Emitted when directory changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State
        self.current_directory = str(Path.home())
        self.file_filter = FileFilter()
        self.directory_model = DirectoryModel(self.current_directory)
        
        # UI components
        self.path_input = None
        self.browse_button = None
        self.filter_input = None
        self.hidden_checkbox = None
        self.file_list = None
        self.status_label = None
        
        self.setup_ui()
        self.load_directory()
        
        logger.info("ExplorerPanel initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Directory path input
        self.path_input = QLineEdit(self.current_directory)
        self.path_input.setFont(get_font(FontRole.BODY))
        self.path_input.returnPressed.connect(self.on_path_changed)
        header_layout.addWidget(self.path_input)
        
        # Browse button
        self.browse_button = QPushButton("Browse")
        self.browse_button.setFont(get_font(FontRole.BODY))
        self.browse_button.clicked.connect(self.on_browse_clicked)
        header_layout.addWidget(self.browse_button)
        
        layout.addLayout(header_layout)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter:")
        filter_label.setFont(get_font(FontRole.BODY))
        filter_layout.addWidget(filter_label)
        
        self.filter_input = QLineEdit()
        self.filter_input.setFont(get_font(FontRole.BODY))
        self.filter_input.setPlaceholderText("*.txt, *.py, doc, etc.")
        self.filter_input.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_input)
        
        self.hidden_checkbox = QCheckBox("Show hidden")
        self.hidden_checkbox.setFont(get_font(FontRole.BODY))
        self.hidden_checkbox.stateChanged.connect(self.on_hidden_changed)
        filter_layout.addWidget(self.hidden_checkbox)
        
        layout.addLayout(filter_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setFont(get_font(FontRole.BODY))
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.file_list)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setFont(get_font(FontRole.CAPTION))
        layout.addWidget(self.status_label)
    
    def load_directory(self):
        """Load and display files from the current directory."""
        try:
            # Update directory model
            self.directory_model = DirectoryModel(
                self.current_directory, 
                include_hidden=self.hidden_checkbox.isChecked() if self.hidden_checkbox else False
            )
            
            # Load files
            files = self.directory_model.load()
            
            # Apply filter
            filtered_files = []
            for file_info in files:
                if self.file_filter.matches(file_info.name, file_info.is_directory):
                    filtered_files.append(file_info)
            
            # Update UI
            self.file_list.clear()
            
            # Add parent directory entry if not at root
            if self.current_directory != "/":
                parent_item = QListWidgetItem(".. (Parent Directory)")
                parent_item.setData(Qt.ItemDataRole.UserRole, "..")
                font = parent_item.font()
                font.setBold(True)
                parent_item.setFont(font)
                self.file_list.addItem(parent_item)
            
            # Add files and directories
            for file_info in filtered_files:
                item_text = file_info.name
                if file_info.is_directory:
                    item_text = f"📁 {file_info.name}/"
                else:
                    item_text = f"📄 {file_info.name}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, file_info.path)
                
                # Style directories differently
                if file_info.is_directory:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                
                self.file_list.addItem(item)
            
            # Update status
            total_files = len([f for f in filtered_files if not f.is_directory])
            total_dirs = len([f for f in filtered_files if f.is_directory])
            self.status_label.setText(f"{total_dirs} folders, {total_files} files")
            
            # Update path input
            self.path_input.setText(self.current_directory)
            
            logger.info(f"Loaded directory: {self.current_directory} ({len(filtered_files)} items)")
            
        except Exception as e:
            logger.error(f"Failed to load directory {self.current_directory}: {e}")
            self.status_label.setText(f"Error: {e}")
    
    def on_path_changed(self):
        """Handle path input change."""
        new_path = self.path_input.text().strip()
        if new_path and os.path.isdir(new_path):
            self.current_directory = os.path.abspath(new_path)
            self.load_directory()
            self.directory_changed.emit(self.current_directory)
        else:
            # Revert to current directory
            self.path_input.setText(self.current_directory)
    
    def on_browse_clicked(self):
        """Handle browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Directory", 
            self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.load_directory()
            self.directory_changed.emit(self.current_directory)
    
    def on_filter_changed(self, text):
        """Handle filter input change."""
        self.file_filter = FileFilter(
            pattern=text,
            include_hidden=self.hidden_checkbox.isChecked() if self.hidden_checkbox else False
        )
        self.load_directory()
    
    def on_hidden_changed(self, state):
        """Handle hidden files checkbox change."""
        include_hidden = state == Qt.CheckState.Checked.value
        self.file_filter = FileFilter(
            pattern=self.filter_input.text() if self.filter_input else "",
            include_hidden=include_hidden
        )
        self.load_directory()
    
    def on_item_double_clicked(self, item):
        """Handle item double-click."""
        path = item.data(Qt.ItemDataRole.UserRole)
        
        if path == "..":
            # Navigate to parent directory
            parent = os.path.dirname(self.current_directory)
            if parent != self.current_directory:  # Avoid infinite loop at root
                self.current_directory = parent
                self.load_directory()
                self.directory_changed.emit(self.current_directory)
        elif os.path.isdir(path):
            # Navigate to subdirectory
            self.current_directory = path
            self.load_directory()
            self.directory_changed.emit(self.current_directory)
        else:
            # File selected
            self.file_selected.emit(path)
    
    def on_selection_changed(self):
        """Handle selection change."""
        current_item = self.file_list.currentItem()
        if current_item:
            path = current_item.data(Qt.ItemDataRole.UserRole)
            if path and path != ".." and os.path.isfile(path):
                self.file_selected.emit(path)
    
    def set_directory(self, path: str):
        """
        Set the current directory programmatically.
        
        Args:
            path: Directory path to set
        """
        if os.path.isdir(path):
            self.current_directory = os.path.abspath(path)
            self.load_directory()
            self.directory_changed.emit(self.current_directory)
    
    def get_selected_file(self) -> str:
        """
        Get the currently selected file path.
        
        Returns:
            Path to selected file, or empty string if none selected
        """
        current_item = self.file_list.currentItem()
        if current_item:
            path = current_item.data(Qt.ItemDataRole.UserRole)
            if path and path != ".." and os.path.isfile(path):
                return path
        return ""
