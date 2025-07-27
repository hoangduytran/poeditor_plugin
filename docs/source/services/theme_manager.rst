Theme Manager
============

.. automodule:: services.theme_manager
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The Theme Manager is a service that handles application themes, allowing users to customize the visual appearance of the application. It supports both light and dark themes and allows plugins to register custom themes.

Class Reference
-------------

ThemeManager
~~~~~~~~~~

Main class for managing themes:

.. code-block:: python

    class ThemeManager(QObject):
        theme_changed = Signal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_theme = "system"
            self.themes = {
                "light": {
                    "name": "Light",
                    "stylesheet": ":/themes/light.css",
                    "icons": "light"
                },
                "dark": {
                    "name": "Dark",
                    "stylesheet": ":/themes/dark.css",
                    "icons": "dark"
                }
            }
            
        def register_theme(self, theme_id, name, stylesheet, icons):
            """Register a new theme with the manager."""
            self.themes[theme_id] = {
                "name": name,
                "stylesheet": stylesheet,
                "icons": icons
            }
            
        def get_available_themes(self):
            """Get all available themes."""
            return {tid: theme["name"] for tid, theme in self.themes.items()}
            
        def get_current_theme(self):
            """Get the ID of the current theme."""
            return self.current_theme
            
        def set_theme(self, theme_id):
            """Set the application theme."""
            if theme_id not in self.themes:
                return False
                
            self.current_theme = theme_id
            self._apply_theme(theme_id)
            self.theme_changed.emit(theme_id)
            return True
            
        def _apply_theme(self, theme_id):
            """Apply the selected theme to the application."""
            theme = self.themes[theme_id]
            
            # Load and set stylesheet
            stylesheet = ""
            if theme["stylesheet"].startswith(":"):
                # Load from resources
                stylesheet = self._load_stylesheet_from_resources(theme["stylesheet"])
            else:
                # Load from file
                with open(theme["stylesheet"], "r") as f:
                    stylesheet = f.read()
                    
            QApplication.instance().setStyleSheet(stylesheet)
            
            # Update icons
            # This would typically trigger an icon manager update
            
        def _load_stylesheet_from_resources(self, path):
            """Load a stylesheet from Qt resources."""
            file = QFile(path)
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                file.close()
                return stylesheet
            return ""

Theme
~~~~~

A simple dataclass for theme information:

.. code-block:: python

    class Theme:
        def __init__(self, id, name, stylesheet, icons):
            self.id = id
            self.name = name
            self.stylesheet = stylesheet
            self.icons = icons
            
        @property
        def is_dark(self):
            """Check if this is a dark theme."""
            return "dark" in self.id.lower()
            
        def __str__(self):
            return self.name

Usage Examples
------------

Using the Theme Manager
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get the theme manager from the plugin manager
    theme_manager = plugin_manager.get_service("theme_manager")
    
    # Get available themes
    themes = theme_manager.get_available_themes()
    print(f"Available themes: {themes}")
    
    # Set a theme
    theme_manager.set_theme("dark")
    
    # Listen for theme changes
    theme_manager.theme_changed.connect(on_theme_changed)
    
    def on_theme_changed(theme_id):
        print(f"Theme changed to: {theme_id}")
        update_ui_for_theme(theme_id)

Registering a Custom Theme
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Register a custom theme
    theme_manager.register_theme(
        "my_theme",                   # Theme ID
        "My Custom Theme",            # Display name
        ":/themes/my_theme.css",      # Stylesheet resource
        "custom"                      # Icon set
    )
    
    # Set the custom theme
    theme_manager.set_theme("my_theme")

Creating a Theme Selection UI
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class ThemeSelectionWidget(QWidget):
        def __init__(self, theme_manager, parent=None):
            super().__init__(parent)
            self.theme_manager = theme_manager
            
            layout = QVBoxLayout(self)
            
            # Theme selector
            self.theme_combo = QComboBox()
            
            # Populate with available themes
            themes = theme_manager.get_available_themes()
            for theme_id, theme_name in themes.items():
                self.theme_combo.addItem(theme_name, theme_id)
                
            # Set current selection
            current_theme = theme_manager.get_current_theme()
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
                
            # Connect to theme change
            self.theme_combo.currentIndexChanged.connect(self.on_theme_selected)
            
            layout.addWidget(QLabel("Select Theme:"))
            layout.addWidget(self.theme_combo)
            
        def on_theme_selected(self, index):
            # Get selected theme ID
            theme_id = self.theme_combo.itemData(index)
            
            # Apply the theme
            self.theme_manager.set_theme(theme_id)

Theme File Format
--------------

Themes are defined using CSS stylesheets. Here's a sample theme:

.. code-block:: css

    /* Light Theme Example */
    
    /* Main window */
    QMainWindow {
        background-color: #f5f5f5;
        color: #333333;
    }
    
    /* Activity bar */
    #activityBar {
        background-color: #e1e1e1;
        border-right: 1px solid #cccccc;
    }
    
    #activityBar QPushButton {
        border: none;
        padding: 10px;
    }
    
    #activityBar QPushButton:checked {
        background-color: #d0d0d0;
        border-left: 2px solid #007acc;
    }
    
    /* Side panel */
    #sidePanel {
        background-color: #f0f0f0;
        border-right: 1px solid #cccccc;
    }
    
    /* Editor tabs */
    QTabBar::tab {
        background-color: #e8e8e8;
        padding: 6px 10px;
        border: 1px solid #cccccc;
        border-bottom: none;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
    }
    
    /* Status bar */
    QStatusBar {
        background-color: #e1e1e1;
        color: #333333;
        border-top: 1px solid #cccccc;
    }
