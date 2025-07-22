"""
Example implementation of the typography and theme system.

This module provides example widgets that demonstrate the proper usage
of the typography and theme system in various components.

Following rules.md: No hasattr/getattr usage, proper error handling with lg.py logger.
"""

from lg import logger
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QGroupBox, QTabWidget, QApplication,
    QDialog, QDialogButtonBox, QFormLayout, QSlider, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from themes.typography import get_font, FontRole, get_typography_manager
from themes.theme_manager import get_theme_manager


class ThemedComponentsWidget(QWidget):
    """Example widget showcasing properly themed components."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()

        self.setWindowTitle("Typography and Theme Example")
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title using HEADING_1
        title = QLabel("Typography Demo")
        title.setFont(get_font(FontRole.HEADING_1))
        layout.addWidget(title)

        # Subtitle using HEADING_3
        subtitle = QLabel("Showcasing consistent typography across components")
        subtitle.setFont(get_font(FontRole.HEADING_3))
        layout.addWidget(subtitle)

        # Form group
        form_group = QGroupBox("Form Elements")
        form_layout = QFormLayout(form_group)

        # Text input using theme styling
        self.text_input = QLineEdit()
        self.text_input.setFont(get_font(FontRole.BODY))
        self.text_input.setPlaceholderText("Enter text...")
        self.apply_component_style(self.text_input, "search_input")
        form_layout.addRow("Text Input:", self.text_input)

        # Dropdown using theme styling
        self.dropdown = QComboBox()
        self.dropdown.setFont(get_font(FontRole.BODY))
        self.dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        self.apply_component_style(self.dropdown, "button")
        form_layout.addRow("Dropdown:", self.dropdown)

        layout.addWidget(form_group)

        # Button row
        button_layout = QHBoxLayout()

        # Primary button
        self.primary_btn = QPushButton("Primary Action")
        self.primary_btn.setFont(get_font(FontRole.BUTTON))
        self.apply_component_style(self.primary_btn, "button")
        button_layout.addWidget(self.primary_btn)

        # Secondary button
        self.secondary_btn = QPushButton("Secondary Action")
        self.secondary_btn.setFont(get_font(FontRole.BUTTON))
        self.apply_component_style(self.secondary_btn, "button")
        button_layout.addWidget(self.secondary_btn)

        layout.addLayout(button_layout)

        # Status text using SMALL
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(get_font(FontRole.SMALL))
        layout.addWidget(self.status_label)

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Select Theme:")
        theme_label.setFont(get_font(FontRole.BODY))
        self.theme_combo = QComboBox()

        # Populate themes
        available_themes = get_theme_manager().get_available_themes()
        for theme_id, theme_name in available_themes.items():
            self.theme_combo.addItem(theme_name, theme_id)

        # Set current theme
        current_theme_id = get_theme_manager().get_current_theme_id()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme_id:
                self.theme_combo.setCurrentIndex(i)
                break

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font settings button
        self.font_settings_btn = QPushButton("Font Settings...")
        self.font_settings_btn.setFont(get_font(FontRole.BUTTON))
        self.apply_component_style(self.font_settings_btn, "button")
        layout.addWidget(self.font_settings_btn)

    def connect_signals(self):
        """Connect widget signals to slots."""
        # Theme change
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        # Font settings button
        self.font_settings_btn.clicked.connect(self._show_font_settings)

        # Listen for theme and typography changes
        self.theme_manager.theme_changed.connect(self._on_theme_updated)
        self.typography_manager.fonts_changed.connect(self._on_fonts_changed)

        # Button actions
        self.primary_btn.clicked.connect(lambda: self._set_status("Primary action clicked"))
        self.secondary_btn.clicked.connect(lambda: self._set_status("Secondary action clicked"))

    def _on_theme_changed(self, index):
        """Handle theme combo box selection change."""
        theme_id = self.theme_combo.itemData(index)
        if theme_id:
            self.theme_manager.set_theme(theme_id)
            self._set_status(f"Theme changed to {self.theme_combo.itemText(index)}")

    def _on_theme_updated(self, theme_id):
        """Handle theme updates from outside this widget."""
        # Update combo box selection
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme_id:
                if self.theme_combo.currentIndex() != i:
                    self.theme_combo.setCurrentIndex(i)
                break

        # Apply component styles
        self._update_component_styles()

    def _on_fonts_changed(self):
        """Handle font changes."""
        # Update all fonts in the UI
        self._update_fonts()
        self._set_status("Fonts updated")

    def _update_fonts(self):
        """Update fonts for all components."""
        # This would be more thorough in a real implementation
        # but this demonstrates the pattern
        for widget, role in [
            (self.findChild(QLabel, ""), FontRole.HEADING_1),
            (self.text_input, FontRole.BODY),
            (self.dropdown, FontRole.BODY),
            (self.primary_btn, FontRole.BUTTON),
            (self.secondary_btn, FontRole.BUTTON),
            (self.status_label, FontRole.SMALL)
        ]:
            if widget:
                widget.setFont(get_font(role))

    def _update_component_styles(self):
        """Update styles for all components."""
        self.apply_component_style(self.text_input, "search_input")
        self.apply_component_style(self.dropdown, "button")
        self.apply_component_style(self.primary_btn, "button")
        self.apply_component_style(self.secondary_btn, "button")
        self.apply_component_style(self.font_settings_btn, "button")

    def apply_component_style(self, widget, component_name):
        """Apply theme styling to a component."""
        try:
            style = self.theme_manager.get_style_for_component(component_name)
            widget_class = widget.__class__.__name__
            widget.setStyleSheet(f"{widget_class} {{ {style} }}")
        except Exception as e:
            logger.error(f"Failed to apply component style: {e}")

    def _set_status(self, message):
        """Update status text."""
        self.status_label.setText(f"Status: {message}")

    def _show_font_settings(self):
        """Show font settings dialog."""
        dialog = FontSettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self._set_status("Font settings updated")


class FontSettingsDialog(QDialog):
    """Dialog for adjusting typography settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()

        self.setWindowTitle("Font Settings")
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Font family selection
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Inter, Segoe UI, Arial, sans-serif",
            "SF Pro Display, system-ui, sans-serif",
            "Roboto, Arial, sans-serif",
            "Ubuntu, Arial, sans-serif"
        ])
        self.font_family_combo.setCurrentText(self.typography_manager.get_base_font_family())
        form_layout.addRow("Font Family:", self.font_family_combo)

        # Font size selection
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.typography_manager.get_base_font_size())
        form_layout.addRow("Base Font Size:", self.font_size_spin)

        # Scale factor slider
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(50, 200)  # 0.5x to 2.0x
        self.scale_slider.setValue(int(self.typography_manager.get_scale_factor() * 100))

        self.scale_label = QLabel(f"{self.typography_manager.get_scale_factor():.1f}x")
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_label.setText(f"{v/100:.1f}x")
        )

        scale_layout = QHBoxLayout()
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_label)
        form_layout.addRow("Scale Factor:", scale_layout)

        layout.addLayout(form_layout)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_heading = QLabel("Heading Example")
        self.preview_heading.setFont(get_font(FontRole.HEADING_2))

        self.preview_body = QLabel("This is an example of body text that shows how the font will appear in the application. The quick brown fox jumps over the lazy dog.")
        self.preview_body.setFont(get_font(FontRole.BODY))
        self.preview_body.setWordWrap(True)

        self.preview_small = QLabel("This is smaller text for UI elements and metadata")
        self.preview_small.setFont(get_font(FontRole.SMALL))

        self.preview_code = QLabel("function example() { return 'code sample'; }")
        self.preview_code.setFont(get_font(FontRole.CODE))

        preview_layout.addWidget(self.preview_heading)
        preview_layout.addWidget(self.preview_body)
        preview_layout.addWidget(self.preview_small)
        preview_layout.addWidget(self.preview_code)

        layout.addWidget(preview_group)

        # Real-time preview checkbox
        self.live_preview_check = QCheckBox("Live Preview")
        self.live_preview_check.setChecked(True)
        layout.addWidget(self.live_preview_check)

        # Connect signals for live preview
        self.font_family_combo.currentTextChanged.connect(self._update_preview)
        self.font_size_spin.valueChanged.connect(self._update_preview)
        self.scale_slider.valueChanged.connect(self._update_preview)

        # Standard dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._apply_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _update_preview(self):
        """Update the font preview."""
        if not self.live_preview_check.isChecked():
            return

        # Get current settings from dialog
        family = self.font_family_combo.currentText()
        size = self.font_size_spin.value()
        scale = self.scale_slider.value() / 100.0

        # Create temporary QFonts for preview
        heading_font = QFont(family.split(',')[0].strip())
        heading_font.setPointSize(int(size * 1.6 * scale))
        heading_font.setBold(True)

        body_font = QFont(family.split(',')[0].strip())
        body_font.setPointSize(int(size * scale))

        small_font = QFont(family.split(',')[0].strip())
        small_font.setPointSize(int(size * 0.85 * scale))

        # Code font is special case
        code_font = QFont("JetBrains Mono, Consolas, Monaco, monospace".split(',')[0].strip())
        code_font.setPointSize(int(size * 0.95 * scale))

        # Apply to preview labels
        self.preview_heading.setFont(heading_font)
        self.preview_body.setFont(body_font)
        self.preview_small.setFont(small_font)
        self.preview_code.setFont(code_font)

    def _apply_settings(self):
        """Apply the settings and close the dialog."""
        # Get current settings from dialog
        family = self.font_family_combo.currentText()
        size = self.font_size_spin.value()
        scale = self.scale_slider.value() / 100.0

        # Apply to typography manager
        self.theme_manager.customize_font_settings(
            font_family=family,
            font_size=size,
            scale_factor=scale
        )

        self.accept()


def show_demo():
    """Show the themed components demo window."""
    app = QApplication([])

    # Initialize theme system
    theme_manager = get_theme_manager()
    typography_manager = get_typography_manager()

    # Apply default theme
    theme_manager.set_theme("light")
    typography_manager.apply_to_application()

    # Create and show demo widget
    widget = ThemedComponentsWidget()
    widget.show()

    app.exec()


if __name__ == "__main__":
    show_demo()
