"""
Account Panel for the POEditor application.

This panel provides user account management, authentication, and profile settings.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QGroupBox, QStackedWidget, QFormLayout,
    QMessageBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QFont, QPixmap

from lg import logger


class AccountPanel(QWidget):
    """
    User account management panel.
    
    Features:
    - User authentication (login/logout)
    - Profile management
    - Account settings
    - Session management
    - User preferences
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Core components
        self.settings = QSettings('POEditor', 'PluginEditor')
        self.current_user: Optional[Dict[str, Any]] = None
        self.is_logged_in = False
        
        # UI components
        self.stacked_widget: Optional[QStackedWidget] = None
        self.login_widget: Optional[QWidget] = None
        self.profile_widget: Optional[QWidget] = None
        
        # Login form components
        self.username_input: Optional[QLineEdit] = None
        self.password_input: Optional[QLineEdit] = None
        self.remember_me_cb: Optional[QCheckBox] = None
        self.login_button: Optional[QPushButton] = None
        
        # Profile components
        self.profile_info: Optional[QTextEdit] = None
        self.logout_button: Optional[QPushButton] = None
        
        # Initialize UI
        self.setup_ui()
        self.check_saved_session()
        
        logger.info("AccountPanel initialized")
    
    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create login and profile widgets
        self.login_widget = self.create_login_widget()
        self.profile_widget = self.create_profile_widget()
        
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.profile_widget)
        
        layout.addWidget(self.stacked_widget)
        
        # Show appropriate view
        self.update_view()
        
        logger.debug("AccountPanel UI setup complete")
    
    def create_login_widget(self) -> QWidget:
        """Create the login form widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("👤 Account Login")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Login form
        form_group = QGroupBox("Sign In")
        form_layout = QFormLayout(form_group)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username or email")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.perform_login)
        form_layout.addRow("Password:", self.password_input)
        
        self.remember_me_cb = QCheckBox("Remember me")
        form_layout.addRow("", self.remember_me_cb)
        
        layout.addWidget(form_group)
        
        # Login button
        self.login_button = QPushButton("🔐 Sign In")
        self.login_button.clicked.connect(self.perform_login)
        layout.addWidget(self.login_button)
        
        # Offline mode info
        offline_info = QLabel(
            "💡 <i>Currently in offline mode.<br>"
            "Login functionality will be available when<br>"
            "connected to POEditor services.</i>"
        )
        offline_info.setWordWrap(True)
        offline_info.setStyleSheet("color: gray; font-size: 11px; margin: 20px 0;")
        offline_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(offline_info)
        
        layout.addStretch()
        return widget
    
    def create_profile_widget(self) -> QWidget:
        """Create the user profile widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area for profile content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Profile content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Profile header
        header_label = QLabel("👤 User Profile")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header_label)
        
        # Profile information
        profile_group = QGroupBox("Profile Information")
        profile_layout = QVBoxLayout(profile_group)
        
        self.profile_info = QTextEdit()
        self.profile_info.setReadOnly(True)
        self.profile_info.setMaximumHeight(200)
        profile_layout.addWidget(self.profile_info)
        
        content_layout.addWidget(profile_group)
        
        # Account actions
        actions_group = QGroupBox("Account Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Profile settings button
        profile_settings_button = QPushButton("⚙️ Profile Settings")
        profile_settings_button.clicked.connect(self.show_profile_settings)
        actions_layout.addWidget(profile_settings_button)
        
        # Change password button
        change_password_button = QPushButton("🔑 Change Password")
        change_password_button.clicked.connect(self.show_change_password)
        actions_layout.addWidget(change_password_button)
        
        # Logout button
        self.logout_button = QPushButton("🚪 Sign Out")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setStyleSheet("QPushButton { background-color: #d73a49; color: white; }")
        actions_layout.addWidget(self.logout_button)
        
        content_layout.addWidget(actions_group)
        
        # Usage statistics (placeholder)
        stats_group = QGroupBox("Usage Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        stats_info = QLabel(
            "📊 Session statistics and usage data<br>"
            "will be displayed here when available."
        )
        stats_info.setStyleSheet("color: gray; font-style: italic;")
        stats_layout.addWidget(stats_info)
        
        content_layout.addWidget(stats_group)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        return widget
    
    def check_saved_session(self) -> None:
        """Check for saved user session."""
        try:
            # Check if remember me is enabled and we have saved credentials
            remember_me = self.settings.value('account/remember_me', False, type=bool)
            saved_username = self.settings.value('account/username', '')
            
            if remember_me and saved_username:
                # Simulate login with saved credentials
                self.current_user = {
                    'username': saved_username,
                    'email': f"{saved_username}@example.com",
                    'display_name': saved_username.title(),
                    'login_time': 'Restored from saved session',
                    'session_type': 'Offline'
                }
                self.is_logged_in = True
                self.update_profile_display()
                logger.info(f"Restored session for user: {saved_username}")
            
        except Exception as e:
            logger.error(f"Error checking saved session: {e}")
    
    def perform_login(self) -> None:
        """Perform user login."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return
        
        try:
            # Simulate login process (replace with actual authentication)
            logger.info(f"Attempting login for user: {username}")
            
            # For demonstration, accept any non-empty credentials
            if len(username) >= 3 and len(password) >= 3:
                # Successful login
                self.current_user = {
                    'username': username,
                    'email': f"{username}@example.com",
                    'display_name': username.title(),
                    'login_time': QTimer().currentTime().toString(),
                    'session_type': 'Demo/Offline'
                }
                self.is_logged_in = True
                
                # Save session if remember me is checked
                if self.remember_me_cb.isChecked():
                    self.settings.setValue('account/remember_me', True)
                    self.settings.setValue('account/username', username)
                else:
                    self.settings.setValue('account/remember_me', False)
                    self.settings.remove('account/username')
                
                self.update_profile_display()
                self.update_view()
                
                QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
                logger.info(f"User logged in successfully: {username}")
                
            else:
                # Login failed
                QMessageBox.warning(
                    self, 
                    "Login Failed", 
                    "Invalid credentials. Please check your username and password.\n\n"
                    "Demo: Use any username and password with at least 3 characters."
                )
                logger.warning(f"Login failed for user: {username}")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            QMessageBox.critical(self, "Login Error", f"An error occurred during login: {e}")
    
    def logout(self) -> None:
        """Perform user logout."""
        try:
            if self.is_logged_in and self.current_user:
                username = self.current_user.get('username', 'Unknown')
                
                # Clear session
                self.current_user = None
                self.is_logged_in = False
                
                # Clear saved session if not remembering
                if not self.settings.value('account/remember_me', False, type=bool):
                    self.settings.remove('account/username')
                
                # Clear form
                self.username_input.clear()
                self.password_input.clear()
                self.remember_me_cb.setChecked(False)
                
                self.update_view()
                
                QMessageBox.information(self, "Logged Out", f"Goodbye, {username}!")
                logger.info(f"User logged out: {username}")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def update_view(self) -> None:
        """Update the view based on login status."""
        if self.is_logged_in:
            self.stacked_widget.setCurrentWidget(self.profile_widget)
        else:
            self.stacked_widget.setCurrentWidget(self.login_widget)
    
    def update_profile_display(self) -> None:
        """Update the profile information display."""
        if self.current_user:
            profile_html = f"""
            <h3>👤 {self.current_user.get('display_name', 'Unknown User')}</h3>
            <p><strong>Username:</strong> {self.current_user.get('username', 'N/A')}</p>
            <p><strong>Email:</strong> {self.current_user.get('email', 'N/A')}</p>
            <p><strong>Login Time:</strong> {self.current_user.get('login_time', 'N/A')}</p>
            <p><strong>Session Type:</strong> {self.current_user.get('session_type', 'N/A')}</p>
            
            <hr>
            <p><em>Account features are currently in demo mode.</em></p>
            """
            self.profile_info.setHtml(profile_html)
    
    def show_profile_settings(self) -> None:
        """Show profile settings dialog."""
        QMessageBox.information(
            self,
            "Profile Settings",
            "Profile settings dialog will be available in a future version.\n\n"
            "This will include:\n"
            "• Personal information editing\n"
            "• Notification preferences\n"
            "• Privacy settings\n"
            "• Account synchronization options"
        )
        logger.info("Profile settings requested (not implemented)")
    
    def show_change_password(self) -> None:
        """Show change password dialog."""
        QMessageBox.information(
            self,
            "Change Password",
            "Password change functionality will be available in a future version.\n\n"
            "This will include:\n"
            "• Current password verification\n"
            "• New password strength validation\n"
            "• Secure password update process"
        )
        logger.info("Change password requested (not implemented)")
    
    # Public API methods for commands
    def show_login(self) -> None:
        """Show the login form."""
        if not self.is_logged_in:
            self.stacked_widget.setCurrentWidget(self.login_widget)
            self.username_input.setFocus()
    
    def show_profile(self) -> None:
        """Show the user profile."""
        if self.is_logged_in:
            self.stacked_widget.setCurrentWidget(self.profile_widget)
        else:
            self.show_login()
