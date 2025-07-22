"""
Panels package for the PySide POEditor plugin.

This package provides panel implementations for the Activity Bar.
"""

from panels.explorer_panel import ExplorerPanel
from panels.search_panel import SearchPanel
from panels.preferences_panel import PreferencesPanel
from panels.extensions_panel import ExtensionsPanel
from panels.account_panel import AccountPanel

__all__ = [
    'ExplorerPanel',
    'SearchPanel',
    'PreferencesPanel',
    'ExtensionsPanel',
    'AccountPanel'
]