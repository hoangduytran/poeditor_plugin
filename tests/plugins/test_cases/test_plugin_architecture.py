"""
Test suite for Phase 2 plugin architecture.

Tests all core plugins and the plugin registration system to ensure
they follow project rules and integrate correctly.
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path and ensure we're in the right directory
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Make sure we change to the project root for proper module resolution
original_cwd = os.getcwd()
os.chdir(str(project_root))

# Configure PySide6 environment for testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from lg import logger

logger.info(f"Test working directory: {os.getcwd()}")
logger.info(f"Project root: {project_root}")
logger.info(f"Plugins directory exists: {(project_root / 'plugins').exists()}")

# Import PySide6 modules
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QObject
from PySide6.QtGui import QIcon

# Now import core modules - use real objects as per rules.md
try:
    from core.api import PluginAPI
    from core.sidebar_manager import SidebarManager
    from core.tab_manager import TabManager
    
    # Note: MainAppWindow has dependencies that don't exist yet, so we'll create
    # a minimal real window class for testing
    logger.info("Core modules imported successfully")
    
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Core path exists: {(project_root / 'core').exists()}")
    logger.info(f"Core files: {list((project_root / 'core').glob('*.py')) if (project_root / 'core').exists() else 'N/A'}")
    raise


class MinimalMainWindow(QWidget):
    """
    Minimal real main window for testing - follows rules.md to use real objects.
    This is a real QWidget-based object, not a mock.
    """
    
    def __init__(self):
        super().__init__()
        
        # Create real manager objects
        self.sidebar_manager = SidebarManager(self)
        self.tab_manager = TabManager(self)
        
        logger.debug("MinimalMainWindow created with real manager objects")


class TestPluginArchitecture(unittest.TestCase):
    """Test the core plugin architecture and registration system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
        
        logger.info("Starting plugin architecture tests")
    
    def setUp(self):
        """Set up test fixtures using real objects as per rules.md."""
        # Create real minimal main window for testing
        self.main_window = MinimalMainWindow()
        
        # Create plugin API with real main window
        self.plugin_api = PluginAPI(self.main_window)
        
        logger.debug("Test setup complete with real objects")
    
    def test_explorer_plugin_registration(self):
        """Test Explorer plugin registration."""
        logger.info("Testing Explorer plugin registration")
        
        try:
            # Import and register plugin
            from plugins.explorer import plugin as explorer_plugin
            
            # Verify plugin metadata
            self.assertEqual(explorer_plugin.__plugin_name__, "Explorer")
            self.assertEqual(explorer_plugin.__version__, "1.0.0")
            self.assertIn("explorer", explorer_plugin.__plugin_description__.lower())
            
            # Test registration
            explorer_plugin.register(self.plugin_api)
            
            # Verify sidebar panel was added
            self.plugin_api._main_window.sidebar_manager.add_panel.assert_called_once()
            
            # Verify commands were registered
            self.assertIn('explorer.refresh', self.plugin_api._commands)
            self.assertIn('explorer.show_hidden', self.plugin_api._commands)
            self.assertIn('explorer.set_filter', self.plugin_api._commands)
            
            logger.info("✅ Explorer plugin registration test passed")
            
        except Exception as e:
            logger.error(f"❌ Explorer plugin registration test failed: {e}")
            self.fail(f"Explorer plugin registration failed: {e}")
    
    def test_search_plugin_registration(self):
        """Test Search plugin registration."""
        logger.info("Testing Search plugin registration")
        
        try:
            # Import and register plugin
            from plugins.search import plugin as search_plugin
            
            # Verify plugin metadata
            self.assertEqual(search_plugin.__plugin_name__, "Search")
            self.assertEqual(search_plugin.__version__, "1.0.0")
            self.assertIn("search", search_plugin.__plugin_description__)
            
            # Test registration
            search_plugin.register(self.plugin_api)
            
            # Verify commands were registered
            self.assertIn('search.find', self.plugin_api._commands)
            self.assertIn('search.clear', self.plugin_api._commands)
            self.assertIn('search.find_in_files', self.plugin_api._commands)
            
            logger.info("✅ Search plugin registration test passed")
            
        except Exception as e:
            logger.error(f"❌ Search plugin registration test failed: {e}")
            self.fail(f"Search plugin registration failed: {e}")
    
    def test_preferences_plugin_registration(self):
        """Test Preferences plugin registration."""
        logger.info("Testing Preferences plugin registration")
        
        try:
            # Import and register plugin
            from plugins.preferences import plugin as preferences_plugin
            
            # Verify plugin metadata
            self.assertEqual(preferences_plugin.__plugin_name__, "Preferences")
            self.assertEqual(preferences_plugin.__version__, "1.0.0")
            self.assertIn("settings", preferences_plugin.__plugin_description__)
            
            # Test registration
            preferences_plugin.register(self.plugin_api)
            
            # Verify commands were registered
            self.assertIn('preferences.open', self.plugin_api._commands)
            self.assertIn('preferences.reset', self.plugin_api._commands)
            self.assertIn('preferences.export', self.plugin_api._commands)
            self.assertIn('preferences.import', self.plugin_api._commands)
            
            logger.info("✅ Preferences plugin registration test passed")
            
        except Exception as e:
            logger.error(f"❌ Preferences plugin registration test failed: {e}")
            self.fail(f"Preferences plugin registration failed: {e}")
    
    def test_extensions_plugin_registration(self):
        """Test Extensions plugin registration."""
        logger.info("Testing Extensions plugin registration")
        
        try:
            # Import and register plugin
            from plugins.extensions import plugin as extensions_plugin
            
            # Verify plugin metadata
            self.assertEqual(extensions_plugin.__plugin_name__, "Extensions")
            self.assertEqual(extensions_plugin.__version__, "1.0.0")
            self.assertIn("plugin", extensions_plugin.__plugin_description__.lower())
            
            # Test registration
            extensions_plugin.register(self.plugin_api)
            
            # Verify commands were registered
            self.assertIn('extensions.refresh', self.plugin_api._commands)
            self.assertIn('extensions.install', self.plugin_api._commands)
            self.assertIn('extensions.uninstall', self.plugin_api._commands)
            
            logger.info("✅ Extensions plugin registration test passed")
            
        except Exception as e:
            logger.error(f"❌ Extensions plugin registration test failed: {e}")
            self.fail(f"Extensions plugin registration failed: {e}")
    
    def test_account_plugin_registration(self):
        """Test Account plugin registration."""
        logger.info("Testing Account plugin registration")
        
        try:
            # Import and register plugin
            from plugins.account import plugin as account_plugin
            
            # Verify plugin metadata
            self.assertEqual(account_plugin.__plugin_name__, "Account")
            self.assertEqual(account_plugin.__version__, "1.0.0")
            self.assertIn("account management", account_plugin.__plugin_description__)
            
            # Test registration
            account_plugin.register(self.plugin_api)
            
            # Verify commands were registered
            self.assertIn('account.login', self.plugin_api._commands)
            self.assertIn('account.logout', self.plugin_api._commands)
            self.assertIn('account.profile', self.plugin_api._commands)
            
            logger.info("✅ Account plugin registration test passed")
            
        except Exception as e:
            logger.error(f"❌ Account plugin registration test failed: {e}")
            self.fail(f"Account plugin registration failed: {e}")
    
    def test_plugin_panel_creation(self):
        """Test that plugin panels can be created without errors."""
        logger.info("Testing plugin panel creation")
        
        try:
            # Test Explorer panel
            from plugins.explorer.explorer_panel import ExplorerPanel
            explorer_panel = ExplorerPanel()
            self.assertIsInstance(explorer_panel, QWidget)
            
            # Test Search panel
            from plugins.search.search_panel import SearchPanel
            search_panel = SearchPanel()
            self.assertIsInstance(search_panel, QWidget)
            
            # Test Preferences panel
            from plugins.preferences.preferences_panel import PreferencesPanel
            preferences_panel = PreferencesPanel()
            self.assertIsInstance(preferences_panel, QWidget)
            
            # Test Extensions panel
            from plugins.extensions.extensions_panel import ExtensionsPanel
            extensions_panel = ExtensionsPanel()
            self.assertIsInstance(extensions_panel, QWidget)
            
            # Test Account panel
            from plugins.account.account_panel import AccountPanel
            account_panel = AccountPanel()
            self.assertIsInstance(account_panel, QWidget)
            
            logger.info("✅ Plugin panel creation test passed")
            
        except Exception as e:
            logger.error(f"❌ Plugin panel creation test failed: {e}")
            self.fail(f"Plugin panel creation failed: {e}")
    
    def test_direct_object_access_compliance(self):
        """Test that plugins follow direct object access rules (no hasattr/getattr)."""
        logger.info("Testing direct object access compliance")
        
        try:
            # Read plugin files and check for forbidden patterns
            plugins_dir = project_root / "plugins"
            forbidden_patterns = ["hasattr(", "getattr("]
            
            violations = []
            
            for plugin_file in plugins_dir.rglob("*.py"):
                # Skip test files and __pycache__
                if "test" in str(plugin_file) or "__pycache__" in str(plugin_file):
                    continue
                    
                with open(plugin_file, 'r') as f:
                    content = f.read()
                    for pattern in forbidden_patterns:
                        if pattern in content:
                            violations.append(f"{plugin_file}: {pattern}")
            
            if violations:
                violation_text = "\n".join(violations)
                self.fail(f"Direct object access rule violations found:\n{violation_text}")
            
            logger.info("✅ Direct object access compliance test passed")
            
        except Exception as e:
            logger.error(f"❌ Direct object access compliance test failed: {e}")
            self.fail(f"Direct object access compliance test failed: {e}")
    
    def test_logging_compliance(self):
        """Test that plugins use lg logger correctly."""
        logger.info("Testing logging compliance")
        
        try:
            # Read plugin files and check for proper logging usage
            plugins_dir = project_root / "plugins"
            
            violations = []
            
            for plugin_file in plugins_dir.rglob("*.py"):
                with open(plugin_file, 'r') as f:
                    content = f.read()
                    
                    # Check for print statements (forbidden)
                    if "print(" in content and "# Test" not in content:
                        violations.append(f"{plugin_file}: contains print() statement")
                    
                    # Check for lg import if logger is used
                    if "logger." in content and "from lg import logger" not in content:
                        violations.append(f"{plugin_file}: uses logger without importing from lg")
            
            if violations:
                violation_text = "\n".join(violations)
                self.fail(f"Logging compliance violations found:\n{violation_text}")
            
            logger.info("✅ Logging compliance test passed")
            
        except Exception as e:
            logger.error(f"❌ Logging compliance test failed: {e}")
            self.fail(f"Logging compliance test failed: {e}")
    
    def test_plugin_directory_structure(self):
        """Test that plugin directory structure follows the standard."""
        logger.info("Testing plugin directory structure")
        
        try:
            plugins_dir = project_root / "plugins"
            expected_plugins = ["explorer", "search", "preferences", "extensions", "account"]
            
            for plugin_name in expected_plugins:
                plugin_dir = plugins_dir / plugin_name
                
                # Check directory exists
                self.assertTrue(plugin_dir.exists(), f"Plugin directory {plugin_name} does not exist")
                
                # Check required files
                init_file = plugin_dir / "__init__.py"
                plugin_file = plugin_dir / "plugin.py"
                panel_file = plugin_dir / f"{plugin_name}_panel.py"
                
                self.assertTrue(init_file.exists(), f"{plugin_name}/__init__.py does not exist")
                self.assertTrue(plugin_file.exists(), f"{plugin_name}/plugin.py does not exist")
                self.assertTrue(panel_file.exists(), f"{plugin_name}/{plugin_name}_panel.py does not exist")
            
            logger.info("✅ Plugin directory structure test passed")
            
        except Exception as e:
            logger.error(f"❌ Plugin directory structure test failed: {e}")
            self.fail(f"Plugin directory structure test failed: {e}")


class TestPluginFunctionality(unittest.TestCase):
    """Test specific plugin functionality using real objects as per rules.md."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures using real objects."""
        # Create real minimal main window for functional testing
        self.main_window = MinimalMainWindow()
        self.plugin_api = PluginAPI(self.main_window)
        logger.debug("Functional test setup complete with real objects")
    
    def test_explorer_file_filtering(self):
        """Test Explorer plugin file filtering functionality."""
        logger.info("Testing Explorer file filtering")
        
        try:
            from plugins.explorer.explorer_panel import ExplorerPanel
            panel = ExplorerPanel()
            
            # Test filter pattern setting
            panel.set_filter_pattern("*.txt")
            self.assertEqual(panel.filter_input.text(), "*.txt")
            
            # Test hidden files toggle
            initial_state = panel.hidden_checkbox.isChecked()
            panel.toggle_hidden_files()
            self.assertNotEqual(panel.hidden_checkbox.isChecked(), initial_state)
            
            logger.info("✅ Explorer file filtering test passed")
            
        except Exception as e:
            logger.error(f"❌ Explorer file filtering test failed: {e}")
            self.fail(f"Explorer file filtering test failed: {e}")
    
    def test_search_functionality(self):
        """Test Search plugin functionality."""
        logger.info("Testing Search functionality")
        
        try:
            from plugins.search.search_panel import SearchPanel
            panel = SearchPanel()
            
            # Test search term setting
            test_term = "test_search"
            panel.search_input.setCurrentText(test_term)
            self.assertEqual(panel.search_input.currentText(), test_term)
            
            # Test search options
            panel.content_search_cb.setChecked(True)
            self.assertTrue(panel.content_search_cb.isChecked())
            
            logger.info("✅ Search functionality test passed")
            
        except Exception as e:
            logger.error(f"❌ Search functionality test failed: {e}")
            self.fail(f"Search functionality test failed: {e}")


if __name__ == '__main__':
    # Run tests
    logger.info("Starting Phase 2 plugin architecture test suite")
    
    # Create test suite using modern approach
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(loader.loadTestsFromTestCase(TestPluginArchitecture))
    test_suite.addTest(loader.loadTestsFromTestCase(TestPluginFunctionality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Log results
    if result.wasSuccessful():
        logger.info("🎉 All plugin architecture tests passed!")
    else:
        logger.error(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
