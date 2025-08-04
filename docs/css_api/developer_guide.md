# CSS Centralization System - Developer Guide

**Generated on**: 2025-08-04 13:13:29

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
QWidget {
    color: var(--color-text-primary);
    background-color: var(--color-bg-surface);
    border: var(--border-width-thin) solid var(--color-border);
}
```

**DON'T:**
```css
/* Avoid hardcoded values */
QWidget {
    color: #333333;
    background-color: #ffffff;
    border: 1px solid #cccccc;
}
```

### 2. Theme Creation

To create a new theme:

1. **Create theme file**: `themes/css/my_theme.css`
2. **Define variables**: Override base variables for your theme
3. **Test thoroughly**: Use cross-platform testing tools
4. **Document changes**: Add theme to documentation

```css
/* my_theme.css */
:root {
    /* Override base variables */
    --color-bg-main: #1e1e1e;
    --color-text-primary: #ffffff;
    --color-accent: #ff6b35;
}
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
    variables.update({'custom-color': '#ff6b35'})
    
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
print(f"Hit ratio: {stats['hit_ratio']:.1f}%")

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
    css = "QWidget { color: var(--test-color); }"
    variables = {"test-color": "#ff0000"}
    
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
