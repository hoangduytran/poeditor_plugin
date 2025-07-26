#!/usr/bin/env python3
"""
Simple runner for the QToolBar CSS theme test.
"""

import sys
from pathlib import Path

# Add the test directory to the path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

# Import and run the test
from test_qtoolbar_themes import main

if __name__ == "__main__":
    sys.exit(main())
