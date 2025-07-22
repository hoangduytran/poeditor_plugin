"""
Explorer Panel Widget

A clean file explorer panel using the proven Phase 1 architecture.
No Qt model complexity - simple and reliable.
"""

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
