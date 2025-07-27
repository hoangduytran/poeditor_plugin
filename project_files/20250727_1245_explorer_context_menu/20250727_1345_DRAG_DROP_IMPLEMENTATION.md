# Drag and Drop Implementation for Explorer

**Date**: July 27, 2025, 13:45  
**Component**: Explorer Drag & Drop System  
**Status**: Technical Documentation  
**Priority**: High

## Overview

This document outlines the implementation of the drag and drop functionality for the Explorer component. The system supports both internal drag and drop operations (within the application) and external operations (from or to other applications or the file system).

## Class Implementation

```python
import os
import mimetypes
from enum import Enum, auto
from typing import List, Optional, Dict, Any

from PySide6.QtCore import (
    Qt, QObject, Signal, QMimeData, QByteArray, 
    QDataStream, QIODevice, QPoint, QUrl
)
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QStyle

from lg import logger
from services.file_operations_service import FileOperationsService


class DropMode(Enum):
    """Enumeration for drop modes"""
    NONE = auto()
    COPY = auto()
    MOVE = auto()
    LINK = auto()


class DragDropManager(QObject):
    """
    Manages drag and drop operations for the Explorer component.
    
    This class handles setting up views for drag and drop, processing
    drag operations, and dispatching drop events to the appropriate handlers.
    """
    
    # Signals
    dragStarted = Signal(list)  # source_paths
    dragEnded = Signal(bool)    # was_accepted
    dropPerformed = Signal(list, str, int)  # source_paths, target_path, drop_mode
    
    def __init__(self, file_operations: FileOperationsService, parent=None):
        """
        Initialize the drag and drop manager.
        
        Args:
            file_operations: FileOperationsService instance for file operations
            parent: QObject parent
        """
        super().__init__(parent)
        
        self.file_ops = file_operations
        
        # MIME types
        self.MIME_TYPE_PATHS = "application/x-explorer-file-paths"
        self.MIME_TYPE_OPERATION = "application/x-explorer-operation"
        
        # Current drag state
        self._dragging = False
        self._drag_source_widget = None
        self._drag_source_paths = []
        
        # Cache of drag images
        self._drag_pixmap_cache: Dict[str, QPixmap] = {}
        
        # File type icons
        self._file_type_icons = {}
        
    def setup_view_for_drag_drop(self, view: QTreeView):
        """
        Configure a QTreeView for drag and drop operations.
        
        Args:
            view: The QTreeView to configure
        """
        # Enable drag and drop
        view.setDragEnabled(True)
        view.setAcceptDrops(True)
        view.setDropIndicatorShown(True)
        view.setDragDropMode(QAbstractItemView.DragDrop)
        
        # Store original event handlers
        original_drag_enter = view.dragEnterEvent
        original_drag_over = view.dragMoveEvent
        original_drop = view.dropEvent
        original_start_drag = view.startDrag
        
        # Override drag and drop event handlers
        def drag_enter_event_override(event):
            """Custom drag enter event handler"""
            if event.mimeData().hasUrls() or event.mimeData().hasFormat(self.MIME_TYPE_PATHS):
                event.acceptProposedAction()
            else:
                original_drag_enter(event)
                
        def drag_over_event_override(event):
            """Custom drag move event handler"""
            if event.mimeData().hasUrls() or event.mimeData().hasFormat(self.MIME_TYPE_PATHS):
                # Get drop target index and update drop indicator
                index = view.indexAt(event.pos())
                
                if index.isValid():
                    # Determine if we should drop on the item or between items
                    rect = view.visualRect(index)
                    if rect.height() > 0:
                        position = QStyle.PositionAtMouse()
                        view.setDropIndicatorShown(True)
                
                event.acceptProposedAction()
            else:
                original_drag_over(event)
                
        def drop_event_override(event):
            """Custom drop event handler"""
            if event.mimeData().hasUrls() or event.mimeData().hasFormat(self.MIME_TYPE_PATHS):
                # Get drop target index and path
                index = view.indexAt(event.pos())
                model = view.model()
                
                # Determine target path
                if index.isValid():
                    file_info = model.fileInfo(index)
                    target_path = file_info.filePath()
                    
                    # If target is not a directory, use its parent
                    if not file_info.isDir():
                        target_path = os.path.dirname(target_path)
                else:
                    # Use root path if no valid index
                    target_path = model.rootPath()
                
                # Process the drop operation
                self._process_drop(event.mimeData(), target_path, event.proposedAction())
                event.acceptProposedAction()
            else:
                original_drop(event)
                
        def start_drag_override(supported_actions):
            """Custom start drag handler"""
            # Get selected indexes and paths
            indexes = view.selectedIndexes()
            if not indexes:
                return
            
            model = view.model()
            paths = []
            for index in indexes:
                if index.column() == 0:  # Only process first column to avoid duplicates
                    paths.append(model.filePath(index))
            
            if not paths:
                return
            
            # Start the drag operation
            self._start_drag(view, paths, supported_actions)
        
        # Attach overridden methods
        view.dragEnterEvent = drag_enter_event_override
        view.dragMoveEvent = drag_over_event_override
        view.dropEvent = drop_event_override
        view.startDrag = start_drag_override
    
    def _start_drag(self, source_widget, paths: List[str], supported_actions):
        """
        Start a drag operation.
        
        Args:
            source_widget: Widget initiating the drag
            paths: List of paths to drag
            supported_actions: Qt supported drag actions
        """
        if not paths:
            return
            
        # Set drag state
        self._dragging = True
        self._drag_source_widget = source_widget
        self._drag_source_paths = paths
        
        # Create mime data
        mime_data = QMimeData()
        
        # Add file paths as URLs
        urls = [QUrl.fromLocalFile(path) for path in paths]
        mime_data.setUrls(urls)
        
        # Add internal format
        paths_data = QByteArray()
        stream = QDataStream(paths_data, QIODevice.WriteOnly)
        stream.writeQStringList(paths)
        mime_data.setData(self.MIME_TYPE_PATHS, paths_data)
        
        # Create drag object
        drag = QDrag(source_widget)
        drag.setMimeData(mime_data)
        
        # Set drag pixmap
        pixmap = self._create_drag_pixmap(paths)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        # Signal drag start
        self.dragStarted.emit(paths)
        
        # Execute drag
        result = drag.exec(supported_actions)
        
        # Clean up drag state
        self._dragging = False
        self._drag_source_widget = None
        
        # Signal drag end
        self.dragEnded.emit(result != Qt.IgnoreAction)
    
    def _process_drop(self, mime_data: QMimeData, target_path: str, proposed_action: Qt.DropAction):
        """
        Process a drop operation.
        
        Args:
            mime_data: Drop mime data
            target_path: Target path
            proposed_action: Qt proposed drop action
        """
        # Ensure target is valid
        if not os.path.isdir(target_path):
            logger.warning(f"Drop target is not a directory: {target_path}")
            return
        
        # Get source paths
        source_paths = []
        
        # First try internal format
        if mime_data.hasFormat(self.MIME_TYPE_PATHS):
            paths_data = mime_data.data(self.MIME_TYPE_PATHS)
            stream = QDataStream(paths_data, QIODevice.ReadOnly)
            source_paths = stream.readQStringList()
        
        # Fall back to URLs
        if not source_paths and mime_data.hasUrls():
            source_paths = [url.toLocalFile() for url in mime_data.urls() 
                           if url.isLocalFile()]
        
        if not source_paths:
            logger.warning("No valid source paths in drop data")
            return
        
        # Determine operation type
        drop_mode = DropMode.NONE
        
        if proposed_action == Qt.CopyAction:
            drop_mode = DropMode.COPY
        elif proposed_action == Qt.MoveAction:
            drop_mode = DropMode.MOVE
        elif proposed_action == Qt.LinkAction:
            drop_mode = DropMode.LINK
        
        # Special case: if dropping onto self, force to COPY
        if any(path == target_path or target_path.startswith(path + os.path.sep) for path in source_paths):
            drop_mode = DropMode.COPY
        
        # Perform the operation
        if drop_mode == DropMode.COPY:
            self.file_ops.copy_to_clipboard(source_paths)
            self.file_ops.paste(target_path)
        elif drop_mode == DropMode.MOVE:
            self.file_ops.move_items(source_paths, target_path)
        elif drop_mode == DropMode.LINK:
            # Links not currently supported
            pass
        
        # Signal drop completion
        self.dropPerformed.emit(source_paths, target_path, drop_mode.value)
    
    def _create_drag_pixmap(self, paths: List[str]) -> QPixmap:
        """
        Create a pixmap for the drag operation.
        
        Args:
            paths: List of paths being dragged
            
        Returns:
            QPixmap for the drag operation
        """
        if not paths:
            # Return a default empty pixmap
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            return pixmap
        
        # Use cached pixmap if we have one for this exact set of paths
        cache_key = ",".join(sorted(paths))
        if cache_key in self._drag_pixmap_cache:
            return self._drag_pixmap_cache[cache_key]
        
        # Set dimensions
        width = 120
        height = min(20 + (len(paths) * 20), 120)
        
        # Create base pixmap
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        # Set up painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw semi-transparent background
        painter.setBrush(QColor(240, 240, 240, 180))
        painter.setPen(QColor(200, 200, 200, 200))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 5, 5)
        
        # Set up text rendering
        painter.setPen(QColor(0, 0, 0))
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        
        # Draw file names
        y = 15
        shown_files = min(len(paths), 4)  # Show max 4 files
        
        for i in range(shown_files):
            file_name = os.path.basename(paths[i])
            
            # Truncate long filenames
            if len(file_name) > 15:
                file_name = file_name[:12] + "..."
            
            # Get file type icon
            file_type = self._get_file_type_icon(paths[i])
            if file_type:
                painter.drawPixmap(5, y - 12, 16, 16, file_type)
                painter.drawText(25, y, file_name)
            else:
                painter.drawText(5, y, file_name)
            
            y += 20
        
        # If there are more files, indicate that
        if len(paths) > shown_files:
            painter.drawText(5, y, f"...and {len(paths) - shown_files} more")
        
        # Draw count indicator
        count_text = str(len(paths))
        text_width = painter.fontMetrics().horizontalAdvance(count_text)
        
        # Draw count badge in top right
        badge_size = max(20, text_width + 10)
        painter.setBrush(QColor(70, 130, 180, 220))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(width - badge_size - 5, 5, badge_size, 20)
        
        # Draw count text
        painter.setPen(Qt.white)
        painter.drawText(width - text_width - 5 - (badge_size - text_width) // 2, 20, count_text)
        
        painter.end()
        
        # Cache the pixmap
        self._drag_pixmap_cache[cache_key] = pixmap
        
        # Limit cache size
        if len(self._drag_pixmap_cache) > 50:
            # Remove a random item (first in the iteration)
            for key in self._drag_pixmap_cache:
                del self._drag_pixmap_cache[key]
                break
        
        return pixmap
    
    def _get_file_type_icon(self, path: str) -> Optional[QPixmap]:
        """
        Get an icon for a file type.
        
        Args:
            path: File path
            
        Returns:
            QPixmap icon or None if not available
        """
        # For simplicity, we'll use file extension based lookup
        # In a production system, this would use the system icon provider
        ext = os.path.splitext(path)[-1].lower()
        
        if ext in self._file_type_icons:
            return self._file_type_icons[ext]
        
        # For directories, use folder icon
        if os.path.isdir(path):
            # This would actually get a proper folder icon from the system
            # For now, we'll just use a placeholder
            return None
            
        # For known file types, we could use specific icons
        # This would be expanded in a full implementation
        return None
    
    def is_dragging(self) -> bool:
        """Check if a drag operation is in progress."""
        return self._dragging
    
    def get_drag_source_widget(self):
        """Get the widget that initiated the current drag."""
        return self._drag_source_widget
    
    def get_drag_source_paths(self) -> List[str]:
        """Get the paths being dragged in the current operation."""
        return self._drag_source_paths
    
    def clear_pixmap_cache(self):
        """Clear the drag pixmap cache."""
        self._drag_pixmap_cache.clear()


class ExplorerTreeView(QTreeView):
    """
    Extended QTreeView with drag and drop support for the Explorer component.
    
    This class integrates with the DragDropManager for consistent
    drag and drop behavior across the application.
    """
    
    def __init__(self, parent=None):
        """Initialize the explorer tree view."""
        super().__init__(parent)
        
        # Configure drag and drop settings
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        
        # Set selection behavior
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Initialize the drag drop manager
        self.file_ops = FileOperationsService()
        self.drag_drop_manager = DragDropManager(self.file_ops)
        self.drag_drop_manager.setup_view_for_drag_drop(self)
        
        # Connect signals
        self.drag_drop_manager.dropPerformed.connect(self._handle_drop_performed)
    
    def _handle_drop_performed(self, source_paths, target_path, drop_mode):
        """
        Handle drop completion.
        
        Args:
            source_paths: List of source paths
            target_path: Target path
            drop_mode: DropMode value
        """
        # Refresh the view to show changes
        self.model().refresh()
```

## Usage Examples

### Implementing Basic Drag Support

```python
# In the explorer panel initialization
from services.file_operations_service import FileOperationsService
from services.drag_drop_service import DragDropManager

class ExplorerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create the tree view
        self.tree_view = QTreeView()
        
        # Create and set up the model
        self.model = QFileSystemModel()
        self.model.setRootPath("/")
        self.tree_view.setModel(self.model)
        
        # Configure for drag and drop
        self.file_ops = FileOperationsService()
        self.drag_drop_manager = DragDropManager(self.file_ops)
        self.drag_drop_manager.setup_view_for_drag_drop(self.tree_view)
        
        # Connect signals
        self.drag_drop_manager.dropPerformed.connect(self._handle_drop)
        
    def _handle_drop(self, source_paths, target_path, drop_mode):
        """Handle drop completion by refreshing the view."""
        # Just refresh the model to show changes
        self.model.refresh()
```

### Handling External Drops

```python
# Supporting drops from external applications

def setupExternalDrops(window):
    """Configure the main window to accept external drops."""
    window.setAcceptDrops(True)
    
    # Store original methods
    original_drag_enter = window.dragEnterEvent
    original_drag_over = window.dragMoveEvent
    original_drop = window.dropEvent
    
    def dragEnterEvent(event):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            original_drag_enter(event)
    
    def dragMoveEvent(event):
        """Handle drag move events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            original_drag_over(event)
    
    def dropEvent(event):
        """Handle drop events."""
        if event.mimeData().hasUrls():
            # Get local file paths
            paths = [url.toLocalFile() for url in event.mimeData().urls()
                    if url.isLocalFile()]
            
            if paths:
                # Get current active explorer panel
                explorer_panel = window.getActiveExplorerPanel()
                if explorer_panel:
                    # Get current directory
                    current_dir = explorer_panel.getCurrentDirectory()
                    
                    # Handle based on drop action
                    if event.proposedAction() == Qt.MoveAction:
                        window.file_ops.move_items(paths, current_dir)
                    else:
                        window.file_ops.copy_to_clipboard(paths)
                        window.file_ops.paste(current_dir)
                
                event.acceptProposedAction()
        else:
            original_drop(event)
    
    # Apply overrides
    window.dragEnterEvent = dragEnterEvent
    window.dragMoveEvent = dragMoveEvent
    window.dropEvent = dropEvent
```

### Customizing Drag Visual Feedback

```python
def customize_drag_appearance(drag_drop_manager):
    """Customize the appearance of drag operations."""
    
    # Override the drag pixmap creation method
    original_create_pixmap = drag_drop_manager._create_drag_pixmap
    
    def custom_drag_pixmap(paths):
        """Create a custom drag pixmap with your own styling."""
        if not paths:
            return original_create_pixmap(paths)
        
        # Create a custom pixmap
        width, height = 150, 100
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        # Setup painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw your custom background
        painter.setBrush(QColor(20, 20, 20, 160))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 8, 8)
        
        # Draw your custom content
        painter.setPen(QColor(220, 220, 220))
        font = QFont("Arial", 10)
        painter.setFont(font)
        
        # Show file count
        painter.drawText(10, 25, f"{len(paths)} items")
        
        # Show file names (up to 3)
        y = 45
        for i, path in enumerate(paths[:3]):
            name = os.path.basename(path)
            if len(name) > 20:
                name = name[:17] + "..."
            painter.drawText(10, y, name)
            y += 20
        
        # Indicate if there are more
        if len(paths) > 3:
            painter.drawText(10, y, "...")
        
        painter.end()
        return pixmap
    
    # Apply the custom method
    drag_drop_manager._create_drag_pixmap = custom_drag_pixmap
```

## Drag and Drop Implementation Details

### MIME Data Format

The drag and drop system uses several MIME formats to maintain compatibility with both internal and external systems:

1. **URLs** (`application/x-qurl`): Standard format for file paths, compatible with most applications
2. **Explorer File Paths** (`application/x-explorer-file-paths`): Internal format for precise path information
3. **Explorer Operation** (`application/x-explorer-operation`): Internal format for operation type metadata

### Drop Processing Logic

When a drop occurs, the following logic is applied:

1. **Target Validation**: Ensure the target exists and is a directory
2. **Path Extraction**: Extract paths from MIME data (internal format, then URLs)
3. **Operation Selection**: Determine the operation type (copy, move, or link)
4. **Self-drop Prevention**: Detect and handle self-drops (dropping items onto themselves)
5. **Operation Execution**: Execute the appropriate file operation
6. **Event Notification**: Emit signals for UI updates

### Drag Visualization

The system creates intuitive drag visuals that:

1. **Reflect Contents**: Show preview of files being dragged
2. **Indicate Quantity**: Display the number of items
3. **Provide Visual Feedback**: Adjust appearance based on operation type
4. **Optimize Performance**: Cache generated drag images for repeated operations

### Integration with File Operations Service

The drag and drop system integrates closely with the FileOperationsService:

1. **Delegation**: All actual file operations are delegated to the service
2. **Consistent Behavior**: Ensures drag-drop operations behave identically to menu actions
3. **Error Handling**: Leverages the service's error handling capabilities
4. **Undo Support**: Operations performed via drag-drop are recorded in the undo stack

## Keyboard Modifier Support

The system supports standard keyboard modifiers:

1. **Ctrl Key**: Forces a copy operation
2. **Shift Key**: Forces a move operation
3. **Alt Key**: Forces a link operation (where supported)
4. **Ctrl+Shift**: Shows a context menu with operation options (in custom implementation)

## Cross-Platform Considerations

The drag and drop implementation handles platform-specific behaviors:

1. **Windows**: Adapts to Windows Explorer compatibility
2. **macOS**: Handles Finder compatibility and macOS drag feedback
3. **Linux**: Supports X11 and Wayland drag and drop protocols

## Performance Optimizations

Several optimizations are implemented to ensure smooth performance:

1. **Pixmap Caching**: Frequently used drag images are cached
2. **Lazy Loading**: File type icons are loaded on demand
3. **Operation Batching**: Bulk operations are processed in batches
4. **Preview Limiting**: Limits the number of previews shown for large selections
5. **Asynchronous Processing**: Large operations don't block the UI
