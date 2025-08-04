"""
CSS Cache Optimization Enhancement

This module provides advanced caching optimizations for the CSS preprocessing system,
including memory-efficient storage, cache persistence, and intelligent invalidation.
"""

import json
import pickle
import hashlib
import weakref
from pathlib import Path
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from lg import logger


@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata"""
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int

    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class AdvancedCSSCache:
    """
    Advanced caching system for CSS preprocessing with:
    - Memory-efficient storage
    - LRU eviction
    - Persistent cache to disk
    - Intelligent invalidation
    - Cache analytics
    """

    def __init__(self, max_memory_mb: int = 50, max_entries: int = 1000,
                 cache_dir: Optional[str] = None):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_entries = max_entries
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / ".css_cache"

        # In-memory cache
        self.entries: Dict[str, CacheEntry] = {}
        self.current_memory_usage = 0

        # Analytics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        # Weak references to track object usage
        self.weak_refs: Set[weakref.ref] = set()

        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)

        logger.info(f"Advanced CSS cache initialized - Max Memory: {max_memory_mb}MB, Max Entries: {max_entries}")

    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data in bytes"""
        if isinstance(data, str):
            return len(data.encode('utf-8'))
        elif isinstance(data, dict):
            return len(str(data).encode('utf-8'))
        else:
            try:
                return len(pickle.dumps(data))
            except:
                return len(str(data).encode('utf-8'))

    def _generate_cache_key(self, key_components: tuple) -> str:
        """Generate consistent cache key from components"""
        key_str = "|".join(str(c) for c in key_components)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _evict_lru(self):
        """Evict least recently used entries"""
        if not self.entries:
            return

        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].last_accessed
        )

        # Evict oldest entries until under memory limit
        while (self.current_memory_usage > self.max_memory_bytes * 0.8 or
               len(self.entries) > self.max_entries * 0.8):
            if not sorted_entries:
                break

            key, entry = sorted_entries.pop(0)
            self.current_memory_usage -= entry.size_bytes
            del self.entries[key]
            self.evictions += 1

            logger.debug(f"Evicted cache entry: {key[:12]}... (Size: {entry.size_bytes} bytes)")

    def put(self, key_components: tuple, data: Any, persist: bool = True) -> str:
        """Store data in cache with optional persistence"""
        cache_key = self._generate_cache_key(key_components)
        data_size = self._calculate_size(data)

        # Check if we need to evict first
        if (self.current_memory_usage + data_size > self.max_memory_bytes or
            len(self.entries) >= self.max_entries):
            self._evict_lru()

        # Create cache entry
        entry = CacheEntry(
            data=data,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            size_bytes=data_size
        )

        # Store in memory
        self.entries[cache_key] = entry
        self.current_memory_usage += data_size

        # Persist to disk if requested
        if persist:
            self._persist_entry(cache_key, entry)

        logger.debug(f"Cached entry: {cache_key[:12]}... (Size: {data_size} bytes)")
        return cache_key

    def get(self, key_components: tuple, load_from_disk: bool = True) -> Optional[Any]:
        """Retrieve data from cache with optional disk loading"""
        cache_key = self._generate_cache_key(key_components)

        # Check memory cache first
        if cache_key in self.entries:
            entry = self.entries[cache_key]
            entry.touch()
            self.hits += 1
            logger.debug(f"Cache hit (memory): {cache_key[:12]}...")
            return entry.data

        # Check disk cache if enabled
        if load_from_disk:
            disk_data = self._load_from_disk(cache_key)
            if disk_data is not None:
                # Load back into memory cache
                self.put(key_components, disk_data, persist=False)
                self.hits += 1
                logger.debug(f"Cache hit (disk): {cache_key[:12]}...")
                return disk_data

        # Cache miss
        self.misses += 1
        logger.debug(f"Cache miss: {cache_key[:12]}...")
        return None

    def _persist_entry(self, cache_key: str, entry: CacheEntry):
        """Persist cache entry to disk"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.cache"

            # Prepare data for serialization
            entry_data = {
                'data': entry.data,
                'metadata': {
                    'created_at': entry.created_at.isoformat(),
                    'last_accessed': entry.last_accessed.isoformat(),
                    'access_count': entry.access_count,
                    'size_bytes': entry.size_bytes
                }
            }

            with open(cache_file, 'wb') as f:
                pickle.dump(entry_data, f)

        except Exception as e:
            logger.warning(f"Failed to persist cache entry {cache_key[:12]}...: {e}")

    def _load_from_disk(self, cache_key: str) -> Optional[Any]:
        """Load cache entry from disk"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.cache"

            if not cache_file.exists():
                return None

            # Check if file is too old (older than 24 hours)
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > timedelta(hours=24):
                cache_file.unlink()  # Delete old cache file
                return None

            with open(cache_file, 'rb') as f:
                entry_data = pickle.load(f)
                return entry_data['data']

        except Exception as e:
            logger.warning(f"Failed to load cache entry {cache_key[:12]}... from disk: {e}")
            return None

    def clear(self, clear_disk: bool = True):
        """Clear all cache entries"""
        self.entries.clear()
        self.current_memory_usage = 0

        if clear_disk:
            try:
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                logger.info("Cleared disk cache")
            except Exception as e:
                logger.warning(f"Failed to clear disk cache: {e}")

        logger.info("Cleared memory cache")

    def cleanup_expired(self, max_age_hours: int = 48):
        """Clean up expired cache entries"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_keys = []

        # Find expired memory entries
        for key, entry in self.entries.items():
            if entry.last_accessed < cutoff_time:
                expired_keys.append(key)

        # Remove expired memory entries
        for key in expired_keys:
            entry = self.entries[key]
            self.current_memory_usage -= entry.size_bytes
            del self.entries[key]

        # Clean up expired disk cache files
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_age > timedelta(hours=max_age_hours):
                    cache_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup expired disk cache: {e}")

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hits + self.misses
        hit_ratio = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'hit_ratio': hit_ratio,
            'total_hits': self.hits,
            'total_misses': self.misses,
            'total_evictions': self.evictions,
            'memory_usage_mb': self.current_memory_usage / 1024 / 1024,
            'memory_usage_percent': (self.current_memory_usage / self.max_memory_bytes * 100),
            'entry_count': len(self.entries),
            'average_entry_size': (self.current_memory_usage / len(self.entries)) if self.entries else 0
        }

    def print_statistics(self):
        """Print cache performance statistics"""
        stats = self.get_statistics()

        logger.info("=== CSS CACHE STATISTICS ===")
        logger.info(f"Hit Ratio: {stats['hit_ratio']:.1f}%")
        logger.info(f"Total Hits: {stats['total_hits']}")
        logger.info(f"Total Misses: {stats['total_misses']}")
        logger.info(f"Total Evictions: {stats['total_evictions']}")
        logger.info(f"Memory Usage: {stats['memory_usage_mb']:.1f} MB ({stats['memory_usage_percent']:.1f}%)")
        logger.info(f"Entry Count: {stats['entry_count']}")
        logger.info(f"Avg Entry Size: {stats['average_entry_size']:.1f} bytes")
        logger.info("=== END CACHE STATISTICS ===")


# Enhanced CSSPreprocessor mixin
class CacheOptimizedMixin:
    """
    Mixin to add advanced caching to CSSPreprocessor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Replace simple cache with advanced cache
        if hasattr(self, 'cache'):
            delattr(self, 'cache')

        self.advanced_cache = AdvancedCSSCache(
            max_memory_mb=25,  # 25MB memory limit
            max_entries=500,   # 500 entry limit
            cache_dir=".css_cache"
        )

        logger.info("Advanced CSS caching enabled")

    def _get_cached_result(self, cache_type: str, *key_components) -> Optional[Any]:
        """Get result from advanced cache"""
        full_key = (cache_type, *key_components)
        return self.advanced_cache.get(full_key)

    def _cache_result(self, result: Any, cache_type: str, *key_components):
        """Store result in advanced cache"""
        full_key = (cache_type, *key_components)
        self.advanced_cache.put(full_key, result)

    def clear_cache(self):
        """Clear advanced cache"""
        if hasattr(self, 'advanced_cache'):
            self.advanced_cache.clear()
            logger.info("Cleared advanced CSS cache")
        elif hasattr(self, 'cache'):
            # Fallback to original cache implementation
            self.cache = {}
            logger.debug("Cleared CSS preprocessor cache")

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        if hasattr(self, 'advanced_cache'):
            return self.advanced_cache.get_statistics()
        return {}

    def print_cache_statistics(self):
        """Print cache performance statistics"""
        if hasattr(self, 'advanced_cache'):
            self.advanced_cache.print_statistics()

    def cleanup_cache(self):
        """Clean up expired cache entries"""
        if hasattr(self, 'advanced_cache'):
            self.advanced_cache.cleanup_expired()


def optimize_css_preprocessor_cache():
    """
    Apply cache optimizations to existing CSSPreprocessor instances
    """
    from services.css_preprocessor import CSSPreprocessor

    # Monkey patch the CSSPreprocessor class to include advanced caching
    original_init = CSSPreprocessor.__init__
    original_clear_cache = CSSPreprocessor.clear_cache

    def enhanced_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # Replace simple cache with advanced cache
        self.advanced_cache = AdvancedCSSCache(
            max_memory_mb=25,
            max_entries=500,
            cache_dir=".css_cache"
        )
        logger.info("Enhanced CSSPreprocessor with advanced caching")

    def enhanced_clear_cache(self):
        if hasattr(self, 'advanced_cache'):
            self.advanced_cache.clear()
        else:
            original_clear_cache(self)

    # Apply patches
    CSSPreprocessor.__init__ = enhanced_init
    CSSPreprocessor.clear_cache = enhanced_clear_cache

    # Add new methods to the class
    def get_cache_statistics(self):
        return self.advanced_cache.get_statistics() if hasattr(self, 'advanced_cache') else {}

    def print_cache_statistics(self):
        if hasattr(self, 'advanced_cache'):
            self.advanced_cache.print_statistics()

    def cleanup_cache(self):
        if hasattr(self, 'advanced_cache'):
            self.advanced_cache.cleanup_expired()

    # Attach methods to class
    setattr(CSSPreprocessor, 'get_cache_statistics', get_cache_statistics)
    setattr(CSSPreprocessor, 'print_cache_statistics', print_cache_statistics)
    setattr(CSSPreprocessor, 'cleanup_cache', cleanup_cache)

    logger.info("Applied advanced caching optimizations to CSSPreprocessor")


if __name__ == "__main__":
    # Test the advanced cache system
    cache = AdvancedCSSCache(max_memory_mb=1, max_entries=10)

    # Test cache operations
    cache.put(("test", "key1"), "test data 1")
    cache.put(("test", "key2"), "test data 2")

    # Test retrieval
    result1 = cache.get(("test", "key1"))
    result2 = cache.get(("test", "key3"))  # Should be None

    print(f"Result 1: {result1}")
    print(f"Result 2: {result2}")

    # Print statistics
    cache.print_statistics()
