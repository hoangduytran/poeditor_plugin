# CSS Centralization System - API Reference

**Generated on**: 2025-08-04 13:13:29

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
## CSSPreprocessor

CSS Preprocessor for handling CSS variables in PySide6

PySide6 doesn't support CSS custom properties (variables), so this preprocessor
converts CSS with variables into standard CSS by replacing var(--variable) references
with their actual values.

### Usage Patterns

- **Variable Resolution**: Load variables from files and process CSS with variable substitution
- **File Combination**: Combine multiple CSS files with shared variables
- **Caching**: Cache processed CSS for performance optimization
- **Nested Variables**: Handle complex variable dependencies and resolution

### Methods

#### clear_cache

```python
clear_cache(self)
```

Clear the preprocessor cache

**Parameters:**
None

**Returns:** `Any`

**Examples:**
No examples available

---

#### combine_css_files

```python
combine_css_files(self, file_paths: List[str], variables: Dict[str, str]) -> str
```

Combine multiple CSS files into a single CSS string with variables replaced

Args:
    file_paths: List of CSS file paths
    variables: Dictionary of variable names and values

Returns:
    Combined and processed CSS content

**Parameters:**
- `file_paths` (typing.List[str]): Parameter file_paths
- `variables` (typing.Dict[str, str]): Parameter variables

**Returns:** `<class 'str'>`

**Examples:**
No examples available

---

#### extract_variables

```python
extract_variables(self, css_content: str) -> Dict[str, str]
```

Extract CSS variables and their values from CSS content

Args:
    css_content: CSS content as string

Returns:
    Dictionary of variable names and their values

**Parameters:**
- `css_content` (<class 'str'>): Parameter css_content

**Returns:** `typing.Dict[str, str]`

**Examples:**
No examples available

---

#### generate_final_css

```python
generate_final_css(self, theme_name: str) -> str
```

Generate final CSS for a theme by combining and processing all relevant files

Args:
    theme_name: Name of the theme (e.g., 'light', 'dark')

Returns:
    Final processed CSS for the theme

**Parameters:**
- `theme_name` (<class 'str'>): Parameter theme_name

**Returns:** `<class 'str'>`

**Examples:**
No examples available

---

#### parse_css_file

```python
parse_css_file(self, file_path: str) -> Dict[str, str]
```

Parse CSS file to extract variables

Args:
    file_path: Path to CSS file

Returns:
    Dictionary of variable names and values

**Parameters:**
- `file_path` (<class 'str'>): Parameter file_path

**Returns:** `typing.Dict[str, str]`

**Examples:**
No examples available

---

#### process_css

```python
process_css(self, css_content: str, variables: Dict[str, str]) -> str
```

Process CSS content by replacing variable references with actual values

Args:
    css_content: CSS content as string
    variables: Dictionary of variable names and values

Returns:
    Processed CSS with variables replaced

**Parameters:**
- `css_content` (<class 'str'>): Parameter css_content
- `variables` (typing.Dict[str, str]): Parameter variables

**Returns:** `<class 'str'>`

**Examples:**
```python
css = "QWidget { color: var(--primary); }"
variables = {"primary": "#0078d4"}
result = processor.process_css(css, variables)
# Result: "QWidget { color: #0078d4; }"
                ```

---

#### process_css_file

```python
process_css_file(self, file_path: str, variables: Dict[str, str]) -> str
```

Process a CSS file by replacing variable references with actual values

Args:
    file_path: Path to CSS file
    variables: Dictionary of variable names and values

Returns:
    Processed CSS content

**Parameters:**
- `file_path` (<class 'str'>): Parameter file_path
- `variables` (typing.Dict[str, str]): Parameter variables

**Returns:** `<class 'str'>`

**Examples:**
No examples available

---

### Examples

```python
# Basic CSS preprocessing
preprocessor = CSSPreprocessor()
variables = {'color-primary': '#0078d4', 'spacing-md': '16px'}
css = "QWidget { color: var(--color-primary); padding: var(--spacing-md); }"
processed = preprocessor.process_css(css, variables)
print(processed)  # QWidget { color: #0078d4; padding: 16px; }
                ```
```python
# Processing CSS files
variables = preprocessor.parse_css_file("themes/css/variables.css")
combined = preprocessor.combine_css_files(["theme1.css", "theme2.css"], variables)
                ```

---



## CSSFileBasedThemeManager

Manages the application's theme, including loading, switching, and applying themes.
Supports both file-based CSS themes and resource-based themes with fallback.

### Usage Patterns

- **Theme Loading**: Load and apply complete themes with preprocessing
- **Dynamic Switching**: Switch themes at runtime with minimal performance impact
- **Cache Management**: Preload and cache themes for fast switching
- **Integration**: Integrate with preprocessors and icon systems

### Methods

#### apply_activity_bar_theme

```python
apply_activity_bar_theme(self, widget) -> bool
```

Apply activity bar specific theme with CSS variable processing.

**Parameters:**
- `widget` (Any): Parameter widget

**Returns:** `<class 'bool'>`

**Examples:**
No examples available

---

#### apply_saved_theme

```python
apply_saved_theme(self)
```

Apply the saved theme from settings.

**Parameters:**
None

**Returns:** `Any`

**Examples:**
No examples available

---

#### get_available_themes

```python
get_available_themes(self) -> list
```

Get list of available themes by dynamically discovering CSS files.

**Parameters:**
None

**Returns:** `<class 'list'>`

**Examples:**
No examples available

---

#### get_css_manager_info

```python
get_css_manager_info(self) -> Dict
```

Get information about CSS manager state.

**Parameters:**
None

**Returns:** `typing.Dict`

**Examples:**
No examples available

---

#### get_current_theme

```python
get_current_theme(self) -> Optional[services.css_file_based_theme_manager.Theme]
```

Get the currently applied theme as a Theme object.

**Parameters:**
None

**Returns:** `typing.Optional[services.css_file_based_theme_manager.Theme]`

**Examples:**
No examples available

---

#### get_raw_css

```python
get_raw_css(self, theme_name: str) -> Optional[str]
```

Get raw CSS content for debugging.

**Parameters:**
- `theme_name` (<class 'str'>): Parameter theme_name

**Returns:** `typing.Optional[str]`

**Examples:**
No examples available

---

#### get_style_for_component

```python
get_style_for_component(self, component_name: str) -> Dict
```

Get style information for a specific component.

**Parameters:**
- `component_name` (<class 'str'>): Parameter component_name

**Returns:** `typing.Dict`

**Examples:**
No examples available

---

#### inject_css

```python
inject_css(self, css_snippet: str, temporary: bool = True) -> bool
```

Inject custom CSS snippet (development feature).

**Parameters:**
- `css_snippet` (<class 'str'>): Parameter css_snippet
- `temporary` (<class 'bool'>): Parameter temporary (default: True)

**Returns:** `<class 'bool'>`

**Examples:**
No examples available

---

#### refresh_theme

```python
refresh_theme(self) -> bool
```

Refresh the current theme (reload and reapply).

**Parameters:**
None

**Returns:** `<class 'bool'>`

**Examples:**
No examples available

---

#### reload_current_theme

```python
reload_current_theme(self) -> bool
```

Reload the current theme from disk (file-based CSS only).

**Parameters:**
None

**Returns:** `<class 'bool'>`

**Examples:**
No examples available

---

#### set_theme

```python
set_theme(self, theme_name: str)
```

Set and apply the theme by name with optimized performance.

Args:
    theme_name (str): The name of the theme to apply.

**Parameters:**
- `theme_name` (<class 'str'>): Parameter theme_name

**Returns:** `Any`

**Examples:**
```python
theme_manager.set_theme("dark")  # Switch to dark theme
theme_manager.set_theme("light") # Switch to light theme
                ```

---

#### toggle_theme

```python
toggle_theme(self) -> str
```

Toggle between available themes in a cycle.

**Parameters:**
None

**Returns:** `<class 'str'>`

**Examples:**
No examples available

---

### Examples

```python
# Basic theme management
theme_manager = CSSFileBasedThemeManager()
theme_manager.set_theme("dark")
available_themes = theme_manager.get_available_themes()
current_theme = theme_manager.get_current_theme()
                ```
```python
# Theme switching with caching
theme_manager.set_theme("light")  # Fast - uses cache
theme_manager.reload_current_theme()  # Force reload
theme_manager.toggle_theme()  # Switch between themes
                ```

---



## IconPreprocessor

Processes SVG icons for theme integration.

Features:
- Base64 SVG encoding for CSS embedding
- Dynamic color replacement based on theme variables
- CSS class generation for theme-aware icons
- Icon optimization and validation

### Usage Patterns

- **SVG Processing**: Convert SVG icons to theme-aware CSS
- **Base64 Encoding**: Embed icons directly in CSS using data URLs
- **Theme Integration**: Generate color-aware icons for different themes
- **Automatic Discovery**: Process all icons in a directory automatically

### Methods

#### generate_icon_css

```python
generate_icon_css(self, generate_variables: bool = False, class_prefix: str = 'icon-') -> str
```

Generate CSS for all icons in the directory.

Args:
    generate_variables: If True, generate CSS variables; if False, generate CSS classes
    class_prefix: Prefix for CSS class names (ignored if generate_variables=True)

Returns:
    CSS string with icon variables/classes

**Parameters:**
- `generate_variables` (<class 'bool'>): Parameter generate_variables (default: False)
- `class_prefix` (<class 'str'>): Parameter class_prefix (default: icon-)

**Returns:** `<class 'str'>`

**Examples:**
```python
# Generate CSS for all processed icons
css = icon_processor.generate_icon_css(generate_variables=True)
# Result: CSS with .icon-* classes and theme variables
                ```

---

#### get_available_icons

```python
get_available_icons(self) -> List[str]
```

Get list of available icon names.

Returns:
    List of icon names

**Parameters:**
None

**Returns:** `typing.List[str]`

**Examples:**
No examples available

---

#### get_icon_data_url

```python
get_icon_data_url(self, icon_name: str, variant: str = 'primary') -> Optional[str]
```

Get the data URL for a specific icon variant.

Args:
    icon_name: Name of the icon
    variant: Variant name (primary, secondary, muted, active, inactive)
    
Returns:
    Data URL string or None if not found

**Parameters:**
- `icon_name` (<class 'str'>): Parameter icon_name
- `variant` (<class 'str'>): Parameter variant (default: primary)

**Returns:** `typing.Optional[str]`

**Examples:**
No examples available

---

#### get_icon_variants

```python
get_icon_variants(self, icon_name: str) -> List[str]
```

Get available variants for a specific icon.

Args:
    icon_name: Name of the icon
    
Returns:
    List of variant names

**Parameters:**
- `icon_name` (<class 'str'>): Parameter icon_name

**Returns:** `typing.List[str]`

**Examples:**
No examples available

---

#### process_all_icons

```python
process_all_icons(self) -> Dict[str, Dict[str, str]]
```

Process all SVG files in the icons directory.

Returns:
    Dictionary of all processed icons with their variants

**Parameters:**
None

**Returns:** `typing.Dict[str, typing.Dict[str, str]]`

**Examples:**
No examples available

---

#### process_svg_file

```python
process_svg_file(self, svg_path: pathlib.Path) -> Optional[Dict[str, str]]
```

Process a single SVG file and generate theme-aware variants.

Args:
    svg_path: Path to the SVG file
    
Returns:
    Dictionary with icon variants or None if processing failed

**Parameters:**
- `svg_path` (<class 'pathlib.Path'>): Parameter svg_path

**Returns:** `typing.Optional[typing.Dict[str, str]]`

**Examples:**
No examples available

---

#### update_color_mapping

```python
update_color_mapping(self, color_key: str, css_variable: str)
```

Update or add a color mapping.

Args:
    color_key: Key for the color mapping
    css_variable: CSS variable to map to

**Parameters:**
- `color_key` (<class 'str'>): Parameter color_key
- `css_variable` (<class 'str'>): Parameter css_variable

**Returns:** `Any`

**Examples:**
No examples available

---

### Examples

```python
# Icon processing
icon_processor = IconPreprocessor("icons")
icon_css = icon_processor.generate_icon_css(generate_variables=True)
processed_icons = icon_processor.process_all_icons()
                ```
```python
# Custom icon processing
processor = IconPreprocessor()
processor.process_svg_file("path/to/icon.svg")
css_with_icons = processor.generate_icon_css()
                ```

---



## AdvancedCSSCache

Advanced caching system for CSS preprocessing with:
- Memory-efficient storage
- LRU eviction
- Persistent cache to disk
- Intelligent invalidation
- Cache analytics

### Usage Patterns

- **Memory Management**: Efficient caching with memory limits and LRU eviction
- **Persistence**: Cache data to disk for cross-session performance
- **Analytics**: Track cache performance and optimization opportunities
- **Cleanup**: Automatic cleanup of expired cache entries

### Methods

#### cleanup_expired

```python
cleanup_expired(self, max_age_hours: int = 48)
```

Clean up expired cache entries

**Parameters:**
- `max_age_hours` (<class 'int'>): Parameter max_age_hours (default: 48)

**Returns:** `Any`

**Examples:**
No examples available

---

#### clear

```python
clear(self, clear_disk: bool = True)
```

Clear all cache entries

**Parameters:**
- `clear_disk` (<class 'bool'>): Parameter clear_disk (default: True)

**Returns:** `Any`

**Examples:**
No examples available

---

#### get

```python
get(self, key_components: tuple, load_from_disk: bool = True) -> Optional[Any]
```

Retrieve data from cache with optional disk loading

**Parameters:**
- `key_components` (<class 'tuple'>): Parameter key_components
- `load_from_disk` (<class 'bool'>): Parameter load_from_disk (default: True)

**Returns:** `typing.Optional[typing.Any]`

**Examples:**
No examples available

---

#### get_statistics

```python
get_statistics(self) -> Dict[str, Any]
```

Get cache performance statistics

**Parameters:**
None

**Returns:** `typing.Dict[str, typing.Any]`

**Examples:**
```python
stats = cache.get_statistics()
print(f"Hit ratio: {stats['hit_ratio']:.1f}%")
print(f"Memory usage: {stats['memory_usage_mb']:.1f} MB")
                ```

---

#### print_statistics

```python
print_statistics(self)
```

Print cache performance statistics

**Parameters:**
None

**Returns:** `Any`

**Examples:**
No examples available

---

#### put

```python
put(self, key_components: tuple, data: Any, persist: bool = True) -> str
```

Store data in cache with optional persistence

**Parameters:**
- `key_components` (<class 'tuple'>): Parameter key_components
- `data` (typing.Any): Parameter data
- `persist` (<class 'bool'>): Parameter persist (default: True)

**Returns:** `<class 'str'>`

**Examples:**
No examples available

---

### Examples

```python
# Advanced caching
cache = AdvancedCSSCache(max_memory_mb=25, max_entries=500)
cache.put(("theme", "dark", "processed"), css_content)
cached_css = cache.get(("theme", "dark", "processed"))
stats = cache.get_statistics()
                ```
```python
# Cache management
cache.cleanup_expired(max_age_hours=24)
cache.clear(clear_disk=True)
cache.print_statistics()
                ```

---

