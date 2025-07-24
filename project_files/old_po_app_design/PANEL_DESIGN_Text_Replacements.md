# Text Replacements Panel - Design Specification

## Overview
The Text Replacements panel provides a powerful system for automating text substitutions during translation work. This feature enables translators to create shortcuts, expand abbreviations, and implement consistent terminology through configurable text replacement rules.

## Design Purpose
- **Productivity Enhancement**: Reduce repetitive typing through smart text expansion
- **Consistency Enforcement**: Ensure consistent terminology across translations
- **Abbreviation Expansion**: Convert short codes into longer, frequently-used phrases
- **Pattern Replacement**: Support both simple text and regex-based substitutions
- **Workflow Optimization**: Streamline common translation tasks

## Component Structure

### Import/Export Section

#### File Operations
**Purpose**: Enable sharing and backup of replacement configurations.

**Features**:
- **Import Button**: Load replacement rules from external files
- **Export Button**: Save current rules to various formats
- **Multiple Formats**: Support for JSON, CSV, and custom formats
- **Drag & Drop**: Accept dropped files for quick importing

**Design Rationale**: 
- Team collaboration requires shareable configurations
- Backup and restore functionality protects user investment
- Multiple formats ensure compatibility with other tools

### Advanced Search Interface

#### Search Scope Selector
**Purpose**: Control which columns are searched during find operations.

**Features**:
- **Dropdown Combo**: "Both", "Shortcut", "Replacement" options
- **Smart Filtering**: Only search relevant data based on selection
- **Performance Optimization**: Reduced search scope improves speed

#### Search Modifiers
**Purpose**: Provide fine-grained control over search behavior.

**Features**:
1. **Match Case ("Aa")**: Toggle case-sensitive searching
2. **Whole Word ("ab" underlined)**: Match only complete words
3. **Regular Expression (".*")**: Enable regex pattern matching
4. **Real-time Updates**: Search results update as options change

**Design Rationale**: 
- Visual icons make options immediately recognizable
- Checkbox format allows multiple modifiers simultaneously
- Real-time updates provide immediate feedback

#### Search Field and Navigation
**Purpose**: Quick location and navigation through replacement entries.

**Features**:
- **Search Input**: Real-time filtering as user types
- **Find Button**: Execute search with current criteria
- **Navigation Arrows**: "↑" and "↓" buttons for result navigation
- **Auto-enable**: Buttons activate only when search has results

### Replacement Table

#### Table Structure
**Purpose**: Display and manage all replacement rules in a sortable, organized view.

**Features**:
- **Two-column Layout**: "Shortcut" and "Replacement" columns
- **Stretch Headers**: Columns automatically resize to available space
- **Row Selection**: Click to select entire replacement rule
- **Sort Functionality**: Click headers to sort by column
- **No Direct Editing**: Prevents accidental modifications

**Design Rationale**: 
- Two-column format clearly shows input → output relationship
- Row selection mode prevents confusion about which rule is selected
- Separate edit area reduces accidental changes

#### Sorting Capabilities
**Purpose**: Organize replacement rules for easy browsing and management.

**Features**:
- **Column Sorting**: Click headers to sort by shortcut or replacement text
- **Ascending/Descending**: Toggle sort order with repeated clicks
- **Visual Feedback**: Headers indicate current sort column and direction
- **Persistent State**: Sort preferences maintained during session

### Edit Panel

#### Input Fields
**Purpose**: Create and modify replacement rules with appropriate input methods.

**Features**:
1. **Shortcut Field**: Single-line input for trigger text
   - Simple text input (QLineEdit)
   - Placeholder: "Shortcut…"
   - Label: "Shortcut:"

2. **Replacement Field**: Multi-line input for replacement text
   - Rich text editor (ReplacementTextEdit)
   - Placeholder: "Replacement…"  
   - Label: "Replacement:"
   - Supports multi-line replacements

**Design Rationale**: 
- Single-line for shortcuts keeps them concise and memorable
- Multi-line for replacements allows complex text blocks
- Clear labels prevent confusion about field purposes

#### Action Buttons
**Purpose**: Provide clear actions for managing replacement rules.

**Features**:
- **Add Button ("+ Add")**: Create new replacement rule
- **Delete Button ("- Delete")**: Remove selected replacement rule
- **Save Button**: Update existing replacement rule
- **Horizontal Layout**: Buttons arranged in logical sequence

**Design Rationale**: 
- Icon prefixes (+ and -) make actions immediately recognizable
- Save function allows modification of existing rules
- Horizontal arrangement saves vertical space

## Technical Implementation

### Data Storage
- **QSettings Backend**: Persistent storage using application settings
- **Array Format**: Rules stored as array of objects with 'replace' and 'with' keys
- **Cross-platform**: Settings automatically adapt to OS conventions

### Search Implementation
- **Real-time Filtering**: Search executes immediately as user types
- **Scope-aware**: Search algorithm respects selected column scope
- **Pattern Matching**: Supports both literal text and regex patterns
- **Performance Optimized**: Efficient searching even with large rule sets

### Replacement Engine Integration
- **Live Text Processing**: Rules automatically apply during typing
- **Context Awareness**: Replacements trigger on appropriate word boundaries
- **Undo Support**: Replacements can be undone like normal text operations

## User Experience Design

### Progressive Disclosure
- **Simple to Complex**: Basic replacements easy to create, advanced options available
- **Visual Hierarchy**: Most important functions (add/edit) prominently displayed
- **Contextual Enable**: Buttons activate only when relevant

### Immediate Feedback
- **Live Search**: Results appear instantly as user types
- **Selection Feedback**: Clicked rules immediately populate edit fields
- **Status Indication**: Button states clearly indicate available actions

### Error Prevention
- **Input Validation**: Prevents empty shortcuts or replacements
- **Confirmation Patterns**: Clear distinction between add and save operations
- **Reversible Actions**: All operations can be undone or corrected

## Integration Points

### Text Editors
- **Main Translation Field**: Replacements work during translation entry
- **Comment Fields**: Rules apply to comment text as well
- **Search Fields**: Replacements can be used in search operations

### File Operations
- **Import Formats**: JSON, CSV, and proprietary formats supported
- **Export Options**: Multiple output formats for different use cases
- **Encoding Handling**: Proper Unicode support for international text

## Replacement Rule Types

### Simple Text Replacement
- **Basic Substitution**: "teh" → "the"
- **Abbreviation Expansion**: "btw" → "by the way"
- **Terminology Consistency**: "app" → "application"

### Advanced Pattern Replacement
- **Date Formats**: Transform date patterns
- **Number Formatting**: Standardize number representations
- **Case Transformations**: Upper/lowercase conversions

### Multi-line Replacements
- **Template Expansion**: Short codes expand to full text blocks
- **Boilerplate Text**: Common phrases and disclaimers
- **Structured Content**: Tables, lists, formatted content

## Workflow Integration

### Translation Memory Synergy
- **Terminology Alignment**: Replacements can enforce translation memory consistency
- **Quality Assurance**: Prevent common terminology mistakes
- **Team Standardization**: Shared replacement rules ensure team consistency

### Keyboard Shortcuts
- **Quick Access**: Key combinations for common replacement functions
- **Navigation Support**: Keyboard navigation through replacement table
- **Edit Mode Triggers**: Shortcuts to activate edit mode for selected rules

## Future Enhancements

### Advanced Features
- **Conditional Replacements**: Rules that apply only in specific contexts
- **Language-specific Rules**: Different replacement sets for different languages
- **Rule Categories**: Organize replacements into themed groups
- **Rule Priorities**: Control order of replacement application

### Collaboration Features
- **Shared Rule Libraries**: Team-wide replacement rule repositories
- **Version Control**: Track changes to replacement configurations
- **Role-based Access**: Different permission levels for rule management

### Integration Expansions
- **External Dictionaries**: Integration with terminology databases
- **Machine Learning**: Suggest replacements based on usage patterns
- **API Integration**: Connect with external translation tools

This panel provides a comprehensive solution for text replacement automation, balancing ease of use with powerful functionality to support professional translation workflows.
