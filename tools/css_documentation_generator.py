"""
CSS System API Documentation Generator

This module generates comprehensive API documentation for the CSS centralization
system, including developer guides, examples, and best practices.
"""

import inspect
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from lg import logger


@dataclass
class APIMethodDoc:
    """Documentation for a single API method"""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, str]]
    return_type: str
    examples: List[str]


@dataclass
class APIClassDoc:
    """Documentation for a complete API class"""
    name: str
    description: str
    methods: List[APIMethodDoc]
    examples: List[str]
    usage_patterns: List[str]


class CSSAPIDocumentationGenerator:
    """
    Comprehensive API documentation generator for CSS system

    Generates:
    - API reference documentation
    - Developer guides with examples
    - Best practices documentation
    - Performance optimization guides
    """

    def __init__(self, output_dir: str = "docs/css_api"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.classes_to_document = [
            'CSSPreprocessor',
            'CSSFileBasedThemeManager',
            'IconPreprocessor',
            'AdvancedCSSCache'
        ]

        logger.info(f"API documentation generator initialized - Output: {output_dir}")

    def _extract_class_documentation(self, module_name: str, class_name: str) -> Optional[APIClassDoc]:
        """Extract documentation from a class"""
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)

            # Get class description
            class_doc = inspect.getdoc(cls) or f"{class_name} class"

            # Extract methods
            methods = []
            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if not name.startswith('_'):  # Skip private methods
                    method_doc = self._extract_method_documentation(method)
                    if method_doc:
                        methods.append(method_doc)

            # Generate usage examples
            examples = self._generate_class_examples(class_name)
            usage_patterns = self._generate_usage_patterns(class_name)

            return APIClassDoc(
                name=class_name,
                description=class_doc,
                methods=methods,
                examples=examples,
                usage_patterns=usage_patterns
            )

        except Exception as e:
            logger.error(f"Failed to extract documentation for {class_name}: {e}")
            return None

    def _extract_method_documentation(self, method) -> Optional[APIMethodDoc]:
        """Extract documentation from a method"""
        try:
            # Get method signature
            sig = inspect.signature(method)
            signature = f"{method.__name__}{sig}"

            # Get docstring
            docstring = inspect.getdoc(method) or "No description available"

            # Extract parameters from signature
            parameters = []
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    param_info = {
                        'name': param_name,
                        'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                        'default': str(param.default) if param.default != inspect.Parameter.empty else None,
                        'description': f"Parameter {param_name}"
                    }
                    parameters.append(param_info)

            # Get return type
            return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else 'Any'

            # Generate examples
            examples = self._generate_method_examples(method.__name__)

            return APIMethodDoc(
                name=method.__name__,
                signature=signature,
                docstring=docstring,
                parameters=parameters,
                return_type=return_type,
                examples=examples
            )

        except Exception as e:
            logger.error(f"Failed to extract method documentation: {e}")
            return None

    def _generate_class_examples(self, class_name: str) -> List[str]:
        """Generate usage examples for a class"""
        examples = []

        if class_name == "CSSPreprocessor":
            examples = [
                """
# Basic CSS preprocessing
preprocessor = CSSPreprocessor()
variables = {'color-primary': '#0078d4', 'spacing-md': '16px'}
css = "QWidget { color: var(--color-primary); padding: var(--spacing-md); }"
processed = preprocessor.process_css(css, variables)
print(processed)  # QWidget { color: #0078d4; padding: 16px; }
                """,
                """
# Processing CSS files
variables = preprocessor.parse_css_file("themes/css/variables.css")
combined = preprocessor.combine_css_files(["theme1.css", "theme2.css"], variables)
                """
            ]

        elif class_name == "CSSFileBasedThemeManager":
            examples = [
                """
# Basic theme management
theme_manager = CSSFileBasedThemeManager()
theme_manager.set_theme("dark")
available_themes = theme_manager.get_available_themes()
current_theme = theme_manager.get_current_theme()
                """,
                """
# Theme switching with caching
theme_manager.set_theme("light")  # Fast - uses cache
theme_manager.reload_current_theme()  # Force reload
theme_manager.toggle_theme()  # Switch between themes
                """
            ]

        elif class_name == "IconPreprocessor":
            examples = [
                """
# Icon processing
icon_processor = IconPreprocessor("icons")
icon_css = icon_processor.generate_icon_css(generate_variables=True)
processed_icons = icon_processor.process_all_icons()
                """,
                """
# Custom icon processing
processor = IconPreprocessor()
processor.process_svg_file("path/to/icon.svg")
css_with_icons = processor.generate_icon_css()
                """
            ]

        elif class_name == "AdvancedCSSCache":
            examples = [
                """
# Advanced caching
cache = AdvancedCSSCache(max_memory_mb=25, max_entries=500)
cache.put(("theme", "dark", "processed"), css_content)
cached_css = cache.get(("theme", "dark", "processed"))
stats = cache.get_statistics()
                """,
                """
# Cache management
cache.cleanup_expired(max_age_hours=24)
cache.clear(clear_disk=True)
cache.print_statistics()
                """
            ]

        return examples

    def _generate_usage_patterns(self, class_name: str) -> List[str]:
        """Generate common usage patterns for a class"""
        patterns = []

        if class_name == "CSSPreprocessor":
            patterns = [
                "Variable Resolution: Load variables from files and process CSS with variable substitution",
                "File Combination: Combine multiple CSS files with shared variables",
                "Caching: Cache processed CSS for performance optimization",
                "Nested Variables: Handle complex variable dependencies and resolution"
            ]

        elif class_name == "CSSFileBasedThemeManager":
            patterns = [
                "Theme Loading: Load and apply complete themes with preprocessing",
                "Dynamic Switching: Switch themes at runtime with minimal performance impact",
                "Cache Management: Preload and cache themes for fast switching",
                "Integration: Integrate with preprocessors and icon systems"
            ]

        elif class_name == "IconPreprocessor":
            patterns = [
                "SVG Processing: Convert SVG icons to theme-aware CSS",
                "Base64 Encoding: Embed icons directly in CSS using data URLs",
                "Theme Integration: Generate color-aware icons for different themes",
                "Automatic Discovery: Process all icons in a directory automatically"
            ]

        elif class_name == "AdvancedCSSCache":
            patterns = [
                "Memory Management: Efficient caching with memory limits and LRU eviction",
                "Persistence: Cache data to disk for cross-session performance",
                "Analytics: Track cache performance and optimization opportunities",
                "Cleanup: Automatic cleanup of expired cache entries"
            ]

        return patterns

    def _generate_method_examples(self, method_name: str) -> List[str]:
        """Generate examples for specific methods"""
        examples = []

        method_examples = {
            "process_css": [
                """
css = "QWidget { color: var(--primary); }"
variables = {"primary": "#0078d4"}
result = processor.process_css(css, variables)
# Result: "QWidget { color: #0078d4; }"
                """
            ],
            "set_theme": [
                """
theme_manager.set_theme("dark")  # Switch to dark theme
theme_manager.set_theme("light") # Switch to light theme
                """
            ],
            "generate_icon_css": [
                """
# Generate CSS for all processed icons
css = icon_processor.generate_icon_css(generate_variables=True)
# Result: CSS with .icon-* classes and theme variables
                """
            ],
            "get_statistics": [
                """
stats = cache.get_statistics()
print(f"Hit ratio: {stats['hit_ratio']:.1f}%")
print(f"Memory usage: {stats['memory_usage_mb']:.1f} MB")
                """
            ]
        }

        return method_examples.get(method_name, [])

    def generate_api_reference(self) -> str:
        """Generate complete API reference documentation"""
        logger.info("Generating API reference documentation")

        api_docs = []

        # Document each class
        for class_name in self.classes_to_document:
            module_map = {
                'CSSPreprocessor': 'services.css_preprocessor',
                'CSSFileBasedThemeManager': 'services.css_file_based_theme_manager',
                'IconPreprocessor': 'services.icon_preprocessor',
                'AdvancedCSSCache': 'services.css_cache_optimizer'
            }

            module_name = module_map.get(class_name)
            if module_name:
                class_doc = self._extract_class_documentation(module_name, class_name)
                if class_doc:
                    api_docs.append(self._format_class_documentation(class_doc))

        # Combine all documentation
        full_doc = self._generate_api_header() + "\n\n".join(api_docs)

        # Write to file
        api_file = self.output_dir / "api_reference.md"
        with open(api_file, 'w') as f:
            f.write(full_doc)

        logger.info(f"API reference generated: {api_file}")
        return str(api_file)

    def _generate_api_header(self) -> str:
        """Generate API documentation header"""
        return f"""# CSS Centralization System - API Reference

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document provides comprehensive API reference for the CSS Centralization System, including all classes, methods, and usage examples.

## Architecture

The CSS system consists of four main components:

1. **CSSPreprocessor**: Handles CSS variable processing and file combination
2. **CSSFileBasedThemeManager**: Manages theme loading, switching, and application
3. **IconPreprocessor**: Processes SVG icons into theme-aware CSS
4. **AdvancedCSSCache**: Provides high-performance caching with memory management

## Quick Start

```python
# Initialize the CSS system
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

theme_manager = CSSFileBasedThemeManager()
theme_manager.set_theme("dark")
```

---
"""

    def _format_class_documentation(self, class_doc: APIClassDoc) -> str:
        """Format class documentation as markdown"""
        doc = f"""## {class_doc.name}

{class_doc.description}

### Usage Patterns

{chr(10).join(f"- **{pattern.split(':')[0]}**: {pattern.split(':', 1)[1].strip()}" for pattern in class_doc.usage_patterns)}

### Methods

"""

        # Add method documentation
        for method in class_doc.methods:
            doc += f"""#### {method.name}

```python
{method.signature}
```

{method.docstring}

**Parameters:**
{chr(10).join(f"- `{p['name']}` ({p['type']}): {p['description']}" + (f" (default: {p['default']})" if p['default'] else "") for p in method.parameters) if method.parameters else "None"}

**Returns:** `{method.return_type}`

**Examples:**
{chr(10).join(f"```python{example}```" for example in method.examples) if method.examples else "No examples available"}

---

"""

        # Add class examples
        if class_doc.examples:
            doc += f"""### Examples

{chr(10).join(f"```python{example}```" for example in class_doc.examples)}

---

"""

        return doc

    def generate_developer_guide(self) -> str:
        """Generate developer guide with best practices"""
        logger.info("Generating developer guide")

        guide_content = f"""# CSS Centralization System - Developer Guide

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Introduction

This guide provides comprehensive information for developers working with the CSS Centralization System in the PySide POEditor Plugin.

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                CSS Centralization System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │ CSSPreprocessor │  │ IconPreprocessor │  │ CacheSystem │ │
│  │                 │  │                  │  │             │ │
│  │ • Variable      │  │ • SVG Processing │  │ • Memory    │ │
│  │   Resolution    │  │ • Base64 Encode  │  │   Management│ │
│  │ • File Combine  │  │ • Theme Colors   │  │ • Disk      │ │
│  │ • Caching       │  │ • CSS Generation │  │   Persist   │ │
│  └─────────────────┘  └──────────────────┘  └─────────────┘ │
│                              │                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           CSSFileBasedThemeManager                      │ │
│  │                                                         │ │
│  │ • Theme Loading & Switching                             │ │
│  │ • Component Integration                                 │ │
│  │ • Performance Optimization                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### 1. CSS Variable Usage

**DO:**
```css
/* Use semantic variable names */
QWidget {{
    color: var(--color-text-primary);
    background-color: var(--color-bg-surface);
    border: var(--border-width-thin) solid var(--color-border);
}}
```

**DON'T:**
```css
/* Avoid hardcoded values */
QWidget {{
    color: #333333;
    background-color: #ffffff;
    border: 1px solid #cccccc;
}}
```

### 2. Theme Creation

To create a new theme:

1. **Create theme file**: `themes/css/my_theme.css`
2. **Define variables**: Override base variables for your theme
3. **Test thoroughly**: Use cross-platform testing tools
4. **Document changes**: Add theme to documentation

```css
/* my_theme.css */
:root {{
    /* Override base variables */
    --color-bg-main: #1e1e1e;
    --color-text-primary: #ffffff;
    --color-accent: #ff6b35;
}}
```

### 3. Performance Optimization

**Theme Switching Performance:**
- Preload common themes in cache
- Use `set_theme()` for instant switching
- Monitor cache hit ratios

**Memory Management:**
- Configure cache limits appropriately
- Clean up expired cache entries
- Monitor memory usage

```python
# Optimal cache configuration
cache = AdvancedCSSCache(
    max_memory_mb=25,    # Reasonable memory limit
    max_entries=500,     # Prevent unlimited growth
    cache_dir=".cache"   # Persistent storage
)
```

### 4. Icon Integration

**SVG Icon Guidelines:**
- Use semantic file names (`icon_active.svg`, `icon_inactive.svg`)
- Keep icons simple for better rendering
- Use theme-aware colors (`currentColor` or specific theme colors)

```python
# Process icons for theme integration
icon_processor = IconPreprocessor("icons")
icon_css = icon_processor.generate_icon_css(generate_variables=True)
```

## Common Patterns

### Pattern 1: Theme Initialization

```python
def setup_theme_system():
    # Initialize theme manager
    theme_manager = CSSFileBasedThemeManager()

    # Load saved theme or default
    theme_manager.apply_saved_theme()

    # Preload cache for performance
    theme_manager._preload_css_cache()

    return theme_manager
```

### Pattern 2: Dynamic Theme Switching

```python
def switch_theme(theme_manager, theme_name):
    # Validate theme exists
    available = theme_manager.get_available_themes()
    if theme_name not in available:
        raise ValueError("Theme not available: " + theme_name)

    # Switch theme
    theme_manager.set_theme(theme_name)

    # Save preference
    theme_manager._save_current_theme()
```

### Pattern 3: Custom CSS Processing

```python
def process_custom_css(css_content, theme_variables):
    preprocessor = CSSPreprocessor()

    # Add custom variables
    variables = theme_variables.copy()
    variables.update({{'custom-color': '#ff6b35'}})

    # Process CSS
    return preprocessor.process_css(css_content, variables)
```

## Troubleshooting

### Common Issues

1. **Theme not loading**: Check file paths and CSS syntax
2. **Variables not resolving**: Verify variable names and scope
3. **Poor performance**: Check cache configuration and memory usage
4. **Icons not displaying**: Verify SVG processing and CSS generation

### Debugging Tools

```python
# Performance monitoring
stats = cache.get_statistics()
print(f"Hit ratio: {{stats['hit_ratio']:.1f}}%")

# CSS processing debugging
processed = preprocessor.process_css(css, variables, debug=True)

# Theme validation
themes = theme_manager.get_available_themes()
current = theme_manager.get_current_theme()
```

## Testing

### Unit Testing

```python
def test_css_processing():
    preprocessor = CSSPreprocessor()
    css = "QWidget {{ color: var(--test-color); }}"
    variables = {{"test-color": "#ff0000"}}

    result = preprocessor.process_css(css, variables)
    assert "var(--test-color)" not in result
    assert "#ff0000" in result
```

### Performance Testing

```python
from tests.performance.css_performance_benchmark import CSSPerformanceBenchmark

benchmark = CSSPerformanceBenchmark()
results = benchmark.run_all_benchmarks()
```

### Cross-Platform Testing

```python
from tests.compatibility.cross_platform_css_validator import CrossPlatformCSSValidator

validator = CrossPlatformCSSValidator()
results = validator.run_all_compatibility_tests(theme_manager)
```

## Migration Guide

### From Legacy System

1. **Identify hardcoded colors**: Use grep to find hex colors in CSS
2. **Create variable mappings**: Map colors to semantic variables
3. **Update CSS files**: Replace hardcoded values with variables
4. **Test thoroughly**: Verify all themes render correctly

### Performance Optimization

1. **Enable caching**: Use AdvancedCSSCache for better performance
2. **Preload themes**: Cache common themes on startup
3. **Monitor metrics**: Track cache hit ratios and memory usage
4. **Optimize variables**: Reduce variable complexity where possible

---

*This guide is automatically generated from the CSS system codebase. For the latest information, see the API reference and source code documentation.*
"""

        # Write to file
        guide_file = self.output_dir / "developer_guide.md"
        with open(guide_file, 'w') as f:
            f.write(guide_content)

        logger.info(f"Developer guide generated: {guide_file}")
        return str(guide_file)

    def generate_performance_guide(self) -> str:
        """Generate performance optimization guide"""
        logger.info("Generating performance optimization guide")

        perf_guide = f"""# CSS System Performance Optimization Guide

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Performance Targets

The CSS Centralization System is designed to meet these performance targets:

- **Theme Switching**: < 100ms per switch
- **CSS Processing**: < 50ms for typical files
- **Memory Usage**: < 25MB for cache system
- **Cache Hit Ratio**: > 80% for optimal performance

## Optimization Strategies

### 1. Caching Configuration

```python
# Optimal cache configuration for different use cases

# Development (frequent changes)
cache = AdvancedCSSCache(
    max_memory_mb=10,
    max_entries=100,
    cache_dir=".cache"
)

# Production (stable themes)
cache = AdvancedCSSCache(
    max_memory_mb=50,
    max_entries=1000,
    cache_dir=".cache"
)

# Memory-constrained environments
cache = AdvancedCSSCache(
    max_memory_mb=5,
    max_entries=50,
    cache_dir=".cache"
)
```

### 2. Theme Preloading

```python
# Preload frequently used themes
def optimize_theme_loading(theme_manager):
    common_themes = ['light', 'dark']

    for theme in common_themes:
        # Preload into cache
        theme_manager.set_theme(theme)

    # Switch back to preferred theme
    theme_manager.apply_saved_theme()
```

### 3. CSS Variable Optimization

**Efficient Variable Structure:**
```css
/* Good: Semantic grouping */
:root {{
    /* Colors */
    --color-primary: #0078d4;
    --color-secondary: #6b7280;

    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
}}
```

**Avoid Complex Nesting:**
```css
/* Avoid: Deep nesting slows processing */
:root {{
    --color-base: #0078d4;
    --color-variant: var(--color-base);
    --color-final: var(--color-variant);
}}
```

### 4. Icon Processing Optimization

```python
# Efficient icon processing
def optimize_icon_processing():
    processor = IconPreprocessor()

    # Process icons once, cache results
    icon_css = processor.generate_icon_css(generate_variables=True)

    # Store processed CSS for reuse
    with open('cache/icons.css', 'w') as f:
        f.write(icon_css)
```

## Performance Monitoring

### Real-time Monitoring

```python
def monitor_performance(theme_manager):
    # Get cache statistics
    if hasattr(theme_manager, 'advanced_cache'):
        stats = theme_manager.advanced_cache.get_statistics()

        # Log performance metrics
        logger.info(f"Cache hit ratio: {{stats['hit_ratio']:.1f}}%")
        logger.info(f"Memory usage: {{stats['memory_usage_mb']:.1f}} MB")

        # Alert if performance degrades
        if stats['hit_ratio'] < 70:
            logger.warning("Cache hit ratio below optimal level")

        if stats['memory_usage_mb'] > 30:
            logger.warning("Memory usage exceeding recommended limit")
```

### Benchmarking

```python
from tests.performance.css_performance_benchmark import CSSPerformanceBenchmark

def run_performance_analysis():
    benchmark = CSSPerformanceBenchmark()
    results = benchmark.run_all_benchmarks()

    # Analyze results
    for result in results:
        if not result.all_passed:
            print(f"Performance issue in {{result.test_name}}")
            for metric in result.metrics:
                if not metric.passed:
                    print(f"  {{metric.name}}: {{metric.value}} {{metric.unit}} (target: {{metric.target}})")
```

## Memory Management

### Cache Cleanup

```python
def optimize_memory_usage(cache):
    # Regular cleanup
    cache.cleanup_expired(max_age_hours=24)

    # Force cleanup if memory usage high
    stats = cache.get_statistics()
    if stats['memory_usage_percent'] > 80:
        cache.clear(clear_disk=False)  # Keep disk cache
```

### Memory Profiling

```python
import tracemalloc

def profile_memory_usage():
    tracemalloc.start()

    # Perform CSS operations
    theme_manager = CSSFileBasedThemeManager()
    theme_manager.set_theme('dark')

    # Get memory usage
    current, peak = tracemalloc.get_traced_memory()
    print(f"Memory usage: {{current / 1024 / 1024:.1f}} MB (peak: {{peak / 1024 / 1024:.1f}} MB)")

    tracemalloc.stop()
```

## Platform-Specific Optimizations

### macOS
- Use `.AppleSystemUIFont` for better rendering performance
- Consider Retina display scaling factors
- Test with multiple color spaces

### Windows
- Optimize for ClearType rendering
- Test with different DPI scaling
- Consider Windows theme integration

### Linux
- Provide efficient font fallbacks
- Test with different desktop environments
- Optimize for various display managers

## Troubleshooting Performance Issues

### Common Issues and Solutions

**Slow Theme Switching:**
- Check cache configuration
- Verify CSS file sizes
- Monitor variable resolution complexity

**High Memory Usage:**
- Reduce cache size limits
- Implement more aggressive cleanup
- Profile memory allocation patterns

**Poor Cache Performance:**
- Analyze cache hit ratios
- Optimize cache key generation
- Review cache eviction policies

---

*For more detailed performance analysis, use the built-in benchmarking tools and monitor cache statistics regularly.*
"""

        # Write to file
        perf_file = self.output_dir / "performance_guide.md"
        with open(perf_file, 'w') as f:
            f.write(perf_guide)

        logger.info(f"Performance guide generated: {perf_file}")
        return str(perf_file)

    def generate_all_documentation(self) -> Dict[str, str]:
        """Generate all CSS system documentation"""
        logger.info("Generating complete CSS system documentation")

        docs = {}
        docs['api_reference'] = self.generate_api_reference()
        docs['developer_guide'] = self.generate_developer_guide()
        docs['performance_guide'] = self.generate_performance_guide()

        # Generate index file
        index_content = f"""# CSS Centralization System Documentation

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Available Documentation

- [API Reference](api_reference.md) - Complete API documentation with examples
- [Developer Guide](developer_guide.md) - Best practices and usage patterns
- [Performance Guide](performance_guide.md) - Optimization strategies and monitoring

## Quick Links

- [Getting Started](#getting-started)
- [Architecture Overview](#architecture-overview)
- [Performance Targets](#performance-targets)

## Getting Started

```python
from services.css_file_based_theme_manager import CSSFileBasedThemeManager

# Initialize the CSS system
theme_manager = CSSFileBasedThemeManager()

# Set a theme
theme_manager.set_theme("dark")

# Get available themes
themes = theme_manager.get_available_themes()
print(f"Available themes: {{themes}}")
```

## Architecture Overview

The CSS Centralization System provides:

1. **Variable Processing**: CSS custom properties support for PySide6
2. **Theme Management**: Dynamic theme loading and switching
3. **Icon Integration**: SVG to CSS conversion with theme awareness
4. **Performance Optimization**: Advanced caching and memory management

## Performance Targets

- Theme switching: < 100ms
- CSS processing: < 50ms
- Memory usage: < 25MB
- Cache hit ratio: > 80%

---

*This documentation is automatically generated from the codebase. For the latest updates, regenerate using the CSSAPIDocumentationGenerator.*
"""

        index_file = self.output_dir / "README.md"
        with open(index_file, 'w') as f:
            f.write(index_content)

        docs['index'] = str(index_file)

        logger.info(f"Complete documentation generated in: {self.output_dir}")
        return docs


def generate_css_documentation():
    """Generate complete CSS system documentation"""
    generator = CSSAPIDocumentationGenerator()
    docs = generator.generate_all_documentation()

    print("\\n=== CSS SYSTEM DOCUMENTATION GENERATED ===")
    for doc_type, file_path in docs.items():
        print(f"{doc_type.replace('_', ' ').title()}: {file_path}")
    print("=" * 50)

    return docs


if __name__ == "__main__":
    generate_css_documentation()
