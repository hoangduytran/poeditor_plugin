Compatibility Testing
====================

.. py:module:: tests.compatibility.cross_platform_css_validator

Cross-platform CSS rendering validation for consistent user experience.

Overview
--------

Validates CSS rendering consistency across macOS, Windows, and Linux platforms.

Class Reference
---------------

.. py:class:: CrossPlatformCSSValidator

   Cross-platform compatibility testing framework.

   .. py:method:: run_all_tests() -> List[Dict[str, Any]]

      Execute all compatibility tests.

   .. py:method:: test_font_rendering() -> bool

      Test font consistency across platforms.

Usage Example
-------------

.. code-block:: python

   from tests.compatibility.cross_platform_css_validator import CrossPlatformCSSValidator
   
   validator = CrossPlatformCSSValidator()
   results = validator.run_all_tests()
   
   passed = sum(1 for r in results if r['passed'])
   print(f"Compatibility tests: {passed}/{len(results)} passed")
