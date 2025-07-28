"""
Keyboard Shortcut Service for POEditor Application.

Manages keyboard shortcuts throughout the application, including registration,
handling, and configuration.
"""

from typing import Dict, Callable, Any, List, Optional, Union
from PySide6.QtCore import QObject, Signal, Qt, QSettings
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from lg import logger

class ShortcutAction:
    """Represents a keyboard shortcut action in the application."""
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        default_sequence: str, 
        callback: Callable[[], None],
        category: str = "General",
        context_sensitive: bool = False,
        description: str = ""
    ):
        """
        Initialize a keyboard shortcut action.
        
        Args:
            id: Unique identifier for the shortcut
            name: Display name for the shortcut
            default_sequence: Default key sequence (e.g., "Ctrl+C")
            callback: Function to call when the shortcut is triggered
            category: Category for grouping shortcuts in the UI
            context_sensitive: Whether the shortcut is context-sensitive
            description: Detailed description of the shortcut action
        """
        self.id = id
        self.name = name
        self.default_sequence = default_sequence
        self.callback = callback
        self.category = category
        self.context_sensitive = context_sensitive
        self.description = description
        self.active_shortcut: Optional[QShortcut] = None  # Will hold the QShortcut instance when activated


class KeyboardShortcutService(QObject):
    """
    Service to manage keyboard shortcuts throughout the application.
    
    Provides functionality to register, handle, and configure keyboard shortcuts.
    """
    
    shortcut_triggered = Signal(str)  # Emitted when a shortcut is triggered, with shortcut ID
    shortcuts_changed = Signal()      # Emitted when shortcuts configuration changes
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyboardShortcutService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Prevent double initialization for QObject
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        super().__init__()  # Initialize QObject
        self._initialized = True
        
        self.actions: Dict[str, ShortcutAction] = {}
        self.custom_sequences: Dict[str, str] = {}
        self.context_maps: Dict[str, List[str]] = {}  # Maps context names to shortcut IDs
        self.active_context: Optional[str] = None
        
        # Load custom key sequences from settings
        self._load_custom_sequences()
        
    def register_shortcut(
        self, 
        id: str, 
        name: str, 
        default_sequence: str, 
        callback: Callable[[], None],
        category: str = "General",
        context: Optional[str] = None,
        context_sensitive: bool = False,
        description: str = ""
    ) -> ShortcutAction:
        """
        Register a new keyboard shortcut.
        
        Args:
            id: Unique identifier for the shortcut
            name: Display name for the shortcut
            default_sequence: Default key sequence (e.g., "Ctrl+C")
            callback: Function to call when the shortcut is triggered
            category: Category for grouping shortcuts in the UI
            context: Context in which this shortcut is applicable
            context_sensitive: Whether the shortcut is context-sensitive
            description: Detailed description of the shortcut action
            
        Returns:
            ShortcutAction: The created shortcut action
        """
        action = ShortcutAction(
            id=id,
            name=name,
            default_sequence=default_sequence,
            callback=callback,
            category=category,
            context_sensitive=context_sensitive,
            description=description
        )
        
        self.actions[id] = action
        
        # Add to context map if specified
        if context:
            if context not in self.context_maps:
                self.context_maps[context] = []
            self.context_maps[context].append(id)
        
        logger.debug(f"Registered shortcut: {id} ({default_sequence})")
        return action
    
    def activate_shortcut(self, id: str, parent: QWidget) -> bool:
        """
        Activate a registered shortcut for a specific widget.
        
        Args:
            id: Shortcut identifier
            parent: Parent widget for the shortcut
            
        Returns:
            bool: True if activation was successful, False otherwise
        """
        if id not in self.actions:
            logger.warning(f"Cannot activate unknown shortcut: {id}")
            return False
        
        action = self.actions[id]
        
        # Determine the sequence to use (custom or default)
        sequence = self.custom_sequences.get(id, action.default_sequence)
        
        # Create the shortcut
        try:
            key_seq = QKeySequence(sequence)
            shortcut = QShortcut(key_seq, parent)
            shortcut.activated.connect(self._create_shortcut_handler(action))
            
            # Store the active shortcut
            action.active_shortcut = shortcut
            
            logger.debug(f"Activated shortcut: {id} ({sequence})")
            return True
        except Exception as e:
            logger.error(f"Error activating shortcut {id} ({sequence}): {e}")
            return False
    
    def _create_shortcut_handler(self, action: ShortcutAction) -> Callable[[], None]:
        """Create a handler function for a shortcut that calls the callback and emits a signal."""
        def handler():
            logger.debug(f"Shortcut triggered: {action.id}")
            try:
                action.callback()
                self.shortcut_triggered.emit(action.id)
            except Exception as e:
                logger.error(f"Error in shortcut handler for {action.id}: {e}")
        return handler
    
    def set_active_context(self, context: str) -> None:
        """
        Set the active context for context-sensitive shortcuts.
        
        Args:
            context: The context name to activate
        """
        self.active_context = context
        logger.debug(f"Set active shortcut context: {context}")
    
    def get_shortcut_sequence(self, id: str) -> str:
        """
        Get the current key sequence for a shortcut.
        
        Args:
            id: Shortcut identifier
            
        Returns:
            str: The key sequence (custom if set, otherwise default)
        """
        if id not in self.actions:
            return ""
        
        return self.custom_sequences.get(id, self.actions[id].default_sequence)
    
    def set_custom_shortcut(self, id: str, sequence: str) -> bool:
        """
        Set a custom key sequence for a shortcut.
        
        Args:
            id: Shortcut identifier
            sequence: New key sequence
            
        Returns:
            bool: True if successful, False otherwise
        """
        if id not in self.actions:
            logger.warning(f"Cannot customize unknown shortcut: {id}")
            return False
        
        # Store the custom sequence
        self.custom_sequences[id] = sequence
        
        # Update active shortcut if it exists
        action = self.actions[id]
        if action.active_shortcut:
            try:
                action.active_shortcut.setKey(QKeySequence(sequence))
            except Exception as e:
                logger.error(f"Error updating shortcut {id} to {sequence}: {e}")
                return False
        
        # Save to settings
        self._save_custom_sequences()
        
        # Notify about the change
        self.shortcuts_changed.emit()
        
        logger.debug(f"Set custom shortcut: {id} = {sequence}")
        return True
    
    def reset_shortcut(self, id: str) -> bool:
        """
        Reset a shortcut to its default key sequence.
        
        Args:
            id: Shortcut identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        if id not in self.actions:
            return False
        
        # Remove from custom sequences
        if id in self.custom_sequences:
            del self.custom_sequences[id]
        
        # Update active shortcut if it exists
        action = self.actions[id]
        if action.active_shortcut:
            action.active_shortcut.setKey(QKeySequence(action.default_sequence))
        
        # Save to settings
        self._save_custom_sequences()
        
        # Notify about the change
        self.shortcuts_changed.emit()
        
        return True
    
    def get_shortcuts_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all shortcuts organized by category.
        
        Returns:
            Dict[str, List[Dict]]: Dictionary mapping categories to lists of shortcut data
        """
        result = {}
        
        for id, action in self.actions.items():
            category = action.category
            if category not in result:
                result[category] = []
            
            # Get current sequence (custom or default)
            sequence = self.custom_sequences.get(id, action.default_sequence)
            
            result[category].append({
                "id": id,
                "name": action.name,
                "sequence": sequence,
                "default_sequence": action.default_sequence,
                "description": action.description,
                "context_sensitive": action.context_sensitive
            })
        
        return result
    
    def _load_custom_sequences(self) -> None:
        """Load custom key sequences from settings."""
        settings = QSettings()
        settings.beginGroup("Shortcuts")
        
        self.custom_sequences = {}
        for key in settings.allKeys():
            self.custom_sequences[key] = settings.value(key)
        
        settings.endGroup()
        logger.debug(f"Loaded {len(self.custom_sequences)} custom shortcuts from settings")
    
    def _save_custom_sequences(self) -> None:
        """Save custom key sequences to settings."""
        settings = QSettings()
        settings.beginGroup("Shortcuts")
        
        # Clear existing shortcuts
        settings.remove("")
        
        # Save custom shortcuts
        for id, sequence in self.custom_sequences.items():
            settings.setValue(id, sequence)
        
        settings.endGroup()
        logger.debug(f"Saved {len(self.custom_sequences)} custom shortcuts to settings")
    
    @classmethod
    def get_instance(cls) -> 'KeyboardShortcutService':
        """Get the singleton instance of the KeyboardShortcutService."""
        return cls()


# Create singleton instance for easy import
keyboard_shortcut_service = KeyboardShortcutService.get_instance()
