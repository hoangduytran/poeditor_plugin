Integration Testing
===================

.. py:module:: tests.integration.css_system_integration

End-to-end testing of the complete CSS centralization system.

Overview
--------

Validates the complete CSS system workflow and component integration.

Class Reference
---------------

.. py:class:: CSSSystemIntegrationTester

   Comprehensive integration testing framework.

   .. py:method:: run_all_integration_tests() -> List[IntegrationTestResult]

      Execute complete integration test suite.

   .. py:method:: test_end_to_end_workflow() -> IntegrationTestResult

      Test complete CSS system workflow.

Usage Example
-------------

.. code-block:: python

   from tests.integration.css_system_integration import CSSSystemIntegrationTester
   
   tester = CSSSystemIntegrationTester()
   results = tester.run_all_integration_tests()
   
   passed = sum(1 for r in results if r.passed)
   print(f"Integration tests: {passed}/{len(results)} passed")
