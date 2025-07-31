# ...existing code...

class ProjectView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        self.project_label = QLabel("Projects")
        # Remove hard-coded styles - handled by CSS
        header_layout.addWidget(self.project_label)

        self.refresh_button = QPushButton("Refresh")
        # Remove hard-coded styles - handled by CSS
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Project table
        self.project_table = QTableWidget()
        # Remove hard-coded styles - handled by CSS
        self.project_table.setColumnCount(3)
        self.project_table.setHorizontalHeaderLabels(["Name", "Language", "Status"])

        # Set table properties
        header = self.project_table.horizontalHeader()
        header.setStretchLastSection(True)

        layout.addWidget(self.project_table)

# ...existing code...

