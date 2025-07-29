"""
Goto Dropdown Widget

Provides a dropdown for quick location selection including:
- Recent locations from navigation history
- Bookmarked locations from location manager
- Quick access locations (Home, Documents, etc.)
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QComboBox, QWidget, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle, QApplication
)
from PySide6.QtCore import Signal, Qt, QModelIndex, QSize
from PySide6.QtGui import QPainter, QFontMetrics, QIcon

from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager, QuickLocation, LocationBookmark


class GotoDropdownDelegate(QStyledItemDelegate):
    """Custom delegate for rendering goto dropdown items with icons and descriptions."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._icon_size = QSize(16, 16)
        
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Custom paint method for dropdown items."""
        # For now, use default painting - can be enhanced later
        super().paint(painter, option, index)
        
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """Return size hint for dropdown items."""
        return QSize(200, 24)


class GotoDropdown(QComboBox):
    """
    Dropdown widget for quick location selection.
    
    Provides access to:
    - Recent locations from navigation history
    - Bookmarked locations
    - Quick access locations (Home, Documents, etc.)
    
    Signals:
        location_selected: Emitted when a location is selected (path: str)
    """
    
    # Signals
    location_selected = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the goto dropdown.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Services (will be injected)
        self._history_service: Optional[NavigationHistoryService] = None
        self._location_manager: Optional[LocationManager] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self) -> None:
        """Setup the dropdown UI."""
        # Set custom delegate
        self.setItemDelegate(GotoDropdownDelegate(self))
        
        # Configure dropdown
        self.setEditable(False)
        self.setMaxVisibleItems(15)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        
        # Set placeholder text
        self.setCurrentText("Select Location...")
        
        # Set minimum size
        self.setMinimumWidth(120)
        self.setFixedHeight(28)
        
        # Apply styles
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 4px 8px;
                background-color: palette(button);
            }
            QComboBox:hover {
                border-color: palette(highlight);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid palette(text);
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid palette(mid);
                background-color: palette(window);
                selection-background-color: palette(highlight);
            }
        """)
        
    def _setup_connections(self) -> None:
        """Setup signal connections."""
        self.currentTextChanged.connect(self._on_selection_changed)
        
    def inject_services(
        self,
        history_service: NavigationHistoryService,
        location_manager: LocationManager
    ) -> None:
        """
        Inject navigation services.
        
        Args:
            history_service: Navigation history service
            location_manager: Location and bookmark manager
        """
        self._history_service = history_service
        self._location_manager = location_manager
        
        # Populate dropdown
        self._populate_dropdown()
        
    def _populate_dropdown(self) -> None:
        """Populate the dropdown with available locations."""
        self.clear()
        
        # Add placeholder item
        self.addItem("Select Location...")
        self.setItemData(0, "", Qt.ItemDataRole.UserRole)  # No path for placeholder
        
        # Add quick locations
        if self._location_manager:
            quick_locations = self._location_manager.get_quick_locations()
            if quick_locations:
                self._add_section_separator("Quick Locations")
                for location in quick_locations:
                    self._add_location_item(location.name, location.path, location.icon)
        
        # Add recent locations
        if self._history_service:
            recent_locations = self._history_service.get_recent_locations(limit=8)
            if recent_locations:
                self._add_section_separator("Recent Locations")
                for location_data in recent_locations:
                    path = location_data.get('path', '')
                    display_name = self._get_display_name(path)
                    self._add_location_item(display_name, path, "")
        
        # Add bookmarks
        if self._location_manager:
            bookmarks = self._location_manager.get_bookmarks()
            if bookmarks:
                self._add_section_separator("Bookmarks")
                for bookmark in bookmarks:
                    self._add_location_item(bookmark.name, bookmark.path, bookmark.icon)
                    
    def _add_section_separator(self, title: str) -> None:
        """
        Add a section separator to the dropdown.
        
        Args:
            title: Section title
        """
        self.addItem(f"--- {title} ---")
        # Store separator info - we'll handle it in selection logic
        item_index = self.count() - 1
        self.setItemData(item_index, "", Qt.ItemDataRole.UserRole)  # No path for separator
            
    def _add_location_item(self, display_name: str, path: str, icon_path: str = "") -> None:
        """
        Add a location item to the dropdown.
        
        Args:
            display_name: Display name for the location
            path: Full path to the location
            icon_path: Optional icon path
        """
        self.addItem(display_name)
        item_index = self.count() - 1
        
        # Set item data
        self.setItemData(item_index, path, Qt.ItemDataRole.UserRole)  # Store path
        self.setItemData(item_index, path, Qt.ItemDataRole.ToolTipRole)  # Tooltip with full path
        if icon_path:
            self.setItemData(item_index, icon_path, Qt.ItemDataRole.UserRole + 1)  # Store icon path
            
    def _get_display_name(self, path: str) -> str:
        """
        Get a user-friendly display name for a path.
        
        Args:
            path: File system path
            
        Returns:
            Display name
        """
        if not path:
            return "Unknown"
            
        try:
            from pathlib import Path
            path_obj = Path(path)
            return path_obj.name or str(path_obj)
        except Exception:
            return path
            
    def _on_selection_changed(self, text: str) -> None:
        """
        Handle dropdown selection change.
        
        Args:
            text: Selected text
        """
        current_index = self.currentIndex()
        if current_index <= 0:  # Skip placeholder and separators
            return
            
        # Get the path from item data
        path = self.itemData(current_index, Qt.ItemDataRole.UserRole)
        if path and path.strip():
            self.location_selected.emit(path)
            
        # Reset to placeholder after selection
        self.setCurrentIndex(0)
        
    def refresh_locations(self) -> None:
        """Refresh the dropdown with updated locations."""
        current_selection = self.currentIndex()
        self._populate_dropdown()
        
        # Try to restore selection if it's still valid
        if current_selection > 0 and current_selection < self.count():
            self.setCurrentIndex(current_selection)
        else:
            self.setCurrentIndex(0)  # Reset to placeholder
            
    def add_recent_location(self, path: str) -> None:
        """
        Add a location to recent items and refresh.
        
        Args:
            path: Path to add to recent locations
        """
        if self._history_service:
            # The history service will handle adding the location
            # We just need to refresh our display
            self.refresh_locations()
            
    def sizeHint(self) -> QSize:
        """Return preferred size for the dropdown."""
        return QSize(120, 28)
