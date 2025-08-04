CSS Centralization System
=========================

The CSS Centralization System provides a unified, high-performance theming infrastructure for the POEditor Plugin application.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The CSS system implements a centralized approach to styling that eliminates redundancy, improves maintainability, and provides optimal performance for theme switching operations.

**Key Benefits:**

* **Consistency**: All components use the same variable system
* **Performance**: Theme switching under 100ms with advanced caching
* **Maintainability**: New components styled without modifying theme files
* **Extensibility**: New themes added without touching component files

Architecture Components
-----------------------

CSS File-Based Theme Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core component responsible for theme management and CSS processing.

.. py:class:: CSSFileBasedThemeManager

   Main theme management interface providing:
   
   * Theme loading and switching
   * CSS variable processing
   * Icon integration
   * Cache management
   * Performance optimization

   **Key Methods:**
   
   .. py:method:: set_theme(theme_name: str) -> None
   
      Switch to the specified theme with optimized processing.
      
   .. py:method:: get_available_themes() -> List[str]
   
      Get list of all available theme names.
      
   .. py:method:: get_current_theme() -> Optional[CSSTheme]
   
      Get the currently active theme object.

CSS Preprocessor
~~~~~~~~~~~~~~~~

Handles CSS variable resolution and file combination.

.. py:class:: CSSPreprocessor

   CSS processing engine providing:
   
   * Variable substitution
   * File combination
   * Cache optimization
   * Error handling
   
   **Key Methods:**
   
   .. py:method:: process_css(css_content: str, variables: Dict[str, str]) -> str
   
      Process CSS content with variable substitution.
      
   .. py:method:: combine_css_files(file_paths: List[str], variables: Dict[str, str]) -> str
   
      Combine multiple CSS files with variable processing.

Icon Preprocessor
~~~~~~~~~~~~~~~~~

Manages SVG icon processing and integration with themes.

.. py:class:: IconPreprocessor

   Icon processing system providing:
   
   * SVG optimization
   * Base64 encoding
   * Theme-aware coloring
   * CSS generation

Advanced CSS Cache
~~~~~~~~~~~~~~~~~~

Memory-efficient caching system with intelligent eviction.

.. py:class:: AdvancedCSSCache

   High-performance caching providing:
   
   * LRU eviction policy
   * Memory usage limits
   * Disk persistence
   * Performance analytics

Theme Structure
---------------

File Organization
~~~~~~~~~~~~~~~~~

The CSS system uses a structured approach to theme files:

.. code-block:: text

   themes/css/
   ├── variables.css          # Global CSS variables
   ├── light_theme.css        # Light theme styles
   ├── dark_theme.css         # Dark theme styles
   ├── colorful_theme.css     # Colorful theme styles
   └── components/
       ├── activity_bar.css   # ActivityBar specific styles
       ├── explorer.css       # Explorer panel styles
       └── sidebar.css        # Sidebar styles

Variable System
~~~~~~~~~~~~~~~

CSS variables provide the foundation for theme consistency:

.. code-block:: css

   /* Core color variables */
   :root {
       --color-primary: #007ACC;
       --color-secondary: #1E1E1E;
       --color-background: #252526;
       --color-text: #CCCCCC;
       
       /* Spacing variables */
       --spacing-xs: 4px;
       --spacing-sm: 8px;
       --spacing-md: 16px;
       --spacing-lg: 24px;
       
       /* Component variables */
       --sidebar-width: 240px;
       --activity-bar-width: 48px;
   }

Performance Characteristics
---------------------------

Benchmark Results
~~~~~~~~~~~~~~~~~

The CSS system achieves the following performance targets:

.. list-table:: Performance Metrics
   :header-rows: 1
   :widths: 30 20 20 30

   * - Operation
     - Target
     - Actual
     - Status
   * - Theme Switching
     - < 100ms
     - ~15ms
     - ✅ PASS
   * - CSS Processing
     - < 50ms
     - ~11ms
     - ✅ PASS
   * - Icon Processing
     - < 30ms
     - ~7ms
     - ✅ PASS
   * - Cache Speedup
     - > 2x
     - ~8x
     - ✅ PASS

Memory Usage
~~~~~~~~~~~~

The system maintains optimal memory usage through:

* **Cache Size Limits**: Maximum 25MB memory usage
* **LRU Eviction**: Intelligent cache cleanup
* **Disk Persistence**: Reduced memory pressure
* **Lazy Loading**: On-demand resource loading

Usage Guide
-----------

Basic Theme Switching
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   # Initialize theme manager
   theme_manager = CSSFileBasedThemeManager()
   
   # Switch to dark theme
   theme_manager.set_theme('dark')
   
   # Get current theme
   current = theme_manager.get_current_theme()
   print(f"Current theme: {current.name}")

Creating Custom Themes
~~~~~~~~~~~~~~~~~~~~~~~

1. **Create theme CSS file**:

   .. code-block:: css
   
      /* themes/css/my_theme.css */
      :root {
          --color-primary: #FF6B6B;
          --color-background: #2C3E50;
          --color-text: #ECF0F1;
      }

2. **Register theme** (automatic discovery):

   The theme manager automatically discovers CSS files in the themes directory.

Component Integration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Apply theme to widget
   widget.setStyleSheet(theme_manager.get_processed_css())
   
   # Use CSS variables in component styles
   component_css = """
   QWidget {
       background-color: var(--color-background);
       color: var(--color-text);
       padding: var(--spacing-md);
   }
   """

Testing and Validation
-----------------------

Performance Testing
~~~~~~~~~~~~~~~~~~~

The system includes comprehensive performance testing:

.. code-block:: python

   from tests.performance.css_performance_benchmark import CSSPerformanceBenchmark
   
   benchmark = CSSPerformanceBenchmark()
   results = benchmark.run_all_benchmarks()

Cross-Platform Testing
~~~~~~~~~~~~~~~~~~~~~~

Compatibility validation across platforms:

.. code-block:: python

   from tests.compatibility.cross_platform_css_validator import CrossPlatformCSSValidator
   
   validator = CrossPlatformCSSValidator()
   results = validator.run_all_tests()

Memory Profiling
~~~~~~~~~~~~~~~~

Memory usage analysis and leak detection:

.. code-block:: python

   from tests.performance.css_memory_profiler import CSSMemoryProfiler
   
   profiler = CSSMemoryProfiler()
   profiles = profiler.run_memory_profiling()

Best Practices
--------------

Theme Development
~~~~~~~~~~~~~~~~~

1. **Use CSS Variables**: Always use variables for colors, spacing, and dimensions
2. **Follow Naming Convention**: Use semantic names (``--color-primary`` not ``--blue``)
3. **Test Cross-Platform**: Validate themes on different operating systems
4. **Optimize Performance**: Keep CSS files modular and focused

Component Styling
~~~~~~~~~~~~~~~~~~

1. **Leverage Variables**: Use existing variables before creating new ones
2. **Avoid Hardcoded Values**: Use variables for all styling properties
3. **Test Theme Switching**: Ensure components work with all themes
4. **Document Dependencies**: Note which variables your component uses

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Enable Caching**: Use the advanced caching system for optimal performance
2. **Monitor Memory**: Regular memory profiling to detect leaks
3. **Minimize CSS**: Keep CSS files concise and focused
4. **Lazy Loading**: Load resources only when needed

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Theme Not Switching**
  * Check theme file exists in ``themes/css/`` directory
  * Verify CSS syntax is valid
  * Check application logs for error messages

**Performance Issues**
  * Enable CSS caching
  * Reduce CSS file size
  * Check for memory leaks with profiler

**Variable Resolution Problems**
  * Ensure variables are defined in ``variables.css``
  * Check variable naming (use ``--`` prefix)
  * Verify import order in CSS files

**Cross-Platform Rendering**
  * Test font availability
  * Validate color consistency
  * Check layout behavior

Debugging Tools
~~~~~~~~~~~~~~~

The system provides several debugging utilities:

.. code-block:: python

   # Enable debug logging
   theme_manager.enable_debug_logging()
   
   # Print cache statistics
   theme_manager.print_cache_statistics()
   
   # Generate performance report
   benchmark.generate_performance_report()

API Reference
-------------

For complete API documentation, see:

* :doc:`../services/css_file_based_theme_manager`
* :doc:`../services/css_preprocessor`
* :doc:`../services/icon_preprocessor`
* :doc:`../services/css_cache_optimizer`

Migration Guide
---------------

Migrating from Legacy System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Identify Hardcoded Styles**: Find CSS with hardcoded colors/values
2. **Extract Variables**: Convert values to CSS variables
3. **Update Component CSS**: Use variable references
4. **Test All Themes**: Validate appearance with each theme
5. **Performance Testing**: Benchmark theme switching speed

Example migration:

.. code-block:: css

   /* Before: Hardcoded values */
   QWidget {
       background-color: #252526;
       color: #CCCCCC;
       padding: 16px;
   }
   
   /* After: Using variables */
   QWidget {
       background-color: var(--color-background);
       color: var(--color-text);
       padding: var(--spacing-md);
   }

Conclusion
----------

The CSS Centralization System provides a robust, high-performance foundation for theming the POEditor Plugin application. With comprehensive testing, advanced caching, and thorough documentation, it ensures consistent user experience while maintaining developer productivity.

For additional support and advanced usage patterns, refer to the complete API documentation and developer guides in the CSS API reference section.
