#!/usr/bin/env python3
"""
Debug CSS content being loaded by theme manager.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

def debug_css_content():
    """Debug what CSS content is being loaded."""
    app = QApplication(sys.argv)
    
    # Get theme manager
    theme_manager = CSSFileBasedThemeManager.get_instance()
    
    print("=== CSS THEME DEBUG ===")
    print(f"Current theme: {theme_manager.current_theme}")
    print(f"Use file CSS: {theme_manager.use_file_css}")
    
    # Get the current CSS content
    if theme_manager.current_theme:
        css_content = theme_manager.get_raw_css(theme_manager.current_theme)
        print(f"\nCSS content length: {len(css_content) if css_content else 0} characters")
        
        if css_content:
            # Search for any blue-ish colors
            lines = css_content.split('\n')
            blue_colors = []
            
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                # Look for hex colors that might be blue-ish
                import re
                hex_colors = re.findall(r'#[0-9a-f]{6}', line_lower)
                for color in hex_colors:
                    if any(pattern in color for pattern in ['084', '094', 'a5c', 'blue', 'selection', 'highlight']):
                        blue_colors.append((i, line.strip(), color))
            
            print(f"\nFound {len(blue_colors)} potentially relevant colors:")
            for line_num, line_text, color in blue_colors:
                print(f"  Line {line_num}: {color} -> {line_text}")
            
            # Also check what's actually applied to the application
            current_stylesheet = app.styleSheet()
            print(f"\nActual applied stylesheet length: {len(current_stylesheet)} characters")
            
            # Search for blue colors in applied stylesheet
            applied_colors = re.findall(r'#[0-9a-f]{6}', current_stylesheet.lower())
            unique_colors = list(set(applied_colors))
            print(f"Colors found in applied stylesheet: {unique_colors}")
            
            # Look specifically for the colors we're seeing
            if '#084ad9' in current_stylesheet.lower():
                print("🎯 FOUND #084ad9 in applied stylesheet!")
            if '#094771' in current_stylesheet.lower():
                print("⚠️ FOUND #094771 in applied stylesheet!")
                
        else:
            print("No CSS content found!")
    
    print("\n=== PALETTE DEBUG ===")
    palette = app.palette()
    highlight_color = palette.color(palette.ColorRole.Highlight)
    print(f"Current palette highlight: {highlight_color.name()}")
    
    return app

if __name__ == "__main__":
    app = debug_css_content()
    print("\nDebug complete. Exiting...")
