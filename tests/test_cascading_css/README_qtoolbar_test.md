# QToolBar CSS Theme Test

This test demonstrates how QToolBar and QPushButton styling looks across different themes using CSS cascading.

## Features

The test creates a window with three different QToolBar configurations:

1. **Main Toolbar** - Primary actions with text and icons (New, Open, Save, Exit)
2. **Secondary Toolbar** - Utility actions with icons only (Undo, Redo, Copy, Paste) 
3. **Text-Only Toolbar** - Text buttons without icons (Bold, Italic, Underline, Settings)

## Controls

- **Ctrl+Shift+T**: Cycle through themes (Dark → Light → Colorful → Dark...)
- **Exit Button**: Click to close the application
- **Other Buttons**: Click any toolbar button to see action logging

## Usage

Run the test with:

```bash
# From the test_cascading_css directory
python3 test_qtoolbar_themes.py

# Or use the run script
python3 run_qtoolbar_test.py
```

## What to Observe

When cycling through themes, observe how:

- **QToolBar background** changes to match the theme
- **QPushButton colors** adapt to each theme's color scheme
- **Button hover effects** change with theme colors
- **Text colors** adjust for readability in each theme
- **Separators and borders** follow the theme styling

## CSS Files Used

The test uses the cascading CSS files:

- `css/common.css` - Base styles shared across all themes
- `css/dark.css` - Dark theme overrides
- `css/light.css` - Light theme overrides  
- `css/colorful.css` - Colorful theme overrides

## Purpose

This test helps you:

1. Validate QToolBar styling across themes
2. See how CSS cascading works with Qt widgets
3. Test button visual consistency
4. Debug theme-specific QToolBar issues
5. Compare how different QToolBar configurations look

The test is particularly useful for ensuring QToolBar buttons remain visually consistent and readable across all theme variations.
