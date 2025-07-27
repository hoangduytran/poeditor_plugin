"""
Integration tests for the Core Services in Phase 1.

This ensures that FileNumberingService, UndoRedoManager,
and FileOperationsService work together correctly.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from lg import logger
from services.file_numbering_service import FileNumberingService
from services.undo_redo_service import UndoRedoManager, FileOperation
from services.file_operations_service import FileOperationsService, OperationType


class CoreServicesIntegrationTests(unittest.TestCase):
    """Integration tests for Core Services."""
    
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
        self.nested_dir = os.path.join(self.source_dir, "nested")
        os.makedirs(self.nested_dir)
        self.nested_file = os.path.join(self.nested_dir, "nested.txt")
        
        with open(self.test_file1, 'w') as f:
            f.write("Test file 1 content")
        with open(self.test_file2, 'w') as f:
            f.write("Test file 2 content")
        with open(self.nested_file, 'w') as f:
            f.write("Nested file content")
            
        # Create services
        self.numbering_service = FileNumberingService()
        self.undo_redo_manager = UndoRedoManager()
        self.file_ops = FileOperationsService()
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_complex_operation_sequence(self):
        """Test a complex sequence of operations with undo/redo."""
        # 1. Copy a file
        self.file_ops.copy_to_clipboard([self.test_file1])
        
        # 2. Paste it to target directory
        pasted_paths = self.file_ops.paste(self.target_dir)
        self.assertEqual(len(pasted_paths), 1)
        
        target_file1 = os.path.join(self.target_dir, "test1.txt")
        self.assertTrue(os.path.exists(target_file1))
        
        # 3. Rename the copy
        renamed_path = self.file_ops.rename_item(target_file1, "renamed.txt")
        self.assertTrue(os.path.exists(renamed_path))
        
        # 4. Create a new file in target
        new_file_path = self.file_ops.create_new_file(self.target_dir, "newfile.txt")
        self.assertTrue(os.path.exists(new_file_path))
        
        # 5. Verify we have 3 undo operations available
        self.assertTrue(self.file_ops.can_undo())
        
        # 6. Undo the new file creation
        self.file_ops.undo()
        self.assertFalse(os.path.exists(new_file_path))
        
        # 7. Undo the rename
        self.file_ops.undo()
        self.assertTrue(os.path.exists(target_file1))
        self.assertFalse(os.path.exists(renamed_path))
        
        # 8. Undo the paste
        self.file_ops.undo()
        self.assertFalse(os.path.exists(target_file1))
        
        # 9. Verify no more undo operations
        self.assertFalse(self.file_ops.can_undo())
        
        # 10. Redo the paste
        self.file_ops.redo()
        self.assertTrue(os.path.exists(target_file1))
        
        # 11. Redo the rename
        self.file_ops.redo()
        self.assertFalse(os.path.exists(target_file1))
        self.assertTrue(os.path.exists(renamed_path))
        
        # 12. Redo the new file creation
        self.file_ops.redo()
        self.assertTrue(os.path.exists(new_file_path))
        
    def test_file_numbering_integration(self):
        """Test file numbering integration with file operations."""
        # 1. Create files with same name
        file1 = self.file_ops.create_new_file(self.target_dir, "file.txt")
        file2 = self.file_ops.create_new_file(self.target_dir, "file.txt")
        file3 = self.file_ops.create_new_file(self.target_dir, "file.txt")
        
        # Check that they have correct numbering
        self.assertEqual(os.path.basename(file1), "file.txt")
        self.assertEqual(os.path.basename(file2), "file (1).txt")
        self.assertEqual(os.path.basename(file3), "file (2).txt")
        
        # 2. Copy a file and paste it multiple times
        self.file_ops.copy_to_clipboard([file1])
        paste1 = self.file_ops.paste(self.target_dir)[0]
        paste2 = self.file_ops.paste(self.target_dir)[0]
        
        # Check correct numbering on paste
        self.assertEqual(os.path.basename(paste1), "file (3).txt")
        self.assertEqual(os.path.basename(paste2), "file (4).txt")
        
        # 3. Duplicate a file
        dup = self.file_ops.duplicate_item(file1)
        self.assertEqual(os.path.basename(dup), "file (5).txt")
        
    def test_undo_redo_complex_operations(self):
        """Test undo/redo with complex operations affecting multiple files."""
        # 1. Create a folder structure
        folder1 = self.file_ops.create_new_folder(self.target_dir, "folder1")
        folder2 = self.file_ops.create_new_folder(self.target_dir, "folder2")
        
        file1 = self.file_ops.create_new_file(folder1, "file1.txt")
        file2 = self.file_ops.create_new_file(folder1, "file2.txt")
        
        # Add content to files
        with open(file1, 'w') as f:
            f.write("File 1 content")
        with open(file2, 'w') as f:
            f.write("File 2 content")
            
        # 2. Move multiple files
        self.file_ops.move_items([file1, file2], folder2)
        
        moved_file1 = os.path.join(folder2, "file1.txt")
        moved_file2 = os.path.join(folder2, "file2.txt")
        
        self.assertTrue(os.path.exists(moved_file1))
        self.assertTrue(os.path.exists(moved_file2))
        self.assertFalse(os.path.exists(file1))
        self.assertFalse(os.path.exists(file2))
        
        # 3. Undo the move
        self.file_ops.undo()
        
        self.assertFalse(os.path.exists(moved_file1))
        self.assertFalse(os.path.exists(moved_file2))
        self.assertTrue(os.path.exists(file1))
        self.assertTrue(os.path.exists(file2))
        
        # 4. Redo the move
        self.file_ops.redo()
        
        self.assertTrue(os.path.exists(moved_file1))
        self.assertTrue(os.path.exists(moved_file2))
        self.assertFalse(os.path.exists(file1))
        self.assertFalse(os.path.exists(file2))
        
        # 5. Delete the target folder with files
        self.file_ops.delete_items([folder2])
        
        self.assertFalse(os.path.exists(folder2))
        self.assertFalse(os.path.exists(moved_file1))
        self.assertFalse(os.path.exists(moved_file2))
        
        # 6. Undo the delete
        self.file_ops.undo()
        
        self.assertTrue(os.path.exists(folder2))
        self.assertTrue(os.path.exists(moved_file1))
        self.assertTrue(os.path.exists(moved_file2))
        
        # Verify content preserved
        with open(moved_file1, 'r') as f:
            content1 = f.read()
        with open(moved_file2, 'r') as f:
            content2 = f.read()
            
        self.assertEqual(content1, "File 1 content")
        self.assertEqual(content2, "File 2 content")


if __name__ == '__main__':
    unittest.main()
