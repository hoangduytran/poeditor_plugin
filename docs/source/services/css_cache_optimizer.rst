CSS Cache Optimizer
===================

.. py:module:: services.css_cache_optimizer

Advanced caching system for CSS centralization with memory management and performance optimization.

Overview
--------

The CSS Cache Optimizer provides high-performance caching with LRU eviction and disk persistence.

Class Reference
---------------

.. py:class:: AdvancedCSSCache

   Memory-efficient caching system with intelligent eviction policies.

   .. py:method:: put(key: str, value: str) -> None

      Store a value in the cache with the specified key.

      :param key: Cache key
      :param value: Value to cache
      :type key: str
      :type value: str

   .. py:method:: get(key: str) -> Optional[str]

      Retrieve a value from the cache.

      :param key: Cache key to retrieve
      :returns: Cached value or None if not found
      :rtype: Optional[str]

   .. py:method:: clear() -> None

      Clear all cached entries.

   .. py:method:: get_statistics() -> Dict[str, Any]

      Get cache performance statistics.

      :returns: Dictionary containing cache metrics
      :rtype: Dict[str, Any]

Usage Example
-------------

.. code-block:: python

   from services.css_cache_optimizer import AdvancedCSSCache
   
   cache = AdvancedCSSCache(max_memory_mb=25)
   cache.put('theme_dark', processed_css)
   
   cached_css = cache.get('theme_dark')
   stats = cache.get_statistics()
