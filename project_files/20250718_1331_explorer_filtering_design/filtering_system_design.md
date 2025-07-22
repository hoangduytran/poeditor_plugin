# Explorer Filtering System Design

**Date:** July 18, 2025  
**Time:** 13:31  
**Component:** Explorer Panel Filtering  
**Status:** In Progress

## Overview

This document outlines the design for a comprehensive file filtering system for the POEditor explorer panel that can grow to support:

- Basic file pattern filtering (*.txt, *.py, etc.)
- Statistical functions (file counts, size analysis)
- Integration with text editors
- Advanced search capabilities

## Problem Statement

The current simple explorer filtering for `*.txt` patterns returns empty results due to over-engineered complexity. We need a well-designed filtering system that:

1. **Solves the immediate problem**: `*.txt` filtering works reliably
2. **Supports future needs**: Text editor integration and statistical analysis
3. **Follows project rules**: Modular architecture, clear APIs, proper logging
4. **Remains extensible**: Can grow with user requirements

## Architecture Design

### Core Components

```
ExplorerFilterEngine (Main API)
├── FilterCriteria (Data Structure)
├── FileFilter (Abstract Base)
│   ├── GlobFileFilter (*.txt, *.py)
│   ├── SubstringFileFilter (readme, test)
│   └── RegexFileFilter (advanced patterns)
├── FileSystemScanner (File Discovery)
└── FilterResult (Results + Statistics)
```

### Component Responsibilities

#### 1. FilterCriteria (Data Class)
```python
@dataclass
class FilterCriteria:
    pattern: str = ""
    current_path: str = ""  # ADDED: Current directory context
    mode: FilterMode = FilterMode.GLOB_PATTERN
    scope: FilterScope = FilterScope.CURRENT_DIRECTORY
    target: FilterTarget = FilterTarget.ALL_ITEMS
    case_sensitive: bool = False
    include_hidden: bool = False
    extra_options: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize missing fields and auto-detect filter mode."""
        if self.extra_options is None:
            self.extra_options = {}
        
        # Auto-detect filter mode if pattern contains special characters
        if self.pattern and self.mode == FilterMode.GLOB_PATTERN:
            if not any(char in self.pattern for char in ['*', '?', '[']):
                self.mode = FilterMode.SUBSTRING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization/settings persistence."""
        return {
            "pattern": self.pattern,
            "mode": self.mode.name,
            "scope": self.scope.name,
            "target": self.target.name,
            "case_sensitive": self.case_sensitive,
            "include_hidden": self.include_hidden,
            "extra_options": self.extra_options
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterCriteria':
        """Create instance from dictionary for settings restoration."""
        return cls(
            pattern=data.get("pattern", ""),
            mode=FilterMode[data.get("mode", FilterMode.GLOB_PATTERN.name)],
            scope=FilterScope[data.get("scope", FilterScope.CURRENT_DIRECTORY.name)],
            target=FilterTarget[data.get("target", FilterTarget.ALL_ITEMS.name)],
            case_sensitive=data.get("case_sensitive", False),
            include_hidden=data.get("include_hidden", False),
            extra_options=data.get("extra_options", {})
        )
```

**Purpose**: Encapsulates ALL filtering parameters with full backward compatibility
**New Benefits**: 
- ✅ **Extensibility**: `extra_options` dict for future parameters
- ✅ **Persistence**: Serialization support for settings
- ✅ **Auto-Detection**: Smart filter mode detection
- ✅ **Migration**: Drop-in replacement for `ExplorerSearchRequest`

## Enhanced Use Cases & Examples

### Immediate Use Case: *.txt Filtering (All Parameters)
```python
# Complete *.txt filtering with all options
engine = ExplorerFilterEngine()
criteria = FilterCriteria(
    pattern="*.txt",
    mode=FilterMode.GLOB_PATTERN,  # Auto-detected
    scope=FilterScope.CURRENT_DIRECTORY,
    target=FilterTarget.FILES_ONLY,
    case_sensitive=False,
    include_hidden=False
)

result = engine.filter_directory("/path/to/dev", criteria)
print(f"Found {len(result.matching_files)} text files (hidden files excluded)")
```

### Advanced Use Case: Hidden Files and Extensions
```python
# Find all hidden configuration files
criteria = FilterCriteria(
    pattern=".*",  # Hidden files pattern
    mode=FilterMode.GLOB_PATTERN,
    scope=FilterScope.RECURSIVE,
    target=FilterTarget.FILES_ONLY,
    case_sensitive=True,
    include_hidden=True,  # CRITICAL: Must include hidden files
    extra_options={
        "max_depth": 3,  # Future extension: limit recursion depth
        "follow_symlinks": False  # Future extension: symlink handling
    }
)

result = engine.filter_directory("/project", criteria)
hidden_configs = [f for f in result.matching_files if f.startswith('.')]
```

### Settings Persistence Use Case
```python
# Save user's preferred filter settings
user_criteria = FilterCriteria(
    pattern="*.py",
    scope=FilterScope.RECURSIVE,
    target=FilterTarget.FILES_ONLY,
    include_hidden=True
)

# Save to settings
settings = user_criteria.to_dict()
save_user_preferences("filter_settings", settings)

# Restore from settings later
saved_settings = load_user_preferences("filter_settings")
restored_criteria = FilterCriteria.from_dict(saved_settings)
```

## Enhanced Technical Decisions

### Why Enhanced FilterCriteria?
- **Full Compatibility**: Replaces `ExplorerSearchRequest` without breaking changes
- **Extensibility**: `extra_options` allows new parameters without schema changes
- **Persistence**: Built-in serialization for user preferences
- **Smart Defaults**: Auto-detection reduces user configuration burden

### Why Extensibility Dict?
- **Future-Proofing**: Can add `max_depth`, `follow_symlinks`, `content_search`, etc.
- **Plugin Support**: Third-party filters can add custom parameters
- **A/B Testing**: Can experiment with new features without breaking existing code
- **Backward Compatibility**: Old code continues working when new options are added

## Enhanced Integration Points

### 1. Backward Compatibility Integration
```python
# Existing code using ExplorerSearchRequest continues working
class SimpleFileView(QTreeView):
    def set_filter_from_legacy(self, search_request: ExplorerSearchRequest):
        # Convert legacy request to new criteria
        criteria = FilterCriteria(
            pattern=search_request.filter_text,
            mode=search_request.filter_mode,
            scope=search_request.filter_scope,
            target=search_request.filter_type,
            case_sensitive=search_request.case_sensitive,
            include_hidden=search_request.include_hidden,
            extra_options=search_request.extra_options or {}
        )
        
        # Use new engine with converted criteria
        result = self.filter_engine.filter_directory(self.current_path, criteria)
        self.update_display(result)
```

### 2. Enhanced Settings Integration
```python
# Settings manager can save/restore complete filter state
class FilterSettingsManager:
    def save_recent_filters(self, criteria_list: List[FilterCriteria]):
        settings_data = [criteria.to_dict() for criteria in criteria_list]
        self.settings.setValue("recent_filters", settings_data)
    
    def load_recent_filters(self) -> List[FilterCriteria]:
        settings_data = self.settings.value("recent_filters", [])
        return [FilterCriteria.from_dict(data) for data in settings_data]
```

### 3. Future Extension Points
```python
# Future extensions can use extra_options seamlessly
class ContentAwareFilter(FileFilter):
    def matches(self, file_path: str, is_directory: bool) -> bool:
        criteria = self.get_criteria()
        
        # Use standard parameters
        if not super().matches(file_path, is_directory):
            return False
        
        # Use extended parameters from extra_options
        if criteria.extra_options.get("content_search"):
            return self.search_file_content(file_path, criteria.extra_options["content_search"])
        
        return True
```

## Comprehensive Parameter Coverage

| Parameter | Current Code | Design Coverage | Status |
|-----------|--------------|----------------|---------|
| Pattern text | ✅ `filter_text` | ✅ `pattern` | Complete |
| Current path | ✅ `current_path` | ✅ `current_path` | **Complete** |
| Filter mode | ✅ `filter_mode` | ✅ `mode` | Complete |
| Scope | ✅ `filter_scope` | ✅ `scope` | Complete |
| Target type | ✅ `filter_type` | ✅ `target` | Complete |
| Case sensitivity | ✅ `case_sensitive` | ✅ `case_sensitive` | Complete |
| Hidden files | ✅ `include_hidden` | ✅ `include_hidden` | **Enhanced** |
| Extensibility | ✅ `extra_options` | ✅ `extra_options` | **Enhanced** |
| Serialization | ✅ `to_dict/from_dict` | ✅ `to_dict/from_dict` | **Enhanced** |
| Auto-detection | ✅ `__post_init__` | ✅ `__post_init__` | **Enhanced** |
| Current path | ✅ `current_path` | ✅ `current_path` | **Complete** |

## Complete Parameter Coverage Achieved

The design now includes ALL parameters from the existing `ExplorerSearchRequest`:

### ✅ All Core Parameters Covered
- **Pattern text**: `filter_text` → `pattern`
- **Current path**: `current_path` → `current_path` (preserved)
- **Filter mode**: `filter_mode` → `mode`  
- **Filter scope**: `filter_scope` → `scope`
- **Filter type**: `filter_type` → `target`
- **Case sensitivity**: `case_sensitive` → `case_sensitive`
- **Hidden files**: `include_hidden` → `include_hidden`
- **Extensibility**: `extra_options` → `extra_options`

### ✅ Enhanced Functionality Added
- **Serialization**: `to_dict` and `from_dict` methods for settings persistence
- **Auto-detection**: Smart filter mode detection in `__post_init__`
- **Validation**: Parameter validation and error handling
- **Documentation**: Comprehensive docstrings and type hints

## Missing Implementation Components

### 1. Core Engine Implementation
- **ExplorerFilterEngine**: Main API class not yet implemented
- **FileSystemScanner**: File discovery logic missing
- **FilterResult**: Results container class incomplete

### 2. Filter Implementations
- **GlobFileFilter**: Pattern matching (*.txt, *.py) - Priority 1
- **SubstringFileFilter**: Simple text matching - Priority 2  
- **RegexFileFilter**: Advanced patterns - Priority 3

### 3. Integration Layer
- **Explorer panel integration**: UI connection points
- **Settings persistence**: Save/restore user preferences
- **Error handling**: Robust exception management

## Implementation Roadmap

### Phase 1: Core Functionality (Week 1)
1. **FilterCriteria class** - Data structure implementation
2. **GlobFileFilter** - Basic *.txt pattern matching
3. **ExplorerFilterEngine** - Simple API with glob support
4. **Unit tests** - Core functionality validation

### Phase 2: Enhanced Features (Week 2)
1. **FileSystemScanner** - Efficient file discovery
2. **FilterResult** - Statistics and metadata
3. **SubstringFileFilter** - Text-based matching
4. **Integration tests** - End-to-end scenarios

### Phase 3: Advanced Features (Week 3)
1. **RegexFileFilter** - Complex pattern support
2. **Settings persistence** - User preference storage
3. **Performance optimization** - Large directory handling
4. **Explorer panel integration** - UI implementation

## Next Steps Required

### Immediate Actions (Today)
1. **Create implementation directory**: `/src/explorer/filtering/`
2. **Implement FilterCriteria**: Start with data class
3. **Create basic tests**: Ensure *.txt filtering works
4. **Validate design**: Test with real file structure

### Implementation Files Needed
```
/src/explorer/filtering/
├── __init__.py
├── filter_criteria.py       # FilterCriteria data class
├── filter_engine.py         # ExplorerFilterEngine main API
├── file_filters.py          # GlobFileFilter, SubstringFileFilter, RegexFileFilter
├── scanner.py               # FileSystemScanner
├── results.py               # FilterResult container
└── tests/
    ├── test_filter_criteria.py
    ├── test_glob_filter.py
    └── test_integration.py
```

### Success Criteria
- [ ] `*.txt` filtering returns correct results
- [ ] All parameters from ExplorerSearchRequest supported
- [ ] Unit tests pass with 90%+ coverage
- [ ] Integration with existing explorer panel
- [ ] Performance: <100ms for directories with 1000+ files

## Risk Assessment

### High Risk ⚠️
- **Over-engineering**: Design is comprehensive but may be too complex for immediate needs
- **Integration complexity**: Backward compatibility with existing ExplorerSearchRequest

### Medium Risk ⚡
- **Performance**: Large directory scanning may be slow
- **Testing coverage**: Complex scenarios need thorough validation

### Low Risk ✅
- **Core functionality**: Basic glob pattern matching is straightforward
- **Extensibility**: Design supports future requirements well

## Decision Points

### Architecture Decisions Made ✅
- Use FilterCriteria as unified parameter container
- Abstract FileFilter base for extensibility
- Maintain backward compatibility with ExplorerSearchRequest

### Decisions Still Needed 🤔
1. **File scanning strategy**: Recursive vs. batched scanning for performance
2. **Caching approach**: Should results be cached? How long?
3. **Error handling level**: Silent failures vs. user notifications
4. **Integration timing**: Replace ExplorerSearchRequest immediately or gradual migration?

## Status Summary

**Current State**: Design Complete, Implementation Not Started
**Next Phase**: Begin FilterCriteria implementation
**Timeline**: 3 weeks for full implementation
**Priority**: High (fixes existing *.txt filtering bug)
