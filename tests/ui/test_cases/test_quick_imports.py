#!/usr/bin/env python3
"""
Quick test to verify plugin imports are working.
"""

import sys
import os
from pathlib import Path
from lg import logger

# Adjust project root path from test file location
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger.info(f"Testing from directory: {project_root}")
logger.info(f"Python path: {sys.path[:3]}")

try:
    # Test core imports
    from core.api import PluginAPI
    logger.info("✅ Core API imported")
    
    # Test plugin imports
    from plugins.explorer import plugin as explorer_plugin
    logger.info("✅ Explorer plugin imported")
    
    from plugins.search import plugin as search_plugin
    logger.info("✅ Search plugin imported")
    
    from plugins.preferences import plugin as preferences_plugin
    logger.info("✅ Preferences plugin imported")
    
    from plugins.extensions import plugin as extensions_plugin
    logger.info("✅ Extensions plugin imported")
    
    from plugins.account import plugin as account_plugin
    logger.info("✅ Account plugin imported")
    
    logger.info("\n🎉 All plugins can be imported successfully!")
    
except Exception as e:
    logger.error(f"❌ Error: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
