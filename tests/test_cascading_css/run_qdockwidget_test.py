#!/usr/bin/env python3
"""
Simple runner for the QDockWidget title bar customization test.
"""

import sys
from pathlib import Path

# Add the test directory to the path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

# Import and run the test
from test_qdockwidget_title_bars import main

if __name__ == "__main__":
    sys.exit(main())
