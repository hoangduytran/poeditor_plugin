"""
Unit tests for the FileOperationsService.

Note: These are mostly integration tests that interact with the real file system.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from lg import logger
from services.file_operations_service import FileOperationsService, OperationType


class FileOperationsServiceTests(unittest.TestCase):
    """Test cases for the FileOperationsService."""

    @classmethod
    def setUpClass(cls):
        """Set up application for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, "source")
        self.target_dir = os.path.join(self.test_dir, "target")

        # Create directories
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)

        # Create test files
        self.test_file1 = os.path.join(self.source_dir, "test1.txt")
        self.test_file2 = os.path.join(self.source_dir, "test2.txt")

        with open(self.test_file1, 'w') as f:
            f.write("Test file 1 content")
        with open(self.test_file2, 'w') as f:
            f.write("Test file 2 content")

        # Create service
        self.service = FileOperationsService()

        # Track signals
        self.signals_received = {
            "started": [],
            "completed": [],
            "failed": []
        }

        self.service.operationStarted.connect(
            lambda op_type, paths: self.signals_received["started"].append((op_type, paths))
        )
        self.service.operationCompleted.connect(
            lambda op_type, paths, target: self.signals_received["completed"].append(
                (op_type, paths, target)
            )
        )
        self.service.operationFailed.connect(
            lambda op_type, paths, error: self.signals_received["failed"].append(
                (op_type, paths, error)
            )
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

        # Reset signals
        self.signals_received = {
            "started": [],
            "completed": [],
            "failed": []
        }

    def test_copy_to_clipboard(self):
        """Test copying files to clipboard."""
        result = self.service.copy_to_clipboard([self.test_file1, self.test_file2])

        self.assertTrue(result)
        mode, paths = self.service.get_clipboard_contents()

        self.assertEqual(mode, "copy")
        self.assertEqual(set(paths), {self.test_file1, self.test_file2})

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.COPY.value)

    def test_cut_to_clipboard(self):
        """Test cutting files to clipboard."""
        result = self.service.cut_to_clipboard([self.test_file1, self.test_file2])

        self.assertTrue(result)
        mode, paths = self.service.get_clipboard_contents()

        self.assertEqual(mode, "cut")
        self.assertEqual(set(paths), {self.test_file1, self.test_file2})

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.CUT.value)

    def test_paste_copy(self):
        """Test pasting files after copy."""
        # Copy files to clipboard
        self.service.copy_to_clipboard([self.test_file1, self.test_file2])

        # Paste to target directory
        new_paths = self.service.paste(self.target_dir)

        # Check that files were copied
        self.assertEqual(len(new_paths), 2)

        target_file1 = os.path.join(self.target_dir, "test1.txt")
        target_file2 = os.path.join(self.target_dir, "test2.txt")

        self.assertTrue(os.path.exists(self.test_file1))  # Original still exists
        self.assertTrue(os.path.exists(self.test_file2))  # Original still exists
        self.assertTrue(os.path.exists(target_file1))  # Copy created
        self.assertTrue(os.path.exists(target_file2))  # Copy created

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 2)  # Copy + Paste
        self.assertEqual(self.signals_received["completed"][1][0], OperationType.PASTE.value)

    def test_paste_cut(self):
        """Test pasting files after cut."""
        # Cut files to clipboard
        self.service.cut_to_clipboard([self.test_file1, self.test_file2])

        # Paste to target directory
        new_paths = self.service.paste(self.target_dir)

        # Check that files were moved
        self.assertEqual(len(new_paths), 2)

        target_file1 = os.path.join(self.target_dir, "test1.txt")
        target_file2 = os.path.join(self.target_dir, "test2.txt")

        self.assertFalse(os.path.exists(self.test_file1))  # Original gone
        self.assertFalse(os.path.exists(self.test_file2))  # Original gone
        self.assertTrue(os.path.exists(target_file1))  # Move target created
        self.assertTrue(os.path.exists(target_file2))  # Move target created

        # Check clipboard cleared
        mode, paths = self.service.get_clipboard_contents()
        self.assertIsNone(mode)
        self.assertEqual(paths, [])

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 2)  # Cut + Paste

    def test_paste_numbering(self):
        """Test pasting files with conflict resolution."""
        # Create a file with the same name in target dir
        target_file1 = os.path.join(self.target_dir, "test1.txt")
        with open(target_file1, 'w') as f:
            f.write("Target file content")

        # Copy file to clipboard and paste
        self.service.copy_to_clipboard([self.test_file1])
        new_paths = self.service.paste(self.target_dir)

        # Check that the file was copied with a number
        self.assertEqual(len(new_paths), 1)
        self.assertTrue(os.path.exists(target_file1))  # Original still there

        # New file should be named "test1 (1).txt"
        numbered_file = os.path.join(self.target_dir, "test1 (1).txt")
        self.assertTrue(os.path.exists(numbered_file))

    def test_delete_items(self):
        """Test deleting files."""
        # Delete files
        result = self.service.delete_items([self.test_file1, self.test_file2])

        # Check that files are gone
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.test_file1))
        self.assertFalse(os.path.exists(self.test_file2))

        # Check signals
        self.assertEqual(len(self.signals_received["started"]), 1)
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.DELETE.value)

    def test_rename_item(self):
        """Test renaming a file."""
        new_name = "renamed.txt"
        new_path = self.service.rename_item(self.test_file1, new_name)

        # Check that file was renamed
        expected_path = os.path.join(self.source_dir, new_name)
        self.assertEqual(new_path, expected_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.test_file1))

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.RENAME.value)

    def test_rename_item_existing(self):
        """Test renaming a file to an existing name."""
        # Should fail because test_file2 already exists
        new_path = self.service.rename_item(self.test_file1, "test2.txt")

        # Check that file was not renamed
        self.assertEqual(new_path, "")
        self.assertTrue(os.path.exists(self.test_file1))

        # Check signals
        self.assertEqual(len(self.signals_received["failed"]), 1)
        self.assertEqual(self.signals_received["failed"][0][0], OperationType.RENAME.value)

    def test_duplicate_item(self):
        """Test duplicating a file."""
        new_path = self.service.duplicate_item(self.test_file1)

        # Check that file was duplicated
        self.assertTrue(os.path.exists(self.test_file1))  # Original still exists
        self.assertTrue(os.path.exists(new_path))  # Duplicate created

        # Check content
        with open(self.test_file1, 'r') as f:
            original_content = f.read()
        with open(new_path, 'r') as f:
            duplicate_content = f.read()
        self.assertEqual(original_content, duplicate_content)

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.DUPLICATE.value)

    def test_create_new_file(self):
        """Test creating a new file."""
        new_file_name = "newfile.txt"
        new_path = self.service.create_new_file(self.target_dir, new_file_name)

        # Check that file was created
        expected_path = os.path.join(self.target_dir, new_file_name)
        self.assertEqual(new_path, expected_path)
        self.assertTrue(os.path.exists(expected_path))

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.NEW_FILE.value)

    def test_create_new_folder(self):
        """Test creating a new folder."""
        new_folder_name = "newfolder"
        new_path = self.service.create_new_folder(self.target_dir, new_folder_name)

        # Check that folder was created
        expected_path = os.path.join(self.target_dir, new_folder_name)
        self.assertEqual(new_path, expected_path)
        self.assertTrue(os.path.isdir(expected_path))

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.NEW_FOLDER.value)

    def test_move_items(self):
        """Test moving files."""
        moved_paths = self.service.move_items([self.test_file1, self.test_file2], self.target_dir)

        # Check that files were moved
        self.assertEqual(len(moved_paths), 2)
        self.assertFalse(os.path.exists(self.test_file1))
        self.assertFalse(os.path.exists(self.test_file2))

        target_file1 = os.path.join(self.target_dir, "test1.txt")
        target_file2 = os.path.join(self.target_dir, "test2.txt")
        self.assertTrue(os.path.exists(target_file1))
        self.assertTrue(os.path.exists(target_file2))

        # Check signals
        self.assertEqual(len(self.signals_received["completed"]), 1)
        self.assertEqual(self.signals_received["completed"][0][0], OperationType.MOVE.value)

    def test_undo_redo(self):
        """Test undo/redo functionality."""
        # Create a new file
        new_file_path = self.service.create_new_file(self.target_dir, "undotest.txt")
        self.assertTrue(os.path.exists(new_file_path))

        # Undo the creation
        self.assertTrue(self.service.can_undo())
        self.service.undo()
        self.assertFalse(os.path.exists(new_file_path))

        # Redo the creation
        self.assertTrue(self.service.can_redo())
        self.service.redo()
        self.assertTrue(os.path.exists(new_file_path))


if __name__ == '__main__':
    unittest.main()
