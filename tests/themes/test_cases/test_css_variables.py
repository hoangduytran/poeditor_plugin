#!/usr/bin/env python3
"""
Test CSS variables implementation in Dark theme.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.css_file_based_theme_manager import CSSFileBasedThemeManager

def test_css_variables():
    """Test CSS variables implementation."""
    print("=== Testing CSS Variables Implementation ===\n")

    # Get the theme manager instance
    theme_manager = CSSFileBasedThemeManager.get_instance()

    # Get raw CSS content for Dark theme
    dark_css = theme_manager.get_raw_css('Dark')

    if dark_css:
        print(f"Dark theme CSS: {len(dark_css):,} characters\n")

        # Check for CSS variables
        variables_found = []
        if ':root {' in dark_css:
            variables_found.append('✓ :root selector found')
        if '--border-primary:' in dark_css:
            variables_found.append('✓ --border-primary variable defined')
        if '--bg-primary:' in dark_css:
            variables_found.append('✓ --bg-primary variable defined')
        if '--text-primary:' in dark_css:
            variables_found.append('✓ --text-primary variable defined')
        if '--accent-blue:' in dark_css:
            variables_found.append('✓ --accent-blue variable defined')

        # Check for variable usage
        usage_found = []
        if 'var(--border-primary)' in dark_css:
            count = dark_css.count('var(--border-primary)')
            usage_found.append(f'✓ var(--border-primary) used {count} times')
        if 'var(--bg-primary)' in dark_css:
            count = dark_css.count('var(--bg-primary)')
            usage_found.append(f'✓ var(--bg-primary) used {count} times')
        if 'var(--text-primary)' in dark_css:
            count = dark_css.count('var(--text-primary)')
            usage_found.append(f'✓ var(--text-primary) used {count} times')

        # Check for old hardcoded values
        old_values = []
        border_count = dark_css.count('#464647')
        if border_count > 0:
            old_values.append(f'⚠️  #464647 still found {border_count} times (should be replaced)')

        bg_count = dark_css.count('#1e1e1e')
        if bg_count > 1:  # One occurrence is acceptable in QMainWindow override
            old_values.append(f'⚠️  #1e1e1e still found {bg_count} times')

        text_count = dark_css.count('#cccccc')
        if text_count > 0:
            old_values.append(f'⚠️  #cccccc still found {text_count} times (should use var(--text-primary))')

        # Display results
        print("CSS VARIABLES DEFINED:")
        for var in variables_found:
            print(f"  {var}")

        print("\nVARIABLE USAGE:")
        for usage in usage_found:
            print(f"  {usage}")

        if old_values:
            print("\nREMAINING HARDCODED VALUES:")
            for old in old_values:
                print(f"  {old}")
        else:
            print("\n✅ No hardcoded values found!")

        # Show sample of CSS variables section
        print("\nCSS VARIABLES SECTION PREVIEW:")
        lines = dark_css.split('\n')
        in_root = False
        root_lines = []
        for line in lines:
            if ':root {' in line:
                in_root = True
            if in_root:
                root_lines.append(line)
                if '}' in line and '--' not in line:
                    break

        for line in root_lines[:15]:  # Show first 15 lines
            print(f"  {line}")

        if len(root_lines) > 15:
            print(f"  ... ({len(root_lines)-15} more lines)")

    else:
        print("❌ Could not load Dark theme CSS")

    print("\n=== CSS Variables Test Complete ===")

if __name__ == "__main__":
    test_css_variables()
