#!/usr/bin/env python3
"""Force refresh theme in running application"""

import sys
sys.path.append('.')

from PySide6.QtWidgets import QApplication
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

def force_theme_refresh():
    app = QApplication.instance()
    if not app:
        print("No running QApplication found")
        return
    
    print("Found running QApplication")
    
    # Get theme manager and force reload
    theme_manager = CSSFileBasedThemeManager()
    
    # Clear any existing style
    print("Clearing existing stylesheet...")
    app.setStyleSheet("")
    
    # Force reload dark theme
    print("Force reloading dark theme...")
    success = theme_manager.reload_current_theme()
    
    if success:
        print("✓ Theme reloaded successfully")
        
        # Verify application
        css = app.styleSheet()
        if "QTreeView::item:selected" in css and "#37373d" in css:
            print("✓ QTreeView selection color is now #37373d")
        else:
            print("✗ QTreeView selection rules not found or incorrect")
    else:
        print("✗ Failed to reload theme")

if __name__ == "__main__":
    force_theme_refresh()
