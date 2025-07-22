"""
Account panel for the PySide POEditor plugin.

This module contains the Account panel implementation.
"""

from lg import logger
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QGroupBox, 
    QFormLayout, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal

from models.activity_models import ACCOUNT_ACTIVITY
from panels.panel_interface import PanelInterface

# Import typography and theme system
from themes.typography import get_typography_manager, FontRole, get_font
from themes.theme_manager import get_theme_manager


class AccountPanel(PanelInterface):
    """
    Account panel for managing user profile and settings.
    """
    
    profile_updated = Signal(dict)
    
    def __init__(self, parent=None, panel_id=None):
        """
        Initialize the account panel.
        
        Args:
            parent: Parent widget
            panel_id: ID of the panel
        """
        super().__init__(parent)
        self.panel_id = panel_id
        self.api = None
        
        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()
        
        # Set up layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create scroll content widget
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(16)
        
        # Add header
        self.header = QLabel("Account")
        # Remove hardcoded styling - will be applied via typography system
        self.scroll_layout.addWidget(self.header)
        
        # Create user profile section
        self._create_profile_section()
        
        # Create account actions section
        self._create_actions_section()
        
        # Create sync settings section
        self._create_sync_section()
        
        # Create API integrations section
        self._create_integrations_section()
        
        # Add spacer at the bottom
        self.scroll_layout.addStretch(1)
        
        # Finish scroll area setup
        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)
        
        # Connect to typography and theme signals
        self._connect_typography_signals()
        
        # Apply initial typography and theme
        self.apply_typography()
        self.apply_theme()
        
        logger.info("AccountPanel initialized with typography integration")
        
        logger.info(f"AccountPanel initialized with ID: {panel_id}")
    
    def _create_profile_section(self):
        """Create the user profile section."""
        profile_group = QGroupBox("User Profile")
        profile_layout = QFormLayout()
        
        # Profile information
        name_label = QLabel("Demo User")
        email_label = QLabel("demo@poeditor.com")
        plan_label = QLabel("Professional")
        
        # Add to form layout
        profile_layout.addRow("Name:", name_label)
        profile_layout.addRow("Email:", email_label)
        profile_layout.addRow("Plan:", plan_label)
        
        # Edit profile button
        edit_btn = QPushButton("Edit Profile")
        profile_layout.addRow("", edit_btn)
        
        profile_group.setLayout(profile_layout)
        self.scroll_layout.addWidget(profile_group)
    
    def _create_actions_section(self):
        """Create the account actions section."""
        actions_group = QGroupBox("Account Actions")
        actions_layout = QVBoxLayout()
        
        # Action buttons
        sign_out_btn = QPushButton("Sign Out")
        change_pwd_btn = QPushButton("Change Password")
        manage_sub_btn = QPushButton("Manage Subscription")
        
        # Add to layout
        actions_layout.addWidget(sign_out_btn)
        actions_layout.addWidget(change_pwd_btn)
        actions_layout.addWidget(manage_sub_btn)
        
        actions_group.setLayout(actions_layout)
        self.scroll_layout.addWidget(actions_group)
    
    def _create_sync_section(self):
        """Create the sync settings section."""
        sync_group = QGroupBox("Synchronization")
        sync_layout = QVBoxLayout()
        
        # Sync settings
        sync_info = QLabel("Sync your settings across devices.")
        last_sync = QLabel("Last synced: Today, 2:30 PM")
        sync_btn = QPushButton("Sync Now")
        
        # Add to layout
        sync_layout.addWidget(sync_info)
        sync_layout.addWidget(last_sync)
        sync_layout.addWidget(sync_btn)
        
        sync_group.setLayout(sync_layout)
        self.scroll_layout.addWidget(sync_group)
    
    def _create_integrations_section(self):
        """Create the API integrations section."""
        integrations_group = QGroupBox("API Integrations")
        integrations_layout = QVBoxLayout()
        
        # Integrations info
        integrations_info = QLabel("Connect external translation services.")
        
        # Integration buttons
        google_btn = QPushButton("Connect Google Translate API")
        deepl_btn = QPushButton("Connect DeepL API")
        microsoft_btn = QPushButton("Connect Microsoft Translator")
        
        # Add to layout
        integrations_layout.addWidget(integrations_info)
        integrations_layout.addWidget(google_btn)
        integrations_layout.addWidget(deepl_btn)
        integrations_layout.addWidget(microsoft_btn)
        
        integrations_group.setLayout(integrations_layout)
        self.scroll_layout.addWidget(integrations_group)
    
    def set_api(self, api):
        """Set the plugin API instance.
        
        Args:
            api: The plugin API instance
        """
        self.api = api
        logger.debug(f"API set for AccountPanel: {self.panel_id}")
        
    def activate(self):
        """Activate the panel."""
        # Refresh data on activation
        logger.info(f"AccountPanel activated: {self.panel_id}")
    
    def deactivate(self):
        """Deactivate the panel."""
        logger.info(f"AccountPanel deactivated: {self.panel_id}")

    def _connect_typography_signals(self):
        """Connect to typography and theme change signals."""
        try:
            # Connect to typography manager signals
            self.typography_manager.fonts_changed.connect(self._on_typography_changed)
            
            # Connect to theme manager signals
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
            
            logger.info("AccountPanel connected to typography and theme change signals")
        except Exception as e:
            logger.error(f"Failed to connect to typography signals in AccountPanel: {e}")
    
    def apply_typography(self):
        """Public method to apply typography to the account panel.
        
        This method is part of the typography integration public API.
        It applies the current typography settings to all components.
        """
        self._apply_typography()
    
    def apply_theme(self):
        """Public method to apply theme styling to the account panel.
        
        This method is part of the theme integration public API.
        It applies the current theme styles to all components.
        """
        self._apply_theme_styling()
    
    def _apply_typography(self):
        """Apply typography to all account panel components."""
        try:
            logger.info("Applying typography to AccountPanel")
            
            # Apply header font (HEADING_1 role)
            self.header.setFont(get_font(FontRole.HEADING_1))
            
            # Apply fonts to all group box titles (HEADING_3 role)
            group_boxes = self.findChildren(QGroupBox)
            for group_box in group_boxes:
                group_box.setFont(get_font(FontRole.HEADING_3))
            
            # Apply fonts to all labels (BODY role for descriptive text, SMALL for form labels)
            labels = self.findChildren(QLabel)
            for label in labels:
                # Skip the main header as it's handled separately
                if label == getattr(self, 'header', None):
                    continue
                    
                # Info/description labels use BODY role
                if any(text in label.text().lower() for text in ['info', 'description', 'connect', 'manage']):
                    label.setFont(get_font(FontRole.BODY))
                else:
                    # Form labels and short text use SMALL role
                    label.setFont(get_font(FontRole.SMALL))
            
            # Apply button font (BUTTON role)
            buttons = self.findChildren(QPushButton)
            for button in buttons:
                button.setFont(get_font(FontRole.BUTTON))
            
            logger.info("Typography applied successfully to AccountPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply typography to AccountPanel: {e}")
    
    def _apply_theme_styling(self):
        """Apply theme-based styling to account panel components."""
        try:
            logger.info("Applying theme styling to AccountPanel")
            
            # Set object names for CSS targeting
            self.header.setObjectName("panel_title")
            
            # Clear any existing stylesheets to ensure global theme takes precedence
            self.header.setStyleSheet("")
            
            # Apply styling to group boxes and buttons
            group_boxes = self.findChildren(QGroupBox)
            for group_box in group_boxes:
                group_box.setObjectName("group_box")
                group_box.setStyleSheet("")
            
            buttons = self.findChildren(QPushButton)
            for button in buttons:
                button.setObjectName("primary_button")
                button.setStyleSheet("")
            
            # Apply info label styling
            labels = self.findChildren(QLabel)
            for label in labels:
                if any(text in label.text().lower() for text in ['info', 'description', 'connect', 'manage']):
                    label.setObjectName("info_label")
                    label.setStyleSheet("")
            
            logger.info("Theme styling applied successfully to AccountPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply theme styling to AccountPanel: {e}")
    
    def _on_typography_changed(self):
        """Handle typography change events."""
        logger.info("AccountPanel typography changed, updating")
        self._apply_typography()
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change events."""
        logger.info(f"AccountPanel theme changed to {theme_name}, updating styling")
        self._apply_theme_styling()
