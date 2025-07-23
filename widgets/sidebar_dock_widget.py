"""
SidebarDockWidget for POEditor application.

Wraps SidebarManager and provides a toolbar with an arrow button to show/hide a menu for dock options (left/right).
Prevents closing and allows docking only left/right.
"""
from typing import Optional
from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QToolBar, QPushButton, QMenu, QMainWindow
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QEvent
from lg import logger

class SidebarDockWidget(QDockWidget):
    def __init__(self, sidebar_manager: QWidget, parent: Optional[QWidget] = None):
        super().__init__("Sidebar", parent)
        self.sidebar_manager = sidebar_manager
        self._main_window_parent = parent  # Store reference to the main window
        self.setObjectName("SidebarDockWidget")
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.setWidget(self._wrap_with_toolbar(sidebar_manager))

        # Connect floating state change signal for logging
        self.topLevelChanged.connect(self._on_floating_changed)

        logger.info(f"SidebarDockWidget initialized with parent: {type(parent).__name__ if parent else 'None'}")

    def _wrap_with_toolbar(self, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Toolbar with arrow button
        toolbar = QToolBar()
        toolbar.setMovable(False)
        arrow_btn = QPushButton("▼")
        arrow_btn.setToolTip("Sidebar options")
        arrow_btn.clicked.connect(self._show_menu)
        toolbar.addWidget(arrow_btn)
        layout.addWidget(toolbar)
        layout.addWidget(widget)
        self._arrow_btn = arrow_btn
        logger.debug("SidebarDockWidget toolbar with arrow button created")
        return container

    def _on_floating_changed(self, floating: bool):
        """Log when floating state changes."""
        state = "floating" if floating else "docked"
        current_parent = type(self.parent()).__name__ if self.parent() else "None"
        logger.info(f"SidebarDockWidget floating state changed to: {state}, current parent: {current_parent}")

    def _show_menu(self):
        logger.debug("SidebarDockWidget menu requested")
        menu = QMenu()

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

        # Show menu and log position
        menu_pos = self._arrow_btn.mapToGlobal(self._arrow_btn.rect().bottomLeft())
        logger.debug(f"Showing sidebar menu at position: {menu_pos}")
        menu.exec_(menu_pos)

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
        logger.warning("Attempted to close SidebarDockWidget - prevented.")
        event.ignore()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Hide:
            logger.warning("Attempted to hide SidebarDockWidget - prevented.")
            return True
        elif event.type() == QEvent.Type.Show:
            logger.debug("SidebarDockWidget show event")
        elif event.type() == QEvent.Type.Move:
            logger.debug("SidebarDockWidget move event")
        elif event.type() == QEvent.Type.Resize:
            logger.debug("SidebarDockWidget resize event")
        return super().event(event)
