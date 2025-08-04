Header Navigation Developer Guide
===================================

This guide provides technical details for developers working with the HeaderNavigationWidget
and its integration with the explorer system.

Class Architecture
------------------

HeaderNavigationWidget
~~~~~~~~~~~~~~~~~~~~~~

The HeaderNavigationWidget extends QHeaderView to provide enhanced navigation and column
management functionality:

.. code-block:: python

   class HeaderNavigationWidget(QHeaderView):
       """Enhanced header widget with navigation and column management capabilities."""
       
       # Navigation signals
       navigation_requested = Signal(str)              # Emitted when navigation requested
       path_changed = Signal(str)                      # Emitted when path changes
       column_visibility_changed = Signal(dict)       # Emitted when columns change
       
       def __init__(self, orientation: Qt.Orientation, parent=None):
           super().__init__(orientation, parent)
           self._setup_header()
           self._create_context_menu()
       
       def inject_services(self, **services):
           """Inject required services for full functionality."""
           self.navigation_service = services.get('navigation_service')
           self.history_service = services.get('history_service')
           self.location_manager = services.get('location_manager')
           self.completion_service = services.get('completion_service')
           self.column_manager = services.get('column_manager')

Service Dependencies
~~~~~~~~~~~~~~~~~~~~

The HeaderNavigationWidget requires several services to provide full functionality:

**NavigationService**
   Core navigation operations and path management

**NavigationHistoryService**
   Tracks navigation history for back/forward functionality

**LocationManager**
   Manages bookmarks and frequently accessed locations

**PathCompletionService**
   Provides auto-completion for path input dialogs

**ColumnManagerService**
   Handles column visibility, sizing, and layout persistence

Context Menu Implementation
---------------------------

Menu Structure
~~~~~~~~~~~~~~

The context menu is built dynamically based on current state:

.. code-block:: python

   def _create_context_menu(self):
       """Create the header context menu with navigation and column options."""
       self.context_menu = QMenu(self)
       
       # Navigation section
       self._add_navigation_actions()
       self.context_menu.addSeparator()
       
       # Quick locations section
       self._add_location_actions()
       self.context_menu.addSeparator()
       
       # Column management section
       self._add_column_actions()

Navigation Actions
~~~~~~~~~~~~~~~~~~

Navigation actions are created with proper state management:

.. code-block:: python

   def _add_navigation_actions(self):
       """Add navigation actions to context menu."""
       
       # Back action with history tooltip
       back_action = self.context_menu.addAction("Back")
       back_action.setEnabled(self.history_service.can_go_back())
       back_action.triggered.connect(self._go_back)
       
       # Set tooltip with previous location
       if self.history_service.can_go_back():
           prev_path = self.history_service.get_previous_path()
           back_action.setToolTip(f"Back to {prev_path}")
       
       # Forward action
       forward_action = self.context_menu.addAction("Forward")
       forward_action.setEnabled(self.history_service.can_go_forward())
       forward_action.triggered.connect(self._go_forward)
       
       # Up action
       up_action = self.context_menu.addAction("Up")
       up_action.setEnabled(self._can_go_up())
       up_action.triggered.connect(self._go_up)
       
       # Home action
       home_action = self.context_menu.addAction("Home")
       home_action.triggered.connect(self._go_home)
       
       # Go to path action
       goto_action = self.context_menu.addAction("Go to Path...")
       goto_action.triggered.connect(self._show_goto_dialog)

Location Management
~~~~~~~~~~~~~~~~~~~

Quick locations provide fast access to common directories:

.. code-block:: python

   def _add_location_actions(self):
       """Add location-based actions to context menu."""
       
       # Recent locations submenu
       recent_menu = self.context_menu.addMenu("Recent Locations")
       recent_paths = self.location_manager.get_recent_paths()
       
       for path in recent_paths[:10]:  # Limit to 10 recent paths
           action = recent_menu.addAction(os.path.basename(path))
           action.setToolTip(path)
           action.triggered.connect(lambda checked, p=path: self._navigate_to(p))
       
       # Bookmarks submenu
       bookmarks_menu = self.context_menu.addMenu("Bookmarks")
       bookmarks = self.location_manager.get_bookmarks()
       
       for bookmark in bookmarks:
           action = bookmarks_menu.addAction(bookmark.name)
           action.setToolTip(bookmark.path)
           action.triggered.connect(
               lambda checked, p=bookmark.path: self._navigate_to(p)
           )
       
       # Bookmark manager
       bookmark_mgr_action = self.context_menu.addAction("Bookmark Manager...")
       bookmark_mgr_action.triggered.connect(self._show_bookmark_manager)

Column Management
~~~~~~~~~~~~~~~~~

Column management actions handle visibility and layout:

.. code-block:: python

   def _add_column_actions(self):
       """Add column management actions to context menu."""
       columns_menu = self.context_menu.addMenu("Columns")
       
       # Column visibility toggles
       visible_columns = self.column_manager.get_visible_columns()
       available_columns = self.column_manager.get_available_columns()
       
       for column_id, column_info in available_columns.items():
           action = columns_menu.addAction(column_info['display_name'])
           action.setCheckable(True)
           action.setChecked(column_id in visible_columns)
           action.triggered.connect(
               lambda checked, col=column_id: self._toggle_column(col, checked)
           )
       
       columns_menu.addSeparator()
       
       # Column layout actions
       fit_action = columns_menu.addAction("Fit Content")
       fit_action.triggered.connect(self._fit_columns_to_content)
       
       reset_action = columns_menu.addAction("Reset Layout")
       reset_action.triggered.connect(self._reset_column_layout)

Signal Handling
---------------

Navigation Signals
~~~~~~~~~~~~~~~~~~

The widget emits signals for navigation requests:

.. code-block:: python

   def _navigate_to(self, path: str):
       """Navigate to the specified path."""
       if self.navigation_service:
           # Emit signal for navigation request
           self.navigation_requested.emit(path)
           
           # Update current path
           self._current_path = path
           self.path_changed.emit(path)

Service Communication
~~~~~~~~~~~~~~~~~~~~~

Services communicate through signal connections:

.. code-block:: python

   def _connect_service_signals(self):
       """Connect signals from injected services."""
       if self.navigation_service:
           self.navigation_service.current_path_changed.connect(
               self._on_path_changed
           )
       
       if self.history_service:
           self.history_service.history_changed.connect(
               self._on_history_changed
           )
       
       if self.column_manager:
           self.column_manager.layout_changed.connect(
               self._on_column_layout_changed
           )

Path Completion Dialog
----------------------

Go To Path Dialog
~~~~~~~~~~~~~~~~~

The "Go to Path" dialog provides auto-completion functionality:

.. code-block:: python

   def _show_goto_dialog(self):
       """Show the 'Go to Path' dialog with auto-completion."""
       dialog = PathCompletionDialog(self)
       dialog.set_completion_service(self.completion_service)
       dialog.set_current_path(self._current_path)
       
       if dialog.exec() == QDialog.Accepted:
           new_path = dialog.get_selected_path()
           if new_path and os.path.exists(new_path):
               self._navigate_to(new_path)

Integration Examples
--------------------

Explorer Panel Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration with the main explorer panel:

.. code-block:: python

   class EnhancedExplorerPanel(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self._setup_ui()
           self._setup_header_navigation()
       
       def _setup_header_navigation(self):
           """Setup header navigation with service injection."""
           header = HeaderNavigationWidget(Qt.Horizontal, self.tree_view)
           self.tree_view.setHeader(header)
           
           # Inject services
           header.inject_services(
               navigation_service=self.navigation_service,
               history_service=self.history_service,
               location_manager=self.location_manager,
               completion_service=self.completion_service,
               column_manager=self.column_manager
           )
           
           # Connect navigation signals
           header.navigation_requested.connect(self._handle_navigation)
           header.column_visibility_changed.connect(self._handle_column_change)

Service Initialization
~~~~~~~~~~~~~~~~~~~~~~

Proper service initialization for header navigation:

.. code-block:: python

   def _initialize_services(self):
       """Initialize services required for header navigation."""
       
       # Navigation service
       self.navigation_service = NavigationService()
       self.navigation_service.set_root_path(self.root_path)
       
       # History service
       self.history_service = NavigationHistoryService()
       self.history_service.load_history()
       
       # Location manager
       self.location_manager = LocationManager()
       self.location_manager.load_bookmarks()
       
       # Path completion service
       self.completion_service = PathCompletionService()
       self.completion_service.set_completion_model(self.file_model)
       
       # Column manager
       self.column_manager = ColumnManagerService()
       self.column_manager.load_column_settings()

Testing Considerations
----------------------

Unit Testing
~~~~~~~~~~~~

Test the header navigation functionality in isolation:

.. code-block:: python

   class TestHeaderNavigationWidget:
       def test_context_menu_creation(self):
           """Test context menu is created with proper structure."""
           header = HeaderNavigationWidget(Qt.Horizontal)
           header._create_context_menu()
           
           assert header.context_menu is not None
           actions = header.context_menu.actions()
           assert len(actions) > 0
       
       def test_navigation_signal_emission(self):
           """Test navigation signals are emitted correctly."""
           header = HeaderNavigationWidget(Qt.Horizontal)
           
           with patch.object(header, 'navigation_requested') as mock_signal:
               header._navigate_to("/test/path")
               mock_signal.emit.assert_called_once_with("/test/path")

Integration Testing
~~~~~~~~~~~~~~~~~~~

Test integration with services:

.. code-block:: python

   class TestHeaderNavigationIntegration:
       def test_service_injection(self):
           """Test services are properly injected and connected."""
           header = HeaderNavigationWidget(Qt.Horizontal)
           nav_service = Mock(spec=NavigationService)
           
           header.inject_services(navigation_service=nav_service)
           
           assert header.navigation_service is nav_service
       
       def test_context_menu_state(self):
           """Test context menu reflects current navigation state."""
           header = HeaderNavigationWidget(Qt.Horizontal)
           history_service = Mock(spec=NavigationHistoryService)
           history_service.can_go_back.return_value = True
           
           header.inject_services(history_service=history_service)
           header._create_context_menu()
           
           # Find back action and verify it's enabled
           actions = header.context_menu.actions()
           back_action = next(a for a in actions if a.text() == "Back")
           assert back_action.isEnabled()

Performance Optimization
------------------------

Lazy Menu Creation
~~~~~~~~~~~~~~~~~~

Context menus are created on-demand to improve performance:

.. code-block:: python

   def contextMenuEvent(self, event):
       """Handle context menu request with lazy creation."""
       # Rebuild menu to reflect current state
       self._rebuild_context_menu()
       self.context_menu.exec(event.globalPos())

Efficient State Management
~~~~~~~~~~~~~~~~~~~~~~~~~~

State updates are batched to minimize UI updates:

.. code-block:: python

   def _update_navigation_state(self):
       """Update navigation state efficiently."""
       # Batch state updates
       updates = {
           'can_go_back': self.history_service.can_go_back(),
           'can_go_forward': self.history_service.can_go_forward(),
           'can_go_up': self._can_go_up(),
           'current_path': self._current_path
       }
       
       # Apply updates in single operation
       self._apply_state_updates(updates)

Related Documentation
---------------------

* :doc:`header_navigation` - User guide for header navigation features
* :doc:`../services/navigation_service` - Navigation service implementation
* :doc:`../services/column_manager_service` - Column management service
* :doc:`../widgets/enhanced_file_view` - Main file view integration
