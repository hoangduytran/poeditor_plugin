"""
Column Header Navigation Test

This script tests the navigation functionality in the column header context menu.
It specifically focuses on the quick navigation options.
"""

import sys
import time
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add the root directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from widgets.simple_explorer_widget_with_column_menu import SimpleExplorerWidgetWithColumnMenu
from lg import logger


class ColumnHeaderNavigationTest:
    """Test for column header navigation functionality."""
    
    def __init__(self):
        """Initialize the test."""
        self.app = QApplication(sys.argv)
        self.explorer = None
        
    def setup(self):
        """Set up the test environment."""
        logger.info("Setting up column header navigation test")
        
        # Create explorer widget with column menu
        self.explorer = SimpleExplorerWidgetWithColumnMenu()
        self.explorer.resize(800, 600)
        self.explorer.show()
        
        return True
        
    def run_test(self):
        """Run the test sequence."""
        if not self.setup():
            logger.error("Test setup failed")
            return False
            
        logger.info("Starting column header navigation test sequence")
        
        # Test 1: Get the initial path
        initial_path = self.explorer.get_current_path()
        logger.info(f"Initial path: {initial_path}")
        
        # Test 2: Navigate to Home
        home_path = os.path.expanduser("~")
        logger.info(f"Simulating navigation to Home: {home_path}")
        self.explorer.file_view._on_navigation_requested(home_path)
        
        # Wait for UI to update
        QApplication.processEvents()
        time.sleep(1)
        
        # Check if navigation worked
        current_path = self.explorer.get_current_path()
        logger.info(f"Current path after Home navigation: {current_path}")
        if current_path != home_path:
            logger.error(f"Navigation failed! Expected: {home_path}, Got: {current_path}")
            return False
            
        # Test 3: Navigate to Documents
        documents_path = os.path.join(home_path, "Documents")
        if os.path.exists(documents_path):
            logger.info(f"Simulating navigation to Documents: {documents_path}")
            self.explorer.file_view._on_navigation_requested(documents_path)
            
            # Wait for UI to update
            QApplication.processEvents()
            time.sleep(1)
            
            # Check if navigation worked
            current_path = self.explorer.get_current_path()
            logger.info(f"Current path after Documents navigation: {current_path}")
            if current_path != documents_path:
                logger.error(f"Navigation failed! Expected: {documents_path}, Got: {current_path}")
                return False
        else:
            logger.warning(f"Documents folder does not exist at {documents_path}, skipping this test")
            
        # Test 4: Navigate to root directory
        root_path = "/"
        logger.info(f"Simulating navigation to Root: {root_path}")
        self.explorer.file_view._on_navigation_requested(root_path)
        
        # Wait for UI to update
        QApplication.processEvents()
        time.sleep(1)
        
        # Check if navigation worked
        current_path = self.explorer.get_current_path()
        logger.info(f"Current path after Root navigation: {current_path}")
        if current_path != root_path:
            logger.error(f"Navigation failed! Expected: {root_path}, Got: {current_path}")
            return False
            
        logger.info("Test sequence completed successfully")
        return True
        
    def execute(self):
        """Execute the test and return result."""
        success = self.run_test()
        
        # Keep window open for a few seconds for visual inspection
        time.sleep(5)
        
        return success

def main():
    """Main entry point."""
    # Set up logging
    logger.setLevel(logging.INFO)
    
    # Run test
    test = ColumnHeaderNavigationTest()
    success = test.execute()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
