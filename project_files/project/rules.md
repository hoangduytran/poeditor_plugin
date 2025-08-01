
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

4. **Automated Testing**  
   - Test and debug files are created in tests/<component>/test_cases if checks needed to be done, and md files in tests/<component>/update_md if needed. <component> here means ('workspace', 'editor', 'ui' etc..)
   - Write unit tests for core logic and plugin loading.
   - Avoid using mock objects, using already created and existed objects in tests.
   - Make use of the logger in lg to log your tests.
   - Use mocks for plugin interfaces if they are not already existed.
   - Add integration tests for plugin registration and UI behavior.
   - Always use pylint and pyflakes, py_compile to perform sanity checks of files and clean up/fix issues.


5. **Documentation**  
   - Maintain up-to-date user and developer documentation.
   - Include examples for plugin authors.
   - Design and documentations are put into project_files/<component> directories (prefix by date/time using format 'YYYYMMDD_HHMMSSzz_', ie. "%Y%m%d_%H%M%S") so we can observe the sequence of designs. In order to get the current system time, in the tests dir, use 'date' function to get the local time correctly.
   - Add API documentations and perform generations of API <PROJECT_DIR/docs> if required in the docs directory with proper directory structure for the components.
   - **Documentation Timing**:
     * Create API documentation progressively during development, not at the end of the project.
     * Update documentation immediately when API changes are made.
     * Include API documentation as part of the "definition of done" for each component.
     * Maintain both reference documentation (API specs) and implementation guides with examples.

6. **Error Handling & Logging**  
   - Catch and log exceptions in plugin loading and execution.
   - Provide clear error messages for plugin failures.
   - Import lg.py and use logger from this module to log errors as this one will give the name of the module where log message is coming from, making it easier to track.

7. **Version Control**  
   - Use git for source control.
   - Commit frequently with meaningful messages.
   - Use branches for features and bugfixes.

8. **Continuous Integration**  
   - Set up CI to run tests and lint checks on every commit.

9. **Extensibility & Backward Compatibility**  
   - Design the Plugin API to be extensible.
   - Avoid breaking changes; deprecate features gradually.

10. **User Experience**  
    - Ensure the UI is responsive and accessible.
    - Provide feedback for plugin actions and errors.

11. **Security**  
    - Sandbox plugins if possible.
    - Validate and sanitize plugin inputs.

12. **Code Reviews**  
    - Review code changes, especially for core and API changes.

13. **Forbidances**
   - Imports, modifications to project_files/old_codes directory. This is only served as a referencing point to the old codes, which will be used to adapt to the current system.
   - The use of hasattr and getattr (using direct object.attr instead for quick access), must double check with where the objects were declared and ensure the __init__ section of the code declared the reference and that somewhere in the code, a value/address assignment has already done to ensure execution works without errors. 
   - Use direct object.attr also help to indicate whether the code is sound or not, if not, exception will raised, which is much more sensible option, allows one to fix the code rahter than suffer quietly in silence, which is more dangerous, bloated codes.
   - Try to avoid using try/catch as this would also slow down the code. We prefer the code to be accurate, clean, and fast, lean approach.
   - The use of print in code/tests, use 'from lg import logger' to write logging messages. This will give the correct locations where log messages are coming from. Ensure that the import is located at the top of the source code file and NOT REPEATING in the code.


14. **Commit After Changes**
    - I'm using local repository, no github.
    - For each large part of the plan, create a branch.    
    - Commit after each changes so we can roll back if needed.
    - Merge to main after a large section completed. Ask if you're not sure.
   