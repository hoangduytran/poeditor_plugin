Introduction
============

What is POEditor Plugin?
----------------------

The POEditor Plugin is a comprehensive tool designed for managing and editing translation files. Built with PySide6, it provides a modern, extensible interface for translation workflows.

Key Features
-----------

* **Explorer Context Menu**: Perform file operations like copy, cut, paste, rename, and delete with full undo/redo support
* **Plugin Architecture**: Extensible design allows adding new functionality through plugins
* **Activity Bar**: Quick access to different application modes (Explorer, Search, etc.)
* **Theme Support**: Customizable appearance with light and dark theme options
* **Advanced Search**: Find text across multiple translation files
* **Translation Database**: Store and retrieve translation suggestions

Architecture Overview
-------------------

The application is built on a modular architecture:

.. code-block::

    ┌─────────────────────────────────────────┐
    │             Main Application            │
    └───────────────────┬─────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                   ▼           ▼
    ┌───────────┐     ┌──────────┐  ┌────────┐
    │   Core    │     │ Services │  │ Widgets│
    └─────┬─────┘     └─────┬────┘  └───┬────┘
          │                 │           │
          ▼                 ▼           ▼
    ┌───────────┐     ┌──────────┐  ┌────────┐
    │ Plugins   │     │  Models  │  │ Panels │
    └───────────┘     └──────────┘  └────────┘

Components
---------

1. **Core**: Foundational components like plugin manager, sidebar manager, and tab manager
2. **Services**: Helper classes that provide functionality like file operations, theming, configuration
3. **Models**: Data structures for activities, files, and other application objects
4. **Widgets**: Reusable UI components like activity bar, sidebar dock, and explorer view
5. **Panels**: Content panels displayed in the sidebar (Explorer, Search, etc.)
6. **Plugins**: Extension points that add new functionality to the application
