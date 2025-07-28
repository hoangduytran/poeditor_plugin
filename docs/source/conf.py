# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add project root to Python path for imports
project_root = os.path.abspath('../..')
sys.path.insert(0, project_root)

# -- Project information -----------------------------------------------------
project = 'POEditor Plugin'
copyright = '2025, POEditor Development Team'
author = 'POEditor Development Team'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

# Mock imports for unavailable dependencies
autodoc_mock_imports = ['PySide6', 'Qt']
