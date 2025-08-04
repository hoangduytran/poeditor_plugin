"""
Bookmark Management Dialog

This dialog allows users to manage their bookmarked locations.
Features include adding, editing, deleting, and organizing bookmarks.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QFrame, QFileDialog,
    QDialogButtonBox, QMessageBox, QGroupBox, QSplitter,
    QTextEdit, QWidget, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon

from services.location_manager import LocationManager, LocationBookmark

logger = logging.getLogger(__name__)


class BookmarkItem(QListWidgetItem):
    """Custom list widget item for bookmarks."""

    def __init__(self, bookmark: LocationBookmark):
        super().__init__()
        self.bookmark = bookmark
        self._update_display()

    def _update_display(self) -> None:
        """Update the display text and tooltip."""
        self.setText(f"{self.bookmark.icon} {self.bookmark.name}")
        self.setToolTip(f"{self.bookmark.name}\n{self.bookmark.path}")

    def get_bookmark(self) -> LocationBookmark:
        """Get the bookmark data."""
        return self.bookmark

    def update_bookmark(self, bookmark: LocationBookmark) -> None:
        """Update the bookmark data."""
        self.bookmark = bookmark
        self._update_display()


class BookmarkManagerDialog(QDialog):
    """
    Dialog for managing bookmarked locations.

    Features:
    - Add new bookmarks
    - Edit existing bookmarks
    - Delete bookmarks
    - Browse to bookmark location
    - Import/Export bookmarks
    """

    bookmarks_changed = Signal()
    bookmark_selected = Signal(str)  # path

    def __init__(self, parent: Optional[QWidget] = None,
                 location_manager: Optional[LocationManager] = None):
        """Initialize the bookmark manager dialog."""
        super().__init__(parent)

        self.location_manager = location_manager
        self.current_bookmark: Optional[LocationBookmark] = None

        self._setup_ui()
        self._setup_connections()
        self._load_bookmarks()

        # Set size
        self.resize(600, 400)

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self.setWindowTitle("Manage Bookmarks")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("Bookmark Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Bookmark list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Bookmark list
        list_label = QLabel("Bookmarks:")
        list_font = QFont()
        list_font.setBold(True)
        list_label.setFont(list_font)
        left_layout.addWidget(list_label)

        self.bookmark_list = QListWidget()
        self.bookmark_list.setMinimumWidth(250)
        left_layout.addWidget(self.bookmark_list)

        # List buttons
        list_buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add...")
        self.edit_button = QPushButton("Edit...")
        self.delete_button = QPushButton("Delete")
        self.browse_button = QPushButton("Browse...")

        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.browse_button.setEnabled(False)

        list_buttons_layout.addWidget(self.add_button)
        list_buttons_layout.addWidget(self.edit_button)
        list_buttons_layout.addWidget(self.delete_button)
        list_buttons_layout.addWidget(self.browse_button)
        left_layout.addLayout(list_buttons_layout)

        splitter.addWidget(left_widget)

        # Right panel - Bookmark details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        details_label = QLabel("Bookmark Details:")
        details_label.setFont(list_font)
        right_layout.addWidget(details_label)

        # Details form
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Shape.Box)
        details_layout = QVBoxLayout(details_frame)

        # Name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter bookmark name")
        name_layout.addWidget(self.name_edit)
        details_layout.addLayout(name_layout)

        # Path field
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path:"))
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter or browse for path")
        self.path_browse_button = QPushButton("Browse...")
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_browse_button)
        details_layout.addLayout(path_layout)

        # Description field
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description")
        self.description_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.description_edit)
        details_layout.addLayout(desc_layout)

        # Save/Cancel buttons for editing
        edit_buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        edit_buttons_layout.addWidget(self.save_button)
        edit_buttons_layout.addWidget(self.cancel_button)
        details_layout.addLayout(edit_buttons_layout)

        right_layout.addWidget(details_frame)
        right_layout.addStretch()

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([250, 350])

        # Bottom buttons
        bottom_layout = QHBoxLayout()

        # Import/Export buttons
        import_button = QPushButton("Import...")
        export_button = QPushButton("Export...")
        bottom_layout.addWidget(import_button)
        bottom_layout.addWidget(export_button)
        bottom_layout.addStretch()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        bottom_layout.addWidget(button_box)

        layout.addLayout(bottom_layout)

        # Store references
        self.button_box = button_box
        self.import_button = import_button
        self.export_button = export_button

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Bookmark list
        self.bookmark_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.bookmark_list.itemDoubleClicked.connect(self._on_bookmark_activated)

        # List buttons
        self.add_button.clicked.connect(self._add_bookmark)
        self.edit_button.clicked.connect(self._edit_bookmark)
        self.delete_button.clicked.connect(self._delete_bookmark)
        self.browse_button.clicked.connect(self._browse_bookmark)

        # Details form
        self.name_edit.textChanged.connect(self._on_details_changed)
        self.path_edit.textChanged.connect(self._on_details_changed)
        self.path_browse_button.clicked.connect(self._browse_path)

        # Edit buttons
        self.save_button.clicked.connect(self._save_bookmark)
        self.cancel_button.clicked.connect(self._cancel_edit)

        # Import/Export
        self.import_button.clicked.connect(self._import_bookmarks)
        self.export_button.clicked.connect(self._export_bookmarks)

        # Dialog buttons
        self.button_box.rejected.connect(self.accept)

    def _load_bookmarks(self) -> None:
        """Load bookmarks from location manager."""
        if not self.location_manager:
            return

        try:
            bookmarks = self.location_manager.get_bookmarks()

            self.bookmark_list.clear()
            for bookmark in bookmarks:
                item = BookmarkItem(bookmark)
                self.bookmark_list.addItem(item)

        except Exception as e:
            logger.error(f"Error loading bookmarks: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load bookmarks: {e}")

    def _on_selection_changed(self) -> None:
        """Handle bookmark selection changes."""
        current_item = self.bookmark_list.currentItem()
        has_selection = current_item is not None

        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.browse_button.setEnabled(has_selection)

        if has_selection and isinstance(current_item, BookmarkItem):
            self._show_bookmark_details(current_item.get_bookmark())
        else:
            self._clear_details()

    def _show_bookmark_details(self, bookmark: LocationBookmark) -> None:
        """Show bookmark details in the form."""
        self.current_bookmark = bookmark

        self.name_edit.setText(bookmark.name)
        self.path_edit.setText(bookmark.path)
        # LocationBookmark doesn't have description, using empty string
        self.description_edit.setPlainText("")

        # Disable editing initially
        self._set_editing_mode(False)

    def _clear_details(self) -> None:
        """Clear the details form."""
        self.current_bookmark = None
        self.name_edit.clear()
        self.path_edit.clear()
        self.description_edit.clear()
        self._set_editing_mode(False)

    def _set_editing_mode(self, editing: bool) -> None:
        """Enable/disable editing mode."""
        self.name_edit.setEnabled(editing)
        self.path_edit.setEnabled(editing)
        self.description_edit.setEnabled(editing)
        self.path_browse_button.setEnabled(editing)
        self.save_button.setEnabled(editing)
        self.cancel_button.setEnabled(editing)

    def _on_details_changed(self) -> None:
        """Handle changes to bookmark details."""
        # Enable save button if in editing mode
        if self.name_edit.isEnabled():
            has_name = bool(self.name_edit.text().strip())
            has_path = bool(self.path_edit.text().strip())
            self.save_button.setEnabled(has_name and has_path)

    def _add_bookmark(self) -> None:
        """Add a new bookmark."""
        self.current_bookmark = None  # Will be created when saving
        self._clear_details()
        self._set_editing_mode(True)
        self.name_edit.setFocus()

    def _edit_bookmark(self) -> None:
        """Edit the selected bookmark."""
        current_item = self.bookmark_list.currentItem()
        if current_item and isinstance(current_item, BookmarkItem):
            self._set_editing_mode(True)
            self.name_edit.setFocus()
            self.name_edit.selectAll()

    def _delete_bookmark(self) -> None:
        """Delete the selected bookmark."""
        current_item = self.bookmark_list.currentItem()
        if not current_item or not isinstance(current_item, BookmarkItem):
            return

        bookmark = current_item.get_bookmark()
        name = bookmark.name

        reply = QMessageBox.question(
            self, "Delete Bookmark",
            f"Are you sure you want to delete the bookmark '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.location_manager:
                try:
                    self.location_manager.remove_bookmark(bookmark.name)
                    self._load_bookmarks()
                    self._clear_details()
                    self.bookmarks_changed.emit()
                except Exception as e:
                    logger.error(f"Error deleting bookmark: {e}")
                    QMessageBox.warning(self, "Error", f"Failed to delete bookmark: {e}")

    def _browse_bookmark(self) -> None:
        """Browse to the selected bookmark location."""
        current_item = self.bookmark_list.currentItem()
        if current_item and isinstance(current_item, BookmarkItem):
            bookmark = current_item.get_bookmark()
            path = bookmark.path
            if path and os.path.exists(path):
                self.bookmark_selected.emit(path)
                self.accept()
            else:
                QMessageBox.warning(self, "Invalid Path",
                                  f"The bookmark path does not exist:\n{path}")

    def _browse_path(self) -> None:
        """Browse for a path to set in the path field."""
        current_path = self.path_edit.text().strip()
        if not current_path:
            current_path = os.path.expanduser("~")

        path = QFileDialog.getExistingDirectory(
            self, "Select Bookmark Location", current_path
        )

        if path:
            self.path_edit.setText(path)

    def _save_bookmark(self) -> None:
        """Save the current bookmark."""
        if not self.location_manager:
            QMessageBox.warning(self, "Error", "No location manager available")
            return

        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        description = self.description_edit.toPlainText().strip()

        if not name or not path:
            QMessageBox.warning(self, "Invalid Data",
                              "Please enter both name and path")
            return

        try:
            # Check if path exists
            if not os.path.exists(path):
                reply = QMessageBox.question(
                    self, "Path Not Found",
                    f"The path does not exist:\n{path}\n\nSave anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            # Save bookmark
            bookmark_data = {
                'name': name,
                'path': path,
                'description': description
            }

            # If editing existing bookmark with different name, remove old one
            if (self.current_bookmark and
                self.current_bookmark.name and
                self.current_bookmark.name != name):
                self.location_manager.remove_bookmark(self.current_bookmark.name)

            self.location_manager.add_bookmark(name, path, description)

            self._load_bookmarks()
            self._set_editing_mode(False)
            self.bookmarks_changed.emit()

            # Select the saved bookmark
            for i in range(self.bookmark_list.count()):
                item = self.bookmark_list.item(i)
                if isinstance(item, BookmarkItem):
                    if item.get_bookmark().name == name:
                        self.bookmark_list.setCurrentItem(item)
                        break

        except Exception as e:
            logger.error(f"Error saving bookmark: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save bookmark: {e}")

    def _cancel_edit(self) -> None:
        """Cancel editing and restore original values."""
        if self.current_bookmark:
            self._show_bookmark_details(self.current_bookmark)
        else:
            self._clear_details()

    def _on_bookmark_activated(self, item: QListWidgetItem) -> None:
        """Handle bookmark double-click."""
        if isinstance(item, BookmarkItem):
            bookmark = item.get_bookmark()
            path = bookmark.path
            if path and os.path.exists(path):
                self.bookmark_selected.emit(path)
                self.accept()

    def _import_bookmarks(self) -> None:
        """Import bookmarks from file."""
        # TODO: Implement bookmark import
        QMessageBox.information(self, "Not Implemented",
                              "Bookmark import feature coming soon!")

    def _export_bookmarks(self) -> None:
        """Export bookmarks to file."""
        # TODO: Implement bookmark export
        QMessageBox.information(self, "Not Implemented",
                              "Bookmark export feature coming soon!")


def show_bookmark_manager(parent: Optional[QWidget] = None,
                         location_manager: Optional[LocationManager] = None) -> bool:
    """
    Show the bookmark manager dialog.

    Args:
        parent: Parent widget
        location_manager: Location manager service

    Returns:
        True if bookmarks were modified
    """
    dialog = BookmarkManagerDialog(parent, location_manager)

    bookmarks_changed = False

    def on_bookmarks_changed():
        nonlocal bookmarks_changed
        bookmarks_changed = True

    dialog.bookmarks_changed.connect(on_bookmarks_changed)

    dialog.exec()
    return bookmarks_changed
