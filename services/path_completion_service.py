"""
PathCompletionService - Intelligent path auto-completion service.

This service provides path auto-completion functionality with threading
support for performance and intelligent suggestions based on context.
"""

import os
import threading
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QTimer
from lg import logger


class PathCompletionWorker(QThread):
    """
    Worker thread for performing path completion operations.
    
    This runs completion searches in a background thread to avoid
    blocking the UI during file system operations.
    """
    
    # Worker signals
    completion_ready = Signal(str, list)  # query, results
    completion_error = Signal(str, str)   # query, error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mutex = QMutex()
        self._current_query = ""
        self._should_stop = False
        
    def search_completions(self, query: str):
        """
        Request completion search for the given query.
        
        Args:
            query: Path query to complete
        """
        self._mutex.lock()
        try:
            self._current_query = query
            self._should_stop = False
        finally:
            self._mutex.unlock()
        
        if not self.isRunning():
            self.start()
    
    def stop_search(self):
        """Stop the current search operation."""
        self._mutex.lock()
        try:
            self._should_stop = True
        finally:
            self._mutex.unlock()
    
    def run(self):
        """Main worker thread execution."""
        try:
            self._mutex.lock()
            try:
                query = self._current_query
            finally:
                self._mutex.unlock()
            
            if not query:
                return
            
            # Perform completion search
            results = self._perform_completion_search(query)
            
            # Check if we should still emit results
            self._mutex.lock()
            try:
                should_emit = not self._should_stop and query == self._current_query
            finally:
                self._mutex.unlock()
                
            if should_emit:
                self.completion_ready.emit(query, results)
                    
        except Exception as e:
            logger.error(f"Path completion worker error: {str(e)}")
            self.completion_error.emit(query, str(e))
    
    def _perform_completion_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform the actual completion search.
        
        Args:
            query: Path query to complete
            
        Returns:
            List of completion results
        """
        results = []
        
        try:
            # Handle empty query
            if not query.strip():
                return []
            
            # Expand user path
            expanded_query = os.path.expanduser(query)
            path_obj = Path(expanded_query)
            
            # Determine search directory and prefix
            if expanded_query.endswith(os.sep) or path_obj.is_dir():
                # Query ends with separator or is existing directory
                search_dir = path_obj
                prefix = ""
            else:
                # Query is partial path
                search_dir = path_obj.parent
                prefix = path_obj.name.lower()
            
            # Check if search directory exists and is accessible
            if not search_dir.exists() or not search_dir.is_dir():
                return []
            
            # Search for matching entries
            try:
                for entry in search_dir.iterdir():
                    # Check if we should stop
                    self._mutex.lock()
                    try:
                        should_stop = self._should_stop
                    finally:
                        self._mutex.unlock()
                    
                    if should_stop:
                        break
                    
                    # Filter by prefix
                    if prefix and not entry.name.lower().startswith(prefix):
                        continue
                    
                    # Create result entry
                    result = {
                        'path': str(entry),
                        'name': entry.name,
                        'is_dir': entry.is_dir(),
                        'is_file': entry.is_file(),
                        'display_path': self._get_display_path(entry, query),
                        'completion': self._get_completion_text(entry, query)
                    }
                    
                    results.append(result)
                    
                    # Limit results to prevent overwhelming the UI
                    if len(results) >= 50:
                        break
                        
            except PermissionError:
                logger.warning(f"Permission denied accessing directory: {search_dir}")
            
        except Exception as e:
            logger.error(f"Completion search error for '{query}': {str(e)}")
        
        # Sort results: directories first, then files, both alphabetically
        results.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        return results
    
    def _get_display_path(self, path: Path, query: str) -> str:
        """
        Get display path for completion result.
        
        Args:
            path: Path object
            query: Original query
            
        Returns:
            Display path string
        """
        try:
            # For home directory paths, show ~ form
            if str(path).startswith(str(Path.home())):
                return str(path).replace(str(Path.home()), "~", 1)
            return str(path)
        except Exception:
            return str(path)
    
    def _get_completion_text(self, path: Path, query: str) -> str:
        """
        Get completion text for the result.
        
        Args:
            path: Path object
            query: Original query
            
        Returns:
            Completion text
        """
        try:
            completion = str(path)
            
            # Add separator for directories
            if path.is_dir() and not completion.endswith(os.sep):
                completion += os.sep
            
            # Convert to ~ form if applicable
            if completion.startswith(str(Path.home())):
                completion = completion.replace(str(Path.home()), "~", 1)
            
            return completion
        except Exception:
            return str(path)


class PathCompletionService(QObject):
    """
    Service providing intelligent path auto-completion.
    
    Features:
    - Threaded completion search for performance
    - Context-aware suggestions
    - Recent path prioritization
    - Bookmark integration
    - Smart filtering and ranking
    
    Signals:
        completions_available(str, list): Emitted when completions are ready
        completion_error(str, str): Emitted when completion fails
    """
    
    # Service signals
    completions_available = Signal(str, list)
    completion_error = Signal(str, str)
    
    def __init__(self, parent=None):
        """
        Initialize the PathCompletionService.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Worker thread for completion operations
        self._worker = PathCompletionWorker(self)
        self._worker.completion_ready.connect(self._on_completion_ready)
        self._worker.completion_error.connect(self._on_completion_error)
        
        # Completion settings
        self._completion_enabled = True
        self._min_query_length = 1
        self._completion_timeout = 500  # milliseconds
        
        # Debounce timer to avoid excessive searches
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._perform_debounced_search)
        
        # Current state
        self._pending_query = ""
        self._last_results: List[Dict[str, Any]] = []
        
        # Service dependencies (set via dependency injection)
        self._location_manager = None
        self._navigation_history = None
        
        logger.info("PathCompletionService initialized")
    
    def set_dependencies(self, location_manager, navigation_history):
        """
        Set service dependencies.
        
        Args:
            location_manager: LocationManager instance
            navigation_history: NavigationHistoryService instance
        """
        self._location_manager = location_manager
        self._navigation_history = navigation_history
        logger.info("PathCompletionService dependencies configured")
    
    def request_completions(self, query: str, debounce: bool = True):
        """
        Request path completions for the given query.
        
        Args:
            query: Path query to complete
            debounce: Whether to debounce the request
        """
        if not self._completion_enabled:
            return
        
        if len(query) < self._min_query_length:
            # Clear results for short queries
            self.completions_available.emit(query, [])
            return
        
        self._pending_query = query
        
        if debounce:
            # Use debounce timer to avoid excessive searches
            self._debounce_timer.start(200)  # 200ms delay
        else:
            # Immediate search
            self._perform_search(query)
    
    def cancel_completion(self):
        """Cancel any pending completion operations."""
        self._debounce_timer.stop()
        self._worker.stop_search()
    
    def get_quick_completions(self, query: str) -> List[Dict[str, Any]]:
        """
        Get quick completions from bookmarks and recent locations.
        
        Args:
            query: Query to match against
            
        Returns:
            List of quick completion results
        """
        quick_results = []
        query_lower = query.lower()
        
        try:
            # Add bookmark completions
            if self._location_manager:
                bookmarks = self._location_manager.get_bookmarks()
                for bookmark in bookmarks:
                    if query_lower in bookmark.name.lower() or query_lower in bookmark.path.lower():
                        quick_results.append({
                            'path': bookmark.path,
                            'name': bookmark.name,
                            'is_dir': Path(bookmark.path).is_dir(),
                            'is_file': Path(bookmark.path).is_file(),
                            'display_path': bookmark.path,
                            'completion': bookmark.path,
                            'type': 'bookmark',
                            'icon': bookmark.icon
                        })
            
            # Add quick location completions
            if self._location_manager:
                quick_locations = self._location_manager.get_quick_locations()
                for location in quick_locations:
                    if query_lower in location.name.lower() or query_lower in location.path.lower():
                        quick_results.append({
                            'path': location.path,
                            'name': location.name,
                            'is_dir': True,  # Quick locations are typically directories
                            'is_file': False,
                            'display_path': location.path,
                            'completion': location.path,
                            'type': 'quick_location',
                            'icon': location.icon
                        })
            
            # Add recent location completions
            if self._navigation_history:
                recent_locations = self._navigation_history.get_recent_locations(10)
                for recent in recent_locations:
                    path = recent.get('path', '')
                    if query_lower in path.lower():
                        quick_results.append({
                            'path': path,
                            'name': Path(path).name or path,
                            'is_dir': Path(path).is_dir(),
                            'is_file': Path(path).is_file(),
                            'display_path': path,
                            'completion': path,
                            'type': 'recent',
                            'visit_count': recent.get('visit_count', 1)
                        })
            
        except Exception as e:
            logger.error(f"Error getting quick completions: {str(e)}")
        
        # Remove duplicates and sort by relevance
        unique_results = []
        seen_paths = set()
        
        for result in quick_results:
            if result['path'] not in seen_paths:
                seen_paths.add(result['path'])
                unique_results.append(result)
        
        # Sort by type priority and relevance
        type_priority = {'bookmark': 0, 'quick_location': 1, 'recent': 2}
        unique_results.sort(key=lambda x: (
            type_priority.get(x.get('type'), 3),
            -x.get('visit_count', 0),
            x['name'].lower()
        ))
        
        return unique_results[:10]  # Limit to top 10 quick results
    
    def set_completion_enabled(self, enabled: bool):
        """
        Enable or disable path completion.
        
        Args:
            enabled: Whether to enable completion
        """
        self._completion_enabled = enabled
        if not enabled:
            self.cancel_completion()
        logger.info(f"Path completion {'enabled' if enabled else 'disabled'}")
    
    def set_min_query_length(self, length: int):
        """
        Set minimum query length for triggering completion.
        
        Args:
            length: Minimum number of characters
        """
        self._min_query_length = max(1, length)
        logger.info(f"Minimum query length set to {self._min_query_length}")
    
    def get_last_results(self) -> List[Dict[str, Any]]:
        """
        Get the last completion results.
        
        Returns:
            List of last completion results
        """
        return self._last_results.copy()
    
    def _perform_debounced_search(self):
        """Perform search after debounce delay."""
        if self._pending_query:
            self._perform_search(self._pending_query)
    
    def _perform_search(self, query: str):
        """
        Perform completion search for the query.
        
        Args:
            query: Query to search for
        """
        try:
            # Get quick completions first
            quick_results = self.get_quick_completions(query)
            
            # If we have good quick results, emit them immediately
            if quick_results:
                self.completions_available.emit(query, quick_results)
            
            # Start threaded search for file system completions
            self._worker.search_completions(query)
            
        except Exception as e:
            logger.error(f"Completion search error: {str(e)}")
            self.completion_error.emit(query, str(e))
    
    def _on_completion_ready(self, query: str, results: List[Dict[str, Any]]):
        """
        Handle completion results from worker thread.
        
        Args:
            query: Original query
            results: Completion results
        """
        try:
            # Combine with quick results and remove duplicates
            quick_results = self.get_quick_completions(query)
            combined_results = []
            seen_paths = set()
            
            # Add quick results first
            for result in quick_results:
                if result['path'] not in seen_paths:
                    seen_paths.add(result['path'])
                    combined_results.append(result)
            
            # Add file system results
            for result in results:
                if result['path'] not in seen_paths:
                    seen_paths.add(result['path'])
                    result['type'] = 'filesystem'
                    combined_results.append(result)
            
            # Store results and emit signal
            self._last_results = combined_results
            self.completions_available.emit(query, combined_results)
            
        except Exception as e:
            logger.error(f"Error processing completion results: {str(e)}")
    
    def _on_completion_error(self, query: str, error_message: str):
        """
        Handle completion error from worker thread.
        
        Args:
            query: Original query
            error_message: Error message
        """
        logger.warning(f"Path completion error for '{query}': {error_message}")
        self.completion_error.emit(query, error_message)
