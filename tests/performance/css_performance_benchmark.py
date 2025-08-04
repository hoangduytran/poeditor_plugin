"""
Performance Testing Framework for CSS Centralization System

This module provides comprehensive performance testing and benchmarking
for the CSS centralization system, measuring theme switching speed,
memory usage, and processing performance.
"""

import time
import gc
import tracemalloc
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer

from lg import logger


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    target: float = None
    passed: bool = None

    def __post_init__(self):
        if self.target is not None:
            self.passed = self.value <= self.target


@dataclass
class BenchmarkResult:
    """Benchmark result containing multiple metrics"""
    test_name: str
    metrics: List[PerformanceMetric]
    timestamp: float
    success: bool

    @property
    def all_passed(self) -> bool:
        """Check if all metrics passed their targets"""
        return all(m.passed for m in self.metrics if m.target is not None)


class CSSPerformanceBenchmark:
    """
    Comprehensive performance benchmarking for CSS system

    Measures:
    - Theme switching speed (target: < 100ms)
    - CSS processing time
    - Memory usage during operations
    - Cache performance
    """

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.theme_manager = None
        self.css_preprocessor = None
        self.icon_preprocessor = None

    def setup_services(self):
        """Initialize CSS services for testing"""
        try:
            from services.css_file_based_theme_manager import CSSFileBasedThemeManager
            from services.css_preprocessor import CSSPreprocessor
            from services.icon_preprocessor import IconPreprocessor

            self.theme_manager = CSSFileBasedThemeManager()
            self.css_preprocessor = CSSPreprocessor()
            self.icon_preprocessor = IconPreprocessor()

            logger.info("CSS services initialized for performance testing")

        except ImportError as e:
            logger.error(f"Failed to import CSS services: {e}")
            raise

    def benchmark_theme_switching(self, iterations: int = 10) -> BenchmarkResult:
        """
        Benchmark theme switching performance
        Target: < 100ms per theme switch
        """
        logger.info(f"Starting theme switching benchmark ({iterations} iterations)")

        themes = ['light', 'dark', 'colorful']
        switch_times = []

        # Create test widget
        test_widget = QWidget()
        test_widget.setObjectName("performance_test_widget")

        try:
            for i in range(iterations):
                theme = themes[i % len(themes)]

                # Measure theme switching time
                start_time = time.perf_counter()
                self.theme_manager.set_theme(theme)
                end_time = time.perf_counter()

                switch_time = (end_time - start_time) * 1000  # Convert to milliseconds
                switch_times.append(switch_time)

                logger.debug(f"Theme switch {i+1}/{iterations} ({theme}): {switch_time:.2f}ms")

                # Small delay to simulate real usage
                QApplication.processEvents()

        except Exception as e:
            logger.error(f"Theme switching benchmark failed: {e}")
            return BenchmarkResult(
                test_name="theme_switching",
                metrics=[],
                timestamp=time.time(),
                success=False
            )

        # Calculate metrics
        avg_time = sum(switch_times) / len(switch_times)
        max_time = max(switch_times)
        min_time = min(switch_times)

        metrics = [
            PerformanceMetric("avg_switch_time", avg_time, "ms", target=100.0),
            PerformanceMetric("max_switch_time", max_time, "ms", target=150.0),
            PerformanceMetric("min_switch_time", min_time, "ms"),
        ]

        result = BenchmarkResult(
            test_name="theme_switching",
            metrics=metrics,
            timestamp=time.time(),
            success=True
        )

        self.results.append(result)
        logger.info(f"Theme switching benchmark complete - Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")

        return result

    def benchmark_css_processing(self) -> BenchmarkResult:
        """
        Benchmark CSS processing performance
        Measures variable resolution and preprocessing speed
        """
        logger.info("Starting CSS processing benchmark")

        processing_times = []
        memory_usage = []

        try:
            # Test with different CSS content sizes
            test_cases = [
                ("small", "QWidget { color: var(--color-text); }"),
                ("medium", self._generate_medium_css()),
                ("large", self._generate_large_css()),
            ]

            for case_name, css_content in test_cases:
                # Start memory tracking
                tracemalloc.start()

                # Measure processing time
                start_time = time.perf_counter()
                processed_css = self.css_preprocessor.process_css(css_content, {
                    'color-text': '#333333',
                    'color-bg': '#ffffff',
                    'spacing-md': '16px'
                })
                end_time = time.perf_counter()

                processing_time = (end_time - start_time) * 1000  # Convert to ms
                processing_times.append(processing_time)

                # Measure memory usage
                current, peak = tracemalloc.get_traced_memory()
                memory_usage.append(peak / 1024 / 1024)  # Convert to MB
                tracemalloc.stop()

                logger.debug(f"CSS processing ({case_name}): {processing_time:.2f}ms, Memory: {peak/1024/1024:.2f}MB")

        except Exception as e:
            logger.error(f"CSS processing benchmark failed: {e}")
            return BenchmarkResult(
                test_name="css_processing",
                metrics=[],
                timestamp=time.time(),
                success=False
            )

        # Calculate metrics
        avg_processing_time = sum(processing_times) / len(processing_times)
        max_memory = max(memory_usage)

        metrics = [
            PerformanceMetric("avg_processing_time", avg_processing_time, "ms", target=50.0),
            PerformanceMetric("max_memory_usage", max_memory, "MB", target=10.0),
        ]

        result = BenchmarkResult(
            test_name="css_processing",
            metrics=metrics,
            timestamp=time.time(),
            success=True
        )

        self.results.append(result)
        logger.info(f"CSS processing benchmark complete - Avg: {avg_processing_time:.2f}ms, Memory: {max_memory:.2f}MB")

        return result

    def benchmark_icon_processing(self) -> BenchmarkResult:
        """
        Benchmark icon processing performance
        Measures SVG processing and CSS generation speed
        """
        logger.info("Starting icon processing benchmark")

        try:
            # Measure icon CSS generation time
            start_time = time.perf_counter()
            icon_css = self.icon_preprocessor.generate_icon_css(generate_variables=True)
            end_time = time.perf_counter()

            processing_time = (end_time - start_time) * 1000  # Convert to ms
            css_size = len(icon_css) / 1024  # Convert to KB

            metrics = [
                PerformanceMetric("icon_processing_time", processing_time, "ms", target=100.0),
                PerformanceMetric("generated_css_size", css_size, "KB"),
            ]

            result = BenchmarkResult(
                test_name="icon_processing",
                metrics=metrics,
                timestamp=time.time(),
                success=True
            )

            self.results.append(result)
            logger.info(f"Icon processing benchmark complete - Time: {processing_time:.2f}ms, CSS Size: {css_size:.2f}KB")

            return result

        except Exception as e:
            logger.error(f"Icon processing benchmark failed: {e}")
            return BenchmarkResult(
                test_name="icon_processing",
                metrics=[],
                timestamp=time.time(),
                success=False
            )

    def benchmark_cache_performance(self) -> BenchmarkResult:
        """
        Benchmark cache performance
        Measures cache hit/miss ratios and lookup speed
        """
        logger.info("Starting cache performance benchmark")

        try:
            # Clear cache and measure cold start
            self.css_preprocessor.clear_cache()

            # Cold cache test
            start_time = time.perf_counter()
            css1 = self.css_preprocessor.process_css("QWidget { color: var(--color-text); }", {'color-text': '#333'})
            cold_time = time.perf_counter() - start_time

            # Warm cache test
            start_time = time.perf_counter()
            css2 = self.css_preprocessor.process_css("QWidget { color: var(--color-text); }", {'color-text': '#333'})
            warm_time = time.perf_counter() - start_time

            cache_speedup = cold_time / warm_time if warm_time > 0 else 0

            metrics = [
                PerformanceMetric("cold_cache_time", cold_time * 1000, "ms"),
                PerformanceMetric("warm_cache_time", warm_time * 1000, "ms"),
                PerformanceMetric("cache_speedup", cache_speedup, "x", target=2.0),
            ]

            result = BenchmarkResult(
                test_name="cache_performance",
                metrics=metrics,
                timestamp=time.time(),
                success=True
            )

            self.results.append(result)
            logger.info(f"Cache performance benchmark complete - Speedup: {cache_speedup:.2f}x")

            return result

        except Exception as e:
            logger.error(f"Cache performance benchmark failed: {e}")
            return BenchmarkResult(
                test_name="cache_performance",
                metrics=[],
                timestamp=time.time(),
                success=False
            )

    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all performance benchmarks"""
        logger.info("Starting comprehensive performance benchmark suite")

        self.setup_services()

        benchmarks = [
            self.benchmark_theme_switching,
            self.benchmark_css_processing,
            self.benchmark_icon_processing,
            self.benchmark_cache_performance,
        ]

        results = []
        for benchmark in benchmarks:
            try:
                result = benchmark()
                results.append(result)
            except Exception as e:
                logger.error(f"Benchmark {benchmark.__name__} failed: {e}")

        self._generate_report()
        return results

    def _generate_medium_css(self) -> str:
        """Generate medium-sized CSS for testing"""
        return """
        QWidget {
            color: var(--color-text);
            background-color: var(--color-bg);
            padding: var(--spacing-md);
        }
        QPushButton {
            background-color: var(--color-button-bg);
            color: var(--color-button-text);
            border: 1px solid var(--color-border);
        }
        """

    def _generate_large_css(self) -> str:
        """Generate large CSS for testing"""
        css_parts = []
        for i in range(50):
            css_parts.append(f"""
            .component-{i} {{
                color: var(--color-text-{i % 5});
                background: var(--color-bg-{i % 3});
                margin: var(--spacing-{i % 4});
            }}
            """)
        return "\n".join(css_parts)

    def _generate_report(self):
        """Generate performance report"""
        logger.info("=== CSS PERFORMANCE BENCHMARK REPORT ===")

        for result in self.results:
            logger.info(f"\n{result.test_name.upper()} BENCHMARK:")
            logger.info(f"Status: {'PASSED' if result.all_passed else 'FAILED'}")

            for metric in result.metrics:
                status = ""
                if metric.target is not None:
                    status = f" ({'PASS' if metric.passed else 'FAIL'})"
                logger.info(f"  {metric.name}: {metric.value:.2f} {metric.unit}{status}")

        logger.info("=== END PERFORMANCE REPORT ===")


def run_performance_tests():
    """Run performance tests as standalone script"""
    if QApplication.instance() is None:
        app = QApplication([])

    benchmark = CSSPerformanceBenchmark()
    results = benchmark.run_all_benchmarks()

    return results


if __name__ == "__main__":
    run_performance_tests()
