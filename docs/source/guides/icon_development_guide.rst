==============================
Icon Development Guide
==============================

.. py:module:: guides.icon_development

Complete guide for adding, managing, and customizing icons in the PySide POEditor Plugin.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
========

The PySide POEditor Plugin uses a sophisticated icon system that provides:

* **SVG Icons**: Scalable vector graphics for crisp display at any size
* **Theme Integration**: Icons automatically adapt to current theme colors
* **CSS Generation**: Icons are converted to CSS for easy styling
* **Caching**: Optimized performance with intelligent caching
* **Activity Bar Integration**: Special support for activity bar icons

Icon System Architecture
=======================

System Components
-----------------

The icon system consists of several key components:

.. code-block:: text

   Icon System Architecture:
   ├── icons/                     # SVG icon files
   ├── IconPreprocessor          # SVG processing and CSS generation
   ├── CSSFileBasedThemeManager  # Theme integration
   └── ActivityBar               # Activity bar icon management

**Key Directories:**

* ``icons/`` - Source SVG files
* ``assets/styles/`` - Generated icon CSS (included in theme files)
* ``services/icon_preprocessor.py`` - Icon processing logic

Icon File Structure
------------------

Icons are organized by naming convention:

.. code-block:: text

   icons/
   ├── explorer_active.svg       # Active state icon
   ├── explorer_inactive.svg     # Inactive state icon
   ├── search_active.svg
   ├── search_inactive.svg
   ├── account_active.svg
   ├── account_inactive.svg
   ├── extensions_active.svg
   ├── extensions_inactive.svg
   └── preferences_active.svg

**Naming Convention:**

* ``{name}_active.svg`` - Icon for active/selected state
* ``{name}_inactive.svg`` - Icon for inactive/default state
* Use lowercase with underscores
* Be descriptive: ``file_explorer`` not ``fe``

Adding New Icons
===============

Step 1: Prepare SVG Files
-------------------------

Create your SVG icon files following these guidelines:

**SVG Requirements:**

* **Format**: SVG (Scalable Vector Graphics)
* **Size**: Design at 24x24px for optimal display
* **Colors**: Use ``currentColor`` or theme-compatible colors
* **Optimization**: Remove unnecessary metadata and comments

**Example SVG Structure:**

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <svg width="24" height="24" viewBox="0 0 24 24" 
        xmlns="http://www.w3.org/2000/svg">
       <path d="M12 2L2 7L12 12L22 7L12 2Z" 
             fill="currentColor" 
             stroke="none"/>
   </svg>

**Color Guidelines:**

.. code-block:: xml

   <!-- GOOD: Use currentColor for theme integration -->
   <path fill="currentColor" />
   
   <!-- GOOD: Use theme-aware colors -->
   <path fill="var(--color-primary)" />
   
   <!-- AVOID: Hard-coded colors -->
   <path fill="#007ACC" />

Step 2: Add Icon Files
----------------------

Place your SVG files in the ``icons/`` directory with proper naming:

.. code-block:: bash

   # Navigate to project root
   cd /path/to/pyside_poeditor_plugin
   
   # Add your icon files
   cp my_new_icon_active.svg icons/
   cp my_new_icon_inactive.svg icons/

**File Naming Examples:**

.. code-block:: text

   icons/
   ├── my_feature_active.svg     # New feature icon (active)
   ├── my_feature_inactive.svg   # New feature icon (inactive) 
   ├── settings_active.svg       # Settings icon (active)
   ├── settings_inactive.svg     # Settings icon (inactive)

Step 3: Process Icons
--------------------

The icon system automatically processes SVG files when themes are loaded. 
To manually trigger processing:

.. code-block:: python

   from services.icon_preprocessor import IconPreprocessor
   
   # Create icon processor
   processor = IconPreprocessor()
   
   # Process all icons
   processed_icons = processor.process_all_icons()
   
   # Generate CSS for icons
   icon_css = processor.generate_icon_css(generate_variables=True)
   
   print(f"Processed {len(processed_icons)} icons")

Step 4: Verify Icon Integration
------------------------------

Check that your icons are properly integrated:

.. code-block:: python

   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   # Initialize theme manager
   theme_manager = CSSFileBasedThemeManager()
   
   # Get processed CSS (includes icon CSS)
   css = theme_manager.get_processed_css()
   
   # Check if your icon CSS is included
   if 'my-feature-active' in css:
       print("Icon successfully integrated!")
   else:
       print("Icon not found in CSS")

Using Icons in Components
========================

CSS-Based Icon Usage
--------------------

Icons are automatically converted to CSS classes for easy use:

.. code-block:: css

   /* Generated CSS classes for icons */
   .icon-my-feature-active {
       background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQi...');
       background-size: contain;
       background-repeat: no-repeat;
       background-position: center;
   }
   
   .icon-my-feature-inactive {
       background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQi...');
       background-size: contain;
       background-repeat: no-repeat;
       background-position: center;
   }

**Using Icons in Qt Widgets:**

.. code-block:: python

   from PySide6.QtWidgets import QPushButton, QWidget
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   class IconButton(QPushButton):
       def __init__(self, icon_name: str, active: bool = False, parent=None):
           super().__init__(parent)
           self.icon_name = icon_name
           self.active = active
           self.theme_manager = CSSFileBasedThemeManager()
           self.setup_icon()
       
       def setup_icon(self):
           """Set up the icon for this button"""
           state = "active" if self.active else "inactive"
           css_class = f"icon-{self.icon_name}-{state}"
           
           # Apply theme CSS
           css = self.theme_manager.get_processed_css()
           
           # Add icon-specific styling
           icon_css = f"""
           QPushButton {{
               width: 24px;
               height: 24px;
               border: none;
               background: transparent;
           }}
           
           QPushButton.{css_class} {{
               /* Icon background is set by generated CSS */
           }}
           """
           
           self.setStyleSheet(css + icon_css)
           self.setProperty("class", css_class)

Activity Bar Icons
-----------------

Activity bar icons have special integration requirements:

.. code-block:: python

   from models.activity_models import ActivityItem
   
   # Create activity with icon
   activity = ActivityItem(
       id="my_feature",
       title="My Feature",
       icon_name="my_feature",  # Corresponds to my_feature_active.svg
       panel_class=MyFeaturePanel
   )

**Activity Bar Icon Requirements:**

* Must have both ``{name}_active.svg`` and ``{name}_inactive.svg``
* Icons should be 24x24px for consistent sizing
* Use ``currentColor`` for theme compatibility
* Test in all themes (light, dark, colorful)

Advanced Icon Usage
==================

Dynamic Icon States
-------------------

Create icons that change based on application state:

.. code-block:: python

   from PySide6.QtWidgets import QLabel
   from PySide6.QtCore import QTimer
   
   class DynamicIcon(QLabel):
       def __init__(self, base_icon_name: str, parent=None):
           super().__init__(parent)
           self.base_icon_name = base_icon_name
           self.is_active = False
           self.theme_manager = CSSFileBasedThemeManager()
           self.setup_icon()
       
       def setup_icon(self):
           """Set up the icon display"""
           self.setFixedSize(24, 24)
           self.update_icon_state()
       
       def update_icon_state(self):
           """Update icon based on current state"""
           state = "active" if self.is_active else "inactive"
           css_class = f"icon-{self.base_icon_name}-{state}"
           
           css = f"""
           QLabel {{
               background-image: url('{self.get_icon_data_url(state)}');
               background-size: contain;
               background-repeat: no-repeat;
               background-position: center;
           }}
           """
           self.setStyleSheet(css)
       
       def set_active(self, active: bool):
           """Change icon state"""
           if self.is_active != active:
               self.is_active = active
               self.update_icon_state()
       
       def get_icon_data_url(self, state: str) -> str:
           """Get the data URL for the icon"""
           from services.icon_preprocessor import IconPreprocessor
           processor = IconPreprocessor()
           processed_icons = processor.process_all_icons()
           
           icon_key = f"{self.base_icon_name}_{state}"
           return processed_icons.get(icon_key, "")

Animated Icons
-------------

Create simple icon animations using Qt properties:

.. code-block:: python

   from PySide6.QtWidgets import QLabel
   from PySide6.QtCore import QPropertyAnimation, QTimer, pyqtProperty
   
   class AnimatedIcon(QLabel):
       def __init__(self, icon_name: str, parent=None):
           super().__init__(parent)
           self.icon_name = icon_name
           self._opacity = 1.0
           self.setup_animation()
       
       @pyqtProperty(float)
       def opacity(self):
           return self._opacity
       
       @opacity.setter
       def opacity(self, value):
           self._opacity = value
           self.update_opacity()
       
       def setup_animation(self):
           """Set up icon animation"""
           self.animation = QPropertyAnimation(self, b"opacity")
           self.animation.setDuration(1000)  # 1 second
           self.animation.setStartValue(1.0)
           self.animation.setEndValue(0.3)
           self.animation.setLoopCount(-1)  # Infinite loop
       
       def start_animation(self):
           """Start the icon animation"""
           self.animation.start()
       
       def stop_animation(self):
           """Stop the icon animation"""
           self.animation.stop()
           self.opacity = 1.0
       
       def update_opacity(self):
           """Update the visual opacity"""
           self.setStyleSheet(f"QLabel {{ opacity: {self._opacity}; }}")

Icon Customization
=================

Theme-Specific Icon Colors
--------------------------

Icons can adapt to different themes by using CSS variables:

.. code-block:: xml

   <!-- SVG with theme-aware colors -->
   <svg width="24" height="24" viewBox="0 0 24 24" 
        xmlns="http://www.w3.org/2000/svg">
       <path d="M12 2L2 7L12 12L22 7L12 2Z" 
             fill="var(--color-primary)" 
             stroke="var(--color-text)"/>
   </svg>

**CSS Variable Integration:**

.. code-block:: css

   /* In theme files */
   :root {
       --icon-color-primary: var(--color-primary);
       --icon-color-secondary: var(--color-secondary);
       --icon-color-muted: var(--color-text-muted);
   }
   
   /* Icon-specific variables */
   .icon-my-feature-active {
       color: var(--icon-color-primary);
   }
   
   .icon-my-feature-inactive {
       color: var(--icon-color-muted);
   }

Multi-State Icons
----------------

Create icons with multiple states beyond active/inactive:

.. code-block:: text

   icons/
   ├── notification_default.svg   # Default state
   ├── notification_active.svg    # Active state
   ├── notification_alert.svg     # Alert state
   ├── notification_disabled.svg  # Disabled state

.. code-block:: python

   class MultiStateIcon(QLabel):
       def __init__(self, icon_name: str, parent=None):
           super().__init__(parent)
           self.icon_name = icon_name
           self.current_state = "default"
           self.setup_icon()
       
       def set_state(self, state: str):
           """Set icon state: 'default', 'active', 'alert', 'disabled'"""
           valid_states = ['default', 'active', 'alert', 'disabled']
           if state in valid_states:
               self.current_state = state
               self.update_icon()
       
       def update_icon(self):
           """Update icon based on current state"""
           css_class = f"icon-{self.icon_name}-{self.current_state}"
           css = f"""
           QLabel {{
               background-image: url('{self.get_icon_data_url()}');
               background-size: contain;
               background-repeat: no-repeat;
               background-position: center;
           }}
           """
           self.setStyleSheet(css)

Performance Optimization
=======================

Icon Caching
------------

The icon system uses aggressive caching for optimal performance:

.. code-block:: python

   from services.icon_preprocessor import IconPreprocessor
   
   # Icons are automatically cached after first processing
   processor = IconPreprocessor()
   
   # First call: processes and caches icons
   icons1 = processor.process_all_icons()
   
   # Subsequent calls: returns cached results
   icons2 = processor.process_all_icons()  # Much faster
   
   # Clear cache if icons have changed
   processor.clear_cache()

Lazy Loading
-----------

Load icons only when needed to improve startup performance:

.. code-block:: python

   class LazyIconLoader:
       def __init__(self):
           self._loaded_icons = {}
           self.processor = IconPreprocessor()
       
       def get_icon_css(self, icon_name: str, state: str = "inactive") -> str:
           """Get icon CSS, loading on demand"""
           key = f"{icon_name}_{state}"
           
           if key not in self._loaded_icons:
               # Load icon on first access
               all_icons = self.processor.process_all_icons()
               self._loaded_icons[key] = all_icons.get(key, "")
           
           return self._loaded_icons[key]

Best Practices
=============

Icon Design Guidelines
---------------------

1. **Consistent Style**: Maintain visual consistency across all icons
2. **Appropriate Size**: Design at 24x24px for optimal display
3. **Theme Compatibility**: Use ``currentColor`` or CSS variables
4. **Simplicity**: Keep icons simple and recognizable
5. **Accessibility**: Ensure sufficient contrast in all themes

File Organization
----------------

1. **Naming Convention**: Use descriptive, lowercase names with underscores
2. **State Variants**: Always provide both active and inactive states
3. **File Optimization**: Remove unnecessary SVG metadata
4. **Version Control**: Commit both SVG source and generated CSS

Performance Guidelines
---------------------

1. **Cache Awareness**: Understand that icons are cached for performance
2. **Batch Processing**: Process multiple icons together when possible
3. **Memory Management**: Clear cache when no longer needed
4. **Lazy Loading**: Load icons on demand for better startup performance

Development Workflow
===================

Complete Icon Addition Process
-----------------------------

1. **Design Icon**: Create SVG icon following design guidelines
2. **Optimize SVG**: Remove unnecessary elements and use theme colors
3. **Add Files**: Place SVG files in ``icons/`` directory
4. **Test Processing**: Verify icon processing works correctly
5. **Integrate**: Use icon in components with proper CSS classes
6. **Test Themes**: Verify icon appearance in all themes
7. **Performance Check**: Ensure icon loading doesn't impact performance

Development Tools
----------------

**Icon Processing Test:**

.. code-block:: python

   def test_icon_processing():
       """Test that icon processing works correctly"""
       from services.icon_preprocessor import IconPreprocessor
       
       processor = IconPreprocessor()
       processed_icons = processor.process_all_icons()
       
       # Check that your icon was processed
       expected_icons = ['my_feature_active', 'my_feature_inactive']
       for icon in expected_icons:
           if icon in processed_icons:
               print(f"✓ {icon} processed successfully")
           else:
               print(f"✗ {icon} not found")

**CSS Generation Test:**

.. code-block:: python

   def test_icon_css_generation():
       """Test that icon CSS is generated correctly"""
       from services.icon_preprocessor import IconPreprocessor
       
       processor = IconPreprocessor()
       css = processor.generate_icon_css(generate_variables=True)
       
       # Check that your icon CSS is included
       if 'icon-my-feature-active' in css:
           print("✓ Icon CSS generated successfully")
       else:
           print("✗ Icon CSS not found")

Troubleshooting
==============

Common Issues
------------

**Issue: Icon Not Appearing**

1. Check file naming matches convention
2. Verify SVG file is valid
3. Clear icon cache and regenerate
4. Check CSS class names in generated CSS

.. code-block:: python

   # Debug icon loading
   from services.icon_preprocessor import IconPreprocessor
   
   processor = IconPreprocessor()
   processor.clear_cache()  # Clear cache
   icons = processor.process_all_icons()
   
   print("Available icons:")
   for icon_name in icons.keys():
       print(f"  {icon_name}")

**Issue: Icon Wrong Color in Theme**

1. Check SVG uses ``currentColor`` or CSS variables
2. Verify theme CSS includes icon color definitions
3. Test in all themes

.. code-block:: xml

   <!-- Fix: Use currentColor instead of hard-coded color -->
   <path fill="currentColor" stroke="currentColor" />

**Issue: Icon Performance Problems**

1. Check icon file sizes (should be small)
2. Monitor cache usage
3. Use lazy loading for many icons

.. code-block:: python

   # Check cache performance
   from services.css_file_based_theme_manager import CSSFileBasedThemeManager
   
   theme_manager = CSSFileBasedThemeManager()
   theme_manager.print_cache_statistics()

Summary
======

The icon system provides a powerful, theme-integrated way to manage icons in the PySide POEditor Plugin. Key points:

* **Add Icons**: Place SVG files in ``icons/`` directory with proper naming
* **Use CSS Classes**: Icons are converted to CSS classes automatically
* **Theme Integration**: Icons adapt to current theme colors
* **Performance**: System uses caching for optimal performance
* **Best Practices**: Follow naming conventions and design guidelines

For additional information, see:

* :doc:`/services/icon_preprocessor` - Icon processing API reference
* :doc:`css_development_guide` - CSS system integration
* :doc:`theme_creation_guide` - Custom theme creation
* :doc:`/services/css_file_based_theme_manager` - Theme manager API
