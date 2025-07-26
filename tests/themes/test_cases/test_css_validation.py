#!/usr/bin/env python3
"""CSS validation test"""

import sys
sys.path.append('.')

from PySide6.QtWidgets import QApplication, QWidget
from services.css_manager import CSSManager

def test_css_syntax():
    app = QApplication([])
    
    # Get the dark theme CSS
    css_manager = CSSManager()
    dark_css = css_manager.get_css("dark_theme")
    
    if not dark_css:
        print("Failed to load dark_theme CSS")
        return
    
    print(f"CSS length: {len(dark_css)} chars")
    
    # Try to apply to a test widget
    test_widget = QWidget()
    
    try:
        print("Testing widget-specific CSS application...")
        test_widget.setStyleSheet(dark_css)
        print("✓ Widget-specific CSS applied successfully")
    except Exception as e:
        print(f"✗ Widget CSS failed: {e}")
    
    try:
        print("Testing application-wide CSS application...")
        # Clear any existing style first
        app.setStyleSheet("")
        app.setStyleSheet(dark_css)
        print("✓ Application CSS applied successfully")
        
        # Check if it actually took
        applied_css = app.styleSheet()
        print(f"Applied CSS length: {len(applied_css)} chars")
        
        if "QTreeView::item:selected" in applied_css:
            print("✓ QTreeView rules are in applied stylesheet")
        else:
            print("✗ QTreeView rules missing from applied stylesheet")
            
    except Exception as e:
        print(f"✗ Application CSS failed: {e}")

if __name__ == "__main__":
    test_css_syntax()
