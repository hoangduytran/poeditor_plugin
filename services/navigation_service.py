"""
NavigationService - Core navigation orchestration service.

This service provides the main navigation functionality for the Explorer,
coordinating between different navigation components and managing the
overall navigation state.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from PySide6.QtCore import QObject, Signal, QThread, QTimer
from lg import logger

if TYPE_CHECKING:
    from .navigation_history_service import NavigationHistoryService
    from .location_manager import LocationManager


class NavigationService(QObject):
    """
    Core navigation service providing path navigation and coordination.
    
    This service orchestrates navigation between different components,
    validates paths, manages navigation state, and provides the main
    API for all navigation operations.
    
    Signals:
        navigation_requested(str): Emitted when navigation to a path is requested
        navigation_completed(str): Emitted when navigation is successfully completed
        navigation_failed(str, str): Emitted when navigation fails (path, error)
        current_path_changed(str): Emitted when the current path changes
        navigation_state_changed(dict): Emitted when navigation state changes
    """
    
    # Navigation signals
    navigation_requested = Signal(str)
    navigation_completed = Signal(str)
    navigation_failed = Signal(str, str)
    current_path_changed = Signal(str)
    navigation_state_changed = Signal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize the NavigationService.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Current navigation state
        self._current_path: Optional[str] = None
        self._is_navigating: bool = False
        self._navigation_history: Optional['NavigationHistoryService'] = None  # Will be set by dependency injection
        self._location_manager: Optional['LocationManager'] = None   # Will be set by dependency injection
        
        # Navigation configuration
        self._auto_refresh_enabled: bool = True
        self._validation_enabled: bool = True
        
        # Internal state
        self._navigation_queue: List[str] = []
        self._last_navigation_time: float = 0.0
        
        logger.info("NavigationService initialized")
    
    def set_dependencies(self, history_service: 'NavigationHistoryService', location_manager: 'LocationManager'):
        """
        Set service dependencies.
        
        Args:
            history_service: NavigationHistoryService instance
            location_manager: LocationManager instance
        """
        self._navigation_history = history_service
        self._location_manager = location_manager
        logger.info("NavigationService dependencies configured")
    
    @property
    def current_path(self) -> Optional[str]:
        """Get the current navigation path."""
        return self._current_path
    
    @property
    def is_navigating(self) -> bool:
        """Check if navigation is currently in progress."""
        return self._is_navigating
    
    def navigate_to(self, path: str, add_to_history: bool = True) -> bool:
        """
        Navigate to the specified path.
        
        Args:
            path: Target path for navigation
            add_to_history: Whether to add this navigation to history
            
        Returns:
            bool: True if navigation started successfully, False otherwise
        """
        if not path:
            logger.warning("Navigation attempted with empty path")
            return False
            
        # Validate path if validation is enabled
        if self._validation_enabled:
            if not self._validate_path(path):
                error_msg = f"Invalid path: {path}"
                logger.error(error_msg)
                self.navigation_failed.emit(path, error_msg)
                return False
        
        # Resolve path to absolute form
        resolved_path = self._resolve_path(path)
        if not resolved_path:
            error_msg = f"Could not resolve path: {path}"
            logger.error(error_msg)
            self.navigation_failed.emit(path, error_msg)
            return False
        
        # Check if we're already at this path
        if resolved_path == self._current_path:
            logger.debug(f"Already at path: {resolved_path}")
            return True
        
        # Start navigation
        self._is_navigating = True
        self.navigation_requested.emit(resolved_path)
        
        try:
            # Perform the navigation
            success = self._perform_navigation(resolved_path)
            
            if success:
                # Update current path
                old_path = self._current_path
                self._current_path = resolved_path
                
                # Add to history if requested
                if add_to_history and self._navigation_history:
                    self._navigation_history.add_to_history(resolved_path)
                
                # Update location manager
                if self._location_manager:
                    self._location_manager.update_recent_location(resolved_path)
                
                # Emit signals
                self.current_path_changed.emit(resolved_path)
                self.navigation_completed.emit(resolved_path)
                
                # Update navigation state
                self._update_navigation_state()
                
                logger.info(f"Navigation successful: {old_path} -> {resolved_path}")
                
            else:
                error_msg = f"Navigation failed to: {resolved_path}"
                logger.error(error_msg)
                self.navigation_failed.emit(resolved_path, error_msg)
                
        except Exception as e:
            error_msg = f"Navigation exception: {str(e)}"
            logger.error(error_msg)
            self.navigation_failed.emit(resolved_path, error_msg)
            success = False
        
        finally:
            self._is_navigating = False
        
        return success
    
    def can_navigate_back(self) -> bool:
        """
        Check if backward navigation is possible.
        
        Returns:
            bool: True if can navigate back, False otherwise
        """
        if not self._navigation_history:
            return False
        return self._navigation_history.can_go_back()
    
    def can_navigate_forward(self) -> bool:
        """
        Check if forward navigation is possible.
        
        Returns:
            bool: True if can navigate forward, False otherwise
        """
        if not self._navigation_history:
            return False
        return self._navigation_history.can_go_forward()
    
    def navigate_back(self) -> bool:
        """
        Navigate to the previous location in history.
        
        Returns:
            bool: True if navigation started successfully, False otherwise
        """
        if not self.can_navigate_back():
            logger.warning("Cannot navigate back - no history available")
            return False
        
        if not self._navigation_history:
            logger.error("Navigation history service not available")
            return False
        
        previous_path = self._navigation_history.go_back()
        if previous_path:
            return self.navigate_to(previous_path, add_to_history=False)
        
        return False
    
    def navigate_forward(self) -> bool:
        """
        Navigate to the next location in history.
        
        Returns:
            bool: True if navigation started successfully, False otherwise
        """
        if not self.can_navigate_forward():
            logger.warning("Cannot navigate forward - no history available")
            return False
        
        if not self._navigation_history:
            logger.error("Navigation history service not available")
            return False
        
        next_path = self._navigation_history.go_forward()
        if next_path:
            return self.navigate_to(next_path, add_to_history=False)
        
        return False
    
    def navigate_up(self) -> bool:
        """
        Navigate to the parent directory.
        
        Returns:
            bool: True if navigation started successfully, False otherwise
        """
        if not self._current_path:
            logger.warning("Cannot navigate up - no current path")
            return False
        
        current_path = Path(self._current_path)
        parent_path = current_path.parent
        
        if parent_path == current_path:
            logger.warning("Already at root directory")
            return False
        
        return self.navigate_to(str(parent_path))
    
    def navigate_home(self) -> bool:
        """
        Navigate to the user's home directory.
        
        Returns:
            bool: True if navigation started successfully, False otherwise
        """
        home_path = str(Path.home())
        return self.navigate_to(home_path)
    
    def refresh_current_location(self) -> bool:
        """
        Refresh the current location.
        
        Returns:
            bool: True if refresh completed successfully, False otherwise
        """
        if not self._current_path:
            logger.warning("Cannot refresh - no current path")
            return False
        
        # Re-emit navigation signals to trigger refresh
        self.navigation_requested.emit(self._current_path)
        self.navigation_completed.emit(self._current_path)
        
        logger.info(f"Refreshed location: {self._current_path}")
        return True
    
    def get_navigation_state(self) -> Dict[str, Any]:
        """
        Get the current navigation state.
        
        Returns:
            Dict containing current navigation state information
        """
        return {
            'current_path': self._current_path,
            'is_navigating': self._is_navigating,
            'can_go_back': self.can_navigate_back(),
            'can_go_forward': self.can_navigate_forward(),
            'auto_refresh_enabled': self._auto_refresh_enabled,
            'validation_enabled': self._validation_enabled
        }
    
    def set_auto_refresh_enabled(self, enabled: bool):
        """
        Enable or disable automatic refresh.
        
        Args:
            enabled: Whether to enable auto-refresh
        """
        self._auto_refresh_enabled = enabled
        self._update_navigation_state()
        logger.info(f"Auto-refresh {'enabled' if enabled else 'disabled'}")
    
    def set_validation_enabled(self, enabled: bool):
        """
        Enable or disable path validation.
        
        Args:
            enabled: Whether to enable path validation
        """
        self._validation_enabled = enabled
        logger.info(f"Path validation {'enabled' if enabled else 'disabled'}")
    
    def _validate_path(self, path: str) -> bool:
        """
        Validate if the given path is accessible.
        
        Args:
            path: Path to validate
            
        Returns:
            bool: True if path is valid and accessible, False otherwise
        """
        try:
            path_obj = Path(path)
            return path_obj.exists()
        except Exception as e:
            logger.error(f"Path validation error for '{path}': {str(e)}")
            return False
    
    def _resolve_path(self, path: str) -> Optional[str]:
        """
        Resolve path to absolute form.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path or None if resolution fails
        """
        try:
            path_obj = Path(path).expanduser().resolve()
            return str(path_obj)
        except Exception as e:
            logger.error(f"Path resolution error for '{path}': {str(e)}")
            return None
    
    def _perform_navigation(self, path: str) -> bool:
        """
        Perform the actual navigation operation.
        
        This method can be overridden by subclasses to implement
        specific navigation behavior.
        
        Args:
            path: Resolved path to navigate to
            
        Returns:
            bool: True if navigation succeeded, False otherwise
        """
        try:
            # Basic implementation - verify path exists and is accessible
            path_obj = Path(path)
            if not path_obj.exists():
                return False
            
            # For directories, check if readable
            if path_obj.is_dir():
                try:
                    list(path_obj.iterdir())
                    return True
                except PermissionError:
                    logger.error(f"Permission denied accessing directory: {path}")
                    return False
            
            # For files, just check existence
            return path_obj.is_file()
            
        except Exception as e:
            logger.error(f"Navigation performance error: {str(e)}")
            return False
    
    def _update_navigation_state(self):
        """Update and emit the current navigation state."""
        state = self.get_navigation_state()
        self.navigation_state_changed.emit(state)
