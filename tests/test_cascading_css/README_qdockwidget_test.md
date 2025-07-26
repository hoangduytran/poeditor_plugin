# QDockWidget Title Bar Customization Test

This comprehensive test demonstrates the full range of QDockWidget title bar customization possibilities, from basic CSS styling to completely custom title bar widgets with advanced functionality.

## Test Components

### 1. CSS-Styled Native Title Bar (Left Dock)
- Uses the native QDockWidget title bar
- Styled with CSS selectors for:
  - `QDockWidget::title` - Title bar background, text, padding
  - `QDockWidget::float-button` - Float button styling and hover effects
  - `QDockWidget::close-button` - Close button styling
- Maintains full native Qt functionality
- Theme-aware styling

### 2. Custom Title Bar Widget (Right Dock)
- Completely replaces the native title bar with a custom QFrame
- Features:
  - Custom title label with themed styling
  - Settings button (⚙) 
  - Float/dock toggle button (⚏/⊞) - changes icon based on state
  - Close button (✕)
  - Drag support for moving floating windows
  - Full CSS theming support

### 3. Advanced Custom Title Bar (Bottom Dock)
- Enhanced custom title bar with rich functionality
- Features:
  - Status indicator (colored dot) with dynamic updates
  - Item count display with live updates
  - Refresh button (↻) with status feedback
  - Settings button (⚙) with status change
  - Float/dock button (⚏)
  - Compact, professional design

## Controls

- **Ctrl+Shift+T**: Cycle through themes (Dark → Light → Colorful → Dark...)
- **Drag title bars**: Move dock widgets around
- **Float buttons**: Toggle docking/floating state
- **Settings buttons**: Trigger settings actions with visual feedback
- **Refresh button**: Update content with status indicators
- **Close button**: Close dock widgets (custom title bar only)

## CSS Customization Examples

### Native Title Bar Styling
```css
QDockWidget::title {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 8px 12px;
    font-weight: bold;
}

QDockWidget::float-button:hover {
    background-color: #007acc;
    border-color: #0099ff;
}
```

### Custom Widget Styling
```css
.CustomTitleBar {
    background-color: #2d2d30;
    border-bottom: 1px solid #464647;
}

.TitleButton:hover {
    background-color: #007acc;
    color: #ffffff;
}
```

## Theme Integration

The test uses the same CSS cascading system as other tests:
- `common.css` - Base styles
- `dark.css`, `light.css`, `colorful.css` - Theme-specific overrides
- Dynamic theme switching shows how title bars adapt

## Key Learning Points

1. **Native vs Custom Trade-offs**:
   - Native: Simpler, maintains Qt behavior, limited customization
   - Custom: Complete control, more complex, need to implement functionality

2. **CSS Capabilities**:
   - Can style native title bar components
   - Limited to appearance, not functionality
   - Theme integration works well

3. **Custom Widget Benefits**:
   - Add any controls you want
   - Implement custom functionality
   - Full design freedom
   - Responsive to application state

4. **Advanced Features**:
   - Status indicators
   - Dynamic content updates
   - Multiple action buttons
   - Professional UI patterns

## Usage

Run the test with:

```bash
# From the test_cascading_css directory
python3 test_qdockwidget_title_bars.py

# Or use the run script
python3 run_qdockwidget_test.py
```

## Implementation Tips

1. **For Basic Styling**: Use CSS on native title bars
2. **For Custom Functionality**: Use `setTitleBarWidget()` with custom widgets
3. **For Professional Apps**: Implement advanced title bars with status indicators
4. **For Theme Support**: Use CSS classes and object names for consistent styling
5. **For Dragging**: Implement mouse events in custom title bars
6. **For State Management**: Connect to dock widget signals like `topLevelChanged`

This test provides a complete reference for QDockWidget title bar customization, showing you exactly how far you can push the customization while maintaining professional appearance and functionality.
