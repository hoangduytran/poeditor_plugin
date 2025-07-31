# ...existing code...

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POEditor Plugin")
        self.setGeometry(100, 100, 1200, 800)

        # Remove hard-coded styling - will be handled by CSS
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setup_ui()
        self.setup_menu_bar()

        # Apply theme from settings
        self.apply_theme()

    def setup_ui(self):
        # Create sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)

        # Create content area
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")

        # Add to layout
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content_area)

        # Setup sidebar content
        self.setup_sidebar()
        self.setup_content_area()

    def setup_sidebar(self):
        # ...existing code...
        pass

    def setup_content_area(self):
        # ...existing code...
        pass

    def setup_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        # ...existing code...

        # View menu
        view_menu = menubar.addMenu("View")

        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")

        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_action)

        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_action)

    def change_theme(self, theme_name):
        """Change the application theme"""
        from core.settings_manager import SettingsManager
        settings = SettingsManager()
        settings.set_setting("theme", theme_name)
        print(f"Theme changed to: {theme_name}")  # Debug output
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme from settings"""
        from core.settings_manager import SettingsManager
        from core.theme_manager import ThemeManager

        settings = SettingsManager()
        theme_name = settings.get_setting("theme", "light")
        print(f"Applying theme: {theme_name}")  # Debug output

        theme_manager = ThemeManager()
        stylesheet = theme_manager.get_theme_stylesheet(theme_name)

        if stylesheet:
            print(f"Loaded stylesheet length: {len(stylesheet)} characters")  # Debug output
            self.setStyleSheet(stylesheet)

            # Keep activity bar and status bar styles
            self.apply_fixed_styles()
        else:
            print(f"Failed to load stylesheet for theme: {theme_name}")

    def apply_fixed_styles(self):
        """Apply styles that should remain fixed regardless of theme"""
        activity_bar_style = """
        QFrame#activity_bar {
            background-color: #333333;
            border-right: 1px solid #444444;
        }
        QFrame#activity_bar QPushButton {
            background-color: transparent;
            border: none;
            padding: 8px;
            margin: 2px;
            border-radius: 4px;
        }
        QFrame#activity_bar QPushButton:hover {
            background-color: #444444;
        }
        QFrame#activity_bar QPushButton:checked {
            background-color: #0078d4;
        }
        """

        status_bar_style = """
        QStatusBar {
            background-color: #007acc;
            color: white;
            border-top: 1px solid #005999;
        }
        QStatusBar::item {
            border: none;
        }
        """

        # Apply fixed styles
        current_stylesheet = self.styleSheet()
        self.setStyleSheet(current_stylesheet + activity_bar_style + status_bar_style)
        print("Fixed styles applied")  # Debug output

# ...existing code...
