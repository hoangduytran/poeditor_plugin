#!/usr/bin/env python3
"""
Main entry point for the POEditor application.

This script initializes the PySide6 application and creates the main window
with the plugin-based architecture.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from lg import logger

from core.main_app_window import MainAppWindow


def main():
    """Main application entry point."""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("POEditor")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("POEditor")
        app.setOrganizationDomain("poeditor.com")
        
        # Import resources after QApplication is created
        import resources_rc

        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        logger.info("Starting POEditor application")
        
        # Create main window
        window = MainAppWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run the application
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
