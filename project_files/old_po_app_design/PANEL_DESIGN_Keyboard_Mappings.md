# Keyboard Mappings Panel - Design Specification

## Overview
The Keyboard Mappings panel provides comprehensive customization of keyboard shortcuts throughout the PO Editor application. This centralized interface allows users to view, modify, and organize all keyboard shortcuts in a hierarchical, easy-to-navigate format.

## Design Purpose
- **Accessibility**: Enable users to customize shortcuts for their physical abilities and preferences
- **Workflow Optimization**: Allow power users to create efficient keyboard-driven workflows
- **Conflict Resolution**: Prevent and resolve keyboard shortcut conflicts
- **Consistency**: Maintain organized, logical grouping of related shortcuts
- **Discoverability**: Make all available shortcuts visible and learnable

## Component Structure

### Tree-based Organization

#### Hierarchical Display
**Purpose**: Organize shortcuts into logical categories for easy navigation and understanding.

**Features**:
- **Expandable Tree Structure**: Top-level categories with child items
- **Two-column Layout**: "Action" and "Shortcut" columns
- **Equal Column Sizing**: 50/50 split with stretch headers
- **Auto-expansion**: All categories expanded by default for full visibility

**Design Rationale**: 
- Tree structure mirrors application menu organization
- Hierarchical grouping reduces cognitive load
- Consistent column sizing ensures readability
- Expanded view provides complete overview of shortcuts

### Shortcut Categories

#### 1. File Menu Category
**Purpose**: Shortcuts for file operations and application-level commands.

**Actions Included**:
- **Open File** (`Ctrl+O`) - Load PO files
- **Save File** (`Ctrl+S`) - Save current work
- **Save As** (`Ctrl+Shift+S`) - Save with new name/location
- **Preferences** (`Ctrl+,`) - Open settings dialog
- **Exit** (`Ctrl+Q`) - Close application

**Design Rationale**: 
- Standard file operations users expect
- Platform-consistent shortcuts (Ctrl on Windows/Linux, Cmd on Mac)
- Logical progression from open → save → exit

#### 2. Table Category
**Purpose**: Navigation and selection shortcuts for the main translation table.

**Actions Included**:
- **Previous Page** (`PageUp`) - Navigate to previous page of entries
- **Next Page** (`PageDown`) - Navigate to next page of entries
- **First Row** (`Home`) - Jump to beginning of table
- **Last Row** (`End`) - Jump to end of table
- **Select (Shift+Up)** (`Shift+Up`) - Extend selection upward
- **Select (Shift+Down)** (`Shift+Down`) - Extend selection downward
- **Select (Ctrl+Click)** (`Ctrl+Shift`) - Multi-select modifier

**Design Rationale**: 
- Table navigation is core to translation workflow
- Standard navigation keys (Home, End, Page Up/Down)
- Selection modifiers follow platform conventions
- Multi-select support for batch operations

#### 3. Sort Category
**Purpose**: Quick access shortcuts for different sorting options.

**Actions Included**:
- **Untranslated Items** (`Ctrl+0`) - Show untranslated entries first
- **Fuzzy Items** (`Ctrl+1`) - Show fuzzy entries first
- **By Line Number** (`Ctrl+2`) - Sort by source file line numbers
- **By ID** (`Ctrl+3`) - Sort alphabetically by message ID
- **By String** (`Ctrl+4`) - Sort by translation content

**Design Rationale**: 
- Numbered shortcuts (0-4) are easy to remember and execute
- Sorting is frequent operation in translation workflow
- Quick access improves productivity for large files

### Shortcut Editor Interface

#### QKeySequenceEdit Widgets
**Purpose**: Provide intuitive, error-free shortcut editing with built-in validation.

**Features**:
- **Native Key Capture**: Records actual key combinations as pressed
- **Visual Feedback**: Shows shortcut notation immediately
- **Conflict Detection**: Qt validates key sequence format
- **Platform Adaptation**: Automatically uses appropriate modifier keys

**Design Rationale**: 
- QKeySequenceEdit prevents invalid key combinations
- Native feel consistent with OS shortcut editors
- Real-time feedback prevents user errors
- Platform adaptation ensures consistency

#### Settings Persistence
**Purpose**: Maintain shortcut customizations across application sessions.

**Features**:
- **QSettings Integration**: Cross-platform settings storage
- **Hierarchical Keys**: "shortcut/{action_key}" naming convention
- **Default Fallbacks**: Graceful handling of missing settings
- **Immediate Save**: Changes persist without manual save action

**Design Rationale**: 
- QSettings provides reliable, cross-platform persistence
- Hierarchical naming prevents key conflicts
- Default fallbacks ensure application always functions
- Auto-save reduces user friction

## Technical Implementation

### Data Structure
- **Action Registry**: Centralized mapping of action keys to descriptions
- **Default Mappings**: Fallback shortcuts for each action
- **Settings Keys**: Consistent "shortcut/{action}" naming pattern
- **Widget Mapping**: Dictionary linking action keys to editor widgets

### Dynamic Loading
- **Settings Scan**: Load all existing shortcuts from QSettings
- **Default Application**: Apply defaults when no custom setting exists
- **Live Updates**: Changes reflect immediately in application
- **Global Synchronization**: Updates propagate to all application components

### Validation System
- **Format Validation**: QKeySequenceEdit ensures valid key combinations
- **Platform Adaptation**: Automatically handles Cmd vs Ctrl differences
- **Modifier Support**: Proper handling of Shift, Ctrl, Alt, Meta keys
- **Conflict Prevention**: Built-in validation prevents impossible combinations

## User Experience Design

### Visual Hierarchy
- **Category Grouping**: Related shortcuts grouped under clear headings
- **Consistent Layout**: Uniform appearance across all shortcut entries
- **Clear Labels**: Descriptive action names that match menu items
- **Shortcut Notation**: Standard notation (Ctrl+S, Shift+F1, etc.)

### Interaction Model
- **Click to Edit**: Single click on shortcut field activates editor
- **Key Capture**: Simply press desired key combination to set
- **Immediate Feedback**: Shortcut appears instantly in field
- **Escape to Cancel**: Standard escape behavior to abort changes

### Error Prevention
- **Valid Sequences Only**: QKeySequenceEdit prevents invalid combinations
- **Clear Visual States**: Obvious difference between set and unset shortcuts
- **Undo Support**: Can clear shortcuts or revert to defaults
- **Conflict Awareness**: Visual indication of potential conflicts

## Integration Points

### Application Menu System
- **Menu Synchronization**: Changes reflect immediately in application menus
- **Tooltip Updates**: Hover text shows current shortcuts
- **Accelerator Keys**: Underlined letters in menu items update accordingly

### Action System
- **QAction Integration**: Direct connection to Qt action framework
- **Context Sensitivity**: Shortcuts work only in appropriate contexts
- **Global vs Local**: Proper scope handling for different shortcut types

### Help System
- **Documentation Updates**: Help text reflects current shortcut assignments
- **Quick Reference**: Generate shortcut reference cards
- **Searchable Shortcuts**: Find actions by their current shortcuts

## Accessibility Features

### Keyboard Navigation
- **Tab Order**: Logical keyboard navigation through all shortcut fields
- **Screen Reader Support**: Proper labeling for assistive technologies
- **High Contrast**: Shortcuts remain visible in high contrast modes

### Physical Limitations
- **Single-handed Shortcuts**: Options for users with limited mobility
- **Alternative Modifiers**: Support for different modifier key preferences
- **Sticky Keys**: Compatible with accessibility features

### Learning Support
- **Mnemonic Patterns**: Encourage memorable shortcut assignments
- **Logical Grouping**: Related actions use similar key patterns
- **Progressive Disclosure**: Basic shortcuts prominent, advanced ones available

## Default Shortcut Strategy

### Platform Consistency
- **OS Standards**: Follow platform conventions (Ctrl vs Cmd)
- **Application Patterns**: Consistent with other translation tools
- **User Expectations**: Match common software patterns

### Memorability
- **Logical Associations**: Shortcuts relate to action names (S for Save)
- **Frequency-based**: Most common actions get easiest shortcuts
- **Conflict Avoidance**: No overlap with system shortcuts

### Scalability
- **Growth Support**: Number-based shortcuts for expandable categories
- **Modifier Combinations**: Systematic use of Shift, Ctrl, Alt
- **Context Awareness**: Same base key for related actions in different contexts

## Future Enhancements

### Advanced Features
- **Shortcut Profiles**: Save/load complete shortcut configurations
- **Conflict Detection**: Visual warnings for overlapping shortcuts
- **Usage Analytics**: Track which shortcuts are actually used
- **Gesture Support**: Integration with mouse gestures or touch

### Import/Export
- **Configuration Sharing**: Export shortcuts for team standardization
- **Migration Tools**: Import shortcuts from other applications
- **Backup/Restore**: Protect customizations during updates

### Learning Aids
- **Shortcut Trainer**: Interactive tutorial for learning shortcuts
- **Usage Hints**: Suggest shortcuts for frequently accessed features
- **Efficiency Metrics**: Show potential time savings from shortcut use

This panel provides a comprehensive, user-friendly interface for keyboard shortcut customization while maintaining the robust functionality required for professional translation workflows.
