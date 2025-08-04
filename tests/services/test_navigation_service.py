"""
Unit tests for NavigationService.

Tests the core navigation functionality including path validation,
navigation operations, and service coordination.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy

from services.navigation_service import NavigationService
from services.navigation_history_service import NavigationHistoryService
from services.location_manager import LocationManager
from lg import logger


class TestNavigationService(unittest.TestCase):
    """Test suite for NavigationService functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create QApplication if it doesn't exist
        if not QCoreApplication.instance():
            cls.app = QCoreApplication([])
        else:
            cls.app = QCoreApplication.instance()

    def setUp(self):
        """Set up each test."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test subdirectories
        self.test_subdir = self.temp_path / "subdir"
        self.test_subdir.mkdir()

        # Create test file
        self.test_file = self.temp_path / "test.txt"
        self.test_file.write_text("test content")

        # Create NavigationService
        self.navigation_service = NavigationService()

        # Create mock dependencies
        self.mock_history = Mock(spec=NavigationHistoryService)
        self.mock_location_manager = Mock(spec=LocationManager)

        # Configure mock behavior
        self.mock_history.can_go_back.return_value = False
        self.mock_history.can_go_forward.return_value = False
        self.mock_history.add_to_history = Mock()

        # Set dependencies
        self.navigation_service.set_dependencies(self.mock_history, self.mock_location_manager)

        logger.info(f"Test setup complete with temp dir: {self.temp_dir}")

    def tearDown(self):
        """Clean up after each test."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_navigate_to_valid_directory(self):
        """Test navigation to a valid directory."""
        # Set up signal spy
        spy = QSignalSpy(self.navigation_service.navigation_completed)

        # Perform navigation
        result = self.navigation_service.navigate_to(str(self.temp_path))

        # Verify results
        self.assertTrue(result)
        # Use resolved path for comparison since NavigationService resolves paths
        expected_path = str(Path(self.temp_path).resolve())
        self.assertEqual(self.navigation_service.current_path, expected_path)
        self.assertEqual(spy.count(), 1)

        # Verify history was updated
        self.mock_history.add_to_history.assert_called_once_with(expected_path)

        logger.info("Test navigate_to_valid_directory passed")

    def test_navigate_to_invalid_path(self):
        """Test navigation to an invalid path."""
        invalid_path = str(self.temp_path / "nonexistent")

        # Set up signal spy
        spy = QSignalSpy(self.navigation_service.navigation_failed)

        # Perform navigation
        result = self.navigation_service.navigate_to(invalid_path)

        # Verify results
        self.assertFalse(result)
        self.assertIsNone(self.navigation_service.current_path)
        self.assertEqual(spy.count(), 1)

        # Verify history was not updated
        self.mock_history.add_to_history.assert_not_called()

        logger.info("Test navigate_to_invalid_path passed")

    def test_navigate_to_empty_path(self):
        """Test navigation with empty path."""
        result = self.navigation_service.navigate_to("")

        self.assertFalse(result)
        self.assertIsNone(self.navigation_service.current_path)

        logger.info("Test navigate_to_empty_path passed")

    def test_navigate_to_same_path(self):
        """Test navigation to the same path."""
        # First navigation
        self.navigation_service.navigate_to(str(self.temp_path))

        # Reset mock calls
        self.mock_history.reset_mock()

        # Second navigation to same path
        result = self.navigation_service.navigate_to(str(self.temp_path))

        # Should succeed but not add to history again
        self.assertTrue(result)
        self.mock_history.add_to_history.assert_not_called()

        logger.info("Test navigate_to_same_path passed")

    def test_navigate_up(self):
        """Test navigate up functionality."""
        # Navigate to subdirectory first
        self.navigation_service.navigate_to(str(self.test_subdir))

        # Navigate up
        result = self.navigation_service.navigate_up()

        # Should navigate to parent directory
        self.assertTrue(result)
        expected_path = str(Path(self.temp_path).resolve())
        self.assertEqual(self.navigation_service.current_path, expected_path)

        logger.info("Test navigate_up passed")

    def test_navigate_up_at_root(self):
        """Test navigate up when already at root."""
        # Navigate to root
        self.navigation_service.navigate_to("/")

        # Try to navigate up from root
        result = self.navigation_service.navigate_up()

        # Should fail
        self.assertFalse(result)

        logger.info("Test navigate_up_at_root passed")

    def test_navigate_home(self):
        """Test navigate to home directory."""
        result = self.navigation_service.navigate_home()

        self.assertTrue(result)
        self.assertEqual(self.navigation_service.current_path, str(Path.home()))

        logger.info("Test navigate_home passed")

    def test_navigate_back_with_history(self):
        """Test backward navigation with history."""
        # Configure mock to have history
        self.mock_history.can_go_back.return_value = True
        self.mock_history.go_back.return_value = str(self.temp_path)

        # Perform back navigation
        result = self.navigation_service.navigate_back()

        # Verify results
        self.assertTrue(result)
        self.mock_history.go_back.assert_called_once()

        logger.info("Test navigate_back_with_history passed")

    def test_navigate_back_without_history(self):
        """Test backward navigation without history."""
        # Mock has no history by default
        result = self.navigation_service.navigate_back()

        self.assertFalse(result)
        self.mock_history.go_back.assert_not_called()

        logger.info("Test navigate_back_without_history passed")

    def test_navigate_forward_with_history(self):
        """Test forward navigation with history."""
        # Configure mock to have forward history
        self.mock_history.can_go_forward.return_value = True
        self.mock_history.go_forward.return_value = str(self.test_subdir)

        # Perform forward navigation
        result = self.navigation_service.navigate_forward()

        # Verify results
        self.assertTrue(result)
        self.mock_history.go_forward.assert_called_once()

        logger.info("Test navigate_forward_with_history passed")

    def test_refresh_current_location(self):
        """Test refreshing current location."""
        # Navigate to a location first
        self.navigation_service.navigate_to(str(self.temp_path))

        # Set up signal spy
        spy = QSignalSpy(self.navigation_service.navigation_completed)

        # Refresh location
        result = self.navigation_service.refresh_current_location()

        # Verify results
        self.assertTrue(result)
        self.assertEqual(spy.count(), 1)

        logger.info("Test refresh_current_location passed")

    def test_refresh_without_current_location(self):
        """Test refreshing when no current location."""
        result = self.navigation_service.refresh_current_location()

        self.assertFalse(result)

        logger.info("Test refresh_without_current_location passed")

    def test_navigation_state(self):
        """Test navigation state reporting."""
        # Initial state
        state = self.navigation_service.get_navigation_state()

        expected_keys = [
            'current_path', 'is_navigating', 'can_go_back',
            'can_go_forward', 'auto_refresh_enabled', 'validation_enabled'
        ]

        for key in expected_keys:
            self.assertIn(key, state)

        self.assertIsNone(state['current_path'])
        self.assertFalse(state['is_navigating'])

        logger.info("Test navigation_state passed")

    def test_validation_disabled(self):
        """Test navigation with validation disabled."""
        # Disable validation
        self.navigation_service.set_validation_enabled(False)

        # Try to navigate to invalid path
        invalid_path = str(self.temp_path / "nonexistent")
        result = self.navigation_service.navigate_to(invalid_path)

        # Should fail in _perform_navigation but not in validation
        self.assertFalse(result)

        logger.info("Test validation_disabled passed")

    def test_auto_refresh_setting(self):
        """Test auto-refresh setting."""
        # Test enabling/disabling auto-refresh
        self.navigation_service.set_auto_refresh_enabled(False)
        state = self.navigation_service.get_navigation_state()
        self.assertFalse(state['auto_refresh_enabled'])

        self.navigation_service.set_auto_refresh_enabled(True)
        state = self.navigation_service.get_navigation_state()
        self.assertTrue(state['auto_refresh_enabled'])

        logger.info("Test auto_refresh_setting passed")


if __name__ == '__main__':
    # Run tests
    unittest.main()
