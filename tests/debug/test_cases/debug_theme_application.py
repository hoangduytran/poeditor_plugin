#!/usr/bin/env python3
"""Debug script to check theme application"""

import sys
import os
sys.path.append('.')

from PySide6.QtWidgets import QApplication
from widgets.simple_explorer_widget import SimpleExplorerWidget
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

def debug_theme_application():
    app = QApplication([])
    
    # Create the explorer widget
    explorer = SimpleExplorerWidget()
    
    # Check if CSS theme manager is working
    theme_manager = CSSFileBasedThemeManager()
    
    # Check available themes
    available_themes = theme_manager.get_available_themes()
    print("Available themes:", available_themes)
    
    # Force reload the dark theme
    print("Force reloading theme...")
    theme_manager.set_theme("Dark")
    
    # Force apply the theme again
    dark_css = theme_manager.get_raw_css("Dark")
    if dark_css:
        print(f"Got Dark CSS: {len(dark_css)} chars")
        theme_manager._apply_theme(dark_css)
    else:
        print("Failed to get Dark CSS content")
    
    # Get the style sheet applied to the application
    app_stylesheet = app.styleSheet()
    print("Application stylesheet length:", len(app_stylesheet))
    print("First 500 chars of stylesheet:")
    print(app_stylesheet[:500])
    print("...")
    
    # Check if QTreeView rules are in the stylesheet
    if "QTreeView::item:selected" in app_stylesheet:
        print("\n✓ QTreeView selection rules found in stylesheet")
        
        # Extract the QTreeView selection color
        lines = app_stylesheet.split('\n')
        in_treeview_selected = False
        for line in lines:
            if "QTreeView::item:selected" in line:
                in_treeview_selected = True
                print(f"Found rule: {line.strip()}")
            elif in_treeview_selected and "background-color:" in line:
                print(f"Selection color: {line.strip()}")
                in_treeview_selected = False
    else:
        print("\n✗ QTreeView selection rules NOT found in stylesheet")
    
    # Check the actual widget
    file_view = explorer.file_view
    print(f"\nFile view type: {type(file_view)}")
    print(f"File view class: {file_view.__class__.__name__}")
    print(f"File view object name: '{file_view.objectName()}'")
    
    # Get the actual stylesheet applied to the widget
    widget_stylesheet = file_view.styleSheet()
    print(f"Widget stylesheet length: {len(widget_stylesheet)}")
    
    if widget_stylesheet:
        print("Widget has specific stylesheet:")
        print(widget_stylesheet[:200])
    else:
        print("Widget uses application stylesheet")

if __name__ == "__main__":
    debug_theme_application()
