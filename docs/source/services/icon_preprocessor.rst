Icon Preprocessor
=================

.. py:module:: services.icon_preprocessor

The Icon Preprocessor handles SVG icon processing and CSS generation for the theming system.

Overview
--------

The ``IconPreprocessor`` class manages SVG icon optimization, Base64 encoding, and CSS generation.

Class Reference
---------------

.. py:class:: IconPreprocessor

   SVG icon processing engine for theme integration.

   .. py:method:: generate_icon_css(generate_variables: bool = False) -> str

      Generate CSS for all processed icons.

      :param generate_variables: Whether to include CSS variables
      :returns: Generated icon CSS content
      :rtype: str

   .. py:method:: process_all_icons() -> Dict[str, str]

      Process all SVG icons and return processed content.

      :returns: Dictionary mapping icon names to processed SVG content
      :rtype: Dict[str, str]

Usage Example
-------------

.. code-block:: python

   from services.icon_preprocessor import IconPreprocessor
   
   processor = IconPreprocessor()
   icon_css = processor.generate_icon_css(generate_variables=True)
   processed_icons = processor.process_all_icons()
