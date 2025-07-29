# POEditor Plugin - Enhanced File Explorer

A modern, plugin-based file explorer application built with PySide6 featuring an advanced activity sidebar and enhanced navigation capabilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.5.0+-green.svg)](https://pypi.org/project/PySide6/)

## 🎯 Project Status

**Current Phase**: Explorer Header Navigation System Design Complete  
**Implementation Status**: Ready for Phase 1 Development  
**Branch**: `feature/explorer-header-navigation`  
**Documentation**: Comprehensive technical design completed  

## 📋 Overview

POEditor Plugin is a sophisticated file explorer application that reimagines file management through a modern plugin architecture. The application features an innovative activity-based sidebar with multiple specialized panels, each designed for specific file management workflows.

### 🎨 Key Design Philosophy

- **Plugin Architecture**: Modular design allowing easy extension and customization
- **Activity-Based Navigation**: Specialized panels for different user workflows
- **Documentation-First Development**: Comprehensive design before implementation
- **Accessibility-Compliant**: Full keyboard navigation and screen reader support
- **Modern UI/UX**: Clean, intuitive interface following contemporary design patterns

## 🏗️ Architecture

### Core Architecture
```
┌─────────────────────────────────────────────────────────┐
│                  Main Application                       │
├─────────────────┬───────────────────────────────────────┤
│   Activity      │            Content Area               │
│   Sidebar       │  ┌─────────────────────────────────┐  │
│                 │  │     Explorer Panel              │  │
│  ┌───────────┐  │  │  ┌─────────────────────────────┐ │  │
│  │ Explorer  │  │  │  │    Header Navigation       │ │  │
│  │ Search    │  │  │  │ [Goto▼] [Search] [←→↑🏠]   │ │  │
│  │ Account   │  │  │  ├─────────────────────────────┤ │  │
│  │Extensions │  │  │  │    File Tree View           │ │  │
│  │Preferences│  │  │  │                             │ │  │
│  └───────────┘  │  │  └─────────────────────────────┘ │  │
│                 │  └─────────────────────────────────────┘  │
└─────────────────┴───────────────────────────────────────────┘
```

### Service Layer
```
Core Services
├── NavigationService          # Navigation orchestration
├── PluginManager             # Plugin lifecycle management  
├── SidebarManager            # Activity panel coordination
├── TabManager                # Tab management system
└── LocationManager           # Bookmarks and quick locations

Navigation Services (In Development)
├── NavigationHistoryService  # Back/forward navigation
├── PathCompletionService     # Auto-completion with threading
├── ColumnConfigurationService # Column display management
└── NavigationStateManager    # Current navigation state
```

## 🚀 Current Features

### ✅ Implemented
- **Plugin Architecture**: Complete modular plugin system
- **Activity Sidebar**: 5 specialized activity panels
- **Core Explorer**: Basic file browsing with tree view
- **Modern UI**: Clean interface with theme support
- **Resource System**: Compiled Qt resources for icons and styles

### 🎯 Explorer Panel Activities
1. **Explorer** - Main file browsing interface
2. **Search** - Advanced file search capabilities  
3. **Account** - User account management
4. **Extensions** - Plugin management interface
5. **Preferences** - Application settings and configuration

## 🔄 Current Development: Explorer Header Navigation

The project is currently implementing a comprehensive Explorer Header Navigation System with the following components:

### 📋 Phase 1: Foundation Services (Current)
- **NavigationService**: Core navigation orchestration
- **LocationManager**: Quick locations and bookmark management
- **NavigationHistoryService**: Back/forward navigation tracking
- **PathCompletionService**: Intelligent path auto-completion

### 🎨 Designed UI Components
```
Explorer Header Context Menu (Right-click)
├── Quick Navigation
│   ├── [Goto ▼] Location Dropdown Interface    
│   ├── [Search] Path Search Field Interface
│   └── [← → ↑ 🏠] Navigation Buttons
├── Quick Locations
│   ├── 🏠 Home, 💾 Root, 📁 Applications
│   ├── 📄 Documents, ⬇️ Downloads, 🖥️ Desktop
│   └── ⚙️ Project Root
├── Recent Locations (with timestamps)
├── Bookmarks (user-defined with custom icons)
├── Navigation Actions (Go to Path, Manage Bookmarks)
└── Column Management (Add/Remove, Settings, Reset)
```

### 📊 Advanced Column Management
- **Available Columns**: Name, Size, Modified, Type, Created, Permissions, Owner, Extension, Path
- **Column Attributes**: Width, resizable, alignment, sort configuration
- **Manager Dialog**: Tabbed interface for comprehensive column control
- **Persistence**: User preferences saved and restored

## 📁 Project Structure

```
pyside_poeditor_plugin/
├── 📄 README.md                    # This file
├── 📄 main.py                      # Application entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 resources.qrc               # Qt resource definitions
├── 📄 resources_rc.py             # Compiled Qt resources
├── 📁 core/                       # Core application modules
│   ├── main_app_window.py         # Main application window
│   ├── plugin_manager.py          # Plugin system management
│   ├── sidebar_manager.py         # Activity sidebar coordination
│   └── tab_manager.py             # Tab management system
├── 📁 panels/                     # Activity panel implementations
│   ├── explorer_panel.py          # Main file explorer panel
│   ├── search_panel.py            # File search interface
│   ├── account_panel.py           # User account management
│   ├── extensions_panel.py        # Plugin management UI
│   └── preferences_panel.py       # Application preferences
├── 📁 plugins/                    # Plugin implementations
│   ├── explorer/                  # Explorer plugin components
│   ├── search/                    # Search plugin components
│   └── [other plugins]/           # Additional plugin modules
├── 📁 services/                   # Business logic services
├── 📁 models/                     # Data models and structures
├── 📁 widgets/                    # Reusable UI components
├── 📁 styles/                     # Application themes and styles
├── 📁 icons/                      # Application icons and graphics
└── 📁 project_files/              # Development documentation
    └── 20250729_0811_explorer_header_navigation/
        ├── 📄 20250729_0815_EXPLORER_HEADER_NAVIGATION_MASTER_PLAN.md
        ├── 📄 20250729_0820_HEADER_CONTEXT_MENU_DESIGN.md  
        ├── 📄 20250729_0825_NAVIGATION_SERVICE_ARCHITECTURE.md
        ├── 📄 20250729_0830_COLUMN_MANAGEMENT_DESIGN.md
        ├── 📄 20250729_0835_IMPLEMENTATION_ROADMAP.md
        └── 📄 README.md
```

## 📚 Documentation

### 🎯 Current Feature Documentation
- **[Master Plan](project_files/20250729_0811_explorer_header_navigation/20250729_0815_EXPLORER_HEADER_NAVIGATION_MASTER_PLAN.md)**: Comprehensive system design (4000+ lines)
- **[Context Menu Design](project_files/20250729_0811_explorer_header_navigation/20250729_0820_HEADER_CONTEXT_MENU_DESIGN.md)**: Right-click menu technical implementation
- **[Service Architecture](project_files/20250729_0811_explorer_header_navigation/20250729_0825_NAVIGATION_SERVICE_ARCHITECTURE.md)**: Core navigation services design
- **[Column Management](project_files/20250729_0811_explorer_header_navigation/20250729_0830_COLUMN_MANAGEMENT_DESIGN.md)**: Advanced column configuration system
- **[Implementation Roadmap](project_files/20250729_0811_explorer_header_navigation/20250729_0835_IMPLEMENTATION_ROADMAP.md)**: 5-phase development plan

### 🔧 Technical Documentation
- **API Documentation**: Located in `docs/` directory
- **Architecture Guides**: Component and service interaction patterns
- **Developer Guides**: Plugin development and extension guidelines
- **User Guides**: Feature usage and workflow documentation

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11 or higher
- PySide6 6.5.0+
- setuptools

### Quick Start
```bash
# Clone the repository
git clone https://github.com/hoangduytran/poeditor_plugin.git
cd poeditor_plugin

# Install dependencies
pip install -r requirements.txt

# Compile resources (if needed)
./compile_resources.sh

# Run the application
python main.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Switch to development branch
git checkout feature/explorer-header-navigation

# Compile resources
./compile_resources.sh

# Run with development settings
python main.py
```

## 🎯 Implementation Roadmap

### Phase 1: Foundation Services (Current - Week 1)
- ✅ NavigationService core implementation
- ✅ LocationManager with quick locations
- ✅ NavigationHistoryService with persistence
- ✅ PathCompletionService with threading

### Phase 2: UI Components (Week 2)
- 🔄 ExplorerHeaderBar widget
- 🔄 GotoDropdown with quick locations
- 🔄 PathSearchField with auto-completion
- 🔄 NavigationButtons (back/forward/up/home)

### Phase 3: Context Menu System (Week 3)
- 🔄 ExplorerHeaderContextMenu implementation
- 🔄 Dynamic menu building with sections
- 🔄 Service integration and signal handling
- 🔄 Accessibility features and keyboard shortcuts

### Phase 4: Column Management (Week 4)
- 🔄 ColumnConfigurationService
- 🔄 ColumnManagerDialog interface
- 🔄 Column definition system
- 🔄 Persistence and state management

### Phase 5: Integration & Polish (Week 5)
- 🔄 Explorer panel integration
- 🔄 Testing and quality assurance
- 🔄 Performance optimization
- 🔄 Documentation completion

## 🔧 Development

### Running Tasks
```bash
# Run the application
python main.py

# Or use VS Code tasks
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Run POEditor App"

# Compile resources
./compile_resources.sh

# Install dependencies
pip install PySide6 setuptools
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function signatures  
- Document all public methods and classes
- Maintain comprehensive docstrings

### Testing Strategy
- Unit tests for all service components
- Integration tests for UI components
- Accessibility testing with screen readers
- Performance testing for large directory navigation

## 🤝 Contributing

### Development Workflow
1. **Documentation First**: All features begin with comprehensive design documents
2. **Branch Strategy**: Feature branches from main with descriptive names
3. **Code Review**: All changes require review before merging
4. **Testing Required**: Unit and integration tests for all new features

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Create design documentation in `project_files/`
4. Implement the feature following the documentation
5. Add comprehensive tests
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Commit Message Format
```
feat: add navigation history service with persistence

- Implement NavigationHistoryService class
- Add SQLite persistence for navigation history
- Include back/forward navigation methods
- Add comprehensive unit tests
- Update documentation with API reference

Closes #123
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PySide6 Team**: For the excellent Qt Python bindings
- **Qt Framework**: For the robust cross-platform UI framework
- **Python Community**: For the amazing ecosystem and tools

## 📞 Contact & Support

- **Repository**: [https://github.com/hoangduytran/poeditor_plugin](https://github.com/hoangduytran/poeditor_plugin)
- **Issues**: [GitHub Issues](https://github.com/hoangduytran/poeditor_plugin/issues)
- **Documentation**: See `docs/` directory for comprehensive guides

---

## 🚀 What's Next?

The Explorer Header Navigation System represents a significant enhancement to the file management experience. With comprehensive documentation complete, the implementation phase will deliver:

1. **Intuitive Navigation**: Right-click header menu with quick access to common locations
2. **Advanced Search**: Path auto-completion with intelligent suggestions  
3. **Flexible Columns**: Complete column management with user customization
4. **Navigation History**: Back/forward navigation with persistent history
5. **Bookmark System**: Custom bookmarks with organization and quick access

**Ready to explore the future of file management? 🗂️✨**
