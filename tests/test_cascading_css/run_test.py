#!/usr/bin/env python3
"""
Simple runner for the CSS cascading theme test.
Usage: python run_test.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the CSS cascading theme test."""
    test_file = Path(__file__).parent / "test_cascading_themes.py"

    print("🎨 Starting CSS Cascading Theme Test...")
    print("📁 Test directory:", Path(__file__).parent)
    print("🐍 Python executable:", sys.executable)
    print()
    print("Controls:")
    print("  Ctrl+Shift+T - Cycle themes (Dark → Light → Colorful)")
    print("  Use the UI elements to see how themes affect different widgets")
    print()

    try:
        # Run the test
        result = subprocess.run([sys.executable, str(test_file)],
                              cwd=Path(__file__).parent.parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
