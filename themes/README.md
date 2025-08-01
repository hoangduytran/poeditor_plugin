# CSS Theming System

## Directory Structure

```
themes/
├── base/             # Base styles and variables
│   ├── variables.css # Global variables
│   └── reset.css     # Base styling reset
├── components/       # Component-specific styles
│   ├── activity_bar.css
│   ├── status_bar.css
│   └── ...
├── variants/         # Theme variations
│   ├── light.css     # Light theme variables
│   ├── dark.css      # Dark theme variables
│   └── colorful.css  # Colorful theme variables
└── icons/            # Icon assets and CSS classes
    ├── icons.css     # Generated CSS classes for icons
    └── svg/          # Original SVG sources
```

## CSS Variable System

This CSS system uses a variable-based approach to ensure consistency across components. The variables are processed by the `CSSPreprocessor` class since PySide6 doesn't natively support CSS variables.

### Example Usage

```css
/* In component file */
.button {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
}
```

## Adding New Components

To add styles for a new component:

1. Create a new CSS file in the `components/` directory
2. Use variables from `base/variables.css` and theme variants
3. Target elements using object names: `QWidget[objectName="your_component"]`

## Adding New Themes

To create a new theme:

1. Create a new CSS file in the `variants/` directory (e.g., `my_theme.css`)
2. Override base variables with theme-specific colors and values
3. Test the theme with various components

## Development and Debugging

Use the CSS Debug Tool (`css_debug_tool.py`) to:

- Visualize applied variables
- Hot-reload CSS changes during development
- Check selector specificity and rule application

## Best Practices

1. **Always use variables** for colors, spacing, and other design tokens
2. **Use objectName for targeting** elements in CSS
3. **Set state properties** on widgets to allow state-based styling
4. **Avoid !important** flags whenever possible
5. **Keep component CSS focused** on the component only

## Working with Icons

The `IconManager` handles converting SVG icons to base64-encoded data URLs for CSS or direct `QIcon` usage. To add a new icon:

1. Add SVG file to `themes/icons/svg/`
2. Use `IconManager.generate_icons_css()` to regenerate the icons CSS

## API Reference

### CSSPreprocessor

Handles variable processing and CSS file management.

### EnhancedThemeManager

Manages theme loading, switching and application to widgets.

### IconManager

Manages SVG icons and generates icon CSS classes.
