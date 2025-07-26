#!/usr/bin/env python3
"""
Comprehensive test to trace where styling comes from in the POEditor app.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel, QPushButton
from PySide6.QtGui import QPalette, QColor
from services.css_file_based_theme_manager import CSSFileBasedThemeManager
from lg import logger

class AppStyleTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POEditor Style Tracking")
        self.setMinimumSize(600, 500)
        
        # Get theme manager
        self.theme_manager = CSSFileBasedThemeManager.get_instance()
        
        # Display available themes dynamically
        available_themes = self.theme_manager.get_available_themes()
        logger.info(f"Available themes discovered: {available_themes}")
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("POEditor Application Style Analysis")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px;")
        layout.addWidget(title)
        
        # Theme info
        self.theme_info = QLabel()
        layout.addWidget(self.theme_info)
        
        # CSS info
        self.css_info = QLabel()
        layout.addWidget(self.css_info)
        
        # Force apply theme button
        apply_btn = QPushButton("Force Apply Theme (Like POEditor Does)")
        apply_btn.clicked.connect(self.force_apply_theme)
        layout.addWidget(apply_btn)
        
        # Test what happens when we manually apply full CSS
        full_css_btn = QPushButton("Apply Full CSS File Manually")
        full_css_btn.clicked.connect(self.apply_full_css)
        layout.addWidget(full_css_btn)
        
        # Test widgets that should be styled
        layout.addWidget(QLabel("Test widgets (should be styled if CSS works):"))
        
        self.test_list = QListWidget()
        self.test_list.addItem("List item 1 - Check colors")
        self.test_list.addItem("List item 2 - Selection test")
        self.test_list.addItem("List item 3 - Background test")
        layout.addWidget(self.test_list)
        
        # Status display
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        # Initial analysis
        self.analyze_current_state()
    
    def analyze_current_state(self):
        """Analyze what's currently controlling the app styling."""
        app = QApplication.instance()
        
        # Theme manager state
        current_theme = self.theme_manager.current_theme
        use_file_css = self.theme_manager.use_file_css
        
        # Get current CSS
        css_content = ""
        if current_theme:
            css_content = self.theme_manager.get_raw_css(current_theme)
        
        # Application stylesheet
        app_stylesheet = app.styleSheet()
        
        # Palette info
        palette = app.palette()
        highlight_color = palette.color(QPalette.ColorRole.Highlight)
        window_color = palette.color(QPalette.ColorRole.Window)
        
        # Update displays
        self.theme_info.setText(f"""Theme: {current_theme} | Use File CSS: {use_file_css}
CSS Content Length: {len(css_content) if css_content else 0} chars""")
        
        self.css_info.setText(f"""Applied Stylesheet Length: {len(app_stylesheet)} chars
Window Color: {window_color.name()} | Highlight: {highlight_color.name()}""")
        
        # Detailed analysis
        analysis = []
        
        if len(app_stylesheet) == 0:
            analysis.append("❌ NO CSS APPLIED - App using system defaults")
        else:
            analysis.append(f"✅ CSS Applied ({len(app_stylesheet)} chars)")
        
        if not css_content:
            analysis.append("❌ No CSS content loaded from theme files")
        elif len(css_content) < 1000:
            analysis.append(f"⚠️ Minimal CSS loaded ({len(css_content)} chars)")
        else:
            analysis.append(f"✅ Full CSS content loaded ({len(css_content)} chars)")
        
        if highlight_color.name() == "#a5cdff":
            analysis.append("ℹ️ Using macOS system highlight color")
        elif highlight_color.name() == "#094771":
            analysis.append("⚠️ Using old hardcoded color (should be fixed)")
        else:
            analysis.append(f"? Using custom highlight: {highlight_color.name()}")
        
        self.status_label.setText("\\n".join(analysis))
        
        logger.info("=== CURRENT STYLE ANALYSIS ===")
        for item in analysis:
            logger.info(item)
        logger.info(f"Theme file path being used: themes/css/{current_theme.lower() if current_theme else 'none'}_theme.css")
    
    def force_apply_theme(self):
        """Force apply theme exactly like POEditor does."""
        logger.info("=== FORCING THEME APPLICATION ===")
        current_theme = self.theme_manager.current_theme
        if current_theme:
            # Clear and reapply
            self.theme_manager.current_theme = None
            self.theme_manager.set_theme(current_theme)
            logger.info(f"Re-applied theme: {current_theme}")
        else:
            # Apply default theme
            self.theme_manager.apply_saved_theme()
            logger.info("Applied saved theme")
        
        self.analyze_current_state()
    
    def apply_full_css(self):
        """Manually apply the full CSS file to see if that works."""
        logger.info("=== APPLYING FULL CSS MANUALLY ===")
        
        # Try to load the full CSS file directly from the correct location
        full_css_path = "themes/css/dark_theme.css"  # Correct path with css/ subdirectory
        try:
            with open(full_css_path, 'r', encoding='utf-8') as f:
                full_css = f.read()
            
            logger.info(f"Loaded {len(full_css)} characters from {full_css_path}")
            
            # Apply directly to application
            app = QApplication.instance()
            app.setStyleSheet(full_css)
            
            logger.info("✅ Full CSS applied directly!")
            self.analyze_current_state()
            
        except Exception as e:
            logger.info(f"❌ Failed to load full CSS: {e}")
            self.status_label.setText(f"Failed to load full CSS: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    logger.info("=== POEditor Style Tracking ===")
    logger.info("This will help identify what's controlling your app's styling")
    
    tracker = AppStyleTracker()
    tracker.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
