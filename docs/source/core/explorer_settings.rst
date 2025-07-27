Explorer Settings
================

.. automodule:: core.explorer_settings
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Explorer Settings module provides configuration and preferences for the file explorer component. It allows users to customize how files are displayed, sorted, and filtered in the explorer view.

Class Reference
-------------

ExplorerSettings
~~~~~~~~~~~~~~

Main class that manages explorer settings:

.. code-block:: python

    class ExplorerSettings(QObject):
        settings_changed = Signal()
        
        def __init__(self, parent=None):
            super().__init__(parent)
            
            # Default settings
            self._settings = {
                "show_hidden_files": False,
                "sort_order": "name_asc",  # name_asc, name_desc, type, modified
                "group_folders_first": True,
                "excluded_patterns": ["*.pyc", "__pycache__/*", ".git/*", "node_modules/*"],
                "file_icons": True,
                "compact_folders": False,
                "auto_reveal_in_explorer": True,
            }
            
            # Load settings from storage
            self._load_settings()
            
        def get(self, key, default=None):
            """Get a setting value."""
            return self._settings.get(key, default)
            
        def set(self, key, value):
            """Set a setting value."""
            if key in self._settings and self._settings[key] != value:
                self._settings[key] = value
                self._save_settings()
                self.settings_changed.emit()
                
        def reset_to_defaults(self):
            """Reset all settings to defaults."""
            self._settings = {
                "show_hidden_files": False,
                "sort_order": "name_asc", 
                "group_folders_first": True,
                "excluded_patterns": ["*.pyc", "__pycache__/*", ".git/*", "node_modules/*"],
                "file_icons": True,
                "compact_folders": False,
                "auto_reveal_in_explorer": True,
            }
            self._save_settings()
            self.settings_changed.emit()
            
        def _load_settings(self):
            """Load settings from storage."""
            settings = QSettings()
            settings.beginGroup("explorer")
            
            for key in self._settings.keys():
                if settings.contains(key):
                    value = settings.value(key)
                    # Convert from QVariant if needed
                    if isinstance(self._settings[key], bool):
                        value = bool(value)
                    elif isinstance(self._settings[key], list):
                        if isinstance(value, str):
                            value = value.split(",")
                    
                    self._settings[key] = value
                    
            settings.endGroup()
            
        def _save_settings(self):
            """Save settings to storage."""
            settings = QSettings()
            settings.beginGroup("explorer")
            
            for key, value in self._settings.items():
                # Convert list to string for storage
                if isinstance(value, list):
                    value = ",".join(value)
                    
                settings.setValue(key, value)
                
            settings.endGroup()

ExplorerSettingsDialog
~~~~~~~~~~~~~~~~~~~

Dialog for editing explorer settings:

.. code-block:: python

    class ExplorerSettingsDialog(QDialog):
        def __init__(self, explorer_settings, parent=None):
            super().__init__(parent)
            self.explorer_settings = explorer_settings
            
            self.setWindowTitle("Explorer Settings")
            self.setMinimumWidth(400)
            
            self.setup_ui()
            self.load_settings()
            
        def setup_ui(self):
            """Set up the dialog UI."""
            layout = QVBoxLayout(self)
            
            # Show hidden files
            self.show_hidden_cb = QCheckBox("Show hidden files")
            layout.addWidget(self.show_hidden_cb)
            
            # Group folders first
            self.group_folders_cb = QCheckBox("Group folders before files")
            layout.addWidget(self.group_folders_cb)
            
            # File icons
            self.file_icons_cb = QCheckBox("Show file type icons")
            layout.addWidget(self.file_icons_cb)
            
            # Compact folders
            self.compact_folders_cb = QCheckBox("Compact empty folders")
            layout.addWidget(self.compact_folders_cb)
            
            # Sort order
            sort_group = QGroupBox("Sort Order")
            sort_layout = QVBoxLayout(sort_group)
            
            self.sort_name_asc = QRadioButton("Name (A to Z)")
            self.sort_name_desc = QRadioButton("Name (Z to A)")
            self.sort_type = QRadioButton("File Type")
            self.sort_modified = QRadioButton("Last Modified")
            
            sort_layout.addWidget(self.sort_name_asc)
            sort_layout.addWidget(self.sort_name_desc)
            sort_layout.addWidget(self.sort_type)
            sort_layout.addWidget(self.sort_modified)
            
            layout.addWidget(sort_group)
            
            # Excluded patterns
            exclude_group = QGroupBox("Excluded Patterns")
            exclude_layout = QVBoxLayout(exclude_group)
            
            self.exclude_list = QListWidget()
            self.exclude_list.setSelectionMode(QListWidget.SingleSelection)
            
            exclude_buttons = QHBoxLayout()
            self.add_exclude_btn = QPushButton("Add")
            self.remove_exclude_btn = QPushButton("Remove")
            
            exclude_buttons.addWidget(self.add_exclude_btn)
            exclude_buttons.addWidget(self.remove_exclude_btn)
            
            exclude_layout.addWidget(self.exclude_list)
            exclude_layout.addLayout(exclude_buttons)
            
            layout.addWidget(exclude_group)
            
            # Dialog buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
            )
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
            
            layout.addWidget(buttons)
            
        def load_settings(self):
            """Load current settings into UI."""
            self.show_hidden_cb.setChecked(self.explorer_settings.get("show_hidden_files"))
            self.group_folders_cb.setChecked(self.explorer_settings.get("group_folders_first"))
            self.file_icons_cb.setChecked(self.explorer_settings.get("file_icons"))
            self.compact_folders_cb.setChecked(self.explorer_settings.get("compact_folders"))
            
            # Set sort order
            sort_order = self.explorer_settings.get("sort_order")
            if sort_order == "name_asc":
                self.sort_name_asc.setChecked(True)
            elif sort_order == "name_desc":
                self.sort_name_desc.setChecked(True)
            elif sort_order == "type":
                self.sort_type.setChecked(True)
            elif sort_order == "modified":
                self.sort_modified.setChecked(True)
                
            # Load exclude patterns
            self.exclude_list.clear()
            for pattern in self.explorer_settings.get("excluded_patterns", []):
                self.exclude_list.addItem(pattern)
                
        def accept(self):
            """Apply settings and close dialog."""
            self.explorer_settings.set("show_hidden_files", self.show_hidden_cb.isChecked())
            self.explorer_settings.set("group_folders_first", self.group_folders_cb.isChecked())
            self.explorer_settings.set("file_icons", self.file_icons_cb.isChecked())
            self.explorer_settings.set("compact_folders", self.compact_folders_cb.isChecked())
            
            # Get sort order
            if self.sort_name_asc.isChecked():
                sort_order = "name_asc"
            elif self.sort_name_desc.isChecked():
                sort_order = "name_desc"
            elif self.sort_type.isChecked():
                sort_order = "type"
            elif self.sort_modified.isChecked():
                sort_order = "modified"
            
            self.explorer_settings.set("sort_order", sort_order)
            
            # Get excluded patterns
            patterns = []
            for i in range(self.exclude_list.count()):
                patterns.append(self.exclude_list.item(i).text())
                
            self.explorer_settings.set("excluded_patterns", patterns)
            
            super().accept()
            
        def restore_defaults(self):
            """Restore default settings."""
            self.explorer_settings.reset_to_defaults()
            self.load_settings()

Usage Examples
------------

Using Explorer Settings
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Create explorer settings
    from core.explorer_settings import ExplorerSettings
    
    settings = ExplorerSettings()
    
    # Access settings
    show_hidden = settings.get("show_hidden_files")
    excluded_patterns = settings.get("excluded_patterns")
    
    # Update a setting
    settings.set("sort_order", "type")
    
    # Listen for settings changes
    settings.settings_changed.connect(on_settings_changed)
    
    def on_settings_changed():
        print("Explorer settings were updated")
        refresh_explorer_view()

Showing the Settings Dialog
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from core.explorer_settings import ExplorerSettingsDialog
    
    def show_explorer_settings():
        dialog = ExplorerSettingsDialog(explorer_settings)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Settings were updated and saved automatically
            refresh_explorer_view()

Integration with Explorer Panel
---------------------------

The settings are integrated with the explorer panel:

.. code-block:: python

    class ExplorerPanel(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            # Create settings
            self.settings = ExplorerSettings()
            
            # Create directory model
            self.directory_model = DirectoryModel()
            
            # Apply settings to model
            self.apply_settings_to_model()
            
            # Listen for settings changes
            self.settings.settings_changed.connect(self.apply_settings_to_model)
            
            # Add settings button
            self.settings_button = QPushButton("Settings")
            self.settings_button.clicked.connect(self.show_settings_dialog)
            
        def apply_settings_to_model(self):
            """Apply current settings to the directory model."""
            self.directory_model.set_show_hidden(self.settings.get("show_hidden_files"))
            self.directory_model.set_sort_order(self.settings.get("sort_order"))
            self.directory_model.set_group_folders_first(self.settings.get("group_folders_first"))
            self.directory_model.set_excluded_patterns(self.settings.get("excluded_patterns"))
            self.directory_model.set_compact_folders(self.settings.get("compact_folders"))
            
            # Refresh the model
            self.directory_model.refresh()
            
        def show_settings_dialog(self):
            """Show the settings dialog."""
            dialog = ExplorerSettingsDialog(self.settings, self)
            dialog.exec_()
