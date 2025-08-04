import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget,
                             QLabel, QWidget)
from PySide6.QtCore import Qt
from lg import logger

def debug_widget_style(widget, depth=0):
    """Debug helper to print widget hierarchy and styling"""
    indent = "  " * depth
    logger.info(f"{indent}=== Widget Debug ===")
    logger.info(f"{indent}Widget: {widget.__class__.__name__}")
    logger.info(f"{indent}ObjectName: {widget.objectName()}")

    # Extra debug info for QDockWidget
    if isinstance(widget, QDockWidget):
        logger.info(f"{indent}=== QDockWidget Specific Debug ===")
        logger.info(f"{indent}Title: {widget.windowTitle()}")
        logger.info(f"{indent}Features: {widget.features()}")
        logger.info(f"{indent}AllowedAreas: {widget.allowedAreas()}")

        # Find and inspect title bar widget and its children
        title_bar = None
        for child in widget.children():
            if isinstance(child, QWidget) and child.objectName() == "qt_dockwidget_titlebar":
                title_bar = child
                break

        if title_bar:
            logger.info(f"{indent}Title Bar Found: {title_bar.__class__.__name__}")
            logger.info(f"{indent}Title Bar Object Name: {title_bar.objectName()}")
            logger.info(f"{indent}Title Bar Style: {title_bar.styleSheet()}")
            logger.info(f"{indent}Title Bar BG Role: {title_bar.backgroundRole()}")
            logger.info(f"{indent}Title Bar FG Role: {title_bar.foregroundRole()}")

            # Check title bar's children (buttons, labels, etc)
            for idx, tchild in enumerate(title_bar.children()):
                if isinstance(tchild, QWidget):
                    logger.info(f"{indent}  Title Bar Child [{idx}]: {tchild.__class__.__name__}")
                    logger.info(f"{indent}  - Object Name: {tchild.objectName()}")
                    logger.info(f"{indent}  - Style Sheet: {tchild.styleSheet()}")
                    logger.info(f"{indent}  - Is Visible: {tchild.isVisible()}")
                    tchild_bg = tchild.palette().color(tchild.backgroundRole())
                    logger.info(f"{indent}  - BG Color: {tchild_bg.name()} (RGB: {tchild_bg.red()},{tchild_bg.green()},{tchild_bg.blue()})")

    # Continue with regular widget debugging
    logger.info(f"{indent}Geometry: {widget.geometry()}")
    logger.info(f"{indent}IsVisible: {widget.isVisible()}")
    logger.info(f"{indent}StyleSheet: {widget.styleSheet()}")
    bg_color = widget.palette().color(widget.backgroundRole())
    fg_color = widget.palette().color(widget.foregroundRole())
    logger.info(f"{indent}Background: {bg_color.name()} (RGB: {bg_color.red()},{bg_color.green()},{bg_color.blue()})")
    logger.info(f"{indent}WA_StyledBackground: {widget.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)}")

    # Check all children
    for child in widget.children():
        if isinstance(child, QWidget):
            debug_widget_style(child, depth + 1)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_window")

        # Create a simple dock widget
        dock = QDockWidget("Test Dock", self)
        dock.setObjectName("test_dock")

        # Configure the dock widget to properly handle styling
        title_bar = None
        for child in dock.children():
            if isinstance(child, QWidget) and child.objectName() == "qt_dockwidget_titlebar":
                title_bar = child
                break

        if title_bar:
            # Enable stylesheet processing
            title_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            # Set proper background role
            title_bar.setAutoFillBackground(True)

            # Debug the title bar configuration
            logger.info("Title bar configuration:")
            logger.info(f"- WA_StyledBackground: {title_bar.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)}")
            logger.info(f"- AutoFillBackground: {title_bar.autoFillBackground()}")

        # Add some content
        content = QLabel("Dock Content")
        dock.setWidget(content)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        # Debug styling after show
        self.show()
        logger.info("\n=== Initial Style Debug ===")
        debug_widget_style(dock)

def main():
    app = QApplication(sys.argv)

    # Load dark theme
    theme_path = Path(__file__).parent.parent / "themes" / "css" / "dark_theme.css"
    with open(theme_path) as f:
        app.setStyleSheet(f.read())

    window = TestWindow()
    window.resize(800, 600)
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
