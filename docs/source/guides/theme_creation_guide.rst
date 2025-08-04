================================
Theme Creation Guide
================================

.. py:module:: guides.theme_creation

Complete guide for creating custom themes for the PySide POEditor Plugin.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

The PySide POEditor Plugin supports custom themes through a CSS-based theming system. This guide covers:

* **Theme Structure**: Understanding how themes are organized
* **CSS Variables**: Using the centralized variable system
* **Component Styling**: Styling individual UI components
* **Testing**: Ensuring your theme works across all components
* **Distribution**: Packaging and sharing custom themes

Theme System Architecture
========================

How Themes Work
---------------

Themes in the PySide POEditor Plugin are built on CSS files with a variable-based system:

.. code-block:: text

   Theme System:
   ├── assets/styles/           # Theme CSS files location
   │   ├── light_theme.css     # Built-in light theme
   │   ├── dark_theme.css      # Built-in dark theme
   │   ├── colorful_theme.css  # Built-in colorful theme
   │   └── my_custom_theme.css # Your custom theme
   ├── CSSFileBasedThemeManager # Theme loading and switching
   ├── CSSPreprocessor         # Variable resolution
   └── IconPreprocessor        # Icon color adaptation

Theme File Structure
-------------------

Each theme is a single CSS file containing:

1. **CSS Variables** - Color, spacing, and size definitions
2. **Component Styles** - Styling for UI components
3. **Icon Styles** - Icon color and state definitions

.. code-block:: css

   /* Example theme structure */
   
   /* ===== CSS VARIABLES ===== */
   :root {
       /* Color definitions */
       --color-primary: #007ACC;
       --color-text: #000000;
       /* ... more variables ... */
   }
   
   /* ===== COMPONENT STYLES ===== */
   /* Activity Bar */
   #activity-bar {
       background-color: var(--color-bg-secondary);
   }
   
   /* Explorer Panel */
   #explorer-panel {
       background-color: var(--color-bg-primary);
   }
   
   /* ===== ICON STYLES ===== */
   .icon-explorer-active {
       color: var(--color-primary);
   }

Creating a Custom Theme
======================

Step 1: Create Theme File
-------------------------

Create a new CSS file in the ``assets/styles/`` directory:

.. code-block:: bash

   # Navigate to project root
   cd /path/to/pyside_poeditor_plugin
   
   # Create your theme file
   touch assets/styles/my_theme.css

**Theme Naming Convention:**

* Use lowercase with underscores: ``my_awesome_theme.css``
* Be descriptive: ``ocean_blue_theme.css`` not ``theme1.css``
* Avoid spaces and special characters

Step 2: Define CSS Variables
----------------------------

Start by defining the core CSS variables for your theme:

.. code-block:: css

   /* my_theme.css */
   :root {
       /* === PRIMARY COLORS === */
       --color-primary: #FF6B35;        /* Main brand color */
       --color-secondary: #004E89;      /* Secondary brand color */
       --color-accent: #F18F01;         /* Accent color */
       
       /* === STATUS COLORS === */
       --color-success: #2ECC71;        /* Success state */
       --color-warning: #F39C12;        /* Warning state */
       --color-danger: #E74C3C;         /* Error state */
       --color-info: #3498DB;           /* Info state */
       
       /* === TEXT COLORS === */
       --color-text: #2C3E50;           /* Primary text */
       --color-text-muted: #7F8C8D;     /* Secondary text */
       --color-text-inverse: #FFFFFF;   /* Light text on dark backgrounds */
       --color-text-disabled: #BDC3C7;  /* Disabled text */
       
       /* === BACKGROUND COLORS === */
       --color-bg-primary: #FFFFFF;     /* Main background */
       --color-bg-secondary: #FAFBFC;   /* Secondary background */
       --color-bg-tertiary: #F5F6F7;    /* Tertiary background */
       --color-bg-overlay: rgba(0, 0, 0, 0.5); /* Modal overlays */
       
       /* === BORDER COLORS === */
       --color-border: #E1E8ED;         /* Default borders */
       --color-border-light: #F0F3F6;   /* Light borders */
       --color-border-dark: #D0D7DE;    /* Dark borders */
       
       /* === SPACING === */
       --spacing-xs: 4px;
       --spacing-sm: 8px;
       --spacing-md: 16px;
       --spacing-lg: 24px;
       --spacing-xl: 32px;
       --spacing-xxl: 48px;
       
       /* === TYPOGRAPHY === */
       --font-size-xs: 11px;
       --font-size-sm: 12px;
       --font-size-md: 14px;
       --font-size-lg: 16px;
       --font-size-xl: 18px;
       --font-size-xxl: 20px;
       
       --font-weight-normal: 400;
       --font-weight-medium: 500;
       --font-weight-bold: 600;
       
       /* === LAYOUT === */
       --border-radius-sm: 3px;
       --border-radius-md: 6px;
       --border-radius-lg: 8px;
       
       --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
       --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
       --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
       
       /* === ACTIVITY BAR === */
       --activity-bar-bg: var(--color-bg-secondary);
       --activity-bar-width: 60px;
       --activity-bar-item-size: 40px;
       --activity-bar-icon-size: 24px;
       
       /* === SIDEBAR === */
       --sidebar-width: 300px;
       --sidebar-bg: var(--color-bg-primary);
       --sidebar-border: var(--color-border);
       
       /* === PANELS === */
       --panel-header-bg: var(--color-bg-secondary);
       --panel-header-height: 32px;
       --panel-content-bg: var(--color-bg-primary);
   }

Step 3: Style Core Components
-----------------------------

Add styling for the main UI components:

**Activity Bar:**

.. code-block:: css

   /* === ACTIVITY BAR === */
   #activity-bar {
       background-color: var(--activity-bar-bg);
       border-right: 1px solid var(--color-border);
       min-width: var(--activity-bar-width);
       max-width: var(--activity-bar-width);
   }
   
   #activity-bar QPushButton {
       width: var(--activity-bar-item-size);
       height: var(--activity-bar-item-size);
       border: none;
       background-color: transparent;
       border-radius: var(--border-radius-sm);
       margin: var(--spacing-xs);
   }
   
   #activity-bar QPushButton:hover {
       background-color: var(--color-bg-tertiary);
   }
   
   #activity-bar QPushButton:checked {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
   }

**Sidebar and Panels:**

.. code-block:: css

   /* === SIDEBAR === */
   #sidebar {
       background-color: var(--sidebar-bg);
       border-right: 1px solid var(--sidebar-border);
       min-width: var(--sidebar-width);
   }
   
   /* === EXPLORER PANEL === */
   #explorer-panel {
       background-color: var(--panel-content-bg);
   }
   
   #explorer-panel QTreeView {
       background-color: var(--panel-content-bg);
       color: var(--color-text);
       border: none;
       outline: none;
   }
   
   #explorer-panel QTreeView::item {
       height: 24px;
       padding: var(--spacing-xs);
       border: none;
   }
   
   #explorer-panel QTreeView::item:hover {
       background-color: var(--color-bg-tertiary);
   }
   
   #explorer-panel QTreeView::item:selected {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
   }

**Search Panel:**

.. code-block:: css

   /* === SEARCH PANEL === */
   #search-panel {
       background-color: var(--panel-content-bg);
   }
   
   #search-panel QLineEdit {
       background-color: var(--color-bg-secondary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-md);
       padding: var(--spacing-sm);
       color: var(--color-text);
       font-size: var(--font-size-md);
   }
   
   #search-panel QLineEdit:focus {
       border-color: var(--color-primary);
       background-color: var(--color-bg-primary);
   }

Step 4: Configure Icon Colors
-----------------------------

Define colors for icon states:

.. code-block:: css

   /* === ICON STYLES === */
   
   /* Activity Bar Icons */
   .icon-explorer-active,
   .icon-search-active,
   .icon-account-active,
   .icon-extensions-active,
   .icon-preferences-active {
       color: var(--color-text-inverse);
   }
   
   .icon-explorer-inactive,
   .icon-search-inactive,
   .icon-account-inactive,
   .icon-extensions-inactive,
   .icon-preferences-inactive {
       color: var(--color-text-muted);
   }
   
   /* Panel Icons */
   .icon-file,
   .icon-folder {
       color: var(--color-text);
   }
   
   .icon-folder-open {
       color: var(--color-primary);
   }

Step 5: Add Custom Styling
--------------------------

Add any custom styling specific to your theme:

.. code-block:: css

   /* === CUSTOM THEME FEATURES === */
   
   /* Custom scrollbars */
   QScrollBar:vertical {
       background-color: var(--color-bg-secondary);
       width: 12px;
       border-radius: var(--border-radius-sm);
   }
   
   QScrollBar::handle:vertical {
       background-color: var(--color-border-dark);
       border-radius: var(--border-radius-sm);
       min-height: 20px;
   }
   
   QScrollBar::handle:vertical:hover {
       background-color: var(--color-primary);
   }
   
   /* Custom tooltips */
   QToolTip {
       background-color: var(--color-bg-overlay);
       color: var(--color-text-inverse);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-md);
       padding: var(--spacing-sm);
       font-size: var(--font-size-sm);
   }
   
   /* Focus indicators */
   QWidget:focus {
       outline: 2px solid var(--color-primary);
       outline-offset: 1px;
   }

Testing Your Theme
==================

Automatic Testing
-----------------

The theme system will automatically detect and load your theme:

.. code-block:: python

   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   # Initialize theme manager
   theme_manager = CSSFileBasedThemeManager()
   
   # Check if your theme is available
   available_themes = theme_manager.get_available_themes()
   print(f"Available themes: {available_themes}")
   
   # Should include 'my_theme' (from my_theme.css)
   if 'my_theme' in available_themes:
       print("✓ Theme detected successfully!")
       
       # Switch to your theme
       theme_manager.set_theme('my_theme')
       print("✓ Theme applied successfully!")
   else:
       print("✗ Theme not found")

Manual Testing Checklist
------------------------

Test your theme with all components:

1. **Activity Bar**
   - [ ] Icons display correctly
   - [ ] Active/inactive states work
   - [ ] Hover effects work
   - [ ] Background color is correct

2. **Explorer Panel**
   - [ ] File tree displays correctly
   - [ ] Selection highlighting works
   - [ ] Hover effects work
   - [ ] Scrollbars are styled

3. **Search Panel**
   - [ ] Input fields are styled
   - [ ] Search results display correctly
   - [ ] Focus states work

4. **General UI**
   - [ ] All text is readable
   - [ ] Colors have sufficient contrast
   - [ ] Spacing looks consistent
   - [ ] No visual glitches

Performance Testing
------------------

Test theme switching performance:

.. code-block:: python

   import time
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   def test_theme_performance():
       theme_manager = CSSFileBasedThemeManager()
       
       # Test switching to your theme
       start_time = time.perf_counter()
       theme_manager.set_theme('my_theme')
       end_time = time.perf_counter()
       
       switch_time = (end_time - start_time) * 1000  # Convert to milliseconds
       print(f"Theme switch time: {switch_time:.1f}ms")
       
       # Should be under 100ms for good performance
       if switch_time < 100:
           print("✓ Performance is good!")
       else:
           print("⚠ Performance may need optimization")

Advanced Theme Features
======================

Variable Inheritance
-------------------

Use CSS variables to create consistent color relationships:

.. code-block:: css

   :root {
       /* Base colors */
       --base-primary: #FF6B35;
       --base-neutral: #7F8C8D;
       
       /* Derived colors using base colors */
       --color-primary: var(--base-primary);
       --color-primary-light: color-mix(in srgb, var(--base-primary) 80%, white);
       --color-primary-dark: color-mix(in srgb, var(--base-primary) 80%, black);
       
       /* Text colors derived from backgrounds */
       --color-text-on-primary: white;
       --color-text-on-light: var(--base-neutral);
   }

Responsive Design
----------------

Create themes that adapt to different screen sizes:

.. code-block:: css

   /* Default (desktop) sizing */
   :root {
       --activity-bar-width: 60px;
       --sidebar-width: 300px;
       --font-size-base: 14px;
   }
   
   /* Smaller screens (if needed in future) */
   @media (max-width: 768px) {
       :root {
           --activity-bar-width: 50px;
           --sidebar-width: 250px;
           --font-size-base: 12px;
       }
   }

Dark Theme Variant
------------------

Create a dark variant of your theme:

.. code-block:: css

   /* my_theme_dark.css */
   :root {
       /* Inverted background colors */
       --color-bg-primary: #1E1E1E;
       --color-bg-secondary: #252525;
       --color-bg-tertiary: #2D2D2D;
       
       /* Inverted text colors */
       --color-text: #FFFFFF;
       --color-text-muted: #B0B0B0;
       --color-text-inverse: #000000;
       
       /* Keep brand colors consistent */
       --color-primary: #FF6B35;
       --color-secondary: #004E89;
       
       /* Adjust borders for dark theme */
       --color-border: #404040;
       --color-border-light: #353535;
       --color-border-dark: #505050;
   }

Best Practices
=============

Color Guidelines
---------------

1. **Accessibility**: Ensure sufficient contrast ratios
   - Normal text: 4.5:1 minimum contrast ratio
   - Large text: 3:1 minimum contrast ratio
   - Use tools like WebAIM contrast checker

2. **Consistency**: Use a limited color palette
   - Primary color for main actions
   - Secondary color for supporting elements
   - Neutral colors for text and backgrounds

3. **Semantic Colors**: Use meaningful color assignments
   - Red for errors/danger
   - Green for success
   - Yellow/orange for warnings
   - Blue for information

Variable Organization
--------------------

1. **Group Related Variables**: Keep related variables together
2. **Use Descriptive Names**: Make variable purposes clear
3. **Establish Hierarchy**: Use primary/secondary/tertiary naming
4. **Document Purpose**: Add comments explaining color choices

.. code-block:: css

   :root {
       /* === BRAND COLORS === */
       /* Primary brand color - used for main actions and highlights */
       --color-primary: #FF6B35;
       
       /* Secondary brand color - used for supporting elements */
       --color-secondary: #004E89;
       
       /* === FUNCTIONAL COLORS === */
       /* Success state - confirmations, completed actions */
       --color-success: #2ECC71;
   }

Performance Optimization
-----------------------

1. **Minimize Complexity**: Avoid overly complex selectors
2. **Use Variables**: Reduce CSS duplication with variables
3. **Efficient Selectors**: Use specific selectors for better performance

.. code-block:: css

   /* GOOD: Specific selector */
   #explorer-panel QTreeView::item {
       background-color: var(--color-bg-primary);
   }
   
   /* AVOID: Overly broad selector */
   * {
       background-color: var(--color-bg-primary);
   }

Theme Distribution
==================

Packaging Your Theme
-------------------

To share your theme with others:

1. **Include Documentation**: Create a README for your theme
2. **Provide Screenshots**: Show your theme in action
3. **Test Thoroughly**: Ensure it works in all scenarios
4. **Version Control**: Use semantic versioning

Example theme package structure:

.. code-block:: text

   my_awesome_theme/
   ├── my_awesome_theme.css      # Main theme file
   ├── README.md                 # Theme documentation
   ├── screenshots/              # Theme screenshots
   │   ├── overview.png
   │   ├── activity_bar.png
   │   └── explorer.png
   └── LICENSE                   # License file

Installation Instructions
------------------------

Provide clear installation instructions:

.. code-block:: markdown

   # My Awesome Theme Installation
   
   1. Download `my_awesome_theme.css`
   2. Copy to `assets/styles/` directory in your POEditor Plugin installation
   3. Restart the application
   4. Select "My Awesome Theme" from the theme selector

Theme Documentation Template
---------------------------

.. code-block:: markdown

   # My Awesome Theme
   
   A vibrant, modern theme for the PySide POEditor Plugin.
   
   ## Features
   - High contrast colors for better readability
   - Modern flat design
   - Optimized for long coding sessions
   
   ## Color Palette
   - Primary: #FF6B35 (Orange)
   - Secondary: #004E89 (Blue)
   - Background: #FFFFFF (White)
   - Text: #2C3E50 (Dark Gray)
   
   ## Installation
   [Installation instructions here]
   
   ## Screenshots
   [Include screenshots here]

Troubleshooting
==============

Common Issues
------------

**Theme Not Appearing**

1. Check file name follows convention (lowercase, .css extension)
2. Verify file is in correct directory (`assets/styles/`)
3. Restart application to refresh theme list

**Colors Not Working**

1. Verify CSS variable names are correct
2. Check for typos in variable references
3. Ensure all variables are defined in `:root` section

**Performance Issues**

1. Simplify complex CSS selectors
2. Remove unnecessary styles
3. Test theme switching speed

**Visual Glitches**

1. Test in all UI states (active, hover, disabled)
2. Check component styling is complete
3. Verify icon colors are defined

Debugging Tools
--------------

.. code-block:: python

   # Debug theme loading
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   theme_manager = CSSFileBasedThemeManager()
   
   # Get processed CSS to debug
   css_content = theme_manager.get_processed_css()
   print(css_content)  # View final CSS
   
   # Check variables
   variables = theme_manager.get_css_variables()
   for name, value in variables.items():
       print(f"{name}: {value}")

Summary
======

Creating custom themes for the PySide POEditor Plugin involves:

1. **Create CSS File**: Add new .css file to `assets/styles/`
2. **Define Variables**: Set up color, spacing, and typography variables
3. **Style Components**: Add styling for all UI components
4. **Test Thoroughly**: Verify theme works in all scenarios
5. **Optimize Performance**: Ensure fast theme switching
6. **Document**: Provide clear documentation for your theme

**Key Points:**

* Use CSS variables for consistency and maintainability
* Test your theme with all UI components
* Follow accessibility guidelines for colors
* Optimize for performance
* Document your theme for others

For additional information, see:

* :doc:`css_development_guide` - CSS system development
* :doc:`icon_development_guide` - Icon system integration
* :doc:`/services/css_file_based_theme_manager` - Theme manager API
* :doc:`/architecture/css_system` - CSS system architecture
