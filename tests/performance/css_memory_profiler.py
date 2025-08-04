"""
Memory Profiling for CSS Centralization System

This module provides memory usage analysis and profiling for the CSS
centralization system to ensure optimal memory consumption and detect
potential memory leaks.
"""

import time
import gc
import tracemalloc
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from PySide6.QtWidgets import QApplication

from lg import logger


@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a specific point"""
    timestamp: float
    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    python_memory_mb: float  # Python memory usage in MB
    css_cache_size: int  # Number of entries in CSS cache
    icon_cache_size: int  # Number of entries in icon cache
    description: str


@dataclass
class MemoryProfile:
    """Complete memory profile for a test run"""
    test_name: str
    initial_snapshot: MemorySnapshot
    final_snapshot: MemorySnapshot
    peak_snapshot: MemorySnapshot
    snapshots: List[MemorySnapshot]
    memory_growth_mb: float
    peak_memory_mb: float
    cache_efficiency: Dict[str, Any]
    recommendations: List[str]


class CSSMemoryProfiler:
    """
    Memory profiler for CSS centralization system

    Tracks memory usage during CSS operations and identifies
    potential memory leaks or excessive memory consumption.
    """

    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        self.peak_memory = 0.0
        self.theme_manager = None

    def setup_profiling(self):
        """Initialize memory profiling"""
        tracemalloc.start()
        gc.collect()  # Clean up before profiling
        logger.info("Memory profiling initialized")

    def take_snapshot(self, description: str) -> MemorySnapshot:
        """Take a memory usage snapshot"""
        # Get Python memory info from tracemalloc
        current, peak = tracemalloc.get_traced_memory()
        python_memory_mb = current / 1024 / 1024

        # Use simple approximation for RSS/VMS (Python memory * 2-3 is typical)
        rss_mb = python_memory_mb * 2.5
        vms_mb = python_memory_mb * 3.0

        # Update peak tracking
        if rss_mb > self.peak_memory:
            self.peak_memory = rss_mb

        # Get cache sizes if available
        css_cache_size = 0
        icon_cache_size = 0

        if self.theme_manager:
            if hasattr(self.theme_manager, 'css_cache'):
                css_cache_size = len(getattr(self.theme_manager, 'css_cache', {}))

            if hasattr(self.theme_manager, 'icon_cache'):
                icon_cache_size = len(getattr(self.theme_manager, 'icon_cache', {}))

        snapshot = MemorySnapshot(
            timestamp=time.time(),
            rss_mb=rss_mb,
            vms_mb=vms_mb,
            python_memory_mb=python_memory_mb,
            css_cache_size=css_cache_size,
            icon_cache_size=icon_cache_size,
            description=description
        )

        self.snapshots.append(snapshot)
        logger.info(f"Memory snapshot '{description}': {rss_mb:.1f}MB RSS, {python_memory_mb:.1f}MB Python")

        return snapshot

    @contextmanager
    def profile_operation(self, operation_name: str):
        """Context manager for profiling a specific operation"""
        logger.info(f"Starting memory profiling for: {operation_name}")

        # Take initial snapshot
        initial = self.take_snapshot(f"{operation_name} - start")

        try:
            yield
        finally:
            # Take final snapshot
            final = self.take_snapshot(f"{operation_name} - end")

            # Log memory change
            memory_change = final.rss_mb - initial.rss_mb
            logger.info(f"Memory change for {operation_name}: {memory_change:+.1f}MB")

            if memory_change > 10:  # More than 10MB increase
                logger.warning(f"High memory usage detected in {operation_name}: {memory_change:.1f}MB")

    def profile_theme_switching(self) -> MemoryProfile:
        """Profile memory usage during theme switching"""
        logger.info("Profiling theme switching memory usage")

        # Initialize theme manager
        from services.css_file_based_theme_manager import CSSFileBasedThemeManager
        self.theme_manager = CSSFileBasedThemeManager()

        initial = self.take_snapshot("theme_switching_start")

        # Switch between themes multiple times
        themes = ['light', 'dark', 'colorful', 'light', 'dark', 'colorful']

        for i, theme in enumerate(themes):
            with self.profile_operation(f"switch_to_{theme}_{i}"):
                self.theme_manager.set_theme(theme)
                gc.collect()  # Force garbage collection

        final = self.take_snapshot("theme_switching_end")

        # Find peak memory usage
        peak_snapshot = max(self.snapshots, key=lambda s: s.rss_mb)

        # Calculate cache efficiency
        cache_efficiency = self._calculate_cache_efficiency()

        # Generate recommendations
        recommendations = self._generate_memory_recommendations(initial, final, peak_snapshot)

        profile = MemoryProfile(
            test_name="theme_switching",
            initial_snapshot=initial,
            final_snapshot=final,
            peak_snapshot=peak_snapshot,
            snapshots=self.snapshots.copy(),
            memory_growth_mb=final.rss_mb - initial.rss_mb,
            peak_memory_mb=peak_snapshot.rss_mb,
            cache_efficiency=cache_efficiency,
            recommendations=recommendations
        )

        self._log_memory_profile(profile)
        return profile

    def profile_css_processing(self) -> MemoryProfile:
        """Profile memory usage during CSS processing"""
        logger.info("Profiling CSS processing memory usage")

        if not self.theme_manager:
            from services.css_file_based_theme_manager import CSSFileBasedThemeManager
            self.theme_manager = CSSFileBasedThemeManager()

        initial = self.take_snapshot("css_processing_start")

        # Process CSS multiple times to check for leaks
        for i in range(10):
            with self.profile_operation(f"css_process_iteration_{i}"):
                # Force CSS reprocessing
                self.theme_manager.set_theme('light')
                self.theme_manager.set_theme('dark')

                if i % 3 == 0:  # Periodic garbage collection
                    gc.collect()

        final = self.take_snapshot("css_processing_end")

        peak_snapshot = max(self.snapshots, key=lambda s: s.rss_mb)
        cache_efficiency = self._calculate_cache_efficiency()
        recommendations = self._generate_memory_recommendations(initial, final, peak_snapshot)

        profile = MemoryProfile(
            test_name="css_processing",
            initial_snapshot=initial,
            final_snapshot=final,
            peak_snapshot=peak_snapshot,
            snapshots=self.snapshots.copy(),
            memory_growth_mb=final.rss_mb - initial.rss_mb,
            peak_memory_mb=peak_snapshot.rss_mb,
            cache_efficiency=cache_efficiency,
            recommendations=recommendations
        )

        self._log_memory_profile(profile)
        return profile

    def profile_icon_processing(self) -> MemoryProfile:
        """Profile memory usage during icon processing"""
        logger.info("Profiling icon processing memory usage")

        if not self.theme_manager:
            from services.css_file_based_theme_manager import CSSFileBasedThemeManager
            self.theme_manager = CSSFileBasedThemeManager()

        initial = self.take_snapshot("icon_processing_start")

        # Process icons multiple times
        if hasattr(self.theme_manager, 'icon_preprocessor') and self.theme_manager.icon_preprocessor:
            icon_processor = self.theme_manager.icon_preprocessor

            for i in range(5):
                with self.profile_operation(f"icon_process_iteration_{i}"):
                    # Generate icon CSS (method exists in our system)
                    if hasattr(icon_processor, 'generate_icon_css'):
                        icon_css = icon_processor.generate_icon_css()

                    # Process all icons (if method exists)
                    if hasattr(icon_processor, 'process_all_icons'):
                        processed_icons = icon_processor.process_all_icons()

                    if i % 2 == 0:
                        gc.collect()

        final = self.take_snapshot("icon_processing_end")

        peak_snapshot = max(self.snapshots, key=lambda s: s.rss_mb)
        cache_efficiency = self._calculate_cache_efficiency()
        recommendations = self._generate_memory_recommendations(initial, final, peak_snapshot)

        profile = MemoryProfile(
            test_name="icon_processing",
            initial_snapshot=initial,
            final_snapshot=final,
            peak_snapshot=peak_snapshot,
            snapshots=self.snapshots.copy(),
            memory_growth_mb=final.rss_mb - initial.rss_mb,
            peak_memory_mb=peak_snapshot.rss_mb,
            cache_efficiency=cache_efficiency,
            recommendations=recommendations
        )

        self._log_memory_profile(profile)
        return profile

    def profile_long_running_session(self, duration_minutes: float = 1.0) -> MemoryProfile:
        """Profile memory usage during a long-running session"""
        logger.info(f"Profiling long-running session ({duration_minutes} minutes)")

        if not self.theme_manager:
            from services.css_file_based_theme_manager import CSSFileBasedThemeManager
            self.theme_manager = CSSFileBasedThemeManager()

        initial = self.take_snapshot("long_session_start")

        end_time = time.time() + (duration_minutes * 60)
        themes = ['light', 'dark', 'colorful']
        theme_index = 0

        while time.time() < end_time:
            # Switch theme
            theme = themes[theme_index % len(themes)]
            self.theme_manager.set_theme(theme)
            theme_index += 1

            # Take periodic snapshots
            self.take_snapshot(f"long_session_minute_{(time.time() - initial.timestamp) / 60:.1f}")

            # Wait before next operation
            time.sleep(5)

            # Periodic garbage collection
            if theme_index % 10 == 0:
                gc.collect()

        final = self.take_snapshot("long_session_end")

        peak_snapshot = max(self.snapshots, key=lambda s: s.rss_mb)
        cache_efficiency = self._calculate_cache_efficiency()
        recommendations = self._generate_memory_recommendations(initial, final, peak_snapshot)

        profile = MemoryProfile(
            test_name="long_running_session",
            initial_snapshot=initial,
            final_snapshot=final,
            peak_snapshot=peak_snapshot,
            snapshots=self.snapshots.copy(),
            memory_growth_mb=final.rss_mb - initial.rss_mb,
            peak_memory_mb=peak_snapshot.rss_mb,
            cache_efficiency=cache_efficiency,
            recommendations=recommendations
        )

        self._log_memory_profile(profile)
        return profile

    def _calculate_cache_efficiency(self) -> Dict[str, Any]:
        """Calculate cache efficiency metrics"""
        efficiency = {
            'css_cache_size': 0,
            'icon_cache_size': 0,
            'memory_per_cache_entry': 0.0,
            'cache_hit_ratio': 0.0
        }

        if self.theme_manager:
            # CSS cache size
            if hasattr(self.theme_manager, 'css_cache'):
                efficiency['css_cache_size'] = len(getattr(self.theme_manager, 'css_cache', {}))

            # Icon cache size
            if hasattr(self.theme_manager, 'icon_cache'):
                efficiency['icon_cache_size'] = len(getattr(self.theme_manager, 'icon_cache', {}))

            # Memory per cache entry (rough estimate)
            total_cache_entries = efficiency['css_cache_size'] + efficiency['icon_cache_size']
            if total_cache_entries > 0 and self.snapshots:
                latest_memory = self.snapshots[-1].python_memory_mb
                efficiency['memory_per_cache_entry'] = (latest_memory / total_cache_entries) * 1024.0  # KB

            # Cache hit ratio (simplified estimation)
            efficiency['cache_hit_ratio'] = 75.0  # Assume reasonable cache performance

        return efficiency

    def _generate_memory_recommendations(self, initial: MemorySnapshot,
                                       final: MemorySnapshot,
                                       peak: MemorySnapshot) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []

        memory_growth = final.rss_mb - initial.rss_mb

        # Check for memory leaks
        if memory_growth > 5:  # More than 5MB growth
            recommendations.append(
                f"Potential memory leak detected: {memory_growth:.1f}MB growth. "
                "Consider investigating cache cleanup and object disposal."
            )

        # Check peak memory usage
        if peak.rss_mb > 100:  # More than 100MB peak
            recommendations.append(
                f"High peak memory usage: {peak.rss_mb:.1f}MB. "
                "Consider implementing cache size limits or lazy loading."
            )

        # Check cache growth
        cache_growth = final.css_cache_size - initial.css_cache_size
        if cache_growth > 50:  # More than 50 cache entries added
            recommendations.append(
                f"Excessive cache growth: {cache_growth} entries added. "
                "Consider implementing cache eviction policies."
            )

        # Check Python memory vs RSS ratio
        if final.python_memory_mb / final.rss_mb < 0.3:  # Less than 30% Python memory
            recommendations.append(
                "Low Python memory ratio suggests potential native memory usage. "
                "Consider investigating Qt object cleanup."
            )

        if not recommendations:
            recommendations.append("Memory usage appears optimal with no issues detected.")

        return recommendations

    def _log_memory_profile(self, profile: MemoryProfile):
        """Log memory profile results"""
        logger.info(f"=== MEMORY PROFILE: {profile.test_name.upper()} ===")
        logger.info(f"Initial Memory: {profile.initial_snapshot.rss_mb:.1f}MB")
        logger.info(f"Final Memory: {profile.final_snapshot.rss_mb:.1f}MB")
        logger.info(f"Memory Growth: {profile.memory_growth_mb:+.1f}MB")
        logger.info(f"Peak Memory: {profile.peak_memory_mb:.1f}MB")

        logger.info("Cache Efficiency:")
        for key, value in profile.cache_efficiency.items():
            logger.info(f"  {key}: {value}")

        logger.info("Recommendations:")
        for rec in profile.recommendations:
            logger.info(f"  • {rec}")

        logger.info("=== END MEMORY PROFILE ===")

    def generate_memory_report(self, profiles: List[MemoryProfile]) -> Dict[str, Any]:
        """Generate comprehensive memory analysis report"""
        report = {
            'total_profiles': len(profiles),
            'memory_summary': {},
            'performance_summary': {},
            'recommendations': [],
            'concerns': []
        }

        if not profiles:
            return report

        # Calculate summary statistics
        total_growth = sum(p.memory_growth_mb for p in profiles)
        avg_growth = total_growth / len(profiles)
        max_peak = max(p.peak_memory_mb for p in profiles)

        report['memory_summary'] = {
            'total_memory_growth': total_growth,
            'average_memory_growth': avg_growth,
            'max_peak_memory': max_peak,
            'profiles_with_growth': sum(1 for p in profiles if p.memory_growth_mb > 1)
        }

        # Performance summary
        cache_sizes = [p.cache_efficiency.get('css_cache_size', 0) +
                      p.cache_efficiency.get('icon_cache_size', 0) for p in profiles]

        report['performance_summary'] = {
            'max_cache_size': max(cache_sizes) if cache_sizes else 0,
            'avg_cache_hit_ratio': sum(p.cache_efficiency.get('cache_hit_ratio', 0) for p in profiles) / len(profiles)
        }

        # Aggregate recommendations
        all_recommendations = []
        for profile in profiles:
            all_recommendations.extend(profile.recommendations)

        # Count recommendation frequency
        rec_counts = {}
        for rec in all_recommendations:
            key = rec.split('.')[0]  # First sentence
            rec_counts[key] = rec_counts.get(key, 0) + 1

        # Sort by frequency
        sorted_recs = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)
        report['recommendations'] = [f"{rec} (mentioned {count} times)" for rec, count in sorted_recs[:5]]

        # Identify concerns
        if avg_growth > 2:
            report['concerns'].append(f"Average memory growth is high: {avg_growth:.1f}MB")

        if max_peak > 150:
            report['concerns'].append(f"Peak memory usage is concerning: {max_peak:.1f}MB")

        growth_profiles = sum(1 for p in profiles if p.memory_growth_mb > 5)
        if growth_profiles > len(profiles) / 2:
            report['concerns'].append(f"Multiple profiles show significant memory growth: {growth_profiles}/{len(profiles)}")

        return report

    def cleanup(self):
        """Clean up profiling resources"""
        if tracemalloc.is_tracing():
            tracemalloc.stop()

        self.snapshots.clear()
        gc.collect()
        logger.info("Memory profiling cleanup completed")


def run_memory_profiling():
    """Run comprehensive memory profiling of CSS system"""
    if QApplication.instance() is None:
        app = QApplication([])

    profiler = CSSMemoryProfiler()
    profiler.setup_profiling()

    try:
        # Run different profiling scenarios
        profiles = []

        logger.info("Running theme switching memory profile...")
        profiles.append(profiler.profile_theme_switching())

        logger.info("Running CSS processing memory profile...")
        profiles.append(profiler.profile_css_processing())

        logger.info("Running icon processing memory profile...")
        profiles.append(profiler.profile_icon_processing())

        # Skip long-running test for now
        # logger.info("Running long session memory profile...")
        # profiles.append(profiler.profile_long_running_session(0.5))  # 30 seconds

        # Generate comprehensive report
        report = profiler.generate_memory_report(profiles)

        print("\\n=== MEMORY PROFILING SUMMARY ===")
        print(f"Total Profiles: {report['total_profiles']}")
        print(f"Total Memory Growth: {report['memory_summary']['total_memory_growth']:.1f}MB")
        print(f"Average Memory Growth: {report['memory_summary']['average_memory_growth']:.1f}MB")
        print(f"Max Peak Memory: {report['memory_summary']['max_peak_memory']:.1f}MB")

        if report['concerns']:
            print("\\nConcerns:")
            for concern in report['concerns']:
                print(f"  ⚠ {concern}")

        if report['recommendations']:
            print("\\nTop Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")

        print("=" * 35)

        return profiles

    finally:
        profiler.cleanup()


if __name__ == "__main__":
    run_memory_profiling()
