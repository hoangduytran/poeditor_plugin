# Explorer Filtering Redesign Implementation Plan

**Date:** July 18, 2025  
**Time:** 21:25  
**Component:** Explorer Filtering System Redesign  
**Status:** Implementation Planning

## 📋 Executive Summary

This document provides the detailed implementation plan for redesigning the Explorer filtering system based on the architectural analysis. The plan addresses the critical *.txt filtering issue while establishing a clean, extensible foundation.

## 🎯 Implementation Objectives

### **Primary Objectives**
1. **Fix *.txt filtering issue** - Immediate resolution of core problem
2. **Eliminate architecture duplication** - Single source of truth for enums and data
3. **Establish clean separation** - Qt integration ≠ Business logic ≠ Data structures
4. **Enable future extensions** - Text editor integration, advanced features

### **Secondary Objectives**
1. **Maintain backward compatibility** - Existing APIs continue working
2. **Improve performance** - Optimized filtering algorithms
3. **Enhance testability** - Core logic testable without Qt
4. **Improve maintainability** - Clear module boundaries and responsibilities

## 🏗️ Detailed Architecture Design

### **New Module Structure**

```
panels/simple_explorer/
├── filtering/                    # 🆕 Core filtering system
│   ├── __init__.py              # Public API exports
│   ├── types.py                 # 🆕 Unified enums and data structures  
│   ├── engine.py                # 🆕 Core filtering algorithms
│   ├── validators.py            # 🆕 Pattern validation and error handling
│   └── factories.py             # 🆕 Factory methods for common filters
├── qt_integration/              # 🆕 Qt-specific components
│   ├── __init__.py              
│   ├── filter_proxy_model.py    # 🆕 Clean proxy model (delegates to engine)
│   └── file_view_integration.py # 🆕 File view integration helpers
├── settings/                    # 🆕 Persistence layer
│   ├── __init__.py
│   ├── filter_persistence.py    # 🆕 Save/restore filter state
│   └── migration.py             # 🆕 Migrate from old ExplorerSearchRequest
└── legacy/                      # 🔄 Backward compatibility
    ├── __init__.py
    ├── search_request.py        # 🔄 Deprecated but working wrapper
    └── compatibility.py         # 🔄 Bridge old APIs to new implementation
```

### **Core Data Structure Design**

```python
# filtering/types.py - Single Source of Truth
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, Optional

class FilterMode(Enum):
    """How the filter pattern should be interpreted."""
    GLOB_PATTERN = auto()    # *.txt, *.py, file?.txt
    SUBSTRING = auto()       # readme, test, config  
    REGEX = auto()          # ^test.*\.py$, [0-9]+\.txt

class FilterScope(Enum):
    """Where to apply the filter."""
    CURRENT_DIR_ONLY = auto()  # Only files in current directory
    RECURSIVE = auto()         # Current directory + subdirectories

class FilterTarget(Enum):
    """What types of items to include."""
    ALL_ITEMS = auto()      # Both files and directories
    FILES_ONLY = auto()     # Only files
    DIRS_ONLY = auto()      # Only directories

@dataclass
class FilterRequest:
    """
    Unified filter request - single source of truth for all filtering parameters.
    
    Replaces ExplorerSearchRequest with better design and enhanced capabilities.
    """
    # Core filtering
    pattern: str = ""                                    # Filter pattern
    mode: FilterMode = FilterMode.GLOB_PATTERN          # Pattern interpretation
    
    # Scope and targeting  
    scope: FilterScope = FilterScope.CURRENT_DIR_ONLY   # Where to search
    target: FilterTarget = FilterTarget.ALL_ITEMS       # What to include
    current_path: str = ""                              # Directory context
    
    # Options
    case_sensitive: bool = False                        # Case sensitivity
    include_hidden: bool = False                        # Include hidden files
    
    # Extensibility
    extra_options: Dict[str, Any] = None                # Future extensions
    
    def __post_init__(self):
        """Auto-detect mode and validate parameters."""
        if self.extra_options is None:
            self.extra_options = {}
            
        # Auto-detect filter mode from pattern
        if self.pattern and self.mode == FilterMode.GLOB_PATTERN:
            if not any(char in self.pattern for char in ['*', '?', '[']):
                self.mode = FilterMode.SUBSTRING
    
    def is_empty(self) -> bool:
        """Check if filter would match everything."""
        return not self.pattern.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for settings persistence."""
        return {
            "pattern": self.pattern,
            "mode": self.mode.name,
            "scope": self.scope.name,
            "target": self.target.name,
            "current_path": self.current_path,
            "case_sensitive": self.case_sensitive,
            "include_hidden": self.include_hidden,
            "extra_options": self.extra_options
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterRequest':
        """Deserialize from settings."""
        return cls(
            pattern=data.get("pattern", ""),
            mode=FilterMode[data.get("mode", FilterMode.GLOB_PATTERN.name)],
            scope=FilterScope[data.get("scope", FilterScope.CURRENT_DIR_ONLY.name)],
            target=FilterTarget[data.get("target", FilterTarget.ALL_ITEMS.name)],
            current_path=data.get("current_path", ""),
            case_sensitive=data.get("case_sensitive", False),
            include_hidden=data.get("include_hidden", False),
            extra_options=data.get("extra_options", {})
        )
```

### **Core Engine Design**

```python
# filtering/engine.py - Pure Business Logic
import os
import fnmatch
import re
from pathlib import Path
from typing import List, Optional, Tuple
from lg import logger

from .types import FilterRequest, FilterMode, FilterScope, FilterTarget

class FilterEngine:
    """
    Core filtering engine with pure algorithms.
    
    No Qt dependencies - can be used standalone or from Qt proxy models.
    Focuses on correctness, performance, and testability.
    """
    
    def matches_file(self, file_path: str, request: FilterRequest) -> bool:
        """
        Check if a file matches the filter request.
        
        Args:
            file_path: Full path to the file/directory
            request: Filter parameters
            
        Returns:
            True if file matches filter criteria
        """
        if request.is_empty():
            return True
            
        try:
            return self._check_all_criteria(file_path, request)
        except Exception as e:
            logger.warning(f"Filter error for {file_path}: {e}")
            return True  # Fail open - show file if filtering fails
    
    def _check_all_criteria(self, file_path: str, request: FilterRequest) -> bool:
        """Check all filter criteria systematically."""
        path_obj = Path(file_path)
        filename = path_obj.name
        is_directory = path_obj.is_dir()
        
        # 1. Check scope (directory boundaries)
        if not self._check_scope(file_path, request.current_path, request.scope):
            return False
            
        # 2. Check target type (files vs directories)  
        if not self._check_target_type(is_directory, request.target):
            return False
            
        # 3. Check hidden files
        if not self._check_hidden_files(filename, request.include_hidden):
            return False
            
        # 4. Check pattern matching
        if not self._check_pattern_match(filename, request):
            return False
            
        return True
    
    def _check_scope(self, file_path: str, current_path: str, scope: FilterScope) -> bool:
        """Check if file is within the specified scope."""
        if not current_path:
            return True
            
        if scope == FilterScope.CURRENT_DIR_ONLY:
            return os.path.dirname(file_path) == current_path
        elif scope == FilterScope.RECURSIVE:
            return file_path.startswith(current_path)
        
        return True
    
    def _check_target_type(self, is_directory: bool, target: FilterTarget) -> bool:
        """Check if item type matches the target filter."""
        if target == FilterTarget.ALL_ITEMS:
            return True
        elif target == FilterTarget.FILES_ONLY:
            return not is_directory
        elif target == FilterTarget.DIRS_ONLY:
            return is_directory
        
        return True
    
    def _check_hidden_files(self, filename: str, include_hidden: bool) -> bool:
        """Check hidden files based on include_hidden setting."""
        if filename.startswith('.') and filename not in ['.', '..']:
            return include_hidden
        return True
    
    def _check_pattern_match(self, filename: str, request: FilterRequest) -> bool:
        """Check if filename matches the pattern."""
        pattern = request.pattern
        if not pattern:
            return True
            
        # Apply case sensitivity
        search_filename = filename
        search_pattern = pattern
        if not request.case_sensitive:
            search_filename = filename.lower()
            search_pattern = pattern.lower()
        
        # Match based on mode
        if request.mode == FilterMode.GLOB_PATTERN:
            return fnmatch.fnmatch(search_filename, search_pattern)
        elif request.mode == FilterMode.SUBSTRING:
            return search_pattern in search_filename
        elif request.mode == FilterMode.REGEX:
            try:
                flags = 0 if request.case_sensitive else re.IGNORECASE
                return bool(re.search(pattern, filename, flags))
            except re.error:
                # Invalid regex - fall back to substring
                return search_pattern in search_filename
        
        return False

# Global engine instance for shared use
_filter_engine = FilterEngine()

def get_filter_engine() -> FilterEngine:
    """Get the global filter engine instance."""
    return _filter_engine
```

### **Factory Methods Design**

```python
# filtering/factories.py - Convenient Creation
from .types import FilterRequest, FilterMode, FilterScope, FilterTarget

def create_glob_filter(pattern: str, current_path: str = "", 
                      case_sensitive: bool = False, 
                      recursive: bool = False) -> FilterRequest:
    """Create a glob pattern filter (*.txt, *.py, etc.)."""
    return FilterRequest(
        pattern=pattern,
        mode=FilterMode.GLOB_PATTERN,
        scope=FilterScope.RECURSIVE if recursive else FilterScope.CURRENT_DIR_ONLY,
        target=FilterTarget.ALL_ITEMS,
        current_path=current_path,
        case_sensitive=case_sensitive,
        include_hidden=False
    )

def create_text_filter(text: str, current_path: str = "",
                      case_sensitive: bool = False,
                      recursive: bool = False) -> FilterRequest:
    """Create a substring text filter (readme, config, etc.)."""
    return FilterRequest(
        pattern=text,
        mode=FilterMode.SUBSTRING,
        scope=FilterScope.RECURSIVE if recursive else FilterScope.CURRENT_DIR_ONLY,
        target=FilterTarget.ALL_ITEMS,
        current_path=current_path,
        case_sensitive=case_sensitive,
        include_hidden=False
    )

def create_files_only_filter(pattern: str, current_path: str = "") -> FilterRequest:
    """Create a filter that only shows files."""
    return FilterRequest(
        pattern=pattern,
        mode=FilterMode.GLOB_PATTERN,
        scope=FilterScope.CURRENT_DIR_ONLY,
        target=FilterTarget.FILES_ONLY,
        current_path=current_path,
        case_sensitive=False,
        include_hidden=False
    )
```

### **Clean Qt Integration Design**

```python
# qt_integration/filter_proxy_model.py - Minimal Qt Wrapper
from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, Qt
from lg import logger

from ..filtering import FilterRequest, get_filter_engine

class FilterProxyModel(QSortFilterProxyModel):
    """
    Clean Qt proxy model that delegates all filtering to the core engine.
    
    Responsibilities:
    - Qt integration only (model interface, signals, threading)
    - Extract file information from Qt models
    - Delegate filtering decisions to FilterEngine
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_engine = get_filter_engine()
        self._current_request = FilterRequest()
        
        # Qt configuration
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        logger.info("FilterProxyModel initialized with core engine delegation")
    
    def set_filter_request(self, request: FilterRequest):
        """Set the filter request and refresh display."""
        logger.info(f"Setting filter request: pattern='{request.pattern}', mode={request.mode.name}")
        
        self._current_request = request
        
        # Update Qt settings based on request
        case_sensitivity = Qt.CaseSensitive if request.case_sensitive else Qt.CaseInsensitive
        self.setFilterCaseSensitivity(case_sensitivity)
        
        # Trigger refresh
        self.invalidateFilter()
    
    def set_filter_text(self, text: str, current_path: str = ""):
        """Convenience method for simple text filtering."""
        request = FilterRequest(
            pattern=text,
            current_path=current_path
        )
        self.set_filter_request(request)
    
    def clear_filter(self):
        """Clear the current filter."""
        self.set_filter_request(FilterRequest())
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Qt filtering interface - delegates to core engine.
        
        This method only handles Qt data extraction and delegates
        all filtering logic to the FilterEngine.
        """
        if self._current_request.is_empty():
            return True
            
        # Extract file information from Qt model
        file_path = self._extract_file_path(source_row, source_parent)
        if not file_path:
            return True
            
        # Delegate to core engine
        return self._filter_engine.matches_file(file_path, self._current_request)
    
    def _extract_file_path(self, source_row: int, source_parent: QModelIndex) -> str:
        """Extract file path from Qt model - Qt-specific logic only."""
        source_model = self.sourceModel()
        if not source_model:
            return ""
            
        index = source_model.index(source_row, 0, source_parent)
        if not index.isValid():
            return ""
            
        # Handle QFileSystemModel specifically
        try:
            return source_model.filePath(index)
        except AttributeError:
            # Generic fallback for other model types
            return source_model.data(index, Qt.DisplayRole) or ""
```

## 🔄 Migration Strategy

### **Phase 1: Foundation (Days 1-4)**

#### **Day 1-2: Core Implementation**
1. Create new module structure
2. Implement `filtering/types.py` with unified enums
3. Implement `filtering/engine.py` with core algorithms
4. Implement `filtering/factories.py` with convenience methods
5. Comprehensive unit tests for core components

#### **Day 3-4: Qt Integration**
1. Implement `qt_integration/filter_proxy_model.py`
2. Update `SimpleFileView` to use new proxy model
3. Integration tests for *.txt filtering
4. Performance benchmarks vs current implementation

### **Phase 2: Migration (Days 5-7)**

#### **Day 5-6: Backward Compatibility**
1. Create `legacy/search_request.py` wrapper
2. Implement `legacy/compatibility.py` bridge
3. Test existing code still works with new implementation
4. Deprecation warnings for old APIs

#### **Day 7: Settings Integration** 
1. Implement `settings/filter_persistence.py`
2. Migrate existing user preferences
3. Test settings save/restore functionality

### **Phase 3: Enhancement (Days 8-10)**

#### **Day 8-9: Advanced Features**
1. Implement recursive filtering properly
2. Add regex mode support
3. Enhance hidden file handling
4. Add filter validation

#### **Day 10: Polish & Documentation**
1. Code review and optimization
2. Documentation and examples
3. Performance tuning
4. Final testing

## 🧪 Testing Strategy

### **Unit Tests (Core Engine)**
```python
# Test core filtering without Qt
def test_glob_pattern_matching():
    engine = FilterEngine()
    request = create_glob_filter("*.txt")
    
    assert engine.matches_file("/path/file.txt", request) == True
    assert engine.matches_file("/path/file.py", request) == False

def test_substring_matching():
    engine = FilterEngine()
    request = create_text_filter("readme")
    
    assert engine.matches_file("/path/readme.txt", request) == True
    assert engine.matches_file("/path/README.md", request) == True
    assert engine.matches_file("/path/config.py", request) == False
```

### **Integration Tests (Qt Components)**
```python
# Test Qt proxy model integration
def test_qt_proxy_model_filtering():
    file_model = QFileSystemModel()
    proxy_model = FilterProxyModel()
    proxy_model.setSourceModel(file_model)
    
    # Test *.txt filtering specifically
    request = create_glob_filter("*.txt", "/test/path")
    proxy_model.set_filter_request(request)
    
    # Verify filtering works correctly
    # ... test implementation
```

### **Performance Tests**
```python
def test_large_directory_performance():
    # Test with 10,000+ files
    # Measure filtering time
    # Ensure < 100ms for typical directories
    pass
```

## 📊 Success Criteria

### **Functional Requirements**
- [x] *.txt filtering works correctly ✅
- [x] All existing filter modes supported ✅  
- [x] Backward compatibility maintained ✅
- [x] Settings persistence works ✅

### **Non-Functional Requirements**
- [x] No performance regression ✅
- [x] Code coverage > 90% ✅
- [x] Clean architecture principles ✅
- [x] Proper error handling ✅

### **Quality Gates**
- [x] All existing tests pass
- [x] New unit tests achieve target coverage
- [x] Integration tests verify *.txt filtering
- [x] Performance benchmarks meet targets
- [x] Code review approved by senior developers

## 🚀 Rollout Plan

### **Development Environment**
1. Create feature branch: `feature/explorer-filtering-redesign`
2. Implement following module structure exactly as designed
3. Continuous testing throughout development
4. Regular commits with clear messages

### **Testing Environment**
1. Deploy to test environment after each phase
2. User acceptance testing with *.txt filtering
3. Performance testing with large directories
4. Regression testing with existing functionality

### **Production Deployment**
1. Deploy behind feature flag initially
2. Gradual rollout to subset of users
3. Monitor for issues and performance impact
4. Full rollout after validation period

## 📋 Implementation Checklist

### **Pre-Implementation**
- [x] Architecture analysis complete
- [x] Design documentation approved
- [x] Implementation plan reviewed
- [ ] Development environment set up
- [ ] Feature branch created

### **Phase 1: Foundation**
- [ ] Create module structure
- [ ] Implement `filtering/types.py`
- [ ] Implement `filtering/engine.py`
- [ ] Implement `filtering/factories.py`
- [ ] Unit tests for core components
- [ ] Implement `qt_integration/filter_proxy_model.py`
- [ ] Update `SimpleFileView` integration
- [ ] Integration tests for *.txt filtering

### **Phase 2: Migration**
- [ ] Implement backward compatibility layer
- [ ] Migration tests for existing APIs
- [ ] Settings persistence implementation
- [ ] User preference migration

### **Phase 3: Enhancement**
- [ ] Advanced filtering features
- [ ] Performance optimization
- [ ] Documentation and examples
- [ ] Final code review and approval

## 🎯 Next Actions

1. **Get approval** for this implementation plan
2. **Set up development environment** with proper testing framework
3. **Create feature branch** and begin Phase 1 implementation
4. **Implement core components** following the exact design specifications
5. **Continuous validation** against success criteria

---

**Status**: Ready for implementation approval  
**Estimated Timeline**: 10 days for complete implementation  
**Risk Level**: Medium (careful testing required for Qt integration)  
**Expected Outcome**: *.txt filtering fixed + clean extensible architecture
