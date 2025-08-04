"""
Plugin Manager for the POEditor application.

Handles loading, initializing, and managing plugins in a modular way.
"""

import sys
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from lg import logger

if TYPE_CHECKING:
    from core.api import PluginAPI


class PluginInfo:
    """Information about a plugin."""

    def __init__(self, name: str, path: str, metadata: Optional[Dict] = None):
        self.name = name
        self.path = path
        self.metadata = metadata or {}
        self.loaded = False
        self.module = None
        self.error = None

    @property
    def version(self) -> str:
        return self.metadata.get('version', '1.0.0')

    @property
    def description(self) -> str:
        return self.metadata.get('description', 'No description available')

    @property
    def author(self) -> str:
        return self.metadata.get('author', 'Unknown')

    @property
    def requires(self) -> List[str]:
        return self.metadata.get('requires', [])

    @property
    def dependencies(self) -> List[str]:
        return self.metadata.get('dependencies', [])


class PluginManager:
    """
    Manages plugin discovery, loading, and lifecycle.

    Features:
    - Plugin discovery from plugins/ directory
    - Metadata parsing from plugin.json files
    - Controlled plugin loading and unloading
    - Error handling and plugin isolation
    - Dependency resolution
    """

    def __init__(self, plugin_dir: str, api: 'PluginAPI'):
        self.plugin_dir = Path(plugin_dir)
        self.api = api
        self._plugins: Dict[str, PluginInfo] = {}
        self._loaded_plugins: Dict[str, Any] = {}

        logger.info(f"PluginManager initialized with directory: {plugin_dir}")

    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins in the plugin directory.

        Returns:
            List of plugin names found
        """
        try:
            plugins_found = []

            if not self.plugin_dir.exists():
                logger.warning(f"Plugin directory does not exist: {self.plugin_dir}")
                return plugins_found

            # Scan for plugin directories
            for item in self.plugin_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    plugin_info = self._analyze_plugin(item)
                    if plugin_info:
                        self._plugins[plugin_info.name] = plugin_info
                        plugins_found.append(plugin_info.name)
                        logger.info(f"Discovered plugin: {plugin_info.name}")

            logger.info(f"Discovered {len(plugins_found)} plugins")
            return plugins_found

        except Exception as e:
            logger.error(f"Failed to discover plugins: {e}")
            return []

    def _analyze_plugin(self, plugin_path: Path) -> Optional[PluginInfo]:
        """
        Analyze a plugin directory to extract metadata and validate structure.

        Args:
            plugin_path: Path to the plugin directory

        Returns:
            PluginInfo object if valid plugin, None otherwise
        """
        try:
            plugin_name = plugin_path.name

            # Check for __init__.py to confirm it's a Python package
            init_file = plugin_path / '__init__.py'
            if not init_file.exists():
                logger.warning(f"Plugin {plugin_name} missing __init__.py")
                return None

            # Check for plugin.py entry point
            plugin_file = plugin_path / 'plugin.py'
            if not plugin_file.exists():
                logger.warning(f"Plugin {plugin_name} missing plugin.py")
                return None

            # Load metadata if available
            metadata = {}
            metadata_file = plugin_path / 'plugin.json'
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {plugin_name}: {e}")

            # Create plugin info
            plugin_info = PluginInfo(plugin_name, str(plugin_path), metadata)

            # Validate plugin structure
            if not self._validate_plugin(plugin_info):
                return None

            return plugin_info

        except Exception as e:
            logger.error(f"Failed to analyze plugin {plugin_path}: {e}")
            return None

    def _validate_plugin(self, plugin_info: PluginInfo) -> bool:
        """
        Validate plugin structure and requirements.

        Args:
            plugin_info: Plugin information to validate

        Returns:
            True if plugin is valid
        """
        try:
            # Check if plugin.py has required functions
            plugin_file = Path(plugin_info.path) / 'plugin.py'

            # Read the plugin file to check for register function
            with open(plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'def register(' not in content:
                logger.error(f"Plugin {plugin_info.name} missing register() function")
                return False

            # Could add more validation here (dependencies, etc.)

            return True

        except Exception as e:
            logger.error(f"Failed to validate plugin {plugin_info.name}: {e}")
            return False

    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a specific plugin.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            True if plugin was loaded successfully
        """
        try:
            if plugin_name not in self._plugins:
                logger.error(f"Plugin not found: {plugin_name}")
                return False

            plugin_info = self._plugins[plugin_name]

            if plugin_info.loaded:
                logger.warning(f"Plugin already loaded: {plugin_name}")
                return True

            # Check dependencies
            if not self._check_dependencies(plugin_info):
                logger.error(f"Plugin {plugin_name} has unmet dependencies")
                return False

            # Load the plugin module
            plugin_module = self._import_plugin_module(plugin_info)
            if not plugin_module:
                return False

            # Call the register function - direct attribute access instead of hasattr
            try:
                plugin_module.register(self.api)
                plugin_info.loaded = True
                plugin_info.module = plugin_module
                self._loaded_plugins[plugin_name] = plugin_module

                logger.info(f"Successfully loaded plugin: {plugin_name}")
                return True

            except AttributeError:
                logger.error(f"Plugin {plugin_name} missing register() function")
                return False
            except Exception as e:
                logger.error(f"Failed to register plugin {plugin_name}: {e}")
                plugin_info.error = str(e)
                return False

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            if plugin_name in self._plugins:
                self._plugins[plugin_name].error = str(e)
            return False

    def _import_plugin_module(self, plugin_info: PluginInfo):
        """
        Import a plugin module safely.

        Args:
            plugin_info: Information about the plugin to import

        Returns:
            Imported module or None if failed
        """
        try:
            plugin_path = Path(plugin_info.path)
            plugin_file = plugin_path / 'plugin.py'

            # Add plugin directory to sys.path temporarily
            sys.path.insert(0, str(plugin_path.parent))

            try:
                # Import the plugin module
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{plugin_info.name}.plugin",
                    plugin_file
                )

                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
                else:
                    logger.error(f"Failed to create module spec for {plugin_info.name}")
                    return None

            finally:
                # Remove from sys.path
                if str(plugin_path.parent) in sys.path:
                    sys.path.remove(str(plugin_path.parent))

        except Exception as e:
            logger.error(f"Failed to import plugin module {plugin_info.name}: {e}")
            return None

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a specific plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if plugin was unloaded successfully
        """
        try:
            if plugin_name not in self._plugins:
                logger.error(f"Plugin not found: {plugin_name}")
                return False

            plugin_info = self._plugins[plugin_name]

            if not plugin_info.loaded:
                logger.warning(f"Plugin not loaded: {plugin_name}")
                return True

            # Call unregister function if available - direct attribute access instead of hasattr
            plugin_module = self._loaded_plugins.get(plugin_name)
            if plugin_module:
                try:
                    plugin_module.unregister(self.api)
                except AttributeError:
                    # Plugin doesn't have unregister method, continue
                    logger.debug(f"Plugin {plugin_name} has no unregister() function")
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_name} unregister: {e}")

            # Mark as unloaded
            plugin_info.loaded = False
            plugin_info.module = None

            # Remove from loaded plugins
            if plugin_name in self._loaded_plugins:
                del self._loaded_plugins[plugin_name]

            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a specific plugin.

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if plugin was reloaded successfully
        """
        try:
            # Unload first
            if not self.unload_plugin(plugin_name):
                return False

            # Re-analyze the plugin (in case files changed)
            if plugin_name in self._plugins:
                plugin_path = Path(self._plugins[plugin_name].path)
                plugin_info = self._analyze_plugin(plugin_path)
                if plugin_info:
                    self._plugins[plugin_name] = plugin_info

            # Load again
            return self.load_plugin(plugin_name)

        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False

    def load_all_plugins(self) -> Dict[str, bool]:
        """
        Load all discovered plugins.

        Returns:
            Dictionary mapping plugin names to load success status
        """
        results = {}

        # First, load plugins without dependencies
        plugins_to_load = list(self._plugins.keys())
        loaded_plugins = set()

        # Simple dependency resolution (could be improved)
        max_iterations = len(plugins_to_load) + 1
        iteration = 0

        while plugins_to_load and iteration < max_iterations:
            iteration += 1
            plugins_loaded_this_iteration = []

            for plugin_name in plugins_to_load:
                plugin_info = self._plugins[plugin_name]

                # Check if all dependencies are loaded
                dependencies_met = all(
                    dep in loaded_plugins for dep in plugin_info.dependencies
                )

                if dependencies_met:
                    success = self.load_plugin(plugin_name)
                    results[plugin_name] = success
                    if success:
                        loaded_plugins.add(plugin_name)
                        plugins_loaded_this_iteration.append(plugin_name)

            # Remove loaded plugins from the list
            for plugin_name in plugins_loaded_this_iteration:
                plugins_to_load.remove(plugin_name)

            # If no plugins were loaded this iteration, break to avoid infinite loop
            if not plugins_loaded_this_iteration:
                break

        # Mark remaining plugins as failed due to unmet dependencies
        for plugin_name in plugins_to_load:
            results[plugin_name] = False
            logger.error(f"Plugin {plugin_name} not loaded due to unmet dependencies")

        logger.info(f"Loaded {len(loaded_plugins)}/{len(self._plugins)} plugins")
        return results

    def unload_all_plugins(self) -> Dict[str, bool]:
        """
        Unload all loaded plugins.

        Returns:
            Dictionary mapping plugin names to unload success status
        """
        results = {}

        # Unload in reverse order to handle dependencies
        for plugin_name in reversed(list(self._loaded_plugins.keys())):
            results[plugin_name] = self.unload_plugin(plugin_name)

        return results

    def get_loaded_plugins(self) -> List[str]:
        """Get list of currently loaded plugins."""
        return [name for name, info in self._plugins.items() if info.loaded]

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin."""
        return self._plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, PluginInfo]:
        """Get information about all discovered plugins."""
        return self._plugins.copy()

    def _check_dependencies(self, plugin_info: PluginInfo) -> bool:
        """
        Check if plugin dependencies are met.

        Args:
            plugin_info: Plugin to check dependencies for

        Returns:
            True if all dependencies are met
        """
        try:
            for dependency in plugin_info.dependencies:
                if dependency not in self._plugins:
                    logger.error(f"Plugin {plugin_info.name} requires {dependency} which is not available")
                    return False

                if not self._plugins[dependency].loaded:
                    logger.error(f"Plugin {plugin_info.name} requires {dependency} which is not loaded")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to check dependencies for {plugin_info.name}: {e}")
            return False

    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all plugins.

        Returns:
            Dictionary with plugin status information
        """
        status = {}

        for name, info in self._plugins.items():
            status[name] = {
                'loaded': info.loaded,
                'version': info.version,
                'description': info.description,
                'author': info.author,
                'dependencies': info.dependencies,
                'error': info.error
            }

        return status
