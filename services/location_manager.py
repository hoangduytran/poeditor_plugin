"""
LocationManager - Quick locations and bookmark management service.

This service manages quick access locations, user bookmarks, and provides
functionality for organizing and persisting location preferences.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QStandardPaths
from lg import logger


class QuickLocation:
    """Data class representing a quick access location."""

    def __init__(self, name: str, icon: str, path: str, description: Optional[str] = None):
        self.name = name
        self.icon = icon
        self.path = path
        self.description = description or f"Navigate to {name}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'icon': self.icon,
            'path': self.path,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuickLocation':
        """Create QuickLocation from dictionary."""
        return cls(
            name=data['name'],
            icon=data['icon'],
            path=data['path'],
            description=data.get('description')
        )


class LocationBookmark:
    """Data class representing a user-defined bookmark."""

    def __init__(self, id: str, name: str, path: str, icon: str = "⭐",
                 category: str = "default", created: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.path = path
        self.icon = icon
        self.category = category
        self.created = created or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'icon': self.icon,
            'category': self.category,
            'created': self.created.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocationBookmark':
        """Create LocationBookmark from dictionary."""
        created = None
        if data.get('created'):
            try:
                created = datetime.fromisoformat(data['created'])
            except Exception:
                created = datetime.now()

        return cls(
            id=data['id'],
            name=data['name'],
            path=data['path'],
            icon=data.get('icon', '⭐'),
            category=data.get('category', 'default'),
            created=created
        )


class LocationManager(QObject):
    """
    Service for managing quick locations and bookmarks.

    Provides functionality for:
    - Standard quick access locations (Home, Documents, etc.)
    - User-defined bookmarks with categories
    - Recent location tracking
    - Import/export of bookmark collections

    Signals:
        bookmarks_changed(): Emitted when bookmarks are modified
        quick_locations_changed(): Emitted when quick locations are updated
    """

    # Location signals
    bookmarks_changed = Signal()
    quick_locations_changed = Signal()

    # Configuration
    BOOKMARKS_FILE_NAME = "bookmarks.json"
    QUICK_LOCATIONS_FILE_NAME = "quick_locations.json"

    def __init__(self, parent=None):
        """
        Initialize the LocationManager.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # Storage for locations and bookmarks
        self._quick_locations: List[QuickLocation] = []
        self._bookmarks: List[LocationBookmark] = []
        self._bookmark_categories: List[str] = ['default', 'projects', 'documents', 'favorites']

        # Recent location tracking (integration with NavigationHistoryService)
        self._recent_locations: List[Dict[str, Any]] = []

        # Storage paths
        self._storage_dir = self._get_storage_directory()
        self._bookmarks_file_path = self._storage_dir / self.BOOKMARKS_FILE_NAME
        self._quick_locations_file_path = self._storage_dir / self.QUICK_LOCATIONS_FILE_NAME

        # Initialize locations and load data
        self._initialize_quick_locations()
        self._load_bookmarks()
        self._load_custom_quick_locations()

        logger.info("LocationManager initialized")

    def get_quick_locations(self) -> List[QuickLocation]:
        """
        Get all quick access locations.

        Returns:
            List of QuickLocation objects
        """
        return self._quick_locations.copy()

    def get_bookmarks(self, category: Optional[str] = None) -> List[LocationBookmark]:
        """
        Get bookmarks, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of LocationBookmark objects
        """
        if category:
            return [bm for bm in self._bookmarks if bm.category == category]
        return self._bookmarks.copy()

    def get_bookmark_categories(self) -> List[str]:
        """
        Get all available bookmark categories.

        Returns:
            List of category names
        """
        return self._bookmark_categories.copy()

    def add_bookmark(self, name: str, path: str, icon: str = "⭐",
                    category: str = "default") -> LocationBookmark:
        """
        Add a new bookmark.

        Args:
            name: Display name for the bookmark
            path: Path the bookmark points to
            icon: Icon for the bookmark
            category: Category for organization

        Returns:
            Created LocationBookmark object
        """
        # Validate path
        if not path or not Path(path).exists():
            raise ValueError(f"Invalid path for bookmark: {path}")

        # Generate unique ID
        bookmark_id = str(uuid.uuid4())

        # Create bookmark
        bookmark = LocationBookmark(
            id=bookmark_id,
            name=name,
            path=str(Path(path).resolve()),
            icon=icon,
            category=category
        )

        # Add to collection
        self._bookmarks.append(bookmark)

        # Add category if new
        if category not in self._bookmark_categories:
            self._bookmark_categories.append(category)

        # Save and emit signals
        self._save_bookmarks()
        self.bookmarks_changed.emit()

        logger.info(f"Added bookmark: {name} -> {path}")
        return bookmark

    def remove_bookmark(self, bookmark_id: str) -> bool:
        """
        Remove a bookmark by ID.

        Args:
            bookmark_id: ID of bookmark to remove

        Returns:
            bool: True if bookmark was removed, False if not found
        """
        for i, bookmark in enumerate(self._bookmarks):
            if bookmark.id == bookmark_id:
                removed_bookmark = self._bookmarks.pop(i)
                self._save_bookmarks()
                self.bookmarks_changed.emit()
                logger.info(f"Removed bookmark: {removed_bookmark.name}")
                return True

        logger.warning(f"Bookmark not found for removal: {bookmark_id}")
        return False

    def update_bookmark(self, bookmark_id: str, name: Optional[str] = None,
                       path: Optional[str] = None, icon: Optional[str] = None,
                       category: Optional[str] = None) -> bool:
        """
        Update an existing bookmark.

        Args:
            bookmark_id: ID of bookmark to update
            name: New name (optional)
            path: New path (optional)
            icon: New icon (optional)
            category: New category (optional)

        Returns:
            bool: True if bookmark was updated, False if not found
        """
        for bookmark in self._bookmarks:
            if bookmark.id == bookmark_id:
                if name is not None:
                    bookmark.name = name
                if path is not None:
                    # Validate new path
                    if not Path(path).exists():
                        raise ValueError(f"Invalid path for bookmark update: {path}")
                    bookmark.path = str(Path(path).resolve())
                if icon is not None:
                    bookmark.icon = icon
                if category is not None:
                    bookmark.category = category
                    # Add category if new
                    if category not in self._bookmark_categories:
                        self._bookmark_categories.append(category)

                self._save_bookmarks()
                self.bookmarks_changed.emit()
                logger.info(f"Updated bookmark: {bookmark.name}")
                return True

        logger.warning(f"Bookmark not found for update: {bookmark_id}")
        return False

    def find_bookmark_by_path(self, path: str) -> Optional[LocationBookmark]:
        """
        Find a bookmark by its path.

        Args:
            path: Path to search for

        Returns:
            LocationBookmark if found, None otherwise
        """
        resolved_path = str(Path(path).resolve())
        for bookmark in self._bookmarks:
            if bookmark.path == resolved_path:
                return bookmark
        return None

    def add_quick_location(self, name: str, icon: str, path: str,
                          description: Optional[str] = None) -> QuickLocation:
        """
        Add a custom quick location.

        Args:
            name: Display name
            icon: Icon for the location
            path: Path the location points to
            description: Optional description

        Returns:
            Created QuickLocation object
        """
        # Validate path
        if not path or not Path(path).exists():
            raise ValueError(f"Invalid path for quick location: {path}")

        location = QuickLocation(
            name=name,
            icon=icon,
            path=str(Path(path).resolve()),
            description=description
        )

        # Add to collection
        self._quick_locations.append(location)

        # Save and emit signals
        self._save_quick_locations()
        self.quick_locations_changed.emit()

        logger.info(f"Added quick location: {name} -> {path}")
        return location

    def remove_quick_location(self, path: str) -> bool:
        """
        Remove a quick location by path.

        Args:
            path: Path of the quick location to remove

        Returns:
            bool: True if location was removed, False if not found
        """
        resolved_path = str(Path(path).resolve())
        for i, location in enumerate(self._quick_locations):
            if location.path == resolved_path:
                removed_location = self._quick_locations.pop(i)
                self._save_quick_locations()
                self.quick_locations_changed.emit()
                logger.info(f"Removed quick location: {removed_location.name}")
                return True

        logger.warning(f"Quick location not found for removal: {path}")
        return False

    def update_recent_location(self, path: str):
        """
        Update recent location tracking.

        This method is called by NavigationHistoryService to keep
        LocationManager informed about recent navigation.

        Args:
            path: Recently navigated path
        """
        # This method provides a hook for future enhancement
        # Currently, recent location tracking is handled by NavigationHistoryService
        logger.debug(f"Recent location updated: {path}")

    def export_bookmarks(self, file_path: str) -> bool:
        """
        Export bookmarks to a JSON file.

        Args:
            file_path: Path where to save the export file

        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            export_data = {
                'bookmarks': [bm.to_dict() for bm in self._bookmarks],
                'categories': self._bookmark_categories,
                'exported_at': datetime.now().isoformat(),
                'version': '1.0'
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported {len(self._bookmarks)} bookmarks to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export bookmarks: {str(e)}")
            return False

    def import_bookmarks(self, file_path: str, merge: bool = True) -> bool:
        """
        Import bookmarks from a JSON file.

        Args:
            file_path: Path to the import file
            merge: If True, merge with existing bookmarks; if False, replace

        Returns:
            bool: True if import successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            imported_bookmarks = [
                LocationBookmark.from_dict(bm_data)
                for bm_data in import_data.get('bookmarks', [])
            ]

            imported_categories = import_data.get('categories', [])

            if not merge:
                # Replace existing bookmarks
                self._bookmarks = imported_bookmarks
                self._bookmark_categories = imported_categories
            else:
                # Merge with existing bookmarks
                existing_paths = {bm.path for bm in self._bookmarks}
                for imported_bm in imported_bookmarks:
                    if imported_bm.path not in existing_paths:
                        self._bookmarks.append(imported_bm)

                # Merge categories
                for category in imported_categories:
                    if category not in self._bookmark_categories:
                        self._bookmark_categories.append(category)

            # Save and emit signals
            self._save_bookmarks()
            self.bookmarks_changed.emit()

            logger.info(f"Imported {len(imported_bookmarks)} bookmarks from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import bookmarks: {str(e)}")
            return False

    def get_project_root(self) -> Optional[str]:
        """
        Detect and return the current project root directory.

        Returns:
            Project root path if detected, None otherwise
        """
        # Start from current working directory
        current_dir = Path.cwd()

        # Look for common project indicators
        project_indicators = [
            '.git', '.svn', '.hg',  # Version control
            'setup.py', 'pyproject.toml', 'requirements.txt',  # Python
            'package.json', 'yarn.lock',  # Node.js
            'Cargo.toml',  # Rust
            'pom.xml', 'build.gradle',  # Java
            'CMakeLists.txt', 'Makefile',  # C/C++
            '.project', '.vscode'  # IDE files
        ]

        # Search up the directory tree
        for parent in [current_dir] + list(current_dir.parents):
            for indicator in project_indicators:
                if (parent / indicator).exists():
                    logger.debug(f"Project root detected: {parent} (indicator: {indicator})")
                    return str(parent)

        # Fallback to current directory
        return str(current_dir)

    def _initialize_quick_locations(self):
        """Initialize the standard quick access locations."""
        home_path = Path.home()

        standard_locations = [
            QuickLocation("Home", "🏠", str(home_path), "User home directory"),
            QuickLocation("Root", "💾", "/", "System root directory"),
            QuickLocation("Documents", "📄", str(home_path / "Documents"), "Documents folder"),
            QuickLocation("Downloads", "⬇️", str(home_path / "Downloads"), "Downloads folder"),
            QuickLocation("Desktop", "🖥️", str(home_path / "Desktop"), "Desktop folder"),
        ]

        # Add macOS specific locations
        if Path("/Applications").exists():
            standard_locations.append(
                QuickLocation("Applications", "📁", "/Applications", "Applications folder")
            )

        # Add project root if detectable
        project_root = self.get_project_root()
        if project_root:
            standard_locations.append(
                QuickLocation("Project Root", "⚙️", project_root, "Current project root")
            )

        # Filter out non-existent paths
        self._quick_locations = [
            loc for loc in standard_locations
            if Path(loc.path).exists()
        ]

        logger.info(f"Initialized {len(self._quick_locations)} quick locations")

    def _get_storage_directory(self) -> Path:
        """Get the directory for storing persistent data."""
        app_data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        storage_dir = Path(app_data_dir) / "locations"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir

    def _load_bookmarks(self):
        """Load bookmarks from persistent storage."""
        try:
            if self._bookmarks_file_path.exists():
                with open(self._bookmarks_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Load bookmarks
                bookmark_data = data.get('bookmarks', [])
                self._bookmarks = [
                    LocationBookmark.from_dict(bm_data)
                    for bm_data in bookmark_data
                ]

                # Load categories
                self._bookmark_categories = data.get('categories', self._bookmark_categories)

                logger.info(f"Loaded {len(self._bookmarks)} bookmarks")

        except Exception as e:
            logger.error(f"Failed to load bookmarks: {str(e)}")

    def _save_bookmarks(self):
        """Save bookmarks to persistent storage."""
        try:
            data = {
                'bookmarks': [bm.to_dict() for bm in self._bookmarks],
                'categories': self._bookmark_categories,
                'saved_at': datetime.now().isoformat()
            }

            with open(self._bookmarks_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save bookmarks: {str(e)}")

    def _load_custom_quick_locations(self):
        """Load custom quick locations from persistent storage."""
        try:
            if self._quick_locations_file_path.exists():
                with open(self._quick_locations_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Load custom locations and append to standard ones
                custom_locations = [
                    QuickLocation.from_dict(loc_data)
                    for loc_data in data.get('custom_locations', [])
                ]

                self._quick_locations.extend(custom_locations)

                logger.info(f"Loaded {len(custom_locations)} custom quick locations")

        except Exception as e:
            logger.error(f"Failed to load custom quick locations: {str(e)}")

    def _save_quick_locations(self):
        """Save custom quick locations to persistent storage."""
        try:
            # Separate standard and custom locations
            # (This is a simplified approach - in practice, you might want to track this differently)
            standard_names = {"Home", "Root", "Documents", "Downloads", "Desktop", "Applications", "Project Root"}
            custom_locations = [
                loc for loc in self._quick_locations
                if loc.name not in standard_names
            ]

            data = {
                'custom_locations': [loc.to_dict() for loc in custom_locations],
                'saved_at': datetime.now().isoformat()
            }

            with open(self._quick_locations_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save custom quick locations: {str(e)}")
