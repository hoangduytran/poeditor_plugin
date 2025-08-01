# SVG Icons

Place SVG icon files in this directory to be processed by the IconManager.

## Naming Conventions

- Use lowercase names with underscores (e.g., `file_explorer.svg`)
- Use descriptive names that indicate the icon's purpose
- For state-specific icons, use suffixes like `_active`, `_inactive`

## Icon Requirements

- SVG files should be optimized and cleaned
- Keep icons simple and recognizable
- Use viewBox attribute to ensure proper scaling
- For monochrome icons, use black (#000000) as the fill color

## Icon Generation

To generate the icon CSS file:

```python
from services.icon_manager import IconManager

icon_mgr = IconManager()
icon_mgr.generate_icons_css()
```

This will process all SVG files and create CSS classes with format `.icon-{name}` that can be used in your application.
