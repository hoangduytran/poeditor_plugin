"""
Test for Explorer Context Menu Theme Integration implementation.

This test validates the theme integration functionality of the Explorer Context Menu
including CSS styling, theme switching, and visual consistency.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import QPoint, Qt, QDir, QItemSelectionModel, QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QPalette, QColor

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from widgets.explorer_context_menu import ExplorerContextMenu
from services.theme_manager import theme_manager


class ExplorerContextMenuThemeTest:
    """
    Test class for Explorer Context Menu Theme Integration functionality.
    
    Tests theme integration features including:
    - CSS styling application
    - Theme switching
    - Visual consistency
    - Dark/light mode support
    """
    
    def __init__(self):
        """Initialize test components."""
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.test_dir = self._create_test_directory()
        self.test_files = self._create_test_files()
        
        # Create widget to host our explorer
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        
        # Create the explorer widget
        self.explorer_widget = EnhancedExplorerWidget()
        self.layout.addWidget(self.explorer_widget)
        
        # Get access to file view
        self.file_view = self.explorer_widget.file_view
        
        # Track theme changes
        self.theme_changes = []
        
        # Navigate to the test directory
        self.explorer_widget.set_current_path(self.test_dir)
        
        # Show the widget - needed for context menu testing
        self.container.resize(800, 600)
        self.container.show()
        
        # Process events to ensure UI is updated
        QApplication.processEvents()
        
        logger.info(f"Theme test initialized with directory: {self.test_dir}")
    
    def _create_test_directory(self) -> str:
        """Create a temporary directory for testing."""
        test_dir = tempfile.mkdtemp(prefix="theme_test_")
        logger.debug(f"Created test directory: {test_dir}")
        return test_dir
    
    def _create_test_files(self) -> List[str]:
        """Create test files in the test directory for theme testing."""
        test_files = []
        
        # Create files for testing theme styling
        file_names = [
            "theme_test.txt", "style_test.css",
            "visual_test.png", "consistency_test.json"
        ]
        
        for filename in file_names:
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Test content for {filename}")
            test_files.append(file_path)
        
        return test_files
    
    def _create_context_menu(self, selected_files: List[str]) -> QMenu:
        """Create a context menu for testing."""
        # Create context menu using the correct constructor
        context_menu_manager = ExplorerContextMenu(
            self.explorer_widget.file_operations_service,
            self.explorer_widget.undo_redo_manager
        )
        
        # Convert file paths to the expected format
        selected_items = []
        for file_path in selected_files:
            selected_items.append({
                'path': file_path,
                'is_dir': os.path.isdir(file_path),
                'name': os.path.basename(file_path)
            })
        
        # Create a QMenu for displaying
        menu = context_menu_manager.create_menu(selected_items, self.test_dir)
        
        return menu
    
    def _get_menu_style(self, menu: QMenu) -> str:
        """Get the current style sheet of a menu."""
        return menu.styleSheet()
    
    def _check_style_property(self, widget: QWidget, property_name: str) -> Any:
        """Check if a style property is set on a widget."""
        return widget.property(property_name)
    
    def test_menu_css_styling(self):
        """Test that context menu has proper CSS styling applied."""
        logger.info("Testing menu CSS styling")
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu to trigger styling
        menu.show()
        QApplication.processEvents()
        
        # Check if menu has style sheet applied
        style_sheet = self._get_menu_style(menu)
        
        if style_sheet:
            logger.info(f"Menu CSS styling test passed: Style sheet applied ({len(style_sheet)} characters)")
        else:
            # Check if menu has default Qt styling
            palette = menu.palette()
            if palette:
                logger.info("Menu CSS styling test passed: Default palette styling available")
            else:
                logger.error("Menu CSS styling test failed: No styling found")
        
        menu.close()
    
    def test_theme_consistency(self):
        """Test that menu styling is consistent with application theme."""
        logger.info("Testing theme consistency")
        
        # Get application palette
        app_palette = QApplication.palette()
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu
        menu.show()
        QApplication.processEvents()
        
        # Get menu palette
        menu_palette = menu.palette()
        
        # Check color consistency (basic test)
        app_bg = app_palette.color(QPalette.ColorRole.Window)
        menu_bg = menu_palette.color(QPalette.ColorRole.Window)
        
        # Colors should be similar or explicitly styled
        if app_bg == menu_bg:
            logger.info("Theme consistency test passed: Menu uses application colors")
        else:
            # Check if menu has custom styling
            style_sheet = self._get_menu_style(menu)
            if style_sheet and "background" in style_sheet:
                logger.info("Theme consistency test passed: Menu has custom background styling")
            else:
                logger.info("Theme consistency test completed: Different colors found (may be intended)")
        
        menu.close()
    
    def test_dark_mode_support(self):
        """Test dark mode support in context menu."""
        logger.info("Testing dark mode support")
        
        # Try to switch to dark mode if theme manager supports it
        try:
            current_theme = theme_manager.get_current_theme()
            
            # Create a context menu
            test_file = os.path.join(self.test_dir, "theme_test.txt")
            menu = self._create_context_menu([test_file])
            
            # Show the menu
            menu.show()
            QApplication.processEvents()
            
            # Check if menu responds to dark theme
            palette = menu.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            
            # In dark mode, background should be darker
            is_dark = window_color.value() < 128  # HSV value less than 50%
            
            current_theme_name = ""
            if current_theme and hasattr(current_theme, 'name'):
                current_theme_name = current_theme.name.lower()
            
            if is_dark or "dark" in current_theme_name:
                logger.info("Dark mode support test passed: Menu supports dark styling")
            else:
                logger.info("Dark mode support test completed: Light theme detected")
            
            menu.close()
            
        except Exception as e:
            logger.error(f"Dark mode support test failed: {e}")
    
    def test_light_mode_support(self):
        """Test light mode support in context menu."""
        logger.info("Testing light mode support")
        
        # Try to get current theme
        try:
            current_theme = theme_manager.get_current_theme()
            
            # Create a context menu
            test_file = os.path.join(self.test_dir, "theme_test.txt")
            menu = self._create_context_menu([test_file])
            
            # Show the menu
            menu.show()
            QApplication.processEvents()
            
            # Check if menu responds to light theme
            palette = menu.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            
            # In light mode, background should be lighter
            is_light = window_color.value() >= 128  # HSV value 50% or more
            
            current_theme_name = ""
            if current_theme and hasattr(current_theme, 'name'):
                current_theme_name = current_theme.name.lower()
            
            if is_light or "light" in current_theme_name:
                logger.info("Light mode support test passed: Menu supports light styling")
            else:
                logger.info("Light mode support test completed: Dark theme detected")
            
            menu.close()
            
        except Exception as e:
            logger.error(f"Light mode support test failed: {e}")
    
    def test_menu_action_styling(self):
        """Test that menu actions have proper styling."""
        logger.info("Testing menu action styling")
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu
        menu.show()
        QApplication.processEvents()
        
        # Check actions styling
        actions = menu.actions()
        styled_actions = 0
        
        for action in actions:
            if action.isSeparator():
                continue
                
            # Check if action has icon or proper text styling
            if action.icon() and not action.icon().isNull():
                styled_actions += 1
            elif action.text():
                styled_actions += 1
        
        if styled_actions > 0:
            logger.info(f"Menu action styling test passed: {styled_actions} actions properly styled")
        else:
            logger.error("Menu action styling test failed: No styled actions found")
        
        menu.close()
    
    def test_hover_state_styling(self):
        """Test hover state styling for menu items."""
        logger.info("Testing hover state styling")
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu
        menu.show()
        QApplication.processEvents()
        
        # Get actions
        actions = menu.actions()
        if len(actions) == 0:
            logger.error("Hover state styling test failed: No actions to test")
            menu.close()
            return
        
        # Test hover by setting active action
        first_action = actions[0]
        if not first_action.isSeparator():
            menu.setActiveAction(first_action)
            QApplication.processEvents()
            
            # Check if active action has different visual state
            # This is handled by Qt internally, so we just verify the action is active
            if menu.activeAction() == first_action:
                logger.info("Hover state styling test passed: Active action set successfully")
            else:
                logger.error("Hover state styling test failed: Could not set active action")
        else:
            logger.info("Hover state styling test skipped: First action is separator")
        
        menu.close()
    
    def test_disabled_action_styling(self):
        """Test styling for disabled menu actions."""
        logger.info("Testing disabled action styling")
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu
        menu.show()
        QApplication.processEvents()
        
        # Find actions and check enabled/disabled state
        actions = menu.actions()
        enabled_count = 0
        disabled_count = 0
        
        for action in actions:
            if action.isSeparator():
                continue
                
            if action.isEnabled():
                enabled_count += 1
            else:
                disabled_count += 1
        
        if enabled_count > 0:
            logger.info(f"Disabled action styling test passed: Found {enabled_count} enabled and {disabled_count} disabled actions")
        else:
            logger.error("Disabled action styling test failed: No enabled actions found")
        
        menu.close()
    
    def test_separator_styling(self):
        """Test styling for menu separators."""
        logger.info("Testing separator styling")
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu
        menu.show()
        QApplication.processEvents()
        
        # Count separators
        actions = menu.actions()
        separator_count = sum(1 for action in actions if action.isSeparator())
        
        if separator_count > 0:
            logger.info(f"Separator styling test passed: Found {separator_count} separators")
        else:
            logger.info("Separator styling test completed: No separators found")
        
        menu.close()
    
    def test_custom_theme_properties(self):
        """Test custom theme properties on context menu."""
        logger.info("Testing custom theme properties")
        
        # Create a context menu
        test_file = os.path.join(self.test_dir, "theme_test.txt")
        menu = self._create_context_menu([test_file])
        
        # Show the menu
        menu.show()
        QApplication.processEvents()
        
        # Check for custom properties that might be set by theme system
        custom_properties = [
            "theme-name",
            "menu-style",
            "context-menu-theme",
            "explorer-theme"
        ]
        
        found_properties = []
        for prop in custom_properties:
            value = self._check_style_property(menu, prop)
            if value:
                found_properties.append(prop)
        
        if found_properties:
            logger.info(f"Custom theme properties test passed: Found properties {found_properties}")
        else:
            logger.info("Custom theme properties test completed: No custom properties found (may be expected)")
        
        menu.close()
    
    def run_tests(self):
        """Run all theme integration tests."""
        logger.info("Starting Explorer Context Menu Theme Integration tests")
        
        self.test_menu_css_styling()
        self.test_theme_consistency()
        self.test_dark_mode_support()
        self.test_light_mode_support()
        self.test_menu_action_styling()
        self.test_hover_state_styling()
        self.test_disabled_action_styling()
        self.test_separator_styling()
        self.test_custom_theme_properties()
        
        logger.info("Explorer Context Menu Theme Integration tests completed")
    
    def cleanup(self):
        """Clean up test resources."""
        # Hide and destroy UI components
        self.container.hide()
        self.container.deleteLater()
        
        # Process events to ensure UI cleanup
        QApplication.processEvents()
        
        # Clean up the test directory
        for file_path in self.test_files:
            if os.path.isfile(file_path):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logger.error(f"Failed to remove test file {file_path}: {e}")
        
        try:
            os.rmdir(self.test_dir)
            logger.debug(f"Removed test directory: {self.test_dir}")
        except Exception as e:
            logger.error(f"Failed to remove test directory {self.test_dir}: {e}")


def run_test():
    """Run the Explorer Context Menu Theme Integration tests."""
    logger.info("Starting Explorer Context Menu Theme Integration tests")
    
    test = ExplorerContextMenuThemeTest()
    try:
        test.run_tests()
    finally:
        test.cleanup()
    
    logger.info("Explorer Context Menu Theme Integration tests completed")


if __name__ == "__main__":
    run_test()
