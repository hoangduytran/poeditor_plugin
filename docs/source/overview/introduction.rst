Introduction
============

What is POEditor Plugin?
----------------------

The POEditor Plugin is a comprehensive tool designed for managing and editing translation files. Built with PySide6, it provides a modern, extensible interface for translation workflows.

Key Features
-----------

* :doc:`Explorer Context Menu <../panels/enhanced_explorer_panel>`: Perform file operations like copy, cut, paste, rename, and delete with full undo/redo support
* :doc:`Plugin Architecture <../core/plugin_manager>`: Extensible design allows adding new functionality through plugins
* :doc:`Activity Bar <../widgets/index>`: Quick access to different application modes (Explorer, Search, etc.)
* :doc:`Theme Support <../services/index>`: Customizable appearance with light and dark theme options
* :doc:`Advanced Search <../panels/index>`: Find text across multiple translation files
* :doc:`Translation Database <../services/index>`: Store and retrieve translation suggestions

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

1. **Core**: Foundational components like :doc:`plugin manager <../core/plugin_manager>`,
   :doc:`sidebar manager <../core/sidebar_manager>`, and :doc:`tab manager <../core/tab_manager>`
   → See :doc:`../core/index`

2. **Services**: Helper classes that provide functionality like
   :doc:`file operations <../services/file_operations_service>`,
   :doc:`theming <../services/theme_manager>`, and configuration
   → See :doc:`../services/index`

3. **Models**: Data structures for :doc:`activities <../models/activity_models>`,
   :doc:`files <../models/file_system_models>`, and other application objects
   → See :doc:`../models/index`

4. **Widgets**: Reusable UI components like activity bar, sidebar dock, and
   :doc:`explorer view <../widgets/enhanced_explorer_widget>`
   → See :doc:`../widgets/index`

5. **Panels**: Content panels displayed in the sidebar like
   :doc:`Explorer <../panels/enhanced_explorer_panel>`, Search, etc.
   → See :doc:`../panels/index`

6. **Plugins**: Extension points that add new functionality to the application
   → See :doc:`../plugins/index`
