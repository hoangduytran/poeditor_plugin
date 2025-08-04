"""
Unit tests for the UndoRedoManager.
"""

import os
import unittest
from datetime import datetime
from typing import Dict, Any, Optional

from lg import logger
from services.undo_redo_service import UndoRedoManager, FileOperation


class UndoRedoManagerTests(unittest.TestCase):
    """Test cases for the UndoRedoManager."""

    def setUp(self):
        """Set up test environment."""
        self.manager = UndoRedoManager()

    def create_test_operation(self, op_type: str, source_paths: list,
                             target_path: str, undo_data: Optional[Dict[str, Any]] = None) -> FileOperation:
        """Helper to create a test operation."""
        return FileOperation(
            operation_type=op_type,
            source_paths=source_paths,
            target_path=target_path,
            timestamp=datetime.now(),
            is_undoable=True,
            undo_data={} if undo_data is None else undo_data
        )

    def test_record_operation(self):
        """Test recording an operation."""
        op = self.create_test_operation(
            "copy", ["/test/file.txt"], "/test/destination/"
        )

        self.manager.record_operation(op)
        self.assertTrue(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

    def test_record_non_undoable_operation(self):
        """Test recording a non-undoable operation."""
        op = FileOperation(
            operation_type="delete",
            source_paths=["/test/temp.txt"],
            target_path="",
            timestamp=datetime.now(),
            is_undoable=False,
            undo_data={}
        )

        self.manager.record_operation(op)
        self.assertFalse(self.manager.can_undo())

    def test_undo(self):
        """Test undoing an operation."""
        op = self.create_test_operation(
            "copy", ["/test/file.txt"], "/test/destination/"
        )

        self.manager.record_operation(op)
        undone_op = self.manager.undo()

        self.assertIsNotNone(undone_op)
        if undone_op:  # Make the type checker happy
            self.assertEqual(undone_op.operation_type, "copy")
        self.assertFalse(self.manager.can_undo())
        self.assertTrue(self.manager.can_redo())

    def test_redo(self):
        """Test redoing an operation."""
        op = self.create_test_operation(
            "copy", ["/test/file.txt"], "/test/destination/"
        )

        self.manager.record_operation(op)
        self.manager.undo()
        redone_op = self.manager.redo()

        self.assertIsNotNone(redone_op)
        if redone_op:  # Make the type checker happy
            self.assertEqual(redone_op.operation_type, "copy")
        self.assertTrue(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

    def test_undo_empty(self):
        """Test undoing when there's nothing to undo."""
        result = self.manager.undo()
        self.assertIsNone(result)

    def test_redo_empty(self):
        """Test redoing when there's nothing to redo."""
        result = self.manager.redo()
        self.assertIsNone(result)

    def test_record_clears_redo(self):
        """Test that recording a new operation clears the redo stack."""
        op1 = self.create_test_operation(
            "copy", ["/test/file1.txt"], "/test/destination/"
        )
        op2 = self.create_test_operation(
            "move", ["/test/file2.txt"], "/test/destination/"
        )

        self.manager.record_operation(op1)
        self.manager.undo()  # op1 goes to redo stack

        # Recording op2 should clear the redo stack (op1)
        self.manager.record_operation(op2)

        self.assertTrue(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())  # redo stack is cleared

        # Undo op2, verify we can't redo op1
        self.manager.undo()
        self.assertFalse(self.manager.can_undo())
        self.assertTrue(self.manager.can_redo())  # Can only redo op2

        # Redo op2
        redone_op = self.manager.redo()
        self.assertIsNotNone(redone_op)
        if redone_op:  # Make the type checker happy
            self.assertEqual(redone_op.operation_type, "move")

    def test_max_history(self):
        """Test that the history is limited to max_history operations."""
        # Create manager with small history limit
        limited_manager = UndoRedoManager(max_history=3)

        # Add 4 operations (should only keep the last 3)
        for i in range(4):
            op = self.create_test_operation(
                f"op{i}", [f"/test/file{i}.txt"], "/test/destination/"
            )
            limited_manager.record_operation(op)

        # Should have 3 operations in history
        history = limited_manager.get_undo_history()
        self.assertEqual(len(history), 3)

        # First operation should be op1 (op0 was pushed out)
        self.assertEqual(history[0].operation_type, "op1")

    def test_peek_undo(self):
        """Test peeking at the undo stack."""
        op = self.create_test_operation(
            "rename", ["/test/old.txt"], "/test/new.txt"
        )

        self.manager.record_operation(op)
        peeked_op = self.manager.peek_undo()

        self.assertIsNotNone(peeked_op)
        if peeked_op:  # Make the type checker happy
            self.assertEqual(peeked_op.operation_type, "rename")
        self.assertTrue(self.manager.can_undo())  # Operation still in stack

    def test_peek_redo(self):
        """Test peeking at the redo stack."""
        op = self.create_test_operation(
            "rename", ["/test/old.txt"], "/test/new.txt"
        )

        self.manager.record_operation(op)
        self.manager.undo()
        peeked_op = self.manager.peek_redo()

        self.assertIsNotNone(peeked_op)
        if peeked_op:  # Make the type checker happy
            self.assertEqual(peeked_op.operation_type, "rename")
        self.assertTrue(self.manager.can_redo())  # Operation still in stack

    def test_clear_history(self):
        """Test clearing the history."""
        op1 = self.create_test_operation(
            "copy", ["/test/file1.txt"], "/test/destination/"
        )
        op2 = self.create_test_operation(
            "move", ["/test/file2.txt"], "/test/destination/"
        )

        self.manager.record_operation(op1)
        self.manager.record_operation(op2)
        self.manager.undo()  # op2 goes to redo stack

        self.manager.clear_history()

        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())
        self.assertEqual(len(self.manager.get_undo_history()), 0)
        self.assertEqual(len(self.manager.get_redo_history()), 0)


if __name__ == '__main__':
    unittest.main()
