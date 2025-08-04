========
Overview
========

.. only:: html

   .. container:: intro-text

      Welcome to the POEditor Plugin! This section provides an introduction to the application,
      including installation instructions and basic usage guidelines.

.. toctree::
   :hidden:
   :maxdepth: 2

   introduction
   installation
   usage

Getting Started
===============

The POEditor Plugin provides a comprehensive translation management interface. 
Get started with these essential sections:

**What is POEditor?**

:doc:`introduction` - Learn about the POEditor Plugin and discover its purpose and 
capabilities. Understand the core features and architecture that make this tool 
powerful for translation workflows.

**Installing POEditor**

:doc:`installation` - Step-by-step guide to installing and setting up the POEditor 
Plugin. Includes requirements, setup instructions, and configuration details.

**Using POEditor**

:doc:`usage` - Basic instructions for getting started with POEditor. Learn navigation, 
file operations, and essential workflows.

Key Features
============

Explore the powerful capabilities of the POEditor Plugin:

**Enhanced File Explorer**

:doc:`../explorer/index` - Navigate and manage translation files with advanced tools 
and context menus. Features include file operations, filtering, and comprehensive 
project navigation.

Explorer Features
~~~~~~~~~~~~~~~~~

The file explorer provides comprehensive file management capabilities:

* **Context Menus**: Right-click operations for :doc:`../explorer/explorer_context_menu`
* **File Operations**: Copy, cut, paste, rename, delete with :doc:`../services/undo_redo_service`
* **Search & Filter**: Find files quickly with built-in filtering
* **Navigation**: Tree view with :doc:`../explorer/header_navigation` support

File Operations
~~~~~~~~~~~~~~~

* **Drag & Drop**: :doc:`../services/drag_drop_service` for intuitive file management
* **Undo/Redo**: Full operation history with :doc:`../services/undo_redo_service`
* **Batch Operations**: Multiple file selection and operations

**Theme Support**

:doc:`../services/theme_manager` - Customize the appearance with light, dark and 
custom themes. The theming system provides consistent styling across all components.

Theme Management
~~~~~~~~~~~~~~~~

The application supports comprehensive theming capabilities:

* **Built-in Themes**: Light, dark, and colorful themes available out of the box
* **CSS Processing**: Advanced :doc:`../services/css_preprocessor` with variable support
* **Icon Integration**: :doc:`../services/icon_preprocessor` for consistent iconography
* **Theme Switching**: Real-time theme changes via :doc:`../services/css_file_based_theme_manager`

Theme Development
~~~~~~~~~~~~~~~~~

Create custom themes using the powerful theming system:

* **CSS Variables**: Use CSS custom properties for consistent theming
* **Theme Creation**: Follow the :doc:`../guides/theme_creation_guide`
* **CSS Development**: Learn :doc:`../guides/css_development_guide` best practices
* **Component Styling**: Use :doc:`../guides/component_styling_guide` for UI elements

**Plugin System**

:doc:`../plugins/index` - Extend functionality with custom plugins and integrations. 
The modular architecture allows adding new features through a well-defined plugin API.

Plugin Communication
~~~~~~~~~~~~~~~~~~~~

Plugins can communicate with the core application and other plugins through:

* **Services**: Accessing shared :doc:`../services/index` through the plugin manager
* **Events**: Publishing and subscribing to application events via the :doc:`../core/api`
* **Direct API**: Directly accessing APIs exposed by other plugins through the 
  :doc:`../guides/plugin_development_guide`

Plugin Development
~~~~~~~~~~~~~~~~~~

* **Plugin Architecture**: Learn the :doc:`../architecture/index` principles
* **Development Guide**: Follow the :doc:`../guides/plugin_development_guide` 
* **API Reference**: Use the :doc:`../core/plugin_manager` for plugin registration

Development Resources
=====================

Learn how to extend and customize the POEditor Plugin:

**Development Guides**

:doc:`../guides/index` - Comprehensive development guides for creating plugins, themes, 
services, and components. Includes best practices and detailed examples.

**System Architecture**

:doc:`../architecture/index` - Understand the modular architecture, component relationships, 
and design principles that power the application.

**Core API Reference**

:doc:`../core/index` - Detailed API documentation for core managers, services, and utilities. 
Essential reference for developers.

Quick Start Checklist
======================

After installation, follow these steps to get started:

1. **Launch the Application**
   
   Run ``python main.py`` from the project directory
   
2. **Explore the Interface**
   
   * Click Explorer icon to browse files
   * Use the search function to find content
   * Try different themes in Preferences
   
3. **Customize Your Setup**
   
   * Set your preferred theme
   * Configure file associations
   * Install additional plugins

4. **Start Working**
   
   * Open translation files in the Explorer
   * Use context menus for file operations
   * Take advantage of undo/redo functionality

Additional Resources
====================

**Testing Framework**

:doc:`../testing/index` - Comprehensive testing framework including unit tests, 
integration tests, and performance benchmarks.

**Service Layer**

:doc:`../services/index` - File operations, theming, CSS processing, drag & drop, 
and other core services that power the application.
