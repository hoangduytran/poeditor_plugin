# Fonts and Languages Panel - Design Specification

## Overview
The Fonts and Languages panel provides comprehensive typography customization for all text elements throughout the PO Editor application. This panel allows users to fine-tune the visual appearance of the interface to match their preferences and improve readability.

## Design Purpose
- **Typography Control**: Enable users to customize fonts for different UI components
- **Accessibility**: Support users with visual impairments through font size adjustments
- **Localization**: Allow selection of target language for translation workflows
- **Consistency**: Maintain consistent font application across the entire application

## Component Structure

### Font Configuration Sections

#### 1. Message ID (msgid) Font
**Purpose**: Controls the appearance of source text in the main translation table and editor panels.

**Features**:
- Font family selector (QFontComboBox)
- Font size spinner (6-72pt range)
- Live preview showing sample text
- Default size: 15pt

**Design Rationale**: 
- Source text needs to be easily readable but not overpowering
- Medium size ensures good readability without consuming too much screen space

#### 2. Translation (msgstr) Font
**Purpose**: Controls the appearance of target translation text - the most important text users interact with.

**Features**:
- Font family selector
- Font size spinner (6-72pt range)
- Live preview with sample text
- Default size: 24pt (largest default)

**Design Rationale**: 
- Translation text is the primary focus of user attention
- Larger default size reduces eye strain during extended translation sessions
- Most critical text element deserves prominent visual treatment

#### 3. Table Font
**Purpose**: Controls the appearance of text within the main translation table rows and columns.

**Features**:
- Font family selector
- Font size spinner
- Live preview
- Default size: 13pt

**Design Rationale**: 
- Table text needs to be compact but readable
- Medium-small size allows more entries to be visible simultaneously
- Balanced between readability and information density

#### 4. Comments Font
**Purpose**: Controls the appearance of translator comments and extracted comments.

**Features**:
- Font family selector
- Font size spinner
- Live preview
- Default size: 15pt

**Design Rationale**: 
- Comments are supplementary information
- Should be readable but not compete with main content
- Similar size to msgid for consistency

#### 5. Suggestions Font
**Purpose**: Controls the appearance of translation suggestions and history entries.

**Features**:
- Font family selector
- Font size spinner
- Live preview
- Default size: 13pt

**Design Rationale**: 
- Suggestions are reference material
- Smaller size indicates secondary importance
- Should not distract from main translation work

#### 6. Controls Font (Buttons, Labels, Headers)
**Purpose**: Controls the appearance of all UI control elements throughout the application.

**Features**:
- Font family selector
- Font size spinner
- Live preview
- Default size: 12pt

**Design Rationale**: 
- Standard UI elements need consistent, professional appearance
- 12pt is optimal for UI controls across different screen sizes
- Affects buttons, labels, group headers, menu items

### Target Language Section

#### Language Selection
**Purpose**: Define the target language for translation workflows and machine translation services.

**Features**:
- Dropdown combo box with country flags/names
- Supported languages: Vietnamese, English, French, Spanish
- Stores ISO language codes internally

**Design Rationale**: 
- Essential for translation memory matching
- Required for machine translation API calls
- Affects spell-checking and text direction

### Font Preview Section

#### Global Preview
**Purpose**: Provide immediate visual feedback of font changes.

**Features**:
- Large preview area showing sample text
- Updates in real-time as fonts are modified
- Shows comprehensive character set: "AaBbCcDdEeFfGg 1234567890 !@#$%^&*()"

**Design Rationale**: 
- Immediate feedback reduces trial-and-error
- Comprehensive character set reveals font characteristics
- Visual confirmation before applying changes

### Apply Font Settings

#### Application Button
**Purpose**: Apply all font changes throughout the application immediately.

**Features**:
- Single "Apply Font Settings" button
- Triggers global font update across all components
- Shows confirmation dialog
- Saves settings to persistent storage

**Design Rationale**: 
- Batch application prevents performance issues
- User control over when changes take effect
- Confirmation feedback ensures changes were applied

## Technical Implementation

### Settings Persistence
- **QSettings Storage**: All font configurations stored in "POEditor" organization settings
- **Font String Format**: Fonts stored as Qt font descriptor strings
- **Key Naming**: Consistent naming pattern (msgidFont, msgstrFont, etc.)

### Real-time Updates
- **Live Previews**: Each font component updates its preview immediately
- **Preference Dialog Feedback**: Control fonts apply to preferences dialog immediately
- **Signal/Slot Architecture**: Font changes trigger immediate UI updates

### Font Family Support
- **System Fonts**: Access to all installed system fonts
- **Cross-platform Compatibility**: Qt font handling ensures consistent appearance
- **Fallback Handling**: Graceful degradation when fonts unavailable

## User Experience Design

### Progressive Disclosure
- **Scrollable Interface**: All font options visible without overwhelming the user
- **Grouped Organization**: Related settings grouped in visually distinct sections
- **Consistent Layout**: All font components follow identical layout pattern

### Visual Feedback
- **Individual Previews**: Each font component shows immediate preview
- **Global Preview**: Main preview area shows comprehensive font appearance
- **Border Styling**: Preview areas clearly delineated with subtle borders

### Accessibility Considerations
- **Large Size Range**: 6-72pt accommodates diverse visual needs
- **Clear Labels**: Descriptive labels for each font component
- **Logical Tab Order**: Keyboard navigation follows logical sequence

## Integration Points

### Application Components
- **Main Table**: Uses table font for entry display
- **Editor Panels**: Uses msgid/msgstr fonts for source/target text
- **Suggestion Panel**: Uses suggestion font for history entries
- **Comment Areas**: Uses comment font for all comment text
- **UI Controls**: Uses control font for buttons, labels, headers

### Settings Synchronization
- **Global Font System**: Integrates with main application font management
- **Immediate Application**: Changes apply across all open windows
- **Persistent Storage**: Settings survive application restarts

## Default Font Strategy

### Size Hierarchy
1. **Translation Text (24pt)** - Largest, most important
2. **Message ID (15pt)** - Medium, source reference
3. **Comments (15pt)** - Medium, supplementary information
4. **Table Text (13pt)** - Compact, high information density
5. **Suggestions (13pt)** - Compact, reference material
6. **Controls (12pt)** - Standard UI elements

### Font Family Defaults
- **System Default**: Uses Qt system font recommendations
- **Cross-platform Consistency**: Appropriate defaults for each OS
- **Professional Appearance**: Defaults chosen for translation work

## Future Enhancements

### Potential Additions
- **Theme Integration**: Font choices could integrate with application themes
- **Font Profiles**: Save/load complete font configuration sets
- **Advanced Typography**: Line spacing, character spacing controls
- **Font Recommendations**: Suggest optimal fonts for different languages
- **Import/Export**: Share font configurations between installations

This panel represents a comprehensive solution for typography customization, balancing user control with sensible defaults and maintaining consistency across the application.
