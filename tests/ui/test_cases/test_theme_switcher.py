#!/usr/bin/env python3
"""
Theme Switcher Test
Tests dynamic theme switching functionality with focus on QPushButtons
"""

import sys
import os
import importlib
from pathlib import Path
import logging

# Configure proper import paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# First import lg to set up logging
from lg import logger

# Import PySide6 components
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QGridLayout, QHBoxLayout, QTabWidget,
    QSplitter, QTreeView, QListWidget, QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon

# Now import our services
try:
    # Try direct import first
    from services.theme_manager import ThemeManager, Theme, theme_manager
except ImportError as e:
    logger.warning(f"Direct import failed: {e}")
    try:
        # Try importing using full path as fallback
        sys.path.append(str(project_root))
        theme_manager_module = importlib.import_module('services.theme_manager')
        ThemeManager = theme_manager_module.ThemeManager
        Theme = theme_manager_module.Theme
        theme_manager = theme_manager_module.theme_manager
        logger.info("Successfully imported services.theme_manager using full path")
    except Exception as e2:
        logger.error(f"Failed to import services.theme_manager: {e2}")
        raise

class ThemeSwitcherTest(QMainWindow):
    """Test application for theme switching and button styling."""
    
    def __init__(self):
        super().__init__()
        logger.debug("[Theme Switcher] Initializing Theme Switcher Test")
        
        self.theme_manager = theme_manager  # Use global theme_manager instance
        logger.debug(f"[Theme Switcher] Theme manager instance: {self.theme_manager}")
        
        # Log initial available themes
        initial_themes = self.theme_manager.get_available_themes()
        logger.debug(f"[Theme Switcher] Initial available themes: {initial_themes}")
        
        # Register custom button test themes
        self.register_button_test_themes()
        
        # Get updated theme list after registration
        self.current_theme_index = 0
        self.themes = self.theme_manager.get_available_themes()
        logger.debug(f"[Theme Switcher] Available themes after registration: {self.themes}")
        
        # Log the current theme before UI initialization
        current_theme = self.theme_manager.get_current_theme()
        if current_theme:
            logger.debug(f"[Theme Switcher] Current theme: {current_theme.name}")
            try:
                logger.debug(f"[Theme Switcher] Current theme dark_mode: {current_theme.dark_mode}")
            except AttributeError:
                logger.debug("[Theme Switcher] Current theme has no dark_mode attribute")
        
        self.initUI()
        
    def register_button_test_themes(self):
        """Register custom button test themes."""
        logger.debug("[Theme Switcher] Starting theme registration")
        
        # First, log existing themes for debugging
        existing_themes = self.theme_manager.get_available_themes()
        logger.debug(f"[Theme Switcher] Existing themes before registration: {existing_themes}")
        
        try:
            # Check if custom themes already exist
            light_path = str(project_root / "themes" / "css" / "button_test_theme.css")
            dark_path = str(project_root / "themes" / "css" / "button_test_dark_theme.css")
            
            # Log CSS file existence for debugging
            logger.debug(f"[Theme Switcher] Light theme CSS path exists: {os.path.exists(light_path)}")
            logger.debug(f"[Theme Switcher] Dark theme CSS path exists: {os.path.exists(dark_path)}")
            
            # Light button test theme
            button_test_theme = Theme(
                name="ButtonTest",
                css_path=light_path,
                dark_mode=False,
                accent_color="#0078d4",
                description="Button Test Theme (Light)"
            )
            reg_result = self.theme_manager.register_theme(button_test_theme)
            logger.debug(f"[Theme Switcher] Light theme registration result: {reg_result}")
            
            # Dark button test theme
            button_test_dark_theme = Theme(
                name="ButtonTestDark",
                css_path=dark_path,
                dark_mode=True,
                accent_color="#0078d4",
                description="Button Test Theme (Dark)"
            )
            reg_result = self.theme_manager.register_theme(button_test_dark_theme)
            logger.debug(f"[Theme Switcher] Dark theme registration result: {reg_result}")
            
            # Check all available themes after registration
            updated_themes = self.theme_manager.get_available_themes()
            logger.debug(f"[Theme Switcher] Available themes after registration: {updated_themes}")
            
            # Force the dark theme to have proper dark mode settings
            # This is a safer way to enforce dark mode without using hasattr/getattr
            try:
                # Get the built-in Dark theme
                dark_theme = self.theme_manager.get_theme("Dark")
                if dark_theme is not None:
                    # Log current state and update
                    logger.info(f"Found Dark theme, dark_mode was: {dark_theme.dark_mode}")
                    logger.debug(f"[Theme Switcher] Dark theme before update - CSS: {dark_theme.css_path}")
                    
                    dark_theme.dark_mode = True  # Force dark mode to be True
                    
                    # Also update the CSS path if it doesn't seem to be working
                    dark_css_path = str(project_root / "themes" / "css" / "dark_theme.css")
                    if os.path.exists(dark_css_path):
                        logger.info(f"Updating Dark theme CSS path to: {dark_css_path}")
                        dark_theme.css_path = dark_css_path
                    
                    # Log the updated state
                    logger.info(f"Updated Dark theme - dark_mode: {dark_theme.dark_mode}, css_path: {dark_theme.css_path}")
                    logger.debug(f"[Theme Switcher] Dark theme object after update: {dark_theme}")
                else:
                    logger.warning("Could not find 'Dark' theme to update")
                    logger.debug("[Theme Switcher] Dark theme lookup returned None")
            except Exception as e:
                logger.error(f"Error updating Dark theme: {e}")
                logger.debug(f"[Theme Switcher] Exception during Dark theme update: {str(e)}")
            
            logger.info("Successfully registered button test themes")
            
        except Exception as e:
            logger.error(f"Failed to register button test themes: {e}")
            logger.debug(f"[Theme Switcher] Exception during theme registration: {str(e)}")
            
        finally:
            # Log final theme state regardless of success/failure
            final_themes = self.theme_manager.get_available_themes()
            logger.debug(f"[Theme Switcher] Final available themes: {final_themes}")
        
    def initUI(self):
        """Set up the UI components."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Theme controls at the top
        controls_layout = QHBoxLayout()
        
        theme_label = QLabel("Current Theme:")
        theme_label.setStyleSheet("font-weight: bold;")
        self.theme_name_label = QLabel(self.get_current_theme_name())
        
        # Add theme status indicator
        self.theme_status_label = QLabel(self.get_theme_status())
        
        switch_theme_btn = QPushButton("Switch Theme")
        switch_theme_btn.clicked.connect(self.switch_theme)
        
        auto_switch_btn = QPushButton("Auto Switch (3s)")
        auto_switch_btn.clicked.connect(self.toggle_auto_switch)
        auto_switch_btn.setCheckable(True)
        self.auto_switch_btn = auto_switch_btn
        
        controls_layout.addWidget(theme_label)
        controls_layout.addWidget(self.theme_name_label)
        controls_layout.addWidget(self.theme_status_label)
        controls_layout.addStretch(1)
        controls_layout.addWidget(switch_theme_btn)
        controls_layout.addWidget(auto_switch_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Create tabs for different UI elements
        tab_widget = QTabWidget()
        
        # Tab 1: Buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        
        # Regular buttons
        buttons_group = QGroupBox("Button Types")
        buttons_grid = QGridLayout(buttons_group)
        
        # Standard button
        std_btn = QPushButton("Standard Button")
        buttons_grid.addWidget(QLabel("Standard:"), 0, 0)
        buttons_grid.addWidget(std_btn, 0, 1)
        
        # Primary button
        primary_btn = QPushButton("Primary Button")
        primary_btn.setProperty("class", "primary")
        buttons_grid.addWidget(QLabel("Primary:"), 1, 0)
        buttons_grid.addWidget(primary_btn, 1, 1)
        
        # Success button
        success_btn = QPushButton("Success Button")
        success_btn.setProperty("class", "success")
        buttons_grid.addWidget(QLabel("Success:"), 2, 0)
        buttons_grid.addWidget(success_btn, 2, 1)
        
        # Warning button
        warning_btn = QPushButton("Warning Button")
        warning_btn.setProperty("class", "warning")
        buttons_grid.addWidget(QLabel("Warning:"), 3, 0)
        buttons_grid.addWidget(warning_btn, 3, 1)
        
        # Danger button
        danger_btn = QPushButton("Danger Button")
        danger_btn.setProperty("class", "danger")
        buttons_grid.addWidget(QLabel("Danger:"), 4, 0)
        buttons_grid.addWidget(danger_btn, 4, 1)
        
        # Info button
        info_btn = QPushButton("Info Button")
        info_btn.setProperty("class", "info")
        buttons_grid.addWidget(QLabel("Info:"), 5, 0)
        buttons_grid.addWidget(info_btn, 5, 1)
        
        buttons_layout.addWidget(buttons_group)
        
        # Button states
        states_group = QGroupBox("Button States")
        states_grid = QGridLayout(states_group)
        
        # Normal button
        normal_btn = QPushButton("Normal Button")
        states_grid.addWidget(QLabel("Normal:"), 0, 0)
        states_grid.addWidget(normal_btn, 0, 1)
        
        # Disabled button
        disabled_btn = QPushButton("Disabled Button")
        disabled_btn.setEnabled(False)
        states_grid.addWidget(QLabel("Disabled:"), 1, 0)
        states_grid.addWidget(disabled_btn, 1, 1)
        
        # Flat button
        flat_btn = QPushButton("Flat Button")
        flat_btn.setFlat(True)
        states_grid.addWidget(QLabel("Flat:"), 2, 0)
        states_grid.addWidget(flat_btn, 2, 1)
        
        # Checked button
        checked_btn = QPushButton("Checked Button")
        checked_btn.setCheckable(True)
        checked_btn.setChecked(True)
        states_grid.addWidget(QLabel("Checked:"), 3, 0)
        states_grid.addWidget(checked_btn, 3, 1)
        
        buttons_layout.addWidget(states_group)
        
        # Tab 2: Other UI Elements
        other_widget = QWidget()
        other_layout = QGridLayout(other_widget)
        
        # Add some sample UI elements
        list_widget = QListWidget()
        list_widget.addItems([f"List Item {i}" for i in range(1, 6)])
        
        tree_view = QTreeView()
        
        radio_group = QGroupBox("Radio Buttons")
        radio_layout = QVBoxLayout(radio_group)
        radio1 = QRadioButton("Option 1")
        radio2 = QRadioButton("Option 2")
        radio3 = QRadioButton("Option 3")
        radio1.setChecked(True)
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        
        other_layout.addWidget(QLabel("List Widget:"), 0, 0)
        other_layout.addWidget(list_widget, 1, 0)
        other_layout.addWidget(QLabel("Tree View:"), 0, 1)
        other_layout.addWidget(tree_view, 1, 1)
        other_layout.addWidget(radio_group, 2, 0, 1, 2)
        
        # Add tabs to tab widget
        tab_widget.addTab(buttons_widget, "Buttons")
        tab_widget.addTab(other_widget, "Other UI Elements")
        
        main_layout.addWidget(tab_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Set window properties
        self.setWindowTitle("Theme Switcher Test")
        self.resize(600, 600)
        
        # Setup auto-switch timer
        self.auto_switch_timer = QTimer()
        self.auto_switch_timer.timeout.connect(self.switch_theme)
        self.auto_switch_timer.setInterval(3000)  # 3 seconds
    
    def get_current_theme_name(self):
        """Get the name of the current theme."""
        current_theme = self.theme_manager.get_current_theme()
        return current_theme.name if current_theme else "Unknown"
        
    def get_theme_status(self):
        """Get the current theme status (including dark mode)."""
        current_theme = self.theme_manager.get_current_theme()
        
        logger.debug(f"[Theme Switcher] Getting theme status for: {current_theme}")
        
        if not current_theme:
            logger.debug("[Theme Switcher] No current theme found")
            return "[No theme]"
            
        try:
            # Attempt to access dark_mode attribute directly
            is_dark = current_theme.dark_mode
            logger.debug(f"[Theme Switcher] Theme status: {current_theme.name}, Dark mode: {is_dark}")
            
            # Get CSS file name for additional debugging
            css_filename = os.path.basename(current_theme.css_path) if hasattr(current_theme, 'css_path') else "unknown"
            logger.debug(f"[Theme Switcher] CSS file: {css_filename}")
            
            # Return a more informative status
            mode_text = 'Dark' if is_dark else 'Light'
            return f"[{mode_text} mode | {css_filename}]"
            
        except AttributeError:
            logger.debug("[Theme Switcher] Failed to access dark_mode attribute")
            return "[Unknown mode]"
    
    def switch_theme(self):
        """Switch to the next theme in the list."""
        if not self.themes:
            return
            
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        next_theme = self.themes[self.current_theme_index]
        
        logger.debug(f"[Theme Switcher] Starting theme switch to: {next_theme}")
        logger.info(f"Switching to theme: {next_theme}")
        
        # Before switch - log current state
        old_theme = self.theme_manager.get_current_theme()
        if old_theme:
            logger.debug(f"[Theme Switcher] Before switch - Theme: {old_theme.name}, CSS: {old_theme.css_path}")
            try:
                logger.debug(f"[Theme Switcher] Before switch - Dark mode: {old_theme.dark_mode}")
            except AttributeError:
                logger.debug("[Theme Switcher] Before switch - Dark mode attribute missing")
        
        # Attempt to switch theme
        if self.theme_manager.set_theme(next_theme):
            self.theme_name_label.setText(next_theme)
            logger.info(f"Theme switched to: {next_theme}")
            
            # Update the theme status display
            self.theme_status_label.setText(self.get_theme_status())
            
            # Update the UI to reflect the new theme's darkness
            current_theme = self.theme_manager.get_current_theme()
            logger.debug(f"[Theme Switcher] After switch - Got theme: {current_theme}")
            
            # Check if current theme exists and apply appropriate styling
            if current_theme is not None:
                # Log theme details for debugging
                logger.debug(f"[Theme Switcher] Theme details - Name: {current_theme.name}, CSS: {current_theme.css_path}")
                
                try:
                    # Access dark_mode directly - if attribute doesn't exist, it will raise AttributeError
                    is_dark_mode = current_theme.dark_mode
                    logger.info(f"Theme {next_theme} dark mode: {is_dark_mode}")
                    logger.debug(f"[Theme Switcher] Dark mode value: {is_dark_mode}, Type: {type(is_dark_mode)}")
                    
                    if is_dark_mode:
                        # For dark themes, apply additional styling to ensure it's visible
                        self.setStyleSheet("color: #ffffff; background-color: #2d2d2d;")
                        logger.debug("[Theme Switcher] Applied dark mode override styles")
                    else:
                        # For light themes, clear the additional styling
                        self.setStyleSheet("")
                        logger.debug("[Theme Switcher] Cleared override styles (light mode)")
                except AttributeError:
                    # If dark_mode attribute doesn't exist, default to light theme
                    logger.warning(f"Theme {next_theme} has no dark_mode attribute, defaulting to light theme")
                    self.setStyleSheet("")
                    logger.debug("[Theme Switcher] Dark mode attribute missing, defaulted to light")
        else:
            logger.error(f"Failed to switch to theme: {next_theme}")
            logger.debug(f"[Theme Switcher] Theme switch operation failed for: {next_theme}")
    
    def toggle_auto_switch(self, checked):
        """Toggle automatic theme switching."""
        if checked:
            logger.info("Starting automatic theme switching")
            self.auto_switch_timer.start()
        else:
            logger.info("Stopping automatic theme switching")
            self.auto_switch_timer.stop()


def run_test():
    """Run the theme switcher test application."""
    app = QApplication.instance() or QApplication([])

    # Import resources to register Qt resource system
    import resources_rc

    test_window = ThemeSwitcherTest()
    test_window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_test())
