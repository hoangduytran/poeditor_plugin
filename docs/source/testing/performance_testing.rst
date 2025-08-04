Performance Testing
===================

.. py:module:: tests.performance.css_performance_benchmark

Automated performance benchmarking for CSS centralization system.

Overview
--------

The performance testing framework validates that the CSS system meets performance targets.

**Performance Targets:**

* Theme switching: < 100ms
* CSS processing: < 50ms  
* Icon processing: < 30ms
* Cache speedup: > 2x improvement

Class Reference
---------------

.. py:class:: CSSPerformanceBenchmark

   Comprehensive performance testing framework.

   .. py:method:: run_all_benchmarks() -> Dict[str, Any]

      Execute all performance benchmarks and return results.

   .. py:method:: benchmark_theme_switching() -> float

      Measure theme switching performance.

   .. py:method:: benchmark_css_processing() -> float

      Measure CSS processing speed.

Usage Example
-------------

.. code-block:: python

   from tests.performance.css_performance_benchmark import CSSPerformanceBenchmark
   
   benchmark = CSSPerformanceBenchmark()
   results = benchmark.run_all_benchmarks()
   
   print(f"Theme switching: {results['theme_switching_time']:.1f}ms")
   print(f"CSS processing: {results['css_processing_time']:.1f}ms")
