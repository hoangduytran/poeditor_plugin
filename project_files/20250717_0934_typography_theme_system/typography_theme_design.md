# Typography and Theme System Design

**Date**: July 17, 2025  
**Version**: 1.0  
**Authors**: Development Team  

## Overview

This document outlines the design and architecture of the centralized typography and theme management system for the PySide POEditor plugin. The system provides consistent font management, theme support, and user customization capabilities across the entire application.

## Problem Statement

### Current Issues
- **Inconsistent Typography**: Font sizes and families scattered across components
- **Hard-coded Styling**: Direct font specifications in individual widgets
- **No Theme Support**: Lack of centralized theme management
- **Poor Accessibility**: No support for font scaling or user preferences
- **Maintenance Burden**: Changes require updates in multiple files

### Requirements
1. **Centralized Font Management**: Single source of truth for typography
2. **Semantic Font Roles**: Use purpose-based font roles instead of hardcoded sizes
3. **Theme Integration**: Typography that adapts to different visual themes
4. **User Customization**: Allow users to adjust font family, size, and scale
5. **Accessibility Support**: Built-in scaling for accessibility needs
6. **Hot Reloading**: Dynamic font updates without restart

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  Main Window  │  Explorer Panel  │  Search Panel  │  Widgets   │
├─────────────────────────────────────────────────────────────────┤
│                      Theme Manager                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Light Theme   │  │   Dark Theme    │  │ High Contrast   │ │
│  │   - Colors      │  │   - Colors      │  │   - Colors      │ │
│  │   - Typography  │  │   - Typography  │  │   - Typography  │ │
│  │   - Components  │  │   - Components  │  │   - Components  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Typography Manager                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Font Role System                            │ │
│  │  HEADING_1 │ HEADING_2 │ BODY │ CODE │ BUTTON │ SMALL     │ │
│  │  20px Bold │ 16px Bold │ 13px │ 12px │ 12px   │ 11px      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Font Configuration                             │ │
│  │  Base Family: Inter, Segoe UI, Arial                       │ │
│  │  Base Size: 13px                                           │ │
│  │  Scale Factor: 1.0 (for accessibility)                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                        PySide6 Layer                            │
│              QFont │ QApplication │ QStyleSheet                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Typography Manager (`themes/typography.py`)

#### Core Responsibilities
- **Font Role Management**: Define and manage semantic font roles
- **Font Generation**: Create QFont instances based on roles and configuration
- **Global Application**: Apply typography to entire QApplication
- **Change Notification**: Signal font changes to listening components
- **Settings Persistence**: Save/load user typography preferences

#### Font Role System
```python
class FontRole(Enum):
    DEFAULT = "default"      # 13px, Normal - Base application font
    HEADING_1 = "heading_1"  # 20px, Bold - Main titles
    HEADING_2 = "heading_2"  # 16px, Bold - Section headers
    HEADING_3 = "heading_3"  # 14px, DemiBold - Sub-section headers
    BODY = "body"           # 13px, Normal - Regular text content
    SMALL = "small"         # 11px, Normal - Secondary information
    CAPTION = "caption"     # 10px, Normal - Image captions, metadata
    CODE = "code"           # 12px, Normal, Monospace - Code snippets
    BUTTON = "button"       # 12px, Medium - Button text
    MENU = "menu"           # 12px, Normal - Menu items
    TOOLTIP = "tooltip"     # 11px, Normal - Tooltip text
    TITLE = "title"         # 11px, Bold - Panel titles
    SUBTITLE = "subtitle"   # 10px, Normal - Panel subtitles
```

#### Typography Scale Configuration
```python
{
    FontRole.DEFAULT: {
        "family": "Inter, Segoe UI, Arial, sans-serif",
        "size": 13,
        "weight": QFont.Normal
    },
    FontRole.HEADING_1: {
        "family": "Inter, Segoe UI, Arial, sans-serif", 
        "size": 20,
        "weight": QFont.Bold
    },
    FontRole.CODE: {
        "family": "JetBrains Mono, Consolas, Monaco, monospace",
        "size": 12,
        "weight": QFont.Normal
    }
    # ... other roles
}
```

### 2. Theme Manager (`themes/theme_manager.py`)

#### Core Responsibilities
- **Theme Loading**: Load and manage multiple visual themes
- **Component Styling**: Generate component-specific stylesheets
- **Typography Integration**: Coordinate with typography manager
- **Theme Switching**: Support runtime theme changes
- **Custom Themes**: Support user-defined custom themes

#### Theme Structure
```json
{
  "name": "Light Theme",
  "typography": {
    "base_font_family": "Inter, Segoe UI, Arial, sans-serif",
    "base_font_size": 13,
    "scale_factor": 1.0
  },
  "colors": {
    "background": "#ffffff",
    "foreground": "#333333",
    "accent": "#007acc",
    "border": "#e5e5e5"
  },
  "styles": {
    "panel_title": {
      "background": "#f8f8f8",
      "color": "#333333",
      "font_role": "title"
    },
    "button": {
      "background": "#f8f8f8",
      "border": "#cccccc",
      "font_role": "button"
    }
  }
}
```

## Usage Patterns

### 1. Component Implementation Pattern

```python
class ExampleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.typography_manager = get_typography_manager()
        self.theme_manager = get_theme_manager()
        
        self._setup_ui()
        self._apply_theme()
        self._connect_signals()
    
    def _apply_theme(self):
        """Apply current theme to all components."""
        # Method 1: Direct font application
        self.title_label.setFont(get_font(FontRole.HEADING_1))
        self.body_text.setFont(get_font(FontRole.BODY))
        
        # Method 2: Complete component styling
        search_style = self.theme_manager.get_style_for_component("search_input")
        self.search_input.setStyleSheet(f"QLineEdit {{ {search_style} }}")
    
    def _connect_signals(self):
        """Connect to theme/font change signals."""
        self.typography_manager.fonts_changed.connect(self._apply_theme)
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
```

### 2. Stylesheet Generation Pattern

```python
# Component-specific stylesheet with typography integration
def get_explorer_stylesheet() -> str:
    theme_manager = get_theme_manager()
    
    return f"""
    QLabel#panel_title {{
        {theme_manager.get_style_for_component("panel_title")}
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    QLineEdit {{
        {theme_manager.get_style_for_component("search_input")}
        border-radius: 3px;
        padding: 4px 6px;
    }}
    """
```

## Built-in Themes

### 1. Light Theme
- **Background**: #ffffff (white)
- **Text**: #333333 (dark gray)
- **Accent**: #007acc (VS Code blue)
- **Typography**: Standard scale with 13px base size

### 2. Dark Theme  
- **Background**: #1e1e1e (VS Code dark background)
- **Text**: #cccccc (light gray)
- **Accent**: #0078d4 (adjusted blue for dark mode)
- **Typography**: Standard scale with 13px base size

### 3. High Contrast Theme
- **Background**: #000000 (black)
- **Text**: #ffffff (white)
- **Accent**: #ffff00 (yellow for high visibility)
- **Typography**: Larger scale with 14px base size and 1.1x scale factor

## User Customization

### Font Preferences Interface
```python
class FontPreferencesWidget:
    # Font Family Selection
    font_families = [
        "Inter, Segoe UI, Arial, sans-serif",
        "SF Pro Display, system-ui, sans-serif", 
        "Roboto, Arial, sans-serif",
        "Ubuntu, Arial, sans-serif"
    ]
    
    # Font Size Range: 8px - 24px
    # Scale Factor Range: 0.5x - 2.0x (50% - 200%)
```

### Settings Persistence
```python
# Settings stored in user preferences
{
    "typography.base_font_family": "Inter, Segoe UI, Arial, sans-serif",
    "typography.base_font_size": 13,
    "typography.scale_factor": 1.0,
    "theme.current": "light"
}
```

## Integration Points

### 1. Application Startup
```python
def setup_application_typography():
    theme_manager = get_theme_manager()
    typography_manager = get_typography_manager()
    
    # Load user preferences
    typography_manager.load_from_settings(settings_service)
    
    # Apply default theme
    theme_manager.set_theme("light")
    
    # Apply to entire application
    typography_manager.apply_to_application()
```

### 2. Existing Component Updates

#### Explorer Panel Integration
- **Panel Title**: Use `FontRole.TITLE` instead of hardcoded styles
- **File Names**: Use `FontRole.BODY` for consistent text
- **Search Input**: Apply theme-based styling with `FontRole.BODY`
- **Buttons**: Use `FontRole.BUTTON` for all action buttons

#### Advanced Search Widget Integration
- **Input Fields**: `FontRole.BODY` with theme colors
- **Option Labels**: `FontRole.SMALL` for compact display
- **Buttons**: `FontRole.BUTTON` with hover states

## Accessibility Features

### 1. Font Scaling
- **Scale Factor**: 0.5x to 2.0x multiplier for all fonts
- **Proportional Scaling**: All font sizes scale together
- **Real-time Updates**: Changes apply immediately without restart

### 2. High Contrast Support
- **Dedicated Theme**: High contrast theme with maximum visibility
- **Larger Base Size**: 14px instead of 13px for better readability
- **Enhanced Scale**: 1.1x default scale factor

### 3. Font Family Support
- **System Fonts**: Support for platform-specific fonts
- **Fallback Chain**: Graceful fallback to available fonts
- **Monospace Code**: Dedicated monospace fonts for code display

## Benefits

### 1. Consistency
- **Uniform Typography**: All text follows the same scale
- **Semantic Roles**: Clear purpose for each font usage
- **Theme Coherence**: Typography matches visual theme

### 2. Maintainability  
- **Single Source**: One place to change font configurations
- **Component Isolation**: Changes don't break existing components
- **Theme Updates**: Easy to add new themes

### 3. User Experience
- **Customization**: Users can adjust fonts to their preference
- **Accessibility**: Built-in support for users with visual needs
- **Performance**: Fonts cached and reused efficiently

### 4. Developer Experience
- **Clear API**: Simple `get_font(FontRole.BODY)` usage
- **Hot Reloading**: Changes apply immediately
- **Type Safety**: Enum-based font roles prevent typos

## Migration Strategy

### Phase 1: Core System Setup
1. Implement `typography.py` and `theme_manager.py`
2. Create built-in themes (Light, Dark, High Contrast)
3. Add global typography application

### Phase 2: Component Integration
1. Update Explorer Panel to use font roles
2. Integrate Advanced Search Widget
3. Apply to remaining panels (Search, Account, Extensions, Preferences)

### Phase 3: User Preferences
1. Add font preferences UI
2. Implement settings persistence
3. Add theme switching interface

### Phase 4: Advanced Features
1. Custom theme support
2. Font preview capabilities
3. Import/export theme functionality

## Testing Considerations

### Unit Tests
- Font role enumeration completeness
- Typography scaling calculations
- Theme loading and validation
- Settings persistence

### Integration Tests  
- Component font application
- Theme switching functionality
- User preference changes
- Accessibility scaling

### Visual Tests
- Font rendering across themes
- Scale factor validation
- Component layout with different font sizes
- Theme consistency verification

## Future Enhancements

### 1. Advanced Typography
- **Font Weight Variants**: Support for more font weights
- **Line Height Control**: Configurable line spacing
- **Font Loading**: Dynamic font loading from files

### 2. Theme System Expansion
- **Color Customization**: User-configurable color palettes
- **Component Variants**: Multiple styles per component type
- **Animation Support**: Smooth theme transitions

### 3. Developer Tools
- **Theme Editor**: Visual theme creation tool
- **Typography Inspector**: Debug font usage in components
- **Style Guide**: Generated documentation of typography scale

## Conclusion

The typography and theme system provides a robust foundation for consistent, accessible, and maintainable text styling throughout the PySide POEditor plugin. By using semantic font roles and centralized theme management, the system eliminates hardcoded styling while providing extensive customization capabilities for both developers and users.

The modular architecture ensures easy integration with existing components and provides clear patterns for future development. The built-in accessibility features and user customization options make the application more inclusive and user-friendly.
