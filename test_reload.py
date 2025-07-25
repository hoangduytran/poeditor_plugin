#!/usr/bin/env python3
"""
Test script to test CSS file reload functionality.
This will test if changes to CSS files are reflected when themes are reloaded.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.css_file_based_theme_manager import CSSFileBasedThemeManager
from lg import logger

def test_css_reload():
    """Test CSS file reload functionality."""
    print("=== Testing CSS File Reload Functionality ===")
    
    # Get the theme manager instance
    theme_manager = CSSFileBasedThemeManager.get_instance()
    
    print(f"Current theme: {theme_manager.current_theme}")
    print(f"Using file-based CSS: {theme_manager.use_file_css}")
    print(f"CSS Manager available: {theme_manager.css_manager is not None}")
    
    # Get current CSS content for comparison
    if theme_manager.current_theme:
        theme_file_name = f"{theme_manager.current_theme.lower()}_theme"
        
        # Check if it's in cache
        if theme_file_name in theme_manager._css_cache:
            cached_css = theme_manager._css_cache[theme_file_name]
            print(f"CSS in cache: {len(cached_css)} characters")
            
            # Show first few lines to see if our change is there
            lines = cached_css.split('\n')[:10]
            for i, line in enumerate(lines, 1):
                if 'background-color:' in line and '#2a0a0a' in line:
                    print(f"✓ Found test change in cache at line {i}: {line.strip()}")
                    break
            else:
                print("❌ Test change NOT found in cached CSS")
        
        # Test reload functionality
        print("\n--- Testing reload_current_theme() ---")
        success = theme_manager.reload_current_theme()
        print(f"Reload result: {success}")
        
        if success:
            # Check cache again after reload
            if theme_file_name in theme_manager._css_cache:
                reloaded_css = theme_manager._css_cache[theme_file_name]
                print(f"Reloaded CSS: {len(reloaded_css)} characters")
                
                # Check if the change is there now
                lines = reloaded_css.split('\n')[:20]  # Check more lines
                for i, line in enumerate(lines, 1):
                    if 'background-color:' in line and '#2a0a0a' in line:
                        print(f"✓ Test change found after reload at line {i}: {line.strip()}")
                        break
                    elif 'background-color:' in line and '#1e1e1e' in line:
                        print(f"❌ Old color still found at line {i}: {line.strip()}")
                        break
                else:
                    # If not found in first 20 lines, search the entire CSS
                    if '#2a0a0a' in reloaded_css:
                        print("✓ Test change found somewhere in reloaded CSS")
                    else:
                        print("❌ Test change NOT found anywhere in reloaded CSS")
                        # Show what we actually got
                        for i, line in enumerate(lines[:10], 1):
                            if 'QWidget' in line or 'background-color' in line:
                                print(f"  Line {i}: {line.strip()}")
        else:
            print("❌ Reload failed")
    
    print("\n=== CSS Reload Test Complete ===")

if __name__ == "__main__":
    test_css_reload()
