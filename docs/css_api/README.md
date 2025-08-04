# CSS Centralization System Documentation

**Generated on**: 2025-08-04 13:13:29

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
print(f"Available themes: {themes}")
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
