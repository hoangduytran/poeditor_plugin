"""
Simple Explorer Widget

A clean, focused file explorer implementation based on the simple_explorer_design.md
specifications. Provides essential file browsing functionality with search/filter
capabilities and settings persistence.

Features:
- Directories always displayed first in sorting (§"/:both in normal and filtered views)
- Clean, consistent appearance without alternating row colors
- Search/filter functionality with context menu options
- Settings persistence for last visited directory
- Theme integration via Qt stylesheet system
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLineEdit,
    QPushButton, QHeaderView, QMenu, QApplication, QFileSystemModel, QLabel,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QDir, QModelIndex, QItemSelectionModel, QSortFilterProxyModel
from PySide6.QtGui import QAction

from core.explorer_settings import ExplorerSettings
from services.file_operations_service import FileOperationsService
from services.undo_redo_service import UndoRedoManager
from widgets.explorer_context_menu import ExplorerContextMenu
from lg import logger


class DirectoryFirstProxyModel(QSortFilterProxyModel):
    """
    Custom sort proxy model that always shows directories first.

    This proxy model implements the directory-first sorting behavior:
    - Directories are always displayed before files
    - Within each group, items are sorted alphabetically
    - This sorting applies to both normal and filtered views
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enable dynamic sorting
        self.setSortRole(Qt.ItemDataRole.DisplayRole)
        self.setDynamicSortFilter(True)

    def lessThan(self, left_index, right_index):
        """
        Custom sorting implementation that prioritizes directories over files.

        Args:
            left_index: Left index from the proxy model
            right_index: Right index from the proxy model

        Returns:
            bool: True if left should be sorted before right
        """
        # Get source model
        source_model = self.sourceModel()

        # Ensure we have a file system model
        if not source_model or not isinstance(source_model, QFileSystemModel):
            return super().lessThan(left_index, right_index)

        try:
            # Map proxy indexes to source model indexes - don't use mapToSource
            # since these are already source indexes in the lessThan method

            # Access file info directly from the source model using column 0
            # which contains the filename
            left_is_dir = source_model.isDir(source_model.index(left_index.row(), 0, left_index.parent()))
            right_is_dir = source_model.isDir(source_model.index(right_index.row(), 0, right_index.parent()))

            # Directory first sorting
            if left_is_dir and not right_is_dir:
                return True
            elif not left_is_dir and right_is_dir:
                return False

            # Both are dirs or both are files, compare by name
            left_name = source_model.data(left_index, Qt.ItemDataRole.DisplayRole)
            right_name = source_model.data(right_index, Qt.ItemDataRole.DisplayRole)

            # Case insensitive sorting
            if isinstance(left_name, str) and isinstance(right_name, str):
                return left_name.lower() < right_name.lower()

            # Fallback to default sorting
            return super().lessThan(left_index, right_index)

        except Exception as e:
            logger.error(f"Sorting error: {e}")
            return super().lessThan(left_index, right_index)


class SimpleSearchBar(QLineEdit):
    """Simple search/filter input with context menu for mode switching."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Filter files... (Right-click for options)")
        self._filter_mode = True  # True = filter files, False = search in files
        self._setup_context_menu()

    def _setup_context_menu(self):
        """Set up the right-click context menu."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        """Show the context menu with filter/search options."""
        menu = QMenu(self)

        # Filter files option
        filter_action = QAction("Filter Files", self)
        filter_action.setCheckable(True)
        filter_action.setChecked(self._filter_mode)
        filter_action.triggered.connect(lambda: self._set_mode(True))
        menu.addAction(filter_action)

        # Search in files option
        search_action = QAction("Search Text In Files", self)
        search_action.setCheckable(True)
        search_action.setChecked(not self._filter_mode)
        search_action.triggered.connect(lambda: self._set_mode(False))
        menu.addAction(search_action)

        menu.exec(self.mapToGlobal(position))

    def _set_mode(self, filter_mode: bool):
        """Set the search/filter mode."""
        self._filter_mode = filter_mode
        if filter_mode:
            self.setPlaceholderText("Filter files... (Right-click for options)")
        else:
            self.setPlaceholderText("Search text in files... (Right-click for options)")
        logger.debug(f"Search bar mode changed to: {'Filter' if filter_mode else 'Search'}")


class SimpleFileView(QTreeView):
    """Simple file tree view with direct QFileSystemModel integration."""

    # Signals
    file_activated = Signal(str)  # Emitted when a file is double-clicked
    directory_changed = Signal(str)  # Emitted when directory changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_model()
        self._setup_view()
        self._setup_context_menu()

    def _setup_context_menu(self):
        """Set up the context menu for file operations."""
        # Initialize required services
        self.file_operations_service = FileOperationsService()
        self.undo_redo_manager = UndoRedoManager()

        # Create the context menu manager
        self.context_menu = ExplorerContextMenu(
            self.file_operations_service,
            self.undo_redo_manager
        )

        # Enable custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Connect context menu signals
        self.context_menu.refresh_requested.connect(self._refresh_view)

    def _refresh_view(self):
        """Refresh the file view."""
        try:
            # Get current path
            current_path = self.get_current_path()

            # Reset the model and view
            self.proxy_model.invalidate()
            self.file_system_model.setRootPath("")  # Clear

            # Set the path again to refresh
            self.set_current_path(current_path)

            logger.debug(f"File view refreshed for path: {current_path}")
        except Exception as e:
            logger.error(f"Error refreshing file view: {e}")

    def _setup_model(self):
        """
        Set up the file system model with directory-first sorting.

        Uses a custom proxy model to ensure directories always appear before files
        in both normal and filtered views.
        """
        # Create the source model
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.currentPath())

        # Set up filtering
        self.file_system_model.setFilter(
            QDir.Filter.AllDirs |
            QDir.Filter.Files |
            QDir.Filter.NoDotAndDotDot |
            QDir.Filter.AllEntries
        )

        # Create and configure the proxy model for directory-first sorting
        self.proxy_model = DirectoryFirstProxyModel()
        self.proxy_model.setSourceModel(self.file_system_model)
        self.proxy_model.setDynamicSortFilter(True)

        # Set the proxy model on the view
        self.setModel(self.proxy_model)

        # Map the root path index through the proxy model
        source_index = self.file_system_model.index(QDir.currentPath())
        proxy_index = self.proxy_model.mapFromSource(source_index)
        self.setRootIndex(proxy_index)

    def _setup_view(self):
        """
        Set up the tree view properties with consistent styling and behavior.

        Design choices:
        - Alternating row colors are disabled for cleaner visual appearance
        - Sorting is enabled with directories always displayed first
        - Consistent appearance across normal and filtered views
        """
        # Hide unnecessary columns initially (can be toggled later)
        self.setRootIsDecorated(False)

        # Explicitly disable alternating row colors for consistent appearance
        self.setAlternatingRowColors(False)

        # Configure selection behavior for proper hover/selection styling
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # # Configure and show appropriate columns
        # for i in range(1, self.model().columnCount()):
        #     self.hideColumn(i)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

        # Configure sorting
        self.setSortingEnabled(True)

        # Set sorting on the proxy model
        self.proxy_model.setDynamicSortFilter(True)

        # First invalidate to ensure the model is properly initialized
        self.proxy_model.invalidate()

        # Now set the sort order on both the view and proxy model
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

        # Process events to ensure sorting takes effect
        QApplication.processEvents()

        # Connect double-click handler
        self.doubleClicked.connect(self._on_activated)

    def _show_context_menu(self, position):
        """Show the context menu for file operations."""
        try:
            # Get the item at the clicked position
            index = self.indexAt(position)
            selected_items = []
            current_directory = self.get_current_path()

            if index.isValid():
                # Get selected items (can be multiple with Ctrl+click)
                selected_indexes = self.selectedIndexes()
                if not selected_indexes:
                    # If nothing is selected, use the clicked item
                    selected_indexes = [index]

                for sel_index in selected_indexes:
                    # Map proxy index to source index
                    source_index = self.proxy_model.mapToSource(sel_index)
                    if source_index.isValid():
                        file_path = self.file_system_model.filePath(source_index)
                        is_dir = self.file_system_model.isDir(source_index)
                        name = self.file_system_model.fileName(source_index)

                        selected_items.append({
                            'path': file_path,
                            'is_dir': is_dir,
                            'name': name
                        })

                        # Update the context menu's selected items for shortcuts
                        self.context_menu.selected_items = selected_items

            # Create and show the context menu
            menu = self.context_menu.create_menu(selected_items, current_directory)
            menu.exec(self.mapToGlobal(position))

        except Exception as e:
            logger.error(f"Error showing context menu: {e}")

    def mousePressEvent(self, event):
        # Clear selection when clicking on empty area
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.clearSelection()
        super().mousePressEvent(event)

    def _on_activated(self, index: QModelIndex):
        """Handle item activation (double-click)."""
        if not index.isValid():
            logger.debug("Invalid index activated")
            return

        try:
            # Map proxy model index to source model index
            source_index = self.proxy_model.mapToSource(index)

            if not source_index.isValid():
                logger.error("Failed to map index to source model")
                return

            file_path = self.file_system_model.filePath(source_index)

            # Emit file activated signal if it's a file
            if not self.file_system_model.isDir(source_index):
                self.file_activated.emit(file_path)
                logger.debug(f"File activated: {file_path}")
            else:
                # If it's a directory, navigate to it
                self.set_current_path(file_path)
                logger.debug(f"Directory activated: {file_path}")
        except Exception as e:
            logger.error(f"Error handling activated item: {e}")

    def set_current_path(self, path: str) -> None:
        """
        Set the current directory path for the view.
        Args:
            path: The absolute path to the directory.
        """
        if path and os.path.isdir(path):
            try:
                # First block signals to prevent unwanted updates
                old_state = self.blockSignals(True)

                # Set the root path on the file system model
                source_index = self.file_system_model.setRootPath(path)

                # Process events to ensure the model has time to update
                QApplication.processEvents()

                # Make sure the source index is valid
                if not source_index.isValid():
                    logger.error(f"Invalid source index for path: {path}")
                    self.blockSignals(old_state)
                    self.directory_changed.emit(path)
                    return

                # Reset the proxy model to clear any cached indices
                self.proxy_model.invalidate()

                # Now map the source index to the proxy model index
                proxy_index = self.proxy_model.mapFromSource(source_index)

                # Set the root index on the view
                if proxy_index.isValid():
                    self.setRootIndex(proxy_index)
                else:
                    logger.warning(f"Invalid proxy index for path: {path}, using fallback")
                    # Try another approach - use the first row of the model
                    self.setRootIndex(self.proxy_model.index(0, 0, QModelIndex()))

                # Re-apply sorting
                self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

                # Process events to ensure UI updates
                QApplication.processEvents()

                # Restore signal blocking state
                self.blockSignals(old_state)

                # Notify listeners
                self.directory_changed.emit(path)
                logger.info(f"Explorer path set to: {path}")
            except Exception as e:
                logger.error(f"Failed to set explorer path to {path}: {e}")
        else:
            logger.warning(f"Invalid path provided to explorer: {path}")

    def get_current_path(self) -> str:
        """Get the current root path of the view."""
        return self.file_system_model.rootPath()

    def apply_filter(self, pattern: str):
        """
        Apply a filter pattern to the file view.

        The filter is applied to the source model while preserving the
        directory-first sorting behavior through the proxy model.
        """
        if pattern:
            self.file_system_model.setNameFilters([f"*{pattern}*"])
            self.file_system_model.setNameFilterDisables(False)
            logger.debug(f"Applied filter: *{pattern}*")
        else:
            # Clear the filter
            self.file_system_model.setNameFilters([])
            logger.debug("Cleared filter")


class SimpleExplorerWidget(QWidget):
    """
    Main simple explorer widget that combines search bar and file view.

    Features:
    - File browsing with QFileSystemModel
    - Search/filter functionality with directory-first sorting
    - Clean, consistent appearance without alternating row colors
    - Settings persistence for last directory
    - Theme integration via Qt stylesheet system
    - Clean, focused UI following simple_explorer_design.md
    """

    # Signals
    file_opened = Signal(str)
    location_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = ExplorerSettings()

        # Initialize UI components first
        self.search_bar = SimpleSearchBar()
        self.clear_button = QPushButton("✕")
        self.file_view = SimpleFileView()
        self.path_label = QLabel("Initializing...")
        self.up_button = QPushButton("↑ Up")
        self.up_button.setObjectName("up_button")

        self._setup_ui()
        self._connect_signals()
        self._load_initial_state()

    def _load_initial_state(self):
        """Load the last visited path from settings."""
        last_path = self.settings.get("last_path")
        if last_path and os.path.isdir(last_path):
            self.file_view.set_current_path(last_path)
        else:
            # Fallback to home directory if last path is invalid
            self.file_view.set_current_path(str(Path.home()))

    def _setup_ui(self):
        """Set up the user interface."""
        # Navigation button
        self.up_button.setToolTip("Go to parent directory")

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.up_button)
        nav_layout.addWidget(self.path_label, 1) # Stretch the label

        # Search/filter layout with clear button
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(2)
        search_layout.addWidget(self.search_bar, 1)  # Stretch the search bar
        search_layout.addWidget(self.clear_button)

        # Configure clear button
        self.clear_button.setToolTip("Clear filter and restore all files")
        self.clear_button.setFixedSize(24, 24)
        self.clear_button.setEnabled(False)  # Initially disabled

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(nav_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.file_view, 1) # Stretch the file view

    def _connect_signals(self):
        """Connect signals to slots."""
        self.up_button.clicked.connect(self._on_up_button_clicked)
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        self.clear_button.clicked.connect(self._on_clear_button_clicked)
        self.file_view.file_activated.connect(self.file_opened)
        self.file_view.directory_changed.connect(self._on_directory_changed)

        # Update path label when directory changes
        self.file_view.directory_changed.connect(
            lambda path: self.path_label.setText(path)
        )

    def _on_up_button_clicked(self):
        """Handle the 'Up' button click."""
        current_path = self.file_view.get_current_path()
        parent_path = os.path.dirname(current_path)
        if parent_path and parent_path != current_path:
            self.file_view.set_current_path(parent_path)

    def _on_search_text_changed(self, text: str):
        """Handle search/filter text changes."""
        self.file_view.apply_filter(text)
        # Enable/disable clear button based on whether there's text
        self.clear_button.setEnabled(bool(text.strip()))

    def _on_clear_button_clicked(self):
        """Handle clear button click to restore unfiltered state."""
        self.search_bar.clear()
        # apply_filter will be called via textChanged signal with empty text
        # which will clear the filter in the file view

    def _on_directory_changed(self, path: str):
        """Handle directory navigation."""
        self.location_changed.emit(path)
        self.settings.set("last_path", path)

    def set_current_path(self, path: str):
        """Public method to set the current path."""
        self.file_view.set_current_path(path)

    def get_current_path(self) -> str:
        """Public method to get the current path."""
        return self.file_view.get_current_path()

    def closeEvent(self, event):
        """Handle widget close event."""
        self.settings.save()
        super().closeEvent(event)
