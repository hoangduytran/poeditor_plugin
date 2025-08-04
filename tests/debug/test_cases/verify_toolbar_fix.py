#!/usr/bin/env python3
"""
Quick test to verify toolbar gradient fix.
"""

import sys
from pathlib import Path

# Add project root to path - script is in tests/debug/test_cases/, so go up 3 levels
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def check_toolbar_css():
    """Check if the toolbar CSS has been fixed."""
    theme_file = project_root / "themes" / "css" / "dark_theme.css"

    if not theme_file.exists():
        print(f"❌ Theme file not found: {theme_file}")
        return False

    content = theme_file.read_text()

    # Check if gradient is removed
    gradient_found = "qlineargradient" in content.lower() and "sidebar_toolbar" in content

    # Check if flat background is applied
    flat_bg_found = "QToolBar#sidebar_toolbar" in content and "background-color: #252526" in content

    # Check if VS Code colors are used
    vs_code_colors = ["#252526", "#464647", "#cccccc", "#2a2d2e"]
    vs_code_colors_found = all(color in content for color in vs_code_colors)

    print("=== TOOLBAR CSS VERIFICATION ===")
    print(f"✅ Gradient removed: {'Yes' if not gradient_found else 'No'}")
    print(f"✅ Flat background applied: {'Yes' if flat_bg_found else 'No'}")
    print(f"✅ VS Code colors used: {'Yes' if vs_code_colors_found else 'No'}")

    # Show relevant CSS section
    lines = content.split('\n')
    toolbar_section = []
    in_toolbar_section = False

    for line in lines:
        if "QToolBar#sidebar_toolbar" in line and "{" in line:
            in_toolbar_section = True

        if in_toolbar_section:
            toolbar_section.append(line)

        if in_toolbar_section and "}" in line and len(toolbar_section) > 1:
            break

    if toolbar_section:
        print("\n=== CURRENT TOOLBAR CSS ===")
        for line in toolbar_section:
            print(line)

    return not gradient_found and flat_bg_found and vs_code_colors_found

if __name__ == "__main__":
    success = check_toolbar_css()
    print(f"\n{'✅ VERIFICATION PASSED' if success else '❌ VERIFICATION FAILED'}")
    sys.exit(0 if success else 1)
