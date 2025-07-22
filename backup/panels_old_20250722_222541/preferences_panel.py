"""
Preferences panel for the PySide POEditor plugin.

This module contains the Preferences panel implementation.
"""

from lg import logger
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QTabWidget, QWidget,
    QFormLayout, QComboBox, QCheckBox, QPushButton,
    QSpinBox, QLineEdit, QColorDialog, QHBoxLayout,
    QScrollArea, QGroupBox, QMessageBox, QSlider
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from panels.panel_interface import PanelInterface
from services.theme_manager import theme_manager
# from widgets.theme_editor import ThemeEditor  # TODO: Create theme_editor widget

# Import typography system
from themes.typography import get_typography_manager, FontRole, get_font
from themes.theme_manager import get_theme_manager


class ColorButton(QPushButton):
    """Custom button for selecting colors."""
    
    color_changed = Signal(QColor)
    
    def __init__(self, color=None, parent=None):
        """
        Initialize the color button.
        
        Args:
            color: The initial color (QColor)
            parent: The parent widget
        """
        super().__init__(parent)
        self.color = color or QColor("#3E3E3E")
        self.setFixedSize(30, 20)
        
        # Set initial style
        self._update_style()
        
        # Connect clicked signal
        self.clicked.connect(self._select_color)
        
    def _update_style(self):
        """Update the button style based on the selected color."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 1px solid #888;
            }}
            QPushButton:hover {{
                border: 1px solid #FFF;
            }}
        """)
        
    def _select_color(self):
        """Show color dialog and update color if accepted."""
        color = QColorDialog.getColor(
            self.color, 
            self, 
            "Select Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        
        if color.isValid():
            self.color = color
            self._update_style()
            self.color_changed.emit(color)
            
    def get_color(self):
        """Get the current color."""
        return self.color
        
    def set_color(self, color):
        """Set the current color."""
        if isinstance(color, str):
            color = QColor(color)
        
        self.color = color
        self._update_style()


class PreferencesPanel(PanelInterface):
    """
    Preferences panel for configuring the POEditor plugin.
    """
    
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None, panel_id=None):
        """
        Initialize the preferences panel.
        
        Args:
            parent: The parent widget
            panel_id: The ID of this panel
        """
        super().__init__(parent)
        self.panel_id = panel_id
        self.api = None
        self.settings = {}
        
        # Initialize typography and theme managers
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()
        
        self._setup_ui()
        
        # Apply initial typography and theme
        self.apply_typography()
        self.apply_theme()
        
        # Connect to typography and theme changes
        self._connect_typography_signals()
        
    def _setup_ui(self):
        """Set up the user interface."""
        logger.info("Setting up Preferences panel UI")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title
        self.title_label = QLabel("PREFERENCES")
        self.title_label.setObjectName("panel_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self._create_general_tab(), "General")
        self.tab_widget.addTab(self._create_editor_tab(), "Editor")
        self.tab_widget.addTab(self._create_appearance_tab(), "Appearance")
        self.tab_widget.addTab(self._create_shortcuts_tab(), "Shortcuts")
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self._save_settings)
        
        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        
        # Add buttons to layout
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.reset_button)
        
        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.tab_widget)
        layout.addLayout(buttons_layout)
        
    def _create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create content widget
        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setSpacing(10)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["System Default", "English", "French", "German", "Spanish"])
        form_layout.addRow("Interface Language:", self.language_combo)
        
        # Auto save
        self.autosave_check = QCheckBox("Enable autosave")
        form_layout.addRow("Auto Save:", self.autosave_check)
        
        # Autosave interval
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(5)
        self.autosave_interval.setSuffix(" minutes")
        form_layout.addRow("Autosave Interval:", self.autosave_interval)
        
        # Check for updates
        self.updates_check = QCheckBox("Check for updates on startup")
        form_layout.addRow("Updates:", self.updates_check)
        
        # Default project folder
        self.project_folder = QLineEdit()
        browse_button = QPushButton("Browse...")
        browse_layout = QHBoxLayout()
        browse_layout.addWidget(self.project_folder)
        browse_layout.addWidget(browse_button)
        form_layout.addRow("Default Project Folder:", browse_layout)
        
        # Connect browse button
        browse_button.clicked.connect(self._browse_for_folder)
        
        # Add to scroll area
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
        
    def _create_editor_tab(self):
        """Create the editor settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Editor options group
        editor_group = QGroupBox("Editor Options")
        editor_form = QFormLayout(editor_group)
        
        # Font selection
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Consolas", "Courier New", "DejaVu Sans Mono", "Monaco"])
        editor_form.addRow("Font:", self.font_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        editor_form.addRow("Font Size:", self.font_size)
        
        # Tab size
        self.tab_size = QSpinBox()
        self.tab_size.setRange(2, 8)
        self.tab_size.setValue(4)
        editor_form.addRow("Tab Size:", self.tab_size)
        
        # Use spaces
        self.use_spaces = QCheckBox("Use spaces for indentation")
        self.use_spaces.setChecked(True)
        editor_form.addRow("Indentation:", self.use_spaces)
        
        # Word wrap
        self.word_wrap = QCheckBox("Enable word wrap")
        editor_form.addRow("Word Wrap:", self.word_wrap)
        
        # Auto-completion
        self.auto_complete = QCheckBox("Enable auto-completion")
        self.auto_complete.setChecked(True)
        editor_form.addRow("Auto-completion:", self.auto_complete)
        
        # Add editor group to content
        content_layout.addWidget(editor_group)
        
        # Spellcheck group
        spellcheck_group = QGroupBox("Spell Check")
        spellcheck_form = QFormLayout(spellcheck_group)
        
        # Enable spellcheck
        self.spellcheck = QCheckBox("Enable spell checking")
        spellcheck_form.addRow("Spell Check:", self.spellcheck)
        
        # Spellcheck language
        self.spell_lang_combo = QComboBox()
        self.spell_lang_combo.addItems(["English (US)", "English (UK)", "French", "German", "Spanish"])
        spellcheck_form.addRow("Spell Check Language:", self.spell_lang_combo)
        
        # Add spellcheck group to content
        content_layout.addWidget(spellcheck_group)
        content_layout.addStretch()
        
        # Add to scroll area
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
        
    def _create_appearance_tab(self):
        """Create the appearance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Theme group
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        
        # Populate with available themes
        available_themes = theme_manager.get_available_themes()
        self.theme_combo.addItems(available_themes)
        
        # Set current theme
        current_theme = theme_manager.get_current_theme()
        if current_theme:
            self.theme_combo.setCurrentText(current_theme.name)
        
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        selection_layout.addWidget(self.theme_combo)
        selection_layout.addStretch()
        
        theme_layout.addLayout(selection_layout)
        
        # Theme editor button
        editor_layout = QHBoxLayout()
        self.edit_themes_btn = QPushButton("Edit Themes...")
        self.edit_themes_btn.clicked.connect(self._open_theme_editor)
        editor_layout.addWidget(self.edit_themes_btn)
        editor_layout.addStretch()
        
        theme_layout.addLayout(editor_layout)
        
        # Theme info
        theme_info = QLabel("Note: The sidebar will always use a dark theme regardless of the selected theme.")
        theme_info.setWordWrap(True)
        theme_info.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
        theme_layout.addWidget(theme_info)
        
        content_layout.addWidget(theme_group)
        
        # Typography settings group
        self._create_typography_settings_group(content_layout)

        # Add legacy custom colors group (hidden by default since we have theme system)
        self._create_legacy_colors_group(content_layout)
        
        content_layout.addStretch()
        
        # Add to scroll area
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_typography_settings_group(self, parent_layout):
        """Create typography settings group that integrates with the typography system."""
        typography_group = QGroupBox("Typography Settings")
        typography_form = QFormLayout(typography_group)

        # Initialize typography manager
        self.typography_manager = get_typography_manager()

        # Font family selection
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Inter, Segoe UI, Arial, sans-serif",
            "SF Pro Display, system-ui, sans-serif",
            "Roboto, Arial, sans-serif",
            "Ubuntu, Arial, sans-serif",
            "JetBrains Mono, Consolas, Monaco, monospace"
        ])
        self.font_family_combo.setCurrentText(self.typography_manager.get_base_font_family())
        self.font_family_combo.currentTextChanged.connect(self._update_typography_preview)
        typography_form.addRow("UI Font Family:", self.font_family_combo)

        # Base font size
        self.base_font_size = QSpinBox()
        self.base_font_size.setRange(8, 24)
        self.base_font_size.setValue(self.typography_manager.get_base_font_size())
        self.base_font_size.setSuffix(" px")
        self.base_font_size.valueChanged.connect(self._update_typography_preview)
        typography_form.addRow("Base Font Size:", self.base_font_size)

        # Scale factor (for accessibility)
        self.scale_factor_layout = QHBoxLayout()
        self.scale_factor_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_factor_slider.setRange(50, 200)  # 0.5x to 2.0x
        current_scale = int(self.typography_manager.get_scale_factor() * 100)
        self.scale_factor_slider.setValue(current_scale)

        self.scale_label = QLabel(f"{current_scale/100:.1f}x")
        self.scale_factor_slider.valueChanged.connect(self._on_scale_changed)

        self.scale_factor_layout.addWidget(self.scale_factor_slider)
        self.scale_factor_layout.addWidget(self.scale_label)
        typography_form.addRow("Scale Factor:", self.scale_factor_layout)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        # Create preview labels for different font roles
        self.preview_heading = QLabel("Heading Example")
        self.preview_heading.setFont(get_font(FontRole.HEADING_1))

        self.preview_body = QLabel("This is an example of body text that shows how the font will appear in the application. The quick brown fox jumps over the lazy dog.")
        self.preview_body.setFont(get_font(FontRole.BODY))
        self.preview_body.setWordWrap(True)

        self.preview_button = QPushButton("Button Example")
        self.preview_button.setFont(get_font(FontRole.BUTTON))

        self.preview_small = QLabel("This is smaller text for UI elements")
        self.preview_small.setFont(get_font(FontRole.SMALL))

        self.preview_code = QLabel("function example() { return 'code sample'; }")
        self.preview_code.setFont(get_font(FontRole.CODE))

        # Add previews to layout
        preview_layout.addWidget(self.preview_heading)
        preview_layout.addWidget(self.preview_body)
        preview_layout.addWidget(self.preview_button)
        preview_layout.addWidget(self.preview_small)
        preview_layout.addWidget(self.preview_code)

        # Create live preview toggle
        self.live_preview = QCheckBox("Live Preview")
        self.live_preview.setChecked(True)
        preview_layout.addWidget(self.live_preview)

        # Add preview group to typography form
        typography_form.addRow("", preview_group)

        # Apply button
        self.apply_typography_btn = QPushButton("Apply Typography")
        self.apply_typography_btn.clicked.connect(self._apply_typography_settings)
        typography_form.addRow("", self.apply_typography_btn)

        # Add the group to parent layout
        parent_layout.addWidget(typography_group)

    def _on_scale_changed(self, value):
        """Handle scale factor slider changes."""
        scale = value / 100.0
        self.scale_label.setText(f"{scale:.1f}x")

        if self.live_preview.isChecked():
            self._update_typography_preview()

    def _update_typography_preview(self):
        """Update the typography preview based on current settings."""
        if not self.live_preview.isChecked():
            return

        try:
            # Get current settings from UI
            family = self.font_family_combo.currentText()
            size = self.base_font_size.value()
            scale = self.scale_factor_slider.value() / 100.0

            # Create temporary QFonts for preview
            heading_font = QFont(family.split(',')[0].strip())
            heading_font.setPointSize(int(size * 1.6 * scale))
            heading_font.setBold(True)

            body_font = QFont(family.split(',')[0].strip())
            body_font.setPointSize(int(size * scale))

            button_font = QFont(family.split(',')[0].strip())
            button_font.setPointSize(int(size * 0.9 * scale))
            button_font.setBold(True)

            small_font = QFont(family.split(',')[0].strip())
            small_font.setPointSize(int(size * 0.85 * scale))

            # Code font is special - always use monospace
            code_font = QFont("JetBrains Mono, Consolas, Monaco, monospace".split(',')[0].strip())
            code_font.setPointSize(int(size * 0.95 * scale))

            # Apply preview fonts
            self.preview_heading.setFont(heading_font)
            self.preview_body.setFont(body_font)
            self.preview_button.setFont(button_font)
            self.preview_small.setFont(small_font)
            self.preview_code.setFont(code_font)

        except Exception as e:
            logger.error(f"Failed to update typography preview: {e}")

    def _apply_typography_settings(self):
        """Apply the typography settings to the application."""
        try:
            # Get settings from UI
            family = self.font_family_combo.currentText()
            size = self.base_font_size.value()
            scale = self.scale_factor_slider.value() / 100.0

            # Apply to typography manager
            theme_manager = get_theme_manager()
            theme_manager.customize_font_settings(
                font_family=family,
                font_size=size,
                scale_factor=scale
            )

            # Update the preview to match actual applied settings
            self._update_typography_preview_from_system()

            logger.info(f"Applied typography settings: family={family}, size={size}px, scale={scale}x")

        except Exception as e:
            logger.error(f"Failed to apply typography settings: {e}")
            QMessageBox.warning(
                self,
                "Typography Error",
                f"Failed to apply typography settings: {str(e)}"
            )

    def _update_typography_preview_from_system(self):
        """Update preview with actual fonts from the typography system."""
        self.preview_heading.setFont(get_font(FontRole.HEADING_1))
        self.preview_body.setFont(get_font(FontRole.BODY))
        self.preview_button.setFont(get_font(FontRole.BUTTON))
        self.preview_small.setFont(get_font(FontRole.SMALL))
        self.preview_code.setFont(get_font(FontRole.CODE))

    def _create_legacy_colors_group(self, parent_layout):
        """Create legacy custom colors group for backward compatibility."""
        colors_group = QGroupBox("Legacy Custom Colors (Advanced)")
        colors_group.setCheckable(True)
        colors_group.setChecked(False)  # Collapsed by default
        colors_form = QFormLayout(colors_group)
        
        # Background color
        self.bg_color = ColorButton(QColor("#1E1E1E"))
        colors_form.addRow("Background:", self.bg_color)
        
        # Text color
        self.text_color = ColorButton(QColor("#D4D4D4"))
        colors_form.addRow("Text:", self.text_color)
        
        # Selection color
        self.selection_color = ColorButton(QColor("#264F78"))
        colors_form.addRow("Selection:", self.selection_color)
        
        # Highlight color
        self.highlight_color = ColorButton(QColor("#FFD700"))
        colors_form.addRow("Highlight:", self.highlight_color)
        
        parent_layout.addWidget(colors_group)
        
    def _on_theme_changed(self, theme_name):
        """Handle theme selection change."""
        try:
            logger.info(f"Switching to theme: {theme_name}")
            theme_manager.set_theme(theme_name)
            logger.info(f"Theme switched successfully to: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to switch theme to {theme_name}: {e}")
            # Show error message to user
            QMessageBox.warning(
                self, 
                "Theme Error", 
                f"Failed to switch to theme '{theme_name}': {str(e)}"
            )
            # Revert combobox to current theme
            current_theme = theme_manager.get_current_theme()
            if current_theme:
                self.theme_combo.setCurrentText(current_theme.name)
    
    def _open_theme_editor(self):
        """Open the theme editor dialog."""
        try:
            logger.info("Opening theme editor")
            # TODO: Implement theme editor when widgets.theme_editor is created
            logger.warning("Theme editor not yet implemented")
            
            # editor = ThemeEditor(self)
            # editor.exec()
            
            # Refresh theme list after editing
            current_selection = self.theme_combo.currentText()
            self.theme_combo.clear()
            self.theme_combo.addItems(theme_manager.get_available_themes())
            
            # Try to restore selection or use current theme
            current_theme = theme_manager.get_current_theme()
            if current_selection in theme_manager.get_available_themes():
                self.theme_combo.setCurrentText(current_selection)
            elif current_theme:
                self.theme_combo.setCurrentText(current_theme.name)
                
        except Exception as e:
            logger.error(f"Failed to open theme editor: {e}")
            QMessageBox.critical(
                self, 
                "Theme Editor Error", 
                f"Failed to open theme editor: {str(e)}"
            )
        
    def _create_shortcuts_tab(self):
        """Create the keyboard shortcuts tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Create content widget
        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setSpacing(10)
        
        # Define shortcuts
        shortcuts = [
            ("Open File", "Ctrl+O"),
            ("Save", "Ctrl+S"),
            ("Save As", "Ctrl+Shift+S"),
            ("Find", "Ctrl+F"),
            ("Replace", "Ctrl+H"),
            ("Next Translation", "Ctrl+Down"),
            ("Previous Translation", "Ctrl+Up"),
            ("Toggle Explorer", "Ctrl+Shift+E"),
            ("Toggle Search", "Ctrl+Shift+F")
        ]
        
        # Add shortcut fields
        self.shortcut_fields = {}
        for name, default in shortcuts:
            shortcut_edit = QLineEdit(default)
            shortcut_edit.setReadOnly(True)
            shortcut_edit.mousePressEvent = lambda e, edit=shortcut_edit: self._capture_shortcut(edit)
            form_layout.addRow(name + ":", shortcut_edit)
            self.shortcut_fields[name] = shortcut_edit
            
        # Reset shortcuts button
        reset_shortcuts = QPushButton("Reset All Shortcuts")
        reset_shortcuts.clicked.connect(self._reset_shortcuts)
        form_layout.addRow("", reset_shortcuts)
        
        # Add to scroll area
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
        
    def _browse_for_folder(self):
        """Open dialog to browse for a folder."""
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(
            self, "Select Default Project Folder", self.project_folder.text()
        )
        if folder:
            self.project_folder.setText(folder)
            
    def _capture_shortcut(self, edit):
        """
        Start capturing keyboard shortcuts.
        
        Args:
            edit: The QLineEdit to capture to
        """
        edit.setText("Press shortcut...")
        edit.setFocus()
        # In a real implementation, we would have a key event filter
        # for the actual key combination capture
            
    def _reset_shortcuts(self):
        """Reset all shortcuts to default values."""
        defaults = {
            "Open File": "Ctrl+O",
            "Save": "Ctrl+S",
            "Save As": "Ctrl+Shift+S",
            "Find": "Ctrl+F",
            "Replace": "Ctrl+H",
            "Next Translation": "Ctrl+Down",
            "Previous Translation": "Ctrl+Up",
            "Toggle Explorer": "Ctrl+Shift+E",
            "Toggle Search": "Ctrl+Shift+F"
        }
        
        for name, field in self.shortcut_fields.items():
            field.setText(defaults.get(name, ""))
            
    def _save_settings(self):
        """Save the current settings."""
        # Collect settings
        settings = {
            # General settings
            "language": self.language_combo.currentText(),
            "autosave": self.autosave_check.isChecked(),
            "autosave_interval": self.autosave_interval.value(),
            "check_updates": self.updates_check.isChecked(),
            "project_folder": self.project_folder.text(),
            
            # Editor settings
            "font": self.font_combo.currentText(),
            "font_size": self.font_size.value(),
            "tab_size": self.tab_size.value(),
            "use_spaces": self.use_spaces.isChecked(),
            "word_wrap": self.word_wrap.isChecked(),
            "auto_complete": self.auto_complete.isChecked(),
            "spellcheck": self.spellcheck.isChecked(),
            "spell_language": self.spell_lang_combo.currentText(),
            
            # Appearance settings
            "theme": self.theme_combo.currentText(),
            "bg_color": self.bg_color.get_color().name(),
            "text_color": self.text_color.get_color().name(),
            "selection_color": self.selection_color.get_color().name(),
            "highlight_color": self.highlight_color.get_color().name(),
            
            # Shortcuts
            "shortcuts": {name: field.text() for name, field in self.shortcut_fields.items()}
        }
        
        # Store settings
        self.settings = settings
        
        # Emit signal
        self.settings_changed.emit(settings)
        
        # Notify via API
        if self.api:
            self.api.emit_event("settings_saved", settings)
            
        logger.info("Settings saved")
            
    def _reset_to_defaults(self):
        """Reset all settings to default values."""
        # Reset general settings
        self.language_combo.setCurrentText("System Default")
        self.autosave_check.setChecked(False)
        self.autosave_interval.setValue(5)
        self.updates_check.setChecked(True)
        self.project_folder.setText("")
        
        # Reset editor settings
        self.font_combo.setCurrentText("Consolas")
        self.font_size.setValue(12)
        self.tab_size.setValue(4)
        self.use_spaces.setChecked(True)
        self.word_wrap.setChecked(False)
        self.auto_complete.setChecked(True)
        self.spellcheck.setChecked(False)
        self.spell_lang_combo.setCurrentText("English (US)")
        
        # Reset appearance settings
        self.theme_combo.setCurrentText("Dark Theme")
        self.bg_color.set_color("#1E1E1E")
        self.text_color.set_color("#D4D4D4")
        self.selection_color.set_color("#264F78")
        self.highlight_color.set_color("#FFD700")
        
        # Reset shortcuts
        self._reset_shortcuts()
        
        logger.info("Settings reset to defaults")
        
    def set_api(self, api):
        """
        Set the API for this panel.
        
        Args:
            api: The API instance
        """
        self.api = api
        
    def load_settings(self, settings):
        """
        Load settings into the UI.
        
        Args:
            settings: Dictionary of settings
        """
        self.settings = settings
        
        # Apply settings to UI controls
        # This would be implemented in a real application
    
    def apply_typography(self):
        """Apply typography settings to all panel elements."""
        try:
            # Direct access - typography_manager is initialized in __init__
            if not self.typography_manager:
                logger.warning("Typography manager not available in PreferencesPanel")
                return
                
            # Apply title typography - title_label is always created in _setup_ui
            font = self.typography_manager.get_font(FontRole.PANEL_TITLE)
            self.title_label.setFont(font)
            
            # Apply typography to tab widget - tab_widget is always created in _setup_ui
            tab_font = self.typography_manager.get_font(FontRole.BODY)
            self.tab_widget.setFont(tab_font)
            
            # Apply to tab bar
            tab_bar = self.tab_widget.tabBar()
            if tab_bar:
                tab_bar.setFont(tab_font)
            
            # Apply typography to buttons - buttons are always created in _setup_ui
            button_font = self.typography_manager.get_font(FontRole.BUTTON)
            self.save_button.setFont(button_font)
            self.reset_button.setFont(button_font)
            
            # Apply typography to form controls
            self._apply_form_typography()
            
            logger.debug("Typography applied to PreferencesPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply typography to PreferencesPanel: {e}")
    
    def apply_theme(self):
        """Apply current theme to the panel."""
        try:
            # Direct access - theme_manager is initialized in __init__
            if not self.theme_manager:
                logger.warning("Theme manager not available in PreferencesPanel")
                return
                
            self._apply_theme_styling()
            logger.debug("Theme applied to PreferencesPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply theme to PreferencesPanel: {e}")
    
    def _apply_form_typography(self):
        """Apply typography to form elements."""
        try:
            body_font = self.typography_manager.get_font(FontRole.BODY)
            small_font = self.typography_manager.get_font(FontRole.SMALL)
            
            # Apply to combo boxes - direct access with exception handling
            for attr_name in ['language_combo', 'font_combo', 'theme_combo', 'spell_lang_combo']:
                try:
                    widget = self.__dict__[attr_name]
                    widget.setFont(body_font)
                except KeyError:
                    # Widget doesn't exist, which is fine for optional form elements
                    pass
            
            # Apply to checkboxes - direct access with exception handling
            for attr_name in ['autosave_check', 'updates_check', 'use_spaces', 'word_wrap', 'auto_complete', 'spellcheck']:
                try:
                    widget = self.__dict__[attr_name]
                    widget.setFont(body_font)
                except KeyError:
                    # Widget doesn't exist, which is fine for optional form elements
                    pass
            
            # Apply to spinboxes - direct access with exception handling
            for attr_name in ['autosave_interval', 'font_size', 'tab_size']:
                try:
                    widget = self.__dict__[attr_name]
                    widget.setFont(body_font)
                except KeyError:
                    # Widget doesn't exist, which is fine for optional form elements
                    pass
            
            # Apply to line edits - direct access with exception handling
            for attr_name in ['project_folder']:
                try:
                    widget = self.__dict__[attr_name]
                    widget.setFont(body_font)
                except KeyError:
                    # Widget doesn't exist, which is fine for optional form elements
                    pass
            
            # Apply to group boxes - direct access with exception handling
            for attr_name in ['editor_group', 'appearance_group', 'shortcuts_group']:
                try:
                    widget = self.__dict__[attr_name]
                    widget.setFont(self.typography_manager.get_font(FontRole.PANEL_TITLE))
                except KeyError:
                    # Widget doesn't exist, which is fine for optional form elements
                    pass
            
        except Exception as e:
            logger.error(f"Failed to apply form typography: {e}")
    
    def _apply_theme_styling(self):
        """Apply theme-based styling with fallbacks."""
        try:
            logger.info("Applying theme styling to PreferencesPanel")
            
            # Set object names for CSS targeting
            self.title_label.setObjectName("panel_title")
            self.tab_widget.setObjectName("tab_widget")
            self.save_button.setObjectName("primary_button")
            self.reset_button.setObjectName("secondary_button")
            
            # Clear any existing stylesheets to ensure global theme takes precedence
            self.title_label.setStyleSheet("")
            self.tab_widget.setStyleSheet("")
            self.save_button.setStyleSheet("")
            self.reset_button.setStyleSheet("")
            
            logger.info("Theme styling applied successfully to PreferencesPanel")
            
        except Exception as e:
            logger.error(f"Failed to apply theme styling: {e}")
    
    def _connect_typography_signals(self):
        """Connect to typography and theme change signals."""
        try:
            # Direct access - managers are initialized in __init__
            if self.typography_manager:
                # TypographyManager has 'fonts_changed' signal, not 'font_changed'
                self.typography_manager.fonts_changed.connect(self.apply_typography)
            
            if self.theme_manager:
                self.theme_manager.theme_changed.connect(self.apply_theme)
            
            logger.debug("Typography signals connected for PreferencesPanel")
            
        except Exception as e:
            logger.error(f"Failed to connect typography signals: {e}")
