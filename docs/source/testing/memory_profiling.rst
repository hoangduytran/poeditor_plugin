Memory Profiling
================

.. py:module:: tests.performance.css_memory_profiler

Memory usage analysis and optimization for the CSS centralization system.

Overview
--------

Profiles memory usage during CSS operations to detect leaks and optimize performance.

Class Reference
---------------

.. py:class:: CSSMemoryProfiler

   Memory profiling and analysis framework.

   .. py:method:: run_memory_profiling() -> List[MemoryProfile]

      Execute complete memory profiling suite.

   .. py:method:: profile_theme_switching() -> MemoryProfile

      Profile memory usage during theme switching operations.

Usage Example
-------------

.. code-block:: python

   from tests.performance.css_memory_profiler import CSSMemoryProfiler
   
   profiler = CSSMemoryProfiler()
   profiles = profiler.run_memory_profiling()
   
   for profile in profiles:
       print(f"{profile.test_name}: {profile.memory_growth_mb:.1f}MB growth")
