"""
Go to Path Dialog implementation for direct path navigation.
"""
from PySide6.QtCore import Qt, Signal, QDir, QStringListModel
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCompleter, QFileDialog, QMessageBox
)
import os
from lg import logger


class GotoPathDialog(QDialog):
    """
    Dialog for direct path navigation with path history and autocompletion.
    """
    # Signal emitted when a path is accepted by the user
    path_accepted = Signal(str)
    
    def __init__(self, parent=None, recent_paths=None):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget
            recent_paths: List of recently visited paths to populate history
        """
        super().__init__(parent)
        self.setWindowTitle("Go to Path")
        self.setMinimumWidth(500)
        self.recent_paths = recent_paths or []
        
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Path entry with label
        path_layout = QVBoxLayout()
        path_label = QLabel("Enter path:")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter a file system path...")
        
        # Set up autocompleter
        completer_model = QStringListModel(self.recent_paths + self._get_drive_roots())
        self.completer = QCompleter()
        self.completer.setModel(completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.path_edit.setCompleter(self.completer)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        layout.addLayout(path_layout)
        
        # Status label for feedback (hidden initially)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: red;")
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Browse button
        self.browse_button = QPushButton("Browse...")
        button_layout.addWidget(self.browse_button)
        
        # Push buttons to the right
        button_layout.addStretch()
        
        # Cancel and OK buttons
        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("Go")
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Set layout and initial focus
        self.setLayout(layout)
        self.path_edit.setFocus()
    
    def _setup_connections(self):
        """Connect signals and slots."""
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._on_path_accepted)
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.path_edit.textChanged.connect(self._on_path_text_changed)
    
    def _on_path_text_changed(self, text):
        """
        Handle path text changes, validate in real-time.
        
        Args:
            text: Current path text
        """
        # Hide status if empty
        if not text:
            self.status_label.hide()
            return
        
        # Validate path
        is_valid, message = self._validate_path(text)
        if not is_valid:
            self.status_label.setText(message)
            self.status_label.show()
            self.ok_button.setEnabled(False)
        else:
            self.status_label.hide()
            self.ok_button.setEnabled(True)
    
    def _validate_path(self, path):
        """
        Validate if the path exists and is accessible.
        
        Args:
            path: Path string to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        # Empty path check
        if not path:
            return False, "Please enter a path."
        
        # Normalize path
        path = os.path.expanduser(path)
        
        # Check if path exists
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"
        
        # Check if path is accessible
        try:
            if os.path.isdir(path):
                os.listdir(path)
            return True, ""
        except PermissionError:
            return False, f"Permission denied: {path}"
        except Exception as e:
            return False, f"Error accessing path: {str(e)}"
    
    def _on_path_accepted(self):
        """Handle OK button click - validate and accept path."""
        path = self.path_edit.text().strip()
        
        # Final validation
        is_valid, message = self._validate_path(path)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Path", message)
            return
        
        # Normalize path for consistency
        path = os.path.normpath(os.path.expanduser(path))
        
        # Update history with this valid path
        self._update_history(path)
        
        # Emit signal and close dialog
        self.path_accepted.emit(path)
        self.accept()
    
    def _on_browse_clicked(self):
        """Open file dialog to browse for a path."""
        # Start from current path or home directory
        start_dir = self.path_edit.text()
        if not os.path.exists(start_dir):
            start_dir = os.path.expanduser("~")
        
        # Open directory selection dialog
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", start_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if dir_path:
            self.path_edit.setText(dir_path)
            self._on_path_text_changed(dir_path)
    
    def _update_history(self, path):
        """
        Update path history with new valid path.
        
        Args:
            path: Path to add to history
        """
        # Skip if already at top of history
        if self.recent_paths and self.recent_paths[0] == path:
            return
            
        # Remove if exists elsewhere in list
        if path in self.recent_paths:
            self.recent_paths.remove(path)
            
        # Add to beginning of list
        self.recent_paths.insert(0, path)
        
        # Update completer with new history
        completer_model = QStringListModel(self.recent_paths + self._get_drive_roots())
        self.completer.setModel(completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.path_edit.setCompleter(self.completer)
    
    def _get_drive_roots(self):
        """
        Get the root drives or common paths for autocomplete.
        
        Returns:
            list: List of root directories or drives
        """
        # For macOS/Linux, add common directories
        common_paths = []
        
        # Add home directory and subdirectories
        home = os.path.expanduser("~")
        common_paths.append(home)
        
        # Common home subdirectories
        for subdir in ["Documents", "Downloads", "Desktop", "Pictures"]:
            path = os.path.join(home, subdir)
            if os.path.exists(path):
                common_paths.append(path)
                
        # Add root directory
        common_paths.append("/")
        
        # On Windows, add drive letters
        if os.name == 'nt':
            for drive in range(ord('A'), ord('Z') + 1):
                drive_letter = chr(drive) + ":\\"
                if os.path.exists(drive_letter):
                    common_paths.append(drive_letter)
        
        return common_paths
    
    def set_path(self, path):
        """
        Pre-populate the dialog with a path.
        
        Args:
            path: Path to pre-populate
        """
        self.path_edit.setText(path)
        self.path_edit.selectAll()
    
    def get_recent_paths(self):
        """
        Get the updated list of recent paths.
        
        Returns:
            list: Updated list of recent paths
        """
        return self.recent_paths
