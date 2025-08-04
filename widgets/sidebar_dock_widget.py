"""
SidebarDockWidget for POEditor application.

Wraps SidebarManager and provides a toolbar with an arrow button to show/hide a menu for dock options (left/right).
Prevents closing and allows docking only left/right.
"""
from typing import Optional
from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QToolBar, QPushButton, QMenu, QMainWindow, QApplication
from PySide6.QtGui import QAction, QCursor
from PySide6.QtCore import Qt, QEvent, QPoint
from lg import logger

class SidebarDockWidget(QDockWidget):
    def __init__(self, sidebar_manager: QWidget, parent: Optional[QWidget] = None):

        # self.setFeatures(
        #     QDockWidget.DockWidgetFeature.DockWidgetMovable |
        #     QDockWidget.DockWidgetFeature.DockWidgetFloatable |
        #     QDockWidget.DockWidgetFeature.DockWidgetClosable
        # )

        # Debug: Log theme state before initialization
        logger.info("=== THEME DEBUG: Before SidebarDockWidget initialization ===")
        if parent:
            logger.info(f"Parent style: {type(parent.style()).__name__}")
            logger.info(f"Parent palette: {parent.palette()}")

        super().__init__("Sidebar", parent)
        self.sidebar_manager = sidebar_manager
        self._main_window_parent = parent
        self._is_app_closing = False  # Track if app is closing
        self._force_close_requested = False  # Track if force close was requested

        # Note: Status bar styling is handled in common.css to ensure consistency across themes
        # The status bar should always maintain VS Code-like appearance regardless of theme changes

        # Debug: Log theme state after super init
        logger.info("=== THEME DEBUG: After super().__init__ ===")
        logger.info(f"DockWidget style: {type(self.style()).__name__}")
        logger.info(f"DockWidget palette: {self.palette()}")

        # Force the dock widget to use stylesheet styling
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        # # Apply explicit styling to override Qt's native gradient
        # self.setStyleSheet("""
        #     QDockWidget {
        #         background-color: #252526;
        #         color: #cccccc;
        #         border: 1px solid #464647;
        #     }
        #     QDockWidget::title {
        #         background-color: #252526;
        #         color: #cccccc;
        #         padding: 4px;
        #         padding-left: 8px;
        #         text-align: left;
        #         border: none;
        #         font-weight: bold;
        #         text-transform: uppercase;
        #         font-size: 11px;
        #         letter-spacing: 1px;
        #     }
        # """)

        self.setObjectName("SidebarDockWidget")
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        # Remove global context menu policy - let child widgets handle their own
        self.setWidget(self._wrap_with_toolbar(sidebar_manager))

        # Install event filter to detect title bar clicks
        self.installEventFilter(self)

        # Debug: Log theme state after widget setup
        logger.info("=== THEME DEBUG: After complete widget setup ===")
        logger.info(f"Final DockWidget style: {type(self.style()).__name__}")
        logger.info(f"Final DockWidget palette: {self.palette()}")

        # Connect floating state change signal for logging
        self.topLevelChanged.connect(self._on_floating_changed)

        # Connect to application quit signal to ensure proper cleanup
        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self._on_app_about_to_quit)
            logger.info("Connected to QApplication.aboutToQuit signal for proper cleanup")

        # Connect to main window destroyed signal if available
        if isinstance(parent, QMainWindow):
            parent.destroyed.connect(self._on_main_window_destroyed)
            logger.info("Connected to main window destroyed signal")

            # Monkey patch the main window's closeEvent to ensure we know when it's closing
            self._original_main_window_close = parent.closeEvent
            parent.closeEvent = self._main_window_close_wrapper
            logger.info("Monkey patched main window closeEvent")

        logger.info(f"SidebarDockWidget initialized with parent: {type(parent).__name__ if parent else 'None'}")

    def _main_window_close_wrapper(self, event):
        """Wrap the main window's closeEvent to ensure we get notified before it closes."""
        logger.info("Main window closeEvent triggered - marking sidebar for forced closure")
        self._is_app_closing = True
        self._force_close_requested = True

        # Force close immediately if floating
        if self.isFloating():
            logger.info("Sidebar is floating during main window close - forcing immediate closure")
            self.hide()
            self.setParent(None)
            self.close()

        # Call the original closeEvent
        if hasattr(self, '_original_main_window_close'):
            self._original_main_window_close(event)

    def _on_main_window_destroyed(self):
        """Handle main window destruction."""
        logger.info("Main window being destroyed - marking app as closing")
        self._is_app_closing = True
        self._force_close_requested = True

    def _on_app_about_to_quit(self):
        """Handle application quit to ensure sidebar closes properly."""
        logger.info("Application is about to quit - forcing sidebar to close")
        self._is_app_closing = True
        self._force_close_requested = True

        # Force close the sidebar immediately
        if self.isVisible():
            logger.info("Sidebar is visible - forcing close")
            # Use deleteLater() to ensure proper cleanup
            self.deleteLater()

        # Also close any child widgets
        if hasattr(self, 'sidebar_manager') and self.sidebar_manager:
            logger.info("Closing sidebar manager")
            self.sidebar_manager.close()

    def _wrap_with_toolbar(self, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Toolbar with arrow button
        # toolbar = QToolBar()
        # toolbar.setObjectName("sidebar_toolbar")  # Set object name for CSS targeting
        # toolbar.setMovable(False)

        # Debug: Log toolbar styling information
        # logger.info("=== THEME DEBUG: Toolbar creation ===")
        # logger.info(f"Toolbar stylesheet: '{toolbar.styleSheet()}'")
        # logger.info(f"Toolbar palette: {toolbar.palette()}")
        # logger.info(f"Toolbar background role: {toolbar.backgroundRole()}")
        # logger.info(f"Toolbar auto fill background: {toolbar.autoFillBackground()}")
        # logger.info(f"Application style name: {toolbar.style().objectName()}")
        # logger.info(f"Toolbar style object: {type(toolbar.style()).__name__}")

        # arrow_btn = QPushButton("▼")
        # arrow_btn.setObjectName("sidebar_arrow_button")  # Set object name for CSS targeting
        # arrow_btn.setToolTip("Sidebar options")
        # arrow_btn.clicked.connect(self._show_menu)

        # Debug: Log button styling information
        # logger.info("=== THEME DEBUG: Arrow button creation ===")
        # logger.info(f"Arrow button stylesheet: '{arrow_btn.styleSheet()}'")
        # logger.info(f"Arrow button palette: {arrow_btn.palette()}")
        # logger.info(f"Arrow button background role: {arrow_btn.backgroundRole()}")

        # toolbar.addWidget(arrow_btn)

        # Debug: Log final toolbar state after adding button
        # logger.info(f"Final toolbar size hint: {toolbar.sizeHint()}")
        # logger.info(f"Final toolbar minimum size: {toolbar.minimumSize()}")

        # layout.addWidget(toolbar)
        layout.addWidget(widget)
        # self._arrow_btn = arrow_btn
        logger.debug("SidebarDockWidget toolbar with arrow button created")
        return container

    def _on_floating_changed(self, floating: bool):
        """Log when floating state changes."""
        state = "floating" if floating else "docked"
        current_parent = type(self.parent()).__name__ if self.parent() else "None"
        logger.info(f"SidebarDockWidget floating state changed to: {state}, current parent: {current_parent}")

    def eventFilter(self, obj, event):
        """Filter events to detect right-clicks on title bar only."""
        if obj == self and event.type() == QEvent.Type.ContextMenu:
            # Check if the click is on the title bar area
            if self._is_click_on_title_bar(event.pos()):
                logger.debug("Right-click detected on title bar")
                self._show_menu(event.pos())
                return True  # Event handled, don't propagate
            else:
                logger.debug("Right-click detected outside title bar, allowing propagation")
                return False  # Let the event propagate to child widgets

        return super().eventFilter(obj, event)

    def _is_click_on_title_bar(self, pos: QPoint) -> bool:
        """Check if the given position is within the title bar area."""
        # Get the title bar rect - this is approximate as Qt doesn't expose exact title bar geometry
        # The title bar is typically at the top of the widget
        widget_rect = self.rect()

        # Estimate title bar height (usually around 20-30 pixels depending on style)
        # This is a reasonable approximation for most desktop environments
        title_bar_height = 30

        # Check if click is in the top area where title bar would be
        title_bar_rect = widget_rect.adjusted(0, 0, 0, -widget_rect.height() + title_bar_height)

        logger.debug(f"Click position: {pos}, Title bar area: {title_bar_rect}, Widget rect: {widget_rect}")
        return title_bar_rect.contains(pos)

    def _show_menu(self, pos: Optional[QPoint] = None):
        logger.debug("SidebarDockWidget menu requested from title bar")
        menu = QMenu(self)

        # # Set object name to match CSS selector in dark_theme.css
        # menu.setObjectName("sidebar_context_menu")

        # # Try to force menu to pick up application styling
        # # This addresses the issue where dynamically created QMenu widgets
        # # sometimes don't inherit the application's stylesheet correctly
        # from PySide6.QtWidgets import QApplication
        # app = QApplication.instance()
        # if app:
        #     # Ensure the menu inherits the application's stylesheet
        #     current_stylesheet = app.styleSheet()
        #     if current_stylesheet:
        #         logger.debug("Applying application stylesheet to context menu")
        #         menu.setStyle(app.style())

        #         # Note: We don't set the stylesheet directly here
        #         # because it's already defined in dark_theme.css

        # Enable window drop shadow for the menu if possible
        try:
            # This is platform-dependent and might not work on all systems
            if hasattr(menu, 'setWindowFlag') and hasattr(Qt, 'WindowType'):
                menu.setWindowFlag(Qt.WindowType.FramelessWindowHint)
                if hasattr(menu, 'setAttribute') and hasattr(Qt, 'WidgetAttribute'):
                    menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            logger.debug("Applied translucent background for better drop shadow visibility")
        except Exception as e:
            logger.debug(f"Could not set advanced window styling for menu: {e}")

        # Add dock options
        left_action = QAction("Dock Left", self)
        left_action.triggered.connect(lambda: self._move_to_area(Qt.DockWidgetArea.LeftDockWidgetArea))
        menu.addAction(left_action)

        right_action = QAction("Dock Right", self)
        right_action.triggered.connect(lambda: self._move_to_area(Qt.DockWidgetArea.RightDockWidgetArea))
        menu.addAction(right_action)

        # Add separator
        menu.addSeparator()

        # Add float/dock toggle
        is_floating = self.isFloating()
        logger.debug(f"SidebarDockWidget current state: {'floating' if is_floating else 'docked'}")

        if is_floating:
            dock_action = QAction("Dock Sidebar", self)
            dock_action.triggered.connect(self._dock_sidebar)
            menu.addAction(dock_action)
            logger.debug("Added 'Dock Sidebar' option to menu")
        else:
            float_action = QAction("Float Sidebar", self)
            float_action.triggered.connect(self._float_sidebar)
            menu.addAction(float_action)
            logger.debug("Added 'Float Sidebar' option to menu")

        # Show the menu at the context menu position or cursor position
        if pos is not None:
            logger.debug(f"Showing sidebar menu at position: {pos}")
            menu.exec_(self.mapToGlobal(pos))
        else:
            logger.debug("Showing sidebar menu at cursor position")
            menu.exec_(QCursor.pos())

    def _move_to_area(self, area: Qt.DockWidgetArea):
        """Move the sidebar to the specified dock area."""
        area_name = {
            Qt.DockWidgetArea.LeftDockWidgetArea: "Left",
            Qt.DockWidgetArea.RightDockWidgetArea: "Right",
            Qt.DockWidgetArea.TopDockWidgetArea: "Top",
            Qt.DockWidgetArea.BottomDockWidgetArea: "Bottom"
        }.get(area, "Unknown")

        logger.info(f"SidebarDockWidget move to {area_name} area requested")

        try:
            # Log current state
            was_floating = self.isFloating()
            current_parent = type(self.parent()).__name__ if self.parent() else "None"
            logger.debug(f"Current state - Floating: {was_floating}, Parent: {current_parent}")
            logger.debug(f"Stored main window parent: {type(self._main_window_parent).__name__ if self._main_window_parent else 'None'}")

            # Ensure we're docked first
            if was_floating:
                logger.debug("Setting floating to False before moving")
                self.setFloating(False)

            # Use the stored main window reference
            if self._main_window_parent and isinstance(self._main_window_parent, QMainWindow):
                logger.debug(f"Adding dock widget to {area_name} area using stored parent reference")
                self._main_window_parent.addDockWidget(area, self)
                logger.info(f"SidebarDockWidget successfully moved to {area_name} area")

                # Verify the move
                new_parent = type(self.parent()).__name__ if self.parent() else "None"
                is_floating = self.isFloating()
                logger.debug(f"After move - Floating: {is_floating}, Parent: {new_parent}")
            else:
                error_msg = f"Cannot move sidebar: main window reference not available or invalid"
                logger.error(error_msg)
                logger.debug(f"Parent check - Has parent: {self._main_window_parent is not None}, Is QMainWindow: {isinstance(self._main_window_parent, QMainWindow) if self._main_window_parent else False}")

        except Exception as e:
            logger.error(f"Failed to move sidebar to {area_name} area: {e}")
            logger.exception("Full traceback for sidebar move error:")

    def _dock_sidebar(self):
        """Dock the floating sidebar to the left area."""
        logger.info("SidebarDockWidget dock from floating requested")
        try:
            # Log current state
            was_floating = self.isFloating()
            current_parent = type(self.parent()).__name__ if self.parent() else "None"
            logger.debug(f"Before docking - Floating: {was_floating}, Parent: {current_parent}")

            # Set floating to false first
            logger.debug("Setting floating to False")
            self.setFloating(False)

            # Move to left area when docking from float
            logger.debug("Moving to left area after setting floating to False")
            self._move_to_area(Qt.DockWidgetArea.LeftDockWidgetArea)

            # Verify final state
            final_floating = self.isFloating()
            final_parent = type(self.parent()).__name__ if self.parent() else "None"
            logger.info(f"Sidebar docked from floating state - Final state: Floating: {final_floating}, Parent: {final_parent}")

        except Exception as e:
            logger.error(f"Failed to dock sidebar from floating: {e}")
            logger.exception("Full traceback for dock sidebar error:")

    def _float_sidebar(self):
        """Make the sidebar floating."""
        logger.info("SidebarDockWidget float requested")
        try:
            # Log current state
            was_floating = self.isFloating()
            current_parent = type(self.parent()).__name__ if self.parent() else "None"
            logger.debug(f"Before floating - Floating: {was_floating}, Parent: {current_parent}")

            # Set to floating
            logger.debug("Setting floating to True")
            self.setFloating(True)

            # Verify final state
            final_floating = self.isFloating()
            final_parent = type(self.parent()).__name__ if self.parent() else "None"
            logger.info(f"Sidebar set to floating state - Final state: Floating: {final_floating}, Parent: {final_parent}")

        except Exception as e:
            logger.error(f"Failed to float sidebar: {e}")
            logger.exception("Full traceback for float sidebar error:")

    def closeEvent(self, event):
        """Handle close events - prevent user closure but allow app closure."""
        # Additional check for main window status
        main_window_closing = False
        if self._main_window_parent:
            # Check if main window is in the process of closing
            try:
                main_window_closing = (not self._main_window_parent.isVisible())
            except (RuntimeError, AttributeError):
                # If we get an error accessing the main window, it's likely being destroyed
                main_window_closing = True

        if self._is_app_closing or self._force_close_requested or main_window_closing:
            logger.info(f"SidebarDockWidget closing due to application shutdown (app_closing={self._is_app_closing}, force_requested={self._force_close_requested}, main_window_closing={main_window_closing})")

            # Remove all signal connections to prevent callback errors
            try:
                app = QApplication.instance()
                if app:
                    app.aboutToQuit.disconnect(self._on_app_about_to_quit)
            except:
                pass

            # Ensure we really close
            QDockWidget.closeEvent(self, event)
            event.accept()
        else:
            logger.warning("Attempted to close SidebarDockWidget by user - prevented.")
            event.ignore()

    def force_close(self):
        """Force close the sidebar (used during app shutdown)."""
        logger.info("Force closing SidebarDockWidget")
        self._is_app_closing = True
        self._force_close_requested = True
        self.deleteLater()

    def _log_current_theme_state(self, context: str):
        """Log current theme state for debugging."""
        logger.info(f"=== THEME DEBUG: {context} ===")
        logger.info(f"DockWidget style: {type(self.style()).__name__}")
        logger.info(f"DockWidget palette: {self.palette()}")
        logger.info(f"DockWidget stylesheet: '{self.styleSheet()}'")

        # Check toolbar and button if they exist
        # if hasattr(self, '_arrow_btn') and self._arrow_btn:
        #     toolbar = self._arrow_btn.parent()
        #     if toolbar:
        #         logger.info(f"Toolbar style after theme: {type(toolbar.style()).__name__}")
        #         logger.info(f"Toolbar palette after theme: {toolbar.palette()}")
        #         logger.info(f"Toolbar stylesheet after theme: '{toolbar.styleSheet()}'")
        #
        #     logger.info(f"Arrow button style after theme: {type(self._arrow_btn.style()).__name__}")
        #     logger.info(f"Arrow button palette after theme: {self._arrow_btn.palette()}")
        #     logger.info(f"Arrow button stylesheet after theme: '{self._arrow_btn.styleSheet()}'")

        logger.info("Toolbar and arrow button are commented out")

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Hide:
            # Don't prevent hide events during app shutdown
            if self._is_app_closing or self._force_close_requested:
                logger.debug("SidebarDockWidget hide event during shutdown - allowing")
                return super().event(event)
            else:
                logger.warning("Attempted to hide SidebarDockWidget - prevented.")
                return True
        elif event.type() == QEvent.Type.Show:
            logger.debug("SidebarDockWidget show event")
            # Debug: Log theme state on show
            logger.info("=== THEME DEBUG: On Show Event ===")
            logger.info(f"Show event - Style: {type(self.style()).__name__}")
            logger.info(f"Show event - Palette: {self.palette()}")
        elif event.type() == QEvent.Type.Move:
            logger.debug("SidebarDockWidget move event")
        elif event.type() == QEvent.Type.Resize:
            logger.debug("SidebarDockWidget resize event")
        elif event.type() == QEvent.Type.StyleChange:
            logger.info("=== THEME DEBUG: Style Change Event ===")
            logger.info(f"Style changed to: {type(self.style()).__name__}")
        elif event.type() == QEvent.Type.PaletteChange:
            logger.info("=== THEME DEBUG: Palette Change Event ===")
            logger.info(f"Palette changed to: {self.palette()}")
            # Log detailed theme state after palette change
            self._log_current_theme_state("After Palette Change")
        elif event.type() == QEvent.Type.ParentChange:
            logger.info("=== THEME DEBUG: Parent Change Event ===")
            logger.info(f"Parent changed - New style: {type(self.style()).__name__}")
            logger.info(f"Parent changed - New palette: {self.palette()}")

        return super().event(event)
