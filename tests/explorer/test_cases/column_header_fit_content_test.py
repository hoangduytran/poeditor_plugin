"""
Column Header Fit Content Test

This script tests the fit content functionality in the column header context menu.
It specifically focuses on the "fit content" option for columns.
"""

import sys
import time
import logging
import os

# Add the root directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from widgets.simple_explorer_widget_with_column_menu import SimpleExplorerWidgetWithColumnMenu
from services.column_manager_service_integration import ColumnManagerService
from lg import logger

class ColumnFitContentTest:
    """Test for column header fit content functionality."""
    
    def __init__(self):
        """Initialize the test."""
        self.app = QApplication(sys.argv)
        self.explorer = None
        
    def setup(self):
        """Set up the test environment."""
        logger.info("Setting up column fit content test")
        
        # Create explorer widget with column menu
        self.explorer = SimpleExplorerWidgetWithColumnMenu()
        self.explorer.resize(800, 600)
        self.explorer.show()
        
        # Get column manager service
        self.column_manager = self.explorer.file_view.column_manager
        if not self.column_manager:
            logger.error("Column manager service not available")
            return False
            
        return True
        
    def run_test(self):
        """Run the test sequence."""
        if not self.setup():
            logger.error("Test setup failed")
            return False
            
        logger.info("Starting column fit content test sequence")
        
        # Test 1: Check initial fit content setting
        initial_fit = self.column_manager.get_fit_content_enabled()
        logger.info(f"Initial fit content setting: {initial_fit}")
        
        # Test 2: Enable fit content if not already enabled
        if not initial_fit:
            logger.info("Enabling fit content")
            self.column_manager.set_fit_content_enabled(True)
            
            # Verify setting was applied
            current_fit = self.column_manager.get_fit_content_enabled()
            logger.info(f"Fit content after enabling: {current_fit}")
            if not current_fit:
                logger.error("Failed to enable fit content")
                return False
        else:
            logger.info("Fit content is already enabled")
            
        # Wait for UI to update
        QApplication.processEvents()
        time.sleep(1)
        
        # Test 3: Check column widths
        header = self.explorer.file_view.header()
        if header:
            for section in range(header.count()):
                width = header.sectionSize(section)
                logger.info(f"Column {section} width after fit content: {width}")
        else:
            logger.error("Header not available")
            
        # Test 4: Toggle fit content off
        logger.info("Disabling fit content")
        self.column_manager.set_fit_content_enabled(False)
        
        # Verify setting was applied
        current_fit = self.column_manager.get_fit_content_enabled()
        logger.info(f"Fit content after disabling: {current_fit}")
        if current_fit:
            logger.error("Failed to disable fit content")
            return False
            
        # Wait for UI to update
        QApplication.processEvents()
        time.sleep(1)
        
        # Test 5: Enable fit content again to see if resizing works
        logger.info("Re-enabling fit content")
        self.column_manager.set_fit_content_enabled(True)
        
        # Wait for UI to update
        QApplication.processEvents()
        time.sleep(1)
        
        # Test 6: Check column widths after re-enabling
        if header:
            for section in range(header.count()):
                width = header.sectionSize(section)
                logger.info(f"Column {section} width after re-enabling fit content: {width}")
        else:
            logger.error("Header not available")
        
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
    test = ColumnFitContentTest()
    success = test.execute()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
