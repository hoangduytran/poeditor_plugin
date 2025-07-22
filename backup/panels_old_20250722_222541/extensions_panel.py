"""
Extensions panel for the PySide POEditor plugin.

This module contains the Extensions panel implementation.
"""

from lg import logger
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QToolBar, QPushButton,
    QHBoxLayout, QScrollArea, QLineEdit, QListWidget,
    QListWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from models.activity_models import EXTENSIONS_ACTIVITY
from panels.panel_interface import PanelInterface

# Import typography and theme system
from themes.typography import get_typography_manager, FontRole, get_font
from themes.theme_manager import get_theme_manager


class ExtensionItem(QWidget):
    """Widget for displaying an extension in the list."""
    
    toggled = Signal(str, bool)
    
    def __init__(self, extension_id, name, description, version, is_enabled=True, parent=None):
        """
        Initialize the extension item.
        
        Args:
            extension_id: Unique identifier for the extension
            name: Display name of the extension
            description: Description of the extension
            version: Extension version
            is_enabled: Whether the extension is enabled
            parent: Parent widget
        """
        super().__init__(parent)
        self.extension_id = extension_id
        self.name = name
        self.description = description
        self.version = version
        
        self._setup_ui(is_enabled)
        
    def _setup_ui(self, is_enabled):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Left side - checkbox and info
        left_layout = QVBoxLayout()
        
        # Checkbox with name
        self.checkbox = QCheckBox(self.name)
        self.checkbox.setChecked(is_enabled)
        self.checkbox.toggled.connect(self._on_toggled)
        
        # Description and version
        desc_layout = QHBoxLayout()
        desc_label = QLabel(self.description)
        desc_label.setObjectName("description_label")
        version_label = QLabel(f"v{self.version}")
        version_label.setObjectName("version_label")
        desc_layout.addWidget(desc_label)
        desc_layout.addStretch()
        desc_layout.addWidget(version_label)
        
        left_layout.addWidget(self.checkbox)
        left_layout.addLayout(desc_layout)
        
        # Right side - buttons
        right_layout = QVBoxLayout()
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedWidth(80)
        self.settings_button.setEnabled(is_enabled)
        right_layout.addWidget(self.settings_button)
        right_layout.addStretch()
        
        # Add layouts to main layout
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 0)
        
    def _on_toggled(self, checked):
        """
        Handle checkbox toggle.
        
        Args:
            checked: Whether the checkbox is checked
        """
        self.settings_button.setEnabled(checked)
        self.toggled.emit(self.extension_id, checked)


class ExtensionsPanel(PanelInterface):
    """
    Extensions panel for managing POEditor plugin extensions.
    """
    
    extension_toggled = Signal(str, bool)
    install_extension = Signal(str)
    
    def __init__(self, parent=None, panel_id=None):
        """
        Initialize the extensions panel.
        
        Args:
            parent: The parent widget
            panel_id: The ID of this panel
        """
        super().__init__(parent)
        self.panel_id = panel_id
        self.api = None
        self.extensions = {}
        
        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()
        
        self._setup_ui()
        
        # Connect to typography and theme signals
        self._connect_typography_signals()
        
        # Apply initial typography and theme
        self.apply_typography()
        self.apply_theme()
        
        logger.info("ExtensionsPanel initialized with typography integration")
        
    def _setup_ui(self):
        """Set up the user interface."""
        logger.info("Setting up Extensions panel UI")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title
        self.title_label = QLabel("EXTENSIONS")
        self.title_label.setObjectName("panel_title")
        self.title_label.setAlignment(Qt.AlignLeft)
        # Remove hardcoded styling - will be applied via typography system
        
        # Search and buttons area
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(5, 5, 5, 5)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search extensions...")
        self.search_input.textChanged.connect(self._filter_extensions)
        
        # Buttons
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self._install_extension)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_extensions)
        
        # Add widgets to top layout
        top_layout.addWidget(self.search_input, 1)
        top_layout.addWidget(self.install_button, 0)
        top_layout.addWidget(self.refresh_button, 0)
        
        # Extensions list
        self.extensions_list = QListWidget()
        self.extensions_list.setSpacing(2)
        self.extensions_list.setAlternatingRowColors(True)
        
        # Add widgets to main layout
        layout.addWidget(self.title_label)
        layout.addLayout(top_layout)
        layout.addWidget(self.extensions_list)
        
        # Add some dummy extensions for demonstration
        self._add_dummy_extensions()
        
    def _add_dummy_extensions(self):
        """Add some dummy extensions for demonstration purposes."""
        self.add_extension("spell-check", "Spell Checker", 
                          "Check spelling in translation files", "1.2.0", True)
        self.add_extension("machine-translate", "Machine Translation", 
                          "Integrate with machine translation services", "0.9.5", False)
        self.add_extension("terminology", "Terminology Manager", 
                          "Manage and enforce terminology consistency", "2.1.3", True)
        self.add_extension("export-docx", "DOCX Export", 
                          "Export translations to Microsoft Word format", "1.0.2", True)
        self.add_extension("translation-memory", "Translation Memory", 
                          "Suggest translations from previous work", "3.2.1", True)
        
    def set_api(self, api):
        """
        Set the API for this panel.
        
        Args:
            api: The API instance
        """
        self.api = api
        
    def add_extension(self, extension_id, name, description, version, is_enabled=True):
        """
        Add an extension to the list.
        
        Args:
            extension_id: Unique identifier for the extension
            name: Display name of the extension
            description: Description of the extension
            version: Extension version
            is_enabled: Whether the extension is enabled
        """
        # Store extension info
        self.extensions[extension_id] = {
            "id": extension_id,
            "name": name,
            "description": description,
            "version": version,
            "enabled": is_enabled
        }
        
        # Create item widget
        item_widget = ExtensionItem(extension_id, name, description, version, is_enabled)
        item_widget.toggled.connect(self._extension_toggled)
        
        # Create list item
        item = QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())
        
        # Add to list
        self.extensions_list.addItem(item)
        self.extensions_list.setItemWidget(item, item_widget)
        
        logger.info(f"Added extension: {name} ({extension_id})")
        
    def remove_extension(self, extension_id):
        """
        Remove an extension from the list.
        
        Args:
            extension_id: Unique identifier for the extension
        """
        if extension_id in self.extensions:
            # Find and remove the list item
            for i in range(self.extensions_list.count()):
                item = self.extensions_list.item(i)
                widget = self.extensions_list.itemWidget(item)
                if widget.extension_id == extension_id:
                    self.extensions_list.takeItem(i)
                    break
                    
            # Remove from dictionary
            del self.extensions[extension_id]
            
            logger.info(f"Removed extension: {extension_id}")
            
    def _extension_toggled(self, extension_id, enabled):
        """
        Handle extension being enabled or disabled.
        
        Args:
            extension_id: Unique identifier for the extension
            enabled: Whether the extension is now enabled
        """
        if extension_id in self.extensions:
            self.extensions[extension_id]["enabled"] = enabled
            
            # Emit signal
            self.extension_toggled.emit(extension_id, enabled)
            
            # Notify via API
            if self.api:
                self.api.emit_event("extension_toggled", {
                    "id": extension_id,
                    "enabled": enabled
                })
                
            logger.info(f"Extension {extension_id} {'enabled' if enabled else 'disabled'}")
            
    def _filter_extensions(self, text):
        """
        Filter extensions based on search text.
        
        Args:
            text: The search text
        """
        text = text.lower()
        
        for i in range(self.extensions_list.count()):
            item = self.extensions_list.item(i)
            widget = self.extensions_list.itemWidget(item)
            
            if text in widget.name.lower() or text in widget.description.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def _install_extension(self):
        """Show dialog to install a new extension."""
        from PySide6.QtWidgets import QInputDialog
        
        extension_id, ok = QInputDialog.getText(
            self,
            "Install Extension",
            "Enter extension ID or URL:"
        )
        
        if ok and extension_id:
            # Emit signal
            self.install_extension.emit(extension_id)
            
            # Notify via API
            if self.api:
                self.api.emit_event("install_extension_requested", {
                    "id": extension_id
                })
                
            logger.info(f"Extension installation requested: {extension_id}")
            
    def _refresh_extensions(self):
        """Refresh the extensions list."""
        logger.info("Refreshing extensions list")
        
        # In a real implementation, this would reload extensions from disk
        # For now, just log that it was called
        
        if self.api:
            self.api.emit_event("refresh_extensions", {})

    def _connect_typography_signals(self):
        """Connect to typography and theme change signals."""
        try:
            # Connect to typography manager signals
            self.typography_manager.fonts_changed.connect(self._on_typography_changed)
            
            # Connect to theme manager signals
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
            
            logger.info("ExtensionsPanel connected to typography and theme change signals")
        except Exception as e:
            logger.error(f"Failed to connect to typography signals in ExtensionsPanel: {e}")
    
    def apply_typography(self):
        """Public method to apply typography to the extensions panel.
        
        This method is part of the typography integration public API.
        It applies the current typography settings to all components.
        """
        self._apply_typography()
    
    def apply_theme(self):
        """Public method to apply theme styling to the extensions panel.
        
        This method is part of the theme integration public API.
        It applies the current theme styles to all components.
        """
        self._apply_theme_styling()
    
    def _apply_typography(self):
        """Apply typography to all extensions panel components."""
        try:
            logger.info("Applying typography to ExtensionsPanel")
            
            # Apply title font (PANEL_TITLE role)
            self.title_label.setFont(get_font(FontRole.PANEL_TITLE))
            
            # Apply search input font (BODY role)
            self.search_input.setFont(get_font(FontRole.BODY))
            
            # Apply button fonts (BUTTON role)
            self.install_button.setFont(get_font(FontRole.BUTTON))
            self.refresh_button.setFont(get_font(FontRole.BUTTON))
            
            # Apply list widget font (BODY role for items)
            self.extensions_list.setFont(get_font(FontRole.BODY))
            
            # Apply typography to extension items in the list
            for i in range(self.extensions_list.count()):
                item = self.extensions_list.item(i)
                if item:
                    widget = self.extensions_list.itemWidget(item)
                    if widget and hasattr(widget, 'apply_typography'):
                        widget.apply_typography()
            
            logger.info("Typography applied successfully to ExtensionsPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply typography to ExtensionsPanel: {e}")
    
    def _apply_theme_styling(self):
        """Apply theme-based styling to extensions panel components."""
        try:
            logger.info("Applying theme styling to ExtensionsPanel")
            
            # Set object names for CSS targeting
            self.title_label.setObjectName("panel_title")
            self.search_input.setObjectName("search_input")
            self.install_button.setObjectName("primary_button")
            self.refresh_button.setObjectName("primary_button")
            self.extensions_list.setObjectName("list_widget")
            
            # Clear any existing stylesheets to ensure global theme takes precedence
            self.title_label.setStyleSheet("")
            self.search_input.setStyleSheet("")
            self.install_button.setStyleSheet("")
            self.refresh_button.setStyleSheet("")
            self.extensions_list.setStyleSheet("")
            
            # Apply theme styling to extension items in the list
            for i in range(self.extensions_list.count()):
                item = self.extensions_list.item(i)
                if item:
                    widget = self.extensions_list.itemWidget(item)
                    if widget and hasattr(widget, 'apply_theme'):
                        widget.apply_theme()
            
            logger.info("Theme styling applied successfully to ExtensionsPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply theme styling to ExtensionsPanel: {e}")
    
    def _on_typography_changed(self):
        """Handle typography change events."""
        logger.info("ExtensionsPanel typography changed, updating")
        self._apply_typography()
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change events."""
        logger.info(f"ExtensionsPanel theme changed to {theme_name}, updating styling")
        self._apply_theme_styling()
