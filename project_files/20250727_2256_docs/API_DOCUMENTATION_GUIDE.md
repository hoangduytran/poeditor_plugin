# API Documentation Guide

**Date**: July 27, 2025  
**Status**: Process Documentation  
**Component**: Documentation Standards

This guide explains how to generate and maintain API documentation for the POEditor Plugin project.

## Documentation Philosophy

We follow a progressive documentation approach where documentation is written during development rather than at the end of the project. This approach offers several benefits:

1. **Higher Quality Documentation**: Details are documented when they're fresh in the developer's mind
2. **Early API Design Feedback**: Writing documentation reveals design issues before they're deeply embedded in the code
3. **Enables Collaboration**: Other team members can use your components while you're still developing them
4. **Reduces Technical Debt**: Avoids the "we'll document later" trap that often leads to undocumented code
5. **Supports Testing**: Well-documented APIs are easier to write tests for

## Documentation Timing

- **Document as You Code**: Write or update documentation while implementing the feature
- **Immediate Updates**: Update documentation as soon as APIs change, not at the end of the project
- **Include in Definition of Done**: A feature is not complete until its documentation is updated
- **Document Before Sharing**: Always ensure documentation is up-to-date before sharing a component with other developers

## Generating Documentation

To generate the HTML API documentation, run the following command from the project root directory:

```bash
./generate_docs.py
```

This script will:
1. Check for and install required dependencies (Sphinx and sphinx_rtd_theme)
2. Create the necessary Sphinx configuration files
3. Generate .rst files for each module in the project
4. Build the HTML documentation

The generated documentation will be available in the `docs/build/html/` directory. Open `docs/build/html/index.html` in a browser to view it.

## Updating Documentation

The documentation is generated from docstrings in the code. To update the documentation:

1. Ensure your code has proper docstrings following the Google style format:
   ```python
   def my_function(param1, param2):
       """
       Description of function.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
           
       Raises:
           ExceptionType: Description of when this exception is raised
       """
       # Function implementation
   ```

2. After updating docstrings, re-run `./generate_docs.py` to rebuild the documentation

## Adding New Modules

If you add new modules to the project that need documentation:

1. Edit `generate_docs.py` to include the new module
2. Add the module to the appropriate section in the `create_module_docs()` function
3. Add the module to the appropriate index.rst file

## Documentation Standards

### API Reference Documentation

Each core service, interface, or public API must include:

- **Class/Module Overview**: Brief description of purpose and responsibility
- **Method Signatures**: Complete with parameter and return type information
- **Parameter Descriptions**: What each parameter is for, including valid values
- **Return Value Details**: What the method returns in different scenarios
- **Exception Information**: What exceptions might be raised and when
- **Thread Safety Notes**: Whether the API is thread-safe and any synchronization requirements

### Implementation Guides

For each major component or service, provide an implementation guide that includes:

- **Integration Examples**: How to use the component with other parts of the system
- **Common Patterns**: Best practices for using the API
- **Edge Cases**: How to handle unusual scenarios
- **Performance Considerations**: Any performance implications to be aware of

## Tips for Better Documentation

- Use meaningful descriptions in your docstrings
- Document all parameters, return values, and exceptions
- Include examples where appropriate
- Keep docstrings up to date when you change code
- Use type hints to provide better type information
- Create separate documents for API reference vs implementation guides
- Add diagrams to illustrate component relationships

## Viewing Documentation

After generating documentation, you can:

1. Open `docs/build/html/index.html` directly in your browser
2. Set up a simple HTTP server to view it: `python -m http.server -d docs/build/html`

## Customizing Documentation Theme

The documentation uses the ReadTheDocs theme by default. To customize:

1. Edit the `conf.py` file in `docs/source/`
2. Modify the `html_theme` and related settings

## Documentation Checklist

Before considering a component complete, ensure it has:

- [ ] API reference documentation for all public methods
- [ ] Implementation guide with integration examples
- [ ] Usage examples covering common scenarios
- [ ] Thread safety and performance notes
- [ ] Links to related components and services

## Examples of Well-Documented Components

Our `FileOperationsService`, `UndoRedoManager`, and `FileNumberingService` provide good examples of well-documented APIs:

- See `docs/CORE_SERVICES_API.md` for API reference
- See `docs/IMPLEMENTATION_GUIDE.md` for implementation examples
