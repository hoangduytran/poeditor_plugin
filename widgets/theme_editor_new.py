"""
Theme Editor widget for the POEditor application.

Provides a visual interface for creating and editing custom themes.
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QLineEdit, QColorDialog, QComboBox, QGroupBox,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QTabWidget,
    QCheckBox
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, Signal

from services.theme_manager import theme_manager, Theme
from lg import logger


class ColorPickerButton(QPushButton):
    """
    A button that opens a color picker and displays the selected color.
    """
    
    color_changed = Signal(str)  # Emits hex color string
    
    def __init__(self, initial_color: str = "#ffffff", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._color = QColor(initial_color)
        self.setFixedSize(60, 30)
        self.update_button_color()
        self.clicked.connect(self._open_color_dialog)
    
    def update_button_color(self) -> None:
        """Update the button's background color to show the selected color."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color.name()};
                border: 2px solid #cccccc;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #999999;
            }}
        """)
        self.setText(self._color.name().upper())
        
        # Set text color based on luminance
        luminance = (0.299 * self._color.red() + 
                    0.587 * self._color.green() + 
                    0.114 * self._color.blue())
        text_color = "#000000" if luminance > 128 else "#ffffff"
        
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + f"QPushButton {{ color: {text_color}; }}")
    
    def _open_color_dialog(self) -> None:
        """Open the color picker dialog."""
        color = QColorDialog.getColor(self._color, self, "Select Color")
        if color.isValid():
            self.set_color(color.name())
    
    def set_color(self, color: str) -> None:
        """
        Set the color.
        
        Args:
            color: Hex color string
        """
        self._color = QColor(color)
        self.update_button_color()
        self.color_changed.emit(color)
    
    def get_color(self) -> str:
        """Get the current color as hex string."""
        return self._color.name()


class ThemePreviewWidget(QWidget):
    """
    Widget that shows a preview of the theme.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup the preview UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Theme Preview")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Preview area
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.Box)
        preview_frame.setMinimumHeight(200)
        
        preview_layout = QVBoxLayout(preview_frame)
        
        # Sample elements
        sample_label = QLabel("Sample Text")
        sample_button = QPushButton("Sample Button")
        sample_input = QLineEdit("Sample Input")
        
        preview_layout.addWidget(sample_label)
        preview_layout.addWidget(sample_button)
        preview_layout.addWidget(sample_input)
        preview_layout.addStretch()
        
        layout.addWidget(preview_frame)
        
        self._preview_frame = preview_frame
        self._sample_elements = [sample_label, sample_button, sample_input]
    
    def update_preview(self, theme_colors: Dict[str, str]) -> None:
        """
        Update the preview with the given theme colors.
        
        Args:
            theme_colors: Dictionary of theme color values
        """
        try:
            # Apply theme CSS to preview frame
            preview_css = f"""
            QFrame {{
                background-color: {theme_colors.get('background', '#ffffff')};
                color: {theme_colors.get('text_primary', '#000000')};
                border: 1px solid {theme_colors.get('border', '#cccccc')};
            }}
            QLabel {{
                color: {theme_colors.get('text_primary', '#000000')};
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {theme_colors.get('button_background', '#f0f0f0')};
                color: {theme_colors.get('text_primary', '#000000')};
                border: 1px solid {theme_colors.get('border', '#cccccc')};
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme_colors.get('button_hover', '#e0e0e0')};
            }}
            QLineEdit {{
                background-color: {theme_colors.get('input_background', '#ffffff')};
                color: {theme_colors.get('text_primary', '#000000')};
                border: 1px solid {theme_colors.get('input_border', '#cccccc')};
                padding: 6px;
                border-radius: 4px;
            }}
            """
            
            self._preview_frame.setStyleSheet(preview_css)
            
        except Exception as e:
            logger.error(f"Failed to update theme preview: {e}")


class ThemeEditor(QWidget):
    """
    Main theme editor widget.
    
    Provides a comprehensive interface for creating and editing themes.
    """
    
    theme_saved = Signal(str)  # Emits theme name when saved
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_theme_name = ""
        self._theme_colors: Dict[str, str] = {}
        self._color_buttons: Dict[str, ColorPickerButton] = {}
        self._preview_widget: Optional[ThemePreviewWidget] = None
        
        self.setup_ui()
        self._load_existing_theme('Light')  # Start with Light theme
        
        logger.info("ThemeEditor initialized")
    
    def setup_ui(self) -> None:
        """Setup the theme editor UI."""
        layout = QHBoxLayout(self)
        
        # Left side: Theme editing
        left_widget = self._create_editor_widget()
        
        # Right side: Preview
        right_widget = self._create_preview_widget()
        
        # Add to layout with splitter-like behavior
        layout.addWidget(left_widget, 2)  # 2/3 of space
        layout.addWidget(right_widget, 1)  # 1/3 of space
    
    def _create_editor_widget(self) -> QWidget:
        """Create the main editor widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with theme selection and actions
        header_layout = QHBoxLayout()
        
        # Theme selection
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(theme_manager.get_available_themes())
        self._theme_combo.currentTextChanged.connect(self._on_theme_selected)
        header_layout.addWidget(QLabel("Base Theme:"))
        header_layout.addWidget(self._theme_combo)
        
        header_layout.addStretch()
        
        # Action buttons
        new_button = QPushButton("New Theme")
        new_button.clicked.connect(self._new_theme)
        save_button = QPushButton("Save Theme")
        save_button.clicked.connect(self._save_theme)
        export_button = QPushButton("Export")
        export_button.clicked.connect(self._export_theme)
        import_button = QPushButton("Import")
        import_button.clicked.connect(self._import_theme)
        
        header_layout.addWidget(new_button)
        header_layout.addWidget(save_button)
        header_layout.addWidget(export_button)
        header_layout.addWidget(import_button)
        
        layout.addLayout(header_layout)
        
        # Theme name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Theme Name:"))
        self._name_input = QLineEdit()
        name_layout.addWidget(self._name_input)
        layout.addLayout(name_layout)
        
        # Dark mode checkbox
        dark_mode_layout = QHBoxLayout()
        self._dark_mode_checkbox = QCheckBox("Dark Mode")
        dark_mode_layout.addWidget(self._dark_mode_checkbox)
        layout.addLayout(dark_mode_layout)
        
        # Color editing tabs
        tabs = QTabWidget()
        
        # Main colors tab
        main_tab = self._create_color_group("Main Colors", [
            ("background", "Background"),
            ("secondary_background", "Secondary Background"),
            ("surface", "Surface"),
            ("text_primary", "Primary Text"),
            ("text_secondary", "Secondary Text"),
            ("text_disabled", "Disabled Text"),
        ])
        tabs.addTab(main_tab, "Main")
        
        # Accent colors tab
        accent_tab = self._create_color_group("Accent Colors", [
            ("accent", "Accent"),
            ("accent_hover", "Accent Hover"),
            ("accent_pressed", "Accent Pressed"),
            ("accent_light", "Accent Light"),
        ])
        tabs.addTab(accent_tab, "Accent")
        
        # State colors tab
        state_tab = self._create_color_group("State Colors", [
            ("success", "Success"),
            ("warning", "Warning"),
            ("error", "Error"),
            ("info", "Info"),
        ])
        tabs.addTab(state_tab, "State")
        
        # Border colors tab
        border_tab = self._create_color_group("Border Colors", [
            ("border", "Border"),
            ("border_focus", "Border Focus"),
            ("border_hover", "Border Hover"),
        ])
        tabs.addTab(border_tab, "Border")
        
        # Interactive elements tab
        interactive_tab = self._create_color_group("Interactive Elements", [
            ("button_background", "Button Background"),
            ("button_hover", "Button Hover"),
            ("button_pressed", "Button Pressed"),
            ("input_background", "Input Background"),
            ("input_border", "Input Border"),
            ("input_focus", "Input Focus"),
        ])
        tabs.addTab(interactive_tab, "Interactive")
        
        layout.addWidget(tabs)
        
        return widget
    
    def _create_preview_widget(self) -> QWidget:
        """Create the preview widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preview area
        self._preview_widget = ThemePreviewWidget()
        layout.addWidget(self._preview_widget)
        
        # Apply button
        apply_button = QPushButton("Apply Theme")
        apply_button.clicked.connect(self._apply_theme)
        layout.addWidget(apply_button)
        
        return widget
    
    def _create_color_group(self, title: str, colors: list) -> QScrollArea:
        """
        Create a group of color editing controls.
        
        Args:
            title: Group title
            colors: List of (field_name, display_name) tuples
            
        Returns:
            QScrollArea containing the color controls
        """
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QGridLayout(widget)
        
        for i, (field_name, display_name) in enumerate(colors):
            label = QLabel(display_name + ":")
            color_button = ColorPickerButton()
            color_button.color_changed.connect(
                lambda color, field=field_name: self._on_color_changed(field, color)
            )
            
            layout.addWidget(label, i, 0)
            layout.addWidget(color_button, i, 1)
            
            self._color_buttons[field_name] = color_button
        
        layout.setRowStretch(len(colors), 1)  # Add stretch at bottom
        
        scroll_area.setWidget(widget)
        return scroll_area
    
    def _load_existing_theme(self, theme_name: str) -> None:
        """
        Load an existing theme for editing.
        
        Args:
            theme_name: Name of the theme to load
        """
        try:
            theme = theme_manager.get_theme(theme_name)
            if not theme:
                logger.error(f"Theme '{theme_name}' not found")
                return
            
            # Store theme information
            self._current_theme_name = theme_name
            
            # Extract theme colors from CSS file
            self._extract_theme_colors(theme)
            
            self._name_input.setText(f"{theme_name} (Copy)")
            self._dark_mode_checkbox.setChecked(theme.dark_mode)
            self._update_color_buttons()
            self._update_preview()
            
        except Exception as e:
            logger.error(f"Failed to load theme '{theme_name}': {e}")
    
    def _extract_theme_colors(self, theme: Theme) -> None:
        """
        Extract colors from theme CSS file.
        
        Args:
            theme: Theme to extract colors from
        """
        try:
            # Here we would parse the CSS file to extract color values
            # For now, let's use some default values for demonstration
            default_colors = {
                # Main colors
                'background': '#ffffff',
                'secondary_background': '#f5f5f5',
                'surface': '#ffffff',
                'text_primary': '#333333',
                'text_secondary': '#666666',
                'text_disabled': '#999999',
                
                # Accent colors
                'accent': '#007acc',
                'accent_hover': '#0062a3',
                'accent_pressed': '#004e82',
                'accent_light': '#e5f3ff',
                
                # State colors
                'success': '#22c55e',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6',
                
                # Border colors
                'border': '#cccccc',
                'border_focus': '#007acc',
                'border_hover': '#999999',
                
                # Interactive elements
                'button_background': '#f0f0f0',
                'button_hover': '#e0e0e0',
                'button_pressed': '#d0d0d0',
                'input_background': '#ffffff',
                'input_border': '#cccccc',
                'input_focus': '#007acc',
            }
            
            # For dark theme, use different defaults
            if theme.dark_mode:
                default_colors.update({
                    'background': '#1e1e1e',
                    'secondary_background': '#252525',
                    'surface': '#2d2d2d',
                    'text_primary': '#ffffff',
                    'text_secondary': '#cccccc',
                    'text_disabled': '#888888',
                    'border': '#444444',
                    'button_background': '#2d2d2d',
                    'button_hover': '#3c3c3c',
                    'button_pressed': '#505050',
                    'input_background': '#3c3c3c',
                    'input_border': '#444444',
                })
                
            self._theme_colors = default_colors
                
        except Exception as e:
            logger.error(f"Failed to extract theme colors: {e}")
    
    def _update_color_buttons(self) -> None:
        """Update all color buttons with current theme colors."""
        try:
            for field_name, button in self._color_buttons.items():
                if field_name in self._theme_colors:
                    color = self._theme_colors[field_name]
                    button.set_color(color)
        except Exception as e:
            logger.error(f"Failed to update color buttons: {e}")
    
    def _update_preview(self) -> None:
        """Update the theme preview."""
        if self._theme_colors and self._preview_widget:
            self._preview_widget.update_preview(self._theme_colors)
    
    def _on_theme_selected(self, theme_name: str) -> None:
        """Handle theme selection change."""
        self._load_existing_theme(theme_name)
    
    def _on_color_changed(self, field_name: str, color: str) -> None:
        """
        Handle color change.
        
        Args:
            field_name: Name of the color field
            color: New hex color value
        """
        try:
            self._theme_colors[field_name] = color
            self._update_preview()
        except Exception as e:
            logger.error(f"Failed to update color '{field_name}': {e}")
    
    def _new_theme(self) -> None:
        """Create a new theme."""
        # Initialize with light theme colors
        self._current_theme_name = "New"
        self._load_existing_theme("Light")
        self._name_input.setText("New Theme")
    
    def _save_theme(self) -> None:
        """Save the current theme."""
        try:
            theme_name = self._name_input.text().strip()
            if not theme_name:
                QMessageBox.warning(self, "Warning", "Please enter a theme name.")
                return
            
            # Create a new theme with current settings
            new_theme = Theme(
                name=theme_name,
                css_path=f":/css/themes/css/{theme_name.lower()}_theme.css",  # This would need to be created
                dark_mode=self._dark_mode_checkbox.isChecked(),
                accent_color=self._theme_colors.get('accent', '#007acc'),
                description=f"Custom theme based on {self._current_theme_name}"
            )
            
            # We'd need to generate the CSS file here based on the colors
            # For now, we'll just register the theme
            
            if theme_manager.register_theme(new_theme):
                QMessageBox.information(self, "Success", f"Theme '{theme_name}' saved successfully.")
                self.theme_saved.emit(theme_name)
            else:
                QMessageBox.warning(self, "Error", "Failed to save theme.")
                
        except Exception as e:
            logger.error(f"Failed to save theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save theme: {e}")
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the application."""
        try:
            theme_name = self._name_input.text().strip()
            if not theme_name:
                QMessageBox.warning(self, "Warning", "Please enter a theme name.")
                return
                
            # Create a temporary theme for preview
            temp_name = f"Preview_{theme_name}"
            
            # Create a new theme with current settings
            preview_theme = Theme(
                name=temp_name,
                css_path=f":/css/themes/css/{self._current_theme_name.lower()}_theme.css",  # Use base theme CSS for now
                dark_mode=self._dark_mode_checkbox.isChecked(),
                accent_color=self._theme_colors.get('accent', '#007acc'),
                description=f"Preview of {theme_name}"
            )
            
            # Register and apply the theme
            if theme_manager.register_theme(preview_theme):
                if theme_manager.set_theme(temp_name):
                    QMessageBox.information(self, "Success", "Theme applied successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to apply theme.")
            else:
                QMessageBox.warning(self, "Error", "Failed to register theme for preview.")
                
        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply theme: {e}")
    
    def _export_theme(self) -> None:
        """Export the current theme to a file."""
        try:
            theme_name = self._name_input.text().strip()
            if not theme_name:
                QMessageBox.warning(self, "Warning", "Please enter a theme name.")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Theme", f"{theme_name}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                # Create a temporary theme to export
                temp_theme = Theme(
                    name=theme_name,
                    css_path="",  # This would be generated
                    dark_mode=self._dark_mode_checkbox.isChecked(),
                    accent_color=self._theme_colors.get('accent', '#007acc'),
                    description=f"Custom theme based on {self._current_theme_name}"
                )
                
                # Register temporarily for export
                theme_manager.register_theme(temp_theme)
                
                if theme_manager.export_theme(theme_name, file_path):
                    QMessageBox.information(self, "Success", "Theme exported successfully.")
                    
                    # Clean up temporary theme
                    theme_manager.unregister_theme(theme_name)
                else:
                    QMessageBox.warning(self, "Error", "Failed to export theme.")
                    
        except Exception as e:
            logger.error(f"Failed to export theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export theme: {e}")
    
    def _import_theme(self) -> None:
        """Import a theme from a file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Theme", "", "JSON Files (*.json)"
            )
            
            if file_path:
                if theme_manager.import_theme(file_path):
                    QMessageBox.information(self, "Success", "Theme imported successfully.")
                    # Refresh theme combo
                    self._theme_combo.clear()
                    self._theme_combo.addItems(theme_manager.get_available_themes())
                else:
                    QMessageBox.warning(self, "Error", "Failed to import theme.")
                    
        except Exception as e:
            logger.error(f"Failed to import theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to import theme: {e}")
