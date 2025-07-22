"""
Example of how to integrate the typography system with UI components.

This demonstrates best practices for using fonts and themes in the application.
"""

from lg import logger
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from PySide6.QtCore import QTimer

from themes.typography import get_font, FontRole, get_typography_manager
from themes.theme_manager import get_theme_manager


class ThemedWidget(QWidget):
    """Example widget showing proper typography usage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.typography_manager = get_typography_manager()

        self._setup_ui()
        self._apply_theme()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Title (uses HEADING_1 role)
        self.title_label = QLabel("Explorer Panel")
        layout.addWidget(self.title_label)

        # Subtitle (uses SUBTITLE role)
        self.subtitle_label = QLabel("Advanced file management")
        layout.addWidget(self.subtitle_label)

        # Search input (uses BODY role)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        layout.addWidget(self.search_input)

        # Button (uses BUTTON role)
        self.action_button = QPushButton("Browse Files")
        layout.addWidget(self.action_button)

        # Code text (uses CODE role)
        self.code_label = QLabel("*.po, *.pot, *.mo")
        layout.addWidget(self.code_label)

    def _apply_theme(self):
        """Apply current theme to all components."""
        # Method 1: Set fonts directly using typography manager
        self.title_label.setFont(get_font(FontRole.HEADING_1))
        self.subtitle_label.setFont(get_font(FontRole.SUBTITLE))
        self.search_input.setFont(get_font(FontRole.BODY))
        self.action_button.setFont(get_font(FontRole.BUTTON))
        self.code_label.setFont(get_font(FontRole.CODE))

        # Method 2: Use theme manager for complete styling
        search_style = self.theme_manager.get_style_for_component("search_input")
        button_style = self.theme_manager.get_style_for_component("button")

        self.search_input.setStyleSheet(f"QLineEdit {{ {search_style} }}")
        self.action_button.setStyleSheet(f"QPushButton {{ {button_style} }}")

    def _connect_signals(self):
        """Connect theme change signals."""
        self.typography_manager.fonts_changed.connect(self._on_fonts_changed)
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_fonts_changed(self):
        """Handle font changes."""
        logger.debug("Fonts changed, updating widget")
        self._apply_theme()

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes."""
        logger.debug(f"Theme changed to: {theme_name}")
        self._apply_theme()


class FontPreferencesWidget(QWidget):
    """Widget for user font preferences."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.typography_manager = get_typography_manager()

        self._setup_ui()

    def _setup_ui(self):
        """Set up the preferences UI."""
        layout = QVBoxLayout(self)

        # Font family selection
        from PySide6.QtWidgets import QComboBox, QSpinBox, QSlider
        from PySide6.QtCore import Qt

        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Inter, Segoe UI, Arial, sans-serif",
            "SF Pro Display, system-ui, sans-serif",
            "Roboto, Arial, sans-serif",
            "Ubuntu, Arial, sans-serif"
        ])
        self.font_combo.setCurrentText(self.typography_manager.get_base_font_family())

        # Font size selection
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(8, 24)
        self.size_spinbox.setValue(self.typography_manager.get_base_font_size())

        # Scale factor for accessibility
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(50, 200)  # 0.5x to 2.0x
        self.scale_slider.setValue(int(self.typography_manager.get_scale_factor() * 100))

        layout.addWidget(QLabel("Font Family:"))
        layout.addWidget(self.font_combo)
        layout.addWidget(QLabel("Font Size:"))
        layout.addWidget(self.size_spinbox)
        layout.addWidget(QLabel("Scale Factor:"))
        layout.addWidget(self.scale_slider)

        # Connect signals
        self.font_combo.currentTextChanged.connect(self._on_font_family_changed)
        self.size_spinbox.valueChanged.connect(self._on_font_size_changed)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)

    def _on_font_family_changed(self, family: str):
        """Handle font family change."""
        self.typography_manager.set_base_font_family(family)

    def _on_font_size_changed(self, size: int):
        """Handle font size change."""
        self.typography_manager.set_base_font_size(size)

    def _on_scale_changed(self, value: int):
        """Handle scale factor change."""
        scale = value / 100.0
        self.typography_manager.set_scale_factor(scale)


# Example usage in your main application
def setup_application_typography():
    """Set up typography for the entire application."""
    theme_manager = get_theme_manager()
    typography_manager = get_typography_manager()

    # Load user preferences
    # (You would integrate this with your settings service)

    # Apply default theme
    theme_manager.set_theme("light")

    # Apply typography to the entire application
    typography_manager.apply_to_application()

    logger.info("Application typography configured")


# Example of component-specific styling
def get_explorer_panel_stylesheet() -> str:
    """Get stylesheet for the explorer panel."""
    theme_manager = get_theme_manager()

    return f"""
    QLabel#panel_title {{
        {theme_manager.get_style_for_component("panel_title")}
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 2px 5px;
        border-bottom: 1px solid #e5e5e5;
    }}
    
    QLineEdit {{
        {theme_manager.get_style_for_component("search_input")}
        border-radius: 3px;
        padding: 4px 6px;
    }}
    
    QPushButton {{
        {theme_manager.get_style_for_component("button")}
        border-radius: 3px;
        padding: 4px 8px;
    }}
    
    QPushButton:hover {{
        background-color: #e8e8e8;
    }}
    """
