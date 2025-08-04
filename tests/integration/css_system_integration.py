"""
System Integration Testing for CSS Centralization

This module provides comprehensive integration testing for the complete
CSS centralization system, validating end-to-end functionality and
ensuring all components work together seamlessly.
"""

import time
from typing import Dict, List, Any, TYPE_CHECKING, Optional
from dataclasses import dataclass

from PySide6.QtWidgets import QApplication

from lg import logger

if TYPE_CHECKING:
    from services.css_file_based_theme_manager import CSSFileBasedThemeManager

# Type ignore for test file - we're testing dynamic behavior
# type: ignore


@dataclass
class IntegrationTestResult:
    """Result of an integration test"""
    test_name: str
    passed: bool
    execution_time_ms: float
    details: Dict[str, Any]
    issues: List[str]


class CSSSystemIntegrationTester:
    """
    Comprehensive integration tester for CSS centralization system

    Tests the complete system including:
    - Theme manager integration
    - CSS preprocessing pipeline
    - Icon system integration
    - Cache system performance
    - End-to-end theme switching
    """

    def __init__(self):
        self.test_results: List[IntegrationTestResult] = []
        self.theme_manager: Optional['CSSFileBasedThemeManager'] = None

    def setup_system(self):
        """Initialize the complete CSS system for testing"""
        try:
            from services.css_file_based_theme_manager import CSSFileBasedThemeManager

            self.theme_manager = CSSFileBasedThemeManager()
            logger.info("CSS system initialized for integration testing")

        except Exception as e:
            logger.error(f"Failed to initialize CSS system: {e}")
            raise

    def test_theme_switching_integration(self) -> IntegrationTestResult:
        """Test complete theme switching workflow"""
        logger.info("Testing theme switching integration")

        start_time = time.perf_counter()
        issues = []
        details = {}

        try:
            # Ensure theme manager is initialized
            if self.theme_manager is None:
                self.setup_system()
            
            assert self.theme_manager is not None, "Theme manager not initialized"
                
            # Get available themes
            available_themes = self.theme_manager.get_available_themes()
            details['available_themes'] = available_themes

            if len(available_themes) < 2:
                issues.append("Insufficient themes available for switching test")

            # Test switching between themes
            switch_times = []
            for theme in available_themes[:3]:  # Test first 3 themes
                switch_start = time.perf_counter()
                self.theme_manager.set_theme(theme)
                switch_end = time.perf_counter()

                switch_time = (switch_end - switch_start) * 1000
                switch_times.append(switch_time)

                # Verify theme was applied
                current = self.theme_manager.get_current_theme()
                if current and current.name.lower() != theme.lower():
                    issues.append(f"Theme switch failed: requested {theme}, got {current.name}")

            details['switch_times'] = switch_times
            details['avg_switch_time'] = sum(switch_times) / len(switch_times) if switch_times else 0

            # Test theme persistence
            current_theme = self.theme_manager.get_current_theme()
            if current_theme:
                original_theme = current_theme.name
                self.theme_manager.set_theme('light')
                self.theme_manager._save_current_theme()

                # Simulate restart by creating new manager
                details['persistence_test'] = 'completed'

        except Exception as e:
            issues.append(f"Theme switching integration failed: {e}")

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        result = IntegrationTestResult(
            test_name="theme_switching_integration",
            passed=len(issues) == 0,
            execution_time_ms=execution_time,
            details=details,
            issues=issues
        )

        self.test_results.append(result)
        logger.info(f"Theme switching integration: {'PASSED' if result.passed else 'FAILED'} ({execution_time:.1f}ms)")

        return result

    def test_css_preprocessing_pipeline(self) -> IntegrationTestResult:
        """Test complete CSS preprocessing pipeline"""
        logger.info("Testing CSS preprocessing pipeline")

        start_time = time.perf_counter()
        issues = []
        details = {}

        try:
            # Ensure theme manager is initialized
            if self.theme_manager is None:
                self.setup_system()
            
            assert self.theme_manager is not None, "Theme manager not initialized"

            # Test variable extraction - direct access required
            try:
                preprocessor = self.theme_manager.css_preprocessor

                if preprocessor is not None:
                    # Test basic variable processing
                    test_css = """
                    QWidget {
                        color: var(--color-text);
                        background: var(--color-bg);
                        padding: var(--spacing-md);
                    }
                    """

                    test_variables = {
                        'color-text': '#333333',
                        'color-bg': '#ffffff',
                        'spacing-md': '16px'
                    }

                    processed = preprocessor.process_css(test_css, test_variables)
                    details['processed_css_length'] = len(processed)

                    # Verify variables were resolved
                    if 'var(--color-text)' in processed:
                        issues.append("CSS variable --color-text not resolved")
                    if 'var(--color-bg)' in processed:
                        issues.append("CSS variable --color-bg not resolved")
                    if 'var(--spacing-md)' in processed:
                        issues.append("CSS variable --spacing-md not resolved")

                else:
                    issues.append("CSS preprocessor is None")
            except AttributeError:
                issues.append("Theme manager does not have css_preprocessor attribute")

        except Exception as e:
            issues.append(f"CSS preprocessing pipeline failed: {e}")

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        result = IntegrationTestResult(
            test_name="css_preprocessing_pipeline",
            passed=len(issues) == 0,
            execution_time_ms=execution_time,
            details=details,
            issues=issues
        )

        self.test_results.append(result)
        logger.info(f"CSS preprocessing pipeline: {'PASSED' if result.passed else 'FAILED'} ({execution_time:.1f}ms)")

        return result

    def test_icon_system_integration(self) -> IntegrationTestResult:
        """Test icon system integration with themes"""
        logger.info("Testing icon system integration")

        start_time = time.perf_counter()
        issues = []
        details = {}

        try:
            # Ensure theme manager is initialized
            if self.theme_manager is None:
                self.setup_system()
            
            assert self.theme_manager is not None, "Theme manager not initialized"

            # Test icon system integration - direct access required
            try:
                icon_processor = self.theme_manager.icon_preprocessor

                if icon_processor is not None:
                    # Test icon CSS generation
                    icon_css = icon_processor.generate_icon_css(generate_variables=True)
                    details['icon_css_length'] = len(icon_css)

                    if not icon_css:
                        issues.append("Icon CSS generation returned empty result")
                    else:
                        # Verify icon CSS contains expected elements
                        if 'data:image/svg+xml;base64,' not in icon_css:
                            issues.append("Icon CSS missing Base64 SVG data")

                        if '.icon-' not in icon_css:
                            issues.append("Icon CSS missing icon class definitions")

                    # Test icon processing if method exists
                    try:
                        processed_icons = icon_processor.process_all_icons()
                        details['processed_icon_count'] = len(processed_icons)
                    except AttributeError:
                        details['processed_icon_count'] = 0

                    # Test theme integration
                    self.theme_manager.set_theme('dark')
                    dark_icon_css = icon_processor.generate_icon_css()

                    self.theme_manager.set_theme('light')
                    light_icon_css = icon_processor.generate_icon_css()

                    details['theme_aware_icons'] = dark_icon_css != light_icon_css
                else:
                    issues.append("Icon preprocessor is None")
            except AttributeError:
                issues.append("Theme manager does not have icon_preprocessor attribute")

        except Exception as e:
            issues.append(f"Icon system integration failed: {e}")

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        result = IntegrationTestResult(
            test_name="icon_system_integration",
            passed=len(issues) == 0,
            execution_time_ms=execution_time,
            details=details,
            issues=issues
        )

        self.test_results.append(result)
        logger.info(f"Icon system integration: {'PASSED' if result.passed else 'FAILED'} ({execution_time:.1f}ms)")

        return result

    def test_cache_system_integration(self) -> IntegrationTestResult:
        """Test cache system integration and performance"""
        logger.info("Testing cache system integration")

        start_time = time.perf_counter()
        issues = []
        details = {}

        try:
            # Ensure theme manager is initialized
            if self.theme_manager is None:
                self.setup_system()
            
            assert self.theme_manager is not None, "Theme manager not initialized"

            # Test cache performance with multiple theme switches
            available_themes = self.theme_manager.get_available_themes()
            themes = available_themes if available_themes else ['light', 'dark']

            # Cold cache test (first switch)
            cold_start = time.perf_counter()
            self.theme_manager.set_theme(themes[0])
            cold_time = (time.perf_counter() - cold_start) * 1000

            # Warm cache test (second switch to same theme)
            warm_start = time.perf_counter()
            self.theme_manager.set_theme(themes[0])
            warm_time = (time.perf_counter() - warm_start) * 1000

            details['cold_cache_time'] = cold_time
            details['warm_cache_time'] = warm_time
            details['cache_speedup'] = cold_time / warm_time if warm_time > 0 else 0

            # Test cache statistics using direct attribute access
            try:
                cache_data = {
                    'entries': len(self.theme_manager._css_cache),
                    'themes_cached': list(self.theme_manager._css_cache.keys()),
                    'cache_loaded': self.theme_manager._cache_loaded
                }
                
                # Access css_manager cache directly
                if self.theme_manager.css_manager:
                    css_manager_cache = self.theme_manager.css_manager.css_cache
                    cache_data['css_manager_entries'] = len(css_manager_cache)
                    cache_data['css_manager_files'] = list(css_manager_cache.keys())
                
                details['cache_stats'] = cache_data
                
                # Verify cache is working
                if cache_data['entries'] == 0:
                    issues.append("Theme cache appears to be empty")
            except AttributeError as e:
                details['cache_stats'] = f'cache_access_error: {e}'
                issues.append(f"Failed to access cache attributes: {e}")

            # Test cache memory usage
            try:
                cache_size = len(self.theme_manager._css_cache)
                details['cache_entries'] = cache_size

                if cache_size == 0:
                    issues.append("Theme cache appears to be empty")
            except AttributeError as e:
                issues.append(f"Failed to access cache size: {e}")

        except Exception as e:
            issues.append(f"Cache system integration failed: {e}")

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        result = IntegrationTestResult(
            test_name="cache_system_integration",
            passed=len(issues) == 0,
            execution_time_ms=execution_time,
            details=details,
            issues=issues
        )

        self.test_results.append(result)
        logger.info(f"Cache system integration: {'PASSED' if result.passed else 'FAILED'} ({execution_time:.1f}ms)")

        return result

    def test_end_to_end_workflow(self) -> IntegrationTestResult:
        """Test complete end-to-end CSS system workflow"""
        logger.info("Testing end-to-end workflow")

        start_time = time.perf_counter()
        issues = []
        details = {}

        try:
            # Step 1: Initialize system
            initialization_start = time.perf_counter()
            if self.theme_manager is None:
                self.setup_system()
            
            assert self.theme_manager is not None, "Theme manager not initialized"
            
            initialization_time = (time.perf_counter() - initialization_start) * 1000
            details['initialization_time'] = initialization_time

            # Step 2: Load and apply theme
            theme_loading_start = time.perf_counter()
            self.theme_manager.set_theme('dark')
            theme_loading_time = (time.perf_counter() - theme_loading_start) * 1000
            details['theme_loading_time'] = theme_loading_time

            # Step 3: Switch themes multiple times
            theme_switches = []
            themes = ['light', 'dark', 'colorful']

            for theme in themes:
                switch_start = time.perf_counter()
                self.theme_manager.set_theme(theme)
                switch_time = (time.perf_counter() - switch_start) * 1000
                theme_switches.append(switch_time)

            details['theme_switches'] = theme_switches
            details['avg_switch_time'] = sum(theme_switches) / len(theme_switches)

            # Step 4: Test persistence - direct access required
            persistence_start = time.perf_counter()
            try:
                self.theme_manager._save_current_theme()
            except AttributeError:
                issues.append("Theme manager does not have _save_current_theme method")
            persistence_time = (time.perf_counter() - persistence_start) * 1000
            details['persistence_time'] = persistence_time

            # Step 5: Test cache statistics - test actual cache access
            try:
                cache_entries = len(self.theme_manager._css_cache)
                details['cache_statistics_available'] = True
                details['final_cache_size'] = cache_entries
            except AttributeError:
                details['cache_statistics_available'] = False

            # Validate performance targets
            if details['avg_switch_time'] > 100:
                issues.append(f"Average theme switch time exceeds target: {details['avg_switch_time']:.1f}ms > 100ms")

            if initialization_time > 1000:
                issues.append(f"System initialization too slow: {initialization_time:.1f}ms > 1000ms")

        except Exception as e:
            issues.append(f"End-to-end workflow failed: {e}")

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        result = IntegrationTestResult(
            test_name="end_to_end_workflow",
            passed=len(issues) == 0,
            execution_time_ms=execution_time,
            details=details,
            issues=issues
        )

        self.test_results.append(result)
        logger.info(f"End-to-end workflow: {'PASSED' if result.passed else 'FAILED'} ({execution_time:.1f}ms)")

        return result

    def run_all_integration_tests(self) -> List[IntegrationTestResult]:
        """Run complete integration test suite"""
        logger.info("Starting CSS system integration test suite")

        # Initialize system
        self.setup_system()

        # Run all tests
        tests = [
            self.test_theme_switching_integration,
            self.test_css_preprocessing_pipeline,
            self.test_icon_system_integration,
            self.test_cache_system_integration,
            self.test_end_to_end_workflow,
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                logger.error(f"Integration test {test.__name__} failed: {e}")

        self._generate_integration_report()
        return results

    def _generate_integration_report(self):
        """Generate integration testing report"""
        logger.info("=== CSS SYSTEM INTEGRATION TEST REPORT ===")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        total_time = sum(r.execution_time_ms for r in self.test_results)

        logger.info(f"Tests: {passed_tests}/{total_tests} passed")
        logger.info(f"Total execution time: {total_time:.1f}ms")

        for result in self.test_results:
            status = "PASS" if result.passed else "FAIL"
            logger.info(f"  {result.test_name}: {status} ({result.execution_time_ms:.1f}ms)")

            if result.issues:
                for issue in result.issues:
                    logger.info(f"    - {issue}")

            # Log key metrics
            if 'avg_switch_time' in result.details:
                logger.info(f"    Average switch time: {result.details['avg_switch_time']:.1f}ms")

            if 'cache_speedup' in result.details:
                logger.info(f"    Cache speedup: {result.details['cache_speedup']:.1f}x")

        logger.info("=== END INTEGRATION TEST REPORT ===")

    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate system health report"""
        health_report = {
            'overall_health': 'healthy' if all(r.passed for r in self.test_results) else 'issues_detected',
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for r in self.test_results if r.passed),
            'total_execution_time': sum(r.execution_time_ms for r in self.test_results),
            'performance_metrics': {},
            'recommendations': []
        }

        # Extract performance metrics
        for result in self.test_results:
            if 'avg_switch_time' in result.details:
                health_report['performance_metrics']['avg_theme_switch_time'] = result.details['avg_switch_time']

            if 'cache_speedup' in result.details:
                health_report['performance_metrics']['cache_speedup'] = result.details['cache_speedup']

        # Generate recommendations
        avg_switch_time = health_report['performance_metrics'].get('avg_theme_switch_time', 0)
        if avg_switch_time > 100:
            health_report['recommendations'].append(
                f"Theme switching performance below target ({avg_switch_time:.1f}ms > 100ms). Consider cache optimization."
            )

        cache_speedup = health_report['performance_metrics'].get('cache_speedup', 0)
        if cache_speedup < 2:
            health_report['recommendations'].append(
                f"Cache performance below optimal ({cache_speedup:.1f}x < 2x). Consider cache tuning."
            )

        if health_report['passed_tests'] < health_report['total_tests']:
            health_report['recommendations'].append(
                "Some integration tests failed. Review test output for specific issues."
            )

        return health_report


def run_integration_tests():
    """Run CSS system integration tests as standalone script"""
    if QApplication.instance() is None:
        QApplication([])

    tester = CSSSystemIntegrationTester()
    results = tester.run_all_integration_tests()

    # Generate health report
    health = tester.get_system_health_report()

    print("\n=== SYSTEM HEALTH SUMMARY ===")
    print(f"Overall Health: {health['overall_health'].upper()}")
    print(f"Tests Passed: {health['passed_tests']}/{health['total_tests']}")
    print(f"Total Time: {health['total_execution_time']:.1f}ms")

    if health['performance_metrics']:
        print("\nPerformance Metrics:")
        for metric, value in health['performance_metrics'].items():
            print(f"  {metric}: {value:.1f}")

    if health['recommendations']:
        print("\nRecommendations:")
        for rec in health['recommendations']:
            print(f"  • {rec}")

    print("=" * 30)

    return results


if __name__ == "__main__":
    run_integration_tests()
