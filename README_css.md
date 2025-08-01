# CSS Theming System

## Overview

This document explains the CSS theming system used in the PySide6 POEditor plugin. The system provides a way to create and customize themes using CSS variables, even though PySide6 doesn't natively support CSS variables.

## Directory Structure

```
themes/
├── base/
│   ├── variables.css      # Global variables
│   └── reset.css          # Base styling reset
├── components/            # Component-specific styles
│   ├── activity_bar.css
│   ├── status_bar.css
│   └── ...
├── variants/              # Theme variations
│   ├── light.css          # Light theme variables
│   ├── dark.css           # Dark theme variables
│   └── ...
├── icons/                 # Icon assets and CSS classes
│   ├── icons.css          # Generated CSS classes for icons
│   └── svg/               # Original SVG sources
└── generated/             # Generated theme CSS files
    ├── light.css
    ├── dark.css
    └── ...
```

## How It Works

1. **CSS Variables**: We use CSS variables (custom properties) in our source CSS files:
   ```css
   .button {
     background-color: var(--color-primary);
     padding: var(--spacing-md);
   }
   ```

2. **Preprocessing**: Since PySide6 doesn't support CSS variables, we use a preprocessor to replace them with actual values before applying the CSS:
   ```css
   /* Processed output */
   .button {
     background-color: #0078D4;
     padding: 16px;
   }
   ```

3. **Theme Variants**: Theme-specific variables are defined in variant files and override the base variables.

## Usage

### In Python Code

```python
from services.enhanced_theme_manager import EnhancedThemeManager

# Initialize the theme manager
theme_manager = EnhancedThemeManager()

# Apply theme to the application
theme_manager.apply_theme_to_application(app)

# Switch themes at runtime
theme_manager.switch_theme("dark")
theme_manager.apply_theme_to_application(app)
```

### Component Styling

Styles for components should be placed in their own CSS files in the `themes/components/` directory:

```css
/* activity_bar.css */
QWidget[objectName="activity_bar"] {
  background-color: var(--color-activity-bar-bg);
  min-width: var(--activity-bar-width);
}
```

### Setting Object Names

For CSS selectors to work properly, widgets must have proper object names:

```python
activity_bar = QWidget()
activity_bar.setObjectName("activity_bar")
```

## Development Tools

The CSS system includes development tools to help with theme creation and testing:

```bash
# Watch CSS files for changes and rebuild themes automatically
python tools/css_dev_tools.py watch

# Build all themes
python tools/css_dev_tools.py build

# Show CSS variables for a theme
python tools/css_dev_tools.py vars --theme dark

# Create a new theme skeleton
python tools/css_dev_tools.py new mytheme

# Export theme variables as JSON
python tools/css_dev_tools.py export dark --output dark_vars.json
```

## Adding New Components

When adding a new component:

1. Create a new CSS file in `themes/components/`
2. Use CSS variables for all styling properties
3. Use proper object names for CSS selectors
4. Avoid using hard-coded values

## Creating a New Theme

To create a new theme:

1. Create a new file in `themes/variants/` (e.g., `mytheme.css`)
2. Define theme-specific variables that override base variables
3. Build the theme with the development tools
4. Test the theme with different components

## Icon System

The CSS system includes an IconManager for working with SVG icons:

```python
from services.icon_manager import IconManager

# Initialize the icon manager
icon_manager = IconManager()

# Get a QIcon for use in Qt widgets
icon = icon_manager.get_icon("file")
button.setIcon(icon)

# Generate CSS for all icons
icon_manager.save_icons_css()
```

In CSS, icons can be used with classes:

```css
.file-icon {
  background-image: url('data:image/png;base64,...');
}
```

## Best Practices

1. **Use Variables**: Always use CSS variables instead of hard-coded values
2. **Component Isolation**: Keep component styles in separate files
3. **Object Names**: Use meaningful object names for CSS selectors
4. **BEM Naming**: Consider using BEM naming for complex components
5. **Testing**: Test themes on all supported platforms
6. **Performance**: Keep an eye on CSS size and complexity

## Troubleshooting

- **Styles Not Applied**: Check object names and selectors
- **Variable Not Found**: Check variable names and theme files
- **Slow Theme Switching**: Use the CSS preprocessor cache
- **Platform Differences**: Test on all supported platforms
