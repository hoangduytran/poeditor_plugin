# CSS Cascading Theme Test

This test demonstrates Qt's CSS cascading behavior and how to implement efficient theming using a common base stylesheet with theme-specific overrides.

## Overview

The test shows how Qt's stylesheet system works similar to web CSS:
- **Cascading**: Later stylesheets override earlier ones
- **Inheritance**: Child widgets inherit parent styles
- **Specificity**: More specific selectors override less specific ones

## File Structure

```
tests/test_cascading_css/
├── css/
│   ├── common.css      # Base styles (fonts, layouts, spacing)
│   ├── dark.css        # Dark theme color overrides
│   ├── light.css       # Light theme color overrides
│   └── colorful.css    # Colorful theme color overrides
├── test_cascading_themes.py  # Main test application
├── run_test.py         # Simple test runner
└── README.md           # This file
```

## How It Works

### 1. Base Styles (common.css)
Contains all the shared styling that doesn't change between themes:
- Font families and sizes
- Padding and margins
- Border radius and spacing
- Layout properties
- Basic widget structure

### 2. Theme Overrides (dark.css, light.css, colorful.css)
Each theme file only contains color-related properties:
- Background colors
- Text colors
- Border colors
- Hover/selected state colors
- Gradients and theme-specific effects

### 3. CSS Cascading
The application loads styles in this order:
```python
combined_css = common_css + "\n" + theme_css
app.setStyleSheet(combined_css)
```

Since CSS cascades, theme-specific colors override the base styles while keeping all the common layout and typography intact.

## Running the Test

### Option 1: Direct execution
```bash
cd tests/test_cascading_css
python test_cascading_themes.py
```

### Option 2: Using the runner
```bash
cd tests/test_cascading_css
python run_test.py
```

## Controls

- **Ctrl+Shift+T**: Cycle through themes (Dark → Light → Colorful → Dark...)
- **UI Elements**: Interact with buttons, tree items, and input fields to see how themes affect them
- **Theme Log**: Watch the theme change log in the bottom panel

## What You'll See

1. **Dark Theme**: VS Code Dark+ inspired colors with dark backgrounds
2. **Light Theme**: Clean light theme with blue accents
3. **Colorful Theme**: Vibrant gradients and colorful UI elements

## Benefits of This Approach

✅ **Maintainable**: Common styles in one place  
✅ **Efficient**: Only override colors, not entire stylesheets  
✅ **Consistent**: Shared base ensures UI consistency  
✅ **Flexible**: Easy to add new themes  
✅ **DRY**: No duplication of layout/typography rules  

## Key Learning Points

1. **Qt CSS Cascading**: Later styles override earlier ones, just like web CSS
2. **Theme Architecture**: Separate common styles from theme-specific colors
3. **Efficient Theming**: Only override what's different between themes
4. **Dynamic Styling**: Themes can be switched at runtime
5. **Maintainability**: Changes to common styles apply to all themes

## CSS Examples

### Common Base Style
```css
QPushButton {
    border: 2px solid;
    padding: 8px 16px;
    border-radius: 6px;
    min-width: 80px;
}
```

### Dark Theme Override
```css
QPushButton {
    background-color: #0e639c;
    border-color: #007acc;
    color: #ffffff;
}
```

### Light Theme Override  
```css
QPushButton {
    background-color: #f3f3f3;
    border-color: #cccccc;
    color: #000000;
}
```

The result is three completely different looking themes that share the same base layout and typography rules.

## Integration with Your POEditor Project

This same approach can be used in your POEditor application:

1. Create a `themes/` directory with `common.css` and theme files
2. Use a `ThemeManager` class to load and combine CSS
3. Apply themes dynamically with `app.setStyleSheet(combined_css)`
4. Switch themes based on user preferences or system settings

This is much more maintainable than having separate complete CSS files for each theme!
