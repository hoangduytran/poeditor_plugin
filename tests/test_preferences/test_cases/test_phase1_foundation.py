"""
Test script for Phase 1: Common Components Foundation

This script validates the Phase 1 implementation by testing core components,
database functionality, and integration points.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Create QApplication first
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from lg import logger

# Import from main project preferences module
from preferences import (
    validate_phase1_installation, get_phase1_status,
    DatabaseManager, PreferenceSearchRequest, ReplacementRecord,
    ImportExportService, create_preferences_dialog
)
from preferences.data_models import DatabasePORecord


def test_database_functionality():
    """Test database creation and basic operations."""
    logger.info("Testing database functionality...")
    
    try:
        # Test in-memory database
        db = DatabaseManager(":memory:")
        
        # Initialize schema
        if not db.initialize_database():
            logger.error("Database initialization failed")
            return False
        
        # Test database stats
        stats = db.get_database_stats()
        logger.info(f"Database stats: {stats}")
        
        # Test backup (will fail for in-memory, but shouldn't crash)
        try:
            db.backup_database("/tmp/test_backup.db")
        except Exception as e:
            logger.debug(f"Expected backup failure for in-memory DB: {e}")
        
        logger.info("Database functionality test passed")
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False


def test_data_models():
    """Test data model creation and serialization."""
    logger.info("Testing data models...")
    
    try:
        # Test ReplacementRecord
        replacement = ReplacementRecord(
            find_text="hello",
            replace_text="world",
            enabled=True,
            use_regex=False
        )
        
        # Test serialization
        replacement_dict = replacement.to_dict()
        replacement_restored = ReplacementRecord.from_dict(replacement_dict)
        
        if replacement.find_text != replacement_restored.find_text:
            logger.error("ReplacementRecord serialization failed")
            return False
        
        # Test DatabasePORecord
        po_record = DatabasePORecord(
            msgid="Test message",
            msgctxt="context",
            current_msgstr="Test translation",
            fuzzy=False
        )
        
        po_dict = po_record.to_dict()
        po_restored = DatabasePORecord.from_dict(po_dict)
        
        if po_record.msgid != po_restored.msgid:
            logger.error("DatabasePORecord serialization failed")
            return False
        
        logger.info("Data models test passed")
        return True
        
    except Exception as e:
        logger.error(f"Data models test failed: {e}")
        return False


def test_search_functionality():
    """Test search request creation and processing."""
    logger.info("Testing search functionality...")
    
    try:
        # Test search request creation
        search_req = PreferenceSearchRequest(
            query="test",
            table_type="replacement"
        )
        
        if search_req.query != "test":
            logger.error("Search request creation failed")
            return False
        
        logger.info("Search functionality test passed")
        return True
        
    except Exception as e:
        logger.error(f"Search test failed: {e}")
        return False


def test_import_export():
    """Test import/export service."""
    logger.info("Testing import/export service...")
    
    try:
        service = ImportExportService()
        
        # Test format registration
        formats = service.get_supported_formats()
        if not formats:
            logger.error("No supported formats found")
            return False
        
        logger.info(f"Supported formats: {list(formats.keys())}")
        
        # Test file filter generation
        filter_str = service.get_file_filter_string()
        if not filter_str:
            logger.error("Failed to generate file filter string")
            return False
        
        logger.info("Import/Export service test passed")
        return True
        
    except Exception as e:
        logger.error(f"Import/Export test failed: {e}")
        return False


def test_dialog_creation():
    """Test preferences dialog creation."""
    logger.info("Testing dialog creation...")
    
    try:
        # This requires PySide6 to be available
        dialog = create_preferences_dialog()
        
        if not dialog:
            logger.error("Failed to create preferences dialog")
            return False
        
        # Test database manager access
        db_manager = dialog.get_database_manager()
        if not db_manager:
            logger.error("Failed to get database manager from dialog")
            return False
        
        logger.info("Dialog creation test passed")
        return True
        
    except Exception as e:
        logger.error(f"Dialog creation test failed: {e}")
        return False


def run_phase1_tests():
    """Run all Phase 1 tests."""
    logger.info("Starting Phase 1: Common Components Foundation tests")
    
    # Run validation
    valid, issues = validate_phase1_installation()
    if not valid:
        logger.error(f"Phase 1 validation failed: {issues}")
        return False
    
    # Individual component tests
    tests = [
        ("Database Functionality", test_database_functionality),
        ("Data Models", test_data_models),
        ("Search Functionality", test_search_functionality),
        ("Import/Export Service", test_import_export),
        ("Dialog Creation", test_dialog_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if test_func():
                logger.info(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test FAILED with exception: {e}")
    
    # Summary
    logger.info(f"\n--- Phase 1 Test Summary ---")
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All Phase 1 tests PASSED!")
        
        # Show status
        status = get_phase1_status()
        logger.info(f"Phase: {status['phase']}")
        logger.info(f"Version: {status['version']}")
        logger.info(f"Ready for next phase: {status['ready_for_phase2']}")
        
        return True
    else:
        logger.error(f"❌ {total - passed} tests FAILED")
        return False


if __name__ == "__main__":
    success = run_phase1_tests()
    sys.exit(0 if success else 1)
