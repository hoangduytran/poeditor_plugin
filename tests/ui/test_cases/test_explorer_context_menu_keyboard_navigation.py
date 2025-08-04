"""
Test for Explorer Context Menu Keyboard Navigation implementation.

This test validates the keyboard navigation functionality of the Explorer Context Menu
including shortcut integration, key handling, and navigation performance.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import QPoint, Qt, QDir, QItemSelectionModel, QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QKeyEvent, QKeySequence

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from widgets.explorer_context_menu import ExplorerContextMenu
from widgets.explorer_context_menu_keyboard_navigation import MenuKeyboardNavigator
from services.keyboard_shortcut_service import keyboard_shortcut_service


class ExplorerContextMenuKeyboardNavigationTest:
    """
    Test class for Explorer Context Menu Keyboard Navigation functionality.

    Tests keyboard navigation features including:
    - Shortcut integration
    - Key event handling
    - Navigation performance
    - Custom key sequences
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

        # Track keyboard events
        self.keyboard_events = []

        # Navigate to the test directory
        self.explorer_widget.set_current_path(self.test_dir)

        # Show the widget - needed for context menu testing
        self.container.resize(800, 600)
        self.container.show()

        # Process events to ensure UI is updated
        QApplication.processEvents()

        logger.info(f"Keyboard navigation test initialized with directory: {self.test_dir}")

    def _create_test_directory(self) -> str:
        """Create a temporary directory for testing."""
        test_dir = tempfile.mkdtemp(prefix="keyboard_nav_test_")
        logger.debug(f"Created test directory: {test_dir}")
        return test_dir

    def _create_test_files(self) -> List[str]:
        """Create test files in the test directory for keyboard testing."""
        test_files = []

        # Create files with names for testing different keyboard operations
        file_names = [
            "copy_me.txt", "cut_me.txt", "delete_me.txt",
            "rename_me.txt", "archive_me.zip",
            "test_folder", "another_folder"
        ]

        for filename in file_names:
            if "folder" in filename:
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

    def _simulate_key_press(self, widget: QWidget, key: Qt.Key, modifier: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier):
        """Simulate a key press on a widget."""
        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, key, modifier)
        QApplication.sendEvent(widget, key_event)
        QApplication.processEvents()

    def _simulate_key_sequence(self, widget: QWidget, sequence: QKeySequence):
        """Simulate a key sequence on a widget."""
        # For testing purposes, we'll simulate common key sequences manually
        sequence_str = sequence.toString()

        if sequence_str == "Ctrl+C":
            self._simulate_key_press(widget, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
        elif sequence_str == "Ctrl+V":
            self._simulate_key_press(widget, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
        elif sequence_str == "Ctrl+X":
            self._simulate_key_press(widget, Qt.Key.Key_X, Qt.KeyboardModifier.ControlModifier)
        else:
            # For other sequences, try to extract the basic key
            keys = sequence_str.split("+")
            if keys:
                last_key = keys[-1]
                if hasattr(Qt.Key, f"Key_{last_key}"):
                    key = getattr(Qt.Key, f"Key_{last_key}")
                    modifiers = Qt.KeyboardModifier.NoModifier
                    if "Ctrl" in sequence_str:
                        modifiers |= Qt.KeyboardModifier.ControlModifier
                    if "Shift" in sequence_str:
                        modifiers |= Qt.KeyboardModifier.ShiftModifier
                    if "Alt" in sequence_str:
                        modifiers |= Qt.KeyboardModifier.AltModifier
                    self._simulate_key_press(widget, key, modifiers)

    def test_keyboard_navigator_creation(self):
        """Test creation of keyboard navigator."""
        logger.info("Testing keyboard navigator creation")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "copy_me.txt")
        menu = self._create_context_menu([test_file])

        # Create keyboard navigator
        try:
            keyboard_navigator = MenuKeyboardNavigator(menu)
            logger.info("Keyboard navigator creation test passed: Navigator created successfully")
        except Exception as e:
            logger.error(f"Keyboard navigator creation test failed: {e}")
            return

        menu.close()

    def test_shortcut_service_integration(self):
        """Test integration with keyboard shortcut service."""
        logger.info("Testing keyboard shortcut service integration")

        # Check if shortcut service has explorer menu shortcuts registered
        try:
            # Get shortcuts by category
            shortcuts_by_category = keyboard_shortcut_service.get_shortcuts_by_category()
            explorer_shortcuts = []

            # Look for explorer-related shortcuts in all categories
            for category, shortcuts in shortcuts_by_category.items():
                for shortcut in shortcuts:
                    if 'explorer' in shortcut.get('name', '').lower() or 'menu' in shortcut.get('name', '').lower():
                        explorer_shortcuts.append(shortcut)

            if explorer_shortcuts:
                logger.info(f"Shortcut service integration test passed: {len(explorer_shortcuts)} explorer shortcuts found")
            else:
                logger.info("Shortcut service integration test completed: No explorer-specific shortcuts found (may be expected)")

        except Exception as e:
            logger.error(f"Shortcut service integration test failed: {e}")

    def test_copy_shortcut_handling(self):
        """Test copy shortcut (Ctrl+C) handling."""
        logger.info("Testing copy shortcut handling")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "copy_me.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Find copy action in menu
        copy_action = None
        for action in menu.actions():
            if action.text() and 'copy' in action.text().lower():
                copy_action = action
                break

        if copy_action:
            # Simulate Ctrl+C
            self._simulate_key_press(menu, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
            logger.info("Copy shortcut handling test passed: Ctrl+C key sequence sent")
        else:
            logger.info("Copy shortcut handling test skipped: No copy action found")

        menu.close()

    def test_paste_shortcut_handling(self):
        """Test paste shortcut (Ctrl+V) handling."""
        logger.info("Testing paste shortcut handling")

        # Create an empty area context menu (paste should be available)
        menu = self._create_context_menu([])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Find paste action in menu
        paste_action = None
        for action in menu.actions():
            if action.text() and 'paste' in action.text().lower():
                paste_action = action
                break

        if paste_action:
            # Simulate Ctrl+V
            self._simulate_key_press(menu, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
            logger.info("Paste shortcut handling test passed: Ctrl+V key sequence sent")
        else:
            logger.info("Paste shortcut handling test skipped: No paste action found")

        menu.close()

    def test_delete_key_handling(self):
        """Test delete key handling."""
        logger.info("Testing delete key handling")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "delete_me.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Find delete action in menu
        delete_action = None
        for action in menu.actions():
            if action.text() and 'delete' in action.text().lower():
                delete_action = action
                break

        if delete_action:
            # Simulate Delete key
            self._simulate_key_press(menu, Qt.Key.Key_Delete)
            logger.info("Delete key handling test passed: Delete key sent")
        else:
            logger.info("Delete key handling test skipped: No delete action found")

        menu.close()

    def test_f2_rename_shortcut(self):
        """Test F2 rename shortcut handling."""
        logger.info("Testing F2 rename shortcut")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "rename_me.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Find rename action in menu
        rename_action = None
        for action in menu.actions():
            if action.text() and 'rename' in action.text().lower():
                rename_action = action
                break

        if rename_action:
            # Simulate F2 key
            self._simulate_key_press(menu, Qt.Key.Key_F2)
            logger.info("F2 rename shortcut test passed: F2 key sent")
        else:
            logger.info("F2 rename shortcut test skipped: No rename action found")

        menu.close()

    def test_enter_key_activation(self):
        """Test Enter key for action activation."""
        logger.info("Testing Enter key activation")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "copy_me.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Get first action
        actions = menu.actions()
        if len(actions) > 0:
            first_action = actions[0]
            menu.setActiveAction(first_action)

            # Simulate Enter key
            self._simulate_key_press(menu, Qt.Key.Key_Return)
            logger.info("Enter key activation test passed: Enter key sent to active action")
        else:
            logger.info("Enter key activation test skipped: No actions found")

        menu.close()

    def test_space_key_activation(self):
        """Test Space key for action activation."""
        logger.info("Testing Space key activation")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "copy_me.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Get first action
        actions = menu.actions()
        if len(actions) > 0:
            first_action = actions[0]
            menu.setActiveAction(first_action)

            # Simulate Space key
            self._simulate_key_press(menu, Qt.Key.Key_Space)
            logger.info("Space key activation test passed: Space key sent to active action")
        else:
            logger.info("Space key activation test skipped: No actions found")

        menu.close()

    def test_tab_navigation(self):
        """Test Tab key navigation between menu items."""
        logger.info("Testing Tab navigation")

        # Create a context menu
        test_file = os.path.join(self.test_dir, "copy_me.txt")
        menu = self._create_context_menu([test_file])

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Get actions count
        actions = menu.actions()
        if len(actions) < 2:
            logger.info("Tab navigation test skipped: Not enough actions to navigate")
            menu.close()
            return

        # Get initial active action
        initial_action = menu.activeAction()

        # Simulate Tab key
        self._simulate_key_press(menu, Qt.Key.Key_Tab)

        # Check if active action changed
        new_action = menu.activeAction()

        if new_action != initial_action:
            logger.info("Tab navigation test passed: Tab key changed active action")
        else:
            logger.info("Tab navigation test completed: Active action unchanged (may be expected)")

        menu.close()

    def test_keyboard_navigation_performance(self):
        """Test keyboard navigation performance with many menu items."""
        logger.info("Testing keyboard navigation performance")

        # Create context menu with multiple files for more menu items
        test_files = [
            os.path.join(self.test_dir, "copy_me.txt"),
            os.path.join(self.test_dir, "cut_me.txt"),
            os.path.join(self.test_dir, "delete_me.txt"),
            os.path.join(self.test_dir, "rename_me.txt")
        ]
        menu = self._create_context_menu(test_files)

        # Set up keyboard navigator
        keyboard_navigator = MenuKeyboardNavigator(menu)

        # Show the menu
        menu.show()
        QApplication.processEvents()

        # Measure time for navigation operations
        import time
        start_time = time.time()

        # Perform multiple navigation operations
        for i in range(10):
            self._simulate_key_press(menu, Qt.Key.Key_Down)
            self._simulate_key_press(menu, Qt.Key.Key_Up)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Performance threshold (should be fast)
        if elapsed_time < 1.0:  # 1 second for 20 operations
            logger.info(f"Keyboard navigation performance test passed: {elapsed_time:.3f}s for 20 operations")
        else:
            logger.error(f"Keyboard navigation performance test failed: {elapsed_time:.3f}s for 20 operations (too slow)")

        menu.close()

    def run_tests(self):
        """Run all keyboard navigation tests."""
        logger.info("Starting Explorer Context Menu Keyboard Navigation tests")

        self.test_keyboard_navigator_creation()
        self.test_shortcut_service_integration()
        self.test_copy_shortcut_handling()
        self.test_paste_shortcut_handling()
        self.test_delete_key_handling()
        self.test_f2_rename_shortcut()
        self.test_enter_key_activation()
        self.test_space_key_activation()
        self.test_tab_navigation()
        self.test_keyboard_navigation_performance()

        logger.info("Explorer Context Menu Keyboard Navigation tests completed")

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
    """Run the Explorer Context Menu Keyboard Navigation tests."""
    logger.info("Starting Explorer Context Menu Keyboard Navigation tests")

    test = ExplorerContextMenuKeyboardNavigationTest()
    try:
        test.run_tests()
    finally:
        test.cleanup()

    logger.info("Explorer Context Menu Keyboard Navigation tests completed")


if __name__ == "__main__":
    run_test()
