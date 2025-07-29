"""
Integration Guide: Adding HeaderNavigationWidget to main.py

This guide shows how to integrate the HeaderNavigationWidget into the main POEditor application.
"""

# Step 1: Import the HeaderNavigationWidget in the main application
from widgets.explorer.explorer_header_bar import HeaderNavigationWidget

# Step 2: In the enhanced explorer panel, replace the standard header
def integrate_header_navigation(explorer_panel):
    """
    Integrate HeaderNavigationWidget into an existing explorer panel.
    
    Args:
        explorer_panel: The explorer panel containing a file view
    """
    # Get the file view (QTreeView)
    file_view = explorer_panel.explorer_widget.file_view
    
    # Create navigation services
    from services.navigation_service import NavigationService
    from services.navigation_history_service import NavigationHistoryService
    from services.location_manager import LocationManager
    from services.path_completion_service import PathCompletionService
    
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
    from PySide6.QtCore import Qt
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
    
    return nav_header

# Step 3: In main_app_window.py, modify the explorer panel setup
def setup_enhanced_explorer_with_navigation(main_window):
    """
    Example of how to set up enhanced explorer with navigation in main_app_window.py
    """
    # Find the explorer panel
    explorer_panel = main_window.sidebar_manager.get_panel('explorer')
    
    if explorer_panel and hasattr(explorer_panel, 'explorer_widget'):
        # Integrate navigation header
        nav_header = integrate_header_navigation(explorer_panel)
        
        # Store reference for later use
        main_window.explorer_nav_header = nav_header
        
        print("✅ HeaderNavigationWidget integrated into explorer!")
        print("🖱️  Right-click on table headers for navigation menu")

# Step 4: Usage in main.py
"""
To integrate into main.py, add this to the MainAppWindow.__init__ method:

    def __init__(self):
        super().__init__()
        # ... existing initialization code ...
        
        # After all plugins are loaded and panels are set up
        self.setup_enhanced_explorer_with_navigation()
        
    def setup_enhanced_explorer_with_navigation(self):
        \"\"\"Set up the enhanced explorer with navigation header.\"\"\"
        try:
            setup_enhanced_explorer_with_navigation(self)
        except Exception as e:
            logger.error(f"Failed to setup explorer navigation: {e}")
"""

# Example of how the integration would look in a real MainAppWindow:
"""
class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Existing initialization...
        self.setup_ui()
        self.setup_theme_system()
        self.setup_plugin_system()
        self.setup_sidebar_buttons()
        self.load_plugins()
        
        # NEW: Add navigation header integration
        self.setup_explorer_navigation()
        
        self.restore_settings()
        
    def setup_explorer_navigation(self):
        \"\"\"Integrate HeaderNavigationWidget into the explorer panel.\"\"\"
        try:
            # Wait for explorer panel to be available
            QTimer.singleShot(100, self._integrate_explorer_navigation)
        except Exception as e:
            logger.error(f"Failed to setup explorer navigation: {e}")
            
    def _integrate_explorer_navigation(self):
        \"\"\"Perform the actual integration after panels are loaded.\"\"\"
        setup_enhanced_explorer_with_navigation(self)
"""

print("📖 Integration guide created!")
print("📁 See this file for step-by-step instructions")
print("🚀 The HeaderNavigationWidget is ready for integration into main.py")
