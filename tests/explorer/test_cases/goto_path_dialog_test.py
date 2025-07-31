"""
Tests for the Go to Path feature in column header navigation.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from PySide6.QtCore import Qt, QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QApplication, QHeaderView

from widgets.goto_path_dialog import GotoPathDialog
from widgets.explorer_header_navigation_integration import HeaderNavigationWidgetIntegration
from core.explorer_settings import ExplorerSettings


class GotoPathTest(unittest.TestCase):
    """Test cases for the Go to Path feature."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create QApplication instance if needed
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
            
        # Set up a test settings file
        cls.test_settings_file = os.path.join(os.path.dirname(__file__), 'test_explorer_settings.json')
        
        # Create a test home directory for path testing
        cls.test_home = os.path.join(os.path.dirname(__file__), 'test_home')
        os.makedirs(cls.test_home, exist_ok=True)
        
        # Create some test directories for navigation
        cls.test_dirs = [
            os.path.join(cls.test_home, 'Documents'),
            os.path.join(cls.test_home, 'Downloads'),
            os.path.join(cls.test_home, 'Projects')
        ]
        
        for directory in cls.test_dirs:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        # Remove test settings file if it exists
        if os.path.exists(cls.test_settings_file):
            os.remove(cls.test_settings_file)
            
        # Clean up test directories if needed
        # This is commented out to avoid accidental deletion of real files
        # import shutil
        # shutil.rmtree(cls.test_home)
    
    def setUp(self):
        """Set up before each test."""
        # Create mock header view
        self.header_view = MagicMock()
        self.header_view.setSectionResizeMode = MagicMock()
        self.header_view.sectionResized = MagicMock()
        
        # Create mock tree view
        self.tree_view = MagicMock()
        
        # Mock the model
        self.model = MagicMock()
        self.model.rootPath = MagicMock(return_value=self.test_home)
        self.tree_view.model.return_value = self.model
        
        # Mock parent method to return tree view
        self.header_view.parent = MagicMock(return_value=self.tree_view)
        
        # Create test settings
        self.settings = ExplorerSettings(self.test_settings_file)
        self.settings._settings["explorer_path_history"] = self.test_dirs
        self.settings.save()
        
        # Create navigation integration object
        with patch('core.explorer_settings.ExplorerSettings', 
                  return_value=self.settings):
            self.header_navigation = HeaderNavigationWidgetIntegration(self.header_view)
            
    def tearDown(self):
        """Clean up after each test."""
        pass
        
    def test_show_goto_path_dialog_creates_dialog(self):
        """Test that _show_goto_path_dialog creates a dialog."""
        with patch('widgets.goto_path_dialog.GotoPathDialog') as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog
            
            self.header_navigation._show_goto_path_dialog()
            
            # Check that dialog was created with the right parameters
            mock_dialog_class.assert_called_once()
            
            # Check that the dialog was shown
            mock_dialog.show.assert_called_once()
    
    def test_goto_path_dialog_sets_current_path(self):
        """Test that dialog is initialized with current path."""
        with patch('widgets.goto_path_dialog.GotoPathDialog') as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog
            
            self.header_navigation._show_goto_path_dialog()
            
            # Check that current path was set
            mock_dialog.set_path.assert_called_once_with(self.test_home)
    
    def test_goto_path_dialog_connects_signals(self):
        """Test that signals are properly connected."""
        with patch('widgets.goto_path_dialog.GotoPathDialog') as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog
            
            self.header_navigation._show_goto_path_dialog()
            
            # Check that path_accepted signal was connected
            mock_dialog.path_accepted.connect.assert_called_once()
            
            # Check that finished signal was connected
            mock_dialog.finished.connect.assert_called_once()
    
    def test_save_path_history_updates_settings(self):
        """Test that _save_path_history updates settings."""
        test_paths = ["/path1", "/path2", "/path3"]
        
        with patch('core.explorer_settings.ExplorerSettings', 
                  return_value=self.settings):
            self.header_navigation._save_path_history(test_paths)
            
            # Check that settings were updated
            saved_paths = self.settings.get("explorer_path_history")
            self.assertEqual(saved_paths, test_paths)


if __name__ == '__main__':
    unittest.main()
