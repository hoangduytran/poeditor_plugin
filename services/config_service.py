"""
Configuration Service for the POEditor application.

This service manages application and plugin settings using QSettings.
It provides a centralized way to store and retrieve configuration data
with plugin-specific namespaces.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from PySide6.QtCore import QSettings, QObject, Signal
from lg import logger


class ConfigurationService(QObject):
    """
    Centralized configuration management service.
    
    Features:
    - Plugin-specific configuration namespaces
    - Type-safe configuration access
    - Configuration change notifications
    - Default value support
    - Bulk configuration operations
    """
    
    # Signals
    setting_changed = Signal(str, str, object)  # namespace, key, value
    namespace_cleared = Signal(str)  # namespace
    
    def __init__(self, organization: str = "POEditor", application: str = "PluginEditor"):
        super().__init__()
        self._settings = QSettings(organization, application)
        self._defaults: Dict[str, Dict[str, Any]] = {}
        self._watchers: Dict[str, List[Callable]] = {}
        
        logger.info(f"ConfigurationService initialized for {organization}/{application}")
    
    def _get_key(self, namespace: str, key: str) -> str:
        """Create a namespaced key."""
        if namespace:
            return f"{namespace}/{key}"
        return key
    
    def set_value(self, namespace: str, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            namespace: Configuration namespace (e.g., plugin name)
            key: Configuration key
            value: Value to store
        """
        try:
            full_key = self._get_key(namespace, key)
            old_value = self._settings.value(full_key)
            
            self._settings.setValue(full_key, value)
            self._settings.sync()
            
            # Emit change signal if value actually changed
            if old_value != value:
                self.setting_changed.emit(namespace, key, value)
                
                # Notify watchers
                watch_key = f"{namespace}.{key}"
                if watch_key in self._watchers:
                    for callback in self._watchers[watch_key]:
                        try:
                            callback(namespace, key, value, old_value)
                        except Exception as e:
                            logger.error(f"Error in configuration watcher: {e}")
            
            logger.info(f"Set config {namespace}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set config {namespace}.{key}: {e}")
            raise
    
    def get_value(self, namespace: str, key: str, default: Any = None, value_type: Optional[type] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            namespace: Configuration namespace
            key: Configuration key
            default: Default value if key doesn't exist
            value_type: Expected type for type conversion
            
        Returns:
            Configuration value or default
        """
        try:
            full_key = self._get_key(namespace, key)
            
            # Check for default value
            if default is None and namespace in self._defaults and key in self._defaults[namespace]:
                default = self._defaults[namespace][key]
            
            # Get value with type conversion
            if value_type:
                value = self._settings.value(full_key, default, type=value_type)
            else:
                value = self._settings.value(full_key, default)
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get config {namespace}.{key}: {e}")
            return default
    
    def has_value(self, namespace: str, key: str) -> bool:
        """
        Check if a configuration value exists.
        
        Args:
            namespace: Configuration namespace
            key: Configuration key
            
        Returns:
            True if value exists
        """
        try:
            full_key = self._get_key(namespace, key)
            return self._settings.contains(full_key)
        except Exception as e:
            logger.error(f"Failed to check config {namespace}.{key}: {e}")
            return False
    
    def remove_value(self, namespace: str, key: str) -> bool:
        """
        Remove a configuration value.
        
        Args:
            namespace: Configuration namespace
            key: Configuration key
            
        Returns:
            True if value was removed
        """
        try:
            full_key = self._get_key(namespace, key)
            
            if self._settings.contains(full_key):
                old_value = self._settings.value(full_key)
                self._settings.remove(full_key)
                self._settings.sync()
                
                self.setting_changed.emit(namespace, key, None)
                
                # Notify watchers
                watch_key = f"{namespace}.{key}"
                if watch_key in self._watchers:
                    for callback in self._watchers[watch_key]:
                        try:
                            callback(namespace, key, None, old_value)
                        except Exception as e:
                            logger.error(f"Error in configuration watcher: {e}")
                
                logger.info(f"Removed config {namespace}.{key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove config {namespace}.{key}: {e}")
            return False
    
    def get_namespace_keys(self, namespace: str) -> List[str]:
        """
        Get all keys in a namespace.
        
        Args:
            namespace: Configuration namespace
            
        Returns:
            List of keys in the namespace
        """
        try:
            if namespace:
                self._settings.beginGroup(namespace)
                keys = self._settings.allKeys()
                self._settings.endGroup()
            else:
                # Get all top-level keys
                keys = [key for key in self._settings.allKeys() if '/' not in key]
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to get keys for namespace {namespace}: {e}")
            return []
    
    def get_namespace_values(self, namespace: str) -> Dict[str, Any]:
        """
        Get all values in a namespace.
        
        Args:
            namespace: Configuration namespace
            
        Returns:
            Dictionary of key-value pairs
        """
        try:
            values = {}
            keys = self.get_namespace_keys(namespace)
            
            for key in keys:
                values[key] = self.get_value(namespace, key)
            
            return values
            
        except Exception as e:
            logger.error(f"Failed to get values for namespace {namespace}: {e}")
            return {}
    
    def set_namespace_values(self, namespace: str, values: Dict[str, Any]) -> None:
        """
        Set multiple values in a namespace.
        
        Args:
            namespace: Configuration namespace
            values: Dictionary of key-value pairs to set
        """
        try:
            for key, value in values.items():
                self.set_value(namespace, key, value)
            
            logger.info(f"Set {len(values)} values in namespace {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to set values for namespace {namespace}: {e}")
            raise
    
    def clear_namespace(self, namespace: str) -> None:
        """
        Clear all values in a namespace.
        
        Args:
            namespace: Configuration namespace to clear
        """
        try:
            if namespace:
                self._settings.beginGroup(namespace)
                self._settings.clear()
                self._settings.endGroup()
            else:
                # Clear all top-level keys
                keys = [key for key in self._settings.allKeys() if '/' not in key]
                for key in keys:
                    self._settings.remove(key)
            
            self._settings.sync()
            self.namespace_cleared.emit(namespace)
            
            logger.info(f"Cleared namespace {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace}: {e}")
            raise
    
    def set_defaults(self, namespace: str, defaults: Dict[str, Any]) -> None:
        """
        Set default values for a namespace.
        
        Args:
            namespace: Configuration namespace
            defaults: Dictionary of default key-value pairs
        """
        try:
            if namespace not in self._defaults:
                self._defaults[namespace] = {}
            
            self._defaults[namespace].update(defaults)
            
            logger.info(f"Set {len(defaults)} defaults for namespace {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to set defaults for namespace {namespace}: {e}")
            raise
    
    def get_defaults(self, namespace: str) -> Dict[str, Any]:
        """
        Get default values for a namespace.
        
        Args:
            namespace: Configuration namespace
            
        Returns:
            Dictionary of default values
        """
        return self._defaults.get(namespace, {}).copy()
    
    def reset_to_defaults(self, namespace: str, keys: Optional[List[str]] = None) -> None:
        """
        Reset values to defaults.
        
        Args:
            namespace: Configuration namespace
            keys: Specific keys to reset, or None for all keys
        """
        try:
            if namespace not in self._defaults:
                logger.warning(f"No defaults defined for namespace {namespace}")
                return
            
            defaults = self._defaults[namespace]
            
            if keys is None:
                keys = list(defaults.keys())
            
            for key in keys:
                if key in defaults:
                    self.set_value(namespace, key, defaults[key])
            
            logger.info(f"Reset {len(keys)} values to defaults in namespace {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to reset to defaults for namespace {namespace}: {e}")
            raise
    
    def watch_setting(self, namespace: str, key: str, callback: Callable) -> None:
        """
        Watch for changes to a specific setting.
        
        Args:
            namespace: Configuration namespace
            key: Configuration key
            callback: Function to call when setting changes
                     Signature: callback(namespace, key, new_value, old_value)
        """
        try:
            watch_key = f"{namespace}.{key}"
            
            if watch_key not in self._watchers:
                self._watchers[watch_key] = []
            
            self._watchers[watch_key].append(callback)
            
            logger.info(f"Added watcher for {namespace}.{key}")
            
        except Exception as e:
            logger.error(f"Failed to add watcher for {namespace}.{key}: {e}")
            raise
    
    def unwatch_setting(self, namespace: str, key: str, callback: Callable) -> bool:
        """
        Stop watching a setting.
        
        Args:
            namespace: Configuration namespace
            key: Configuration key
            callback: Callback function to remove
            
        Returns:
            True if watcher was removed
        """
        try:
            watch_key = f"{namespace}.{key}"
            
            if watch_key in self._watchers and callback in self._watchers[watch_key]:
                self._watchers[watch_key].remove(callback)
                
                # Clean up empty watcher lists
                if not self._watchers[watch_key]:
                    del self._watchers[watch_key]
                
                logger.info(f"Removed watcher for {namespace}.{key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove watcher for {namespace}.{key}: {e}")
            return False
    
    def export_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Export all settings from a namespace.
        
        Args:
            namespace: Configuration namespace to export
            
        Returns:
            Dictionary containing all settings
        """
        try:
            return self.get_namespace_values(namespace)
        except Exception as e:
            logger.error(f"Failed to export namespace {namespace}: {e}")
            return {}
    
    def import_namespace(self, namespace: str, settings: Dict[str, Any], 
                        overwrite: bool = True) -> None:
        """
        Import settings into a namespace.
        
        Args:
            namespace: Configuration namespace
            settings: Dictionary of settings to import
            overwrite: Whether to overwrite existing settings
        """
        try:
            if not overwrite:
                # Only import non-existing keys
                existing_keys = set(self.get_namespace_keys(namespace))
                settings = {k: v for k, v in settings.items() if k not in existing_keys}
            
            self.set_namespace_values(namespace, settings)
            
            logger.info(f"Imported {len(settings)} settings into namespace {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to import settings into namespace {namespace}: {e}")
            raise
    
    def sync(self) -> None:
        """Force synchronization of settings to storage."""
        try:
            self._settings.sync()
            logger.info("Configuration synchronized to storage")
        except Exception as e:
            logger.error(f"Failed to sync configuration: {e}")
    
    def get_all_namespaces(self) -> List[str]:
        """
        Get list of all configuration namespaces.
        
        Returns:
            List of namespace names
        """
        try:
            all_keys = self._settings.allKeys()
            namespaces = set()
            
            for key in all_keys:
                if '/' in key:
                    namespace = key.split('/')[0]
                    namespaces.add(namespace)
            
            return sorted(list(namespaces))
            
        except Exception as e:
            logger.error(f"Failed to get namespaces: {e}")
            return []
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about configuration storage.
        
        Returns:
            Dictionary with storage information
        """
        return {
            "organization": self._settings.organizationName(),
            "application": self._settings.applicationName(),
            "format": self._settings.format(),
            "filename": self._settings.fileName(),
            "namespaces": self.get_all_namespaces(),
            "total_keys": len(self._settings.allKeys())
        }
