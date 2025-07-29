# Navigation Service Architecture Design

**Date**: July 29, 2025, 08:25  
**Component**: Navigation Service Layer  
**Status**: Technical Design  
**Priority**: High

## Overview

This document defines the architecture for the Navigation Service layer, which provides comprehensive navigation functionality including history management, path validation, quick locations, bookmarks, and navigation state tracking for the Explorer Header Navigation System.

## Service Architecture

### Core Services Overview

```
Navigation Service Layer
├── NavigationService              # Core navigation orchestration
├── LocationManager               # Quick locations and bookmarks
├── NavigationHistoryService      # History tracking and management
├── PathCompletionService         # Path auto-completion
├── ColumnConfigurationService    # Column display management
└── NavigationStateManager        # Current state tracking
```

## 1. NavigationService

### 1.1 Core Navigation Service

```python
from PySide6.QtCore import QObject, Signal
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

class NavigationService(QObject):
    """
    Core navigation service providing centralized navigation functionality.
    
    This service orchestrates navigation operations, maintains navigation state,
    and coordinates with other navigation-related services.
    """
    
    # Signals
    navigation_started = Signal(str)  # path
    navigation_completed = Signal(str)  # path
    navigation_failed = Signal(str, str)  # path, error_message
    current_path_changed = Signal(str)  # new_path
    navigation_state_changed = Signal(dict)  # navigation_state
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path = str(Path.home())
        self._navigation_history = []
        self._history_index = -1
        self._max_history_size = 100
        
        # Related services
        self.history_service = None
        self.location_manager = None
        self.state_manager = None
        
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize related services."""
        from services.navigation_history_service import NavigationHistoryService
        from services.location_manager import LocationManager
        from services.navigation_state_manager import NavigationStateManager
        
        self.history_service = NavigationHistoryService(self)
        self.location_manager = LocationManager(self)
        self.state_manager = NavigationStateManager(self)
        
    # Core Navigation Methods
    def navigate_to(self, path: str, add_to_history: bool = True) -> bool:
        """
        Navigate to the specified path.
        
        Args:
            path: Target path to navigate to
            add_to_history: Whether to add this navigation to history
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.navigation_started.emit(path)
            
            # Validate path
            if not self._validate_path(path):
                error_msg = f"Invalid or inaccessible path: {path}"
                self.navigation_failed.emit(path, error_msg)
                return False
                
            # Resolve path
            resolved_path = self._resolve_path(path)
            
            # Update current path
            old_path = self._current_path
            self._current_path = resolved_path
            
            # Add to history if requested
            if add_to_history:
                self.history_service.add_to_history(resolved_path)
                
            # Update navigation state
            self.state_manager.update_navigation_state({
                'current_path': resolved_path,
                'previous_path': old_path,
                'can_go_back': self.can_navigate_back(),
                'can_go_forward': self.can_navigate_forward(),
                'can_go_up': self.can_navigate_up()
            })
            
            # Emit completion signals
            self.current_path_changed.emit(resolved_path)
            self.navigation_completed.emit(resolved_path)
            
            return True
            
        except Exception as e:
            error_msg = f"Navigation error: {str(e)}"
            self.navigation_failed.emit(path, error_msg)
            return False
            
    def navigate_back(self) -> Optional[str]:
        """
        Navigate to the previous location in history.
        
        Returns:
            str: Previous path if available, None otherwise
        """
        previous_path = self.history_service.get_previous_path()
        if previous_path:
            if self.navigate_to(previous_path, add_to_history=False):
                return previous_path
        return None
        
    def navigate_forward(self) -> Optional[str]:
        """
        Navigate to the next location in history.
        
        Returns:
            str: Next path if available, None otherwise
        """
        next_path = self.history_service.get_next_path()
        if next_path:
            if self.navigate_to(next_path, add_to_history=False):
                return next_path
        return None
        
    def navigate_up(self) -> Optional[str]:
        """
        Navigate to the parent directory.
        
        Returns:
            str: Parent path if available, None otherwise
        """
        current_path = Path(self._current_path)
        parent_path = current_path.parent
        
        if parent_path != current_path:  # Not already at root
            if self.navigate_to(str(parent_path)):
                return str(parent_path)
        return None
        
    def navigate_home(self) -> str:
        """
        Navigate to the user's home directory.
        
        Returns:
            str: Home directory path
        """
        home_path = str(Path.home())
        self.navigate_to(home_path)
        return home_path
        
    # Navigation State Queries
    def get_current_path(self) -> str:
        """Get the current navigation path."""
        return self._current_path
        
    def can_navigate_back(self) -> bool:
        """Check if backward navigation is possible."""
        return self.history_service.can_go_back()
        
    def can_navigate_forward(self) -> bool:
        """Check if forward navigation is possible."""
        return self.history_service.can_go_forward()
        
    def can_navigate_up(self) -> bool:
        """Check if upward navigation is possible."""
        current_path = Path(self._current_path)
        return current_path.parent != current_path
        
    # Path Utilities
    def _validate_path(self, path: str) -> bool:
        """
        Validate that the path exists and is accessible.
        
        Args:
            path: Path to validate
            
        Returns:
            bool: True if path is valid and accessible
        """
        try:
            path_obj = Path(path)
            return path_obj.exists() and os.access(path, os.R_OK)
        except (OSError, PermissionError):
            return False
            
    def _resolve_path(self, path: str) -> str:
        """
        Resolve path to absolute form, handling ~ and relative paths.
        
        Args:
            path: Path to resolve
            
        Returns:
            str: Resolved absolute path
        """
        path_obj = Path(path).expanduser().resolve()
        return str(path_obj)
        
    # Service Integration
    def get_navigation_history(self) -> List[str]:
        """Get the complete navigation history."""
        return self.history_service.get_history()
        
    def get_recent_locations(self, limit: int = 10) -> List[str]:
        """Get recently visited locations."""
        return self.history_service.get_recent_locations(limit)
        
    def clear_history(self):
        """Clear navigation history."""
        self.history_service.clear_history()
```

## 2. LocationManager

### 2.1 Location and Bookmark Management

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json
from pathlib import Path

@dataclass
class QuickLocation:
    """Represents a quick access location."""
    name: str
    path: str
    icon: str
    description: Optional[str] = None
    shortcut: Optional[str] = None
    
@dataclass 
class LocationBookmark:
    """Represents a user-defined bookmark."""
    id: str
    name: str
    path: str
    icon: str = "⭐"
    created: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None

class LocationManager(QObject):
    """
    Manages quick locations, bookmarks, and location-related functionality.
    """
    
    # Signals
    bookmark_added = Signal(LocationBookmark)
    bookmark_removed = Signal(str)  # bookmark_id
    bookmark_updated = Signal(LocationBookmark)
    quick_locations_changed = Signal()
    
    def __init__(self, navigation_service=None):
        super().__init__()
        self.navigation_service = navigation_service
        self._bookmarks = {}
        self._quick_locations = []
        self._bookmarks_file = Path.home() / ".poeditor_bookmarks.json"
        
        self._initialize_quick_locations()
        self._load_bookmarks()
        
    def _initialize_quick_locations(self):
        """Initialize standard quick access locations."""
        self._quick_locations = [
            QuickLocation(
                name="Home",
                path=str(Path.home()),
                icon="🏠",
                description="User home directory",
                shortcut="Ctrl+H"
            ),
            QuickLocation(
                name="Root",
                path="/",
                icon="💾", 
                description="Root directory",
                shortcut="Ctrl+R"
            ),
            QuickLocation(
                name="Applications",
                path="/Applications",
                icon="📁",
                description="Applications folder"
            ),
            QuickLocation(
                name="Documents", 
                path=str(Path.home() / "Documents"),
                icon="📄",
                description="Documents folder"
            ),
            QuickLocation(
                name="Downloads",
                path=str(Path.home() / "Downloads"),
                icon="⬇️",
                description="Downloads folder"
            ),
            QuickLocation(
                name="Desktop",
                path=str(Path.home() / "Desktop"),
                icon="🖥️",
                description="Desktop folder"
            ),
        ]
        
        # Add project root if available
        project_root = self._detect_project_root()
        if project_root:
            self._quick_locations.append(
                QuickLocation(
                    name="Project Root",
                    path=project_root,
                    icon="⚙️",
                    description="Current project root directory",
                    shortcut="Ctrl+P"
                )
            )
            
    def _detect_project_root(self) -> Optional[str]:
        """Detect current project root directory."""
        # Look for common project indicators
        current_dir = Path.cwd()
        
        for parent in [current_dir] + list(current_dir.parents):
            # Check for common project files
            indicators = [
                ".git", ".svn", ".hg",  # Version control
                "pyproject.toml", "setup.py", "requirements.txt",  # Python
                "package.json", "yarn.lock",  # Node.js
                "Cargo.toml",  # Rust
                "pom.xml",  # Java Maven
                "build.gradle",  # Gradle
                ".project",  # Eclipse
                ".vscode"  # VS Code workspace
            ]
            
            if any((parent / indicator).exists() for indicator in indicators):
                return str(parent)
                
        return None
        
    # Quick Locations API
    def get_quick_locations(self) -> List[QuickLocation]:
        """Get all quick access locations."""
        # Filter out locations that don't exist
        valid_locations = []
        for location in self._quick_locations:
            if Path(location.path).exists():
                valid_locations.append(location)
                
        return valid_locations
        
    def add_quick_location(self, location: QuickLocation):
        """Add a custom quick location."""
        self._quick_locations.append(location)
        self.quick_locations_changed.emit()
        
    def remove_quick_location(self, name: str) -> bool:
        """Remove a quick location by name."""
        for i, location in enumerate(self._quick_locations):
            if location.name == name:
                del self._quick_locations[i]
                self.quick_locations_changed.emit()
                return True
        return False
        
    # Bookmarks API
    def get_bookmarks(self) -> List[LocationBookmark]:
        """Get all bookmarks."""
        return list(self._bookmarks.values())
        
    def add_bookmark(self, name: str, path: str, icon: str = "⭐", 
                    description: str = None, tags: List[str] = None) -> LocationBookmark:
        """Add a new bookmark."""
        bookmark_id = self._generate_bookmark_id()
        bookmark = LocationBookmark(
            id=bookmark_id,
            name=name,
            path=path,
            icon=icon,
            description=description,
            tags=tags or []
        )
        
        self._bookmarks[bookmark_id] = bookmark
        self._save_bookmarks()
        self.bookmark_added.emit(bookmark)
        
        return bookmark
        
    def remove_bookmark(self, bookmark_id: str) -> bool:
        """Remove a bookmark by ID."""
        if bookmark_id in self._bookmarks:
            del self._bookmarks[bookmark_id]
            self._save_bookmarks()
            self.bookmark_removed.emit(bookmark_id)
            return True
        return False
        
    def update_bookmark(self, bookmark_id: str, **kwargs) -> bool:
        """Update bookmark properties."""
        if bookmark_id not in self._bookmarks:
            return False
            
        bookmark = self._bookmarks[bookmark_id]
        
        # Update provided fields
        for field_name, value in kwargs.items():
            if hasattr(bookmark, field_name):
                setattr(bookmark, field_name, value)
                
        self._save_bookmarks()
        self.bookmark_updated.emit(bookmark)
        return True
        
    def find_bookmarks(self, query: str) -> List[LocationBookmark]:
        """Find bookmarks matching a query."""
        query_lower = query.lower()
        matches = []
        
        for bookmark in self._bookmarks.values():
            if (query_lower in bookmark.name.lower() or
                query_lower in bookmark.path.lower() or
                (bookmark.description and query_lower in bookmark.description.lower()) or
                any(query_lower in tag.lower() for tag in bookmark.tags)):
                matches.append(bookmark)
                
        return matches
        
    # Persistence
    def _load_bookmarks(self):
        """Load bookmarks from file."""
        if not self._bookmarks_file.exists():
            return
            
        try:
            with open(self._bookmarks_file, 'r') as f:
                data = json.load(f)
                
            for bookmark_data in data.get('bookmarks', []):
                bookmark = LocationBookmark(
                    id=bookmark_data['id'],
                    name=bookmark_data['name'],
                    path=bookmark_data['path'],
                    icon=bookmark_data.get('icon', '⭐'),
                    created=datetime.fromisoformat(bookmark_data['created']),
                    tags=bookmark_data.get('tags', []),
                    description=bookmark_data.get('description')
                )
                self._bookmarks[bookmark.id] = bookmark
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log error and continue with empty bookmarks
            from lg import logger
            logger.error(f"Failed to load bookmarks: {e}")
            
    def _save_bookmarks(self):
        """Save bookmarks to file."""
        try:
            data = {
                'version': '1.0',
                'bookmarks': [
                    {
                        'id': bookmark.id,
                        'name': bookmark.name,
                        'path': bookmark.path,
                        'icon': bookmark.icon,
                        'created': bookmark.created.isoformat(),
                        'tags': bookmark.tags,
                        'description': bookmark.description
                    }
                    for bookmark in self._bookmarks.values()
                ]
            }
            
            # Ensure parent directory exists
            self._bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._bookmarks_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except (OSError, IOError) as e:
            from lg import logger
            logger.error(f"Failed to save bookmarks: {e}")
            
    def _generate_bookmark_id(self) -> str:
        """Generate a unique bookmark ID."""
        import uuid
        return str(uuid.uuid4())
        
    # Import/Export
    def export_bookmarks(self, file_path: str) -> bool:
        """Export bookmarks to a file."""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'bookmarks': [
                    {
                        'name': bookmark.name,
                        'path': bookmark.path,
                        'icon': bookmark.icon,
                        'description': bookmark.description,
                        'tags': bookmark.tags
                    }
                    for bookmark in self._bookmarks.values()
                ]
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
            
        except (OSError, IOError) as e:
            from lg import logger
            logger.error(f"Failed to export bookmarks: {e}")
            return False
            
    def import_bookmarks(self, file_path: str, merge: bool = True) -> bool:
        """Import bookmarks from a file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if not merge:
                self._bookmarks.clear()
                
            for bookmark_data in data.get('bookmarks', []):
                self.add_bookmark(
                    name=bookmark_data['name'],
                    path=bookmark_data['path'],
                    icon=bookmark_data.get('icon', '⭐'),
                    description=bookmark_data.get('description'),
                    tags=bookmark_data.get('tags', [])
                )
                
            return True
            
        except (json.JSONDecodeError, KeyError, OSError, IOError) as e:
            from lg import logger
            logger.error(f"Failed to import bookmarks: {e}")
            return False
```

## 3. NavigationHistoryService

### 3.1 History Management

```python
from collections import deque
from datetime import datetime, timedelta
from typing import List, Optional, Dict

@dataclass
class NavigationEntry:
    """Represents a navigation history entry."""
    path: str
    timestamp: datetime
    visit_count: int = 1
    
    @property
    def relative_time(self) -> str:
        """Get human-readable relative time."""
        delta = datetime.now() - self.timestamp
        
        if delta.total_seconds() < 60:
            return "Just now"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif delta.days == 0:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            return self.timestamp.strftime("%b %d, %Y")

class NavigationHistoryService(QObject):
    """
    Service for managing navigation history and providing history-based features.
    """
    
    # Signals
    history_changed = Signal()
    entry_added = Signal(NavigationEntry)
    history_cleared = Signal()
    
    def __init__(self, navigation_service=None):
        super().__init__()
        self.navigation_service = navigation_service
        
        # History storage
        self._history = deque(maxlen=100)  # Circular buffer for memory efficiency
        self._current_index = -1
        self._path_visit_counts = {}
        self._recent_locations_cache = None
        self._cache_expiry = None
        
    def add_to_history(self, path: str):
        """Add a path to navigation history."""
        now = datetime.now()
        
        # Check if this is the same as current location
        if self._history and self._current_index >= 0:
            current_entry = self._history[self._current_index]
            if current_entry.path == path:
                # Update timestamp and visit count
                current_entry.timestamp = now
                current_entry.visit_count += 1
                self._update_visit_count(path)
                return
                
        # Create new entry
        entry = NavigationEntry(path=path, timestamp=now)
        
        # If we're not at the end of history, truncate forward history
        if self._current_index < len(self._history) - 1:
            # Remove entries after current position
            entries_to_remove = len(self._history) - self._current_index - 1
            for _ in range(entries_to_remove):
                self._history.pop()
                
        # Add new entry
        self._history.append(entry)
        self._current_index = len(self._history) - 1
        
        # Update visit count
        self._update_visit_count(path)
        
        # Clear cache
        self._invalidate_cache()
        
        # Emit signals
        self.entry_added.emit(entry)
        self.history_changed.emit()
        
    def _update_visit_count(self, path: str):
        """Update visit count for a path."""
        self._path_visit_counts[path] = self._path_visit_counts.get(path, 0) + 1
        
    def get_previous_path(self) -> Optional[str]:
        """Get the previous path in history."""
        if self.can_go_back():
            return self._history[self._current_index - 1].path
        return None
        
    def get_next_path(self) -> Optional[str]:
        """Get the next path in history."""
        if self.can_go_forward():
            return self._history[self._current_index + 1].path
        return None
        
    def can_go_back(self) -> bool:
        """Check if backward navigation is possible."""
        return self._current_index > 0
        
    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible."""
        return self._current_index < len(self._history) - 1
        
    def navigate_back(self) -> Optional[str]:
        """Move back in history."""
        if self.can_go_back():
            self._current_index -= 1
            return self._history[self._current_index].path
        return None
        
    def navigate_forward(self) -> Optional[str]:
        """Move forward in history."""
        if self.can_go_forward():
            self._current_index += 1
            return self._history[self._current_index].path
        return None
        
    def get_history(self) -> List[NavigationEntry]:
        """Get the complete navigation history."""
        return list(self._history)
        
    def get_recent_locations(self, limit: int = 10) -> List[NavigationEntry]:
        """Get recent locations with caching."""
        # Use cache if valid
        if (self._recent_locations_cache is not None and
            self._cache_expiry and datetime.now() < self._cache_expiry):
            return self._recent_locations_cache[:limit]
            
        # Build recent locations list
        recent_paths = set()
        recent_entries = []
        
        # Iterate through history in reverse order (most recent first)
        for entry in reversed(self._history):
            if entry.path not in recent_paths:
                recent_paths.add(entry.path)
                recent_entries.append(entry)
                
                if len(recent_entries) >= limit * 2:  # Cache more than requested
                    break
                    
        # Sort by timestamp (most recent first)
        recent_entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Cache results for 30 seconds
        self._recent_locations_cache = recent_entries
        self._cache_expiry = datetime.now() + timedelta(seconds=30)
        
        return recent_entries[:limit]
        
    def get_most_visited_locations(self, limit: int = 10) -> List[tuple]:
        """Get most frequently visited locations."""
        # Sort by visit count
        sorted_locations = sorted(
            self._path_visit_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_locations[:limit]
        
    def clear_history(self):
        """Clear all navigation history."""
        self._history.clear()
        self._current_index = -1
        self._path_visit_counts.clear()
        self._invalidate_cache()
        
        self.history_cleared.emit()
        self.history_changed.emit()
        
    def remove_from_history(self, path: str) -> bool:
        """Remove all entries for a specific path."""
        removed_any = False
        
        # Remove from history deque
        new_history = deque(maxlen=self._history.maxlen)
        new_index = -1
        
        for i, entry in enumerate(self._history):
            if entry.path != path:
                new_history.append(entry)
                if i <= self._current_index:
                    new_index += 1
            else:
                removed_any = True
                
        if removed_any:
            self._history = new_history
            self._current_index = max(-1, new_index)
            
            # Remove from visit counts
            self._path_visit_counts.pop(path, None)
            
            # Invalidate cache
            self._invalidate_cache()
            
            self.history_changed.emit()
            
        return removed_any
        
    def _invalidate_cache(self):
        """Invalidate cached data."""
        self._recent_locations_cache = None
        self._cache_expiry = None
        
    def get_history_statistics(self) -> Dict[str, Any]:
        """Get statistics about navigation history."""
        total_entries = len(self._history)
        unique_paths = len(set(entry.path for entry in self._history))
        
        if total_entries == 0:
            return {
                'total_entries': 0,
                'unique_paths': 0,
                'average_visits_per_path': 0,
                'most_visited_path': None,
                'oldest_entry': None,
                'newest_entry': None
            }
            
        most_visited = max(self._path_visit_counts.items(), key=lambda x: x[1])
        oldest_entry = min(self._history, key=lambda e: e.timestamp)
        newest_entry = max(self._history, key=lambda e: e.timestamp)
        
        return {
            'total_entries': total_entries,
            'unique_paths': unique_paths,
            'average_visits_per_path': total_entries / unique_paths,
            'most_visited_path': most_visited[0],
            'most_visited_count': most_visited[1],
            'oldest_entry': oldest_entry,
            'newest_entry': newest_entry
        }
```

## 4. PathCompletionService

### 4.1 Path Auto-completion

```python
import os
from pathlib import Path
from typing import List, Tuple, Optional
import threading
from concurrent.futures import ThreadPoolExecutor
import time

class PathCompletionService(QObject):
    """
    Service providing path auto-completion functionality.
    """
    
    # Signals
    completion_ready = Signal(str, list)  # query, completions
    completion_failed = Signal(str, str)  # query, error_message
    
    def __init__(self):
        super().__init__()
        self._completion_cache = {}
        self._cache_timeout = 10.0  # seconds
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._completion_history = []
        
    def get_path_completions(self, partial_path: str, max_results: int = 20) -> List[str]:
        """
        Get path completions for a partial path.
        
        Args:
            partial_path: The partial path to complete
            max_results: Maximum number of results to return
            
        Returns:
            List of possible completions
        """
        # Check cache first
        cache_key = f"{partial_path}:{max_results}"
        if cache_key in self._completion_cache:
            cached_result, timestamp = self._completion_cache[cache_key]
            if time.time() - timestamp < self._cache_timeout:
                return cached_result
                
        # Submit completion task
        future = self._executor.submit(self._compute_completions, partial_path, max_results)
        
        try:
            # Wait briefly for completion (non-blocking UI)
            completions = future.result(timeout=0.1)
            
            # Cache result
            self._completion_cache[cache_key] = (completions, time.time())
            
            return completions
            
        except:
            # Return cached result if available, otherwise empty list
            if cache_key in self._completion_cache:
                cached_result, _ = self._completion_cache[cache_key]
                return cached_result
            return []
            
    def get_path_completions_async(self, partial_path: str, max_results: int = 20):
        """
        Get path completions asynchronously and emit signal when ready.
        """
        def completion_callback(future):
            try:
                completions = future.result()
                self.completion_ready.emit(partial_path, completions)
            except Exception as e:
                self.completion_failed.emit(partial_path, str(e))
                
        future = self._executor.submit(self._compute_completions, partial_path, max_results)
        future.add_done_callback(completion_callback)
        
    def _compute_completions(self, partial_path: str, max_results: int) -> List[str]:
        """
        Compute path completions (runs in background thread).
        """
        try:
            # Expand user path
            expanded_path = os.path.expanduser(partial_path)
            path_obj = Path(expanded_path)
            
            # Determine parent directory and filename prefix
            if partial_path.endswith('/') or partial_path.endswith('\\'):
                # Complete within directory
                parent_dir = path_obj
                filename_prefix = ""
            else:
                # Complete filename
                parent_dir = path_obj.parent
                filename_prefix = path_obj.name.lower()
                
            if not parent_dir.exists():
                return []
                
            # Get directory contents
            completions = []
            
            try:
                for item in parent_dir.iterdir():
                    # Check if item matches prefix
                    if item.name.lower().startswith(filename_prefix):
                        # Add trailing slash for directories
                        completion = str(item)
                        if item.is_dir():
                            completion += "/"
                            
                        completions.append(completion)
                        
                        if len(completions) >= max_results:
                            break
                            
            except PermissionError:
                # Skip directories we can't read
                pass
                
            # Sort completions (directories first, then alphabetical)
            completions.sort(key=lambda x: (not x.endswith('/'), x.lower()))
            
            return completions[:max_results]
            
        except Exception:
            return []
            
    def add_to_completion_history(self, path: str):
        """Add a completed path to history for better suggestions."""
        if path not in self._completion_history:
            self._completion_history.append(path)
            
            # Keep history limited
            if len(self._completion_history) > 100:
                self._completion_history.pop(0)
                
    def get_completion_suggestions(self, partial_path: str) -> List[str]:
        """Get suggestions based on completion history."""
        partial_lower = partial_path.lower()
        suggestions = []
        
        for historical_path in reversed(self._completion_history):
            if historical_path.lower().startswith(partial_lower):
                suggestions.append(historical_path)
                
                if len(suggestions) >= 10:
                    break
                    
        return suggestions
        
    def clear_cache(self):
        """Clear the completion cache."""
        self._completion_cache.clear()
        
    def shutdown(self):
        """Shutdown the completion service."""
        self._executor.shutdown(wait=True)
```

## 5. Service Integration and Coordination

### 5.1 Navigation Service Coordinator

```python
class NavigationServiceCoordinator(QObject):
    """
    Coordinates all navigation-related services and provides unified API.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.navigation_service = NavigationService(self)
        self.location_manager = LocationManager(self.navigation_service)
        self.history_service = self.navigation_service.history_service
        self.completion_service = PathCompletionService()
        
        # Set up cross-service connections
        self._setup_service_connections()
        
    def _setup_service_connections(self):
        """Set up connections between services."""
        # Navigation service connections
        self.navigation_service.navigation_completed.connect(
            self.completion_service.add_to_completion_history
        )
        
        # Location manager connections
        self.location_manager.bookmark_added.connect(
            self._on_bookmark_added
        )
        
    def _on_bookmark_added(self, bookmark: LocationBookmark):
        """Handle bookmark addition."""
        # Could trigger cache updates or other coordination tasks
        pass
        
    def shutdown(self):
        """Shutdown all services."""
        self.completion_service.shutdown()
```

This architecture provides a comprehensive, well-structured foundation for the navigation services layer, with proper separation of concerns, caching, async operations, and service coordination.
