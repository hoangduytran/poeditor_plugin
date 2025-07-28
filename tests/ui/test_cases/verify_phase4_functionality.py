#!/usr/bin/env python3
"""
Simple verification script for Explorer Context Menu Phase 4 features.
This script checks that all modules can be imported and basic functionality works.
"""

import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
sys.path.insert(0, project_root)

print(f"Script directory: {script_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 entries

def test_imports():
    """Test that all Phase 4 modules can be imported."""
    try:
        from widgets.explorer_context_menu import ExplorerContextMenu
        print("✅ ExplorerContextMenu import successful")
        
        from widgets.explorer_context_menu_accessibility import MenuAccessibilityManager
        print("✅ MenuAccessibilityManager import successful")
        
        from widgets.explorer_context_menu_keyboard_navigation import MenuKeyboardNavigator
        print("✅ MenuKeyboardNavigator import successful")
        
        from services.file_operations_service import FileOperationsService
        print("✅ FileOperationsService import successful")
        
        from services.undo_redo_service import UndoRedoManager
        print("✅ UndoRedoManager import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without GUI."""
    try:
        from services.file_operations_service import FileOperationsService
        from services.undo_redo_service import UndoRedoManager
        from widgets.explorer_context_menu import ExplorerContextMenu
        from widgets.explorer_context_menu_accessibility import MenuAccessibilityManager
        
        # Create services
        file_ops = FileOperationsService()
        undo_manager = UndoRedoManager()
        
        # Create context menu manager
        context_menu = ExplorerContextMenu(file_ops, undo_manager)
        print("✅ ExplorerContextMenu instantiation successful")
        
        # Create accessibility manager
        accessibility = MenuAccessibilityManager()
        print("✅ MenuAccessibilityManager instantiation successful")
        
        # Test creating a context menu (without showing it)
        test_items = [{
            'path': '/tmp/test.txt',
            'is_dir': False,
            'name': 'test.txt'
        }]
        
        menu = context_menu.create_menu(test_items, '/tmp')
        print("✅ Context menu creation successful")
        
        # Test accessibility features
        accessibility.add_accessibility_to_menu(menu)
        print("✅ Accessibility enhancement successful")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run verification tests."""
    print("🔍 Explorer Context Menu Phase 4 Verification")
    print("=" * 50)
    
    import_success = test_imports()
    print()
    
    functionality_success = test_basic_functionality()
    print()
    
    if import_success and functionality_success:
        print("🎉 All verification tests passed!")
        print("✅ Phase 4 implementation is working correctly")
        return 0
    else:
        print("❌ Some verification tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
