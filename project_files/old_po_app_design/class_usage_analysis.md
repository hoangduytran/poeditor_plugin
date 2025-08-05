# Class Usage Analysis

## AppMode
**File Path**: `gvar.py`

**Inheritance**: Enum

**Docstring**: Application modes for the taskbar

**Methods**:
- None

**Referenced**: `64` times in the project.

---

## MainWindow
**File Path**: `gvar.py`

**Inheritance**: None

**Docstring**: Holds shared application state and widget references.

**Methods**:
- `__init__`

**Referenced**: `34` times in the project.

---

## SyncedHeightTable
**File Path**: `main_gui.py`

**Inheritance**: SelectableTable

**Methods**:
- `resizeEvent`

**Referenced**: `2` times in the project.

---

## POEditorWindow
**File Path**: `main_gui.py`

**Inheritance**: QMainWindow

**Methods**:
- `__init__`
- `_create_widgets`
- `_sync_nav_scrollbar_height`
- `_resize_editors`
- `_create_actions`
- `_create_menu`
- `_connect_actions`
- `apply_shortcuts`
- `_show_find_replace_dialog`
- `_toggle_sidebar`
- `set_gv_vars`
- `showEvent`
- `closeEvent`
- `on_search_results_find_and_replace`
- `show_find_replace_results_in_taskbar`
- `show_matches_in_taskbar`
- `show_span_in_taskbar`
- `highlight_find_replace_match`
- `on_find_and_replace_in_files`
- `on_find_and_replace_goto_match`
- `on_find_and_replace_show_results`
- `show_find_replace_results_dialog`
- `on_table_filter_changed`
- `on_table_selection_changed`
- `on_editor_text_changed`
- `on_taskbar_button_clicked`
- `on_find_and_replace_triggered`
- `on_find_and_replace_closed`
- `on_find_and_replace_find`
- `on_find_and_replace_replace`
- `toggle_minimalistic_mode`
- `_exit_search_mode`
- `_enter_search_mode`
- `_on_find_requested`
- `_on_replace_one_requested`
- `_on_replace_all_requested`
- `_on_findbar_jump`
- `_connect_text_field_signals`
- `_on_table_row_selected_during_search`

**Referenced**: `12` times in the project.

---

## ImportWorker
**File Path**: `main_utils/import_worker.py`

**Inheritance**: QObject

**Methods**:
- `__init__`
- `run`

**Referenced**: `1` times in the project.

---

## POFileTableModel
**File Path**: `main_utils/po_ed_table_model.py`

**Inheritance**: QAbstractTableModel

**Docstring**: Table model for displaying PO entries with columns:
  0: msgid, 1: msgctxt, 2: msgstr, 3: fuzzy, 4: linenum

**Methods**:
- `__init__`
- `set_page_info`
- `rowCount`
- `columnCount`
- `data`
- `headerData`
- `flags`
- `setData`
- `setEntries`
- `entries`
- `set_issue_rows`
- `apply_column_resize_modes`

**Referenced**: `10` times in the project.

---

## PopupMenuManager
**File Path**: `main_utils/popup_mnu.py`

**Inheritance**: QMenu

**Methods**:
- `__new__`
- `__init__`
- `show_for`
- `_copy`
- `_paste`
- `_view_suggestion`
- `_view_all_suggestions`
- `_accept_and_insert`

**Referenced**: `4` times in the project.

---

## SelectableTable
**File Path**: `main_utils/table_widgets.py`

**Inheritance**: QTableView

**Methods**:
- `mousePressEvent`

**Referenced**: `4` times in the project.

---

## PreferencesDialog
**File Path**: `pref/preferences.py`

**Inheritance**: QDialog

**Methods**:
- `__init__`
- `apply_font_settings`
- `save_settings`
- `accept`

**Referenced**: `5` times in the project.

---

## FontSettingsTab
**File Path**: `pref/kbd/font_settings.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `create_font_group`
- `update_component_font`
- `_get_history_table`
- `_get_root_widget`
- `_apply_font_to_preferences`
- `load_settings`
- `save_settings`
- `apply_font_settings`

**Referenced**: `3` times in the project.

---

## KeyboardSettingsTab
**File Path**: `pref/kbd/keyboard_settings.py`

**Inheritance**: QWidget

**Docstring**: A tab that shows all the remappable keyboard shortcuts in a tree:
  - File Menu
  - Table
Each child row has an Action name and an editable QKeySequenceEdit.
Saves/loads to QSettings("POEditor","Settings") under "shortcut/<key>".

**Methods**:
- `__init__`
- `_populate_tree`
- `_add_action_item`
- `load_settings`
- `save_settings`

**Referenced**: `3` times in the project.

---

## ReplacementActions
**File Path**: `pref/repl/replacement_actions.py`

**Inheritance**: None

**Methods**:
- `__init__`
- `import_file`
- `clear_search`
- `export_current`
- `save_edit`
- `delete_selected`
- `on_search_text_changed`
- `on_find`
- `on_prev_match`
- `on_next_match`
- `_highlight_match`
- `_update_buttons_state`
- `on_add`
- `on_delete`

**Referenced**: `3` times in the project.

---

## ReplacementRecord
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: None

**Docstring**: Represents a single text-replacement pair.

**Methods**:
- `__init__`
- `to_dict`
- `from_dict`

**Referenced**: `36` times in the project.

---

## BaseHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: None

**Docstring**: Base interface for import/export handlers.

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `10` times in the project.

---

## PlistHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## JsonHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## CsvHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## YamlHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `3` times in the project.

---

## AHKHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## AclHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## BambooMacroHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## SqliteHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `3` times in the project.

---

## M17nHandler
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: BaseHandler

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `2` times in the project.

---

## ReplacementEngine
**File Path**: `pref/repl/replacement_engine.py`

**Inheritance**: None

**Docstring**: Main engine to import/export across multiple formats.

**Methods**:
- `import_file`
- `export_file`

**Referenced**: `4` times in the project.

---

## ReplacementsDialog
**File Path**: `pref/repl/replacement_gui.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `_on_import`
- `_on_export`
- `_on_search_text_changed`
- `_on_find`
- `_on_prev_match`
- `_on_next_match`
- `_on_cell_activated`
- `_on_add`
- `_on_delete`
- `_on_save_edit`
- `_replacement_refresh_table`
- `_on_header_clicked`

**Referenced**: `20` times in the project.

---

## ReplacementsDialog
**File Path**: `pref/repl/replacement_old.py`

**Inheritance**: QWidget

**Docstring**: Widget encapsulating text replacements management.
Displays a 2-column table, supports search, row highlighting,
editing via bottom panel, drag-and-drop import/export, sorting,
and add/delete via modal dialogs.

**Methods**:
- `__init__`
- `_replacement_refresh_table`
- `_on_search`
- `_on_header_clicked`
- `_on_cell_activated`
- `_save_edit`
- `_clear_search`
- `_import_plist`
- `_load_plist`
- `_export_current`
- `_show_add_dialog`
- `_delete_selected`

**Referenced**: `20` times in the project.

---

## ReplacementSettingsTab
**File Path**: `pref/repl/replacement_settings.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `load_settings`
- `save_settings`

**Referenced**: `3` times in the project.

---

## AdvancedSettingsWidget
**File Path**: `pref/settings/advanced_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `4` times in the project.

---

## AppearanceSettingsWidget
**File Path**: `pref/settings/appearance_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `4` times in the project.

---

## EditorSettingsWidget
**File Path**: `pref/settings/editor_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `_on_font_setting_changed`
- `_on_setting_changed`

**Referenced**: `12` times in the project.

---

## FontSettingsWidget
**File Path**: `pref/settings/font_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `2` times in the project.

---

## GeneralSettingsWidget
**File Path**: `pref/settings/general_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `4` times in the project.

---

## HistorySettingsWidget
**File Path**: `pref/settings/history_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `6` times in the project.

---

## KeyboardSettingsWidget
**File Path**: `pref/settings/keyboard_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `_flatten_actions`
- `_populate_table`
- `reset_shortcut`
- `restore_defaults`
- `save_changes`

**Referenced**: `2` times in the project.

---

## NetworkSettingsWidget
**File Path**: `pref/settings/network_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `4` times in the project.

---

## ReplacementSettingsWidget
**File Path**: `pref/settings/replacement_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `2` times in the project.

---

## TranslationHistorySettingsWidget
**File Path**: `pref/settings/translation_history_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`

**Referenced**: `2` times in the project.

---

## TranslationSettingsWidget
**File Path**: `pref/settings/translation_settings_widget.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `get_enabled_issues`
- `save_settings`
- `load_settings`

**Referenced**: `5` times in the project.

---

## ComboBoxDelegate
**File Path**: `pref/tran_history/db_msgtr_combo.py`

**Inheritance**: QStyledItemDelegate

**Methods**:
- `__init__`
- `createEditor`
- `setEditorData`
- `setModelData`

**Referenced**: `3` times in the project.

---

## TranslationDBRecord
**File Path**: `pref/tran_history/db_record.py`

**Inheritance**: None

**Docstring**: A record from the translation database

**Methods**:
- `update_translation_version`

**Referenced**: `3` times in the project.

---

## HistoryTableModel
**File Path**: `pref/tran_history/history_table_model.py`

**Inheritance**: QAbstractTableModel

**Methods**:
- `__init__`
- `rowCount`
- `columnCount`
- `flags`
- `data`
- `setData`
- `headerData`
- `insertRow`
- `removeRow`
- `refreshData`
- `getData`
- `getColumns`

**Referenced**: `3` times in the project.

---

## PagedSearchNavBar
**File Path**: `pref/tran_history/paged_search_nav_bar.py`

**Inheritance**: QDockWidget

**Docstring**: An enhanced navigation bar that displays search results with paging support.
This handles large result sets more efficiently and provides a more stable UI.

**Methods**:
- `__init__`
- `setTotal`
- `setFoundRecords`
- `update_pagination`
- `go_to_page`
- `update_list_for_page`
- `on_next_page`
- `on_prev_page`
- `on_page_changed`
- `on_item_clicked`
- `highlight_global_item`
- `highlight_local_item`
- `highlight_item`
- `get_record_info`
- `closeEvent`

**Referenced**: `1` times in the project.

---

## DatabasePORecord
**File Path**: `pref/tran_history/tran_db_record.py`

**Inheritance**: None

**Docstring**: In-memory representation of a PO entry and its translation history.
Backed by the TranslationDB singleton (`translation_db`).

**Methods**:
- `__init__`
- `__repr__`
- `is_my_parent`
- `has_tran_text`
- `_normalize`
- `is_virtually_same`
- `_filter_versions`
- `_dedupe_versions`
- `_fuzzy_dedupe`
- `retrieve_from_db`
- `insert_to_db`
- `update_translation_version`
- `delete_record`
- `_persist_versions`
- `update_record_with_changes`
- `add_version_mem`
- `delete_version_mem`
- `reverse_versions_mem`
- `_renumber_versions`

**Referenced**: `82` times in the project.

---

## NavBar
**File Path**: `pref/tran_history/tran_navbar.py`

**Inheritance**: QDockWidget

**Methods**:
- `__init__`
- `setHighlights`
- `setTotal`
- `_on_item_clicked`
- `set_items`
- `get_items`
- `clear`

**Referenced**: `12` times in the project.

---

## TranslationRecord
**File Path**: `pref/tran_history/tran_record.py`

**Inheritance**: None

**Docstring**: A record from the translation history database

**Methods**:
- None

**Referenced**: `7` times in the project.

---

## FoundRecord
**File Path**: `pref/tran_history/tran_search_nav_bar.py`

**Inheritance**: None

**Methods**:
- None

**Referenced**: `5` times in the project.

---

## SearchNavBar
**File Path**: `pref/tran_history/tran_search_nav_bar.py`

**Inheritance**: QDockWidget

**Docstring**: A custom navigation bar that displays a list of found record indices.
Clicking on an item will emit a signal to jump to that record.
It is dockable in the main window.

**Methods**:
- `__init__`
- `setTotal`
- `setResults`
- `updateList`
- `on_item_clicked`
- `highlight_item`
- `get_record_info`
- `_adjust_list_to_width`
- `resizeEvent`
- `closeEvent`

**Referenced**: `11` times in the project.

---

## TranslationDB
**File Path**: `pref/tran_history/translation_db.py`

**Inheritance**: None

**Docstring**: Encapsulates all SQLite logic for translation history storage.
Queries always fetch all matching rows before indexing, and handle `context` = None
by generating separate queries for NULL vs. non-NULL context.

**Methods**:
- `__init__`
- `_regexp`
- `_ensure_schema`
- `clear_database`
- `_fetch_english`
- `_fetch_translations`
- `list_entries`
- `english_text_count`
- `list_entries_page`
- `get_entry`
- `add_entry`
- `update_entry`
- `add_version`
- `get_entry_by_id`
- `delete_entry`
- `delete_version`
- `insert_po_entry`
- `get_entry_from_po_entry`
- `import_po_fast`
- `export_po`
- `get_all_contexts`
- `_search_msgid`
- `_search_msgstr`
- `search_entries`
- `fetch_entries_by_ids`
- `update_version`
- `close`
- `replace_found`

**Referenced**: `20` times in the project.

---

## ImportDictTypeDialog
**File Path**: `pref/tran_history/translation_db_gui.py`

**Inheritance**: QDialog

**Methods**:
- `__init__`
- `_on_combo_changed`
- `selected_dict_type`

**Referenced**: `2` times in the project.

---

## TranslationHistoryDialog
**File Path**: `pref/tran_history/translation_db_gui.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `_on_mode_changed`
- `_clear_search_state`
- `_emit_clear_all_signal`
- `_is_in_search_mode`
- `_switch_to_database_view`
- `_refresh_view`
- `_refresh_database_view`
- `_refresh_search_view`
- `_on_page_requested`
- `_navigate_to_page`
- `_go_to_last_page`
- `_go_to_next_page`
- `_go_to_prev_page`
- `_configure_table_columns`
- `_on_header_clicked`
- `_sort_search_results`
- `_on_row_selected`
- `_jump_to_instance`
- `_highlight_instance_in_editor`
- `_build_match_instances`
- `_build_match_pairs`
- `_jump_to_pair`
- `_highlight_pair_matches`
- `_update_pair_navigation_status`
- `_navigate_to_next_row_first_pair`
- `_navigate_to_prev_row_last_pair`
- `_on_find_requested`
- `_on_replace_one_requested`
- `_on_replace_all_requested`
- `_on_findbar_jump`
- `_navigate_pairs`
- `_navigate_instances`
- `_load_database_page`
- `_load_search_page`
- `_update_translation_editor_with_record`
- `_on_translation_edited`
- `_on_fuzzy_changed`
- `_on_translation_saved`
- `_on_version_selected`
- `save_translation`
- `_on_import`
- `_on_export`
- `_clear_all`
- `_on_edit_entry`
- `_on_delete_entry`
- `_init_editor_state`
- `_apply_keyboard_shortcuts`
- `_connect_editor_settings_signals`
- `_on_editor_settings_changed`
- `dragEnterEvent`
- `dropEvent`
- `saveState`
- `restoreState`
- `closeEvent`
- `showEvent`

**Referenced**: `12` times in the project.

---

## VersionTableModel
**File Path**: `pref/tran_history/versions/tran_edit_version_tbl_model.py`

**Inheritance**: QAbstractTableModel

**Docstring**: Table model for displaying the msgstr_versions of a DatabasePORecord:
column 0 = version_id, column 1 = translation text, column 2 = source.

**Methods**:
- `__init__`
- `rowCount`
- `columnCount`
- `data`
- `headerData`
- `clear`
- `setRecord`
- `record`
- `refresh`

**Referenced**: `5` times in the project.

---

## _EntryDialog
**File Path**: `pref/tran_history/versions/tran_entry_edit_dlg.py`

**Inheritance**: QDialog

**Methods**:
- `__init__`
- `on_add`
- `on_delete`
- `on_edit`
- `on_save`
- `on_cancel`
- `reject`

**Referenced**: `5` times in the project.

---

## TransVersionEditor
**File Path**: `pref/tran_history/versions/tran_version_editor.py`

**Inheritance**: QDialog

**Docstring**: Dialog to add or edit a single translation version.

**Methods**:
- `__init__`

**Referenced**: `4` times in the project.

---

## SearchRequest
**File Path**: `search/fast_search.py`

**Inheritance**: None

**Docstring**: Encapsulates parameters for a search.
Attributes:
    root_path: str - directory to search
    keyword: str - search string or pattern
    glob_patterns: list[str] or None - file patterns to include
    use_regex: bool - whether to use regex engine
    ignore_case: bool - case-insensitive flag for regex
    context: int - number of chars to include around match

**Methods**:
- `__init__`

**Referenced**: `12` times in the project.

---

## SearchResult
**File Path**: `search/fast_search.py`

**Inheritance**: None

**Docstring**: Holds a single match result.
Attributes:
    filepath: str
    line: int
    column: int
    preview: str

**Methods**:
- `__init__`

**Referenced**: `57` times in the project.

---

## SearchRequest
**File Path**: `search/fast_search_open_ext_editor.py`

**Inheritance**: None

**Docstring**: Search parameters container.

Attributes:
    root_path (str): Directory to search.
    keyword (str): Search term or regex.
    glob_patterns (list[str]|None): File patterns to include.
    use_regex (bool): Regex mode flag.
    ignore_case (bool): Case-insensitive for regex.
    context (int): Preview characters around match.
    open_results (bool): Open matches externally.
    show_progress (bool): Display progress bar.

**Methods**:
- `__init__`

**Referenced**: `12` times in the project.

---

## SearchResult
**File Path**: `search/fast_search_open_ext_editor.py`

**Inheritance**: None

**Docstring**: Represents a single match.

Attributes:
    filepath (str): File path.
    line (int): 1-based line number.
    column (int): 0-based column offset.
    preview (str): Context snippet.

**Methods**:
- `__init__`

**Referenced**: `57` times in the project.

---

## PaginationMode
**File Path**: `subcmp/find_replace_manager.py`

**Inheritance**: Enum

**Docstring**: Defines the current pagination mode

**Methods**:
- None

**Referenced**: `20` times in the project.

---

## PageInfo
**File Path**: `subcmp/find_replace_manager.py`

**Inheritance**: None

**Docstring**: Information about a specific page

**Methods**:
- None

**Referenced**: `10` times in the project.

---

## DatabasePager
**File Path**: `subcmp/find_replace_manager.py`

**Inheritance**: Protocol

**Docstring**: Protocol for database pagination operations

**Methods**:
- `get_total_records`
- `get_page`

**Referenced**: `10` times in the project.

---

## FindReplaceManager
**File Path**: `subcmp/find_replace_manager.py`

**Inheritance**: QObject

**Docstring**: Professional manager for handling both database pagination and search results.

This class provides a unified interface that allows the same TableView to display
either regular database pages or search result pages, with seamless navigation
between both modes.

**Methods**:
- `__init__`
- `set_database_pager`
- `set_page_size`
- `set_search_results`
- `clear_search_results`
- `go_to_page`
- `go_first`
- `go_last`
- `go_next`
- `go_prev`
- `get_page_info`
- `get_current_records`
- `find_record_page`
- `can_go_prev`
- `can_go_next`
- `get_page_range_info`
- `_update_database_info`
- `_update_search_info`
- `_get_total_pages`
- `_get_total_records`
- `_load_current_page`
- `_load_database_page`
- `_load_search_page`
- `_cache_page`
- `_clear_cache`

**Referenced**: `15` times in the project.

---

## TableViewAdapter
**File Path**: `subcmp/find_replace_manager.py`

**Inheritance**: None

**Docstring**: Adapter class to integrate FindReplaceManager with a TableView.

This class handles the connection between the manager and the table view,
providing methods to update the table based on the current pagination mode.

**Methods**:
- `__init__`
- `update_table_with_records`
- `update_table_with_search_results`
- `handle_mode_change`
- `query_database_by_ids`
- `apply_search_highlighting`

**Referenced**: `9` times in the project.

---

## DatabasePagerImpl
**File Path**: `subcmp/find_replace_manager.py`

**Inheritance**: None

**Docstring**: Example implementation of DatabasePager protocol

**Methods**:
- `__init__`
- `get_total_records`
- `get_page`

**Referenced**: `2` times in the project.

---

## ReplacementLineEdit
**File Path**: `subcmp/line_rep_imp.py`

**Inheritance**: QLineEdit, ReplacementBase

**Methods**:
- `__init__`
- `keyPressEvent`
- `apply_replacement_logic`
- `set_cursor_position`

**Referenced**: `6` times in the project.

---

## NewTaskbar
**File Path**: `subcmp/new_taskbar.py`

**Inheritance**: QFrame

**Docstring**: A new streamlined taskbar widget with specific action buttons.
Replaces mode switching with direct action buttons.

**Methods**:
- `__init__`
- `_setup_ui`
- `_create_button`
- `_setup_shortcuts`
- `_on_button_clicked`
- `connect_callback`
- `set_button_enabled`
- `set_button_checked`
- `get_button_keys`

**Referenced**: `3` times in the project.

---

## NavRecord
**File Path**: `subcmp/paged_nav_scrollbar.py`

**Inheritance**: None

**Docstring**: Represents a single record in the navigation bar

**Methods**:
- None

**Referenced**: `21` times in the project.

---

## PagedNavScrollbar
**File Path**: `subcmp/paged_nav_scrollbar.py`

**Inheritance**: QDockWidget

**Docstring**: A component that combines SearchNavBar and TransparentMarkerScrollbar.

The left side displays search results with details for the current page,
while the right side provides navigation for all pages.

**Methods**:
- `__init__`
- `set_total_records`
- `set_records`
- `update_pagination`
- `go_to_page`
- `update_list_for_page`
- `on_next_page`
- `on_prev_page`
- `on_page_changed`
- `on_item_clicked`
- `highlight_global_item`
- `highlight_local_item`
- `highlight_item`
- `set_page_size`
- `_adjust_items_to_width`
- `resizeEvent`
- `closeEvent`
- `update_page_info`

**Referenced**: `57` times in the project.

---

## RecordMarkerBar
**File Path**: `subcmp/record_marker_bar.py`

**Inheritance**: QWidget

**Docstring**: A visual marker bar with transparent slider for smooth navigation

**Methods**:
- `__init__`
- `set_records`
- `set_highlight`
- `clear_highlight`
- `set_slider_position`
- `_animate_slider_to`
- `paintEvent`
- `_draw_markers`
- `_draw_slider`
- `mousePressEvent`
- `mouseMoveEvent`
- `mouseReleaseEvent`
- `leaveEvent`
- `_is_point_on_slider`
- `_update_slider_from_mouse`
- `_get_marker_at_pos`
- `slider_position_property`
- `slider_position_property`

**Referenced**: `6` times in the project.

---

## ReplacementBase
**File Path**: `subcmp/replacement_base.py`

**Inheritance**: None

**Methods**:
- `__init__`
- `_load_replacements`
- `apply_replacement`

**Referenced**: `8` times in the project.

---

## PagingScrollBar
**File Path**: `subcmp/table_nav_scrollbar.py`

**Inheritance**: QWidget

**Methods**:
- `__init__`
- `set_total_pages`
- `set_current_page`
- `_on_slider_changed`
- `_on_first`
- `_on_last`
- `_on_prev`
- `_on_next`
- `_update_slider_window`
- `_tooltip`

**Referenced**: `20` times in the project.

---

## TablePagerBase
**File Path**: `subcmp/table_nav_widget.py`

**Inheritance**: QObject

**Docstring**: Abstract paging controller for table widgets. Handles page navigation, page size, and emits signals for UI updates.
Subclass and implement update_table_view() to show only rows for the current page.

**Methods**:
- `__init__`
- `_connect_signals`
- `_on_model_reset`
- `update_table_view`
- `go_to_page`
- `go_first`
- `go_last`
- `go_prev`
- `go_next`
- `set_page_size`
- `get_page_info`
- `get_page_indices`
- `refresh`
- `ensure_row_visible`
- `handle_key_event`

**Referenced**: `4` times in the project.

---

## Taskbar
**File Path**: `subcmp/taskbar.py`

**Inheritance**: QFrame

**Docstring**: A taskbar widget that allows switching between different application modes
and provides context-sensitive controls for each mode.

**Methods**:
- `__init__`
- `_setup_ui`
- `_update_controls_visibility`
- `_on_mode_selected`
- `_on_nav_prev`
- `_on_nav_next`
- `set_mode`
- `update_navigation_count`
- `set_status_text`
- `_get_main_window`

**Referenced**: `24` times in the project.

---

## ReplacementTextEdit
**File Path**: `subcmp/text_rep_imp.py`

**Inheritance**: QTextEdit, ReplacementBase

**Methods**:
- `__init__`
- `_match_case`
- `keyPressEvent`
- `apply_replacement_logic`
- `set_cursor_position`

**Referenced**: `22` times in the project.

---

## TranslationEditorWidget
**File Path**: `subcmp/translation_edit_widget.py`

**Inheritance**: QWidget

**Docstring**: A reusable widget for editing translation entries with source and target fields.
Similar to the layout in main_gui.py, but designed to be instantiated multiple times.

Features:
- Source field (msgid) with label
- Translation field (msgstr) with label
- "Needs Work" checkbox (fuzzy flag)
- Support for multiple translation fields (plurals)

**Methods**:
- `__init__`
- `_create_widgets`
- `_setup_layout`
- `_connect_signals`
- `resizeEvent`
- `showEvent`
- `_apply_global_fonts`
- `_on_fuzzy_changed`
- `_on_source_changed`
- `_on_translation_changed`
- `set_source_text`
- `set_translation_text`
- `get_source_text`
- `get_translation_text`
- `set_fuzzy`
- `get_fuzzy`
- `add_translation_field`
- `clear`

**Referenced**: `27` times in the project.

---

## PluralTranslationEditorWidget
**File Path**: `subcmp/translation_edit_widget.py`

**Inheritance**: TranslationEditorWidget

**Docstring**: A specialized version of TranslationEditorWidget with built-in
support for multiple translation fields (plural forms).

**Methods**:
- `__init__`

**Referenced**: `3` times in the project.

---

## FindReplaceResult
**File Path**: `subcmp/transparent_marker_scrollbar.py`

**Inheritance**: None

**Methods**:
- None

**Referenced**: `296` times in the project.

---

## TransparentMarkerScrollbar
**File Path**: `subcmp/transparent_marker_scrollbar.py`

**Inheritance**: QWidget

**Docstring**: PyCharm-inspired transparent vertical marker bar with page indicators

This is a replacement for PagingScrollBar that shows all pages as markers
in the scrollbar, with a transparent overlay slider.

**Methods**:
- `__init__`
- `setResults`
- `paintEvent`
- `mousePressEvent`
- `mouseMoveEvent`
- `mouseReleaseEvent`
- `leaveEvent`
- `_position_to_page`
- `navigate_to_page`
- `_on_first`
- `_on_last`
- `_on_prev`
- `_on_next`
- `_update_button_states`
- `_tooltip`
- `_calculate_slider_dimensions`
- `set_current_page`
- `set_total_pages`
- `set_minimalistic_mode`
- `is_minimalistic_mode`
- `get_current_page`
- `get_total_pages`
- `has_results`
- `get_results_count`

**Referenced**: `42` times in the project.

---

## VersionedTranslationWidget
**File Path**: `subcmp/versioned_translation_widget.py`

**Inheritance**: QWidget

**Docstring**: A widget for editing translation entries with support for multiple versions.
Instead of showing multiple editors vertically, it uses a combobox to select
which version to edit.

Features:
- Source field (msgid) with label
- Translation field (msgstr) with label
- "Needs Work" checkbox (fuzzy flag)
- Version selector (combobox) for multiple translations
- Save button to commit changes to the current version
- Resizable panels with standard QSplitter handle

**Methods**:
- `__init__`
- `_create_widgets`
- `_setup_layout`
- `_connect_signals`
- `_on_fuzzy_changed`
- `_on_source_changed`
- `_on_translation_text_changed`
- `_on_version_selected`
- `_on_save_clicked`
- `_save_current_version`
- `resizeEvent`
- `showEvent`
- `_apply_global_fonts`
- `set_source_text`
- `set_translation_text`
- `get_source_text`
- `get_translation_text`
- `set_fuzzy`
- `get_fuzzy`
- `set_version_count`
- `get_version_count`
- `_ensure_version_count`
- `clear`
- `select_version`
- `highlight_text`
- `highlight_text_instance`
- `highlight_paired_matches`
- `clear_highlighting`
- `clear`
- `highlight_row_matches`

**Referenced**: `29` times in the project.

---

## SuggestionController
**File Path**: `sugg/suggestion_controller.py`

**Inheritance**: None

**Docstring**: Handles suggestion logic on table row changes and integrates with the translation history DB.

**Methods**:
- `__init__`
- `on_row_change`
- `_commit_previous_suggestion`
- `_update_global_po_state`
- `_populate_editors`
- `_load_new_entry`
- `_clear_all_panes`

**Referenced**: `3` times in the project.

---

## Suggestor
**File Path**: `sugg/translate.py`

**Inheritance**: QObject

**Methods**:
- None

**Referenced**: `2` times in the project.

---

## TranslateTask
**File Path**: `sugg/translate.py`

**Inheritance**: QRunnable

**Methods**:
- `__init__`
- `run`

**Referenced**: `5` times in the project.

---

## ButtonSymbol
**File Path**: `workspace/button_symbols.py`

**Inheritance**: Enum

**Methods**:
- `__init__`

**Referenced**: `57` times in the project.

---

## FlagLineEdit
**File Path**: `workspace/find_replace_bar.py`

**Inheritance**: ReplacementTextEdit

**Docstring**: A QTextEdit for search/replace, visually single-line, with flag buttons inside the text field.

**Methods**:
- `__init__`
- `resizeEvent`
- `_update_flag_widget_pos`
- `mousePressEvent`
- `keyPressEvent`
- `insertFromMimeData`
- `text`
- `_on_flag_changed`

**Referenced**: `4` times in the project.

---

## FindReplaceBar
**File Path**: `workspace/find_replace_bar.py`

**Inheritance**: QWidget

**Docstring**: Collapsible Find/Replace bar with flags and navigation.

**Methods**:
- `__init__`
- `_build_ui`
- `_sync_textfield_widths`
- `_connect_signals`
- `_on_find_return`
- `_on_replace_return`
- `_on_flag_changed`
- `_on_toggle_clicked`
- `_on_toggle`
- `_lock_to_one_row`
- `_collapse_replace_row`
- `_sync_widths`
- `showEvent`
- `resizeEvent`
- `_emit_find`
- `_emit_replace`
- `setStatus`
- `setHighlightedMatch`
- `refresh_contexts`
- `find_edit`
- `fill_context_combo`
- `focus_find_field`
- `set_issues_mode`
- `update_navigation_status`

**Referenced**: `16` times in the project.

---

## FindReplaceResultsDialog
**File Path**: `workspace/find_replace_results_dialog.py`

**Inheritance**: QDialog

**Docstring**: Dialog for viewing and navigating only find/replace results.
Uses paging system similar to translation_db_gui.py for large result sets.

**Methods**:
- `__init__`
- `_create_widgets`
- `_setup_layout`
- `_connect_signals`
- `_connect_to_font_settings`
- `_apply_font_settings`
- `_on_font_settings_changed`
- `_on_find_requested`
- `_on_replace_one_requested`
- `_on_replace_all_requested`
- `_on_jump_requested`
- `_navigate_instances`
- `_navigate_pairs`
- `_jump_to_pair`
- `_build_match_instances`
- `_jump_to_instance`
- `_load_current_page`
- `_optimize_column_sizes`
- `_navigate_to_page`
- `_on_page_requested`
- `_go_to_last_page`
- `_go_to_next_page`
- `_go_to_prev_page`
- `_update_page_info`
- `_on_row_changed`
- `_on_row_double_clicked`
- `_highlight_matches_in_editor`
- `_apply_font_settings`
- `_on_font_settings_changed`

**Referenced**: `9` times in the project.

---

## FindReplaceTableModel
**File Path**: `workspace/find_replace_results_dialog.py`

**Inheritance**: POFileTableModel

**Docstring**: Table model for displaying find/replace results

**Methods**:
- `__init__`
- `set_records`
- `rowCount`
- `columnCount`
- `data`
- `headerData`

**Referenced**: `2` times in the project.

---

## ReplacementCaseMatch
**File Path**: `workspace/find_replace_support_functions.py`

**Inheritance**: Enum

**Methods**:
- None

**Referenced**: `66` times in the project.

---

## PagingMode
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: Enum

**Docstring**: Paging modes for the TranslationHistoryDialog

**Methods**:
- None

**Referenced**: `19` times in the project.

---

## EmptyMode
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: Enum

**Methods**:
- None

**Referenced**: `35` times in the project.

---

## FindReplaceScope
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: Enum

**Methods**:
- None

**Referenced**: `12` times in the project.

---

## FindReplaceOperation
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: Enum

**Methods**:
- None

**Referenced**: `3` times in the project.

---

## ReplacementCaseMatch
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: Enum

**Methods**:
- None

**Referenced**: `66` times in the project.

---

## FindReplaceRequest
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: None

**Methods**:
- None

**Referenced**: `40` times in the project.

---

## MatchInstance
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: None

**Docstring**: Represents a single match instance for precise navigation

**Methods**:
- None

**Referenced**: `32` times in the project.

---

## FindReplaceResult
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: None

**Methods**:
- None

**Referenced**: `296` times in the project.

---

## MatchPair
**File Path**: `workspace/find_replace_types.py`

**Inheritance**: None

**Docstring**: Represents a synchronized pair of msgid/msgstr matches for AND navigation

**Methods**:
- None

**Referenced**: `16` times in the project.

---

## IssueOnlyDialog
**File Path**: `workspace/issue_only_dialog.py`

**Inheritance**: QDialog

**Docstring**: Dialog for viewing and navigating only translation records that have issues.
Similar to TranslationHistoryDialog but focused on issue records.

All pagination is handled by TransparentMarkerScrollbar.

**Methods**:
- `__init__`
- `_create_widgets`
- `_setup_layout`
- `_connect_signals`
- `_load_issue_records`
- `_load_from_issue_records`
- `_load_from_direct_scan`
- `_init_pagination`
- `_load_current_page_data`
- `_navigate_to_page`
- `_optimize_column_sizes`
- `_on_row_changed`
- `_update_translation_editor`
- `_on_row_double_clicked`
- `_on_goto_record`
- `_show_find_bar`
- `_on_escape`
- `_on_find_requested`
- `_on_jump_requested`
- `setResultsToScrollbar`

**Referenced**: `8` times in the project.

---

## IssueTableModel
**File Path**: `workspace/issue_only_dialog.py`

**Inheritance**: POFileTableModel

**Docstring**: Table model for displaying issue records

**Methods**:
- `__init__`
- `set_records`
- `rowCount`
- `columnCount`
- `data`
- `headerData`

**Referenced**: `8` times in the project.

---

## IssueOnlyDialog
**File Path**: `workspace/issue_only_dialog_paged.py`

**Inheritance**: QDialog

**Docstring**: Dialog for viewing and navigating only translation records that have issues.
Similar to TranslationHistoryDialog but focused on issue records.

**Methods**:
- `__init__`
- `_create_widgets`
- `_setup_layout`
- `_connect_signals`
- `_load_issue_records`
- `_load_from_issue_records`
- `_load_from_direct_scan`
- `_init_pagination`
- `_update_page_indicator`
- `_load_current_page`
- `_go_to_page`
- `_go_to_next_page`
- `_go_to_prev_page`
- `_on_page_value_changed`
- `_on_page_size_changed`
- `_optimize_column_sizes`
- `_on_row_changed`
- `_update_translation_editor`
- `_on_row_double_clicked`
- `_on_goto_record`
- `_show_find_bar`
- `_on_escape`
- `_on_find_requested`
- `_on_jump_requested`

**Referenced**: `8` times in the project.

---

## IssueTableModel
**File Path**: `workspace/issue_only_dialog_paged.py`

**Inheritance**: POFileTableModel

**Docstring**: Table model for displaying issue records

**Methods**:
- `__init__`
- `set_records`
- `rowCount`
- `columnCount`
- `data`
- `headerData`

**Referenced**: `8` times in the project.

---

## ModeState
**File Path**: `workspace/mode_record.py`

**Inheritance**: None

**Docstring**: Represents the state for a specific mode

**Methods**:
- None

**Referenced**: `13` times in the project.

---

## ModeRecord
**File Path**: `workspace/mode_record.py`

**Inheritance**: None

**Docstring**: Manages mode-specific states and provides seamless switching between modes.

This class stores the current state for each mode (EDITOR, SEARCH, ISSUES) including:
- Current page index and local position
- Selected unique_id and row information
- Search results and navigation state
- UI state like scroll position and selections

When switching modes, it preserves the state of the previous mode and restores
the state of the target mode, enabling seamless navigation.

**Methods**:
- `__init__`
- `get_current_state`
- `get_state`
- `switch_to_mode`
- `update_current_position`
- `update_search_state`
- `update_issues_state`
- `clear_mode_state`
- `has_previous_mode`
- `return_to_previous_mode`
- `store_edit_position`
- `store_search_position`
- `get_navigation_info`
- `should_auto_switch_to_search`
- `get_mode_summary`
- `sync_show_issues_state`
- `should_keep_issues_highlighting`
- `_update_state_attributes`

**Referenced**: `10` times in the project.

---

## SearchResult
**File Path**: `workspace/mode_record_integration_guide.py`

**Inheritance**: None

**Docstring**: Base class for search results to ensure consistent interface

**Methods**:
- `__init__`

**Referenced**: `57` times in the project.

---

## 🔢 Class Usage Count (Descending)

| Class Name | File Path | Times Referenced |
|------------|-----------|------------------|
| `FindReplaceResult` | `subcmp/transparent_marker_scrollbar.py` | 296 |
| `FindReplaceResult` | `workspace/find_replace_types.py` | 296 |
| `DatabasePORecord` | `pref/tran_history/tran_db_record.py` | 82 |
| `ReplacementCaseMatch` | `workspace/find_replace_support_functions.py` | 66 |
| `ReplacementCaseMatch` | `workspace/find_replace_types.py` | 66 |
| `AppMode` | `gvar.py` | 64 |
| `SearchResult` | `search/fast_search.py` | 57 |
| `SearchResult` | `search/fast_search_open_ext_editor.py` | 57 |
| `PagedNavScrollbar` | `subcmp/paged_nav_scrollbar.py` | 57 |
| `ButtonSymbol` | `workspace/button_symbols.py` | 57 |
| `SearchResult` | `workspace/mode_record_integration_guide.py` | 57 |
| `TransparentMarkerScrollbar` | `subcmp/transparent_marker_scrollbar.py` | 42 |
| `FindReplaceRequest` | `workspace/find_replace_types.py` | 40 |
| `ReplacementRecord` | `pref/repl/replacement_engine.py` | 36 |
| `EmptyMode` | `workspace/find_replace_types.py` | 35 |
| `MainWindow` | `gvar.py` | 34 |
| `MatchInstance` | `workspace/find_replace_types.py` | 32 |
| `VersionedTranslationWidget` | `subcmp/versioned_translation_widget.py` | 29 |
| `TranslationEditorWidget` | `subcmp/translation_edit_widget.py` | 27 |
| `Taskbar` | `subcmp/taskbar.py` | 24 |
| `ReplacementTextEdit` | `subcmp/text_rep_imp.py` | 22 |
| `NavRecord` | `subcmp/paged_nav_scrollbar.py` | 21 |
| `ReplacementsDialog` | `pref/repl/replacement_gui.py` | 20 |
| `ReplacementsDialog` | `pref/repl/replacement_old.py` | 20 |
| `TranslationDB` | `pref/tran_history/translation_db.py` | 20 |
| `PaginationMode` | `subcmp/find_replace_manager.py` | 20 |
| `PagingScrollBar` | `subcmp/table_nav_scrollbar.py` | 20 |
| `PagingMode` | `workspace/find_replace_types.py` | 19 |
| `FindReplaceBar` | `workspace/find_replace_bar.py` | 16 |
| `MatchPair` | `workspace/find_replace_types.py` | 16 |
| `FindReplaceManager` | `subcmp/find_replace_manager.py` | 15 |
| `ModeState` | `workspace/mode_record.py` | 13 |
| `POEditorWindow` | `main_gui.py` | 12 |
| `EditorSettingsWidget` | `pref/settings/editor_settings_widget.py` | 12 |
| `NavBar` | `pref/tran_history/tran_navbar.py` | 12 |
| `TranslationHistoryDialog` | `pref/tran_history/translation_db_gui.py` | 12 |
| `SearchRequest` | `search/fast_search.py` | 12 |
| `SearchRequest` | `search/fast_search_open_ext_editor.py` | 12 |
| `FindReplaceScope` | `workspace/find_replace_types.py` | 12 |
| `SearchNavBar` | `pref/tran_history/tran_search_nav_bar.py` | 11 |
| `POFileTableModel` | `main_utils/po_ed_table_model.py` | 10 |
| `BaseHandler` | `pref/repl/replacement_engine.py` | 10 |
| `PageInfo` | `subcmp/find_replace_manager.py` | 10 |
| `DatabasePager` | `subcmp/find_replace_manager.py` | 10 |
| `ModeRecord` | `workspace/mode_record.py` | 10 |
| `TableViewAdapter` | `subcmp/find_replace_manager.py` | 9 |
| `FindReplaceResultsDialog` | `workspace/find_replace_results_dialog.py` | 9 |
| `ReplacementBase` | `subcmp/replacement_base.py` | 8 |
| `IssueOnlyDialog` | `workspace/issue_only_dialog.py` | 8 |
| `IssueTableModel` | `workspace/issue_only_dialog.py` | 8 |
| `IssueOnlyDialog` | `workspace/issue_only_dialog_paged.py` | 8 |
| `IssueTableModel` | `workspace/issue_only_dialog_paged.py` | 8 |
| `TranslationRecord` | `pref/tran_history/tran_record.py` | 7 |
| `HistorySettingsWidget` | `pref/settings/history_settings_widget.py` | 6 |
| `ReplacementLineEdit` | `subcmp/line_rep_imp.py` | 6 |
| `RecordMarkerBar` | `subcmp/record_marker_bar.py` | 6 |
| `PreferencesDialog` | `pref/preferences.py` | 5 |
| `TranslationSettingsWidget` | `pref/settings/translation_settings_widget.py` | 5 |
| `FoundRecord` | `pref/tran_history/tran_search_nav_bar.py` | 5 |
| `VersionTableModel` | `pref/tran_history/versions/tran_edit_version_tbl_model.py` | 5 |
| `_EntryDialog` | `pref/tran_history/versions/tran_entry_edit_dlg.py` | 5 |
| `TranslateTask` | `sugg/translate.py` | 5 |
| `PopupMenuManager` | `main_utils/popup_mnu.py` | 4 |
| `SelectableTable` | `main_utils/table_widgets.py` | 4 |
| `ReplacementEngine` | `pref/repl/replacement_engine.py` | 4 |
| `AdvancedSettingsWidget` | `pref/settings/advanced_settings_widget.py` | 4 |
| `AppearanceSettingsWidget` | `pref/settings/appearance_settings_widget.py` | 4 |
| `GeneralSettingsWidget` | `pref/settings/general_settings_widget.py` | 4 |
| `NetworkSettingsWidget` | `pref/settings/network_settings_widget.py` | 4 |
| `TransVersionEditor` | `pref/tran_history/versions/tran_version_editor.py` | 4 |
| `TablePagerBase` | `subcmp/table_nav_widget.py` | 4 |
| `FlagLineEdit` | `workspace/find_replace_bar.py` | 4 |
| `FontSettingsTab` | `pref/kbd/font_settings.py` | 3 |
| `KeyboardSettingsTab` | `pref/kbd/keyboard_settings.py` | 3 |
| `ReplacementActions` | `pref/repl/replacement_actions.py` | 3 |
| `YamlHandler` | `pref/repl/replacement_engine.py` | 3 |
| `SqliteHandler` | `pref/repl/replacement_engine.py` | 3 |
| `ReplacementSettingsTab` | `pref/repl/replacement_settings.py` | 3 |
| `ComboBoxDelegate` | `pref/tran_history/db_msgtr_combo.py` | 3 |
| `TranslationDBRecord` | `pref/tran_history/db_record.py` | 3 |
| `HistoryTableModel` | `pref/tran_history/history_table_model.py` | 3 |
| `NewTaskbar` | `subcmp/new_taskbar.py` | 3 |
| `PluralTranslationEditorWidget` | `subcmp/translation_edit_widget.py` | 3 |
| `SuggestionController` | `sugg/suggestion_controller.py` | 3 |
| `FindReplaceOperation` | `workspace/find_replace_types.py` | 3 |
| `SyncedHeightTable` | `main_gui.py` | 2 |
| `PlistHandler` | `pref/repl/replacement_engine.py` | 2 |
| `JsonHandler` | `pref/repl/replacement_engine.py` | 2 |
| `CsvHandler` | `pref/repl/replacement_engine.py` | 2 |
| `AHKHandler` | `pref/repl/replacement_engine.py` | 2 |
| `AclHandler` | `pref/repl/replacement_engine.py` | 2 |
| `BambooMacroHandler` | `pref/repl/replacement_engine.py` | 2 |
| `M17nHandler` | `pref/repl/replacement_engine.py` | 2 |
| `FontSettingsWidget` | `pref/settings/font_settings_widget.py` | 2 |
| `KeyboardSettingsWidget` | `pref/settings/keyboard_settings_widget.py` | 2 |
| `ReplacementSettingsWidget` | `pref/settings/replacement_settings_widget.py` | 2 |
| `TranslationHistorySettingsWidget` | `pref/settings/translation_history_settings_widget.py` | 2 |
| `ImportDictTypeDialog` | `pref/tran_history/translation_db_gui.py` | 2 |
| `DatabasePagerImpl` | `subcmp/find_replace_manager.py` | 2 |
| `Suggestor` | `sugg/translate.py` | 2 |
| `FindReplaceTableModel` | `workspace/find_replace_results_dialog.py` | 2 |
| `ImportWorker` | `main_utils/import_worker.py` | 1 |
| `PagedSearchNavBar` | `pref/tran_history/paged_search_nav_bar.py` | 1 |

---
## 🔤 Class Reference Table (Alphabetical)

| Class Name | File Path | Times Referenced |
|------------|-----------|------------------|
| `_EntryDialog` | `pref/tran_history/versions/tran_entry_edit_dlg.py` | 5 |
| `AclHandler` | `pref/repl/replacement_engine.py` | 2 |
| `AdvancedSettingsWidget` | `pref/settings/advanced_settings_widget.py` | 4 |
| `AHKHandler` | `pref/repl/replacement_engine.py` | 2 |
| `AppearanceSettingsWidget` | `pref/settings/appearance_settings_widget.py` | 4 |
| `AppMode` | `gvar.py` | 64 |
| `BambooMacroHandler` | `pref/repl/replacement_engine.py` | 2 |
| `BaseHandler` | `pref/repl/replacement_engine.py` | 10 |
| `ButtonSymbol` | `workspace/button_symbols.py` | 57 |
| `ComboBoxDelegate` | `pref/tran_history/db_msgtr_combo.py` | 3 |
| `CsvHandler` | `pref/repl/replacement_engine.py` | 2 |
| `DatabasePager` | `subcmp/find_replace_manager.py` | 10 |
| `DatabasePagerImpl` | `subcmp/find_replace_manager.py` | 2 |
| `DatabasePORecord` | `pref/tran_history/tran_db_record.py` | 82 |
| `EditorSettingsWidget` | `pref/settings/editor_settings_widget.py` | 12 |
| `EmptyMode` | `workspace/find_replace_types.py` | 35 |
| `FindReplaceBar` | `workspace/find_replace_bar.py` | 16 |
| `FindReplaceManager` | `subcmp/find_replace_manager.py` | 15 |
| `FindReplaceOperation` | `workspace/find_replace_types.py` | 3 |
| `FindReplaceRequest` | `workspace/find_replace_types.py` | 40 |
| `FindReplaceResult` | `subcmp/transparent_marker_scrollbar.py` | 296 |
| `FindReplaceResult` | `workspace/find_replace_types.py` | 296 |
| `FindReplaceResultsDialog` | `workspace/find_replace_results_dialog.py` | 9 |
| `FindReplaceScope` | `workspace/find_replace_types.py` | 12 |
| `FindReplaceTableModel` | `workspace/find_replace_results_dialog.py` | 2 |
| `FlagLineEdit` | `workspace/find_replace_bar.py` | 4 |
| `FontSettingsTab` | `pref/kbd/font_settings.py` | 3 |
| `FontSettingsWidget` | `pref/settings/font_settings_widget.py` | 2 |
| `FoundRecord` | `pref/tran_history/tran_search_nav_bar.py` | 5 |
| `GeneralSettingsWidget` | `pref/settings/general_settings_widget.py` | 4 |
| `HistorySettingsWidget` | `pref/settings/history_settings_widget.py` | 6 |
| `HistoryTableModel` | `pref/tran_history/history_table_model.py` | 3 |
| `ImportDictTypeDialog` | `pref/tran_history/translation_db_gui.py` | 2 |
| `ImportWorker` | `main_utils/import_worker.py` | 1 |
| `IssueOnlyDialog` | `workspace/issue_only_dialog.py` | 8 |
| `IssueOnlyDialog` | `workspace/issue_only_dialog_paged.py` | 8 |
| `IssueTableModel` | `workspace/issue_only_dialog.py` | 8 |
| `IssueTableModel` | `workspace/issue_only_dialog_paged.py` | 8 |
| `JsonHandler` | `pref/repl/replacement_engine.py` | 2 |
| `KeyboardSettingsTab` | `pref/kbd/keyboard_settings.py` | 3 |
| `KeyboardSettingsWidget` | `pref/settings/keyboard_settings_widget.py` | 2 |
| `M17nHandler` | `pref/repl/replacement_engine.py` | 2 |
| `MainWindow` | `gvar.py` | 34 |
| `MatchInstance` | `workspace/find_replace_types.py` | 32 |
| `MatchPair` | `workspace/find_replace_types.py` | 16 |
| `ModeRecord` | `workspace/mode_record.py` | 10 |
| `ModeState` | `workspace/mode_record.py` | 13 |
| `NavBar` | `pref/tran_history/tran_navbar.py` | 12 |
| `NavRecord` | `subcmp/paged_nav_scrollbar.py` | 21 |
| `NetworkSettingsWidget` | `pref/settings/network_settings_widget.py` | 4 |
| `NewTaskbar` | `subcmp/new_taskbar.py` | 3 |
| `PagedNavScrollbar` | `subcmp/paged_nav_scrollbar.py` | 57 |
| `PagedSearchNavBar` | `pref/tran_history/paged_search_nav_bar.py` | 1 |
| `PageInfo` | `subcmp/find_replace_manager.py` | 10 |
| `PaginationMode` | `subcmp/find_replace_manager.py` | 20 |
| `PagingMode` | `workspace/find_replace_types.py` | 19 |
| `PagingScrollBar` | `subcmp/table_nav_scrollbar.py` | 20 |
| `PlistHandler` | `pref/repl/replacement_engine.py` | 2 |
| `PluralTranslationEditorWidget` | `subcmp/translation_edit_widget.py` | 3 |
| `POEditorWindow` | `main_gui.py` | 12 |
| `POFileTableModel` | `main_utils/po_ed_table_model.py` | 10 |
| `PopupMenuManager` | `main_utils/popup_mnu.py` | 4 |
| `PreferencesDialog` | `pref/preferences.py` | 5 |
| `RecordMarkerBar` | `subcmp/record_marker_bar.py` | 6 |
| `ReplacementActions` | `pref/repl/replacement_actions.py` | 3 |
| `ReplacementBase` | `subcmp/replacement_base.py` | 8 |
| `ReplacementCaseMatch` | `workspace/find_replace_support_functions.py` | 66 |
| `ReplacementCaseMatch` | `workspace/find_replace_types.py` | 66 |
| `ReplacementEngine` | `pref/repl/replacement_engine.py` | 4 |
| `ReplacementLineEdit` | `subcmp/line_rep_imp.py` | 6 |
| `ReplacementRecord` | `pref/repl/replacement_engine.py` | 36 |
| `ReplacementsDialog` | `pref/repl/replacement_gui.py` | 20 |
| `ReplacementsDialog` | `pref/repl/replacement_old.py` | 20 |
| `ReplacementSettingsTab` | `pref/repl/replacement_settings.py` | 3 |
| `ReplacementSettingsWidget` | `pref/settings/replacement_settings_widget.py` | 2 |
| `ReplacementTextEdit` | `subcmp/text_rep_imp.py` | 22 |
| `SearchNavBar` | `pref/tran_history/tran_search_nav_bar.py` | 11 |
| `SearchRequest` | `search/fast_search.py` | 12 |
| `SearchRequest` | `search/fast_search_open_ext_editor.py` | 12 |
| `SearchResult` | `search/fast_search.py` | 57 |
| `SearchResult` | `search/fast_search_open_ext_editor.py` | 57 |
| `SearchResult` | `workspace/mode_record_integration_guide.py` | 57 |
| `SelectableTable` | `main_utils/table_widgets.py` | 4 |
| `SqliteHandler` | `pref/repl/replacement_engine.py` | 3 |
| `SuggestionController` | `sugg/suggestion_controller.py` | 3 |
| `Suggestor` | `sugg/translate.py` | 2 |
| `SyncedHeightTable` | `main_gui.py` | 2 |
| `TablePagerBase` | `subcmp/table_nav_widget.py` | 4 |
| `TableViewAdapter` | `subcmp/find_replace_manager.py` | 9 |
| `Taskbar` | `subcmp/taskbar.py` | 24 |
| `TranslateTask` | `sugg/translate.py` | 5 |
| `TranslationDB` | `pref/tran_history/translation_db.py` | 20 |
| `TranslationDBRecord` | `pref/tran_history/db_record.py` | 3 |
| `TranslationEditorWidget` | `subcmp/translation_edit_widget.py` | 27 |
| `TranslationHistoryDialog` | `pref/tran_history/translation_db_gui.py` | 12 |
| `TranslationHistorySettingsWidget` | `pref/settings/translation_history_settings_widget.py` | 2 |
| `TranslationRecord` | `pref/tran_history/tran_record.py` | 7 |
| `TranslationSettingsWidget` | `pref/settings/translation_settings_widget.py` | 5 |
| `TransparentMarkerScrollbar` | `subcmp/transparent_marker_scrollbar.py` | 42 |
| `TransVersionEditor` | `pref/tran_history/versions/tran_version_editor.py` | 4 |
| `VersionedTranslationWidget` | `subcmp/versioned_translation_widget.py` | 29 |
| `VersionTableModel` | `pref/tran_history/versions/tran_edit_version_tbl_model.py` | 5 |
| `YamlHandler` | `pref/repl/replacement_engine.py` | 3 |
