=======================
API Documentation Guide
=======================

:Date: July 28, 2025
:Component: Developer Documentation
:Version: 1.0.0
:Status: Production

Overview
========

This guide explains the structure and organization of the API documentation for the PySide POEditor Plugin project. It serves as a reference for developers who need to understand or extend the documentation.

Documentation Structure
=======================

The project documentation is organized into several key documents:

API Documentation
-----------------

- :doc:`explorer_api_documentation` - Comprehensive API reference for Explorer components
- :doc:`core_services_api` - API reference for core services

Technical Documentation
----------------------------

- :doc:`enhanced_explorer_technical_design` - Technical architecture and design decisions
- :doc:`implementation_guide` - Implementation details and patterns

User Documentation
------------------

- :doc:`enhanced_explorer_user_guide` - End-user guide for Explorer features

Release Information
------------------

- :doc:`explorer_changelog` - Version history and changes

Developer References
--------------------

- :doc:`explorer_developer_reference` - Quick reference for developers

Documentation Standards
=======================

Document Header Format
----------------------

All documentation files should start with a standard header::

    Document Title
    ==============

    :Date: YYYY-MM-DD
    :Component: Component Name
    :Version: X.Y.Z
    :Status: [Development|Review|Production]

API Documentation Format
------------------------

API documentation should follow this structure:

Class Documentation
~~~~~~~~~~~~~~~~~~~

Each class should be documented with:

1. **Purpose and Responsibility**
   
   Clear description of what the class does and why it exists.

2. **Constructor Parameters**
   
   .. code-block:: python
   
      class ExampleClass:
          """
          Brief description of the class.
          
          :param param1: Description of parameter 1
          :type param1: str
          :param param2: Description of parameter 2
          :type param2: int
          """

3. **Public Methods**
   
   Each public method should include:
   
   - Purpose and behavior
   - Parameters with types
   - Return values with types
   - Exceptions that may be raised
   - Example usage

4. **Signals (for QObject classes)**
   
   List all signals with:
   
   - Signal signature
   - When the signal is emitted
   - What data is passed

Method Documentation Format
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this template for documenting methods::

    def method_name(self, param1: str, param2: int = 0) -> bool:
        """
        Brief description of what the method does.
        
        Detailed description if needed, explaining the behavior,
        side effects, and any important implementation details.
        
        :param param1: Description of parameter 1
        :type param1: str
        :param param2: Description of parameter 2 (optional)
        :type param2: int
        :return: Description of return value
        :rtype: bool
        :raises ValueError: When param1 is empty
        :raises RuntimeError: When operation fails
        
        Example:
            >>> obj = ExampleClass()
            >>> result = obj.method_name("test", 5)
            >>> print(result)
            True
        """

Code Examples
~~~~~~~~~~~~~

Include practical examples for complex APIs:

.. code-block:: python

   # Example: Using the Explorer API
   from core.explorer_service import ExplorerService
   from models.file_system_models import FileSystemModel
   
   # Initialize the service
   explorer = ExplorerService()
   
   # Set up the model
   model = FileSystemModel()
   explorer.set_model(model)
   
   # Navigate to a directory
   success = explorer.navigate_to("/home/user/documents")
   if success:
       print("Navigation successful")

Best Practices
==============

Documentation Writing Guidelines
-------------------------------

1. **Be Clear and Concise**
   
   - Use simple, direct language
   - Avoid unnecessary jargon
   - Explain complex concepts step by step

2. **Provide Context**
   
   - Explain why something exists
   - Describe how it fits into the larger system
   - Include background information when helpful

3. **Use Examples**
   
   - Show practical usage scenarios
   - Include complete, runnable code examples
   - Demonstrate common patterns and use cases

4. **Keep Documentation Current**
   
   - Update docs when code changes
   - Review documentation during code reviews
   - Remove outdated information promptly

Code Documentation
-----------------

1. **Docstring Standards**
   
   - Use Python docstring conventions
   - Include type hints in function signatures
   - Document all public APIs

2. **Comment Guidelines**
   
   - Explain complex logic
   - Document design decisions
   - Clarify non-obvious behavior

3. **Naming Conventions**
   
   - Use descriptive names
   - Follow Python naming conventions
   - Be consistent across the codebase

Cross-References
===============

To maintain consistency across documentation:

- Use ``:doc:`` directive for referencing other documents
- Use ``:class:`` directive for referencing classes
- Use ``:meth:`` directive for referencing methods
- Use ``:attr:`` directive for referencing attributes

Example cross-references::

    See :doc:`explorer_api_documentation` for complete API details.
    
    The :class:`ExplorerService` class provides navigation functionality.
    
    Use the :meth:`ExplorerService.navigate_to` method to change directories.
    
    The :attr:`ExplorerService.current_path` attribute stores the current location.

Sphinx Configuration
===================

The documentation uses Sphinx for generation. Key configuration options:

Extensions
----------

.. code-block:: python

   extensions = [
       'sphinx.ext.autodoc',       # Automatic documentation from docstrings
       'sphinx.ext.viewcode',      # Include source code in docs
       'sphinx.ext.intersphinx',   # Link to other projects' documentation
       'sphinx.ext.napoleon',      # Support for Google/NumPy docstring styles
   ]

Autodoc Settings
---------------

.. code-block:: python

   autodoc_default_options = {
       'members': True,
       'member-order': 'bysource',
       'special-members': '__init__',
       'undoc-members': True,
       'exclude-members': '__weakref__'
   }

Building Documentation
=====================

Local Development
----------------

To build documentation locally:

.. code-block:: bash

   cd docs/
   make html

The generated documentation will be in ``docs/build/html/``.

Continuous Integration
---------------------

Documentation is automatically built and published when:

- Changes are pushed to the main branch
- Pull requests are created (for review)
- New releases are tagged

Troubleshooting
==============

Common Issues
------------

1. **Missing Cross-References**
   
   - Ensure referenced documents exist
   - Check file paths and naming
   - Verify Sphinx can find all referenced content

2. **Code Examples Not Highlighting**
   
   - Check language specification in code blocks
   - Ensure Pygments supports the specified language
   - Verify syntax is correct

3. **Build Warnings**
   
   - Address all Sphinx warnings
   - Check for circular references
   - Ensure all required files are present

Maintenance
===========

Regular Tasks
------------

1. **Review and Update**
   
   - Quarterly review of all documentation
   - Update examples to reflect current APIs
   - Remove deprecated information

2. **Quality Checks**
   
   - Verify all links work correctly
   - Test code examples
   - Check for spelling and grammar errors

3. **User Feedback Integration**
   
   - Monitor user questions and confusion points
   - Update documentation based on feedback
   - Add FAQ sections for common questions

Contributing
===========

When contributing to documentation:

1. Follow the established format and style
2. Include examples for new features
3. Update cross-references as needed
4. Test documentation builds locally
5. Review changes for clarity and accuracy

For questions about documentation, see :doc:`developer_reference` or contact the development team.
