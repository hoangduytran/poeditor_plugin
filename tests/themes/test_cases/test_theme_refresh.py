#!/usr/bin/env python3
"""
Test to force theme refresh and check for #094771 color sources.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel, QPushButton
from PySide6.QtGui import QPalette, QColor
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

class ThemeTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Test - Force Refresh")
        self.setMinimumSize(400, 300)
        
        # Get theme manager
        self.theme_manager = CSSFileBasedThemeManager.get_instance()
        
        layout = QVBoxLayout()
        
        # Current theme info
        current_theme = self.theme_manager.current_theme
        layout.addWidget(QLabel(f"Current theme: {current_theme}"))
        
        # Force refresh button
        refresh_btn = QPushButton("Force Theme Refresh")
        refresh_btn.clicked.connect(self.force_refresh)
        layout.addWidget(refresh_btn)
        
        # Clear cache button
        clear_btn = QPushButton("Clear Theme Cache")
        clear_btn.clicked.connect(self.clear_cache)
        layout.addWidget(clear_btn)
        
        # Test list widget
        self.list_widget = QListWidget()
        self.list_widget.addItem("Item 1 - Check selection color")
        self.list_widget.addItem("Item 2 - Should NOT be #094771")
        self.list_widget.addItem("Item 3 - Should be system default")
        layout.addWidget(self.list_widget)
        
        # Palette info
        self.palette_label = QLabel()
        self.update_palette_info()
        layout.addWidget(self.palette_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def force_refresh(self):
        """Force refresh the current theme."""
        print("=== FORCING THEME REFRESH ===")
        current_theme = self.theme_manager.current_theme
        if current_theme:
            # Clear current theme and reapply
            self.theme_manager.current_theme = None
            self.theme_manager.set_theme(current_theme)
            print(f"Forced refresh of theme: {current_theme}")
            self.update_palette_info()
        else:
            print("No current theme to refresh")
    
    def clear_cache(self):
        """Clear theme cache."""
        print("=== CLEARING THEME CACHE ===")
        self.theme_manager._css_cache.clear()
        self.theme_manager._cache_loaded = False
        print("Theme cache cleared")
        self.force_refresh()
    
    def update_palette_info(self):
        """Update palette information display."""
        app = QApplication.instance()
        palette = app.palette()
        highlight_color = palette.color(QPalette.ColorRole.Highlight)
        
        # Check if it's the problematic color
        is_problem_color = highlight_color.name().lower() == "#094771"
        
        info_text = f"Highlight Color: {highlight_color.name()}"
        if is_problem_color:
            info_text += " ⚠️ PROBLEM COLOR DETECTED!"
        else:
            info_text += " ✅ Clean"
        
        self.palette_label.setText(info_text)
        
        print(f"Current highlight color: {highlight_color.name()}")
        return highlight_color.name()

def main():
    app = QApplication(sys.argv)
    
    print("=== THEME TEST APPLICATION ===")
    print("This will test the current theme state and allow forced refresh")
    
    window = ThemeTestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
