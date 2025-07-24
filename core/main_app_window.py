"""
Main Application Window for the POEditor application.

This is the main window that hosts the entire application UI using a plugin-based
architecture similar to VS Code. It manages the sidebar, tab area, and plugin loading.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter, QTextEdit,
    QMenuBar, QStatusBar, QApplication, QDockWidget, QVBoxLayout
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt, QSettings
from lg import logger

# Custom editor classes with file_path attribute
class FileAwareTextEdit(QTextEdit):
    """Custom QTextEdit that can store a file_path attribute."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_path = None
    
    @property
    def file_path(self) -> Optional[str]:
        """Get the file path."""
        return self._file_path
    
    @file_path.setter
    def file_path(self, path: str) -> None:
        """Set the file path."""
        self._file_path = path

from core.api import PluginAPI
from core.plugin_manager import PluginManager
from core.sidebar_manager import SidebarManager
from core.tab_manager import TabManager
from managers.activity_manager import ActivityManager
from models.core_activities import (
    EXPLORER_ACTIVITY, SEARCH_ACTIVITY, PREFERENCES_ACTIVITY, 
    EXTENSIONS_ACTIVITY, ACCOUNT_ACTIVITY
)
# Theme system imports
from services.theme_manager import theme_manager
from services.icon_manager import icon_manager
# Dockable activity bar imports
from widgets.activity_bar import ActivityBar
from widgets.activity_bar_dock_widget import ActivityBarDockWidget


class MainAppWindow(QMainWindow):
    """
    Main application window with plugin-based architecture.
    
    Layout:
    +---------------------------------------------------------------+
    | Menu Bar                                                      |
    +---------------------------------------------------------------+
    | [Activity Bar] [Sidebar Panels] | [Tab Area]                 |
    |                                  |                           |
    |                                  |                           |
    +---------------------------------------------------------------+
    | Status Bar                                                    |
    +---------------------------------------------------------------+
    """
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.plugin_api: Optional[PluginAPI] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.sidebar_manager: Optional[SidebarManager] = None
        self.tab_manager: Optional[TabManager] = None
        self.activity_manager: Optional[ActivityManager] = None
        
        # Dockable activity bar components
        self.activity_bar: Optional[ActivityBar] = None
        self.activity_bar_dock: Optional[ActivityBarDockWidget] = None
        
        # UI components
        self.main_splitter: Optional[QSplitter] = None
        
        # Settings
        self.settings = QSettings('POEditor', 'PluginEditor')
        
        # Initialize the application
        self.setup_ui()
        self.setup_theme_system()  # Initialize theme system
        self.setup_plugin_system()
        self.setup_sidebar_buttons()  # Add sidebar buttons
        self.load_plugins()
        self.restore_settings()
        
        logger.info("MainAppWindow initialized")
    
    def setup_ui(self) -> None:
        """Setup the main window UI."""
        try:
            # Set window properties
            self.setWindowTitle("POEditor - Plugin-based Translation Editor")
            self.setMinimumSize(800, 600)
            self.resize(1200, 800)
            
            # Create menu bar
            self.setup_menu_bar()
            
            # Create status bar
            self.setup_status_bar()
            
            # Create main layout
            self.setup_main_layout()
            
            # Apply styles
            self.apply_styles()
            
            logger.info("Main UI setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup main UI: {e}")
            raise
    
    def setup_menu_bar(self) -> None:
        """Setup the application menu bar."""
        try:
            menu_bar = self.menuBar()
            
            # File menu
            file_menu = menu_bar.addMenu('&File')
            
            new_action = QAction('&New', self)
            new_action.setShortcut(QKeySequence.StandardKey.New)
            new_action.triggered.connect(self.on_new_file)
            file_menu.addAction(new_action)
            
            open_action = QAction('&Open...', self)
            open_action.setShortcut(QKeySequence.StandardKey.Open)
            open_action.triggered.connect(self.on_open_file)
            file_menu.addAction(open_action)
            
            file_menu.addSeparator()
            
            save_action = QAction('&Save', self)
            save_action.setShortcut(QKeySequence.StandardKey.Save)
            save_action.triggered.connect(self.on_save_file)
            file_menu.addAction(save_action)
            
            save_as_action = QAction('Save &As...', self)
            save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
            save_as_action.triggered.connect(self.on_save_as_file)
            file_menu.addAction(save_as_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction('E&xit', self)
            exit_action.setShortcut(QKeySequence.StandardKey.Quit)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # View menu
            view_menu = menu_bar.addMenu('&View')
            
            toggle_sidebar_action = QAction('Toggle &Sidebar', self)
            toggle_sidebar_action.setShortcut(QKeySequence('Ctrl+B'))
            toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
            view_menu.addAction(toggle_sidebar_action)
            
            view_menu.addSeparator()
            
            toggle_theme_action = QAction('Toggle &Theme', self)
            toggle_theme_action.setShortcut(QKeySequence('Ctrl+Shift+T'))
            toggle_theme_action.triggered.connect(self.toggle_theme)
            view_menu.addAction(toggle_theme_action)
            
            view_menu.addSeparator()
            
            # Activity bar position submenu
            activity_bar_menu = view_menu.addMenu('Activity Bar Position')
            
            left_action = QAction('Move to &Left', self)
            left_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.LeftDockWidgetArea))
            activity_bar_menu.addAction(left_action)
            
            right_action = QAction('Move to &Right', self)
            right_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.RightDockWidgetArea))
            activity_bar_menu.addAction(right_action)
            
            top_action = QAction('Move to &Top', self)
            top_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.TopDockWidgetArea))
            activity_bar_menu.addAction(top_action)
            
            bottom_action = QAction('Move to &Bottom', self)
            bottom_action.triggered.connect(lambda: self.move_activity_bar_to(Qt.DockWidgetArea.BottomDockWidgetArea))
            activity_bar_menu.addAction(bottom_action)
            
            # Help menu
            help_menu = menu_bar.addMenu('&Help')
            
            about_action = QAction('&About', self)
            about_action.triggered.connect(self.on_about)
            help_menu.addAction(about_action)
            
        except Exception as e:
            logger.error(f"Failed to setup menu bar: {e}")
    
    def setup_status_bar(self) -> None:
        """Setup the application status bar."""
        try:
            status_bar = self.statusBar()
            status_bar.showMessage("Ready")
            
        except Exception as e:
            logger.error(f"Failed to setup status bar: {e}")
    
    def setup_main_layout(self) -> None:
        """Setup main window layout with fixed ActivityBar and dockable Sidebar."""
        # Create main central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Fixed ActivityBar on the left (permanent part of main window)
        self.activity_bar = ActivityBar(self.plugin_api)
        self.activity_bar.setFixedWidth(48)
        main_layout.addWidget(self.activity_bar)

        # Create dockable area widget (contains sidebar and editor)
        self.dock_area_widget = QWidget()
        main_layout.addWidget(self.dock_area_widget)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Setup dock areas within the dock area widget
        self.setup_dock_areas()

        logger.info("Main layout setup: ActivityBar fixed left, dockable area created.")

    def setup_dock_areas(self) -> None:
        """Setup the dock areas within the dockable area widget."""
        try:
            # Create a vertical layout for the dockable area
            dock_layout = QVBoxLayout(self.dock_area_widget)
            dock_layout.setContentsMargins(0, 0, 0, 0)
            dock_layout.setSpacing(0)

            # Create inner main window for proper docking within dock area
            self.inner_main_window = QMainWindow()
            self.inner_main_window.setDockNestingEnabled(True)

            # Create the sidebar manager and dock widget
            self.sidebar_manager = SidebarManager()
            from widgets.sidebar_dock_widget import SidebarDockWidget
            self.sidebar_dock_widget = SidebarDockWidget(self.sidebar_manager, self.inner_main_window)

            # Create TabManager (main editor area) as central widget of inner window
            self.tab_manager = TabManager()
            self.inner_main_window.setCentralWidget(self.tab_manager)

            # Add sidebar dock widget to inner main window (left by default)
            self.inner_main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar_dock_widget)

            # Configure dock widget features
            self.sidebar_dock_widget.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )

            # Enable only left and right dock areas for sidebar
            self.sidebar_dock_widget.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
            )

            # Add inner main window to dock area layout
            dock_layout.addWidget(self.inner_main_window)

            logger.info("Dock areas setup: Inner main window with proper sidebar docking.")

            # Connect signals
            self.connect_signals()

        except Exception as e:
            logger.error(f"Failed to setup dock areas: {e}")

    def on_activity_bar_position_changed(self, area: Qt.DockWidgetArea) -> None:
        """Handle activity bar position changes."""
        try:
            logger.info(f"Activity bar position changed to: {area}")
            
            # Update splitter layout based on position
            self.update_splitter_layout(area)
            
            # Update sidebar manager position if needed
            if self.sidebar_manager:
                self.sidebar_manager.update_layout_for_activity_bar_position(area)
            
        except Exception as e:
            logger.error(f"Failed to handle activity bar position change: {e}")

    def update_splitter_layout(self, activity_bar_area: Qt.DockWidgetArea) -> None:
        """Update splitter orientation based on activity bar position."""
        try:
            # Skip if main_splitter is not initialized
            if self.main_splitter is None:
                logger.warning("Cannot update splitter layout: main_splitter is not initialized")
                return
                
            if activity_bar_area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
                # Horizontal layout for left/right activity bar
                if self.main_splitter.orientation() != Qt.Orientation.Horizontal:
                    self.main_splitter.setOrientation(Qt.Orientation.Horizontal)
                self.main_splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
                self.main_splitter.setStretchFactor(1, 1)  # Tab area stretches
                self.main_splitter.setSizes([300, 900])
            else:
                # Vertical layout for top/bottom activity bar
                if self.main_splitter.orientation() != Qt.Orientation.Vertical:
                    self.main_splitter.setOrientation(Qt.Orientation.Vertical)
                self.main_splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
                self.main_splitter.setStretchFactor(1, 1)  # Tab area stretches
                self.main_splitter.setSizes([200, 600])
                
        except Exception as e:
            logger.error(f"Failed to update splitter layout: {e}")
    
    def connect_signals(self) -> None:
        """Connect internal signals."""
        try:
            if self.tab_manager:
                self.tab_manager.tab_close_requested.connect(self.on_tab_close_requested)
                self.tab_manager.tab_changed.connect(self.on_tab_changed)
            
            if self.sidebar_manager:
                self.sidebar_manager.panel_changed.connect(self.on_sidebar_panel_changed)
                
        except Exception as e:
            logger.error(f"Failed to connect signals: {e}")
    
    def apply_styles(self) -> None:
        """Apply application styles."""
        try:
            # Minimal styling - let components style themselves
            self.setStyleSheet("""
                /* Absolutely minimal main window styling */
                QMainWindow {
                    background-color: #ffffff;
                }
                
                /* Light menu bar */
                QMenuBar {
                    background-color: #f8f8f8;
                    border-bottom: 1px solid #e0e0e0;
                }
                
                /* Light status bar */
                QStatusBar {
                    background-color: #f0f0f0;
                    border-top: 1px solid #e0e0e0;
                }
                
                /* Minimal splitter */
                QSplitter::handle:horizontal {
                    width: 2px;
                    background-color: #e0e0e0;
                }
            """)
            
        except Exception as e:
            logger.error(f"Failed to apply styles: {e}")
    
    def setup_theme_system(self) -> None:
        """Initialize the theme system."""
        try:
            # Connect to theme change signals
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
            # Apply initial theme (will be loaded from settings)
            theme_manager.refresh_theme()
            
            logger.info("Theme system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize theme system: {e}")
    
    def toggle_theme(self) -> None:
        """Toggle between available themes."""
        try:
            logger.info("=== Theme toggle requested from main window ===")
            logger.info(f"Current available themes: {theme_manager.get_available_themes()}")
            logger.info(f"Current theme before toggle: {theme_manager.get_current_theme()}")
            
            next_theme = theme_manager.toggle_theme()
            logger.info(f"Theme toggle executed. New theme: {next_theme}")
            
            # Show a temporary status message
            status_msg = f"Theme changed to: {next_theme}"
            logger.info(f"Showing status message: {status_msg}")
            self.statusBar().showMessage(status_msg, 3000)
            
        except Exception as e:
            logger.error(f"Failed to toggle theme: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _on_theme_changed(self, theme) -> None:
        """Handle theme changes."""
        try:
            # Handle both Theme objects and string theme names
            try:
                theme_name = theme.name
            except AttributeError:
                theme_name = str(theme)
            logger.info(f"Theme changed to: {theme_name}")
            
            # Propagate theme changes to other components
            self._propagate_theme_changes(theme_name)
            
            # Update the main window styling
            self.apply_styles()
            
            # Force style refresh on QDockWidgets for better style application
            for dock in self.findChildren(QDockWidget):
                dock.setStyle(QApplication.style())
                # Temporarily toggle visibility to force style refresh
                was_visible = dock.isVisible()
                if was_visible:
                    dock.hide()
                    dock.show()
            
            # Update status bar with theme information temporarily
            self.statusBar().showMessage(f"Theme changed to: {theme_name}", 3000)
            
        except Exception as e:
            logger.error(f"Failed to handle theme change: {e}")
    
    def setup_plugin_system(self) -> None:
        """Initialize the plugin system."""
        try:
            # Create plugin API
            self.plugin_api = PluginAPI(self)
            
            # Create plugin manager
            self.plugin_manager = PluginManager("plugins", self.plugin_api)
            
            # Discover plugins
            discovered = self.plugin_manager.discover_plugins()
            logger.info(f"Discovered {len(discovered)} plugins: {discovered}")
            
            # Setup activities after plugin API is available
            if self.sidebar_manager and not self.activity_manager:
                self.setup_activity_manager()
            
        except Exception as e:
            logger.error(f"Failed to setup plugin system: {e}")
            raise
    
    def load_plugins(self) -> None:
        """Load all discovered plugins."""
        try:
            if not self.plugin_manager:
                logger.error("Plugin manager not initialized")
                return
            
            results = self.plugin_manager.load_all_plugins()
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            logger.info(f"Loaded {successful}/{total} plugins")
            
            if successful < total:
                failed_plugins = [name for name, success in results.items() if not success]
                logger.warning(f"Failed to load plugins: {failed_plugins}")
            
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}")
    
    def show_sidebar(self, visible: bool = True) -> None:
        """Show or hide the sidebar."""
        try:
            if self.sidebar_manager:
                if visible:
                    self.sidebar_manager.show()
                else:
                    self.sidebar_manager.hide()
                    
        except Exception as e:
            logger.error(f"Failed to toggle sidebar: {e}")
    
    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        try:
            if self.sidebar_manager:
                # Use direct method access with try/except
                try:
                    self.sidebar_manager.toggle_visibility()
                except AttributeError:
                    logger.warning("sidebar_manager.toggle_visibility method not available")
        except Exception as e:
            logger.error(f"Failed to toggle sidebar: {e}")

    def move_activity_bar_to(self, area: Qt.DockWidgetArea) -> None:
        """Move activity bar to specified dock area."""
        try:
            if self.activity_bar_dock:
                self.addDockWidget(area, self.activity_bar_dock)
                logger.info(f"Moved activity bar to: {area}")
        except Exception as e:
            logger.error(f"Failed to move activity bar: {e}")
    
    def get_active_tab(self) -> Optional[QWidget]:
        """Get the currently active tab widget."""
        try:
            if self.tab_manager:
                return self.tab_manager.get_active_tab()
            return None
        except Exception as e:
            logger.error(f"Failed to get active tab: {e}")
            return None
    
    def save_settings(self) -> None:
        """Save application settings."""
        try:
            # Save window geometry and state
            self.settings.setValue('geometry', self.saveGeometry())
            self.settings.setValue('windowState', self.saveState())
            
            # Save activity bar specific settings
            if self.activity_bar_dock:
                area = self.dockWidgetArea(self.activity_bar_dock)
                # Store area as an integer value
                area_value = int(area.value)
                self.settings.setValue("activityBarArea", area_value)
                self.settings.setValue("activityBarSize", self.activity_bar_dock.size())
                self.settings.setValue("activityBarFloating", self.activity_bar_dock.isFloating())
            
            # Save splitter state
            if self.main_splitter:
                self.settings.setValue('splitterState', self.main_splitter.saveState())
                self.settings.setValue("splitterSizes", self.main_splitter.sizes())
            
            # Save sidebar visibility
            if self.sidebar_manager:
                self.settings.setValue('sidebarVisible', self.sidebar_manager.is_visible())
            
            logger.info("Settings saved")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def restore_settings(self) -> None:
        """Restore application settings."""
        try:
            # Restore window geometry
            geometry = self.settings.value('geometry')
            if geometry:
                self.restoreGeometry(geometry)
            
            # Restore window state (including dock widgets)
            window_state = self.settings.value('windowState')
            if window_state:
                self.restoreState(window_state)
            
                        # Restore activity bar position if saved (fallback to left if invalid)
            if self.activity_bar_dock:
                if self.settings.contains("activityBarArea"):
                    try:
                        area = Qt.DockWidgetArea(int(self.settings.value("activityBarArea")))
                        self.addDockWidget(area, self.activity_bar_dock)
                    except (ValueError, TypeError):
                        logger.warning("Invalid activity bar area saved, defaulting to left")
                        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.activity_bar_dock)
                
                # Restore floating state
                if self.settings.contains("activityBarFloating"):
                    # Explicitly convert to bool to avoid type issues
                    floating_value = self.settings.value("activityBarFloating", False)
                    # Convert various possible types to bool
                    is_floating = False
                    if isinstance(floating_value, bool):
                        is_floating = floating_value
                    elif isinstance(floating_value, str):
                        is_floating = floating_value.lower() in ('true', '1', 'yes')
                    elif isinstance(floating_value, int):
                        is_floating = bool(floating_value)
                    
                    self.activity_bar_dock.setFloating(is_floating)
            
            # Restore splitter state and sizes
            if self.main_splitter:
                splitter_state = self.settings.value('splitterState')
                if splitter_state:
                    self.main_splitter.restoreState(splitter_state)
                
                # Restore splitter sizes
                if self.settings.contains("splitterSizes"):
                    sizes = self.settings.value("splitterSizes")
                    if sizes:
                        self.main_splitter.setSizes(sizes)
            
            # Restore sidebar visibility
            if self.sidebar_manager:
                sidebar_visible = self.settings.value('sidebarVisible', True, type=bool)
                if not sidebar_visible:
                    # Use direct method access with try/except
                    try:
                        self.sidebar_manager.toggle_visibility()
                    except AttributeError:
                        logger.warning("sidebar_manager.toggle_visibility method not available")
            
            logger.info("Settings restored")
            
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
    
    def setup_activity_manager(self) -> None:
        """Set up the activity manager and register core activities."""
        try:
            # Create activity manager and link to sidebar
            if self.sidebar_manager and self.plugin_api:
                activity_bar = self.sidebar_manager.get_activity_bar()
                panel_container = self.sidebar_manager.get_panel_container()
                
                # Initialize activity manager
                self.activity_manager = ActivityManager(
                    self.plugin_api, 
                    activity_bar, 
                    panel_container
                )
                
                # Register core activities
                self.register_core_activities()
                
                # Connect signals
                self.activity_manager.activity_changed.connect(
                    self.on_activity_changed
                )
                
                logger.info("Activity manager initialized")
            else:
                logger.error("Cannot initialize ActivityManager: sidebar_manager or plugin_api not available")
                
        except Exception as e:
            logger.error(f"Failed to setup activity manager: {e}")
            
    def register_core_activities(self) -> None:
        """Register the core activities with the activity manager."""
        try:
            if not self.activity_manager:
                logger.error("Activity manager not initialized")
                return
                
            # Register the core activities
            self.activity_manager.register_activity(EXPLORER_ACTIVITY)
            self.activity_manager.register_activity(SEARCH_ACTIVITY)
            self.activity_manager.register_activity(PREFERENCES_ACTIVITY)
            self.activity_manager.register_activity(EXTENSIONS_ACTIVITY)
            self.activity_manager.register_activity(ACCOUNT_ACTIVITY)
            
            # Set the initial active activity
            # We'll use set_active_panel directly since we're still setting up
            if self.sidebar_manager:
                self.sidebar_manager.set_active_panel("explorer")
            
            logger.info("Core activities registered")
            
        except Exception as e:
            logger.error(f"Failed to register core activities: {e}")
            
    def on_activity_changed(self, old_id: str, new_id: str) -> None:
        """Handle activity changed event."""
        try:
            logger.info(f"Activity changed from {old_id} to {new_id}")
            self.statusBar().showMessage(f"Activity: {new_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle activity change: {e}")
    
    def setup_sidebar_buttons(self) -> None:
        """Setup the sidebar activity buttons."""
        try:
            # Import the panel classes
            from panels.explorer_panel import ExplorerPanel
            from panels.search_panel import SearchPanel
            from panels.preferences_panel import PreferencesPanel
            from panels.extensions_panel import ExtensionsPanel
            from panels.account_panel import AccountPanel
            
            # Create panel instances
            explorer_panel = ExplorerPanel()
            # Set the API for enhanced features if available
            if self.plugin_api:
                explorer_panel.set_api(self.plugin_api)
                logger.info("Enhanced Explorer panel initialized with API")
            
            # Connect Explorer panel signals to main application
            explorer_panel.file_opened.connect(self.on_file_opened_from_explorer)
            explorer_panel.location_changed.connect(self.on_explorer_location_changed)
            
            search_panel = SearchPanel()
            preferences_panel = PreferencesPanel()
            extensions_panel = ExtensionsPanel()
            account_panel = AccountPanel()
            
            # Get icons from icon manager
            icons = icon_manager.get_default_sidebar_icons()
            
            # Add panels to sidebar manager (only panel_id and widget)
            if self.sidebar_manager:
                # Use direct method access with try/except
                try:
                    self.sidebar_manager.add_panel("explorer", explorer_panel)
                    self.sidebar_manager.add_panel("search", search_panel)
                    self.sidebar_manager.add_panel("preferences", preferences_panel)
                    self.sidebar_manager.add_panel("extensions", extensions_panel)
                    self.sidebar_manager.add_panel("account", account_panel)
                except AttributeError as e:
                    logger.warning(f"sidebar_manager.add_panel method not available: {e}")

            # Add buttons to activity bar (with icons and titles)
            if self.activity_bar:
                from models.activity_models import ActivityConfig

                # Create activity configurations with icon paths rather than QIcons
                activities = [
                    ActivityConfig(id="explorer", icon="explorer", tooltip="Explorer", panel_class="ExplorerPanel"),
                    ActivityConfig(id="search", icon="search", tooltip="Search", panel_class="SearchPanel"),
                    ActivityConfig(id="preferences", icon="preferences", tooltip="Preferences", panel_class="PreferencesPanel"),
                    ActivityConfig(id="extensions", icon="extensions", tooltip="Extensions", panel_class="ExtensionsPanel"),
                    ActivityConfig(id="account", icon="account", tooltip="Account", panel_class="AccountPanel")
                ]

                # Add activities to activity bar
                for activity in activities:
                    self.activity_bar.add_activity_button(activity)

                # Connect activity bar to sidebar manager
                if self.sidebar_manager:
                    # Use direct method access with try/except
                    try:
                        self.activity_bar.panel_requested.connect(self.sidebar_manager.set_active_panel)
                        # Show the explorer panel by default
                        self.sidebar_manager.set_active_panel("explorer")
                    except AttributeError as e:
                        logger.warning(f"sidebar_manager.set_active_panel method not available: {e}")

            logger.info("Successfully added all sidebar buttons to main application")
            
        except Exception as e:
            logger.error(f"Failed to add sidebar buttons: {e}")
            raise
    
    # Menu action handlers
    def on_new_file(self) -> None:
        """Handle new file action."""
        try:
            if self.plugin_api:
                self.plugin_api.execute_command('file.new')
        except Exception as e:
            logger.error(f"Failed to handle new file: {e}")
    
    def on_open_file(self) -> None:
        """Handle open file action."""
        try:
            if self.plugin_api:
                self.plugin_api.execute_command('file.open')
        except Exception as e:
            logger.error(f"Failed to handle open file: {e}")
    
    def on_save_file(self) -> None:
        """Handle save file action."""
        try:
            if self.plugin_api:
                self.plugin_api.execute_command('file.save')
        except Exception as e:
            logger.error(f"Failed to handle save file: {e}")
    
    def on_save_as_file(self) -> None:
        """Handle save as file action."""
        try:
            if self.plugin_api:
                self.plugin_api.execute_command('file.save_as')
        except Exception as e:
            logger.error(f"Failed to handle save as file: {e}")
    
    def on_about(self) -> None:
        """Handle about action."""
        try:
            from PySide6.QtWidgets import QMessageBox
            
            QMessageBox.about(
                self,
                "About POEditor",
                "POEditor Plugin-based Translation Editor\n\n"
                "A modern, extensible translation editor built with PySide6\n"
                "and a VS Code-like plugin architecture."
            )
        except Exception as e:
            logger.error(f"Failed to show about dialog: {e}")
    
    # Event handlers
    def on_tab_close_requested(self, index: int) -> None:
        """Handle tab close request."""
        try:
            if self.tab_manager:
                self.tab_manager.close_tab(index)
        except Exception as e:
            logger.error(f"Failed to handle tab close request: {e}")
    
    def on_tab_changed(self, index: int) -> None:
        """Handle tab change."""
        try:
            if self.tab_manager:
                widget = self.tab_manager.widget(index)
                if widget:
                    title = self.tab_manager.get_tab_title(index)
                    self.setWindowTitle(f"POEditor - {title}")
                else:
                    self.setWindowTitle("POEditor - Plugin-based Translation Editor")
        except Exception as e:
            logger.error(f"Failed to handle tab change: {e}")
    
    def on_sidebar_panel_changed(self, panel_id: str) -> None:
        """Handle sidebar panel change."""
        try:
            logger.info(f"Sidebar panel changed to: {panel_id}")
            self.statusBar().showMessage(f"Active panel: {panel_id}")
        except Exception as e:
            logger.error(f"Failed to handle sidebar panel change: {e}")
    
    def closeEvent(self, event) -> None:
        """Handle application close event."""
        try:
            # Check for modified tabs
            if self.tab_manager and self.tab_manager.has_modified_tabs():
                from PySide6.QtWidgets import QMessageBox
                
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "You have unsaved changes. Save all before closing?",
                    QMessageBox.StandardButton.Save | 
                    QMessageBox.StandardButton.Discard | 
                    QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    if not self.tab_manager.save_all_modified_tabs():
                        event.ignore()
                        return
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
            
            # Save settings before closing
            self.save_settings()
            
            # Unload all plugins
            if self.plugin_manager:
                self.plugin_manager.unload_all_plugins()
            
            event.accept()
            logger.info("Application closed")
            
        except Exception as e:
            logger.error(f"Failed to handle close event: {e}")
            event.accept()  # Close anyway to avoid hanging
    
    def on_file_opened_from_explorer(self, file_path: str) -> None:
        """Handle file opened from Explorer panel."""
        try:
            logger.info(f"Opening file from Explorer: {file_path}")
            
            # Check if file is already open in a tab
            if self.tab_manager:
                # Use direct method access with try/except
                try:
                    existing_index = self.tab_manager.find_tab_by_path(file_path)
                    if isinstance(existing_index, int) and existing_index >= 0:
                        # Tab exists, switch to it
                        self.tab_manager.setCurrentIndex(existing_index)
                        logger.info(f"Switched to existing tab for: {file_path}")
                        return
                except AttributeError:
                    logger.warning("tab_manager.find_tab_by_path method not available")
                
                # Open new tab for the file
                from pathlib import Path
                file_name = Path(file_path).name
                
                # Create appropriate editor widget based on file type
                editor_widget = self.create_editor_for_file(file_path)
                if editor_widget:
                    tab_index = self.tab_manager.add_tab(editor_widget, file_name)
                    self.tab_manager.setCurrentIndex(tab_index)
                    logger.info(f"Opened file in new tab: {file_path}")
                else:
                    logger.warning(f"Could not create editor for file: {file_path}")
            
            # Update status bar
            self.statusBar().showMessage(f"Opened: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to handle file opened from Explorer: {e}")
            self.statusBar().showMessage(f"Error opening file: {file_path}")
    
    def on_explorer_location_changed(self, path: str) -> None:
        """Handle location change in Explorer panel."""
        try:
            logger.debug(f"Explorer location changed to: {path}")
            
            # Update window title to show current directory
            from pathlib import Path
            dir_name = Path(path).name or Path(path).parts[-1] if Path(path).parts else "Root"
            self.setWindowTitle(f"POEditor - {dir_name}")
            
            # Update status bar
            self.statusBar().showMessage(f"Explorer: {path}")
            
        except Exception as e:
            logger.error(f"Failed to handle Explorer location change: {e}")
    
    def create_editor_for_file(self, file_path: str) -> Optional[QWidget]:
        """
        Create an appropriate editor widget for the given file.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            QWidget: Editor widget or None if unsupported file type
        """
        try:
            from pathlib import Path
            
            file_extension = Path(file_path).suffix.lower()
            
            # Handle different file types
            if file_extension in ['.po', '.pot']:
                # PO/POT files - create translation editor
                return self.create_translation_editor(file_path)
            elif file_extension in ['.txt', '.md', '.py', '.js', '.json', '.xml']:
                # Text files - create text editor
                return self.create_text_editor(file_path)
            else:
                # Unsupported file type
                logger.warning(f"Unsupported file type: {file_extension}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create editor for file {file_path}: {e}")
            return None
    
    def create_translation_editor(self, file_path: str) -> Optional[QWidget]:
        """Create a translation editor for PO/POT files."""
        try:
            # Use our custom FileAwareTextEdit instead of standard QTextEdit
            editor = FileAwareTextEdit()
            
            # Load file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.setPlainText(content)
                logger.info(f"Loaded translation file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load file content: {e}")
                editor.setPlainText(f"Error loading file: {e}")
            
            # Store file path in widget for saving
            editor.file_path = file_path
            
            return editor
            
        except Exception as e:
            logger.error(f"Failed to create translation editor: {e}")
            return None
    
    def create_text_editor(self, file_path: str) -> Optional[QWidget]:
        """Create a text editor for general text files."""
        try:
            # Use our custom FileAwareTextEdit
            editor = FileAwareTextEdit()
            
            # Load file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.setPlainText(content)
                logger.info(f"Loaded text file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load file content: {e}")
                editor.setPlainText(f"Error loading file: {e}")
            
            # Store file path in widget for saving
            editor.file_path = file_path
            
            return editor
            
        except Exception as e:
            logger.error(f"Failed to create text editor: {e}")
            return None
    
    def setup_typography_system(self) -> None:
        """Initialize and configure the typography system."""
        try:
            logger.info("Initializing typography system")
            
            # Import typography modules only when needed
            from themes.typography import get_typography_manager, get_font, FontRole
            
            # Get typography manager
            self.typography_manager = get_typography_manager()
            
            # Apply global font configuration to QApplication
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                # Set the application default font
                default_font = get_font(FontRole.DEFAULT)
                app.setFont(default_font)
                logger.info(f"Applied default font to application: {default_font.family()}, {default_font.pointSize()}pt")
            
            # Connect to typography change signals for global updates
            self.typography_manager.fonts_changed.connect(self._on_global_typography_changed)
            theme_manager.theme_changed.connect(self._on_global_theme_changed)
            
            logger.info("Typography system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize typography system: {e}")
            # Continue with default fonts if typography system fails
    
    def _on_global_typography_changed(self):
        """Handle global typography changes."""
        try:
            logger.info("Global typography changed, updating application")
            
            # Import typography modules only when needed
            from themes.typography import get_font, FontRole
            
            # Update application default font
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                default_font = get_font(FontRole.DEFAULT)
                app.setFont(default_font)
            
            # Propagate change to all components
            self._propagate_typography_changes()
            
        except Exception as e:
            logger.error(f"Failed to handle global typography change: {e}")
    
    def _on_global_theme_changed(self, theme):
        """Handle global theme changes."""
        try:
            # Handle both Theme objects and string theme names
            try:
                theme_name = theme.name
            except AttributeError:
                theme_name = str(theme)
            logger.info(f"Global theme changed to: {theme_name}")
            
            # Update application styling
            self.apply_styles()
            
            # Propagate change to all components
            self._propagate_theme_changes(theme_name)
            
        except Exception as e:
            logger.error(f"Failed to handle global theme change: {e}")
    
    def _propagate_typography_changes(self):
        """Propagate typography changes to all UI components."""
        try:
            # Import typography modules only when needed
            from themes.typography import get_font, FontRole
            
            # Update menu bar - menuBar() always returns a valid QMenuBar
            self.menuBar().setFont(get_font(FontRole.MENU))
            
            # Update status bar - statusBar() always returns a valid QStatusBar
            self.statusBar().setFont(get_font(FontRole.SMALL))
            
            # Tab manager handles its own typography updates
            if self.tab_manager:
                # Use direct method access with try/except
                try:
                    self.tab_manager._on_typography_changed()
                except AttributeError:
                    logger.warning("tab_manager._on_typography_changed method not available")
                    
            # Activity bar handles its own typography updates
            if self.activity_bar:
                # Use direct method access with try/except
                try:
                    self.activity_bar._on_typography_changed()
                except AttributeError:
                    logger.warning("activity_bar._on_typography_changed method not available")
            
            # Note: SidebarManager doesn't have typography methods (it's just a container)
            
            logger.info("Typography changes propagated to all components")
            
        except Exception as e:
            logger.error(f"Failed to propagate typography changes: {e}")
    
    def _propagate_theme_changes(self, theme_name: str):
        """Propagate theme changes to all UI components."""
        try:
            # Tab manager handles its own theme updates
            if self.tab_manager:
                # Use direct method access with try/except
                try:
                    self.tab_manager._on_theme_changed(theme_name)
                except AttributeError:
                    logger.warning("tab_manager._on_theme_changed method not available")
                    
            # Activity bar handles its own theme updates
            if self.activity_bar:
                # Use direct method access with try/except
                try:
                    self.activity_bar._on_theme_changed(theme_name)
                except AttributeError:
                    logger.warning("activity_bar._on_theme_changed method not available")
            
            # Note: SidebarManager doesn't have theme methods (it's just a container)
            
            logger.info(f"Theme changes propagated to all components: {theme_name}")
            
        except Exception as e:
            logger.error(f"Failed to propagate theme changes: {e}")

    def apply_global_typography(self):
        """Public method to apply global typography to all components.
        
        This method is part of the Phase 3 typography integration public API.
        It triggers a global typography update across all UI components.
        """
        try:
            logger.info("Applying global typography to all components")
            self._propagate_typography_changes()
            logger.info("Global typography application completed")
        except Exception as e:
            logger.error(f"Failed to apply global typography: {e}")
    
    def apply_global_theme(self):
        """Public method to apply global theme to all components.
        
        This method is part of the Phase 3 theme integration public API.
        It triggers a global theme update across all UI components.
        """
        try:
            logger.info("Applying global theme to all components")
            # Get current theme name and propagate
            current_theme = theme_manager.get_current_theme()
            theme_name = current_theme.name if current_theme else 'Light'
            self._propagate_theme_changes(theme_name)
            logger.info(f"Global theme application completed: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to apply global theme: {e}")
