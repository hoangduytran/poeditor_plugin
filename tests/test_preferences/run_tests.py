#!/usr/bin/env python3
"""
Test runner for preferences module tests.

This script runs all preference-related tests and provides a summary report.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from lg import logger


def run_phase1_tests():
    """Run Phase 1 foundation tests."""
    logger.info("Running Phase 1: Common Components Foundation tests...")
    
    test_file = Path(__file__).parent / "test_cases" / "test_phase1_foundation.py"
    
    try:
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            logger.info("✅ Phase 1 tests PASSED")
            print(result.stdout)
            return True
        else:
            logger.error("❌ Phase 1 tests FAILED")
            print(result.stderr)
            return False
    except Exception as e:
        logger.error(f"Error running Phase 1 tests: {e}")
        return False


def main():
    """Main test runner."""
    print("=" * 60)
    print("Preferences Module Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 1
    
    # Run Phase 1 tests
    if run_phase1_tests():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All preferences tests PASSED!")
        return 0
    else:
        print("❌ Some preferences tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
