CSS Preprocessor
================

.. py:module:: services.css_preprocessor

The CSS Preprocessor handles CSS variable resolution, file combination, and optimization for the CSS centralization system.

Overview
--------

The ``CSSPreprocessor`` class provides core CSS processing functionality including variable substitution, file combination, and performance optimization through caching.

Class Reference
---------------

.. py:class:: CSSPreprocessor

   CSS processing engine for variable resolution and file combination.

   .. py:method:: process_css(css_content: str, variables: Dict[str, str]) -> str

      Process CSS content with variable substitution.

      :param css_content: Raw CSS content to process
      :param variables: Dictionary of CSS variables to substitute
      :returns: Processed CSS with variables resolved
      :rtype: str

   .. py:method:: combine_css_files(file_paths: List[str], variables: Dict[str, str]) -> str

      Combine multiple CSS files with variable processing.

      :param file_paths: List of CSS file paths to combine
      :param variables: Dictionary of CSS variables to substitute
      :returns: Combined and processed CSS content
      :rtype: str

Usage Example
-------------

.. code-block:: python

   from services.css_preprocessor import CSSPreprocessor
   
   preprocessor = CSSPreprocessor()
   
   variables = {
       '--color-primary': '#007ACC',
       '--spacing-md': '16px'
   }
   
   css = """
   QWidget {
       color: var(--color-primary);
       padding: var(--spacing-md);
   }
   """
   
   processed = preprocessor.process_css(css, variables)
