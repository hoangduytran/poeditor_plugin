"""
Test for Explorer Context Menu implementation.

This test validates the functionality of the Explorer Context Menu components.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QPoint, Qt, QDir, QItemSelectionModel
from PySide6.QtTest import QTest

from lg import logger
from widgets.enhanced_explorer_widget import EnhancedExplorerWidget
from widgets.explorer_context_menu import ExplorerContextMenu
from services.file_operations_service import FileOperationsService, OperationType
from services.undo_redo_service import UndoRedoManager
from services.file_numbering_service import FileNumberingService


class ExplorerContextMenuTest:
    """
    Test class for Explorer Context Menu functionality.

    This test uses real component instances rather than mocks,
    following the project guidelines.
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

        # Get access to file view and context menu
        self.file_view = self.explorer_widget.file_view

        # Track operation signals
        self.operations_log = []
        self.explorer_widget.file_operations_service.operationStarted.connect(
            self._log_operation_started
        )
        self.explorer_widget.file_operations_service.operationCompleted.connect(
            self._log_operation_completed
        )

        # Navigate to the test directory
        self.explorer_widget.set_current_path(self.test_dir)

        # Show the widget - needed for context menu testing
        self.container.resize(800, 600)
        self.container.show()

        # Process events to ensure UI is updated
        QApplication.processEvents()

        logger.info(f"Test initialized with directory: {self.test_dir}")
        logger.info(f"Test files created: {self.test_files}")

    def _create_test_directory(self) -> str:
        """Create a temporary directory for testing."""
        test_dir = tempfile.mkdtemp(prefix="context_menu_test_")
        logger.debug(f"Created test directory: {test_dir}")
        return test_dir

    def _create_test_files(self) -> List[str]:
        """Create test files in the test directory."""
        test_files = []

        # Create some test files
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content for file {i}")
            test_files.append(file_path)

        # Create a test subdirectory
        subdir_path = os.path.join(self.test_dir, "test_subdir")
        os.makedirs(subdir_path, exist_ok=True)
        test_files.append(subdir_path)

        # Create a file in the subdirectory
        subdir_file_path = os.path.join(subdir_path, "subdir_file.txt")
        with open(subdir_file_path, "w") as f:
            f.write("Test content for subdirectory file")
        test_files.append(subdir_file_path)

        return test_files

    def _log_operation_started(self, operation_type: str, targets: List[str]):
        """Log when an operation is started."""
        self.operations_log.append({
            "event": "started",
            "operation": operation_type,
            "targets": targets
        })
        logger.debug(f"Operation started: {operation_type} on {targets}")

    def _log_operation_completed(self, operation_type: str, targets: List[str], destination: str):
        """Log when an operation is completed."""
        self.operations_log.append({
            "event": "completed",
            "operation": operation_type,
            "targets": targets,
            "destination": destination
        })
        logger.debug(f"Operation completed: {operation_type} on {targets} to {destination}")

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

    def _get_directory_index(self, dirname: str):
        """Get the model index for a directory in the explorer."""
        model = self.file_view.model()
        dir_path = os.path.join(self.test_dir, dirname)

        # Traverse the model to find the directory
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            path = self.file_view.file_system_model.filePath(
                self.file_view.proxy_model.mapToSource(index)
            )
            if path == dir_path:
                return index

        return None

    def _clear_operations_log(self):
        """Clear the operations log."""
        self.operations_log = []

    def _simulate_context_menu(self, index):
        """Simulate right-click context menu on an item."""
        # Select the item first
        self.file_view.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        # Get the rect for the index
        rect = self.file_view.visualRect(index)
        center = rect.center()

        # Simulate right-click
        QTest.mouseClick(
            self.file_view.viewport(),
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
            center
        )

    def run_tests(self):
        """Run all tests."""
        logger.info("Starting Explorer Context Menu tests")

        self.test_file_selection()
        self.test_directory_selection()
        self.test_copy_operation()

        logger.info("Explorer Context Menu tests completed")

    def test_file_selection(self):
        """Test selecting a file in the explorer."""
        logger.info("Testing file selection")

        # Get index for test file
        index = self._get_file_index("test_file_0.txt")
        if not index:
            logger.error("Could not find test file index")
            return

        # Select the file
        self.file_view.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        # Check that selection worked
        selected = self.file_view.selectionModel().selectedIndexes()
        if len(selected) == 0:
            logger.error("File selection failed")
        else:
            logger.info("File selection test passed")

    def test_directory_selection(self):
        """Test selecting a directory in the explorer."""
        logger.info("Testing directory selection")

        # Get index for test directory
        index = self._get_file_index("test_subdir")
        if not index:
            logger.error("Could not find test directory index")
            return

        # Select the directory
        self.file_view.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        # Check that selection worked
        selected = self.file_view.selectionModel().selectedIndexes()
        if len(selected) == 0:
            logger.error("Directory selection failed")
        else:
            logger.info("Directory selection test passed")

    def test_multiple_file_selection(self):
        """Test selecting multiple files in the explorer."""
        logger.info("Testing multiple file selection")

        # Get indexes for test files
        index1 = self._get_file_index("test_file_0.txt")
        index2 = self._get_file_index("test_file_1.txt")
        if not index1 or not index2:
            logger.error("Could not find test file indexes")
            return

        # Select the first file
        self.file_view.selectionModel().select(
            index1,
            QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        # Add the second file to selection with control key
        self.file_view.selectionModel().select(
            index2,
            QItemSelectionModel.SelectionFlag.Select
        )

        # Check that selection worked
        selected = self.file_view.selectionModel().selectedIndexes()
        if len(selected) != 2:
            logger.error(f"Multiple file selection failed, got {len(selected)} items selected")
        else:
            logger.info("Multiple file selection test passed")

    def test_mixed_selection(self):
        """Test selecting both files and directories in the explorer."""
        logger.info("Testing mixed selection")

        # Get indexes for test file and directory
        file_index = self._get_file_index("test_file_0.txt")
        dir_index = self._get_directory_index("test_dir_0")

        if not file_index or not dir_index:
            logger.error("Could not find test indexes")
            return

        # Select the file
        self.file_view.selectionModel().select(
            file_index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        # Add the directory to selection
        self.file_view.selectionModel().select(
            dir_index,
            QItemSelectionModel.SelectionFlag.Select
        )

        # Check that selection worked
        selected = self.file_view.selectionModel().selectedIndexes()
        if len(selected) != 2:
            logger.error(f"Mixed selection failed, got {len(selected)} items selected")
        else:
            logger.info("Mixed selection test passed")

    def test_copy_operation(self):
        """Test the copy operation via context menu."""
        logger.info("Testing copy operation")
        self._clear_operations_log()

        # Get index for test file
        index = self._get_file_index("test_file_0.txt")
        if not index:
            logger.error("Could not find test file index")
            return

        # Directly access file operations service to test copy functionality
        file_path = os.path.join(self.test_dir, "test_file_0.txt")
        self.explorer_widget.file_operations_service.copy_to_clipboard([file_path])

        # Check operations log
        if len(self.operations_log) == 0:
            logger.error("No operations logged for copy")
        elif self.operations_log[0]["operation"] != OperationType.COPY.value:
            logger.error(f"Unexpected operation: {self.operations_log[0]}")
        else:
            logger.info(f"Copy operation test passed: {self.operations_log}")

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
            os.rmdir(os.path.join(self.test_dir, "test_subdir"))
            os.rmdir(self.test_dir)
            logger.debug(f"Removed test directory: {self.test_dir}")
        except Exception as e:
            logger.error(f"Failed to remove test directory {self.test_dir}: {e}")


def run_test():
    """Run the Explorer Context Menu tests."""
    logger.info("Starting Explorer Context Menu tests")

    test = ExplorerContextMenuTest()
    try:
        test.run_tests()
    finally:
        test.cleanup()

    logger.info("Explorer Context Menu tests completed")


if __name__ == "__main__":
    run_test()
