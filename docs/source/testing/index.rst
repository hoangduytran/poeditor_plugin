Testing Framework
=================

Comprehensive testing infrastructure for the CSS centralization system.

.. toctree::
   :maxdepth: 2
   
   performance_testing
   compatibility_testing
   integration_testing
   memory_profiling

Overview
--------

The testing framework provides comprehensive validation of the CSS centralization system including:

* **Performance Testing**: Benchmarking theme switching and processing speed
* **Compatibility Testing**: Cross-platform CSS rendering validation
* **Integration Testing**: End-to-end system functionality testing
* **Memory Profiling**: Memory usage analysis and leak detection

Testing Components
------------------

Performance Benchmarks
~~~~~~~~~~~~~~~~~~~~~~~

Automated performance testing with configurable targets and detailed metrics.

Compatibility Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

Cross-platform testing ensuring consistent CSS rendering across operating systems.

Integration Tests
~~~~~~~~~~~~~~~~~

End-to-end testing of the complete CSS system workflow.

Memory Analysis
~~~~~~~~~~~~~~~

Memory usage profiling and optimization guidance.

Running Tests
-------------

.. code-block:: bash

   # Run all CSS system tests
   python -m tests.run_all_css_tests
   
   # Run specific test suites
   python -m tests.performance.css_performance_benchmark
   python -m tests.compatibility.cross_platform_css_validator
   python -m tests.integration.css_system_integration
   python -m tests.performance.css_memory_profiler
