==============================
CSS Development Guide
==============================

.. py:module:: guides.css_development

Complete guide for developers working with CSS variables, components, and the theming system.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

The PySide POEditor Plugin uses a sophisticated CSS centralization system that enables:

* **CSS Variables**: Centralized color and sizing definitions
* **Component Styling**: Modular CSS for individual UI components  
* **Theme Support**: Easy switching between light, dark, and custom themes
* **Performance Optimization**: Caching and preprocessing for fast theme changes

Architecture
============

CSS System Components
---------------------

The CSS system consists of several key components:

.. code-block:: text

   CSS System Architecture:
   ├── CSSFileBasedThemeManager    # Main theme management
   ├── CSSPreprocessor            # Variable resolution & processing
   ├── IconPreprocessor           # SVG icon processing
   └── AdvancedCSSCache          # Performance optimization

**Key Files:**

* ``assets/styles/`` - Theme CSS files (light_theme.css, dark_theme.css, etc.)
* ``services/css_file_based_theme_manager.py`` - Main theme manager
* ``services/css_preprocessor.py`` - CSS variable processing
* ``services/icon_preprocessor.py`` - Icon CSS generation

CSS Variable System
-------------------

The system uses CSS custom properties (variables) for consistent theming:

.. code-block:: css

   /* Theme variables defined in theme files */
   :root {
       /* Color System */
       --color-primary: #007ACC;
       --color-secondary: #6C757D;
       --color-success: #28A745;
       --color-warning: #FFC107;
       --color-danger: #DC3545;
       
       /* Text Colors */
       --color-text: #212529;
       --color-text-muted: #6C757D;
       --color-text-inverse: #FFFFFF;
       
       /* Background Colors */
       --color-bg-primary: #FFFFFF;
       --color-bg-secondary: #F8F9FA;
       --color-bg-tertiary: #E9ECEF;
       
       /* Spacing */
       --spacing-xs: 4px;
       --spacing-sm: 8px;
       --spacing-md: 16px;
       --spacing-lg: 24px;
       --spacing-xl: 32px;
       
       /* Typography */
       --font-size-xs: 11px;
       --font-size-sm: 12px;
       --font-size-md: 14px;
       --font-size-lg: 16px;
       --font-size-xl: 18px;
   }

Adding New CSS Elements
=======================

Step 1: Define CSS Variables
-----------------------------

When adding new UI components, first define any new variables needed:

.. code-block:: css

   /* Add to theme files (light_theme.css, dark_theme.css, etc.) */
   :root {
       /* New component variables */
       --my-component-bg: #F0F0F0;
       --my-component-border: #CCCCCC;
       --my-component-hover: #E0E0E0;
       --my-component-padding: var(--spacing-md);
   }

**Variable Naming Convention:**

* Use kebab-case: ``--color-primary`` not ``--colorPrimary``
* Be descriptive: ``--sidebar-width`` not ``--sw``
* Use semantic names: ``--color-success`` not ``--color-green``
* Group related variables: ``--button-bg``, ``--button-text``, ``--button-border``

Step 2: Create Component CSS
----------------------------

Create CSS rules for your component using the defined variables:

.. code-block:: css

   /* Component CSS using variables */
   .my-component {
       background-color: var(--my-component-bg);
       border: 1px solid var(--my-component-border);
       padding: var(--my-component-padding);
       color: var(--color-text);
       font-size: var(--font-size-md);
   }
   
   .my-component:hover {
       background-color: var(--my-component-hover);
   }
   
   .my-component .title {
       color: var(--color-primary);
       font-size: var(--font-size-lg);
       margin-bottom: var(--spacing-sm);
   }

Step 3: Add to Theme Files
--------------------------

Add your component CSS to all theme files to ensure consistency:

**File Locations:**
* ``assets/styles/light_theme.css``
* ``assets/styles/dark_theme.css`` 
* ``assets/styles/colorful_theme.css``

.. code-block:: css

   /* In each theme file, add both variables and component CSS */
   
   /* === VARIABLES === */
   :root {
       /* Existing variables... */
       
       /* My Component Variables */
       --my-component-bg: #F0F0F0;        /* Light theme value */
       --my-component-border: #CCCCCC;
       --my-component-hover: #E0E0E0;
   }
   
   /* === COMPONENT STYLES === */
   /* My Component Styles */
   .my-component {
       background-color: var(--my-component-bg);
       border: 1px solid var(--my-component-border);
       /* ... rest of component CSS ... */
   }

**Theme-Specific Values:**

.. code-block:: css

   /* light_theme.css */
   :root {
       --my-component-bg: #FFFFFF;
       --my-component-border: #E0E0E0;
   }
   
   /* dark_theme.css */
   :root {
       --my-component-bg: #2D2D2D;
       --my-component-border: #404040;
   }
   
   /* colorful_theme.css */
   :root {
       --my-component-bg: #F0F8FF;
       --my-component-border: #4A90E2;
   }

Step 4: Apply CSS to Qt Widgets
-------------------------------

Use the theme manager to apply CSS to your Qt widgets:

.. code-block:: python

   from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   class MyComponent(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.theme_manager = CSSFileBasedThemeManager()
           self.setup_ui()
           self.apply_theme()
       
       def setup_ui(self):
           """Set up the UI components"""
           self.setObjectName("my-component")  # CSS class selector
           
           layout = QVBoxLayout(self)
           
           title = QLabel("My Component Title")
           title.setObjectName("title")  # CSS class selector
           
           layout.addWidget(title)
       
       def apply_theme(self):
           """Apply current theme CSS to this component"""
           css = self.theme_manager.get_processed_css()
           self.setStyleSheet(css)

**CSS Selectors for Qt:**

.. code-block:: css

   /* Object name selector */
   #my-component {
       background-color: var(--my-component-bg);
   }
   
   /* Child selector */
   #my-component #title {
       color: var(--color-primary);
   }
   
   /* Class-based selector */
   QWidget[objectName="my-component"] {
       background-color: var(--my-component-bg);
   }

Working with Existing Variables
===============================

Using Standard Variables
------------------------

Always use existing variables when possible to maintain consistency:

.. code-block:: css

   /* GOOD: Using existing variables */
   .my-button {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
       padding: var(--spacing-md);
       font-size: var(--font-size-md);
   }
   
   /* AVOID: Hard-coded values */
   .my-button {
       background-color: #007ACC;
       color: white;
       padding: 16px;
       font-size: 14px;
   }

Variable Categories
------------------

**Colors:**
* ``--color-primary``, ``--color-secondary`` - Brand colors
* ``--color-success``, ``--color-warning``, ``--color-danger`` - Status colors
* ``--color-text``, ``--color-text-muted`` - Text colors
* ``--color-bg-primary``, ``--color-bg-secondary`` - Background colors

**Spacing:**
* ``--spacing-xs`` (4px) through ``--spacing-xl`` (32px)
* Use for padding, margin, gaps

**Typography:**
* ``--font-size-xs`` (11px) through ``--font-size-xl`` (18px)
* ``--font-weight-normal``, ``--font-weight-bold``

**Layout:**
* ``--border-radius-sm``, ``--border-radius-md`` - Border radius values
* ``--shadow-sm``, ``--shadow-md`` - Box shadow definitions

Dynamic CSS Variables
====================

Accessing Variables in Python
-----------------------------

You can access CSS variables programmatically:

.. code-block:: python

   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   theme_manager = CSSFileBasedThemeManager()
   
   # Get all variables for current theme
   variables = theme_manager.get_css_variables()
   
   # Access specific variables
   primary_color = variables.get('--color-primary', '#007ACC')
   text_color = variables.get('--color-text', '#000000')
   
   # Use in custom styling
   custom_css = f"""
   QCustomWidget {{
       background-color: {primary_color};
       color: {text_color};
   }}
   """

Creating Dynamic Styles
-----------------------

.. code-block:: python

   def create_dynamic_button_style(theme_manager, button_type='primary'):
       """Create button CSS based on current theme and button type"""
       variables = theme_manager.get_css_variables()
       
       if button_type == 'primary':
           bg_color = variables.get('--color-primary')
           text_color = variables.get('--color-text-inverse')
       elif button_type == 'secondary':
           bg_color = variables.get('--color-secondary')
           text_color = variables.get('--color-text')
       else:
           bg_color = variables.get('--color-bg-secondary')
           text_color = variables.get('--color-text')
       
       return f"""
       QPushButton {{
           background-color: {bg_color};
           color: {text_color};
           padding: {variables.get('--spacing-md')};
           border-radius: {variables.get('--border-radius-md', '4px')};
       }}
       """

Performance Considerations
=========================

CSS Preprocessing
----------------

The system preprocesses CSS for optimal performance:

* **Variable Resolution**: CSS variables are resolved at theme switch time
* **File Combination**: Multiple CSS files are combined into single output
* **Caching**: Processed CSS is cached to avoid reprocessing
* **Minification**: Whitespace and comments are removed

Best Practices
--------------

1. **Minimize Custom CSS**: Use existing variables and components when possible
2. **Cache Aware**: Understand that CSS is cached; clear cache during development
3. **Theme Testing**: Test all themes when adding new components
4. **Performance Monitoring**: Use theme manager cache statistics

.. code-block:: python

   # Clear cache during development
   theme_manager.clear_cache()
   
   # Monitor performance
   theme_manager.print_cache_statistics()

Development Workflow
===================

Step-by-Step Process
-------------------

1. **Plan Component**: Define what variables and styles you need
2. **Add Variables**: Add CSS variables to all theme files
3. **Write Component CSS**: Create CSS using the variables
4. **Apply to Widget**: Use theme manager to apply CSS
5. **Test All Themes**: Verify appearance in light, dark, and colorful themes
6. **Test Performance**: Ensure theme switching remains fast

Development Tools
----------------

**Cache Management:**

.. code-block:: python

   # Clear cache to see changes immediately
   theme_manager.clear_cache()
   
   # Check cache performance
   theme_manager.print_cache_statistics()

**Variable Inspection:**

.. code-block:: python

   # List all variables
   variables = theme_manager.get_css_variables()
   for name, value in variables.items():
       print(f"{name}: {value}")

**CSS Debugging:**

.. code-block:: python

   # Get processed CSS for debugging
   css = theme_manager.get_processed_css()
   print(css)  # View final CSS output

Testing Your CSS
================

Manual Testing
--------------

1. **Theme Switching**: Test your component in all available themes
2. **Responsive Design**: Test with different window sizes
3. **State Changes**: Test hover, focus, and other interactive states

Automated Testing
----------------

.. code-block:: python

   def test_component_css():
       """Test that component CSS loads correctly"""
       theme_manager = CSSFileBasedThemeManager()
       
       for theme in theme_manager.get_available_themes():
           theme_manager.set_theme(theme)
           css = theme_manager.get_processed_css()
           
           # Check that your variables exist
           assert '--my-component-bg' in css
           assert '.my-component' in css

Common Issues and Solutions
==========================

Issue: CSS Changes Not Visible
------------------------------

**Solution**: Clear the CSS cache

.. code-block:: python

   theme_manager.clear_cache()
   theme_manager.set_theme(current_theme)  # Reload

Issue: Variables Not Resolving
------------------------------

**Solution**: Check variable names and ensure they're defined in all themes

.. code-block:: python

   # Debug variables
   variables = theme_manager.get_css_variables()
   if '--my-variable' not in variables:
       print("Variable not defined in current theme")

Issue: Qt Selector Not Working
------------------------------

**Solution**: Use correct Qt CSS selectors

.. code-block:: css

   /* GOOD: Object name selector */
   #my-widget { }
   
   /* GOOD: Class selector with object name */
   QWidget[objectName="my-widget"] { }
   
   /* AVOID: Standard CSS class selectors don't work in Qt */
   .my-widget { }  /* This won't work */

Best Practices Summary
=====================

CSS Development Guidelines
--------------------------

1. **Use Variables**: Always use CSS variables instead of hard-coded values
2. **Semantic Names**: Use descriptive, semantic variable names
3. **Test All Themes**: Verify your component in all available themes
4. **Performance First**: Minimize custom CSS; reuse existing styles
5. **Consistent Naming**: Follow established naming conventions
6. **Clear Cache**: Clear cache during development to see changes

Code Organization
----------------

1. **Group Variables**: Keep related variables together
2. **Component Sections**: Organize CSS by component
3. **Comment Thoroughly**: Document complex CSS rules
4. **Consistent Indentation**: Use consistent CSS formatting

For additional information, see:

* :doc:`/services/css_file_based_theme_manager` - API reference
* :doc:`/services/css_preprocessor` - CSS processing details
* :doc:`icon_development_guide` - Icon system integration
* :doc:`theme_creation_guide` - Creating custom themes
