==============================
Panel Development Guide
==============================

.. py:module:: guides.panel_development

Complete guide for creating UI panels and views in the PySide POEditor Plugin.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

Panels are the main UI components that provide functionality in the PySide POEditor Plugin. This guide covers:

* **Panel Architecture**: Understanding the panel system
* **Panel Interface**: Implementing the required panel interface
* **UI Development**: Creating responsive and accessible UIs
* **Integration**: Connecting panels with services and activities
* **Best Practices**: Performance and maintainability guidelines

Panel System Architecture
=========================

How Panels Work
---------------

Panels are displayed in the sidebar and provide the main user interface:

.. code-block:: text

   Panel System Architecture:
   ├── SidebarManager              # Manages panel container
   ├── ActivityManager             # Manages panel activation
   ├── Panel Container (QStackedWidget)
   └── Individual Panels
       ├── ExplorerPanel          # File explorer
       ├── SearchPanel            # Search functionality
       ├── AccountPanel           # Account management
       └── CustomPanel            # Your custom panel

**Key Components:**

* ``core/sidebar_manager.py`` - Panel container management
* ``panels/panel_interface.py`` - Panel interface definition
* ``panels/`` - Panel implementations

Panel Interface Requirements
---------------------------

All panels must implement the PanelInterface:

.. code-block:: python

   # panels/panel_interface.py
   from PySide6.QtCore import Signal
   from abc import ABC, abstractmethod
   
   class PanelInterface(ABC):
       """Interface that all panels must implement"""
       
       # Signals
       panel_activated = Signal()
       panel_deactivated = Signal()
       
       @abstractmethod
       def get_title(self) -> str:
           """Get panel title"""
           pass
       
       @abstractmethod
       def get_icon_name(self) -> str:
           """Get panel icon name"""
           pass
       
       def refresh(self):
           """Refresh panel content (optional)"""
           pass
       
       def cleanup(self):
           """Clean up resources (optional)"""
           pass

Creating Custom Panels
======================

Step 1: Basic Panel Structure
-----------------------------

Create a panel following the interface:

.. code-block:: python

   # panels/my_custom_panel.py
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
   from PySide6.QtWidgets import QPushButton, QLineEdit, QTextEdit, QListWidget
   from PySide6.QtCore import Signal, Qt
   
   from panels.panel_interface import PanelInterface
   from core.api import PluginAPI
   from lg import logger
   
   class MyCustomPanel(QWidget, PanelInterface):
       """Custom panel demonstrating panel development"""
       
       # Panel interface signals
       panel_activated = Signal()
       panel_deactivated = Signal()
       
       # Custom panel signals
       item_selected = Signal(str)
       action_performed = Signal(dict)
       
       def __init__(self, api: PluginAPI = None, parent=None):
           super().__init__(parent)
           self.api = api
           self._is_active = False
           
           self.setup_ui()
           self.connect_signals()
           self.apply_styling()
           
           logger.info(f"Initialized {self.__class__.__name__}")
       
       def setup_ui(self):
           """Set up the panel user interface"""
           self.setObjectName("my-custom-panel")
           
           # Main layout
           layout = QVBoxLayout(self)
           layout.setContentsMargins(16, 16, 16, 16)
           layout.setSpacing(12)
           
           # Header section
           self.create_header_section(layout)
           
           # Content section
           self.create_content_section(layout)
           
           # Actions section
           self.create_actions_section(layout)
           
           # Stretch to fill remaining space
           layout.addStretch()
       
       def create_header_section(self, parent_layout):
           """Create the panel header"""
           header_layout = QHBoxLayout()
           
           # Title
           self.title_label = QLabel("My Custom Panel")
           self.title_label.setObjectName("panel-title")
           header_layout.addWidget(self.title_label)
           
           # Refresh button
           self.refresh_button = QPushButton("Refresh")
           self.refresh_button.setObjectName("refresh-button")
           self.refresh_button.clicked.connect(self.refresh)
           header_layout.addWidget(self.refresh_button)
           
           parent_layout.addLayout(header_layout)
       
       def create_content_section(self, parent_layout):
           """Create the main content area"""
           # Search/filter input
           self.search_input = QLineEdit()
           self.search_input.setObjectName("search-input")
           self.search_input.setPlaceholderText("Search items...")
           self.search_input.textChanged.connect(self.filter_items)
           parent_layout.addWidget(self.search_input)
           
           # Item list
           self.item_list = QListWidget()
           self.item_list.setObjectName("item-list")
           self.item_list.itemClicked.connect(self.on_item_selected)
           parent_layout.addWidget(self.item_list)
           
           # Details area
           self.details_area = QTextEdit()
           self.details_area.setObjectName("details-area")
           self.details_area.setPlaceholderText("Select an item to view details...")
           self.details_area.setMaximumHeight(100)
           parent_layout.addWidget(self.details_area)
       
       def create_actions_section(self, parent_layout):
           """Create action buttons"""
           actions_layout = QHBoxLayout()
           
           # Add button
           self.add_button = QPushButton("Add Item")
           self.add_button.setObjectName("add-button")
           self.add_button.clicked.connect(self.add_item)
           actions_layout.addWidget(self.add_button)
           
           # Remove button
           self.remove_button = QPushButton("Remove Item")
           self.remove_button.setObjectName("remove-button")
           self.remove_button.clicked.connect(self.remove_item)
           self.remove_button.setEnabled(False)
           actions_layout.addWidget(self.remove_button)
           
           actions_layout.addStretch()
           parent_layout.addLayout(actions_layout)
       
       def connect_signals(self):
           """Connect internal signals"""
           self.item_list.itemSelectionChanged.connect(self.update_selection_state)
       
       def apply_styling(self):
           """Apply theme styling to the panel"""
           if self.api and hasattr(self.api, 'theme_manager'):
               css = self.api.theme_manager.get_processed_css()
               self.setStyleSheet(css)

Step 2: Panel Logic Implementation
---------------------------------

Add the panel's core functionality:

.. code-block:: python

   # Continue panels/my_custom_panel.py
   
   class MyCustomPanel(QWidget, PanelInterface):
       # ... previous code ...
       
       def load_initial_data(self):
           """Load initial panel data"""
           try:
               # Simulate loading data
               sample_items = [
                   "Sample Item 1",
                   "Sample Item 2", 
                   "Sample Item 3",
                   "Custom Data Item",
                   "Test Entry"
               ]
               
               self.item_list.clear()
               self.item_list.addItems(sample_items)
               
               logger.info(f"Loaded {len(sample_items)} items")
               
           except Exception as e:
               logger.error(f"Error loading initial data: {e}")
       
       def filter_items(self, text: str):
           """Filter items based on search text"""
           for i in range(self.item_list.count()):
               item = self.item_list.item(i)
               item.setHidden(text.lower() not in item.text().lower())
       
       def on_item_selected(self, item):
           """Handle item selection"""
           if item:
               details = f"Selected: {item.text()}\\nType: Sample Item\\nStatus: Active"
               self.details_area.setText(details)
               self.item_selected.emit(item.text())
       
       def update_selection_state(self):
           """Update UI state based on selection"""
           has_selection = len(self.item_list.selectedItems()) > 0
           self.remove_button.setEnabled(has_selection)
       
       def add_item(self):
           """Add a new item"""
           from PySide6.QtWidgets import QInputDialog
           
           text, ok = QInputDialog.getText(self, "Add Item", "Enter item name:")
           if ok and text:
               self.item_list.addItem(text)
               self.action_performed.emit({"action": "add", "item": text})
               logger.info(f"Added item: {text}")
       
       def remove_item(self):
           """Remove selected item"""
           selected_items = self.item_list.selectedItems()
           if selected_items:
               for item in selected_items:
                   item_text = item.text()
                   row = self.item_list.row(item)
                   self.item_list.takeItem(row)
                   self.action_performed.emit({"action": "remove", "item": item_text})
                   logger.info(f"Removed item: {item_text}")
               
               self.details_area.clear()
       
       # Panel Interface Implementation
       def get_title(self) -> str:
           """Get panel title"""
           return "My Custom Panel"
       
       def get_icon_name(self) -> str:
           """Get panel icon name"""
           return "my_custom"
       
       def refresh(self):
           """Refresh panel content"""
           logger.info("Refreshing panel content")
           self.load_initial_data()
           self.details_area.clear()
           self.search_input.clear()
       
       def cleanup(self):
           """Clean up panel resources"""
           logger.info("Cleaning up panel resources")
           # Disconnect signals if needed
           # Clear references
           # Save state if needed

Step 3: Advanced Panel Features
------------------------------

Add advanced functionality:

.. code-block:: python

   # panels/advanced_custom_panel.py
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
   from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QTabWidget
   from PySide6.QtCore import QTimer, QThread, QObject, Signal
   
   class AdvancedCustomPanel(QWidget, PanelInterface):
       """Advanced panel with multiple views and background operations"""
       
       def __init__(self, api: PluginAPI = None, parent=None):
           super().__init__(parent)
           self.api = api
           self.background_worker = None
           self.auto_refresh_timer = QTimer()
           
           self.setup_ui()
           self.setup_background_operations()
           self.load_settings()
       
       def setup_ui(self):
           """Set up advanced UI with multiple views"""
           self.setObjectName("advanced-custom-panel")
           
           layout = QVBoxLayout(self)
           
           # Create tab widget for multiple views
           self.tab_widget = QTabWidget()
           self.tab_widget.setObjectName("panel-tabs")
           
           # List view tab
           self.create_list_view_tab()
           
           # Tree view tab
           self.create_tree_view_tab()
           
           # Settings tab
           self.create_settings_tab()
           
           layout.addWidget(self.tab_widget)
       
       def create_list_view_tab(self):
           """Create list view tab"""
           list_widget = QWidget()
           list_layout = QVBoxLayout(list_widget)
           
           # Add list view components here
           from PySide6.QtWidgets import QLabel
           list_layout.addWidget(QLabel("List View Content"))
           
           self.tab_widget.addTab(list_widget, "List")
       
       def create_tree_view_tab(self):
           """Create tree view tab"""
           tree_widget = QWidget()
           tree_layout = QVBoxLayout(tree_widget)
           
           # Tree widget
           self.tree_view = QTreeWidget()
           self.tree_view.setObjectName("tree-view")
           self.tree_view.setHeaderLabels(["Name", "Type", "Size"])
           tree_layout.addWidget(self.tree_view)
           
           self.tab_widget.addTab(tree_widget, "Tree")
       
       def create_settings_tab(self):
           """Create settings tab"""
           settings_widget = QWidget()
           settings_layout = QVBoxLayout(settings_widget)
           
           # Add settings controls here
           from PySide6.QtWidgets import QCheckBox, QSpinBox
           
           self.auto_refresh_checkbox = QCheckBox("Auto Refresh")
           self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
           settings_layout.addWidget(self.auto_refresh_checkbox)
           
           self.refresh_interval_spinbox = QSpinBox()
           self.refresh_interval_spinbox.setRange(1, 60)
           self.refresh_interval_spinbox.setValue(5)
           self.refresh_interval_spinbox.setSuffix(" seconds")
           settings_layout.addWidget(self.refresh_interval_spinbox)
           
           settings_layout.addStretch()
           self.tab_widget.addTab(settings_widget, "Settings")
       
       def setup_background_operations(self):
           """Set up background operations"""
           self.auto_refresh_timer.timeout.connect(self.refresh)
           
       def toggle_auto_refresh(self, enabled: bool):
           """Toggle auto refresh functionality"""
           if enabled:
               interval = self.refresh_interval_spinbox.value() * 1000
               self.auto_refresh_timer.start(interval)
               logger.info(f"Auto refresh enabled: {interval}ms")
           else:
               self.auto_refresh_timer.stop()
               logger.info("Auto refresh disabled")
       
       def load_settings(self):
           """Load panel settings"""
           if self.api and hasattr(self.api, 'settings_manager'):
               auto_refresh = self.api.settings_manager.get_setting(
                   'advanced_panel.auto_refresh', False
               )
               self.auto_refresh_checkbox.setChecked(auto_refresh)

Panel Styling and Theming
=========================

Panel CSS Styling
-----------------

Create comprehensive CSS for your panel:

.. code-block:: css

   /* Add to theme files */
   
   /* === MY CUSTOM PANEL === */
   #my-custom-panel {
       background-color: var(--color-bg-primary);
       color: var(--color-text);
   }
   
   #my-custom-panel #panel-title {
       font-size: var(--font-size-lg);
       font-weight: var(--font-weight-bold);
       color: var(--color-primary);
       margin-bottom: var(--spacing-sm);
   }
   
   #my-custom-panel #search-input {
       background-color: var(--color-bg-secondary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-sm);
       padding: var(--spacing-sm);
       margin-bottom: var(--spacing-md);
   }
   
   #my-custom-panel #search-input:focus {
       border-color: var(--color-primary);
   }
   
   #my-custom-panel #item-list {
       background-color: var(--color-bg-primary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-sm);
       outline: none;
   }
   
   #my-custom-panel #item-list::item {
       padding: var(--spacing-sm);
       border-bottom: 1px solid var(--color-border-light);
   }
   
   #my-custom-panel #item-list::item:selected {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
   }
   
   #my-custom-panel #item-list::item:hover {
       background-color: var(--color-bg-tertiary);
   }
   
   #my-custom-panel #details-area {
       background-color: var(--color-bg-secondary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-sm);
       padding: var(--spacing-sm);
       font-family: monospace;
   }
   
   #my-custom-panel QPushButton {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
       border: none;
       padding: var(--spacing-sm) var(--spacing-md);
       border-radius: var(--border-radius-md);
       font-weight: var(--font-weight-medium);
   }
   
   #my-custom-panel QPushButton:hover {
       background-color: color-mix(in srgb, var(--color-primary) 85%, black);
   }
   
   #my-custom-panel QPushButton:disabled {
       background-color: var(--color-bg-tertiary);
       color: var(--color-text-muted);
   }

Responsive Design
----------------

Make panels responsive to different sizes:

.. code-block:: python

   from PySide6.QtCore import QSize
   
   class ResponsivePanel(QWidget, PanelInterface):
       def __init__(self, api: PluginAPI = None, parent=None):
           super().__init__(parent)
           self.api = api
           self.min_width = 200
           self.preferred_width = 300
           
       def sizeHint(self) -> QSize:
           """Provide size hint for layout"""
           return QSize(self.preferred_width, 400)
       
       def minimumSizeHint(self) -> QSize:
           """Provide minimum size hint"""
           return QSize(self.min_width, 200)
       
       def resizeEvent(self, event):
           """Handle resize events"""
           super().resizeEvent(event)
           width = event.size().width()
           
           # Adjust layout based on width
           if width < 250:
               self.use_compact_layout()
           else:
               self.use_normal_layout()
       
       def use_compact_layout(self):
           """Switch to compact layout for narrow panels"""
           # Hide less important elements
           # Stack elements vertically
           pass
       
       def use_normal_layout(self):
           """Switch to normal layout"""
           # Show all elements
           # Use horizontal layouts where appropriate
           pass

Panel Testing
=============

Unit Testing Panels
-------------------

Create unit tests for panel functionality:

.. code-block:: python

   # tests/panels/test_my_custom_panel.py
   import unittest
   from unittest.mock import Mock
   from PySide6.QtWidgets import QApplication
   from PySide6.QtTest import QTest
   from PySide6.QtCore import Qt
   
   from panels.my_custom_panel import MyCustomPanel
   from core.api import PluginAPI
   
   class TestMyCustomPanel(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           cls.app = QApplication.instance() or QApplication([])
       
       def setUp(self):
           """Set up test environment"""
           self.mock_api = Mock(spec=PluginAPI)
           self.panel = MyCustomPanel(self.mock_api)
       
       def tearDown(self):
           """Clean up after tests"""
           self.panel.cleanup()
       
       def test_panel_initialization(self):
           """Test panel initialization"""
           self.assertIsNotNone(self.panel)
           self.assertEqual(self.panel.get_title(), "My Custom Panel")
           self.assertEqual(self.panel.get_icon_name(), "my_custom")
       
       def test_add_item(self):
           """Test adding items to the panel"""
           initial_count = self.panel.item_list.count()
           
           # Simulate adding an item
           self.panel.item_list.addItem("Test Item")
           
           self.assertEqual(self.panel.item_list.count(), initial_count + 1)
       
       def test_search_functionality(self):
           """Test search/filter functionality"""
           # Add test items
           self.panel.item_list.addItems(["Apple", "Banana", "Cherry"])
           
           # Filter for "a"
           self.panel.filter_items("a")
           
           # Check visibility
           visible_items = [
               self.panel.item_list.item(i).text()
               for i in range(self.panel.item_list.count())
               if not self.panel.item_list.item(i).isHidden()
           ]
           
           self.assertIn("Apple", visible_items)
           self.assertIn("Banana", visible_items)
           self.assertNotIn("Cherry", visible_items)
       
       def test_item_selection(self):
           """Test item selection"""
           # Add test item
           self.panel.item_list.addItem("Test Item")
           
           # Select item
           item = self.panel.item_list.item(0)
           self.panel.item_list.setCurrentItem(item)
           
           # Trigger selection handler
           self.panel.on_item_selected(item)
           
           # Check that details are updated
           self.assertIn("Test Item", self.panel.details_area.toPlainText())

UI Testing
---------

Test user interactions:

.. code-block:: python

   # tests/ui/test_panel_interactions.py
   import unittest
   from PySide6.QtWidgets import QApplication
   from PySide6.QtTest import QTest
   from PySide6.QtCore import Qt
   
   from panels.my_custom_panel import MyCustomPanel
   
   class TestPanelInteractions(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           cls.app = QApplication.instance() or QApplication([])
       
       def setUp(self):
           self.panel = MyCustomPanel()
           self.panel.show()
       
       def test_refresh_button_click(self):
           """Test refresh button interaction"""
           # Click refresh button
           QTest.mouseClick(self.panel.refresh_button, Qt.LeftButton)
           
           # Verify refresh was called
           # (In real test, you'd mock the refresh method)
           
       def test_search_input_typing(self):
           """Test typing in search input"""
           # Type in search input
           QTest.keyClicks(self.panel.search_input, "test")
           
           # Verify filter was applied
           self.assertEqual(self.panel.search_input.text(), "test")

Performance Testing
------------------

Test panel performance:

.. code-block:: python

   # tests/performance/test_panel_performance.py
   import unittest
   import time
   from PySide6.QtWidgets import QApplication
   
   from panels.my_custom_panel import MyCustomPanel
   
   class TestPanelPerformance(unittest.TestCase):
       @classmethod
       def setUpClass(cls):
           cls.app = QApplication.instance() or QApplication([])
       
       def test_panel_creation_time(self):
           """Test panel creation performance"""
           start_time = time.perf_counter()
           
           panel = MyCustomPanel()
           
           end_time = time.perf_counter()
           creation_time = end_time - start_time
           
           # Panel should be created quickly
           self.assertLess(creation_time, 0.5)  # Under 500ms
       
       def test_large_dataset_performance(self):
           """Test performance with large datasets"""
           panel = MyCustomPanel()
           
           # Add many items
           start_time = time.perf_counter()
           
           items = [f"Item {i}" for i in range(1000)]
           panel.item_list.addItems(items)
           
           end_time = time.perf_counter()
           add_time = end_time - start_time
           
           # Should handle 1000 items quickly
           self.assertLess(add_time, 1.0)  # Under 1 second

Best Practices
=============

Panel Design Guidelines
----------------------

1. **Consistent Layout**: Use consistent spacing and alignment
2. **Clear Hierarchy**: Establish clear visual hierarchy
3. **Responsive Design**: Adapt to different panel sizes
4. **Accessibility**: Ensure keyboard navigation and screen reader support
5. **Performance**: Optimize for large datasets and frequent updates

Code Organization
----------------

1. **Separation of Concerns**: Separate UI setup, logic, and styling
2. **Signal Usage**: Use signals for communication with other components
3. **Resource Management**: Properly clean up resources
4. **Error Handling**: Handle errors gracefully with user feedback
5. **Testing**: Include comprehensive tests

Integration Patterns
-------------------

1. **API Usage**: Use Plugin API for core functionality
2. **Service Integration**: Connect with relevant services
3. **Theme Integration**: Support all available themes
4. **Settings Integration**: Save and load panel preferences
5. **Activity Integration**: Work properly with activity system

Summary
======

Creating panels for the PySide POEditor Plugin involves:

1. **Interface Implementation**: Implement PanelInterface methods
2. **UI Development**: Create responsive and accessible user interfaces
3. **Logic Implementation**: Add core panel functionality
4. **Styling**: Apply consistent CSS styling with theme support
5. **Integration**: Connect with API, services, and activities
6. **Testing**: Create comprehensive unit and UI tests
7. **Performance**: Optimize for large datasets and responsiveness

**Key Points:**

* Follow the PanelInterface requirements
* Use consistent styling with CSS variables
* Implement proper resource management
* Create comprehensive tests
* Follow accessibility guidelines
* Optimize for performance

For additional information, see:

* :doc:`component_styling_guide` - Panel styling best practices
* :doc:`plugin_development_guide` - Creating plugins with panels
* :doc:`service_development_guide` - Integrating with services
* :doc:`/panels/panel_interface` - Panel interface reference
