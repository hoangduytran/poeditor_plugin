"""
Extensions Panel for the POEditor application.

This panel provides plugin management capabilities including viewing installed plugins,
installing new plugins, and managing plugin configurations.
"""

import os
import importlib
import importlib.util
from pathlib import Path
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QTextEdit,
    QSplitter, QMessageBox, QProgressBar, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from lg import logger


class ExtensionsPanel(QWidget):
    """
    Plugin management panel.

    Features:
    - View installed plugins
    - Plugin information display
    - Enable/disable plugins
    - Plugin installation (future)
    - Plugin configuration (future)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core components
        self.plugins_path = Path(__file__).parent.parent
        self.installed_plugins: List[Dict[str, Any]] = []

        # UI components - will be initialized in setup_ui()

        # Initialize UI
        self.setup_ui()
        self.refresh_plugins()

        logger.info("ExtensionsPanel initialized")

    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header with refresh button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📦 Installed Plugins"))
        header_layout.addStretch()

        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Refresh plugin list")
        self.refresh_button.setMaximumWidth(30)
        self.refresh_button.clicked.connect(self.refresh_plugins)
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Plugins list
        plugins_group = QGroupBox("Plugins")
        plugins_layout = QVBoxLayout(plugins_group)

        self.plugins_list = QListWidget()
        self.plugins_list.itemSelectionChanged.connect(self.on_plugin_selected)
        plugins_layout.addWidget(self.plugins_list)

        # Plugin actions
        actions_layout = QHBoxLayout()

        self.enable_button = QPushButton("✅ Enable")
        self.enable_button.clicked.connect(self.enable_plugin)
        self.enable_button.setEnabled(False)
        actions_layout.addWidget(self.enable_button)

        self.disable_button = QPushButton("❌ Disable")
        self.disable_button.clicked.connect(self.disable_plugin)
        self.disable_button.setEnabled(False)
        actions_layout.addWidget(self.disable_button)

        actions_layout.addStretch()
        plugins_layout.addLayout(actions_layout)

        splitter.addWidget(plugins_group)

        # Plugin information
        info_group = QGroupBox("Plugin Information")
        info_layout = QVBoxLayout(info_group)

        self.plugin_info = QTextEdit()
        self.plugin_info.setReadOnly(True)
        self.plugin_info.setMaximumHeight(200)
        info_layout.addWidget(self.plugin_info)

        splitter.addWidget(info_group)

        # Set splitter proportions
        splitter.setSizes([300, 200])
        layout.addWidget(splitter)

        logger.debug("ExtensionsPanel UI setup complete")

    def refresh_plugins(self) -> None:
        """Refresh the list of installed plugins."""
        try:
            logger.info("Refreshing plugin list")

            self.installed_plugins.clear()
            self.plugins_list.clear()

            # Scan plugins directory
            if self.plugins_path.exists():
                for plugin_dir in self.plugins_path.iterdir():
                    if plugin_dir.is_dir() and not plugin_dir.name.startswith('.'):
                        plugin_info = self.get_plugin_info(plugin_dir)
                        if plugin_info:
                            self.installed_plugins.append(plugin_info)
                            self.add_plugin_item(plugin_info)

            logger.info(f"Found {len(self.installed_plugins)} plugins")

        except Exception as e:
            logger.error(f"Error refreshing plugins: {e}")

    def get_plugin_info(self, plugin_dir: Path) -> Optional[Dict[str, Any]]:
        """Get information about a plugin from its directory."""
        try:
            plugin_name = plugin_dir.name

            # Check for required files
            init_file = plugin_dir / "__init__.py"
            plugin_file = plugin_dir / "plugin.py"

            if not (init_file.exists() and plugin_file.exists()):
                return None

            # Try to import plugin module to get metadata
            plugin_info = {
                'name': plugin_name,
                'path': str(plugin_dir),
                'version': 'Unknown',
                'description': 'No description available',
                'enabled': True,  # Default enabled
                'has_init': init_file.exists(),
                'has_plugin': plugin_file.exists(),
                'error': None
            }

            try:
                # Import the module to get metadata
                spec = importlib.util.spec_from_file_location(
                    f"{plugin_name}.__init__",
                    str(init_file)
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Extract metadata - use try/except for safe attribute access
                    try:
                        plugin_info['version'] = module.__version__
                    except AttributeError:
                        plugin_info['version'] = 'Unknown'

                    try:
                        plugin_info['description'] = module.__plugin_description__
                    except AttributeError:
                        plugin_info['description'] = 'No description available'

                    try:
                        plugin_info['plugin_name'] = module.__plugin_name__
                    except AttributeError:
                        plugin_info['plugin_name'] = plugin_name.title()

            except Exception as e:
                plugin_info['error'] = str(e)
                logger.debug(f"Error loading plugin metadata for {plugin_name}: {e}")

            return plugin_info

        except Exception as e:
            logger.error(f"Error getting plugin info for {plugin_dir}: {e}")
            return None

    def add_plugin_item(self, plugin_info: Dict[str, Any]) -> None:
        """Add a plugin item to the list."""
        name = plugin_info.get('plugin_name', plugin_info['name'])
        version = plugin_info.get('version', 'Unknown')
        enabled = plugin_info.get('enabled', True)
        has_error = plugin_info.get('error') is not None

        # Status indicator
        if has_error:
            status_icon = "❌"
            status_text = "Error"
        elif enabled:
            status_icon = "✅"
            status_text = "Enabled"
        else:
            status_icon = "⏸"
            status_text = "Disabled"

        display_text = f"{status_icon} {name} v{version} ({status_text})"

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, plugin_info)

        # Style based on status
        if has_error:
            font = item.font()
            font.setItalic(True)
            item.setFont(font)

        self.plugins_list.addItem(item)

    def on_plugin_selected(self) -> None:
        """Handle plugin selection change."""
        current_item = self.plugins_list.currentItem()

        if current_item:
            plugin_info = current_item.data(Qt.ItemDataRole.UserRole)
            self.display_plugin_info(plugin_info)

            # Update button states
            enabled = plugin_info.get('enabled', True)
            has_error = plugin_info.get('error') is not None

            self.enable_button.setEnabled(not enabled and not has_error)
            self.disable_button.setEnabled(enabled and not has_error)
        else:
            self.plugin_info.clear()
            self.enable_button.setEnabled(False)
            self.disable_button.setEnabled(False)

    def display_plugin_info(self, plugin_info: Dict[str, Any]) -> None:
        """Display detailed plugin information."""
        name = plugin_info.get('plugin_name', plugin_info['name'])
        version = plugin_info.get('version', 'Unknown')
        description = plugin_info.get('description', 'No description available')
        path = plugin_info.get('path', '')
        enabled = plugin_info.get('enabled', True)
        error = plugin_info.get('error')

        info_text = f"""
<h3>{name}</h3>
<p><strong>Version:</strong> {version}</p>
<p><strong>Status:</strong> {'Enabled' if enabled else 'Disabled'}</p>
<p><strong>Path:</strong> {path}</p>
<p><strong>Description:</strong><br>{description}</p>
"""

        if error:
            info_text += f"""
<p><strong>Error:</strong><br>
<span style="color: red;">{error}</span></p>
"""

        # Check for required files
        has_init = plugin_info.get('has_init', False)
        has_plugin = plugin_info.get('has_plugin', False)

        info_text += f"""
<p><strong>Files:</strong><br>
__init__.py: {'✅' if has_init else '❌'}<br>
plugin.py: {'✅' if has_plugin else '❌'}</p>
"""

        self.plugin_info.setHtml(info_text)

    def enable_plugin(self) -> None:
        """Enable the selected plugin."""
        current_item = self.plugins_list.currentItem()
        if current_item:
            plugin_info = current_item.data(Qt.ItemDataRole.UserRole)
            plugin_name = plugin_info.get('plugin_name', plugin_info['name'])

            # TODO: Implement actual plugin enabling logic
            logger.info(f"Enabling plugin: {plugin_name}")

            # Update plugin info
            plugin_info['enabled'] = True

            # Refresh display
            self.refresh_plugins()

            QMessageBox.information(
                self,
                "Plugin Enabled",
                f"Plugin '{plugin_name}' has been enabled.\nRestart may be required."
            )

    def disable_plugin(self) -> None:
        """Disable the selected plugin."""
        current_item = self.plugins_list.currentItem()
        if current_item:
            plugin_info = current_item.data(Qt.ItemDataRole.UserRole)
            plugin_name = plugin_info.get('plugin_name', plugin_info['name'])

            reply = QMessageBox.question(
                self,
                "Disable Plugin",
                f"Are you sure you want to disable plugin '{plugin_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # TODO: Implement actual plugin disabling logic
                logger.info(f"Disabling plugin: {plugin_name}")

                # Update plugin info
                plugin_info['enabled'] = False

                # Refresh display
                self.refresh_plugins()

                QMessageBox.information(
                    self,
                    "Plugin Disabled",
                    f"Plugin '{plugin_name}' has been disabled.\nRestart may be required."
                )

    def install_plugin(self) -> None:
        """Install a new plugin (placeholder for future implementation)."""
        QMessageBox.information(
            self,
            "Feature Coming Soon",
            "Plugin installation from external sources will be available in a future version."
        )
        logger.info("Plugin installation requested (not implemented)")

    def uninstall_plugin(self) -> None:
        """Uninstall a plugin (placeholder for future implementation)."""
        current_item = self.plugins_list.currentItem()
        if current_item:
            plugin_info = current_item.data(Qt.ItemDataRole.UserRole)
            plugin_name = plugin_info.get('plugin_name', plugin_info['name'])

            QMessageBox.information(
                self,
                "Feature Coming Soon",
                f"Plugin uninstallation will be available in a future version.\n\nTo manually remove '{plugin_name}':\n1. Stop the application\n2. Delete the plugin directory: {plugin_info['path']}\n3. Restart the application"
            )
            logger.info(f"Plugin uninstallation requested for: {plugin_name} (not implemented)")
