================================
Component Styling Guide
================================

.. py:module:: guides.component_styling

Best practices guide for styling new UI components in the PySide POEditor Plugin.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

This guide covers best practices for styling new UI components in the PySide POEditor Plugin. It focuses on:

* **CSS Integration**: How to integrate new components with the CSS system
* **Variable Usage**: Using existing CSS variables effectively
* **Qt Styling**: Working with Qt-specific CSS features
* **Performance**: Ensuring efficient styling
* **Maintainability**: Creating maintainable component styles

Component Styling Philosophy
===========================

Design Principles
-----------------

The PySide POEditor Plugin follows these styling principles:

1. **Consistency**: All components use the same visual language
2. **Accessibility**: Sufficient contrast and readable typography
3. **Performance**: Efficient CSS with minimal overhead
4. **Maintainability**: Easy to update and extend
5. **Theme Compatibility**: Works across all themes

CSS Architecture
---------------

Component styling follows a hierarchical approach:

.. code-block:: text

   Styling Hierarchy:
   ├── CSS Variables (Theme-level)
   │   ├── Colors (:root --color-*)
   │   ├── Spacing (:root --spacing-*)
   │   └── Typography (:root --font-*)
   ├── Component Styles (Component-level)
   │   ├── Layout and positioning
   │   ├── Colors using variables
   │   └── Typography using variables
   └── State Styles (Interaction-level)
       ├── Hover states
       ├── Active states
       └── Focus states

Styling New Components
=====================

Step 1: Analyze Component Requirements
-------------------------------------

Before writing CSS, analyze your component:

1. **Visual Hierarchy**: What elements need emphasis?
2. **Interaction States**: What states does the component have?
3. **Theme Integration**: How should it adapt to different themes?
4. **Responsive Needs**: Does it need to adapt to different sizes?

**Example Analysis for a Custom Button:**

.. code-block:: python

   # Component: CustomButton
   # Requirements:
   # - Primary and secondary variants
   # - Hover, active, disabled states  
   # - Icon support
   # - Theme color integration
   # - Consistent with existing buttons

Step 2: Set Up Component Structure
---------------------------------

Create your component with proper object names for CSS targeting:

.. code-block:: python

   from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel
   from PySide6.QtCore import Qt
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   class CustomButton(QPushButton):
       def __init__(self, text: str, variant: str = "primary", parent=None):
           super().__init__(text, parent)
           self.variant = variant
           self.theme_manager = CSSFileBasedThemeManager()
           
           # Set object name for CSS targeting
           self.setObjectName("custom-button")
           
           # Set variant as property for CSS selection
           self.setProperty("variant", variant)
           
           self.setup_ui()
           self.apply_styling()
       
       def setup_ui(self):
           """Set up the button UI"""
           # Additional UI setup if needed
           pass
       
       def apply_styling(self):
           """Apply CSS styling to the button"""
           css = self.theme_manager.get_processed_css()
           self.setStyleSheet(css)

Step 3: Define Component Variables
---------------------------------

Add component-specific variables to theme files:

.. code-block:: css

   /* In all theme files (light_theme.css, dark_theme.css, etc.) */
   :root {
       /* Custom Button Variables */
       --custom-button-padding-y: var(--spacing-sm);
       --custom-button-padding-x: var(--spacing-md);
       --custom-button-border-radius: var(--border-radius-md);
       --custom-button-font-size: var(--font-size-md);
       --custom-button-font-weight: var(--font-weight-medium);
       
       /* Primary Button Colors */
       --custom-button-primary-bg: var(--color-primary);
       --custom-button-primary-text: var(--color-text-inverse);
       --custom-button-primary-border: var(--color-primary);
       --custom-button-primary-hover-bg: color-mix(in srgb, var(--color-primary) 85%, black);
       
       /* Secondary Button Colors */
       --custom-button-secondary-bg: transparent;
       --custom-button-secondary-text: var(--color-primary);
       --custom-button-secondary-border: var(--color-primary);
       --custom-button-secondary-hover-bg: var(--color-bg-tertiary);
   }

Step 4: Write Component CSS
--------------------------

Create CSS rules for your component:

.. code-block:: css

   /* Custom Button Base Styles */
   #custom-button {
       padding: var(--custom-button-padding-y) var(--custom-button-padding-x);
       border-radius: var(--custom-button-border-radius);
       font-size: var(--custom-button-font-size);
       font-weight: var(--custom-button-font-weight);
       border: 1px solid transparent;
       cursor: pointer;
       outline: none;
       transition: all 0.2s ease;
   }
   
   /* Primary Variant */
   #custom-button[variant="primary"] {
       background-color: var(--custom-button-primary-bg);
       color: var(--custom-button-primary-text);
       border-color: var(--custom-button-primary-border);
   }
   
   #custom-button[variant="primary"]:hover {
       background-color: var(--custom-button-primary-hover-bg);
   }
   
   #custom-button[variant="primary"]:pressed {
       transform: translateY(1px);
   }
   
   /* Secondary Variant */
   #custom-button[variant="secondary"] {
       background-color: var(--custom-button-secondary-bg);
       color: var(--custom-button-secondary-text);
       border-color: var(--custom-button-secondary-border);
   }
   
   #custom-button[variant="secondary"]:hover {
       background-color: var(--custom-button-secondary-hover-bg);
   }
   
   /* Disabled State */
   #custom-button:disabled {
       opacity: 0.6;
       cursor: not-allowed;
   }
   
   /* Focus State */
   #custom-button:focus {
       box-shadow: 0 0 0 2px var(--color-primary);
   }

Working with Qt CSS Features
============================

Qt-Specific Selectors
---------------------

Qt provides powerful CSS selectors beyond standard CSS:

.. code-block:: css

   /* Object name selector */
   #my-widget { }
   
   /* Property-based selector */
   QWidget[objectName="my-widget"] { }
   QWidget[variant="primary"] { }
   QWidget[state="active"] { }
   
   /* Type-based selector */
   QPushButton { }
   QLabel { }
   QTreeView { }
   
   /* Pseudo-states */
   QPushButton:hover { }
   QPushButton:pressed { }
   QPushButton:checked { }
   QPushButton:disabled { }
   
   /* Sub-controls (for complex widgets) */
   QScrollBar::handle:vertical { }
   QTreeView::item:selected { }
   QComboBox::drop-down { }

Dynamic Properties
-----------------

Use dynamic properties for flexible styling:

.. code-block:: python

   # In Python component
   button.setProperty("variant", "primary")
   button.setProperty("size", "large")
   button.setProperty("state", "loading")
   
   # Update style after property change
   button.style().unpolish(button)
   button.style().polish(button)

.. code-block:: css

   /* In CSS */
   QPushButton[variant="primary"][size="large"] {
       padding: var(--spacing-lg) var(--spacing-xl);
       font-size: var(--font-size-lg);
   }
   
   QPushButton[state="loading"] {
       opacity: 0.7;
       cursor: wait;
   }

Complex Widget Styling
---------------------

Style complex widgets with sub-controls:

.. code-block:: css

   /* Custom TreeView */
   #my-tree-view {
       background-color: var(--color-bg-primary);
       border: 1px solid var(--color-border);
       outline: none;
   }
   
   #my-tree-view::item {
       height: 28px;
       padding: var(--spacing-xs) var(--spacing-sm);
       border: none;
   }
   
   #my-tree-view::item:hover {
       background-color: var(--color-bg-tertiary);
   }
   
   #my-tree-view::item:selected {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
   }
   
   #my-tree-view::branch {
       width: 16px;
   }
   
   #my-tree-view::branch:has-children:!has-siblings:closed,
   #my-tree-view::branch:closed:has-children:has-siblings {
       image: url(icons/branch-closed.svg);
   }
   
   #my-tree-view::branch:open:has-children:!has-siblings,
   #my-tree-view::branch:open:has-children:has-siblings {
       image: url(icons/branch-open.svg);
   }

Best Practices for Component CSS
================================

Variable Usage Guidelines
-------------------------

1. **Use Existing Variables**: Prefer existing variables over custom ones

.. code-block:: css

   /* GOOD: Using existing variables */
   .my-component {
       padding: var(--spacing-md);
       color: var(--color-text);
       background-color: var(--color-bg-primary);
   }
   
   /* AVOID: Hard-coded values */
   .my-component {
       padding: 16px;
       color: #333333;
       background-color: #FFFFFF;
   }

2. **Create Semantic Variables**: When creating new variables, use semantic names

.. code-block:: css

   /* GOOD: Semantic variable names */
   :root {
       --button-padding: var(--spacing-md);
       --button-border-radius: var(--border-radius-md);
   }
   
   /* AVOID: Generic names */
   :root {
       --button-pad: 16px;
       --button-round: 6px;
   }

3. **Group Related Variables**: Keep component variables together

.. code-block:: css

   :root {
       /* === CUSTOM BUTTON === */
       --custom-button-height: 36px;
       --custom-button-padding: var(--spacing-md);
       --custom-button-font-size: var(--font-size-md);
       
       /* === CUSTOM PANEL === */
       --custom-panel-header-height: 32px;
       --custom-panel-padding: var(--spacing-lg);
   }

Performance Optimization
------------------------

1. **Efficient Selectors**: Use specific selectors for better performance

.. code-block:: css

   /* GOOD: Specific selector */
   #my-component .header {
       font-weight: var(--font-weight-bold);
   }
   
   /* AVOID: Overly broad selector */
   * .header {
       font-weight: var(--font-weight-bold);
   }

2. **Minimize Cascade Depth**: Avoid deeply nested selectors

.. code-block:: css

   /* GOOD: Shallow nesting */
   #panel .item {
       padding: var(--spacing-sm);
   }
   
   /* AVOID: Deep nesting */
   #container #panel .content .item .text {
       padding: var(--spacing-sm);
   }

3. **Use Class-based Targeting**: Combine object names with Qt properties

.. code-block:: css

   /* GOOD: Property-based selection */
   QPushButton[variant="primary"] { }
   
   /* LESS EFFICIENT: Complex selectors */
   #container QPushButton.primary-button { }

State Management
---------------

Handle component states consistently:

.. code-block:: css

   /* Base state */
   .interactive-component {
       transition: all 0.2s ease;
       background-color: var(--color-bg-primary);
   }
   
   /* Hover state */
   .interactive-component:hover {
       background-color: var(--color-bg-secondary);
   }
   
   /* Active state */
   .interactive-component:pressed,
   .interactive-component[state="active"] {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
   }
   
   /* Disabled state */
   .interactive-component:disabled,
   .interactive-component[state="disabled"] {
       opacity: 0.6;
       cursor: not-allowed;
   }
   
   /* Focus state */
   .interactive-component:focus {
       outline: 2px solid var(--color-primary);
       outline-offset: 1px;
   }

Integration Patterns
===================

Theme Manager Integration
------------------------

Integrate your component with the theme manager:

.. code-block:: python

   from PySide6.QtWidgets import QWidget
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   class ThemedComponent(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.theme_manager = CSSFileBasedThemeManager()
           
           # Connect to theme changes
           self.theme_manager.theme_changed.connect(self.on_theme_changed)
           
           self.setup_ui()
           self.apply_theme()
       
       def setup_ui(self):
           """Set up the component UI"""
           self.setObjectName("themed-component")
           # Add UI elements...
       
       def apply_theme(self):
           """Apply current theme to this component"""
           css = self.theme_manager.get_processed_css()
           self.setStyleSheet(css)
       
       def on_theme_changed(self, theme_name: str):
           """Handle theme change events"""
           self.apply_theme()

Dynamic Styling
--------------

Create components that adapt their styling dynamically:

.. code-block:: python

   class AdaptiveComponent(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.theme_manager = CSSFileBasedThemeManager()
           self._variant = "default"
           self._size = "medium"
           self.setup_ui()
       
       @property
       def variant(self) -> str:
           return self._variant
       
       @variant.setter
       def variant(self, value: str):
           if self._variant != value:
               self._variant = value
               self.setProperty("variant", value)
               self.update_styling()
       
       @property
       def size(self) -> str:
           return self._size
       
       @size.setter
       def size(self, value: str):
           if self._size != value:
               self._size = value
               self.setProperty("size", value)
               self.update_styling()
       
       def update_styling(self):
           """Update styling after property changes"""
           # Force style recalculation
           self.style().unpolish(self)
           self.style().polish(self)

Component Testing
================

CSS Testing
----------

Test your component styling across all themes:

.. code-block:: python

   def test_component_styling():
       """Test component in all available themes"""
       from services.css_file_based_theme_manager import CSSFileBasedThemeManager
       
       theme_manager = CSSFileBasedThemeManager()
       available_themes = theme_manager.get_available_themes()
       
       for theme_name in available_themes:
           print(f"Testing theme: {theme_name}")
           
           # Switch to theme
           theme_manager.set_theme(theme_name)
           
           # Create component
           component = MyCustomComponent()
           
           # Verify styling is applied
           css = theme_manager.get_processed_css()
           assert "my-custom-component" in css
           
           print(f"✓ {theme_name} theme works correctly")

Visual Testing
-------------

Create visual tests for component states:

.. code-block:: python

   from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
   
   def create_component_showcase():
       """Create a showcase window for testing component visuals"""
       app = QApplication.instance() or QApplication([])
       
       window = QWidget()
       window.setWindowTitle("Component Showcase")
       window.resize(800, 600)
       
       layout = QVBoxLayout(window)
       
       # Test different component variants
       for variant in ["primary", "secondary", "danger"]:
           for size in ["small", "medium", "large"]:
               component = MyCustomComponent()
               component.variant = variant
               component.size = size
               layout.addWidget(component)
       
       window.show()
       return window

Common Patterns
==============

Panel Components
---------------

Standard pattern for panel-style components:

.. code-block:: css

   .custom-panel {
       background-color: var(--color-bg-primary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-md);
   }
   
   .custom-panel .header {
       background-color: var(--color-bg-secondary);
       padding: var(--spacing-sm) var(--spacing-md);
       border-bottom: 1px solid var(--color-border);
       font-weight: var(--font-weight-medium);
   }
   
   .custom-panel .content {
       padding: var(--spacing-md);
   }

Input Components
---------------

Standard pattern for input-style components:

.. code-block:: css

   .custom-input {
       background-color: var(--color-bg-primary);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius-sm);
       padding: var(--spacing-sm);
       font-size: var(--font-size-md);
       color: var(--color-text);
   }
   
   .custom-input:focus {
       border-color: var(--color-primary);
       outline: none;
       box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
   }
   
   .custom-input:disabled {
       background-color: var(--color-bg-tertiary);
       color: var(--color-text-muted);
       cursor: not-allowed;
   }

List Components
--------------

Standard pattern for list-style components:

.. code-block:: css

   .custom-list {
       background-color: var(--color-bg-primary);
       border: 1px solid var(--color-border);
   }
   
   .custom-list .item {
       padding: var(--spacing-sm) var(--spacing-md);
       border-bottom: 1px solid var(--color-border-light);
   }
   
   .custom-list .item:last-child {
       border-bottom: none;
   }
   
   .custom-list .item:hover {
       background-color: var(--color-bg-secondary);
   }
   
   .custom-list .item.selected {
       background-color: var(--color-primary);
       color: var(--color-text-inverse);
   }

Troubleshooting
==============

Common Issues
------------

**CSS Not Applied**

1. Check object name is set correctly
2. Verify CSS is included in theme files
3. Clear theme cache and reload

.. code-block:: python

   # Debug CSS application
   widget.setObjectName("my-component")  # Ensure object name is set
   theme_manager.clear_cache()           # Clear cache
   theme_manager.set_theme(current_theme) # Reload theme

**Qt Selector Not Working**

1. Use Qt-specific selectors, not standard CSS class selectors
2. Check property values match exactly
3. Test selector specificity

.. code-block:: css

   /* WORKS in Qt */
   #my-widget { }
   QWidget[objectName="my-widget"] { }
   
   /* DOESN'T WORK in Qt */
   .my-widget { }  /* Standard CSS class selector */

**Performance Issues**

1. Simplify complex selectors
2. Reduce CSS specificity conflicts
3. Minimize dynamic property changes

.. code-block:: css

   /* GOOD: Simple, specific selector */
   #fast-component {
       background-color: var(--color-bg-primary);
   }
   
   /* SLOW: Complex, nested selector */
   #container #wrapper #content #slow-component {
       background-color: var(--color-bg-primary);
   }

Summary
======

Key guidelines for styling new components:

1. **Use Object Names**: Set unique object names for CSS targeting
2. **Leverage Variables**: Use existing CSS variables for consistency
3. **Follow Patterns**: Use established patterns for similar components
4. **Test Thoroughly**: Test in all themes and component states
5. **Optimize Performance**: Use efficient selectors and minimal CSS
6. **Document Changes**: Document component styling for maintainability

**Best Practices Checklist:**

- [ ] Component has unique object name
- [ ] Uses existing CSS variables where possible
- [ ] Defines custom variables when needed
- [ ] Handles all interaction states (hover, focus, disabled)
- [ ] Works in all available themes
- [ ] Uses efficient CSS selectors
- [ ] Follows established design patterns
- [ ] Is properly documented

For additional information, see:

* :doc:`css_development_guide` - Complete CSS development guide
* :doc:`icon_development_guide` - Icon integration
* :doc:`theme_creation_guide` - Theme development
* :doc:`/services/css_file_based_theme_manager` - Theme manager API
