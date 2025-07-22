# Theme System Configuration Reference

**Date**: July 17, 2025  
**Version**: 1.0  
**Type**: Configuration Reference  
**Dependencies**: typography_theme_design.md  

## Theme JSON Schema

### Complete Theme Structure
```json
{
  "$schema": "https://poeditor-plugin/theme-schema.json",
  "name": "Theme Display Name",
  "version": "1.0",
  "author": "Theme Author",
  "description": "Theme description",
  "typography": {
    "base_font_family": "Inter, Segoe UI, Arial, sans-serif",
    "base_font_size": 13,
    "scale_factor": 1.0,
    "roles": {
      "heading_1": {
        "family": "Inter, Segoe UI, Arial, sans-serif",
        "size": 20,
        "weight": 700
      },
      "code": {
        "family": "JetBrains Mono, Consolas, Monaco, monospace",
        "size": 12,
        "weight": 400
      }
    }
  },
  "colors": {
    "primary": "#007acc",
    "secondary": "#6c757d",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "background": "#ffffff",
    "surface": "#f8f9fa",
    "text_primary": "#333333",
    "text_secondary": "#6c757d",
    "text_muted": "#999999",
    "border": "#e5e5e5",
    "focus": "#007acc",
    "hover": "#e8e8e8",
    "active": "#d6d6d6",
    "disabled": "#f0f0f0"
  },
  "components": {
    "panel_title": {
      "background": "$surface",
      "color": "$text_primary",
      "font_role": "title",
      "border_bottom": "1px solid $border",
      "padding": "8px 12px",
      "text_transform": "uppercase",
      "letter_spacing": "0.5px"
    },
    "button_primary": {
      "background": "$primary",
      "color": "#ffffff",
      "font_role": "button",
      "border": "1px solid $primary",
      "border_radius": "4px",
      "padding": "8px 16px"
    },
    "button_secondary": {
      "background": "transparent",
      "color": "$primary",
      "font_role": "button",
      "border": "1px solid $primary",
      "border_radius": "4px",
      "padding": "8px 16px"
    },
    "input_field": {
      "background": "$background",
      "color": "$text_primary",
      "font_role": "body",
      "border": "1px solid $border",
      "border_radius": "4px",
      "padding": "8px 12px"
    },
    "search_input": {
      "background": "$background",
      "color": "$text_primary",
      "font_role": "body",
      "border": "1px solid $border",
      "border_radius": "3px",
      "padding": "4px 6px"
    },
    "tree_view": {
      "background": "$background",
      "color": "$text_primary",
      "font_role": "body",
      "selection_background": "$primary",
      "selection_color": "#ffffff",
      "alternate_background": "$surface"
    },
    "tooltip": {
      "background": "#333333",
      "color": "#ffffff",
      "font_role": "tooltip",
      "border": "none",
      "border_radius": "4px",
      "padding": "4px 8px"
    },
    "context_menu": {
      "background": "$background",
      "color": "$text_primary",
      "font_role": "menu",
      "border": "1px solid $border",
      "border_radius": "4px",
      "item_padding": "8px 12px"
    }
  }
}
```

## Built-in Theme Configurations

### 1. Light Theme (Default)
```json
{
  "name": "Light",
  "typography": {
    "base_font_family": "Inter, Segoe UI, Arial, sans-serif",
    "base_font_size": 13,
    "scale_factor": 1.0
  },
  "colors": {
    "primary": "#007acc",
    "background": "#ffffff",
    "surface": "#f8f9fa",
    "text_primary": "#333333",
    "text_secondary": "#6c757d",
    "border": "#e5e5e5",
    "hover": "#e8e8e8",
    "focus": "#007acc"
  }
}
```

### 2. Dark Theme
```json
{
  "name": "Dark",
  "typography": {
    "base_font_family": "Inter, Segoe UI, Arial, sans-serif",
    "base_font_size": 13,
    "scale_factor": 1.0
  },
  "colors": {
    "primary": "#0078d4",
    "background": "#1e1e1e",
    "surface": "#2d2d30",
    "text_primary": "#cccccc",
    "text_secondary": "#999999",
    "border": "#464647",
    "hover": "#3e3e42",
    "focus": "#0078d4"
  }
}
```

### 3. High Contrast Theme
```json
{
  "name": "High Contrast",
  "typography": {
    "base_font_family": "Inter, Segoe UI, Arial, sans-serif",
    "base_font_size": 14,
    "scale_factor": 1.1
  },
  "colors": {
    "primary": "#ffff00",
    "background": "#000000",
    "surface": "#000000",
    "text_primary": "#ffffff",
    "text_secondary": "#ffffff",
    "border": "#ffffff",
    "hover": "#333333",
    "focus": "#ffff00"
  },
  "components": {
    "button_primary": {
      "border": "2px solid $border"
    },
    "input_field": {
      "border": "2px solid $border"
    }
  }
}
```

## Component Style Reference

### Panel Components
```css
/* Panel Title */
.panel_title {
  background: $surface;
  color: $text_primary;
  font: FontRole.TITLE;
  border-bottom: 1px solid $border;
  padding: 8px 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Panel Container */
.panel_container {
  background: $background;
  color: $text_primary;
  border: 1px solid $border;
}
```

### Button Components
```css
/* Primary Button */
.button_primary {
  background: $primary;
  color: #ffffff;
  font: FontRole.BUTTON;
  border: 1px solid $primary;
  border-radius: 4px;
  padding: 8px 16px;
}

.button_primary:hover {
  background: lighten($primary, 10%);
}

.button_primary:pressed {
  background: darken($primary, 10%);
}

/* Secondary Button */
.button_secondary {
  background: transparent;
  color: $primary;
  font: FontRole.BUTTON;
  border: 1px solid $primary;
  border-radius: 4px;
  padding: 8px 16px;
}

/* Navigation Button */
.navigation_button {
  background: $surface;
  color: $text_primary;
  font: FontRole.BUTTON;
  border: 1px solid $border;
  border-radius: 3px;
  padding: 4px 8px;
}
```

### Input Components
```css
/* Text Input */
.input_field {
  background: $background;
  color: $text_primary;
  font: FontRole.BODY;
  border: 1px solid $border;
  border-radius: 4px;
  padding: 8px 12px;
}

.input_field:focus {
  border-color: $focus;
  outline: none;
}

/* Search Input */
.search_input {
  background: $background;
  color: $text_primary;
  font: FontRole.BODY;
  border: 1px solid $border;
  border-radius: 3px;
  padding: 4px 6px;
}

/* Checkbox */
.checkbox {
  color: $text_primary;
  font: FontRole.SMALL;
}

/* Combo Box */
.combo_box {
  background: $background;
  color: $text_primary;
  font: FontRole.BODY;
  border: 1px solid $border;
  border-radius: 3px;
  padding: 4px 8px;
}
```

### Tree and List Components
```css
/* Tree View */
.tree_view {
  background: $background;
  color: $text_primary;
  font: FontRole.BODY;
  border: 1px solid $border;
  selection-background-color: $primary;
  selection-color: #ffffff;
  alternate-background-color: $surface;
}

/* List Widget */
.list_widget {
  background: $background;
  color: $text_primary;
  font: FontRole.BODY;
  border: 1px solid $border;
}

/* Table Header */
.table_header {
  background: $surface;
  color: $text_secondary;
  font: FontRole.CAPTION;
  border-bottom: 1px solid $border;
  padding: 4px 8px;
}
```

### Menu and Tooltip Components
```css
/* Context Menu */
.context_menu {
  background: $background;
  color: $text_primary;
  font: FontRole.MENU;
  border: 1px solid $border;
  border-radius: 4px;
}

.context_menu_item {
  padding: 8px 12px;
}

.context_menu_item:hover {
  background: $hover;
}

/* Tooltip */
.tooltip {
  background: #333333;
  color: #ffffff;
  font: FontRole.TOOLTIP;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
}

/* Menu Bar */
.menu_bar {
  background: $surface;
  color: $text_primary;
  font: FontRole.MENU;
  border-bottom: 1px solid $border;
}
```

## Usage Examples

### 1. Applying Component Styles
```python
# Using theme manager for complete styling
theme_manager = get_theme_manager()
button_style = theme_manager.get_style_for_component("button_primary")
self.save_button.setStyleSheet(f"QPushButton {{ {button_style} }}")

# Combining with custom properties
search_style = theme_manager.get_style_for_component("search_input")
custom_style = f"""
QLineEdit {{
    {search_style}
    placeholder-text-color: {theme_manager.get_color('text_secondary')};
}}
"""
self.search_input.setStyleSheet(custom_style)
```

### 2. Creating Custom Component Styles
```python
def create_custom_button_style(theme_manager, variant="primary"):
    """Create custom button style with theme colors."""
    base_style = theme_manager.get_style_for_component(f"button_{variant}")
    
    return f"""
    QPushButton {{
        {base_style}
        min-width: 80px;
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background-color: {theme_manager.get_color('hover')};
    }}
    
    QPushButton:pressed {{
        background-color: {theme_manager.get_color('active')};
    }}
    
    QPushButton:disabled {{
        background-color: {theme_manager.get_color('disabled')};
        color: {theme_manager.get_color('text_muted')};
    }}
    """
```

### 3. Theme Color Interpolation
```python
def get_hover_color(base_color, factor=0.1):
    """Generate hover color by lightening/darkening base color."""
    # Implementation would depend on color manipulation library
    pass

def apply_interactive_states(component, theme_manager):
    """Apply hover/active states to interactive components."""
    primary_color = theme_manager.get_color('primary')
    hover_color = get_hover_color(primary_color, 0.1)
    active_color = get_hover_color(primary_color, -0.1)
    
    style = f"""
    {component.styleSheet()}
    
    :hover {{ background-color: {hover_color}; }}
    :pressed {{ background-color: {active_color}; }}
    """
    
    component.setStyleSheet(style)
```

## Custom Theme Creation Guide

### 1. Theme File Structure
```
custom_theme/
├── theme.json          # Main theme configuration
├── preview.png         # Theme preview image
├── readme.md          # Theme documentation
└── assets/            # Optional custom assets
    ├── icons/
    └── fonts/
```

### 2. Color Palette Guidelines
- **Primary**: Main brand/accent color
- **Background**: Main content background
- **Surface**: Elevated surface color (panels, cards)
- **Text Primary**: Main text color
- **Text Secondary**: Secondary text color
- **Border**: Default border color
- **Focus**: Focus indicator color
- **Hover/Active**: Interactive state colors

### 3. Typography Customization
```json
{
  "typography": {
    "roles": {
      "heading_1": {
        "family": "Custom Font Family",
        "size": 22,
        "weight": 700,
        "line_height": 1.2
      }
    }
  }
}
```

### 4. Component Override Patterns
```json
{
  "components": {
    "custom_component": {
      "extends": "button_primary",
      "modifications": {
        "border_radius": "8px",
        "padding": "12px 24px"
      }
    }
  }
}
```

This configuration reference provides the complete schema and examples for creating and customizing themes in the typography system, enabling both built-in theme usage and custom theme development.
