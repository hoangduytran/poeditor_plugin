Installation
============

Requirements
-----------

Before installing the POEditor Plugin application, ensure you have the following:

* Python 3.9 or newer
* PySide6 (Qt for Python)
* A Python virtual environment (recommended)

Setup Steps
----------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone https://github.com/yourusername/pyside_poeditor_plugin.git
    cd pyside_poeditor_plugin

2. Create a Virtual Environment (Optional but Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Using venv
    python -m venv venv
    
    # Activate the virtual environment
    # On Windows
    venv\Scripts\activate
    
    # On macOS/Linux
    source venv/bin/activate

3. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -r requirements.txt

4. Compile Resources
~~~~~~~~~~~~~~~~~~

The application uses Qt resources for icons and themes. Compile them with:

.. code-block:: bash

    # Run the resource compilation script
    ./compile_resources.sh

5. Run the Application
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Run directly with Python
    python main.py
    
    # Or use the provided task in VS Code
    # View > Command Palette > Tasks: Run Task > Run POEditor App

Development Setup
---------------

For development purposes, you might want to install additional packages:

.. code-block:: bash

    pip install -r requirements-dev.txt

This includes:
- pytest for testing
- flake8 for linting
- sphinx for documentation

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~

1. **PySide6 Installation Errors**:
   
   If you encounter issues installing PySide6, try:
   
   .. code-block:: bash
   
       pip install --index-url=https://download.qt.io/official_releases/QtForPython/ pyside6
   
2. **Resource Compilation Errors**:
   
   Ensure you have the PySide6 tools installed:
   
   .. code-block:: bash
   
       pip install PySide6-tools
   
3. **Application Crashes on Startup**:
   
   Check the log file at `application.log` for error details.

Platform-Specific Notes
---------------------

Windows
~~~~~~

* Ensure you have the Visual C++ Redistributable installed
* Some file operations may require administrative privileges

macOS
~~~~

* On newer macOS versions, you may need to grant permissions for the app to access the file system
* If using a virtual environment, ensure it has access to the system Qt libraries

Linux
~~~~~

* You may need to install additional libraries: `sudo apt-get install libxcb-xinerama0`
* For custom theming, ensure you have the Qt platform theme integration packages installed
