#!/usr/bin/env python3
"""
Test Qt's CSS variables support
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

def test_qt_css_variables():
    """Test if Qt supports CSS variables."""
    print("=== Testing Qt CSS Variables Support ===\n")

    app = QApplication(sys.argv)

    # Create a test widget
    widget = QWidget()
    layout = QVBoxLayout(widget)
    label = QLabel("Test Label")
    layout.addWidget(label)

    # Test CSS with variables
    css_with_variables = """
    :root {
        --test-color: #ff0000;
        --test-bg: #00ff00;
    }

    QLabel {
        color: var(--test-color);
        background-color: var(--test-bg);
        padding: 10px;
    }
    """

    # Test CSS without variables
    css_without_variables = """
    QLabel {
        color: #ff0000;
        background-color: #00ff00;
        padding: 10px;
    }
    """

    print("1. Testing CSS with variables...")
    widget.setStyleSheet(css_with_variables)
    widget.show()
    widget.repaint()

    # Check if the styling was applied
    actual_style = widget.styleSheet()
    print(f"   Applied stylesheet: {len(actual_style)} characters")

    # Get computed style (this is limited in Qt)
    palette = label.palette()
    print(f"   Label background role: {label.backgroundRole()}")
    print(f"   Label foreground role: {label.foregroundRole()}")

    widget.hide()

    print("\n2. Testing CSS without variables...")
    widget.setStyleSheet(css_without_variables)
    widget.show()
    widget.repaint()

    actual_style2 = widget.styleSheet()
    print(f"   Applied stylesheet: {len(actual_style2)} characters")

    widget.hide()

    print("\n3. CSS Variable Support Analysis:")
    if 'var(' in css_with_variables:
        print("   ✓ CSS contains variable syntax")

    # Check if Qt processed the variables
    if 'var(' in actual_style:
        print("   ⚠️ CSS variables NOT processed by Qt (var() still present)")
        print("   ❌ Qt does NOT support CSS custom properties")
        return False
    else:
        print("   ✓ CSS variables processed by Qt")
        print("   ✅ Qt supports CSS custom properties")
        return True

if __name__ == "__main__":
    try:
        supports_variables = test_qt_css_variables()
        if not supports_variables:
            print("\n🚨 ISSUE FOUND: Qt doesn't support CSS variables!")
            print("   Need to replace CSS variables with hardcoded values.")
        else:
            print("\n✅ Qt supports CSS variables - issue is elsewhere.")
    except Exception as e:
        print(f"\nError during test: {e}")
    finally:
        print("\n=== Test Complete ===")
