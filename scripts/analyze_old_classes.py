#!/usr/bin/env python3
"""
Script to analyze all classes in the old_po_app_design/old_codes directory.
Exports a CSV file with class information, usage data, and classification.
"""

import os
import re
import ast
import csv
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
from lg import logger


# Configuration constants
OLD_CODES_DIR = os.path.join('project_files', 'old_po_app_design', 'old_codes')
OUTPUT_CSV = os.path.join('project_files', 'old_po_app_design', 'old_classes_analysis.csv')
BASE_DIR = os.getcwd()  # Assumes script is run from project root

# Classification patterns - based on class name, path or inheritance
CLASSIFICATION_PATTERNS = {
    'GUI Component': [
        r'Dialog$', r'Widget$', r'Window$', r'Tab$', r'View$', r'Panel$',
        r'widgets/', r'gui/', r'/ui/', 
        r'(QWidget|QDialog|QMainWindow|QFrame)'
    ],
    'Data Model': [
        r'Model$', r'Entry$', r'Item$', r'Data$', r'Record$',
        r'models/', r'/data/', r'dataclass'
    ],
    'Service': [
        r'Service$', r'Manager$', r'Provider$', r'Handler$',
        r'services/', r'/handlers/'
    ],
    'Utility': [
        r'Utils$', r'Util$', r'Helper$', r'Factory$',
        r'utils/', r'/helpers/'
    ],
    'Controller': [
        r'Controller$', r'Mediator$', r'Coordinator$',
        r'controllers/', r'/mediators/'
    ],
    'Enum/Constant': [
        r'Enum$', r'Mode$', r'Type$', r'Status$', r'State$',
        r'enums/', r'(Enum)'
    ]
}


class ClassInfo:
    """Store and manage information about a class."""
    
    def __init__(self, name: str, bases: List[str], doc: str, file_path: str, line_number: int):
        self.name = name
        self.bases = bases
        self.doc = self._clean_doc(doc)
        self.file_path = file_path
        self.line_number = line_number
        self.used_in: Dict[str, Set[int]] = defaultdict(set)  # file path -> line numbers
        self.classification = self._classify()
        
    def _clean_doc(self, doc: str) -> str:
        """Clean up and format the docstring."""
        if not doc:
            return ""
        # Remove newlines and excessive whitespace
        return re.sub(r'\s+', ' ', doc).strip()
    
    def _classify(self) -> str:
        """Classify the class based on name, path, and base classes."""
        combined_info = f"{self.name} {self.file_path} {' '.join(self.bases)}"
        
        for classification, patterns in CLASSIFICATION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_info, re.IGNORECASE):
                    return classification
        
        return "Other"
    
    def add_usage(self, file_path: str, line_number: int):
        """Add a usage location for this class."""
        self.used_in[file_path].add(line_number)
    
    @property
    def usage_count(self) -> int:
        """Get the number of files where this class is used."""
        return len(self.used_in)
    
    @property
    def usage_locations(self) -> str:
        """Get a formatted string of all usage locations."""
        locations = []
        for file_path, lines in self.used_in.items():
            lines_str = ",".join(str(line) for line in sorted(lines))
            locations.append(f"{file_path}:{lines_str}")
        return "; ".join(locations)
    
    @property
    def inheritance_str(self) -> str:
        """Get a formatted string showing inheritance."""
        if not self.bases:
            return self.name
        return f"{self.name}({', '.join(self.bases)})"
    
    def to_dict(self) -> Dict:
        """Convert class info to a dictionary for CSV export."""
        return {
            "Class Name": self.inheritance_str,
            "Functionality": self.doc,
            "File Path": self.file_path,
            "Classification": self.classification,
            "Usage Count": self.usage_count,
            "Usage Locations": self.usage_locations
        }


class ModuleParser(ast.NodeVisitor):
    """Parse a Python module to find classes and imports."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.classes: List[ClassInfo] = []
        self.imports: Dict[str, str] = {}  # imported name -> original name
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract information about a class definition."""
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attribute_path(base)}")
        
        # Get docstring
        doc = ast.get_docstring(node) or ""
        
        # Create ClassInfo object
        class_info = ClassInfo(
            name=node.name,
            bases=bases,
            doc=doc,
            file_path=self.file_path,
            line_number=node.lineno
        )
        self.classes.append(class_info)
        
        # Continue parsing
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Handle simple imports: import X, import X as Y"""
        for name in node.names:
            if name.asname:
                self.imports[name.asname] = name.name
            else:
                self.imports[name.name] = name.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle from imports: from X import Y, from X import Y as Z"""
        if node.module is None:
            # Relative import without module like "from . import Y"
            module_prefix = ""
        else:
            module_prefix = f"{node.module}."
            
        for name in node.names:
            if name.asname:
                self.imports[name.asname] = f"{module_prefix}{name.name}"
            else:
                self.imports[name.name] = f"{module_prefix}{name.name}"
        self.generic_visit(node)
    
    def _get_attribute_path(self, node: ast.Attribute) -> str:
        """Get the full path of an attribute (e.g., module.Class)."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_path(node.value)}.{node.attr}"
        return node.attr


class UsageDetector(ast.NodeVisitor):
    """Detect class usages in Python code."""
    
    def __init__(self, file_path: str, classes_by_name: Dict[str, ClassInfo], 
                 module_parser: ModuleParser):
        self.file_path = file_path
        self.classes_by_name = classes_by_name
        self.module_parser = module_parser
    
    def visit_Name(self, node: ast.Name) -> None:
        """Check if a name is a usage of a class."""
        name = node.id
        
        # Check if this is a direct reference to a known class
        if name in self.classes_by_name:
            self.classes_by_name[name].add_usage(self.file_path, node.lineno)
        
        # Check if this is a reference to an imported class
        if name in self.module_parser.imports:
            imported_name = self.module_parser.imports[name]
            
            # Handle simple import like "import X" -> X is a module, not a class
            if '.' not in imported_name:
                return
            
            # Handle cases like "from module import Class"
            parts = imported_name.split('.')
            class_name = parts[-1]
            
            if class_name in self.classes_by_name:
                self.classes_by_name[class_name].add_usage(self.file_path, node.lineno)
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check for attribute-style class references (e.g., module.Class)."""
        if isinstance(node.value, ast.Name):
            module_name = node.value.id
            class_name = node.attr
            
            # Handle cases where a module is imported and its classes are accessed
            if module_name in self.module_parser.imports:
                imported_module = self.module_parser.imports[module_name]
                # If imported_module is actually a class, this isn't a class usage
                if imported_module in self.classes_by_name:
                    return
                
                # Check if the attribute matches a known class name
                if class_name in self.classes_by_name:
                    self.classes_by_name[class_name].add_usage(self.file_path, node.lineno)
        
        self.generic_visit(node)


def normalize_path(path: str) -> str:
    """Normalize a file path relative to old_codes directory."""
    rel_path = os.path.relpath(path, os.path.join(BASE_DIR, OLD_CODES_DIR))
    return rel_path


def parse_python_file(file_path: str) -> Optional[ModuleParser]:
    """Parse a Python file and extract class information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
            parser = ModuleParser(normalize_path(file_path))
            parser.visit(tree)
            return parser
        except SyntaxError:
            logger.error(f"Syntax error in {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return None


def find_python_files(directory: str) -> List[str]:
    """Recursively find all Python files in a directory."""
    python_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def analyze_classes():
    """Analyze all classes in the old_codes directory and generate CSV report."""
    old_codes_path = os.path.join(BASE_DIR, OLD_CODES_DIR)
    logger.info(f"Analyzing classes in: {old_codes_path}")
    
    if not os.path.exists(old_codes_path):
        logger.error(f"Directory not found: {old_codes_path}")
        return
    
    # Step 1: Find all Python files
    python_files = find_python_files(old_codes_path)
    logger.info(f"Found {len(python_files)} Python files")
    
    # Step 2: Parse all files to extract class information
    all_parsers = []
    all_classes: List[ClassInfo] = []
    classes_by_name: Dict[str, ClassInfo] = {}
    
    for file_path in python_files:
        parser = parse_python_file(file_path)
        if parser:
            all_parsers.append(parser)
            all_classes.extend(parser.classes)
            
            # Add classes to lookup dictionary
            for class_info in parser.classes:
                classes_by_name[class_info.name] = class_info
    
    logger.info(f"Extracted information for {len(all_classes)} classes")
    
    # Step 3: Detect class usages across all files
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            module_parser = next((p for p in all_parsers if normalize_path(file_path) == p.file_path), None)
            
            if module_parser:
                detector = UsageDetector(normalize_path(file_path), classes_by_name, module_parser)
                detector.visit(tree)
        except Exception as e:
            logger.error(f"Error analyzing usages in {file_path}: {e}")
    
    # Step 4: Save results to CSV
    csv_path = os.path.join(BASE_DIR, OUTPUT_CSV)
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                "Class Name", "Functionality", "File Path", 
                "Classification", "Usage Count", "Usage Locations"
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Sort classes by classification and then by name
            sorted_classes = sorted(all_classes, key=lambda c: (c.classification, c.name))
            
            for class_info in sorted_classes:
                writer.writerow(class_info.to_dict())
    
        logger.info(f"Analysis complete. Results saved to: {csv_path}")
    except Exception as e:
        logger.error(f"Error saving CSV file: {e}")


if __name__ == "__main__":
    analyze_classes()
