"""
Test script to debug the styling of SidebarDockWidget title bar in dark theme.
This script creates a minimal application to isolate and debug the styling issue.
"""

import sys
import os
from pathlib import Path

# Fix the path to point to the actual project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QDockWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

# Import the widget we want to test
from widgets.sidebar_dock_widget import SidebarDockWidget
from lg import logger
# Set up basic logging

class SimpleSidebarContent(QWidget):
    """A simple widget to serve as sidebar content"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Sidebar Content"))
        layout.addWidget(QPushButton("Test Button"))


class TestWindow(QMainWindow):
    """Test window with sidebar dock widget"""
    def __init__(self):
        super().__init__()
        self.setObjectName("main_window")
        self.setWindowTitle("Sidebar Styling Test")
        self.resize(800, 600)
        
        # Create a central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Central Widget"))
        
        # Create sidebar content
        sidebar_content = SimpleSidebarContent()
        
        logger.info("=== Creating SidebarDockWidget ===")
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            logger.info("Before creation - Application stylesheet length: "
                       f"{len(app.styleSheet())}")
        else:
            logger.info("Before creation - QApplication instance not available")
        
        # Create the sidebar dock widget
        self.sidebar = SidebarDockWidget(sidebar_content, self)
        
        logger.info(f"Created SidebarDockWidget with parent: {type(self).__name__}")
        logger.info(f"SidebarDockWidget features: {self.sidebar.features()}")
        
        # Log widget hierarchy immediately after creation
        logger.info("Initial widget hierarchy:")
        self._log_widget_hierarchy(self.sidebar)
        
        # Add the sidebar to the main window
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        logger.info("Added SidebarDockWidget to main window")
        
        # Log hierarchy after adding to main window
        logger.info("Widget hierarchy after adding to main window:")
        self._log_widget_hierarchy(self.sidebar)
        
        # Debug widget styles
        self.debug_styles()
        
        # Add a button to trigger style refresh and debugging
        refresh_button = QPushButton("Refresh & Debug Styles")
        refresh_button.clicked.connect(self.debug_styles)
        layout.addWidget(refresh_button)

    def _log_widget_hierarchy(self, widget, depth=0):
        """Log detailed widget hierarchy with styling information"""
        indent = "  " * depth
        logger.info(f"{indent}Widget: {widget.__class__.__name__}")
        logger.info(f"{indent}ObjectName: {widget.objectName()}")
        logger.info(f"{indent}StyleSheet: {widget.styleSheet()}")
        logger.info(f"{indent}Background Role: {widget.backgroundRole()}")
        logger.info(f"{indent}Auto Fill Background: {widget.autoFillBackground()}")
        logger.info(f"{indent}WA_StyledBackground: {widget.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)}")
        
        # Get effective style
        if hasattr(widget, 'style'):
            style = widget.style()
            logger.info(f"{indent}Style class: {style.__class__.__name__}")
        
        # Get color information
        palette = widget.palette()
        bg_color = palette.color(widget.backgroundRole())
        fg_color = palette.color(widget.foregroundRole())
        logger.info(f"{indent}Background color: {bg_color.name()} (RGB: {bg_color.red()},{bg_color.green()},{bg_color.blue()})")
        logger.info(f"{indent}Foreground color: {fg_color.name()}")
        
        # Check parent relationship
        if widget.parent():
            logger.info(f"{indent}Parent: {type(widget.parent()).__name__}")
        
        # Log children
        for child in widget.children():
            if isinstance(child, QWidget):
                self._log_widget_hierarchy(child, depth + 1)

    def debug_styles(self):
        """Debug the styles applied to the sidebar dock widget title bar"""
        logger.info("\n=== DEBUGGING SIDEBAR DOCK WIDGET STYLING ===")
        logger.info("Current application stylesheet sections:")
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            stylesheet = app.styleSheet()
            # Log relevant style sections
            for line in stylesheet.split('\n'):
                if any(key in line for key in ['QDockWidget', 'title', 'background']):
                    logger.info(f"Style rule: {line.strip()}")
        
        # Try to find title bar widget more comprehensively
        title_bar = None

        # Method 1: Look for qt_dockwidget_titlebar
        for child in self.sidebar.children():
            if isinstance(child, QWidget) and child.objectName() == "qt_dockwidget_titlebar":
                title_bar = child
                break

        # Method 2: If not found, look for any child that might be the title bar
        if not title_bar:
            for child in self.sidebar.children():
                if isinstance(child, QWidget):
                    # Check if this widget looks like a title bar
                    if hasattr(child, 'height') and child.height() > 0 and child.height() < 50:
                        logger.info(f"Potential title bar found: {type(child).__name__} with objectName: '{child.objectName()}'")
                        title_bar = child
                        break

        if title_bar:
            logger.info("\n=== Title Bar Widget State ===")
            logger.info(f"Title bar widget found: {type(title_bar).__name__}")
            logger.info(f"Style sheet: {title_bar.styleSheet()}")
            logger.info(f"Property 'class': {title_bar.property('class')}")
            logger.info(f"Auto fill background: {title_bar.autoFillBackground()}")
            logger.info(f"WA_StyledBackground: {title_bar.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)}")
            
            # Force apply dark styling directly to the title bar
            logger.info("Attempting to force dark styling on title bar...")
            title_bar.setAutoFillBackground(True)
            title_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            title_bar.setStyleSheet("""
                background-color: #252526;
                color: #cccccc;
                padding: 4px;
                padding-left: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            """)

            # Log complete widget hierarchy from title bar
            logger.info("\nTitle bar widget hierarchy:")
            self._log_widget_hierarchy(title_bar)
            
            # Check application stylesheet for QDockWidget title styling
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                app_stylesheet = app.styleSheet()
                
                # Print relevant sections of the stylesheet
                if "QDockWidget" in app_stylesheet:
                    logger.info("Found QDockWidget styling in application stylesheet")
                    lines = app_stylesheet.split('\n')
                    dock_style_lines = []
                    in_dock_rule = False
                    for line in lines:
                        if "QDockWidget" in line:
                            in_dock_rule = True
                            dock_style_lines.append(line)
                        elif in_dock_rule and "}" in line:
                            dock_style_lines.append(line)
                            in_dock_rule = False
                        elif in_dock_rule:
                            dock_style_lines.append(line)
                    
                    for line in dock_style_lines:
                        logger.info(f"STYLE: {line.strip()}")
                else:
                    logger.info("No QDockWidget styling found in application stylesheet")
        else:
            logger.info("Could not find the title bar widget!")

            # Force apply styling directly to the dock widget itself
            logger.info("Attempting to style through the dock widget...")
            self.sidebar.setAutoFillBackground(True)
            self.sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

            # Apply more specific styling with !important equivalent (higher specificity)
            self.sidebar.setStyleSheet("""
                QDockWidget#SidebarDockWidget {
                    background-color: #252526;
                    color: #cccccc;
                    border: 1px solid #464647;
                }
                QDockWidget#SidebarDockWidget::title {
                    background-color: #252526;
                    color: #cccccc;
                    padding: 4px;
                    padding-left: 8px;
                    text-align: left;
                    border: none;
                    font-weight: bold;
                    font-size: 11px;
                    letter-spacing: 1px;
                }
            """)

            # Try to force a style update
            self.sidebar.style().unpolish(self.sidebar)
            self.sidebar.style().polish(self.sidebar)
            self.sidebar.update()

        logger.info("=== END DEBUGGING ===\n")


def load_dark_theme():
    """Load the dark theme CSS and dock widget CSS"""
    css_content = ""

    # Load main dark theme CSS
    dark_theme_path = project_root / "themes" / "css" / "dark_theme.css"
    if dark_theme_path.exists():
        with open(dark_theme_path, 'r') as f:
            css_content = f.read()
        logger.info("Dark theme CSS loaded successfully")
    else:
        logger.error(f"Dark theme CSS not found at {dark_theme_path}")

    # Load dock widget specific CSS
    dock_widget_path = project_root / "themes" / "css" / "dock_widget.css"
    if dock_widget_path.exists():
        with open(dock_widget_path, 'r') as f:
            css_content += "\n" + f.read()
        logger.info("Dock widget CSS loaded successfully")
    else:
        logger.error(f"Dock widget CSS not found at {dock_widget_path}")

    return css_content


def run_test():
    """Run the test application"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    dark_theme_css = load_dark_theme()
    if dark_theme_css:
        logger.info("Dark theme CSS loaded successfully")
        app.setStyleSheet(dark_theme_css)
    else:
        logger.warning("Failed to load dark theme CSS")
    
    # Create and show the test window
    window = TestWindow()
    window.show()
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_test())
