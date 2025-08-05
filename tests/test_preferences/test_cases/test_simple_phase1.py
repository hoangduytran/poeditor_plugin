#!/usr/bin/env python3
"""
Simple test runner for Phase 1 foundation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}...")

# Create QApplication first
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Test the preferences import
try:
    import preferences
    print("✅ Preferences module imported successfully")
    
    # Test validation function
    result = preferences.validate_phase1_installation()
    if result:
        print("✅ Phase 1 validation PASSED")
    else:
        print("❌ Phase 1 validation FAILED")
        
    # Test status
    status = preferences.get_phase1_status()
    print(f"📊 Phase 1 Status: {status}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("🎉 Phase 1 basic test completed successfully!")
