Theme System
===========

Overview
--------

The Theme System provides a way to customize the application's appearance through CSS-based themes. It supports both light and dark modes as well as custom theme variants.

Components
---------

The Theme System consists of several components:

1. **ThemeManager**: Service that manages theme loading and application
2. **CSS Managers**: Services that handle loading and processing CSS files
3. **Theme Editor**: UI for customizing and creating themes

Theme Manager
-----------

The ``ThemeManager`` provides central theme management:

.. code-block:: python

    class ThemeManager(QObject):
        theme_changed = Signal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_theme = "light"
            self.themes = {
                "light": {"name": "Light", "path": ":/themes/light.css"},
                "dark": {"name": "Dark", "path": ":/themes/dark.css"}
            }
            
        def set_theme(self, theme_id):
            """Set the current theme."""
            if theme_id in self.themes:
                self.current_theme = theme_id
                self._apply_theme()
                self.theme_changed.emit(theme_id)
                
        def register_theme(self, theme_id, theme_data):
            """Register a new theme."""
            self.themes[theme_id] = theme_data

CSS-Based Theming
---------------

The application uses Qt's stylesheet system with CSS variables for consistent theming:

.. code-block:: css

    /* Example theme CSS */
    :root {
        --background-color: #ffffff;
        --foreground-color: #333333;
        --accent-color: #007acc;
        --border-color: #cccccc;
    }
    
    QWidget {
        background-color: var(--background-color);
        color: var(--foreground-color);
    }
    
    QPushButton {
        background-color: var(--accent-color);
        border: 1px solid var(--border-color);
    }

Theme Configuration
-----------------

Themes can be configured through:

1. **Built-in themes**: Included in the application resources
2. **CSS files**: Loaded from the filesystem
3. **Theme Editor**: Interactive UI for customizing themes

Custom themes are stored in the application's configuration directory.

Theme Switching
-------------

Users can switch themes through:

1. **Preferences Panel**: Select from available themes
2. **Theme Editor**: Create and apply custom themes
3. **API**: Programmatically switch themes

.. code-block:: python

    # Switch to dark theme
    theme_manager = plugin_manager.get_service("theme_manager")
    theme_manager.set_theme("dark")

Creating Custom Themes
-------------------

Custom themes can be created by:

1. Creating a new CSS file with theme variables
2. Using the Theme Editor to customize colors and styles
3. Extending an existing theme with custom rules

The Theme Editor provides a visual way to:
- Adjust color variables
- Preview changes in real-time
- Save custom themes for later use
