# ...existing code...

class TranslationView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header with controls
        header_layout = QHBoxLayout()

        self.language_combo = QComboBox()
        # Remove hard-coded styles - handled by CSS
        header_layout.addWidget(QLabel("Language:"))
        header_layout.addWidget(self.language_combo)

        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("Search translations...")
        # Remove hard-coded styles - handled by CSS
        header_layout.addWidget(self.search_line)

        self.save_button = QPushButton("Save")
        # Remove hard-coded styles - handled by CSS
        header_layout.addWidget(self.save_button)

        layout.addLayout(header_layout)

        # Translation table
        self.translation_table = QTableWidget()
        # Remove hard-coded styles - handled by CSS
        self.translation_table.setColumnCount(3)
        self.translation_table.setHorizontalHeaderLabels(["Key", "Original", "Translation"])

        # Set table properties
        header = self.translation_table.horizontalHeader()
        header.setStretchLastSection(True)

        layout.addWidget(self.translation_table)

        # Detail panel
        self.setup_detail_panel(layout)

    def setup_detail_panel(self, parent_layout):
        detail_group = QGroupBox("Translation Details")
        # Remove hard-coded styles - handled by CSS
        detail_layout = QVBoxLayout(detail_group)

        # Key info
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.key_label = QLabel("")
        # Remove hard-coded styles - handled by CSS
        key_layout.addWidget(self.key_label)
        detail_layout.addLayout(key_layout)

        # Original text
        detail_layout.addWidget(QLabel("Original:"))
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        # Remove hard-coded styles - handled by CSS
        detail_layout.addWidget(self.original_text)

        # Translation text
        detail_layout.addWidget(QLabel("Translation:"))
        self.translation_text = QTextEdit()
        # Remove hard-coded styles - handled by CSS
        detail_layout.addWidget(self.translation_text)

        parent_layout.addWidget(detail_group)

# ...existing code...

