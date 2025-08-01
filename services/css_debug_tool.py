"""CSS Debug Tool for theme development

Provides development utilities for CSS debugging and hot-reloading.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
import json

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QApplication, QDialog, QTabWidget, QTextEdit,
    QCheckBox, QSpinBox, QComboBox, QFileSystemWatcher
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QColor, QPalette

from lg import logger
from services.css_preprocessor import CSSPreprocessor
from services.enhanced_theme_manager import EnhancedThemeManager

class CSSDebugTool(QDialog):
    """CSS Debug Tool window for theme development"""

    def __init__(self, theme_manager: EnhancedThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.preprocessor = theme_manager.preprocessor
        self.watcher = QFileSystemWatcher()
        self.watched_files = set()

        self.setWindowTitle("CSS Debug Tool")
        self.setMinimumSize(800, 600)

        # Initialize UI
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Setup file watcher
        self._setup_file_watcher()

        # Populate initial data
        self._populate_theme_combo()
        self._populate_variables_tree()

        logger.info("CSS Debug Tool initialized")

    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Controls area
        controls_layout = QHBoxLayout()

        # Theme selector
        theme_layout = QVBoxLayout()
        theme_label = QLabel("Current Theme:")
        self.theme_combo = QComboBox()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)

        # Hot reload controls
        reload_layout = QVBoxLayout()
        self.auto_reload_check = QCheckBox("Auto Reload")
        self.auto_reload_check.setChecked(True)
        self.reload_interval_spin = QSpinBox()
        self.reload_interval_spin.setRange(1, 10)
        self.reload_interval_spin.setValue(2)
        self.reload_interval_spin.setSuffix(" sec")
        self.manual_reload_btn = QPushButton("Reload CSS Now")
        reload_layout.addWidget(self.auto_reload_check)
        reload_layout.addWidget(self.reload_interval_spin)
        reload_layout.addWidget(self.manual_reload_btn)

        # Add to controls layout
        controls_layout.addLayout(theme_layout)
        controls_layout.addLayout(reload_layout)
        controls_layout.addStretch()

        # Tabs
        self.tabs = QTabWidget()

        # Variables tab
        self.variables_tab = QWidget()
        variables_layout = QVBoxLayout(self.variables_tab)
        self.variables_tree = QTreeWidget()
        self.variables_tree.setHeaderLabels(["Variable", "Value"])
        self.variables_tree.setColumnWidth(0, 300)
        variables_layout.addWidget(self.variables_tree)

        # CSS Output tab
        self.css_output_tab = QWidget()
        css_output_layout = QVBoxLayout(self.css_output_tab)
        self.css_output_text = QTextEdit()
        self.css_output_text.setReadOnly(True)
        self.css_output_text.setFont(QFont("Courier New", 10))
        css_output_layout.addWidget(self.css_output_text)

        # File Watcher tab
        self.file_watcher_tab = QWidget()
        file_watcher_layout = QVBoxLayout(self.file_watcher_tab)
        self.watched_files_tree = QTreeWidget()
        self.watched_files_tree.setHeaderLabels(["File", "Last Modified"])
        self.watched_files_tree.setColumnWidth(0, 500)
        file_watcher_layout.addWidget(self.watched_files_tree)

        # Add tabs
        self.tabs.addTab(self.variables_tab, "Variables")
        self.tabs.addTab(self.css_output_tab, "CSS Output")
        self.tabs.addTab(self.file_watcher_tab, "File Watcher")

        # Add to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.tabs)

        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

    def _connect_signals(self):
        """Connect UI signals to slots"""
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self.manual_reload_btn.clicked.connect(self._reload_css)
        self.auto_reload_check.stateChanged.connect(self._toggle_auto_reload)
        self.watcher.fileChanged.connect(self._on_file_changed)

        # Setup auto-reload timer
        self.reload_timer = QTimer(self)
        self.reload_timer.timeout.connect(self._reload_css)
        self._toggle_auto_reload()

    def _setup_file_watcher(self):
        """Setup file system watcher for CSS files"""
        themes_dir = Path(self.preprocessor.themes_dir)

        # Watch all CSS files in themes directory
        for root, _, files in os.walk(themes_dir):
            for file in files:
                if file.endswith(".css"):
                    file_path = os.path.join(root, file)
                    self.watcher.addPath(file_path)
                    self.watched_files.add(file_path)

        # Update watched files tree
        self._update_watched_files_tree()

    def _populate_theme_combo(self):
        """Populate theme selector combobox"""
        themes = self.theme_manager.get_theme_list()
        current_theme = self.theme_manager.get_current_theme()

        self.theme_combo.clear()
        self.theme_combo.addItems(themes)

        # Set current theme
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

    def _populate_variables_tree(self):
        """Populate variables tree with current theme variables"""
        self.variables_tree.clear()

        current_theme = self.theme_manager.get_current_theme()

        # Get base variables
        base_vars_path = os.path.join(self.preprocessor.themes_dir, "base", "variables.css")
        base_vars = self.preprocessor.parse_css_file(base_vars_path)

        # Get theme variables
        theme_vars_path = os.path.join(self.preprocessor.themes_dir, "variants", f"{current_theme}.css")
        theme_vars = self.preprocessor.parse_css_file(theme_vars_path)

        # Create tree items
        base_root = QTreeWidgetItem(self.variables_tree, ["Base Variables", ""])
        theme_root = QTreeWidgetItem(self.variables_tree, ["Theme Variables", ""])

        # Sort variables by name
        sorted_base_vars = sorted(base_vars.items())
        sorted_theme_vars = sorted(theme_vars.items())

        # Add base variables
        for name, value in sorted_base_vars:
            QTreeWidgetItem(base_root, [f"--{name}", value])

        # Add theme variables
        for name, value in sorted_theme_vars:
            item = QTreeWidgetItem(theme_root, [f"--{name}", value])

            # Highlight if overriding base variable
            if name in base_vars:
                # Visual indication of override
                item.setBackground(0, QColor(240, 240, 255))
                item.setBackground(1, QColor(240, 240, 255))

        # Expand roots
        base_root.setExpanded(True)
        theme_root.setExpanded(True)

        # Update CSS output
        self._update_css_output()

    def _update_css_output(self):
        """Update CSS output text"""
        current_theme = self.theme_manager.get_current_theme()
        css = self.theme_manager.load_theme(current_theme)

        self.css_output_text.setText(css)

    def _update_watched_files_tree(self):
        """Update watched files tree"""
        self.watched_files_tree.clear()

        # Group files by directory
        files_by_dir = {}
        for file_path in sorted(self.watched_files):
            dir_name = os.path.dirname(file_path)
            if dir_name not in files_by_dir:
                files_by_dir[dir_name] = []
            files_by_dir[dir_name].append(file_path)

        # Add to tree
        for dir_name, files in sorted(files_by_dir.items()):
            dir_item = QTreeWidgetItem(self.watched_files_tree, [dir_name, ""])

            for file_path in sorted(files):
                file_name = os.path.basename(file_path)
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
                QTreeWidgetItem(dir_item, [file_name, mtime])

            dir_item.setExpanded(True)

    def _on_theme_changed(self, theme_name):
        """Handle theme selection change"""
        if not theme_name:
            return

        # Switch theme
        success = self.theme_manager.switch_theme(theme_name)
        if success:
            # Apply to application
            app = QApplication.instance()
            if app:
                self.theme_manager.apply_theme_to_application(app)

            # Update UI
            self._populate_variables_tree()
            self.status_label.setText(f"Switched to theme: {theme_name}")
        else:
            self.status_label.setText(f"Failed to switch to theme: {theme_name}")

    def _reload_css(self):
        """Reload CSS and update application"""
        # Clear caches
        self.theme_manager.reload_styles()

        # Apply to application
        app = QApplication.instance()
        if app:
            self.theme_manager.apply_theme_to_application(app)

        # Update UI
        self._populate_variables_tree()
        self._update_watched_files_tree()

        # Update status
        self.status_label.setText(f"CSS reloaded at {time.strftime('%H:%M:%S')}")

    def _toggle_auto_reload(self):
        """Toggle auto-reload timer"""
        if self.auto_reload_check.isChecked():
            interval_sec = self.reload_interval_spin.value()
            self.reload_timer.start(interval_sec * 1000)
            self.status_label.setText(f"Auto-reload enabled ({interval_sec}s interval)")
        else:
            self.reload_timer.stop()
            self.status_label.setText("Auto-reload disabled")

        # Update UI state
        self.reload_interval_spin.setEnabled(self.auto_reload_check.isChecked())

    def _on_file_changed(self, file_path):
        """Handle file change notification"""
        self.status_label.setText(f"File changed: {os.path.basename(file_path)}")

        # Re-add the file to the watcher (needed on some platforms)
        if os.path.exists(file_path):
            self.watcher.addPath(file_path)

        # Reload if auto-reload is enabled
        if self.auto_reload_check.isChecked():
            # Small delay to allow multiple files to be saved
            QTimer.singleShot(100, self._reload_css)


class CSSInspector(QWidget):
    """Widget inspector for debugging CSS selectors and properties"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSS Inspector")
        self.setMinimumSize(600, 400)

        # Initialize UI
        self._init_ui()

        # Timer for inspection
        self.inspect_timer = QTimer(self)
        self.inspect_timer.timeout.connect(self._inspect_current_widget)
        self.inspect_timer.start(500)  # Check every 500ms

    def _init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.inspect_check = QCheckBox("Enable Inspection")
        self.inspect_check.setChecked(True)
        controls_layout.addWidget(self.inspect_check)
        controls_layout.addStretch()

        # Properties tabs
        self.tabs = QTabWidget()

        # Widget Info tab
        self.widget_info_tab = QWidget()
        widget_info_layout = QVBoxLayout(self.widget_info_tab)
        self.widget_info_text = QTextEdit()
        self.widget_info_text.setReadOnly(True)
        widget_info_layout.addWidget(self.widget_info_text)

        # CSS Properties tab
        self.css_props_tab = QWidget()
        css_props_layout = QVBoxLayout(self.css_props_tab)
        self.css_props_tree = QTreeWidget()
        self.css_props_tree.setHeaderLabels(["Property", "Value"])
        css_props_layout.addWidget(self.css_props_tree)

        # Add tabs
        self.tabs.addTab(self.widget_info_tab, "Widget Info")
        self.tabs.addTab(self.css_props_tab, "CSS Properties")

        # Add to layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.tabs)

    def _inspect_current_widget(self):
        """Inspect widget under mouse cursor"""
        if not self.inspect_check.isChecked():
            return

        app = QApplication.instance()
        if not app:
            return

        # Get widget under cursor
        pos = app.primaryScreen().cursor().pos()
        widget = app.widgetAt(pos)

        if widget:
            self._update_widget_info(widget)
            self._update_css_properties(widget)

    def _update_widget_info(self, widget):
        """Update widget info text"""
        info = [
            f"Class: {widget.__class__.__name__}",
            f"ObjectName: {widget.objectName()}",
            f"Size: {widget.width()}x{widget.height()}",
            f"Visible: {widget.isVisible()}",
            "\nProperties:"
        ]

        # Get dynamic properties
        for prop in widget.dynamicPropertyNames():
            prop_name = bytes(prop).decode()
            prop_value = widget.property(prop_name)
            info.append(f"  {prop_name}: {prop_value}")

        # Get stylesheet
        if widget.styleSheet():
            info.append("\nStyleSheet:")
            info.append(widget.styleSheet())

        self.widget_info_text.setText("\n".join(info))

    def _update_css_properties(self, widget):
        """Update CSS properties tree"""
        self.css_props_tree.clear()

        # This is a simplified approach - in a real implementation,
        # you would need to parse the applied CSS and determine which
        # properties are actually applied to the widget

        # For now, just show some common properties from the palette
        palette = widget.palette()
        colors_item = QTreeWidgetItem(self.css_props_tree, ["Colors", ""])

        # Add color roles
        roles = [
            ("background", QPalette.Base),
            ("background-color", QPalette.Window),
            ("color", QPalette.WindowText),
            ("border-color", QPalette.Mid)
        ]

        for name, role in roles:
            color = palette.color(role)
            value = f"rgb({color.red()}, {color.green()}, {color.blue()})" 
            QTreeWidgetItem(colors_item, [name, value])

        colors_item.setExpanded(True)


def launch_css_debug_tool(theme_manager=None):
    """Launch the CSS Debug Tool

    Args:
        theme_manager: Optional EnhancedThemeManager instance
    """
    # Create theme manager if not provided
    if theme_manager is None:
        theme_manager = EnhancedThemeManager()

    # Create and show debug tool
    debug_tool = CSSDebugTool(theme_manager)
    debug_tool.show()

    return debug_tool


def launch_css_inspector():
    """Launch the CSS Inspector tool"""
    inspector = CSSInspector()
    inspector.show()

    return inspector


if __name__ == "__main__":
    # For standalone testing
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    theme_manager = EnhancedThemeManager()
    debug_tool = launch_css_debug_tool(theme_manager)
    inspector = launch_css_inspector()

    sys.exit(app.exec())
