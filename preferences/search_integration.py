"""
Search integration components for preferences system.

This module provides search functionality that integrates with the existing
find/replace infrastructure, including search bars, result highlighting,
and navigation controls.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QCheckBox, QComboBox, QToolButton, QFrame, QButtonGroup,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QObject
from PySide6.QtGui import QIcon, QAction, QFont

from typing import Optional, List, Dict, Any, Callable
import re

from lg import logger
from .workspace_types import FindReplaceScope, ReplacementCaseMatch
from .data_models import PreferenceSearchRequest, PreferenceSearchResult, MatchInstance


class PreferenceFlagLineEdit(QLineEdit):
    """Search field for preferences with flag buttons for search options."""
    
    # Signals
    search_requested = Signal(object)  # PreferenceSearchRequest
    flags_changed = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None, placeholder: str = "Search..."):
        super().__init__(parent)
        self.setObjectName("PreferenceFlagLineEdit")
        self.setPlaceholderText(placeholder)
        
        # Search configuration
        self.search_flags = {
            'case_sensitive': False,
            'use_regex': False,
            'whole_word': False,
            'search_scope': FindReplaceScope.ALL
        }
        
        self._table_type = "replacement"
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._emit_search_request)
        
        self._setup_flag_buttons()
        self._connect_signals()
        logger.debug("PreferenceFlagLineEdit created")
    
    def _setup_flag_buttons(self):
        """Setup flag buttons for search options."""
        # Create flag buttons as actions
        self._case_action = QAction("Aa", self)
        self._case_action.setToolTip("Case sensitive search")
        self._case_action.setCheckable(True)
        self._case_action.toggled.connect(self._on_case_toggled)
        
        self._regex_action = QAction(".*", self)
        self._regex_action.setToolTip("Regular expression search")
        self._regex_action.setCheckable(True)
        self._regex_action.toggled.connect(self._on_regex_toggled)
        
        self._word_action = QAction("ab", self)
        self._word_action.setToolTip("Whole word search")
        self._word_action.setCheckable(True)
        self._word_action.toggled.connect(self._on_word_toggled)
        
        # Add actions to line edit (they will appear as buttons)
        self.addAction(self._case_action, QLineEdit.ActionPosition.TrailingPosition)
        self.addAction(self._regex_action, QLineEdit.ActionPosition.TrailingPosition)
        self.addAction(self._word_action, QLineEdit.ActionPosition.TrailingPosition)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._emit_search_request)
    
    def _on_text_changed(self, text: str):
        """Handle text changes with debouncing."""
        self._search_timer.stop()
        if text.strip():  # Only search if there's actual text
            self._search_timer.start(300)  # 300ms debounce
    
    def _on_case_toggled(self, checked: bool):
        """Handle case sensitivity toggle."""
        self.search_flags['case_sensitive'] = checked
        self.flags_changed.emit()
        if self.text().strip():
            self._emit_search_request()
    
    def _on_regex_toggled(self, checked: bool):
        """Handle regex toggle."""
        self.search_flags['use_regex'] = checked
        self.flags_changed.emit()
        if self.text().strip():
            self._emit_search_request()
    
    def _on_word_toggled(self, checked: bool):
        """Handle whole word toggle."""
        self.search_flags['whole_word'] = checked
        self.flags_changed.emit()
        if self.text().strip():
            self._emit_search_request()
    
    def _emit_search_request(self):
        """Emit search request with current configuration."""
        query = self.text().strip()
        if not query:
            return
        
        request = self.create_search_request(query)
        self.search_requested.emit(request)
        logger.debug(f"Search request emitted: {query}")
    
    def create_search_request(self, query: str) -> PreferenceSearchRequest:
        """Create search request from current configuration."""
        case_match = ReplacementCaseMatch.MATCH if self.search_flags['case_sensitive'] else ReplacementCaseMatch.IGNORE
        
        request = PreferenceSearchRequest(
            query=query,
            scope=self.search_flags['search_scope'],
            case_match=case_match,
            use_regex=self.search_flags['use_regex'],
            table_type=self._table_type
        )
        
        return request
    
    def set_table_type(self, table_type: str):
        """Set table type for search context."""
        self._table_type = table_type
    
    def get_search_flags(self) -> Dict[str, Any]:
        """Get current search flags."""
        return self.search_flags.copy()
    
    def set_search_flags(self, flags: Dict[str, Any]):
        """Set search flags."""
        self.search_flags.update(flags)
        
        # Update UI to reflect flags
        self._case_action.setChecked(self.search_flags.get('case_sensitive', False))
        self._regex_action.setChecked(self.search_flags.get('use_regex', False))
        self._word_action.setChecked(self.search_flags.get('whole_word', False))
        
        self.flags_changed.emit()


class PreferenceSearchBar(QWidget):
    """Enhanced search bar for preferences with find/replace functionality."""
    
    # Signals
    search_requested = Signal(object)  # PreferenceSearchRequest
    search_cleared = Signal()
    next_match = Signal()
    prev_match = Signal()
    replace_requested = Signal(str)  # replacement text
    replace_all_requested = Signal(str)
    export_results = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None, table_type: str = "replacement"):
        super().__init__(parent)
        self.setObjectName("PreferenceSearchBar")
        self.table_type = table_type
        self.current_results: List[PreferenceSearchResult] = []
        self.current_match_index = 0
        self.total_matches = 0
        
        self._setup_ui()
        self._connect_signals()
        logger.debug(f"PreferenceSearchBar created for {table_type}")
    
    def _setup_ui(self):
        """Setup search bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search field
        self.search_field = PreferenceFlagLineEdit(placeholder="Search...")
        self.search_field.set_table_type(self.table_type)
        layout.addWidget(self.search_field)
        
        # Search navigation
        self.prev_btn = QPushButton("↑")
        self.prev_btn.setMaximumWidth(30)
        self.prev_btn.setToolTip("Previous match")
        self.prev_btn.setEnabled(False)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("↓")
        self.next_btn.setMaximumWidth(30)
        self.next_btn.setToolTip("Next match")
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)
        
        # Match counter
        self.match_label = QLabel("0 matches")
        layout.addWidget(self.match_label)
        
        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setMaximumWidth(30)
        self.clear_btn.setToolTip("Clear search")
        layout.addWidget(self.clear_btn)
        
        # Add preference-specific controls
        self._setup_preference_specific_controls(layout)
    
    def _setup_preference_specific_controls(self, layout: QHBoxLayout):
        """Add preference-specific search controls."""
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        layout.addWidget(separator)
        
        if self.table_type == "history":
            # Date range filter for history
            self.date_filter_cb = QCheckBox("Date filter")
            layout.addWidget(self.date_filter_cb)
        
        elif self.table_type == "replacement":
            # Context filter for replacements
            self.context_filter = QComboBox()
            self.context_filter.addItems(["All contexts", "UI", "Messages", "Errors"])
            self.context_filter.setToolTip("Filter by context")
            layout.addWidget(self.context_filter)
        
        # Export results button
        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip("Export search results")
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.search_field.search_requested.connect(self._on_search_requested)
        self.prev_btn.clicked.connect(self.prev_match.emit)
        self.next_btn.clicked.connect(self.next_match.emit)
        self.clear_btn.clicked.connect(self._clear_search)
        self.export_btn.clicked.connect(self.export_results.emit)
    
    def _on_search_requested(self, request: PreferenceSearchRequest):
        """Handle search request from search field."""
        self.search_requested.emit(request)
    
    def _clear_search(self):
        """Clear search and reset state."""
        self.search_field.clear()
        self.current_results.clear()
        self.current_match_index = 0
        self.total_matches = 0
        self._update_navigation_state()
        self.search_cleared.emit()
        logger.debug("Search cleared")
    
    def set_search_results(self, results: List[PreferenceSearchResult]):
        """Set search results and update navigation."""
        self.current_results = results
        self.total_matches = len(results)
        self.current_match_index = 0 if results else -1
        self._update_navigation_state()
        logger.debug(f"Search results set: {len(results)} matches")
    
    def _update_navigation_state(self):
        """Update navigation buttons and match counter."""
        has_matches = self.total_matches > 0
        
        # Update buttons
        self.prev_btn.setEnabled(has_matches and self.current_match_index > 0)
        self.next_btn.setEnabled(has_matches and self.current_match_index < self.total_matches - 1)
        self.export_btn.setEnabled(has_matches)
        
        # Update counter
        if has_matches:
            self.match_label.setText(f"Match {self.current_match_index + 1} of {self.total_matches}")
        else:
            self.match_label.setText("0 matches")
    
    def navigate_to_match(self, index: int):
        """Navigate to specific match index."""
        if 0 <= index < self.total_matches:
            self.current_match_index = index
            self._update_navigation_state()
    
    def get_current_search_text(self) -> str:
        """Get current search text."""
        return self.search_field.text()
    
    def set_search_text(self, text: str):
        """Set search text."""
        self.search_field.setText(text)


class SearchResultHighlighter:
    """Helper class for highlighting search matches in text."""
    
    @staticmethod
    def highlight_matches(text: str, matches: List[MatchInstance], 
                         highlight_format: str = "<mark>%s</mark>") -> str:
        """Highlight matches in text using HTML formatting."""
        if not matches:
            return text
        
        # Sort matches by start position (reverse order for safe replacement)
        sorted_matches = sorted(matches, key=lambda m: m.start, reverse=True)
        
        result = text
        for match in sorted_matches:
            if 0 <= match.start <= match.end <= len(result):
                match_text = result[match.start:match.end]
                highlighted = highlight_format % match_text
                result = result[:match.start] + highlighted + result[match.end:]
        
        return result
    
    @staticmethod
    def find_text_matches(text: str, pattern: str, use_regex: bool = False,
                         case_sensitive: bool = False) -> List[MatchInstance]:
        """Find all matches of pattern in text."""
        matches = []
        
        if not text or not pattern:
            return matches
        
        try:
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                regex = re.compile(pattern, flags)
                for match in regex.finditer(text):
                    matches.append(MatchInstance(
                        start=match.start(),
                        end=match.end(),
                        text=match.group(),
                        field="text"
                    ))
            else:
                # Simple text search
                search_text = text if case_sensitive else text.lower()
                search_pattern = pattern if case_sensitive else pattern.lower()
                
                start = 0
                while True:
                    pos = search_text.find(search_pattern, start)
                    if pos == -1:
                        break
                    
                    matches.append(MatchInstance(
                        start=pos,
                        end=pos + len(pattern),
                        text=text[pos:pos + len(pattern)],
                        field="text"
                    ))
                    start = pos + 1
        
        except re.error as e:
            logger.warning(f"Regex error in search: {e}")
        
        return matches


class SearchNavigationWidget(QWidget):
    """Navigation widget for search results."""
    
    # Signals
    match_selected = Signal(int)  # match index
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("SearchNavigationWidget")
        self.search_results: List[PreferenceSearchResult] = []
        self.current_index = -1
        self._setup_ui()
        logger.debug("SearchNavigationWidget created")
    
    def _setup_ui(self):
        """Setup navigation UI."""
        layout = QVBoxLayout(self)
        
        # Navigation header
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Search Results")
        self.title_label.setFont(QFont("", 10, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        self.count_label = QLabel("0 results")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Results list would go here
        # For now, just a placeholder
        self.results_label = QLabel("No search results")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.results_label)
    
    def set_search_results(self, results: List[PreferenceSearchResult]):
        """Set search results for navigation."""
        self.search_results = results
        self.current_index = 0 if results else -1
        self._update_display()
    
    def _update_display(self):
        """Update navigation display."""
        count = len(self.search_results)
        self.count_label.setText(f"{count} results")
        
        if count == 0:
            self.results_label.setText("No search results")
        else:
            self.results_label.setText(f"Showing {count} search results")
    
    def navigate_to_result(self, index: int):
        """Navigate to specific result."""
        if 0 <= index < len(self.search_results):
            self.current_index = index
            self.match_selected.emit(index)


class PreferenceSearchService:
    """Service for unified search functionality across preferences."""
    
    def __init__(self):
        self.search_providers: Dict[str, Callable] = {}
        logger.debug("PreferenceSearchService initialized")
    
    def register_search_provider(self, table_type: str, provider: Callable):
        """Register search provider for specific table type."""
        self.search_providers[table_type] = provider
        logger.debug(f"Search provider registered for: {table_type}")
    
    def search(self, request: PreferenceSearchRequest) -> List[PreferenceSearchResult]:
        """Perform search using appropriate provider."""
        provider = self.search_providers.get(request.table_type)
        if not provider:
            logger.warning(f"No search provider for table type: {request.table_type}")
            return []
        
        try:
            results = provider(request)
            logger.debug(f"Search completed: {len(results)} results for '{request.query}'")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def highlight_results(self, results: List[PreferenceSearchResult], 
                         query: str, use_regex: bool = False) -> List[PreferenceSearchResult]:
        """Add highlighting information to search results."""
        for result in results:
            # Add highlighting to display text
            try:
                # Replacement record - try find_text first
                matches = SearchResultHighlighter.find_text_matches(
                    result.record.find_text, query, use_regex
                )
                result.display_text = SearchResultHighlighter.highlight_matches(
                    result.record.find_text, matches
                )
            except AttributeError:
                try:
                    # History record - try msgid
                    matches = SearchResultHighlighter.find_text_matches(
                        result.record.msgid, query, use_regex
                    )
                    result.display_text = SearchResultHighlighter.highlight_matches(
                        result.record.msgid, matches
                    )
                except AttributeError:
                    # Fallback - no highlighting
                    result.display_text = str(result.record)
        
        return results
