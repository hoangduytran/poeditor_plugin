"""
Main preferences dialog foundation.

This module provides the core preferences dialog structure that will host
the various preference panels and manage common functionality like themes,
settings persistence, and plugin integration.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QDialogButtonBox, QWidget, QSplitter, QFrame, QLabel,
    QMessageBox, QApplication, QProgressDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QObject
from PySide6.QtGui import QIcon, QCloseEvent

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from lg import logger
from .data_models import PluginPreferenceTab
from .base_components import PreferencePage
from .database import DatabaseManager, DatabaseMigration


class PreferencesDialog(QDialog):
    """Main preferences dialog with tabbed interface and plugin support."""
    
    # Signals
    preferences_changed = Signal()
    database_initialized = Signal()
    plugin_tab_added = Signal(str)  # plugin_id
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("PreferencesDialog")
        self.setWindowTitle("Preferences")
        self.resize(800, 600)
        
        # Core components
        self.db_manager = DatabaseManager()
        self.db_migration = DatabaseMigration(self.db_manager)
        
        # Tab management
        self.preference_pages: Dict[str, PreferencePage] = {}
        self.plugin_tabs: Dict[str, PluginPreferenceTab] = {}
        self._modified_pages: set = set()
        
        # UI components
        self.tab_widget: Optional[QTabWidget] = None
        self.button_box: Optional[QDialogButtonBox] = None
        
        self._setup_ui()
        self._initialize_database()
        self._connect_signals()
        logger.info("PreferencesDialog initialized")
    
    def _setup_ui(self):
        """Setup main dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Main content area
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("PreferencesTabWidget")
        layout.addWidget(self.tab_widget)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Reset
        )
        layout.addWidget(self.button_box)
        
        # Initially disable Apply button
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
    
    def _initialize_database(self):
        """Initialize database in background thread."""
        logger.info("Initializing preferences database")
        
        # For now, initialize synchronously. In production, this could be threaded.
        try:
            if self.db_migration.migrate_to_current():
                self.database_initialized.emit()
                logger.info("Database initialization completed")
            else:
                logger.error("Database initialization failed")
                self._show_database_error()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            self._show_database_error()
    
    def _show_database_error(self):
        """Show database error message to user."""
        QMessageBox.critical(
            self,
            "Database Error",
            "Failed to initialize preferences database. "
            "Some features may not work correctly."
        )
    
    def _connect_signals(self):
        """Connect internal signals."""
        if self.button_box:
            self.button_box.accepted.connect(self._on_ok_clicked)
            self.button_box.rejected.connect(self._on_cancel_clicked)
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply_clicked)
            self.button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self._on_reset_clicked)
    
    def add_preference_page(self, page_id: str, page: PreferencePage, icon: Optional[QIcon] = None):
        """Add a preference page to the dialog."""
        if page_id in self.preference_pages:
            logger.warning(f"Preference page {page_id} already exists")
            return
        
        self.preference_pages[page_id] = page
        
        # Add to tab widget
        if self.tab_widget:
            if icon:
                self.tab_widget.addTab(page, icon, page.title)
            else:
                self.tab_widget.addTab(page, page.title)
        
        # Connect page signals
        page.data_changed.connect(lambda: self._on_page_modified(page_id))
        page.validation_failed.connect(self._on_validation_failed)
        
        logger.debug(f"Added preference page: {page_id}")
    
    def add_plugin_tab(self, plugin_tab: PluginPreferenceTab) -> bool:
        """Add a plugin-contributed preference tab."""
        if not plugin_tab.validate():
            return False
        
        if plugin_tab.plugin_id in self.plugin_tabs:
            logger.warning(f"Plugin tab {plugin_tab.plugin_id} already exists")
            return False
        
        self.plugin_tabs[plugin_tab.plugin_id] = plugin_tab
        
        # Add to tab widget
        if self.tab_widget:
            if plugin_tab.icon:
                tab_index = self.tab_widget.addTab(
                    plugin_tab.tab_widget, plugin_tab.icon, plugin_tab.tab_name
                )
            else:
                tab_index = self.tab_widget.addTab(
                    plugin_tab.tab_widget, plugin_tab.tab_name
                )
            
            # Handle position preference
            if plugin_tab.position >= 0:
                current_index = tab_index
                target_index = min(plugin_tab.position, self.tab_widget.count() - 1)
                if current_index != target_index:
                    # Move tab to desired position
                    widget = self.tab_widget.widget(current_index)
                    text = self.tab_widget.tabText(current_index)
                    icon = self.tab_widget.tabIcon(current_index)
                    
                    self.tab_widget.removeTab(current_index)
                    self.tab_widget.insertTab(target_index, widget, icon, text)
        
        self.plugin_tab_added.emit(plugin_tab.plugin_id)
        logger.info(f"Added plugin preference tab: {plugin_tab.tab_name}")
        return True
    
    def remove_plugin_tab(self, plugin_id: str) -> bool:
        """Remove a plugin preference tab."""
        if plugin_id not in self.plugin_tabs:
            return False
        
        plugin_tab = self.plugin_tabs[plugin_id]
        
        # Find and remove tab from widget
        if self.tab_widget:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == plugin_tab.tab_widget:
                    self.tab_widget.removeTab(i)
                    break
        
        del self.plugin_tabs[plugin_id]
        logger.info(f"Removed plugin preference tab: {plugin_id}")
        return True
    
    def _on_page_modified(self, page_id: str):
        """Handle page modification."""
        self._modified_pages.add(page_id)
        
        # Enable Apply button
        if self.button_box:
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)
    
    def _on_validation_failed(self, message: str):
        """Handle validation failure."""
        QMessageBox.warning(self, "Validation Error", message)
    
    def _on_ok_clicked(self):
        """Handle OK button click."""
        if self._save_all_changes():
            self.accept()
    
    def _on_cancel_clicked(self):
        """Handle Cancel button click."""
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to cancel?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.reject()
        else:
            self.reject()
    
    def _on_apply_clicked(self):
        """Handle Apply button click."""
        if self._save_all_changes():
            # Disable Apply button after successful save
            if self.button_box:
                self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
    
    def _on_reset_clicked(self):
        """Handle Reset button click."""
        reply = QMessageBox.question(
            self,
            "Reset Changes",
            "Are you sure you want to reset all changes to their saved values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._reset_all_changes()
    
    def _save_all_changes(self) -> bool:
        """Save changes from all modified pages."""
        logger.info("Saving preferences changes")
        
        # Validate all pages first
        for page_id in self._modified_pages:
            page = self.preference_pages.get(page_id)
            if page and not page.validate():
                logger.error(f"Validation failed for page: {page_id}")
                return False
        
        # Save changes
        success = True
        for page_id in self._modified_pages:
            page = self.preference_pages.get(page_id)
            if page:
                if not page.save_changes():
                    logger.error(f"Failed to save changes for page: {page_id}")
                    success = False
        
        if success:
            self._modified_pages.clear()
            self.preferences_changed.emit()
            logger.info("All preferences saved successfully")
        
        return success
    
    def _reset_all_changes(self):
        """Reset all pages to their saved state."""
        logger.info("Resetting preferences changes")
        
        for page_id in self._modified_pages:
            page = self.preference_pages.get(page_id)
            if page:
                page.reset_changes()
        
        self._modified_pages.clear()
        
        # Disable Apply button
        if self.button_box:
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
    
    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return len(self._modified_pages) > 0
    
    def get_database_manager(self) -> DatabaseManager:
        """Get database manager for use by preference pages."""
        return self.db_manager
    
    def get_current_page(self) -> Optional[QWidget]:
        """Get currently active preference page."""
        if self.tab_widget:
            return self.tab_widget.currentWidget()
        return None
    
    def switch_to_page(self, page_id: str) -> bool:
        """Switch to specific preference page."""
        if page_id not in self.preference_pages:
            return False
        
        page = self.preference_pages[page_id]
        if self.tab_widget:
            index = self.tab_widget.indexOf(page)
            if index >= 0:
                self.tab_widget.setCurrentIndex(index)
                return True
        
        return False
    
    def closeEvent(self, event: QCloseEvent):
        """Handle dialog close event."""
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if self._save_all_changes():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:  # Cancel
                event.ignore()
        else:
            event.accept()


class PreferencePageRegistry:
    """Registry for managing preference page creation and lifecycle."""
    
    def __init__(self):
        self.page_factories: Dict[str, Callable] = {}
        self.page_metadata: Dict[str, Dict[str, Any]] = {}
        logger.debug("PreferencePageRegistry initialized")
    
    def register_page(self, page_id: str, factory: Callable, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Register a preference page factory."""
        self.page_factories[page_id] = factory
        self.page_metadata[page_id] = metadata or {}
        logger.debug(f"Registered preference page: {page_id}")
    
    def create_page(self, page_id: str, **kwargs) -> Optional[PreferencePage]:
        """Create a preference page instance."""
        factory = self.page_factories.get(page_id)
        if not factory:
            logger.error(f"No factory registered for page: {page_id}")
            return None
        
        try:
            page = factory(**kwargs)
            logger.debug(f"Created preference page: {page_id}")
            return page
        except Exception as e:
            logger.error(f"Failed to create preference page {page_id}: {e}")
            return None
    
    def get_available_pages(self) -> List[str]:
        """Get list of available page IDs."""
        return list(self.page_factories.keys())
    
    def get_page_metadata(self, page_id: str) -> Dict[str, Any]:
        """Get metadata for a page."""
        return self.page_metadata.get(page_id, {})


# Global registry instance
preference_page_registry = PreferencePageRegistry()


def create_preferences_dialog(parent: Optional[QWidget] = None) -> PreferencesDialog:
    """Create and setup a preferences dialog with default pages."""
    dialog = PreferencesDialog(parent)
    
    # Future: Add default preference pages here
    # from .text_replacements import TextReplacementsPage
    # from .translation_history import TranslationHistoryPage
    # 
    # dialog.add_preference_page("replacements", TextReplacementsPage())
    # dialog.add_preference_page("history", TranslationHistoryPage())
    
    return dialog
