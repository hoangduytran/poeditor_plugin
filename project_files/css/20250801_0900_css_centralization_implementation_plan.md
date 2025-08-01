# CSS Centralization Implementation Plan

**Date:** 2025-08-01

## Current State Analysis

The PySide6 POEditor plugin currently has multiple CSS files spread across different locations with inconsistent organization:

1. **Multiple directories**:
   - `/themes/css/` - Contains theme files and component-specific CSS
   - `/assets/styles/` - Contains duplicated theme files

2. **Inconsistent naming and structure**:
   - Some components have dedicated CSS files (activity_bar.css, status_bar.css)
   - Theme files contain many component styles directly (light_theme.css, dark_theme.css)
   - Excessive use of `!important` flags to override styles

3. **Hard-coded values**:
   - Color values are hard-coded throughout CSS files
   - Spacing, typography, and other design tokens are not centralized

4. **CSS application mechanism**:
   - Current `ThemeManager` class loads CSS files directly without variable processing
   - No support for CSS variables (as PySide6 doesn't natively support them)

## Proposed Solution

Implement a centralized CSS theming system using a custom CSS preprocessor to handle variables and a more organized file structure.

### 1. Directory Structure

```
themes/
├── base/
│   ├── variables.css      # Global variables
│   └── reset.css          # Base styling reset
├── components/            # Component-specific styles
│   ├── activity_bar.css
│   ├── status_bar.css
│   ├── explorer.css
│   └── ...
├── variants/              # Theme variations
│   ├── light.css          # Light theme variables
│   ├── dark.css           # Dark theme variables
│   └── colorful.css       # Other theme variables
└── icons/                 # Icon assets and CSS classes
    ├── icons.css          # Generated CSS classes for icons
    └── svg/               # Original SVG sources
```

### 2. CSS Variables System

Since PySide6 doesn't support CSS variables natively, we'll implement a custom preprocessor that:

1. Parses CSS files with variable declarations (`--variable-name: value;`)
2. Resolves and replaces `var(--variable-name)` usages with actual values
3. Generates theme-specific CSS with all variables replaced

**Example variable usage:**

```css
/* In variables.css */
:root {
  --color-primary: #0078D4;
  --spacing-md: 16px;
}

/* In component file */
.button {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
}

/* Processed output for PySide6 */
.button {
  background-color: #0078D4;
  padding: 16px;
}
```

### 3. CSS Manager Implementation

Create a new `CSSPreprocessor` class that will:

1. Parse CSS files to extract variables
2. Process CSS by replacing variable references
3. Cache processed CSS for performance
4. Support multiple themes with variable cascading

Enhance the existing `ThemeManager` to:

1. Use the preprocessor to load and process theme CSS
2. Support runtime theme switching
3. Apply CSS to the application or specific widgets
4. Support hot-reloading during development

### 4. Icon System Integration

PySide6 has limited support for SVG icons in CSS. We'll implement:

1. A conversion utility to transform SVGs to either:
   - Base64-encoded PNG/JPG for CSS embedding
   - QIcon resources for direct Qt usage

2. An icon CSS class generator that creates:
   ```css
   .icon-file {
     background-image: url(data:image/png;base64,...);
     width: 16px;
     height: 16px;
   }
   ```

3. An `IconManager` class to handle icon loading and theming

### 5. Component Styling Strategy

1. **Use objectName for targeting**:
   - Every component should have a meaningful `objectName`
   - CSS selectors should use these object names: `QWidget[objectName="explorer_panel"]`

2. **Class-based styling**:
   - Use the Qt property system to apply CSS classes: `widget.setProperty("class", "primary-button")`
   - Target with CSS: `QPushButton[class="primary-button"]`

3. **State-based styling**:
   - Set state properties: `button.setProperty("state", "active")`
   - Target with CSS: `QPushButton[state="active"]`

### 6. Theme Organization

1. **Base Variables**: Common variables used across all themes
   ```css
   --spacing-xs: 4px;
   --spacing-sm: 8px;
   --spacing-md: 16px;
   --font-family-base: ".AppleSystemUIFont", "Segoe UI", sans-serif;
   --font-size-base: 13px;
   --border-radius-sm: 2px;
   ```

2. **Theme-Specific Variables**: Override base variables for each theme
   ```css
   /* light.css */
   --color-bg-primary: #ffffff;
   --color-text-primary: #333333;

   /* dark.css */
   --color-bg-primary: #1e1e1e;
   --color-text-primary: #ffffff;
   ```

3. **Component Styles**: Use variables from base and theme
   ```css
   /* activity_bar.css */
   QWidget[objectName="activity_bar"] {
     background-color: var(--color-activity-bar-bg);
     border-right: 1px solid var(--color-border);
   }
   ```

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)

1. Create new directory structure
2. Define core variables
3. Implement CSS preprocessor and theme manager classes
4. Create developer tools for CSS debugging

### Phase 2: Component Migration (Weeks 2-3)

1. Migrate existing components one by one
2. Convert hard-coded values to variables
3. Create component-specific CSS files
4. Update component code to use objectName and properties

### Phase 3: Icon System (Week 4)

1. Implement icon conversion utility
2. Create icon CSS generator
3. Update components to use new icon system

### Phase 4: Testing and Optimization (Week 5)

1. Benchmark performance
2. Optimize CSS caching
3. Ensure cross-platform compatibility
4. Document the new system

## Technical Implementation Details

### CSS Preprocessor

```python
class CSSPreprocessor:
    def __init__(self):
        self.cache = {}
        self.var_pattern = re.compile(r'var\(--([\w-]+)(?:,\s*([^)]+))?\)')

    def parse_variables(self, css_content):
        """Extract CSS variables from content"""
        variables = {}
        var_pattern = re.compile(r'--([\w-]+)\s*:\s*([^;]+);')

        for match in var_pattern.finditer(css_content):
            name, value = match.groups()
            variables[name] = value.strip()

        return variables

    def process_css(self, css_content, variables):
        """Replace variable references with actual values"""
        def replace_var(match):
            var_name, fallback = match.groups()
            if var_name in variables:
                return variables[var_name]
            elif fallback:
                return fallback.strip()
            return ''

        return self.var_pattern.sub(replace_var, css_content)

    def generate_theme_css(self, theme_name):
        """Generate complete CSS for a theme"""
        # Load base variables
        # Load theme variables
        # Process component CSS files
        # Return combined CSS
```

### ThemeManager Enhancement

```python
class ThemeManager:
    def __init__(self):
        self.preprocessor = CSSPreprocessor()
        self.current_theme = "light"

    def load_theme(self, theme_name):
        """Load and process CSS for a theme"""
        return self.preprocessor.generate_theme_css(theme_name)

    def switch_theme(self, theme_name):
        """Switch to a different theme"""
        self.current_theme = theme_name
        css = self.load_theme(theme_name)

        # Apply to application
        QApplication.instance().setStyleSheet(css)

    def apply_theme_to_widget(self, widget, theme_name=None):
        """Apply theme to a specific widget"""
        theme = theme_name or self.current_theme
        css = self.load_theme(theme)
        widget.setStyleSheet(css)
```

### IconManager

```python
class IconManager:
    def __init__(self):
        self.icons = {}
        self.icon_css = ""

    def load_icons(self, theme_name):
        """Load icons for a theme"""
        # Process SVG icons
        # Generate CSS classes
        # Cache results

    def get_icon(self, name):
        """Get QIcon for a named icon"""
        if name in self.icons:
            return self.icons[name]
        return QIcon()

    def get_icon_css(self):
        """Get CSS for all icons"""
        return self.icon_css
```

## Success Criteria

1. **Consistency**: All components use the same variable system
2. **Performance**: Theme switching takes < 100ms
3. **Maintainability**: New components can be styled without modifying theme files
4. **Extensibility**: New themes can be added without touching component files
5. **Developer Experience**: Clear documentation and tooling for CSS development

## Risk Mitigation

1. **Performance**: Implement aggressive caching for processed CSS
2. **PySide6 Limitations**: Test thoroughly on all platforms
3. **Migration Complexity**: Phase the migration, starting with simple components

---

This plan provides a comprehensive approach to centralizing and standardizing the CSS implementation in the PySide6 POEditor plugin, making it more maintainable, efficient, and consistent across components and themes.
