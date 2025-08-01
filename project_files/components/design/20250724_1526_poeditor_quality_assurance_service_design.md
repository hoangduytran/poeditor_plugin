# POEditor Quality Assurance Service Design

**Date**: July 24, 2025  
**Component**: Quality Assurance Service  
**Status**: Design  
**Dependencies**: Core Services Framework

## 1. Overview

The Quality Assurance Service provides comprehensive validation and issue detection for the POEditor plugin. It analyzes translations for common problems, consistency issues, and formatting errors, helping translators maintain high-quality output. The service offers both real-time validation during editing and batch validation for entire files, with configurable rules and severity levels.

This design document outlines the architecture, core functionality, integration points, and implementation details for the Quality Assurance Service.

## 2. Core Architecture

### 2.1 Component Structure

```
Quality Assurance Service
├── Rule Engine
│   ├── Rule Registry
│   ├── Rule Execution
│   └── Rule Management
├── Issue Detection
│   ├── Standard Rules
│   ├── Custom Rules
│   └── Issue Classification
├── Service Interface
│   ├── Entry Validation
│   ├── File Validation
│   └── Settings Integration
└── Reporting System
    ├── Issue Aggregation
    ├── Statistics Generation
    └── Report Formatting
```

### 2.2 Data Models

#### 2.2.1 Issue Model

```python
@dataclass
class TranslationIssue:
    """Represents a detected issue in a translation."""
    
    id: str  # Unique issue identifier
    entry_id: str  # ID of the PO entry with the issue
    rule_id: str  # ID of the rule that detected the issue
    severity: IssueSeverity  # Severity level
    message: str  # Human-readable issue description
    suggestion: Optional[str] = None  # Suggested fix
    details: Optional[dict] = None  # Additional details
    
    @property
    def is_critical(self) -> bool:
        """Return whether this is a critical issue."""
        return self.severity == IssueSeverity.CRITICAL
        
    @property
    def is_warning(self) -> bool:
        """Return whether this is a warning."""
        return self.severity == IssueSeverity.WARNING
        
    @property
    def is_info(self) -> bool:
        """Return whether this is an info message."""
        return self.severity == IssueSeverity.INFO
```

#### 2.2.2 Rule Model

```python
class IssueSeverity(Enum):
    """Severity levels for translation issues."""
    
    CRITICAL = "critical"  # Serious problems that must be fixed
    WARNING = "warning"    # Potential problems that should be reviewed
    INFO = "info"          # Informational messages
    
    
class ValidationRule(ABC):
    """Base class for all validation rules."""
    
    def __init__(self, rule_id: str, name: str, description: str, severity: IssueSeverity):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.enabled = True
        self.options = {}
        
    @abstractmethod
    def validate(self, entry: POEntry) -> List[TranslationIssue]:
        """Validate a PO entry and return any issues found."""
        pass
        
    def get_option(self, name: str, default: Any = None) -> Any:
        """Get option value with fallback to default."""
        return self.options.get(name, default)
        
    def set_option(self, name: str, value: Any) -> None:
        """Set option value."""
        self.options[name] = value
        
    def describe_issue(self, entry_id: str, message: str, suggestion: Optional[str] = None) -> TranslationIssue:
        """Create a standardized issue description."""
        return TranslationIssue(
            id=f"{self.rule_id}_{entry_id}_{uuid.uuid4().hex[:8]}",
            entry_id=entry_id,
            rule_id=self.rule_id,
            severity=self.severity,
            message=message,
            suggestion=suggestion
        )
```

## 3. Core Service Interface

```python
class QualityAssuranceService(Service):
    """Service for validating translations and detecting quality issues."""
    
    def __init__(self, api: PluginAPI):
        super().__init__(api)
        self._rules = {}
        self._register_standard_rules()
        self._load_rule_settings()
        
        # Subscribe to events
        api.subscribe_event("settings.changed.qa", self._on_settings_changed)
        
    def validate_entry(self, entry: POEntry) -> List[TranslationIssue]:
        """Validate a single PO entry and return any issues."""
        issues = []
        
        # Apply each enabled rule
        for rule in self._rules.values():
            if rule.enabled:
                try:
                    rule_issues = rule.validate(entry)
                    issues.extend(rule_issues)
                except Exception as e:
                    from lg import logger
                    logger.error(f"Error applying rule {rule.rule_id}: {e}", exc_info=True)
                    
        return issues
        
    def validate_file(self, entries: List[POEntry]) -> Dict[str, List[TranslationIssue]]:
        """Validate a list of PO entries and return issues grouped by entry ID."""
        result = {}
        
        for entry in entries:
            entry_issues = self.validate_entry(entry)
            if entry_issues:
                result[entry.msgid] = entry_issues
                
        return result
        
    def get_rules(self) -> Dict[str, ValidationRule]:
        """Get all registered validation rules."""
        return self._rules.copy()
        
    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """Get a specific validation rule."""
        return self._rules.get(rule_id)
        
    def enable_rule(self, rule_id: str, enabled: bool = True) -> bool:
        """Enable or disable a validation rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = enabled
            self._save_rule_settings()
            return True
        return False
        
    def set_rule_severity(self, rule_id: str, severity: IssueSeverity) -> bool:
        """Set the severity level for a validation rule."""
        if rule_id in self._rules:
            self._rules[rule_id].severity = severity
            self._save_rule_settings()
            return True
        return False
        
    def set_rule_option(self, rule_id: str, option: str, value: Any) -> bool:
        """Set an option for a validation rule."""
        if rule_id in self._rules:
            self._rules[rule_id].set_option(option, value)
            self._save_rule_settings()
            return True
        return False
        
    def register_custom_rule(self, rule: ValidationRule) -> bool:
        """Register a custom validation rule."""
        if rule.rule_id in self._rules:
            from lg import logger
            logger.error(f"Rule ID already exists: {rule.rule_id}")
            return False
            
        self._rules[rule.rule_id] = rule
        self._save_rule_settings()
        
        # Notify rule added
        self.api.emit_event("qa.rule_added", {"rule_id": rule.rule_id})
        
        return True
        
    def generate_report(self, issues: Dict[str, List[TranslationIssue]]) -> dict:
        """Generate a summary report from validation results."""
        # Count issues by severity
        severity_counts = {
            IssueSeverity.CRITICAL.value: 0,
            IssueSeverity.WARNING.value: 0,
            IssueSeverity.INFO.value: 0
        }
        
        # Count issues by rule
        rule_counts = {}
        
        # Track affected entries
        affected_entries = set()
        
        # Process all issues
        for entry_id, entry_issues in issues.items():
            affected_entries.add(entry_id)
            
            for issue in entry_issues:
                # Count by severity
                severity_counts[issue.severity.value] += 1
                
                # Count by rule
                rule_id = issue.rule_id
                if rule_id not in rule_counts:
                    rule_counts[rule_id] = 0
                rule_counts[rule_id] += 1
                
        # Generate report
        return {
            "total_issues": sum(severity_counts.values()),
            "affected_entries": len(affected_entries),
            "severity_counts": severity_counts,
            "rule_counts": rule_counts,
            "most_common_rule": max(rule_counts.items(), key=lambda x: x[1])[0] if rule_counts else None,
            "has_critical": severity_counts[IssueSeverity.CRITICAL.value] > 0
        }
```

## 4. Standard Validation Rules

### 4.1 Empty Translation Rule

```python
class EmptyTranslationRule(ValidationRule):
    """Rule that checks for empty translations."""
    
    def __init__(self):
        super().__init__(
            rule_id="empty_translation",
            name="Empty Translation",
            description="Checks for translations that are empty",
            severity=IssueSeverity.CRITICAL
        )
        
    def validate(self, entry: POEntry) -> List[TranslationIssue]:
        issues = []
        
        # Skip if no msgid
        if not entry.msgid:
            return issues
            
        # Check if translation is empty
        if not entry.msgstr or entry.msgstr.strip() == "":
            issues.append(self.describe_issue(
                entry_id=entry.msgid,
                message="Translation is empty",
                suggestion="Add a translation for this entry"
            ))
            
        return issues
```

### 4.2 Identical Translation Rule

```python
class IdenticalTranslationRule(ValidationRule):
    """Rule that checks if translation is identical to source."""
    
    def __init__(self):
        super().__init__(
            rule_id="identical_translation",
            name="Identical Translation",
            description="Checks if translation is identical to source text",
            severity=IssueSeverity.WARNING
        )
        self.set_option("ignore_specific_terms", True)
        self.set_option("ignored_terms", ["OK", "Cancel", "Error"])
        
    def validate(self, entry: POEntry) -> List[TranslationIssue]:
        issues = []
        
        # Skip if no msgid or msgstr
        if not entry.msgid or not entry.msgstr:
            return issues
            
        # Check if translation is identical
        if entry.msgid == entry.msgstr:
            # Check if this is an ignored term
            if self.get_option("ignore_specific_terms", True):
                ignored_terms = self.get_option("ignored_terms", [])
                if entry.msgid in ignored_terms:
                    return issues
                    
            issues.append(self.describe_issue(
                entry_id=entry.msgid,
                message="Translation is identical to source text",
                suggestion="Provide a proper translation or mark as fuzzy if unsure"
            ))
            
        return issues
```

### 4.3 Placeholder Mismatch Rule

```python
class PlaceholderMismatchRule(ValidationRule):
    """Rule that checks for mismatched placeholders in source and translation."""
    
    def __init__(self):
        super().__init__(
            rule_id="placeholder_mismatch",
            name="Placeholder Mismatch",
            description="Checks if translation has the same placeholders as source",
            severity=IssueSeverity.CRITICAL
        )
        
    def validate(self, entry: POEntry) -> List[TranslationIssue]:
        issues = []
        
        # Skip if no msgid or msgstr
        if not entry.msgid or not entry.msgstr:
            return issues
            
        # Find placeholders in source
        source_placeholders = self._extract_placeholders(entry.msgid)
        
        # Find placeholders in translation
        translation_placeholders = self._extract_placeholders(entry.msgstr)
        
        # Check for missing placeholders
        missing_placeholders = source_placeholders - translation_placeholders
        if missing_placeholders:
            issues.append(self.describe_issue(
                entry_id=entry.msgid,
                message=f"Missing placeholders in translation: {', '.join(missing_placeholders)}",
                suggestion="Add the missing placeholders to the translation"
            ))
            
        # Check for extra placeholders
        extra_placeholders = translation_placeholders - source_placeholders
        if extra_placeholders:
            issues.append(self.describe_issue(
                entry_id=entry.msgid,
                message=f"Extra placeholders in translation: {', '.join(extra_placeholders)}",
                suggestion="Remove the extra placeholders from the translation"
            ))
            
        return issues
        
    def _extract_placeholders(self, text: str) -> Set[str]:
        """Extract placeholders from text."""
        # Extract printf-style placeholders (%s, %d, etc.)
        printf_placeholders = set(re.findall(r'%(?:\d+\$)?[diouxXeEfFgGaAcspn]', text))
        
        # Extract named placeholders ({name}, {0}, etc.)
        named_placeholders = set(re.findall(r'\{([^{}]+)\}', text))
        named_placeholders = {f"{{{p}}}" for p in named_placeholders}
        
        # Extract HTML/XML tags
        html_tags = set(re.findall(r'<[^>]+>', text))
        
        # Combine all placeholders
        return printf_placeholders | named_placeholders | html_tags
```

### 4.4 Leading/Trailing Whitespace Rule

```python
class WhitespaceRule(ValidationRule):
    """Rule that checks for incorrect leading/trailing whitespace."""
    
    def __init__(self):
        super().__init__(
            rule_id="whitespace",
            name="Whitespace Issues",
            description="Checks for improper leading or trailing whitespace",
            severity=IssueSeverity.WARNING
        )
        
    def validate(self, entry: POEntry) -> List[TranslationIssue]:
        issues = []
        
        # Skip if no msgid or msgstr
        if not entry.msgid or not entry.msgstr:
            return issues
            
        # Check leading whitespace consistency
        source_leading = len(entry.msgid) - len(entry.msgid.lstrip())
        translation_leading = len(entry.msgstr) - len(entry.msgstr.lstrip())
        
        if source_leading != translation_leading:
            issues.append(self.describe_issue(
                entry_id=entry.msgid,
                message="Leading whitespace doesn't match source",
                suggestion=f"Make sure leading whitespace matches source ({source_leading} vs {translation_leading} spaces)"
            ))
            
        # Check trailing whitespace consistency
        source_trailing = len(entry.msgid) - len(entry.msgid.rstrip())
        translation_trailing = len(entry.msgstr) - len(entry.msgstr.rstrip())
        
        if source_trailing != translation_trailing:
            issues.append(self.describe_issue(
                entry_id=entry.msgid,
                message="Trailing whitespace doesn't match source",
                suggestion=f"Make sure trailing whitespace matches source ({source_trailing} vs {translation_trailing} spaces)"
            ))
            
        return issues
```

### 4.5 Ending Punctuation Rule

```python
class EndingPunctuationRule(ValidationRule):
    """Rule that checks for consistent ending punctuation."""
    
    def __init__(self):
        super().__init__(
            rule_id="ending_punctuation",
            name="Ending Punctuation",
            description="Checks if translation has consistent ending punctuation",
            severity=IssueSeverity.WARNING
        )
        
    def validate(self, entry: POEntry) -> List[TranslationIssue]:
        issues = []
        
        # Skip if no msgid or msgstr
        if not entry.msgid or not entry.msgstr:
            return issues
            
        # Get last non-whitespace character of source and translation
        source_last_char = entry.msgid.rstrip()[-1] if entry.msgid.rstrip() else ""
        translation_last_char = entry.msgstr.rstrip()[-1] if entry.msgstr.rstrip() else ""
        
        # Check if both end with punctuation or neither does
        source_has_punctuation = source_last_char in ".,:;!?…"
        translation_has_punctuation = translation_last_char in ".,:;!?…"
        
        if source_has_punctuation != translation_has_punctuation:
            if source_has_punctuation:
                issues.append(self.describe_issue(
                    entry_id=entry.msgid,
                    message=f"Source ends with '{source_last_char}' but translation doesn't end with punctuation",
                    suggestion=f"Consider adding appropriate ending punctuation to match source"
                ))
            else:
                issues.append(self.describe_issue(
                    entry_id=entry.msgid,
                    message=f"Translation ends with '{translation_last_char}' but source doesn't end with punctuation",
                    suggestion="Consider removing the ending punctuation to match source"
                ))
                
        return issues
```

## 5. Implementation Details

### 5.1 Rule Registration

```python
def _register_standard_rules(self):
    """Register the standard validation rules."""
    # Empty translation rule
    self._rules["empty_translation"] = EmptyTranslationRule()
    
    # Identical translation rule
    self._rules["identical_translation"] = IdenticalTranslationRule()
    
    # Placeholder mismatch rule
    self._rules["placeholder_mismatch"] = PlaceholderMismatchRule()
    
    # Whitespace rule
    self._rules["whitespace"] = WhitespaceRule()
    
    # Ending punctuation rule
    self._rules["ending_punctuation"] = EndingPunctuationRule()
    
    # Length rule
    self._rules["length"] = TranslationLengthRule()
    
    # Missing context rule
    self._rules["missing_context"] = MissingContextRule()
    
    # Capitalization rule
    self._rules["capitalization"] = CapitalizationRule()
    
    # Double space rule
    self._rules["double_space"] = DoubleSpaceRule()
    
    # HTML tag rule
    self._rules["html_tags"] = HtmlTagRule()
```

### 5.2 Settings Management

```python
def _load_rule_settings(self):
    """Load rule settings from QSettings."""
    settings = QSettings("POEditor", "Settings")
    
    # Load rule states
    rule_states = settings.value("qa/rule_states", {}, dict)
    for rule_id, rule_state in rule_states.items():
        if rule_id in self._rules:
            # Set enabled state
            if "enabled" in rule_state:
                self._rules[rule_id].enabled = rule_state["enabled"]
                
            # Set severity
            if "severity" in rule_state:
                try:
                    self._rules[rule_id].severity = IssueSeverity(rule_state["severity"])
                except ValueError:
                    pass
                    
            # Set options
            if "options" in rule_state and isinstance(rule_state["options"], dict):
                for option, value in rule_state["options"].items():
                    self._rules[rule_id].set_option(option, value)
                    
def _save_rule_settings(self):
    """Save rule settings to QSettings."""
    settings = QSettings("POEditor", "Settings")
    
    # Collect rule states
    rule_states = {}
    for rule_id, rule in self._rules.items():
        rule_states[rule_id] = {
            "enabled": rule.enabled,
            "severity": rule.severity.value,
            "options": rule.options.copy()
        }
        
    # Save to settings
    settings.setValue("qa/rule_states", rule_states)
    
    # Notify settings changed
    self.api.emit_event("qa.settings_changed", {})
    
def _on_settings_changed(self, event_data: dict):
    """Handle settings changed event."""
    if event_data.get("key") == "qa/rule_states":
        self._load_rule_settings()
```

### 5.3 Rule Loading System

```python
def load_custom_rules(self, directory: str) -> int:
    """Load custom validation rules from Python files in a directory."""
    if not os.path.isdir(directory):
        from lg import logger
        logger.error(f"Custom rules directory not found: {directory}")
        return 0
        
    count = 0
    for file_name in os.listdir(directory):
        if not file_name.endswith(".py"):
            continue
            
        try:
            # Construct module name
            module_name = os.path.splitext(file_name)[0]
            
            # Load module
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(directory, file_name)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find rule classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, ValidationRule) and 
                    obj is not ValidationRule):
                    
                    # Create instance
                    rule = obj()
                    
                    # Register rule
                    if self.register_custom_rule(rule):
                        count += 1
                        
        except Exception as e:
            from lg import logger
            logger.error(f"Error loading custom rule from {file_name}: {e}", exc_info=True)
            
    return count
```

## 6. Integration with POEditor Tab

### 6.1 Real-time Validation

```python
# In POEditorTab._handle_translation_changed method
def _handle_translation_changed(self, text: str):
    # Update model with new translation
    index = self.table_view.currentIndex()
    if index.isValid():
        # Apply the change to the model
        self.model.update_translation(index.row(), text)
        
        # Validate entry if QA service is available
        if self.qa_service:
            entry = self.model.get_entry(index)
            issues = self.qa_service.validate_entry(entry)
            
            # Update model with issues
            self.model.set_issues(index.row(), issues)
            
            # Update visual indicators
            self.table_view.update(index)
            
            # Show issues in status bar if present
            if issues:
                issue_count = len(issues)
                critical_count = sum(1 for i in issues if i.is_critical)
                
                if critical_count > 0:
                    self.set_status(f"⚠️ {critical_count} critical issues in current entry")
                else:
                    self.set_status(f"⚠️ {issue_count} issues in current entry")
            else:
                self.clear_status()
```

### 6.2 Issue Highlighting in Table

```python
# In POFileTableModel.data method
def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
    if not index.isValid():
        return None
        
    row = index.row()
    col = index.column()
    
    if row < 0 or row >= len(self._entries):
        return None
        
    entry = self._entries[row]
    
    # Handle display role
    if role == Qt.DisplayRole:
        # Return appropriate column data
        if col == self.COL_MSGID:
            return entry.msgid
        elif col == self.COL_MSGSTR:
            return entry.msgstr
        # ... other columns
        
    # Handle background color role for issue highlighting
    elif role == Qt.BackgroundRole:
        # Highlight translation column if entry has issues
        if col == self.COL_MSGSTR and entry in self._issues:
            issues = self._issues[entry]
            
            # Use red for critical issues, pink for warnings
            if any(issue.is_critical for issue in issues):
                return QColor(255, 200, 200)  # Light red
            elif any(issue.is_warning for issue in issues):
                return QColor(255, 230, 230)  # Light pink
                
    # Handle tooltip role for showing issue details
    elif role == Qt.ToolTipRole:
        if col == self.COL_MSGSTR and entry in self._issues:
            issues = self._issues[entry]
            
            # Build tooltip with issue descriptions
            tooltip = "<p><b>Issues:</b></p><ul>"
            for issue in issues:
                severity_icon = "🔴" if issue.is_critical else "⚠️" if issue.is_warning else "ℹ️"
                tooltip += f"<li>{severity_icon} {issue.message}</li>"
            tooltip += "</ul>"
            
            return tooltip
            
    return None
```

### 6.3 Batch Validation

```python
# In POEditorTab class
def validate_all_entries(self):
    """Validate all entries in the file."""
    if not self.qa_service:
        return
        
    # Show progress dialog
    progress = QProgressDialog("Validating translations...", "Cancel", 0, self.model.rowCount(), self)
    progress.setWindowModality(Qt.WindowModal)
    
    # Clear existing issues
    self.model.clear_all_issues()
    
    # Track issues
    total_issues = 0
    entries_with_issues = 0
    
    try:
        # Process entries in batches
        batch_size = 100
        for start_row in range(0, self.model.rowCount(), batch_size):
            # Check for cancellation
            if progress.wasCanceled():
                break
                
            # Get batch of entries
            end_row = min(start_row + batch_size, self.model.rowCount())
            entries = [self.model.get_entry_by_row(row) for row in range(start_row, end_row)]
            
            # Update progress
            progress.setValue(start_row)
            
            # Validate batch
            for i, entry in enumerate(entries):
                row = start_row + i
                issues = self.qa_service.validate_entry(entry)
                
                if issues:
                    # Update model with issues
                    self.model.set_issues(row, issues)
                    total_issues += len(issues)
                    entries_with_issues += 1
                    
            # Process events to keep UI responsive
            QApplication.processEvents()
            
        # Final progress update
        progress.setValue(self.model.rowCount())
        
        # Generate report
        self.show_validation_report(total_issues, entries_with_issues)
        
        # Refresh view
        self.table_view.viewport().update()
        
    finally:
        progress.close()
        
def show_validation_report(self, total_issues: int, entries_with_issues: int):
    """Show a dialog with validation results."""
    if total_issues == 0:
        QMessageBox.information(
            self, 
            "Validation Complete", 
            "No issues found! The translation is perfect."
        )
    else:
        QMessageBox.warning(
            self,
            "Validation Complete",
            f"Found {total_issues} issues in {entries_with_issues} entries.\n\n"
            f"Issues are highlighted in the table. Click 'Navigate to Issues' "
            f"to review them one by one."
        )
```

## 7. Settings Panel Implementation

### 7.1 QA Settings Panel

```python
class QASettingsPanel(QWidget):
    """Settings panel for quality assurance configuration."""
    
    def __init__(self, api: PluginAPI, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api = api
        self.qa_service = api.get_service("quality_assurance")
        
        self._setup_ui()
        self._load_rules()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(4)
        self.rules_table.setHorizontalHeaderLabels([
            "Enabled", "Rule", "Severity", "Description"
        ])
        self.rules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rules_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.rules_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.edit_rule_button = QPushButton("Edit Rule")
        self.edit_options_button = QPushButton("Options...")
        
        button_layout.addWidget(self.edit_rule_button)
        button_layout.addWidget(self.edit_options_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Options group
        options_group = QGroupBox("Global Options")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_validate_check = QCheckBox("Validate automatically while typing")
        self.highlight_issues_check = QCheckBox("Highlight entries with issues")
        self.show_tooltips_check = QCheckBox("Show issue details in tooltips")
        
        options_layout.addWidget(self.auto_validate_check)
        options_layout.addWidget(self.highlight_issues_check)
        options_layout.addWidget(self.show_tooltips_check)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
    def _connect_signals(self):
        """Connect UI signals."""
        self.rules_table.itemChanged.connect(self._on_rule_item_changed)
        self.rules_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.edit_rule_button.clicked.connect(self._on_edit_rule)
        self.edit_options_button.clicked.connect(self._on_edit_options)
        
        self.auto_validate_check.stateChanged.connect(self._on_global_option_changed)
        self.highlight_issues_check.stateChanged.connect(self._on_global_option_changed)
        self.show_tooltips_check.stateChanged.connect(self._on_global_option_changed)
        
        # Subscribe to events
        self.api.subscribe_event("qa.settings_changed", self._on_qa_settings_changed)
        self.api.subscribe_event("qa.rule_added", self._on_qa_rule_changed)
        self.api.subscribe_event("qa.rule_updated", self._on_qa_rule_changed)
        
    def _load_rules(self):
        """Load rules into the table."""
        if not self.qa_service:
            return
            
        # Clear table
        self.rules_table.setRowCount(0)
        
        # Get rules
        rules = self.qa_service.get_rules()
        
        # Add rules to table
        self.rules_table.setRowCount(len(rules))
        for i, (rule_id, rule) in enumerate(rules.items()):
            # Enabled checkbox
            enabled_item = QTableWidgetItem()
            enabled_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            enabled_item.setCheckState(Qt.Checked if rule.enabled else Qt.Unchecked)
            enabled_item.setData(Qt.UserRole, rule_id)
            self.rules_table.setItem(i, 0, enabled_item)
            
            # Rule name
            name_item = QTableWidgetItem(rule.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.rules_table.setItem(i, 1, name_item)
            
            # Severity combo
            severity_combo = QComboBox()
            severity_combo.addItem("Critical", IssueSeverity.CRITICAL.value)
            severity_combo.addItem("Warning", IssueSeverity.WARNING.value)
            severity_combo.addItem("Info", IssueSeverity.INFO.value)
            severity_combo.setCurrentIndex(
                [s.value for s in IssueSeverity].index(rule.severity.value)
            )
            severity_combo.currentIndexChanged.connect(
                lambda idx, r=rule_id: self._on_severity_changed(r, idx)
            )
            self.rules_table.setCellWidget(i, 2, severity_combo)
            
            # Description
            desc_item = QTableWidgetItem(rule.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.rules_table.setItem(i, 3, desc_item)
```

### 7.2 Rule Options Dialog

```python
class RuleOptionsDialog(QDialog):
    """Dialog for editing rule options."""
    
    def __init__(self, rule: ValidationRule, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.rule = rule
        self.option_widgets = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(f"Options for {self.rule.name}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add form layout for options
        form_layout = QFormLayout()
        
        # Create widgets for each option
        for option, value in self.rule.options.items():
            if isinstance(value, bool):
                # Boolean option
                widget = QCheckBox()
                widget.setChecked(value)
                form_layout.addRow(self._format_option_name(option), widget)
                self.option_widgets[option] = widget
            elif isinstance(value, int):
                # Integer option
                widget = QSpinBox()
                widget.setValue(value)
                form_layout.addRow(self._format_option_name(option), widget)
                self.option_widgets[option] = widget
            elif isinstance(value, float):
                # Float option
                widget = QDoubleSpinBox()
                widget.setValue(value)
                form_layout.addRow(self._format_option_name(option), widget)
                self.option_widgets[option] = widget
            elif isinstance(value, str):
                # String option
                widget = QLineEdit(value)
                form_layout.addRow(self._format_option_name(option), widget)
                self.option_widgets[option] = widget
            elif isinstance(value, list):
                # List option
                widget = QLineEdit(", ".join(str(item) for item in value))
                form_layout.addRow(self._format_option_name(option), widget)
                self.option_widgets[option] = widget
                
        layout.addLayout(form_layout)
        
        # Add description
        if self.rule.description:
            desc_label = QLabel(self.rule.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: gray;")
            layout.addWidget(desc_label)
            
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _format_option_name(self, option: str) -> str:
        """Format option name for display."""
        return option.replace("_", " ").title() + ":"
        
    def save_options(self) -> None:
        """Save options back to the rule."""
        for option, widget in self.option_widgets.items():
            original_value = self.rule.options.get(option)
            
            if isinstance(widget, QCheckBox):
                self.rule.set_option(option, widget.isChecked())
            elif isinstance(widget, QSpinBox):
                self.rule.set_option(option, widget.value())
            elif isinstance(widget, QDoubleSpinBox):
                self.rule.set_option(option, widget.value())
            elif isinstance(widget, QLineEdit):
                if isinstance(original_value, list):
                    # Parse comma-separated list
                    items = [item.strip() for item in widget.text().split(",")]
                    
                    # Convert types if needed
                    if all(original_value) and all(isinstance(item, int) for item in original_value):
                        items = [int(item) for item in items if item.isdigit()]
                    elif all(original_value) and all(isinstance(item, float) for item in original_value):
                        items = [float(item) for item in items if self._is_float(item)]
                        
                    self.rule.set_option(option, items)
                else:
                    self.rule.set_option(option, widget.text())
                    
    def _is_float(self, value: str) -> bool:
        """Check if string can be converted to float."""
        try:
            float(value)
            return True
        except ValueError:
            return False
```

## 8. Performance Considerations

### 8.1 Batch Processing

```python
def validate_entries_batch(self, entries: List[POEntry]) -> Dict[str, List[TranslationIssue]]:
    """Validate multiple entries efficiently."""
    result = {}
    
    # Group enabled rules by type for more efficient processing
    regex_rules = []
    placeholder_rules = []
    length_rules = []
    other_rules = []
    
    for rule in self._rules.values():
        if not rule.enabled:
            continue
            
        if isinstance(rule, PlaceholderMismatchRule) or isinstance(rule, HtmlTagRule):
            placeholder_rules.append(rule)
        elif isinstance(rule, TranslationLengthRule):
            length_rules.append(rule)
        elif isinstance(rule, RegexBasedRule):
            regex_rules.append(rule)
        else:
            other_rules.append(rule)
            
    # Process entries in batches with similar rules
    for entry in entries:
        entry_id = entry.msgid
        entry_issues = []
        
        # Apply rule groups
        if regex_rules:
            for rule in regex_rules:
                entry_issues.extend(rule.validate(entry))
                
        if placeholder_rules:
            for rule in placeholder_rules:
                entry_issues.extend(rule.validate(entry))
                
        if length_rules:
            for rule in length_rules:
                entry_issues.extend(rule.validate(entry))
                
        if other_rules:
            for rule in other_rules:
                entry_issues.extend(rule.validate(entry))
                
        # Add to results if issues found
        if entry_issues:
            result[entry_id] = entry_issues
            
    return result
```

### 8.2 Rule Caching

```python
class RegexBasedRule(ValidationRule):
    """Base class for rules that use regex patterns."""
    
    def __init__(self, rule_id: str, name: str, description: str, severity: IssueSeverity):
        super().__init__(rule_id, name, description, severity)
        self._regex_cache = {}
        
    def get_regex(self, pattern: str, flags: int = 0) -> re.Pattern:
        """Get or create a compiled regex pattern."""
        cache_key = (pattern, flags)
        
        if cache_key not in self._regex_cache:
            self._regex_cache[cache_key] = re.compile(pattern, flags)
            
        return self._regex_cache[cache_key]
        
    def clear_cache(self) -> None:
        """Clear the regex cache."""
        self._regex_cache.clear()
```

## 9. Testing Strategy

### 9.1 Unit Tests

```python
class TestQualityAssuranceService(unittest.TestCase):
    """Unit tests for the Quality Assurance Service."""
    
    def setUp(self):
        """Set up the test environment."""
        self.api_mock = MagicMock()
        self.service = QualityAssuranceService(self.api_mock)
        
    def test_empty_translation_rule(self):
        """Test empty translation detection."""
        # Create test entry
        entry = POEntry(msgid="Test", msgstr="")
        
        # Validate entry
        issues = self.service.validate_entry(entry)
        
        # Check issues
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].rule_id, "empty_translation")
        self.assertEqual(issues[0].severity, IssueSeverity.CRITICAL)
        
    def test_identical_translation_rule(self):
        """Test identical translation detection."""
        # Create test entry
        entry = POEntry(msgid="Test", msgstr="Test")
        
        # Validate entry
        issues = self.service.validate_entry(entry)
        
        # Check issues
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].rule_id, "identical_translation")
        self.assertEqual(issues[0].severity, IssueSeverity.WARNING)
        
        # Test with ignored term
        rule = self.service.get_rule("identical_translation")
        rule.set_option("ignored_terms", ["Test"])
        
        # Validate again
        issues = self.service.validate_entry(entry)
        
        # Check no issues
        self.assertEqual(len(issues), 0)
        
    def test_placeholder_mismatch_rule(self):
        """Test placeholder mismatch detection."""
        # Create test entry with missing placeholder
        entry1 = POEntry(msgid="Hello, %s!", msgstr="Hello!")
        
        # Validate entry
        issues1 = self.service.validate_entry(entry1)
        
        # Check issues
        self.assertEqual(len(issues1), 1)
        self.assertEqual(issues1[0].rule_id, "placeholder_mismatch")
        self.assertEqual(issues1[0].severity, IssueSeverity.CRITICAL)
        
        # Create test entry with extra placeholder
        entry2 = POEntry(msgid="Hello!", msgstr="Hello, %s!")
        
        # Validate entry
        issues2 = self.service.validate_entry(entry2)
        
        # Check issues
        self.assertEqual(len(issues2), 1)
        self.assertEqual(issues2[0].rule_id, "placeholder_mismatch")
        
        # Create test entry with matching placeholders
        entry3 = POEntry(msgid="Hello, %s!", msgstr="Hello, %s!")
        
        # Validate entry
        issues3 = self.service.validate_entry(entry3)
        
        # Check no placeholder issues
        self.assertFalse(any(i.rule_id == "placeholder_mismatch" for i in issues3))
```

### 9.2 Integration Tests

```python
class TestQAIntegration(unittest.TestCase):
    """Integration tests for the Quality Assurance Service."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a real application environment
        self.app = QApplication([])
        
        # Create plugin API
        self.api = PluginAPI()
        
        # Create and register service
        self.service = QualityAssuranceService(self.api)
        self.api.register_service("quality_assurance", self.service)
        
    def tearDown(self):
        """Clean up test environment."""
        self.app.quit()
        
    def test_po_editor_integration(self):
        """Test integration with POEditor tab."""
        # Create a POEditor tab with API
        tab = POEditorTab("test.po", self.api)
        
        # Create a mock model
        model = MagicMock()
        tab.model = model
        
        # Create a test entry with issues
        entry = POEntry(msgid="Test with %s", msgstr="Test without placeholder")
        model.get_entry.return_value = entry
        
        # Simulate translation changed
        tab._handle_translation_changed("Test without placeholder")
        
        # Check that the model was updated with issues
        model.set_issues.assert_called_once()
        issues = model.set_issues.call_args[0][1]
        
        # Verify issues
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any(i.rule_id == "placeholder_mismatch" for i in issues))
```

## 10. Future Enhancements

### 10.1 Enhanced Rule System

Future versions could implement more sophisticated rule capabilities:

- **Rule Dependencies**: Rules that depend on other rules' results
- **Rule Chaining**: Multi-stage validation with intermediate results
- **Rule Aggregation**: Combine related issues into higher-level problems
- **Rule Templates**: Easy creation of common rule patterns

### 10.2 Machine Learning Integration

The QA service could leverage machine learning for advanced validation:

- **Translation Quality Prediction**: Estimate overall translation quality
- **Stylistic Consistency**: Check for consistent writing style
- **Cultural Appropriateness**: Flag potentially inappropriate translations
- **Natural Language Analysis**: Check grammar and fluency

### 10.3 Visual Issue Explorer

Enhance the UI with a dedicated issue explorer:

- **Issue Browser**: Dedicated panel to browse all issues
- **Issue Categories**: Group issues by type or severity
- **Issue Navigation**: Quickly jump between related issues
- **Batch Fixing**: Tools to fix multiple similar issues at once

### 10.4 Custom Rule Editor

Add a visual editor for creating custom validation rules:

- **Rule Builder**: Visual interface for creating rules
- **Rule Testing**: Live testing of rules against examples
- **Rule Sharing**: Import/export custom rule collections
- **Rule Marketplace**: Community-shared rules

## 11. Conclusion

The Quality Assurance Service provides a comprehensive solution for ensuring translation quality within the POEditor plugin. By implementing a flexible rule-based validation system with configurable severity levels and detailed issue reporting, the service helps translators identify and fix problems before they impact the final translations.

The core architecture supports both standard and custom validation rules, allowing for both general quality checks and project-specific requirements. The integration with the POEditor tab component provides real-time feedback during editing while also supporting batch validation for comprehensive quality assessments.

The implementation balances performance considerations with thorough validation capabilities, ensuring that even large translation files can be processed efficiently. The user-friendly settings panel makes it easy for users to configure validation rules according to their specific needs and quality standards.

With a solid foundation and clear extension points, the Quality Assurance Service is well-positioned for future enhancements that could incorporate more advanced validation techniques, machine learning, and improved user interfaces for managing translation quality.
