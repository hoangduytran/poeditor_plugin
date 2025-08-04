CSS File-Based Theme Manager
============================

.. py:module:: services.css_file_based_theme_manager

The CSS File-Based Theme Manager is the core component of the CSS centralization system, providing high-performance theme management with advanced caching and optimization.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The ``CSSFileBasedThemeManager`` class serves as the main interface for theme operations in the POEditor Plugin application. It integrates CSS preprocessing, icon processing, and intelligent caching to deliver optimal performance for theme switching operations.

**Key Features:**

* **Fast Theme Switching**: Sub-100ms theme transitions
* **Advanced Caching**: Memory-efficient CSS and icon caching
* **Variable Processing**: CSS variable resolution and substitution
* **Icon Integration**: SVG icon processing with theme awareness
* **Cross-Platform**: Consistent rendering across operating systems

Class Reference
---------------

.. py:class:: CSSFileBasedThemeManager

   Main theme management class providing comprehensive theming functionality.

   **Constructor:**

   .. py:method:: __init__(themes_dir: str = 'themes/css')

      Initialize the theme manager with the specified themes directory.

      :param themes_dir: Path to directory containing theme CSS files
      :type themes_dir: str

   **Theme Management Methods:**

   .. py:method:: set_theme(theme_name: str) -> None

      Switch to the specified theme with optimized processing and caching.

      :param theme_name: Name of the theme to activate
      :type theme_name: str
      :raises FileNotFoundError: If theme file does not exist
      :raises ValueError: If theme name is invalid

      **Example:**

      .. code-block:: python

         theme_manager = CSSFileBasedThemeManager()
         theme_manager.set_theme('dark')

   .. py:method:: get_current_theme() -> Optional[CSSTheme]

      Get the currently active theme object.

      :returns: Current theme object or None if no theme is active
      :rtype: Optional[CSSTheme]

      **Example:**

      .. code-block:: python

         current = theme_manager.get_current_theme()
         if current:
             print(f"Current theme: {current.name}")

   .. py:method:: get_available_themes() -> List[str]

      Get list of all available theme names from the themes directory.

      :returns: List of theme names
      :rtype: List[str]

      **Example:**

      .. code-block:: python

         themes = theme_manager.get_available_themes()
         print(f"Available themes: {', '.join(themes)}")

   .. py:method:: reload_themes() -> None

      Reload theme list from the themes directory.

      **Example:**

      .. code-block:: python

         # After adding new theme files
         theme_manager.reload_themes()

   **CSS Processing Methods:**

   .. py:method:: get_processed_css() -> str

      Get the fully processed CSS for the current theme with variables resolved.

      :returns: Processed CSS content
      :rtype: str

      **Example:**

      .. code-block:: python

         css_content = theme_manager.get_processed_css()
         widget.setStyleSheet(css_content)

   .. py:method:: get_css_variables() -> Dict[str, str]

      Get all CSS variables defined for the current theme.

      :returns: Dictionary mapping variable names to values
      :rtype: Dict[str, str]

      **Example:**

      .. code-block:: python

         variables = theme_manager.get_css_variables()
         primary_color = variables.get('--color-primary', '#007ACC')

   **Cache Management Methods:**

   .. py:method:: clear_cache() -> None

      Clear all cached CSS and icon data.

      **Example:**

      .. code-block:: python

         # Clear cache to force reprocessing
         theme_manager.clear_cache()

   .. py:method:: print_cache_statistics() -> None

      Print detailed cache performance statistics to the logger.

      **Example:**

      .. code-block:: python

         # View cache performance
         theme_manager.print_cache_statistics()

   **Persistence Methods:**

   .. py:method:: _save_current_theme() -> None

      Save the current theme selection to persistent storage.

      .. note::
         This method is called automatically when themes are switched.

   .. py:method:: _load_saved_theme() -> Optional[str]

      Load the previously saved theme from persistent storage.

      :returns: Saved theme name or None if no theme was saved
      :rtype: Optional[str]

Properties
----------

.. py:attribute:: CSSFileBasedThemeManager.css_preprocessor

   The CSS preprocessor instance used for variable resolution and file combination.

   :type: CSSPreprocessor

.. py:attribute:: CSSFileBasedThemeManager.icon_preprocessor

   The icon preprocessor instance used for SVG processing and CSS generation.

   :type: IconPreprocessor

.. py:attribute:: CSSFileBasedThemeManager.themes_dir

   Path to the directory containing theme CSS files.

   :type: str

.. py:attribute:: CSSFileBasedThemeManager.current_theme_name

   Name of the currently active theme.

   :type: Optional[str]

Theme Object Reference
----------------------

.. py:class:: CSSTheme

   Represents a single theme with its associated CSS content and metadata.

   .. py:attribute:: name
      
      The theme name (derived from filename).
      
      :type: str

   .. py:attribute:: css_content
      
      The raw CSS content from the theme file.
      
      :type: str

   .. py:attribute:: file_path
      
      Path to the theme CSS file.
      
      :type: str

   .. py:attribute:: variables
      
      CSS variables defined in this theme.
      
      :type: Dict[str, str]

Usage Examples
--------------

Basic Theme Management
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   # Initialize theme manager
   theme_manager = CSSFileBasedThemeManager()
   
   # List available themes
   available = theme_manager.get_available_themes()
   print(f"Available themes: {available}")
   
   # Switch to dark theme
   theme_manager.set_theme('dark')
   
   # Get processed CSS
   css = theme_manager.get_processed_css()
   
   # Apply to widget
   widget.setStyleSheet(css)

Advanced Usage
~~~~~~~~~~~~~~

.. code-block:: python

   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   # Initialize with custom themes directory
   theme_manager = CSSFileBasedThemeManager('custom/themes/path')
   
   # Switch theme and check performance
   import time
   start = time.perf_counter()
   theme_manager.set_theme('colorful')
   end = time.perf_counter()
   
   print(f"Theme switch took: {(end - start) * 1000:.1f}ms")
   
   # View cache statistics
   theme_manager.print_cache_statistics()
   
   # Get theme variables for custom styling
   variables = theme_manager.get_css_variables()
   custom_css = f"""
   QCustomWidget {{
       background-color: {variables.get('--color-primary', '#007ACC')};
       color: {variables.get('--color-text', '#FFFFFF')};
   }}
   """

Integration with Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from PySide6.QtWidgets import QWidget
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   class ThemedWidget(QWidget):
       def __init__(self):
           super().__init__()
           self.theme_manager = CSSFileBasedThemeManager()
           self.apply_theme()
       
       def apply_theme(self):
           """Apply current theme to this widget"""
           css = self.theme_manager.get_processed_css()
           self.setStyleSheet(css)
       
       def switch_theme(self, theme_name: str):
           """Switch to a different theme"""
           self.theme_manager.set_theme(theme_name)
           self.apply_theme()

Performance Optimization
------------------------

Caching Strategy
~~~~~~~~~~~~~~~~

The theme manager implements a multi-level caching strategy:

1. **CSS Cache**: Processed CSS content with resolved variables
2. **Icon Cache**: Processed SVG icons with Base64 encoding
3. **Variable Cache**: Parsed CSS variables for quick access
4. **File Cache**: Raw file content to avoid disk I/O

**Memory Management:**

* Maximum cache size: 25MB
* LRU eviction policy
* Automatic cleanup of unused entries
* Disk persistence for large files

Theme Switching Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Theme switching is optimized through:

* **Preloaded Variables**: CSS variables cached on first load
* **Incremental Processing**: Only reprocess changed content
* **Background Processing**: Non-blocking theme preparation
* **Smart Invalidation**: Selective cache clearing

Best Practices
--------------

Performance Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

1. **Reuse Theme Manager**: Create one instance and reuse it
2. **Monitor Cache**: Use ``print_cache_statistics()`` to monitor performance
3. **Clear Cache Sparingly**: Only clear when necessary (file changes)
4. **Preload Themes**: Load frequently used themes during initialization

Memory Management
~~~~~~~~~~~~~~~~~

1. **Monitor Memory Usage**: Use memory profiling tools
2. **Limit Cache Size**: Configure appropriate cache limits
3. **Clean Up**: Call ``clear_cache()`` when disposing theme manager
4. **Avoid Memory Leaks**: Properly dispose of theme manager instances

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   try:
       theme_manager.set_theme('nonexistent_theme')
   except FileNotFoundError as e:
       logger.error(f"Theme file not found: {e}")
       # Fall back to default theme
       theme_manager.set_theme('light')
   except ValueError as e:
       logger.error(f"Invalid theme name: {e}")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Theme Not Switching**

* Verify theme file exists in themes directory
* Check file permissions
* Validate CSS syntax
* Review application logs

**Performance Issues**

* Check cache statistics for hit ratio
* Monitor memory usage
* Reduce CSS file complexity
* Enable debug logging

**CSS Variables Not Resolving**

* Ensure variables are defined in variables.css
* Check variable syntax (``--variable-name``)
* Verify import order in CSS files

Debugging
~~~~~~~~~

Enable detailed logging:

.. code-block:: python

   import logging
   logging.getLogger('services.css_file_based_theme_manager').setLevel(logging.DEBUG)

View internal state:

.. code-block:: python

   # Print current theme info
   current = theme_manager.get_current_theme()
   if current:
       print(f"Theme: {current.name}")
       print(f"Variables: {len(current.variables)}")
   
   # Print cache statistics
   theme_manager.print_cache_statistics()

API Changelog
-------------

**Version 4.0** (Phase 4)
  * Added advanced caching system
  * Implemented memory profiling
  * Enhanced performance optimization
  * Added cross-platform compatibility

**Version 3.0** (Phase 3)
  * Integrated icon preprocessing
  * Added SVG processing capabilities
  * Enhanced variable system

**Version 2.0** (Phase 2)
  * Implemented CSS preprocessing
  * Added variable resolution
  * Enhanced caching mechanism

**Version 1.0** (Phase 1)
  * Initial theme management implementation
  * Basic file-based theme loading
  * Simple CSS processing

See Also
--------

* :doc:`css_preprocessor` - CSS variable processing
* :doc:`icon_preprocessor` - SVG icon processing  
* :doc:`css_cache_optimizer` - Advanced caching system
* :doc:`../architecture/css_system` - CSS system architecture
