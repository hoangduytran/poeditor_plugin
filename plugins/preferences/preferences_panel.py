"""
Preferences Panel for the POEditor application.

This panel provides configuration and settings management including theme selection,
typography settings, and application preferences.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QCheckBox, QSpinBox, QGroupBox, QScrollArea,
    QFileDialog, QMessageBox, QSlider, QLineEdit, QTabWidget
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont

from lg import logger


class PreferencesPanel(QWidget):
    """
    Application preferences and settings panel.
    
    Features:
    - Theme selection and configuration
    - Typography and font settings
    - Application behavior settings
    - Import/export settings
    - Reset to defaults
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Settings
        self.settings = QSettings('POEditor', 'PluginEditor')
        
        # UI components
        self.tab_widget: Optional[QTabWidget] = None
        
        # Theme settings
        self.theme_combo: Optional[QComboBox] = None
        
        # Typography settings
        self.font_family_combo: Optional[QComboBox] = None
        self.font_size_spin: Optional[QSpinBox] = None
        
        # Application settings
        self.auto_save_cb: Optional[QCheckBox] = None
        self.show_line_numbers_cb: Optional[QCheckBox] = None
        self.word_wrap_cb: Optional[QCheckBox] = None
        
        # Initialize UI
        self.setup_ui()
        self.load_settings()
        
        logger.info("PreferencesPanel initialized")
    
    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Create scroll area for large content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(appearance_tab, "🎨 Appearance")
        
        # Editor tab
        editor_tab = self.create_editor_tab()
        self.tab_widget.addTab(editor_tab, "📝 Editor")
        
        # General tab
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "⚙️ General")
        
        content_layout.addWidget(self.tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("🔄 Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        export_button = QPushButton("📤 Export Settings")
        export_button.clicked.connect(self.export_settings)
        button_layout.addWidget(export_button)
        
        import_button = QPushButton("📥 Import Settings")
        import_button.clicked.connect(self.import_settings)
        button_layout.addWidget(import_button)
        
        button_layout.addStretch()
        content_layout.addLayout(button_layout)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        logger.debug("PreferencesPanel UI setup complete")
    
    def create_appearance_tab(self) -> QWidget:
        """Create the appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Select theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Colorful"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Typography settings
        typography_group = QGroupBox("Typography")
        typography_layout = QVBoxLayout(typography_group)
        
        # Font family
        typography_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Inter", "SF Pro Display", "Segoe UI", "Roboto", 
            "Arial", "Helvetica", "Consolas", "Monaco"
        ])
        self.font_family_combo.currentTextChanged.connect(self.on_font_changed)
        typography_layout.addWidget(self.font_family_combo)
        
        # Font size
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        typography_layout.addLayout(font_size_layout)
        
        layout.addWidget(typography_group)
        
        layout.addStretch()
        return tab
    
    def create_editor_tab(self) -> QWidget:
        """Create the editor settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Editor behavior
        behavior_group = QGroupBox("Editor Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.show_line_numbers_cb = QCheckBox("Show line numbers")
        self.show_line_numbers_cb.toggled.connect(self.on_setting_changed)
        behavior_layout.addWidget(self.show_line_numbers_cb)
        
        self.word_wrap_cb = QCheckBox("Enable word wrap")
        self.word_wrap_cb.toggled.connect(self.on_setting_changed)
        behavior_layout.addWidget(self.word_wrap_cb)
        
        layout.addWidget(behavior_group)
        
        # File handling
        file_group = QGroupBox("File Handling")
        file_layout = QVBoxLayout(file_group)
        
        self.auto_save_cb = QCheckBox("Auto-save files")
        self.auto_save_cb.toggled.connect(self.on_setting_changed)
        file_layout.addWidget(self.auto_save_cb)
        
        layout.addWidget(file_group)
        
        layout.addStretch()
        return tab
    
    def create_general_tab(self) -> QWidget:
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Application settings
        app_group = QGroupBox("Application")
        app_layout = QVBoxLayout(app_group)
        
        # Language (placeholder for future implementation)
        app_layout.addWidget(QLabel("Language:"))
        language_combo = QComboBox()
        language_combo.addItems(["English", "Spanish", "French", "German"])
        language_combo.setEnabled(False)  # Not implemented yet
        app_layout.addWidget(language_combo)
        
        layout.addWidget(app_group)
        
        # Plugin settings
        plugin_group = QGroupBox("Plugins")
        plugin_layout = QVBoxLayout(plugin_group)
        
        plugin_layout.addWidget(QLabel("Plugin management and settings will be available here."))
        
        layout.addWidget(plugin_group)
        
        layout.addStretch()
        return tab
    
    def load_settings(self) -> None:
        """Load settings from QSettings."""
        try:
            # Theme
            theme = self.settings.value('theme/current', 'Dark')
            index = self.theme_combo.findText(theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
            
            # Typography
            font_family = self.settings.value('typography/font_family', 'Inter')
            index = self.font_family_combo.findText(font_family)
            if index >= 0:
                self.font_family_combo.setCurrentIndex(index)
            
            font_size = int(self.settings.value('typography/font_size', 12))
            self.font_size_spin.setValue(font_size)
            
            # Editor settings
            show_line_numbers = self.settings.value('editor/show_line_numbers', True, type=bool)
            self.show_line_numbers_cb.setChecked(show_line_numbers)
            
            word_wrap = self.settings.value('editor/word_wrap', True, type=bool)
            self.word_wrap_cb.setChecked(word_wrap)
            
            auto_save = self.settings.value('general/auto_save', False, type=bool)
            self.auto_save_cb.setChecked(auto_save)
            
            logger.debug("Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self) -> None:
        """Save current settings to QSettings."""
        try:
            # Theme
            self.settings.setValue('theme/current', self.theme_combo.currentText())
            
            # Typography
            self.settings.setValue('typography/font_family', self.font_family_combo.currentText())
            self.settings.setValue('typography/font_size', self.font_size_spin.value())
            
            # Editor settings
            self.settings.setValue('editor/show_line_numbers', self.show_line_numbers_cb.isChecked())
            self.settings.setValue('editor/word_wrap', self.word_wrap_cb.isChecked())
            
            # General settings
            self.settings.setValue('general/auto_save', self.auto_save_cb.isChecked())
            
            # Sync settings
            self.settings.sync()
            
            logger.debug("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        logger.info(f"Theme changed to: {theme_name}")
        self.save_settings()
        # TODO: Apply theme change to application
    
    def on_font_changed(self, font_family: str) -> None:
        """Handle font family change."""
        logger.info(f"Font family changed to: {font_family}")
        self.save_settings()
        # TODO: Apply font change to application
    
    def on_font_size_changed(self, font_size: int) -> None:
        """Handle font size change."""
        logger.info(f"Font size changed to: {font_size}")
        self.save_settings()
        # TODO: Apply font size change to application
    
    def on_setting_changed(self) -> None:
        """Handle general setting change."""
        self.save_settings()
        logger.debug("Settings updated")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, 
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear all settings
                self.settings.clear()
                
                # Reload defaults
                self.load_settings()
                
                logger.info("Settings reset to defaults")
                QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
                
            except Exception as e:
                logger.error(f"Error resetting settings: {e}")
                QMessageBox.warning(self, "Error", f"Failed to reset settings: {e}")
    
    def export_settings(self) -> None:
        """Export settings to a JSON file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Settings",
                str(Path.home() / "poeditor_settings.json"),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Collect all settings
                settings_data = {}
                for key in self.settings.allKeys():
                    settings_data[key] = self.settings.value(key)
                
                # Write to file
                with open(file_path, 'w') as f:
                    json.dump(settings_data, f, indent=2)
                
                logger.info(f"Settings exported to: {file_path}")
                QMessageBox.information(self, "Export Complete", f"Settings exported to:\n{file_path}")
                
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to export settings: {e}")
    
    def import_settings(self) -> None:
        """Import settings from a JSON file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Settings",
                str(Path.home()),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Read settings file
                with open(file_path, 'r') as f:
                    settings_data = json.load(f)
                
                # Apply settings
                for key, value in settings_data.items():
                    self.settings.setValue(key, value)
                
                # Reload UI
                self.load_settings()
                
                logger.info(f"Settings imported from: {file_path}")
                QMessageBox.information(self, "Import Complete", f"Settings imported from:\n{file_path}")
                
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            QMessageBox.warning(self, "Import Error", f"Failed to import settings: {e}")
