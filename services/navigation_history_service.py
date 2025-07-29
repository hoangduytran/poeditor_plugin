"""
NavigationHistoryService - Navigation history tracking and management.

This service manages the navigation history, providing back/forward
functionality and tracking recent locations with timestamps.
"""

import json
import time
from collections import deque
from pathlib import Path
from typing import Optional, List, Dict, Any, Deque
from datetime import datetime, timedelta
from PySide6.QtCore import QObject, Signal, QStandardPaths
from lg import logger


class NavigationHistoryService(QObject):
    """
    Service for managing navigation history and recent locations.
    
    Provides back/forward navigation functionality, recent location tracking,
    and persistent storage of navigation history.
    
    Signals:
        history_changed(): Emitted when navigation history changes
        recent_locations_changed(): Emitted when recent locations list changes
    """
    
    # History signals
    history_changed = Signal()
    recent_locations_changed = Signal()
    
    # Configuration constants
    MAX_HISTORY_SIZE = 100
    MAX_RECENT_LOCATIONS = 20
    HISTORY_FILE_NAME = "navigation_history.json"
    RECENT_LOCATIONS_FILE_NAME = "recent_locations.json"
    
    def __init__(self, parent=None):
        """
        Initialize the NavigationHistoryService.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # History deques for back/forward navigation
        self._back_history: Deque[str] = deque(maxlen=self.MAX_HISTORY_SIZE)
        self._forward_history: Deque[str] = deque(maxlen=self.MAX_HISTORY_SIZE)
        
        # Current position tracking
        self._current_path: Optional[str] = None
        
        # Recent locations with metadata
        self._recent_locations: List[Dict[str, Any]] = []
        
        # Storage paths
        self._storage_dir = self._get_storage_directory()
        self._history_file_path = self._storage_dir / self.HISTORY_FILE_NAME
        self._recent_file_path = self._storage_dir / self.RECENT_LOCATIONS_FILE_NAME
        
        # Load persistent data
        self._load_history()
        self._load_recent_locations()
        
        logger.info("NavigationHistoryService initialized")
    
    def add_to_history(self, path: str):
        """
        Add a path to the navigation history.
        
        Args:
            path: Path to add to history
        """
        if not path:
            return
        
        # If we have a current path, add it to back history
        if self._current_path and self._current_path != path:
            self._back_history.append(self._current_path)
            
            # Clear forward history when adding new location
            self._forward_history.clear()
        
        # Update current path
        self._current_path = path
        
        # Update recent locations
        self._update_recent_location(path)
        
        # Save to persistent storage
        self._save_history()
        
        # Emit signals
        self.history_changed.emit()
        
        logger.debug(f"Added to history: {path}")
    
    def can_go_back(self) -> bool:
        """
        Check if backward navigation is possible.
        
        Returns:
            bool: True if can go back, False otherwise
        """
        return len(self._back_history) > 0
    
    def can_go_forward(self) -> bool:
        """
        Check if forward navigation is possible.
        
        Returns:
            bool: True if can go forward, False otherwise
        """
        return len(self._forward_history) > 0
    
    def go_back(self) -> Optional[str]:
        """
        Go back to the previous location in history.
        
        Returns:
            str: Previous path or None if no history available
        """
        if not self.can_go_back():
            logger.warning("Cannot go back - no history available")
            return None
        
        # Move current path to forward history
        if self._current_path:
            self._forward_history.appendleft(self._current_path)
        
        # Get previous path from back history
        previous_path = self._back_history.pop()
        self._current_path = previous_path
        
        # Save state and emit signals
        self._save_history()
        self.history_changed.emit()
        
        logger.debug(f"Navigated back to: {previous_path}")
        return previous_path
    
    def go_forward(self) -> Optional[str]:
        """
        Go forward to the next location in history.
        
        Returns:
            str: Next path or None if no forward history available
        """
        if not self.can_go_forward():
            logger.warning("Cannot go forward - no forward history available")
            return None
        
        # Move current path to back history
        if self._current_path:
            self._back_history.append(self._current_path)
        
        # Get next path from forward history
        next_path = self._forward_history.popleft()
        self._current_path = next_path
        
        # Save state and emit signals
        self._save_history()
        self.history_changed.emit()
        
        logger.debug(f"Navigated forward to: {next_path}")
        return next_path
    
    def get_back_history(self, limit: int = 10) -> List[str]:
        """
        Get the back navigation history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of paths in back history (most recent first)
        """
        return list(reversed(list(self._back_history)[-limit:]))
    
    def get_forward_history(self, limit: int = 10) -> List[str]:
        """
        Get the forward navigation history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of paths in forward history
        """
        return list(self._forward_history)[:limit]
    
    def get_recent_locations(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent locations with metadata.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent location dictionaries with metadata
        """
        if limit is None:
            limit = self.MAX_RECENT_LOCATIONS
        
        return self._recent_locations[:limit]
    
    def clear_history(self):
        """Clear all navigation history."""
        self._back_history.clear()
        self._forward_history.clear()
        self._current_path = None
        
        # Save cleared state
        self._save_history()
        self.history_changed.emit()
        
        logger.info("Navigation history cleared")
    
    def clear_recent_locations(self):
        """Clear all recent locations."""
        self._recent_locations.clear()
        
        # Save cleared state
        self._save_recent_locations()
        self.recent_locations_changed.emit()
        
        logger.info("Recent locations cleared")
    
    def remove_from_recent_locations(self, path: str):
        """
        Remove a specific path from recent locations.
        
        Args:
            path: Path to remove
        """
        self._recent_locations = [
            loc for loc in self._recent_locations 
            if loc.get('path') != path
        ]
        
        # Save updated state
        self._save_recent_locations()
        self.recent_locations_changed.emit()
        
        logger.debug(f"Removed from recent locations: {path}")
    
    def get_history_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about navigation history.
        
        Returns:
            Dictionary containing history statistics
        """
        return {
            'back_history_count': len(self._back_history),
            'forward_history_count': len(self._forward_history),
            'recent_locations_count': len(self._recent_locations),
            'current_path': self._current_path,
            'total_visits': sum(loc.get('visit_count', 1) for loc in self._recent_locations)
        }
    
    def _update_recent_location(self, path: str):
        """
        Update the recent locations list with the given path.
        
        Args:
            path: Path to update in recent locations
        """
        current_time = datetime.now().isoformat()
        
        # Check if path already exists in recent locations
        existing_location = None
        for i, location in enumerate(self._recent_locations):
            if location.get('path') == path:
                existing_location = location
                self._recent_locations.pop(i)
                break
        
        # Create or update location entry
        if existing_location:
            existing_location['last_visited'] = current_time
            existing_location['visit_count'] = existing_location.get('visit_count', 1) + 1
            location_entry = existing_location
        else:
            location_entry = {
                'path': path,
                'last_visited': current_time,
                'visit_count': 1,
                'display_name': self._get_display_name(path)
            }
        
        # Add to beginning of list
        self._recent_locations.insert(0, location_entry)
        
        # Trim to maximum size
        if len(self._recent_locations) > self.MAX_RECENT_LOCATIONS:
            self._recent_locations = self._recent_locations[:self.MAX_RECENT_LOCATIONS]
        
        # Save updated state
        self._save_recent_locations()
        self.recent_locations_changed.emit()
    
    def _get_display_name(self, path: str) -> str:
        """
        Get a display name for the given path.
        
        Args:
            path: Path to get display name for
            
        Returns:
            Display name for the path
        """
        try:
            path_obj = Path(path)
            if path_obj == Path.home():
                return "Home"
            elif path_obj == Path("/"):
                return "Root"
            elif path_obj.name:
                return path_obj.name
            else:
                return str(path_obj)
        except Exception:
            return str(path)
    
    def _get_storage_directory(self) -> Path:
        """
        Get the directory for storing persistent data.
        
        Returns:
            Path object for storage directory
        """
        app_data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        storage_dir = Path(app_data_dir) / "navigation"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir
    
    def _load_history(self):
        """Load navigation history from persistent storage."""
        try:
            if self._history_file_path.exists():
                with open(self._history_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load history lists
                back_history = data.get('back_history', [])
                forward_history = data.get('forward_history', [])
                
                # Populate deques
                self._back_history.extend(back_history)
                self._forward_history.extend(forward_history)
                
                # Load current path
                self._current_path = data.get('current_path')
                
                logger.info(f"Loaded navigation history: {len(back_history)} back, {len(forward_history)} forward")
                
        except Exception as e:
            logger.error(f"Failed to load navigation history: {str(e)}")
    
    def _save_history(self):
        """Save navigation history to persistent storage."""
        try:
            data = {
                'back_history': list(self._back_history),
                'forward_history': list(self._forward_history),
                'current_path': self._current_path,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self._history_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save navigation history: {str(e)}")
    
    def _load_recent_locations(self):
        """Load recent locations from persistent storage."""
        try:
            if self._recent_file_path.exists():
                with open(self._recent_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._recent_locations = data.get('recent_locations', [])
                
                # Clean up old entries (older than 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                self._recent_locations = [
                    loc for loc in self._recent_locations
                    if loc.get('last_visited') and self._parse_timestamp(loc.get('last_visited', '')) > cutoff_date
                ]
                
                logger.info(f"Loaded {len(self._recent_locations)} recent locations")
                
        except Exception as e:
            logger.error(f"Failed to load recent locations: {str(e)}")
    
    def _save_recent_locations(self):
        """Save recent locations to persistent storage."""
        try:
            data = {
                'recent_locations': self._recent_locations,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self._recent_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save recent locations: {str(e)}")
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string to datetime object.
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            datetime object
        """
        try:
            return datetime.fromisoformat(timestamp_str)
        except Exception:
            return datetime.now() - timedelta(days=31)  # Default to old date
