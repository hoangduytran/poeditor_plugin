#!/usr/bin/env python3
"""
Debug CSS specificity for explorer file list.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel, QPushButton
from PySide6.QtGui import QPalette, QColor
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

class ExplorerDebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Explorer CSS Debug")
        self.setMinimumSize(500, 400)
        
        # Get theme manager
        self.theme_manager = CSSFileBasedThemeManager.get_instance()
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Testing different list widget configurations:"))
        
        # Test 1: Generic QListWidget (like your tests)
        layout.addWidget(QLabel("1. Generic QListWidget:"))
        generic_list = QListWidget()
        generic_list.addItem("Generic item 1")
        generic_list.addItem("Generic item 2 (should use QListWidget CSS)")
        generic_list.addItem("Generic item 3")
        layout.addWidget(generic_list)
        
        # Test 2: QListWidget with explorer_file_list objectName (like real explorer)
        layout.addWidget(QLabel("2. QListWidget with objectName='explorer_file_list':"))
        explorer_list = QListWidget()
        explorer_list.setObjectName("explorer_file_list")  # Same as real explorer
        explorer_list.addItem("Explorer item 1")
        explorer_list.addItem("Explorer item 2 (should use specific CSS)")
        explorer_list.addItem("Explorer item 3")
        layout.addWidget(explorer_list)
        
        # Test 3: Force specific style
        force_btn = QPushButton("Force Apply CSS to Explorer List")
        force_btn.clicked.connect(lambda: self.force_apply_css(explorer_list))
        layout.addWidget(force_btn)
        
        # Test 4: Show current applied styles
        style_btn = QPushButton("Show Applied Styles")
        style_btn.clicked.connect(lambda: self.show_styles(explorer_list))
        layout.addWidget(style_btn)
        
        # Status
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.update_status()
    
    def force_apply_css(self, list_widget):
        """Force apply specific CSS to the list widget."""
        print("=== FORCING CSS APPLICATION ===")
        
        # Apply very specific CSS directly
        specific_css = """
        QListWidget {
            background-color: #252526;
            color: #cccccc;
        }
        QListWidget::item:selected {
            background-color: #ff0000 !important;
            color: #ffffff !important;
        }
        QListWidget::item:hover {
            background-color: #00ff00 !important;
        }
        """
        
        try:
            list_widget.setStyleSheet(specific_css)
            print(f"Applied direct CSS to widget: {list_widget.objectName()}")
            self.status_label.setText("✅ Direct CSS applied with !important")
        except Exception as e:
            print(f"Failed to apply CSS: {e}")
            self.status_label.setText(f"❌ Failed: {e}")
    
    def show_styles(self, list_widget):
        """Show what styles are currently applied."""
        print("=== CURRENT STYLE ANALYSIS ===")
        
        # Check applied stylesheet
        widget_style = list_widget.styleSheet()
        app_style = QApplication.instance().styleSheet()
        
        print(f"Widget objectName: {list_widget.objectName()}")
        print(f"Widget-specific stylesheet length: {len(widget_style)}")
        print(f"App-wide stylesheet length: {len(app_style)}")
        
        # Check palette
        palette = list_widget.palette()
        highlight = palette.color(QPalette.ColorRole.Highlight)
        base = palette.color(QPalette.ColorRole.Base)
        
        info = f"""Current State:
Object Name: {list_widget.objectName()}
Widget CSS: {len(widget_style)} chars
App CSS: {len(app_style)} chars  
Palette Highlight: {highlight.name()}
Palette Base: {base.name()}"""
        
        self.status_label.setText(info)
        print(info)
    
    def update_status(self):
        """Update status with current theme info."""
        theme = self.theme_manager.current_theme
        css_length = len(self.theme_manager.get_raw_css(theme) or "")
        self.status_label.setText(f"Theme: {theme}, CSS: {css_length} chars")

def main():
    app = QApplication(sys.argv)
    
    print("=== EXPLORER CSS DEBUG ===")
    print("This will test CSS application to list widgets")
    
    window = ExplorerDebugWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
