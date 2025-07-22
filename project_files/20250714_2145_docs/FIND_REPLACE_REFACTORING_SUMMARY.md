# Find/Replace Types Refactoring Summary

## Overview
The find/replace types have been refactored to eliminate duplication and create a more unified architecture. The main changes consolidate common navigation and match span functionality into base classes.

## New Architecture

### Base Classes

1. **`BaseNavRecord`** - Common navigation attributes
   - `row_index`: Original index in dataset
   - `unique_id`: Unique identifier
   - `page_index`: Page number for navigation
   - `local_index`: Local index within page

2. **`MatchSpans`** - Unified match span handling
   - `spans`: List of (start, end) match positions
   - `current_span_idx`: Current span for highlighting
   - `field`: Field containing current span
   - Helper methods: `add_span()`, `get_current_span()`, `has_spans()`, `set_current()`

### Specialized Classes

3. **`FileSearchRecord`** (alias: `SearchNavRecord`)
   - Extends `BaseNavRecord` for file system search results
   - File metadata: path, name, size, modified time
   - Match information via `MatchSpans`

4. **`DatabaseMatchRecord`** (alias: `MatchInstance`)
   - Extends `BaseNavRecord` for database search results
   - Separate `MatchSpans` for msgid, msgstr, context fields
   - Links to `FindReplaceResult`

5. **`FindReplaceResult`**
   - Now extends `BaseNavRecord`
   - Uses `MatchSpans` objects for each field
   - Legacy fields maintained for backward compatibility
   - Helper methods for span manipulation

## Migration Guide

### For SearchNavRecord Users
**Old:**
```python
record = SearchNavRecord(
    row_index=0,
    file_path="/path/to/file",
    file_name="file.txt",
    file_size=1024,
    modified_time=time.time(),
    is_dir=False,
    match_spans=[(0, 5), (10, 15)],
    content_preview="preview text",
    page_index=1,
    local_index=2,
    unique_id=123
)
```

**New:**
```python
# Direct construction
record = FileSearchRecord(
    row_index=0,
    unique_id=123,
    page_index=1,
    local_index=2,
    file_path="/path/to/file",
    file_name="file.txt",
    file_size=1024,
    modified_time=time.time(),
    is_dir=False,
    content_preview="preview text"
)
record.match_spans.spans = [(0, 5), (10, 15)]

# Or use factory function
record = create_search_nav_record(
    file_path="/path/to/file",
    file_name="file.txt",
    file_size=1024,
    modified_time=time.time(),
    is_dir=False,
    row_index=0,
    match_spans=[(0, 5), (10, 15)],
    content_preview="preview text",
    unique_id=123,
    page_index=1,
    local_index=2
)
```

### For FindReplaceResult Users
**Old:**
```python
result.msgid_match_list = [(0, 5), (10, 15)]
result.current_span_idx = 0
result.current_field = "msgid"
```

**New:**
```python
# Using new structure
result.msgid_spans.spans = [(0, 5), (10, 15)]
result.set_current_match("msgid", 0)

# Or migrate existing data
result.migrate_legacy_spans()
```

### For MatchInstance Users
**Old:**
```python
instance = MatchInstance(
    result=find_result,
    field="msgid",
    span_idx=0,
    unique_id=123,
    page_index=1,
    local_index=2
)
```

**New:**
```python
# Direct construction
instance = DatabaseMatchRecord(
    row_index=0,
    unique_id=123,
    page_index=1,
    local_index=2,
    result=find_result,
    field="msgid",
    span_idx=0
)

# Or use factory function
instance = create_match_instance(
    result=find_result,
    field="msgid",
    span_idx=0,
    unique_id=123,
    page_index=1,
    local_index=2,
    row_index=0
)
```

## Benefits

1. **Eliminated Duplication**: Common navigation attributes now in `BaseNavRecord`
2. **Unified Match Handling**: `MatchSpans` class handles all match span operations
3. **Backward Compatibility**: Aliases and migration functions preserve existing code
4. **Better Organization**: Clear separation between file search and database operations
5. **Enhanced Functionality**: Helper methods simplify common operations

## Backward Compatibility

- `SearchNavRecord` is now an alias for `FileSearchRecord`
- `MatchInstance` is now an alias for `DatabaseMatchRecord`
- Legacy fields in `FindReplaceResult` are preserved but deprecated
- Migration functions help convert old data structures
- Factory functions provide convenient creation methods

## Future Considerations

- Legacy fields can be removed in a future version after migration
- Additional match types can easily extend `BaseNavRecord`
- `MatchSpans` can be extended for more complex highlighting needs
