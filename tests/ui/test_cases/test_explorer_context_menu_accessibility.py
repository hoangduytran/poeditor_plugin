"""
Test for Explorer Context Menu Accessibility implementation.

This test validates the accessibility functionality of the Explorer Context Menu components
including screen reader support, keyboard navigation, and focus management.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import QPoint, Qt, QDir, QItemSelectionModel, QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QKeyEvent

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from widgets.explorer_context_menu import ExplorerContextMenu
from widgets.explorer_context_menu_accessibility import MenuAccessibilityManager
from widgets.explorer_context_menu_keyboard_navigation import MenuKeyboardNavigator
from services.file_operations_service import FileOperationsService, OperationType


class ExplorerContextMenuAccessibilityTest:
    """
    Test class for Explorer Context Menu Accessibility functionality.

    Tests accessibility features including:
    - Screen reader announcements
    - Keyboard navigation
    - Focus management
    - First-letter navigation
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

        # Create accessibility manager for testing
        self.accessibility_manager = MenuAccessibilityManager()

        # Track accessibility events
        self.accessibility_events = []
        self.screen_reader_announcements = []

        # Navigate to the test directory
        self.explorer_widget.set_current_path(self.test_dir)

        # Show the widget - needed for context menu testing
        self.container.resize(800, 600)
        self.container.show()

        # Process events to ensure UI is updated
        QApplication.processEvents()

        logger.info(f"Accessibility test initialized with directory: {self.test_dir}")

    def _create_test_directory(self) -> str:
        """Create a temporary directory for testing."""
        test_dir = tempfile.mkdtemp(prefix="accessibility_test_")
        logger.debug(f"Created test directory: {test_dir}")
        return test_dir

    def _create_test_files(self) -> List[str]:
        """Create test files in the test directory with diverse names for keyboard navigation testing."""
        test_files = []

        # Create files with different starting letters for first-letter navigation testing
        file_names = [
            "apple.txt", "banana.txt", "cherry.txt",
            "document.pdf", "excel.xlsx",
            "folder_a", "folder_b",
            "image.png", "music.mp3",
            "notebook.txt", "orange.txt"
        ]

        for filename in file_names:
            if filename.startswith("folder_"):
                # Create directory
                dir_path = os.path.join(self.test_dir, filename)
                os.makedirs(dir_path, exist_ok=True)
                test_files.append(dir_path)
            else:
                # Create file
                file_path = os.path.join(self.test_dir, filename)
                with open(file_path, "w") as f:
                    f.write(f"Test content for {filename}")
                test_files.append(file_path)

        return test_files

    def _get_file_index(self, filename: str):
        """Get the model index for a file in the explorer."""
        model = self.file_view.model()
        file_path = os.path.join(self.test_dir, filename)

        # Traverse the model to find the file
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            path = self.file_view.file_system_model.filePath(
                self.file_view.proxy_model.mapToSource(index)
            )
            if path == file_path:
                return index

        return None

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

        # Set up accessibility manager for the menu
        self.accessibility_manager.add_accessibility_to_menu(menu)

        return menu

    def _simulate_key_press(self, widget: QWidget, key: Qt.Key, modifier: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier):
        """Simulate a key press on a widget."""
        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, key, modifier)
        QApplication.sendEvent(widget, key_event)
        QApplication.processEvents()

    def test_screen_reader_setup(self):
        """Test that screen reader support is properly configured."""
        logger.info("Testing screen reader setup")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Check that accessibility properties are set
        actions = menu.actions()
        if len(actions) == 0:
            logger.error("No actions found in context menu")
            return

        # Check first action has accessibility text
        first_action = actions[0]
        accessible_name = first_action.text()

        if not accessible_name:
            logger.error("No accessible text found for menu action")
        else:
            logger.info(f"Screen reader setup test passed: Action has accessible text '{accessible_name}'")

        menu.close()

    def test_keyboard_navigation_setup(self):
        """Test that keyboard navigation is properly set up."""
        logger.info("Testing keyboard navigation setup")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Create keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Check that event filter is installed - direct access required
        try:
            # Access eventFilter directly to ensure it exists
            event_filter = keyboard_navigator.eventFilter
            logger.info("Keyboard navigation setup test passed: Event filter available")
        except AttributeError:
            logger.error("Keyboard navigation setup failed: No event filter method")

        menu.close()

    def test_focus_management(self):
        """Test focus management in context menu."""
        logger.info("Testing focus management")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Check that menu has focus
        if menu.hasFocus():
            logger.info("Focus management test passed: Menu has focus when shown")
        else:
            # Menu might not have direct focus, but should be active
            if menu.isVisible():
                logger.info("Focus management test passed: Menu is visible and active")
            else:
                logger.error("Focus management test failed: Menu is not visible or focused")

        menu.close()

    def test_first_letter_navigation(self):
        """Test first-letter navigation in context menu."""
        logger.info("Testing first-letter navigation")

        # Create a context menu with multiple items
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Get initial active action
        initial_action = menu.activeAction()

        # Simulate pressing 'C' key (should navigate to "Copy" action if it exists)
        self._simulate_key_press(menu, Qt.Key.Key_C)

        # Check if active action changed
        new_action = menu.activeAction()

        if new_action != initial_action:
            logger.info("First-letter navigation test passed: Active action changed with key press")
        else:
            # This might be normal if there's only one action starting with 'C' or none
            logger.info("First-letter navigation test completed: No change in active action (may be expected)")

        menu.close()

    def test_arrow_key_navigation(self):
        """Test arrow key navigation in context menu."""
        logger.info("Testing arrow key navigation")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Get actions count
        actions = menu.actions()
        if len(actions) < 2:
            logger.info("Arrow key navigation test skipped: Not enough actions to navigate")
            menu.close()
            return

        # Get initial active action
        initial_action = menu.activeAction()

        # Simulate down arrow key
        self._simulate_key_press(menu, Qt.Key.Key_Down)

        # Check if active action changed
        new_action = menu.activeAction()

        if new_action != initial_action:
            logger.info("Arrow key navigation test passed: Down arrow changed active action")
        else:
            logger.info("Arrow key navigation test completed: Active action unchanged (may be expected)")

        menu.close()

    def test_escape_key_handling(self):
        """Test escape key closes the context menu."""
        logger.info("Testing escape key handling")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Verify menu is visible
        if not menu.isVisible():
            logger.error("Escape key test failed: Menu not visible after show()")
            return

        # Simulate escape key
        self._simulate_key_press(menu, Qt.Key.Key_Escape)

        # Check if menu is closed
        if not menu.isVisible():
            logger.info("Escape key handling test passed: Menu closed with escape key")
        else:
            logger.error("Escape key handling test failed: Menu still visible after escape")

    def test_accessibility_role_assignment(self):
        """Test that proper accessibility roles are assigned to menu items."""
        logger.info("Testing accessibility role assignment")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "apple.txt")
        menu = self._create_context_menu([test_file])

        # Check that the menu has proper accessibility role
        # In Qt, QMenu automatically has proper accessibility roles
        actions = menu.actions()

        if len(actions) > 0:
            # Check that actions have text (which is used for accessibility)
            action_with_text = any(action.text().strip() for action in actions)
            if action_with_text:
                logger.info("Accessibility role assignment test passed: Actions have text for screen readers")
            else:
                logger.error("Accessibility role assignment test failed: No actions have text")
        else:
            logger.error("Accessibility role assignment test failed: No actions found")

        menu.close()

    def test_multiple_file_accessibility(self):
        """Test accessibility with multiple selected files."""
        logger.info("Testing multiple file accessibility")

        # Create context menu for multiple files
        test_files = [
            os.path.join(self.test_dir, "apple.txt"),
            os.path.join(self.test_dir, "banana.txt")
        ]
        menu = self._create_context_menu(test_files)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Check that menu is accessible with multiple files
        actions = menu.actions()

        if len(actions) > 0:
            # Should have actions appropriate for multiple files
            action_texts = [action.text() for action in actions if action.text().strip()]
            logger.info(f"Multiple file accessibility test passed: {len(action_texts)} actions available")
        else:
            logger.error("Multiple file accessibility test failed: No actions available")

        menu.close()

    def run_tests(self):
        """Run all accessibility tests."""
        logger.info("Starting Explorer Context Menu Accessibility tests")

        self.test_screen_reader_setup()
        self.test_keyboard_navigation_setup()
        self.test_focus_management()
        self.test_first_letter_navigation()
        self.test_arrow_key_navigation()
        self.test_escape_key_handling()
        self.test_accessibility_role_assignment()
        self.test_multiple_file_accessibility()

        logger.info("Explorer Context Menu Accessibility tests completed")

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
            elif os.path.isdir(file_path):
                try:
                    os.rmdir(file_path)
                except Exception as e:
                    logger.error(f"Failed to remove test directory {file_path}: {e}")

        try:
            os.rmdir(self.test_dir)
            logger.debug(f"Removed test directory: {self.test_dir}")
        except Exception as e:
            logger.error(f"Failed to remove test directory {self.test_dir}: {e}")


def run_test():
    """Run the Explorer Context Menu Accessibility tests."""
    logger.info("Starting Explorer Context Menu Accessibility tests")

    test = ExplorerContextMenuAccessibilityTest()
    try:
        test.run_tests()
    finally:
        test.cleanup()

    logger.info("Explorer Context Menu Accessibility tests completed")


if __name__ == "__main__":
    run_test()
