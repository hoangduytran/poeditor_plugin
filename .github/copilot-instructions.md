# Copilot Instructions for AI Coding Agents

Welcome to the PySide POEditor Plugin codebase! This guide is for AI coding agents (e.g., GitHub Copilot, ChatGPT) to maximize productivity and maintain code quality in this project.

## Project Overview
- **Framework:** PySide6 (Qt for Python)
- **Architecture:** Modular, plugin-based with core, panels, plugins, services, and managers
- **Theming:** Centralized QSS/CSS system, themes in `assets/styles/`
- **Logging:** Custom logger, output to `application.log`
- **Testing:** Unit and integration tests, especially for UI and services

## Key Conventions
- **Code Style:**
  - Follow PEP 8
  - Use type hints for all function signatures
  - Document all public methods/classes with docstrings
- **Directory Structure:**
  - `core/`: Core logic (ThemeManager, SettingsManager, etc.)
  - `panels/`: UI panels (sidebar, explorer, etc.)
  - `plugins/`: Modular plugin system
  - `assets/styles/`: QSS/CSS theme files (edit these for theming)
  - `application.log`: Main log file (check for debug info)
  - `tests/`: Test cases (unit/integration)
  - `project_files/`: Design docs, patches, and feature specs

## Theming & Styling
- **ThemeManager** loads QSS from `assets/styles/` (not `themes/`)
- To change the app's look, edit the relevant CSS file in `assets/styles/`
- Use objectName selectors for widget-specific styling (e.g., `#sidebar`)
- Confirm theme file loading via logger output in `application.log`

## Development Workflow
1. **Documentation First:** Start with a design doc in `project_files/`
2. **Branching:** Use feature branches from `main`
3. **Testing:** Add/maintain unit and integration tests for all features
4. **Code Review:** All changes require review before merging
5. **Commit Format:**
   ```
   feat: add navigation history service with persistence
   - Implement NavigationHistoryService class
   - ...
   Closes #123
   ```

## Testing
- Run tests with your preferred runner or via VS Code tasks
- Check `application.log` for debug output
- Ensure new features have comprehensive test coverage

## Common Tasks
- **Run app:** `python main.py` or VS Code task "Run POEditor App"
- **Compile resources:** `./compile_resources.sh`
- **Install dependencies:** `pip install -r requirements.txt` or use VS Code task

## AI Agent Guidance
- **Always check which theme file is loaded at runtime (see logger output)**
- **Edit only the CSS file actually loaded by ThemeManager**
- **Use logging for debugging file paths and runtime behavior**
- **Respect modular architecture and directory boundaries**
- **Document all changes and update tests as needed**

## References
- See `README.md` for architecture and workflow
- See `docs/` for technical and user guides
- For questions, check `application.log` or open an issue

# 📝 Project Engineering Rules (Reference)

The best software engineering practices include:

1. **Modular Architecture**  
   - Separate core logic, plugins, and UI components into clear modules/directories.
   - Use interfaces (like your PluginAPI) to decouple core and plugins.

2. **Clear API Contracts**  
   - Document the Plugin API thoroughly.
   - Use type hints and docstrings for all public methods.

3. **Consistent Coding Standards**  
   - Follow PEP8 for Python code.
   - Use linters (e.g., flake8, pylint) and auto-formatters (e.g., black).
   - Make sure names are consistent, do not create confusions of terms, remove redundancy, use the same file_name for class_name (file name uses lower case, classname use mixed UpperLower case).
   - **Architecture Terminology** (VS Code-like):
     * **ActivityBar** (`widgets/activity_bar.py`): Full-featured vertical navigation buttons with plugin API support
     * **SidebarActivityBar** (`core/sidebar_manager.py`): Simple activity bar implementation for basic sidebar functionality
     * **SidebarManager** (`core/sidebar_manager.py`): Complete left sidebar containing activity bar + panel container
     * **Panel Container**: QStackedWidget holding the actual content panels (Explorer, Search, etc.)

4. **Readable Multi-Condition If Statements**
   - **Formatting for Readability:**
     * Break complex conditions into multiple lines with proper indentation
     * Group related conditions with parentheses for clarity
     * Use meaningful variable names for intermediate boolean values
     * Align operators vertically when splitting across lines
   - **Best Practices by Language:**
     * **Python:** Use `and`/`or` keywords, break at logical operators
       ```python
       # Good - Clear grouping and formatting
       if (user.is_authenticated and user.has_permission('read') and
           (document.is_public or document.owner == user) and
           not document.is_archived):
           process_document(document)
       
       # Better - Extract complex logic
       can_access_document = (
           user.is_authenticated and 
           user.has_permission('read') and
           (document.is_public or document.owner == user)
       )
       if can_access_document and not document.is_archived:
           process_document(document)
       ```
     * **C++/JavaScript:** Use `&&`/`||`, similar formatting principles
       ```cpp
       // C++ - Good formatting
       if ((user.isAuthenticated() && user.hasPermission("read")) &&
           (document.isPublic() || document.getOwner() == user) &&
           !document.isArchived()) {
           processDocument(document);
       }
       ```
   - **Readability Guidelines:**
     * **Short-circuit evaluation:** Place most likely false conditions first for `&&`, most likely true for `||`
     * **Avoid deep nesting:** Use early returns or guard clauses instead of nested if statements
     * **Group logically:** Use parentheses to group related conditions even when not required
     * **Extract complex expressions:** Create boolean variables for complex sub-conditions
     * **Consistent indentation:** Align continuation lines consistently (4 spaces recommended)
   - **Common Patterns:**
     ```python
     # Permission checking pattern
     has_basic_access = user.is_active and not user.is_suspended
     has_resource_access = (resource.is_public or 
                           user in resource.allowed_users or
                           user.role in resource.allowed_roles)
     
     if has_basic_access and has_resource_access:
         grant_access()
     
     # Validation pattern with early return
     def validate_input(data):
         if not data or not isinstance(data, dict):
             return False
         
         required_fields = ['name', 'email', 'type']
         if not all(field in data for field in required_fields):
             return False
         
         if (not data['email'].count('@') == 1 or
             len(data['name']) < 2 or
             data['type'] not in VALID_TYPES):
             return False
         
         return True
     ```

5. **Automated Testing**  
   - Test and debug files are created in tests/<component>/test_cases if checks needed to be done, and md files in tests/<component>/update_md if needed. <component> here means ('workspace', 'editor', 'ui' etc..)
   - Write unit tests for core logic and plugin loading.
   - Avoid using mock objects, using already created and existed objects in tests.
   - Make use of the logger in lg to log your tests.
   - Use mocks for plugin interfaces if they are not already existed.
   - Add integration tests for plugin registration and UI behavior.
   - Always use pylint and pyflakes, py_compile to perform sanity checks of files and clean up/fix issues.

6. **Documentation**  
   - Avoid using 'Grid' containers.
   - Maintain up-to-date user and developer documentation.
   - Include examples for plugin authors.
   - Design and documentations are put into project_files/<component> directories (prefix by date/time using format 'YYYYMMDD_HHMMSSzz_', ie. "%Y%m%d_%H%M%S") so we can observe the sequence of designs. In order to get the current system time, in the tests dir, use 'date' function to get the local time correctly.
   - Add API documentations and perform generations of API <PROJECT_DIR/docs> if required in the docs directory with proper directory structure for the components.
   - **Documentation Timing**:
     * Create API documentation progressively during development, not at the end of the project.
     * Update documentation immediately when API changes are made.
     * Include API documentation as part of the "definition of done" for each component.
     * Maintain both reference documentation (API specs) and implementation guides with examples.

7. **Error Handling & Logging**  
   - Catch and log exceptions in plugin loading and execution.
   - Provide clear error messages for plugin failures.
   - Import lg.py and use logger from this module to log errors as this one will give the name of the module where log message is coming from, making it easier to track.

8. **Version Control**  
   - Use git for source control.
   - Commit frequently with meaningful messages.
   - Use branches for features and bugfixes.

9. **Continuous Integration**  
   - Set up CI to run tests and lint checks on every commit.

10. **Extensibility & Backward Compatibility**  
    - Design the Plugin API to be extensible.
    - Avoid breaking changes; deprecate features gradually.

11. **User Experience**  
    - Ensure the UI is responsive and accessible.
    - Provide feedback for plugin actions and errors.

12. **Security**  
    - Sandbox plugins if possible.
    - Validate and sanitize plugin inputs.

13. **Code Reviews**  
    - Review code changes, especially for core and API changes.

14. **Forbidances**
   - Imports, modifications to project_files/old_po_app_design/old_codes directory. This is only served as a referencing point to the old codes, which will be used to adapt to the current system.
   - The use of hasattr and getattr (using direct object.attr instead for quick access), must double check with where the objects were declared and ensure the __init__ section of the code declared the reference and that somewhere in the code, a value/address assignment has already done to ensure execution works without errors. 
   - Use direct object.attr also help to indicate whether the code is sound or not, if not, exception will raised, which is much more sensible option, allows one to fix the code rahter than suffer quietly in silence, which is more dangerous, bloated codes.
   - Try to avoid using try/catch as this would also slow down the code. We prefer the code to be accurate, clean, and fast, lean approach.
   - The use of print in code/tests, use 'from lg import logger' to write logging messages. This will give the correct locations where log messages are coming from. Ensure that the import is located at the top of the source code file and NOT REPEATING in the code.


15. **Commit After Changes**
    - I'm using local repository, no github.
    - For each large part of the plan, create a branch.    
    - Commit after each changes so we can roll back if needed.
    - Merge to main after a large section completed. Ask if you're not sure.
