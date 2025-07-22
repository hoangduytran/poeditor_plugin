# Main Window Layout Fix Design
**Date**: July 16, 2025  
**Status**: Design Phase  
**Priority**: High  

## Problem Analysis

### Current Issues
1. **Activity Bar Positioning**: Activity bar appears in the middle instead of being fixed on the left
2. **Sidebar Docking**: Sidebar cannot be properly docked left/right - menu dropdown callbacks don't work
3. **Drag and Drop**: Cannot drag sidebar to different dock areas
4. **Layout Structure**: Activity bar and main window are not properly integrated as one concrete component

### Root Cause
The current design treats the activity bar as a separate dockable widget instead of an integral part of the main window layout. This causes:
- Incorrect positioning and sizing
- Broken docking mechanics
- Poor user experience

## New Design Solution

### Core Principle
**Activity Bar + Main Window = One Concrete Component**
- Activity bar is fixed on the left side of the main window
- Only the area to the right of the activity bar is dockable
- Sidebar can dock left/right within the available dockable area

### Layout Structure
```
+------------------------------------------------------------+
| Menu Bar                                                   |
+------------------------------------------------------------+
| [AB] | [Dockable Area for Sidebar and Editor]            |
| [AB] |                                                    |
| [AB] | +------------------+  +----------------------+    |
| [AB] | | Sidebar Panel    |  | Editor/Tab Area      |    |
| [AB] | | (Dockable L/R)   |  | (Main Content)       |    |
| [AB] | |                  |  |                      |    |
| [AB] | +------------------+  +----------------------+    |
+------------------------------------------------------------+
| Status Bar                                                 |
+------------------------------------------------------------+

AB = Activity Bar (Fixed, Non-dockable)
```

### Key Changes Required

#### 1. Main Window Layout Redesign
- Create a fixed left panel for the activity bar
- Create a main dockable area for sidebar and content
- Remove activity bar from dock widget system

#### 2. Activity Bar Integration
- Make activity bar a permanent child widget of main window
- Position it in a fixed left area
- Remove all docking capabilities from activity bar

#### 3. Sidebar Docking Area
- Create dedicated docking area to the right of activity bar
- Implement proper dock widget areas (left/right of content area)
- Fix docking callbacks and drag-and-drop functionality

#### 4. Layout Management
```python
# New layout structure
main_window:
  ├── menu_bar (QMenuBar)
  ├── central_widget (QWidget)
  │   ├── horizontal_layout (QHBoxLayout)
  │   │   ├── activity_bar (ActivityBar) [Fixed width: 48px]
  │   │   └── dock_area_widget (QWidget) [Expandable]
  │   │       └── Contains dockable sidebar and editor area
  └── status_bar (QStatusBar)
```

## Implementation Plan

### Phase 1: Layout Restructure
1. **Remove activity bar from dock system**
   - Update `main_app_window.py` layout setup
   - Remove `ActivityBarDockWidget` dependencies
   - Make activity bar a direct child of main window

2. **Create dedicated dock area**
   - Implement proper QMainWindow dock areas
   - Configure left/right docking for sidebar only
   - Ensure activity bar area is excluded from docking

### Phase 2: Sidebar Docking Fix
1. **Fix docking callbacks**
   - Implement proper dock area change handlers
   - Fix dropdown menu functionality
   - Enable drag-and-drop between dock areas

2. **Test docking functionality**
   - Verify left/right docking works
   - Test drag-and-drop operations
   - Validate menu callbacks

### Phase 3: Integration and Testing
1. **Component integration**
   - Ensure activity bar and sidebar work together
   - Test activity button functionality
   - Verify panel switching

2. **UI/UX validation**
   - Confirm activity bar stays fixed on left
   - Test sidebar docking in all scenarios
   - Validate overall layout behavior

## Technical Implementation Details

### Main Window Structure
```python
class MainAppWindow(QMainWindow):
    def setup_main_layout(self):
        # Central widget with horizontal layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Fixed activity bar on the left
        self.activity_bar = ActivityBar()
        self.activity_bar.setFixedWidth(48)
        main_layout.addWidget(self.activity_bar)
        
        # Dockable area widget
        self.dock_area_widget = QWidget()
        main_layout.addWidget(self.dock_area_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Setup dock areas within dock_area_widget
        self.setup_dock_areas()
```

### Dock Area Configuration
```python
def setup_dock_areas(self):
    # Create inner main window for docking within dock_area_widget
    self.inner_main_window = QMainWindow()
    
    # Create sidebar dock widget
    self.sidebar_dock = SidebarDockWidget(self.sidebar_manager)
    
    # Add to left dock area by default
    self.inner_main_window.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar_dock)
    
    # Create editor area as central widget
    self.inner_main_window.setCentralWidget(self.tab_manager)
    
    # Add inner main window to dock area
    dock_layout = QVBoxLayout(self.dock_area_widget)
    dock_layout.setContentsMargins(0, 0, 0, 0)
    dock_layout.addWidget(self.inner_main_window)
```

## Expected Outcomes

### Fixed Issues
- ✅ Activity bar will be properly positioned on the left
- ✅ Sidebar will dock correctly left/right of content area
- ✅ Drag-and-drop docking will work properly
- ✅ Menu dropdown callbacks will function correctly
- ✅ Layout will be stable and predictable

### User Experience
- Fixed activity bar provides consistent navigation
- Sidebar can be docked left or right of content
- Smooth drag-and-drop docking experience
- Proper visual feedback during docking operations

## Validation Criteria
1. Activity bar remains fixed on far left of window
2. Sidebar can be docked left/right of editor area
3. Drag-and-drop docking works smoothly
4. Menu callbacks for dock position changes work
5. Layout remains stable during window resize
6. All existing functionality is preserved

## Risk Assessment
- **Low Risk**: Changes are contained to layout structure
- **Minimal Impact**: Core functionality remains unchanged
- **Easy Rollback**: Changes can be reverted if needed

## Next Steps
1. Review and approve this design
2. Implement Phase 1 changes
3. Test layout restructure
4. Implement Phase 2 docking fixes
5. Validate complete solution
