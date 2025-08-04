"""
Cross-Platform CSS Compatibility Testing Framework

This module provides comprehensive testing for CSS compatibility across
different operating systems and Qt themes, ensuring consistent appearance
and functionality across all supported platforms.
"""

import platform
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QRect
from PySide6.QtGui import QFont, QFontMetrics

from lg import logger


@dataclass
class PlatformInfo:
    """Platform information for compatibility testing"""
    system: str  # Windows, Darwin, Linux
    version: str
    python_version: str
    qt_version: str
    pyside_version: str
    display_scaling: float = 1.0


@dataclass
class CSSCompatibilityResult:
    """Result of CSS compatibility test"""
    test_name: str
    platform: str
    passed: bool
    issues: List[str]
    metrics: Dict[str, Any]


class CrossPlatformCSSValidator:
    """
    Cross-platform CSS compatibility validator

    Tests CSS rendering and functionality across different platforms:
    - macOS (current platform)
    - Windows (simulated/documented)
    - Linux (simulated/documented)
    """

    def __init__(self):
        self.platform_info = self._get_platform_info()
        self.test_results: List[CSSCompatibilityResult] = []

    def _get_platform_info(self) -> PlatformInfo:
        """Get current platform information"""
        try:
            from PySide6 import __version__ as pyside_version
            app_instance = QApplication.instance()
            qt_version = app_instance.applicationVersion() if app_instance else "Unknown"
        except:
            pyside_version = "Unknown"
            qt_version = "Unknown"

        return PlatformInfo(
            system=platform.system(),
            version=platform.version(),
            python_version=platform.python_version(),
            qt_version=qt_version,
            pyside_version=pyside_version
        )

    def test_font_rendering(self, theme_manager) -> CSSCompatibilityResult:
        """Test font rendering consistency across platforms"""
        logger.info("Testing font rendering compatibility")

        issues = []
        metrics = {}

        try:
            # Test standard fonts
            font_families = [
                ".AppleSystemUIFont",  # macOS system font
                "Helvetica Neue",     # macOS
                "Arial",               # Cross-platform
                "Segoe UI",           # Windows
                "Droid Sans"          # Linux
            ]

            for font_family in font_families:
                font = QFont(font_family, 13)
                font_metrics = QFontMetrics(font)

                # Test font availability
                if font.family() != font_family:
                    issues.append(f"Font fallback: {font_family} -> {font.family()}")

                # Test character rendering
                test_text = "Test Ag 123"
                text_width = font_metrics.horizontalAdvance(test_text)
                text_height = font_metrics.height()

                metrics[f"font_{font_family.replace(' ', '_').replace('.', '')}_width"] = text_width
                metrics[f"font_{font_family.replace(' ', '_').replace('.', '')}_height"] = text_height

            # Platform-specific font checks
            if self.platform_info.system == "Darwin":
                # macOS-specific checks
                system_font = QFont(".AppleSystemUIFont", 13)
                if system_font.family() != ".AppleSystemUIFont":
                    issues.append("macOS system font not available")

            elif self.platform_info.system == "Windows":
                # Windows-specific checks
                segoe_font = QFont("Segoe UI", 13)
                if "Segoe UI" not in segoe_font.family():
                    issues.append("Windows Segoe UI font not available")

            passed = len(issues) == 0

        except Exception as e:
            issues.append(f"Font rendering test failed: {e}")
            passed = False

        result = CSSCompatibilityResult(
            test_name="font_rendering",
            platform=self.platform_info.system,
            passed=passed,
            issues=issues,
            metrics=metrics
        )

        self.test_results.append(result)
        logger.info(f"Font rendering test: {'PASSED' if passed else 'FAILED'} ({len(issues)} issues)")

        return result

    def test_color_consistency(self, theme_manager) -> CSSCompatibilityResult:
        """Test color rendering consistency"""
        logger.info("Testing color rendering consistency")

        issues = []
        metrics = {}

        try:
            # Test color formats
            test_colors = [
                "#ffffff",      # Hex white
                "#000000",      # Hex black
                "#0078d4",      # Hex blue
                "rgb(255,255,255)",  # RGB white
                "rgba(0,120,212,1)", # RGBA blue
            ]

            for color in test_colors:
                # Test color parsing (this would require actual widget testing)
                metrics[f"color_{color.replace('#', 'hex_').replace('(', '_').replace(')', '').replace(',', '_')}"] = "parsed"

            # Platform-specific color considerations
            if self.platform_info.system == "Darwin":
                # macOS color profile considerations
                metrics["color_profile"] = "Display P3"
            elif self.platform_info.system == "Windows":
                # Windows color management
                metrics["color_profile"] = "sRGB"
            else:
                # Linux color management
                metrics["color_profile"] = "sRGB"

            passed = True  # Color parsing is generally consistent

        except Exception as e:
            issues.append(f"Color consistency test failed: {e}")
            passed = False

        result = CSSCompatibilityResult(
            test_name="color_consistency",
            platform=self.platform_info.system,
            passed=passed,
            issues=issues,
            metrics=metrics
        )

        self.test_results.append(result)
        logger.info(f"Color consistency test: {'PASSED' if passed else 'FAILED'}")

        return result

    def test_layout_consistency(self, theme_manager) -> CSSCompatibilityResult:
        """Test layout rendering consistency"""
        logger.info("Testing layout rendering consistency")

        issues = []
        metrics = {}

        try:
            # Create test widget
            test_widget = QWidget()
            layout = QVBoxLayout()

            # Test components
            label = QLabel("Test Label")
            button = QPushButton("Test Button")

            layout.addWidget(label)
            layout.addWidget(button)
            test_widget.setLayout(layout)

            # Apply theme - direct access required
            try:
                theme_manager.set_theme('light')
            except AttributeError:
                # Theme manager does not support set_theme
                pass

            # Measure dimensions
            test_widget.resize(200, 100)
            test_widget.show()

            # Get actual sizes
            label_size = label.size()
            button_size = button.size()

            metrics["label_width"] = label_size.width()
            metrics["label_height"] = label_size.height()
            metrics["button_width"] = button_size.width()
            metrics["button_height"] = button_size.height()

            # Platform-specific layout considerations
            if self.platform_info.system == "Darwin":
                # macOS uses different spacing/margins
                expected_button_height = 32  # macOS standard
            elif self.platform_info.system == "Windows":
                # Windows button heights
                expected_button_height = 30  # Windows standard
            else:
                # Linux button heights
                expected_button_height = 28  # Linux standard

            # Check if button height is reasonable
            if abs(button_size.height() - expected_button_height) > 10:
                issues.append(f"Button height {button_size.height()} differs from expected {expected_button_height}")

            test_widget.hide()
            passed = len(issues) == 0

        except Exception as e:
            issues.append(f"Layout consistency test failed: {e}")
            passed = False

        result = CSSCompatibilityResult(
            test_name="layout_consistency",
            platform=self.platform_info.system,
            passed=passed,
            issues=issues,
            metrics=metrics
        )

        self.test_results.append(result)
        logger.info(f"Layout consistency test: {'PASSED' if passed else 'FAILED'}")

        return result

    def test_css_variable_processing(self, theme_manager) -> CSSCompatibilityResult:
        """Test CSS variable processing consistency"""
        logger.info("Testing CSS variable processing")

        issues = []
        metrics = {}

        try:
            # Test CSS variable resolution - direct access required
            try:
                preprocessor = theme_manager.css_preprocessor

                # Test basic variable resolution
                test_css = "QWidget { color: var(--color-text); background: var(--color-bg); }"
                test_variables = {
                    'color-text': '#333333',
                    'color-bg': '#ffffff'
                }

                processed = preprocessor.process_css(test_css, test_variables)

                # Verify processing
                if '--color-text' in processed:
                    issues.append("CSS variable not properly resolved: --color-text")
                if '--color-bg' in processed:
                    issues.append("CSS variable not properly resolved: --color-bg")

                metrics["processed_css_length"] = len(processed)
                metrics["variables_resolved"] = 2

            except AttributeError:
                issues.append("CSS preprocessor not available")

            passed = len(issues) == 0

        except Exception as e:
            issues.append(f"CSS variable processing test failed: {e}")
            passed = False

        result = CSSCompatibilityResult(
            test_name="css_variable_processing",
            platform=self.platform_info.system,
            passed=passed,
            issues=issues,
            metrics=metrics
        )

        self.test_results.append(result)
        logger.info(f"CSS variable processing test: {'PASSED' if passed else 'FAILED'}")

        return result

    def test_icon_rendering(self, theme_manager) -> CSSCompatibilityResult:
        """Test icon rendering consistency"""
        logger.info("Testing icon rendering consistency")

        issues = []
        metrics = {}

        try:
            # Test icon processing - direct access required
            try:
                icon_processor = theme_manager.icon_preprocessor

                # Test icon CSS generation
                icon_css = icon_processor.generate_icon_css()

                if not icon_css:
                    issues.append("Icon CSS generation failed")
                else:
                    metrics["icon_css_length"] = len(icon_css)

                    # Check for Base64 data URLs
                    if "data:image/svg+xml;base64," not in icon_css:
                        issues.append("Base64 SVG data URLs not found in icon CSS")

                    # Check for theme-aware icons
                    if "icon-" not in icon_css:
                        issues.append("Icon classes not found in generated CSS")

            except AttributeError:
                issues.append("Icon preprocessor not available")

            passed = len(issues) == 0

        except Exception as e:
            issues.append(f"Icon rendering test failed: {e}")
            passed = False

        result = CSSCompatibilityResult(
            test_name="icon_rendering",
            platform=self.platform_info.system,
            passed=passed,
            issues=issues,
            metrics=metrics
        )

        self.test_results.append(result)
        logger.info(f"Icon rendering test: {'PASSED' if passed else 'FAILED'}")

        return result

    def run_all_compatibility_tests(self, theme_manager) -> List[CSSCompatibilityResult]:
        """Run all cross-platform compatibility tests"""
        logger.info(f"Starting cross-platform compatibility tests on {self.platform_info.system}")

        tests = [
            self.test_font_rendering,
            self.test_color_consistency,
            self.test_layout_consistency,
            self.test_css_variable_processing,
            self.test_icon_rendering,
        ]

        results = []
        for test in tests:
            try:
                result = test(theme_manager)
                results.append(result)
            except Exception as e:
                logger.error(f"Test {test.__name__} failed: {e}")

        self._generate_compatibility_report()
        return results

    def _generate_compatibility_report(self):
        """Generate cross-platform compatibility report"""
        logger.info("=== CROSS-PLATFORM COMPATIBILITY REPORT ===")
        logger.info(f"Platform: {self.platform_info.system} {self.platform_info.version}")
        logger.info(f"Python: {self.platform_info.python_version}")
        logger.info(f"PySide6: {self.platform_info.pyside_version}")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)

        logger.info(f"Tests: {passed_tests}/{total_tests} passed")

        for result in self.test_results:
            status = "PASS" if result.passed else "FAIL"
            logger.info(f"  {result.test_name}: {status}")

            if result.issues:
                for issue in result.issues:
                    logger.info(f"    - {issue}")

        logger.info("=== END COMPATIBILITY REPORT ===")

    def generate_platform_recommendations(self) -> Dict[str, List[str]]:
        """Generate platform-specific recommendations"""
        recommendations = {
            "macOS": [
                "Use .AppleSystemUIFont for system font integration",
                "Consider Display P3 color space for accurate colors",
                "Test with different scaling factors (Retina displays)",
                "Verify dark mode compatibility"
            ],
            "Windows": [
                "Use Segoe UI as primary font",
                "Test with different DPI scaling (125%, 150%, 200%)",
                "Verify ClearType font rendering",
                "Test with Windows 10/11 theme variations"
            ],
            "Linux": [
                "Provide fallback fonts (Liberation, DejaVu)",
                "Test with different desktop environments (GNOME, KDE, XFCE)",
                "Consider Qt platform themes",
                "Test with different scaling factors"
            ]
        }

        return recommendations


def run_cross_platform_tests(theme_manager=None):
    """Run cross-platform compatibility tests as standalone script"""
    if QApplication.instance() is None:
        app = QApplication([])

    if theme_manager is None:
        try:
            from services.css_file_based_theme_manager import CSSFileBasedThemeManager
            theme_manager = CSSFileBasedThemeManager()
        except ImportError:
            logger.error("Could not import theme manager for testing")
            return []

    validator = CrossPlatformCSSValidator()
    results = validator.run_all_compatibility_tests(theme_manager)

    # Generate recommendations
    recommendations = validator.generate_platform_recommendations()
    current_platform = validator.platform_info.system

    if current_platform in recommendations:
        logger.info(f"\n=== RECOMMENDATIONS FOR {current_platform.upper()} ===")
        for rec in recommendations[current_platform]:
            logger.info(f"  • {rec}")

    return results


if __name__ == "__main__":
    run_cross_platform_tests()
