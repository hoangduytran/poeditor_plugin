"""
Unit tests for the FileNumberingService.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from lg import logger
from services.file_numbering_service import FileNumberingService


class FileNumberingServiceTests(unittest.TestCase):
    """Test cases for the FileNumberingService."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.service = FileNumberingService()
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_extract_pattern_parentheses(self):
        """Test extracting numbering pattern with parentheses."""
        path = os.path.join(self.test_dir, "file (1).txt")
        base_name, separator, number, extension = self.service.extract_pattern(path)
        
        self.assertEqual(base_name, "file")
        self.assertEqual(separator, " (")
        self.assertEqual(number, 1)
        self.assertEqual(extension, ").txt")
        
    def test_extract_pattern_underscore(self):
        """Test extracting numbering pattern with underscore."""
        path = os.path.join(self.test_dir, "file_2.txt")
        base_name, separator, number, extension = self.service.extract_pattern(path)
        
        self.assertEqual(base_name, "file")
        self.assertEqual(separator, "_")
        self.assertEqual(number, 2)
        self.assertEqual(extension, ".txt")
        
    def test_extract_pattern_dash(self):
        """Test extracting numbering pattern with dash."""
        path = os.path.join(self.test_dir, "file-3.txt")
        base_name, separator, number, extension = self.service.extract_pattern(path)
        
        self.assertEqual(base_name, "file")
        self.assertEqual(separator, "-")
        self.assertEqual(number, 3)
        self.assertEqual(extension, ".txt")
        
    def test_extract_pattern_no_extension(self):
        """Test extracting numbering pattern from a file with no extension."""
        path = os.path.join(self.test_dir, "file (4)")
        base_name, separator, number, extension = self.service.extract_pattern(path)
        
        self.assertEqual(base_name, "file")
        self.assertEqual(separator, " (")
        self.assertEqual(number, 4)
        self.assertEqual(extension, ")")
        
    def test_extract_pattern_no_number(self):
        """Test extracting pattern from a file with no number."""
        path = os.path.join(self.test_dir, "file.txt")
        base_name, separator, number, extension = self.service.extract_pattern(path)
        
        self.assertEqual(base_name, "file")
        self.assertEqual(separator, " (")
        self.assertEqual(number, 0)
        self.assertEqual(extension, ").txt")
        
    def test_generate_numbered_name(self):
        """Test generating a numbered name when the original doesn't exist."""
        path = os.path.join(self.test_dir, "file.txt")
        new_path = self.service.generate_numbered_name(path)
        
        # If the file doesn't exist, it should return the original path
        self.assertEqual(path, new_path)
        
    def test_generate_numbered_name_exists(self):
        """Test generating a numbered name when the original already exists."""
        path = os.path.join(self.test_dir, "file.txt")
        
        # Create the original file
        with open(path, 'w') as f:
            f.write("Original")
            
        new_path = self.service.generate_numbered_name(path)
        expected_path = os.path.join(self.test_dir, "file (1).txt")
        
        self.assertEqual(new_path, expected_path)
        
    def test_generate_numbered_name_multiple_exists(self):
        """Test generating a numbered name when multiple numbered versions exist."""
        base_path = os.path.join(self.test_dir, "file.txt")
        path1 = os.path.join(self.test_dir, "file (1).txt")
        path2 = os.path.join(self.test_dir, "file (2).txt")
        
        # Create the original and numbered files
        with open(base_path, 'w') as f:
            f.write("Original")
        with open(path1, 'w') as f:
            f.write("Copy 1")
        with open(path2, 'w') as f:
            f.write("Copy 2")
            
        new_path = self.service.generate_numbered_name(base_path)
        expected_path = os.path.join(self.test_dir, "file (3).txt")
        
        self.assertEqual(new_path, expected_path)
        
    def test_generate_numbered_name_preferred_pattern(self):
        """Test generating a numbered name with a preferred pattern."""
        path = os.path.join(self.test_dir, "file.txt")
        
        # Create the original file
        with open(path, 'w') as f:
            f.write("Original")
            
        new_path = self.service.generate_numbered_name(path, preferred_pattern="_")
        expected_path = os.path.join(self.test_dir, "file_1.txt")
        
        self.assertEqual(new_path, expected_path)
        
    def test_detect_existing_numbering(self):
        """Test detecting existing numbered files in a directory."""
        # Create test files with different numbering patterns
        with open(os.path.join(self.test_dir, "doc (1).txt"), 'w') as f:
            f.write("Parentheses 1")
        with open(os.path.join(self.test_dir, "doc (3).txt"), 'w') as f:
            f.write("Parentheses 3")
        with open(os.path.join(self.test_dir, "doc_2.txt"), 'w') as f:
            f.write("Underscore 2")
        with open(os.path.join(self.test_dir, "doc-4.txt"), 'w') as f:
            f.write("Dash 4")
            
        result = self.service.detect_existing_numbering(self.test_dir, "doc")
        
        self.assertEqual(sorted(result["parentheses"]), [1, 3])
        self.assertEqual(result["underscore"], [2])
        self.assertEqual(result["dash"], [4])
        
    def test_get_next_available_number(self):
        """Test getting the next available number in a sequence."""
        # Create test files with parentheses pattern
        with open(os.path.join(self.test_dir, "report (1).txt"), 'w') as f:
            f.write("Report 1")
        with open(os.path.join(self.test_dir, "report (2).txt"), 'w') as f:
            f.write("Report 2")
        with open(os.path.join(self.test_dir, "report (5).txt"), 'w') as f:
            f.write("Report 5")
            
        next_number = self.service.get_next_available_number(
            self.test_dir, "report", "parentheses")
            
        self.assertEqual(next_number, 6)
        
    def test_get_next_available_number_no_existing(self):
        """Test getting the next available number when no numbered files exist."""
        next_number = self.service.get_next_available_number(
            self.test_dir, "nonexistent", "underscore")
            
        self.assertEqual(next_number, 1)


if __name__ == '__main__':
    unittest.main()
