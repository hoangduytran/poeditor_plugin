"""
Plugin API for the POEditor application.

This module defines the interface that plugins use to interact with the core application.
It provides methods for registering UI components, commands, and accessing core services.
"""

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal
from lg import logger

if TYPE_CHECKING:
    from core.main_app_window import MainAppWindow


class PluginAPI(QObject):
    """
    API interface for plugins to interact with the core application.
    
    This class provides all the methods that plugins can use to:
    - Add sidebar panels
    - Create and manage tabs
    - Register commands
    - Subscribe to events
    - Access core services
    """
    
    # Signals for event system
    event_emitted = Signal(str, dict)  # event_name, event_data
    
    def __init__(self, main_window: 'MainAppWindow'):
        super().__init__()
        self._main_window = main_window
        self._commands: Dict[str, Callable] = {}
        self._services: Dict[str, Any] = {}
        self._event_subscribers: Dict[str, List[Callable]] = {}
        
        logger.info("PluginAPI initialized")
    
    # Sidebar management
    def add_sidebar_panel(self, panel_id: str, widget: QWidget, icon: QIcon, title: str) -> None:
        """
        Add a panel to the sidebar.
        
        Args:
            panel_id: Unique identifier for the panel
            widget: The widget to display in the panel
            icon: Icon for the panel activity bar
            title: Display title for the panel
        """
        try:
            if self._main_window.sidebar_manager:
                self._main_window.sidebar_manager.add_panel(panel_id, widget, icon, title)
                logger.info(f"Added sidebar panel: {panel_id}")
            else:
                logger.error("Sidebar manager not available")
        except Exception as e:
            logger.error(f"Failed to add sidebar panel {panel_id}: {e}")
            raise
    
    def remove_sidebar_panel(self, panel_id: str) -> bool:
        """
        Remove a panel from the sidebar.
        
        Args:
            panel_id: Identifier of the panel to remove
            
        Returns:
            True if panel was removed successfully
        """
        try:
            if self._main_window.sidebar_manager:
                result = self._main_window.sidebar_manager.remove_panel(panel_id)
                if result:
                    logger.info(f"Removed sidebar panel: {panel_id}")
                else:
                    logger.warning(f"Panel not found: {panel_id}")
                return result
            else:
                logger.error("Sidebar manager not available")
                return False
        except Exception as e:
            logger.error(f"Failed to remove sidebar panel {panel_id}: {e}")
            return False
    
    def show_sidebar_panel(self, panel_id: str) -> None:
        """Show a specific sidebar panel."""
        try:
            if self._main_window.sidebar_manager:
                self._main_window.sidebar_manager.set_active_panel(panel_id)
                logger.info(f"Showed sidebar panel: {panel_id}")
        except Exception as e:
            logger.error(f"Failed to show sidebar panel {panel_id}: {e}")
    
    # Tab management
    def add_tab(self, widget: QWidget, title: str, icon: Optional[QIcon] = None) -> int:
        """
        Add a new tab to the main editor area.
        
        Args:
            widget: The widget to display in the tab
            title: Tab title
            icon: Optional icon for the tab
            
        Returns:
            Index of the created tab
        """
        try:
            if self._main_window.tab_manager:
                index = self._main_window.tab_manager.add_tab(widget, title, icon)
                logger.info(f"Added tab: {title} at index {index}")
                return index
            else:
                logger.error("Tab manager not available")
                return -1
        except Exception as e:
            logger.error(f"Failed to add tab {title}: {e}")
            return -1
    
    def close_tab(self, widget: QWidget) -> bool:
        """
        Close a tab containing the specified widget.
        
        Args:
            widget: The widget whose tab should be closed
            
        Returns:
            True if tab was closed successfully
        """
        try:
            if self._main_window.tab_manager:
                index = self._main_window.tab_manager.find_tab(widget)
                if index >= 0:
                    result = self._main_window.tab_manager.close_tab(index)
                    if result:
                        logger.info(f"Closed tab at index {index}")
                    return result
                else:
                    logger.warning("Tab widget not found")
                    return False
            else:
                logger.error("Tab manager not available")
                return False
        except Exception as e:
            logger.error(f"Failed to close tab: {e}")
            return False
    
    def get_active_tab(self) -> Optional[QWidget]:
        """Get the currently active tab widget."""
        try:
            if self._main_window.tab_manager:
                return self._main_window.tab_manager.get_active_tab()
            return None
        except Exception as e:
            logger.error(f"Failed to get active tab: {e}")
            return None
    
    def set_tab_modified(self, widget: QWidget, modified: bool) -> None:
        """
        Set the modified state of a tab.
        
        Args:
            widget: The tab widget
            modified: True if tab content is modified
        """
        try:
            if self._main_window.tab_manager:
                index = self._main_window.tab_manager.find_tab(widget)
                if index >= 0:
                    self._main_window.tab_manager.set_tab_modified(index, modified)
        except Exception as e:
            logger.error(f"Failed to set tab modified state: {e}")
    
    # Command system
    def register_command(self, command_id: str, callback: Callable) -> None:
        """
        Register a command that can be executed by other plugins or UI.
        
        Args:
            command_id: Unique identifier for the command
            callback: Function to call when command is executed
        """
        try:
            if command_id in self._commands:
                logger.warning(f"Command {command_id} already registered, overwriting")
            
            self._commands[command_id] = callback
            logger.info(f"Registered command: {command_id}")
        except Exception as e:
            logger.error(f"Failed to register command {command_id}: {e}")
            raise
    
    def execute_command(self, command_id: str, *args, **kwargs) -> Any:
        """
        Execute a registered command.
        
        Args:
            command_id: Identifier of the command to execute
            *args: Positional arguments to pass to the command
            **kwargs: Keyword arguments to pass to the command
            
        Returns:
            Result of the command execution
        """
        try:
            if command_id not in self._commands:
                logger.error(f"Command not found: {command_id}")
                return None
            
            callback = self._commands[command_id]
            result = callback(*args, **kwargs)
            logger.info(f"Executed command: {command_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute command {command_id}: {e}")
            return None
    
    def unregister_command(self, command_id: str) -> bool:
        """
        Unregister a command.
        
        Args:
            command_id: Identifier of the command to unregister
            
        Returns:
            True if command was unregistered successfully
        """
        try:
            if command_id in self._commands:
                del self._commands[command_id]
                logger.info(f"Unregistered command: {command_id}")
                return True
            else:
                logger.warning(f"Command not found: {command_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to unregister command {command_id}: {e}")
            return False
    
    # Event system
    def subscribe_event(self, event_name: str, callback: Callable) -> None:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is emitted
        """
        try:
            if event_name not in self._event_subscribers:
                self._event_subscribers[event_name] = []
            
            self._event_subscribers[event_name].append(callback)
            logger.info(f"Subscribed to event: {event_name}")
        except Exception as e:
            logger.error(f"Failed to subscribe to event {event_name}: {e}")
            raise
    
    def emit_event(self, event_name: str, **event_data) -> None:
        """
        Emit an event to all subscribers.
        
        Args:
            event_name: Name of the event to emit
            **event_data: Data to pass to event subscribers
        """
        try:
            logger.info(f"Emitting event: {event_name}")
            
            # Emit via signal for Qt integration
            self.event_emitted.emit(event_name, event_data)
            
            # Call direct subscribers
            if event_name in self._event_subscribers:
                for callback in self._event_subscribers[event_name]:
                    try:
                        callback(**event_data)
                    except Exception as e:
                        logger.error(f"Error in event subscriber for {event_name}: {e}")
        except Exception as e:
            logger.error(f"Failed to emit event {event_name}: {e}")
    
    def unsubscribe_event(self, event_name: str, callback: Callable) -> bool:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Name of the event
            callback: Callback function to remove
            
        Returns:
            True if callback was removed successfully
        """
        try:
            if event_name in self._event_subscribers:
                if callback in self._event_subscribers[event_name]:
                    self._event_subscribers[event_name].remove(callback)
                    logger.info(f"Unsubscribed from event: {event_name}")
                    return True
            
            logger.warning(f"Callback not found for event: {event_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to unsubscribe from event {event_name}: {e}")
            return False
    
    # Service system
    def register_service(self, service_name: str, service: Any) -> None:
        """
        Register a service that other plugins can use.
        
        Args:
            service_name: Unique name for the service
            service: The service instance
        """
        try:
            if service_name in self._services:
                logger.warning(f"Service {service_name} already registered, overwriting")
            
            self._services[service_name] = service
            logger.info(f"Registered service: {service_name}")
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
            raise
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get a registered service.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The service instance, or None if not found
        """
        try:
            service = self._services.get(service_name)
            if service is None:
                logger.warning(f"Service not found: {service_name}")
            return service
        except Exception as e:
            logger.error(f"Failed to get service {service_name}: {e}")
            return None
    
    def unregister_service(self, service_name: str) -> bool:
        """
        Unregister a service.
        
        Args:
            service_name: Name of the service to unregister
            
        Returns:
            True if service was unregistered successfully
        """
        try:
            if service_name in self._services:
                del self._services[service_name]
                logger.info(f"Unregistered service: {service_name}")
                return True
            else:
                logger.warning(f"Service not found: {service_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to unregister service {service_name}: {e}")
            return False
    
    # Application integration
    def get_main_window(self) -> 'MainAppWindow':
        """Get the main application window."""
        return self._main_window
    
    def show_sidebar(self, visible: bool = True) -> None:
        """Show or hide the sidebar."""
        try:
            self._main_window.show_sidebar(visible)
        except Exception as e:
            logger.error(f"Failed to toggle sidebar: {e}")
    
    def get_commands(self) -> List[str]:
        """Get list of all registered commands."""
        return list(self._commands.keys())
    
    def get_services(self) -> List[str]:
        """Get list of all registered services."""
        return list(self._services.keys())
    
    def get_event_subscribers(self) -> Dict[str, int]:
        """Get count of subscribers for each event."""
        return {event: len(callbacks) for event, callbacks in self._event_subscribers.items()}
    
    def get_icon_manager(self):
        """
        Get the application's icon manager.
        
        Returns:
            IconManager instance for accessing application icons
        """
        try:
            from services.icon_manager import icon_manager
            return icon_manager
        except Exception as e:
            logger.error(f"Failed to get icon manager: {e}")
            return None
