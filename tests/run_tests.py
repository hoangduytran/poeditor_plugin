#!/usr/bin/env python3
"""
Test runner for POEditor Plugin services.

This script runs the unit tests for the services package.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lg import logger


def run_service_tests():
    """Run all service tests."""
    logger.info("Starting service tests...")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "services"
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    if result.wasSuccessful():
        logger.info(f"All tests passed! Ran {result.testsRun} tests.")
        return True
    else:
        logger.error(f"Tests failed! {len(result.failures)} failures, {len(result.errors)} errors.")
        return False


if __name__ == '__main__':
    success = run_service_tests()
    sys.exit(0 if success else 1)
