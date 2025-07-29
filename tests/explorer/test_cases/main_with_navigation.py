#!/usr/bin/env python3
"""
HeaderNavigationWidget in Main Application Demo

This script shows how the HeaderNavigationWidget can be integrated into
the main POEditor application by modifying the existing explorer panel.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from lg import logger
from core.main_app_window import MainAppWindow
from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from services.path_completion_service import PathCompletionService
from widgets.explorer.explorer_header_bar import HeaderNavigationWidget


def integrate_navigation_header(main_window):
    """
    Integrate HeaderNavigationWidget into the main application's explorer panel.
    
    Args:
        main_window: The main application window
    """
    try:
        # Wait a bit for panels to be fully loaded
        QTimer.singleShot(500, lambda: _perform_integration(main_window))
        logger.info("Scheduled HeaderNavigationWidget integration")
    except Exception as e:
        logger.error(f"Failed to schedule integration: {e}")


def _perform_integration(main_window):
    """Perform the actual HeaderNavigationWidget integration."""
    try:
        # Get the explorer panel
        if not hasattr(main_window, 'sidebar_manager') or not main_window.sidebar_manager:
            logger.warning("SidebarManager not available yet")
            return
            
        # Find panels that might contain the explorer
        panels = []
        if hasattr(main_window.sidebar_manager, 'panels'):
            panels = main_window.sidebar_manager.panels
        elif hasattr(main_window.sidebar_manager, 'get_panel'):
            try:
                explorer_panel = main_window.sidebar_manager.get_panel('explorer')
                if explorer_panel:
                    panels = [explorer_panel]
            except:
                pass
                
        if not panels:
            logger.warning("No explorer panels found")
            return
            
        # Look for explorer widgets in the panels
        explorer_widget = None
        for panel in panels:
            if hasattr(panel, 'explorer_widget'):
                explorer_widget = panel.explorer_widget
                break
            elif hasattr(panel, 'widget') and hasattr(panel.widget, 'file_view'):
                explorer_widget = panel.widget
                break
                
        if not explorer_widget:
            logger.warning("No explorer widget found in panels")
            return
            
        # Get the file view
        file_view = None
        if hasattr(explorer_widget, 'file_view'):
            file_view = explorer_widget.file_view
        elif hasattr(explorer_widget, 'tree_view'):
            file_view = explorer_widget.tree_view
            
        if not file_view:
            logger.warning("No file view found in explorer widget")
            return
            
        # Create navigation services
        navigation_service = NavigationService()
        history_service = NavigationHistoryService()
        location_manager = LocationManager()
        completion_service = PathCompletionService()
        
        # Set up service dependencies
        navigation_service.set_dependencies(
            history_service=history_service,
            location_manager=location_manager
        )
        
        # Create navigation header
        nav_header = HeaderNavigationWidget(Qt.Orientation.Horizontal)
        
        # Inject services
        nav_header.inject_services(
            navigation_service=navigation_service,
            history_service=history_service,
            location_manager=location_manager,
            completion_service=completion_service
        )
        
        # Replace the tree view header
        file_view.setHeader(nav_header)
        
        # Store reference
        main_window.explorer_nav_header = nav_header
        
        logger.info("✅ HeaderNavigationWidget successfully integrated!")
        logger.info("🖱️  Right-click on table headers for navigation menu")
        
    except Exception as e:
        logger.error(f"Failed to integrate HeaderNavigationWidget: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the main application with HeaderNavigationWidget integration."""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("POEditor with Header Navigation")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("POEditor")
        app.setOrganizationDomain("poeditor.com")
        
        # Import resources after QApplication is created
        try:
            import resources_rc
        except ImportError:
            logger.warning("Resources not available - some icons may not display")

        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        logger.info("Starting POEditor with HeaderNavigationWidget integration")
        
        # Create main window
        window = MainAppWindow()
        
        # Integrate navigation header
        integrate_navigation_header(window)
        
        window.show()
        
        logger.info("Application started successfully")
        logger.info("HeaderNavigationWidget integration scheduled")
        
        # Run the application
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
