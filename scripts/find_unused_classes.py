#!/usr/bin/env python3
"""
Script to identify classes that are declared but potentially unused in the codebase.
This script performs a comprehensive analysis of class usage by:
1. Finding direct imports of classes
2. Detecting class instantiation (ClassName() pattern)
3. Finding method calls and attribute access
4. Analyzing inheritance relationships
5. Examining string literals and reflection patterns
"""

import os
import re
import ast
import csv
import inspect
import importlib.util
import sys
import subprocess
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
from lg import logger

# Configuration
OLD_CODES_DIR = os.path.join('project_files', 'old_po_app_design', 'old_codes')
CSV_PATH = os.path.join('project_files', 'old_po_app_design', 'old_classes_analysis.csv')
OUTPUT_PATH = os.path.join('project_files', 'old_po_app_design', 'class_usage_analysis.md')
BASE_DIR = os.getcwd()  # Assumes script is run from project root

class ClassUsageInfo:
    """Store comprehensive information about class usage."""
    
    def __init__(self, name: str, full_name: str, file_path: str, classification: str, functionality: str):
        self.name = name  # Base class name without inheritance
        self.full_name = full_name  # Full class name with inheritance
        self.file_path = file_path
        self.classification = classification
        self.functionality = functionality
        
        # Usage tracking
        self.direct_imports: Dict[str, List[int]] = defaultdict(list)  # file -> line numbers
        self.instantiations: Dict[str, List[int]] = defaultdict(list)  # file -> line numbers
        self.method_calls: Dict[str, List[int]] = defaultdict(list)    # file -> line numbers
        self.string_refs: Dict[str, List[int]] = defaultdict(list)     # file -> line numbers
        self.class_refs: Dict[str, List[int]] = defaultdict(list)      # file -> line numbers
        self.inheritance_uses: Dict[str, List[int]] = defaultdict(list)  # file -> line numbers
        
    @property
    def total_usage_count(self) -> int:
        """Get total count of all usage types."""
        return (len(self.direct_imports) + 
                len(self.instantiations) + 
                len(self.method_calls) + 
                len(self.string_refs) + 
                len(self.class_refs) + 
                len(self.inheritance_uses))
                
    @property
    def usage_file_count(self) -> int:
        """Get unique files where the class is used."""
        all_files = set()
        for files_dict in [self.direct_imports, self.instantiations, self.method_calls, 
                           self.string_refs, self.class_refs, self.inheritance_uses]:
            all_files.update(files_dict.keys())
        return len(all_files)
        
    @property 
    def is_used(self) -> bool:
        """Determine if the class is used anywhere."""
        return self.total_usage_count > 0
        
    @property
    def usage_types(self) -> Dict[str, int]:
        """Count usage by type."""
        return {
            "imports": len(self.direct_imports),
            "instantiations": len(self.instantiations),
            "method_calls": len(self.method_calls),
            "string_refs": len(self.string_refs),
            "class_refs": len(self.class_refs),
            "inheritance": len(self.inheritance_uses)
        }
        
    def add_usage(self, usage_type: str, file_path: str, line_number: int):
        """Add a usage instance."""
        if usage_type == "import":
            self.direct_imports[file_path].append(line_number)
        elif usage_type == "instantiation":
            self.instantiations[file_path].append(line_number)
        elif usage_type == "method_call":
            self.method_calls[file_path].append(line_number)
        elif usage_type == "string_ref":
            self.string_refs[file_path].append(line_number)
        elif usage_type == "class_ref":
            self.class_refs[file_path].append(line_number)
        elif usage_type == "inheritance":
            self.inheritance_uses[file_path].append(line_number)
            
    def get_usage_summary(self) -> Dict:
        """Get summary of usage data."""
        return {
            "total": self.total_usage_count,
            "file_count": self.usage_file_count,
            "is_used": self.is_used,
            "types": self.usage_types
        }
        
    def get_detailed_locations(self) -> str:
        """Format detailed usage locations for reporting."""
        locations = []
        
        # Process each usage type
        for usage_type, usage_dict in [
            ("Import", self.direct_imports),
            ("Instantiation", self.instantiations),
            ("Method call", self.method_calls),
            ("String reference", self.string_refs),
            ("Class reference", self.class_refs),
            ("Inheritance", self.inheritance_uses)
        ]:
            if usage_dict:
                for file_path, lines in usage_dict.items():
                    locations.append(f"{usage_type} in {file_path}: lines {', '.join(map(str, sorted(lines)))}")
        
        return "; ".join(locations)


class EnhancedClassAnalyzer:
    """Enhanced analyzer for class usage with comprehensive detection."""
    
    def __init__(self, old_codes_path: str, csv_path: str):
        self.old_codes_path = old_codes_path
        self.csv_path = csv_path
        self.class_info: Dict[str, Dict] = {}  # Raw data from CSV
        self.class_usage: Dict[str, ClassUsageInfo] = {}  # Complete usage analysis
        self.python_files: List[str] = []
        self.class_definitions: Dict[str, List[Tuple[str, int]]] = defaultdict(list)  # class_name -> [(file, line)]
        self.inheritance_map: Dict[str, List[str]] = defaultdict(list)  # base -> [derived]
        self.ast_class_definitions = {}  # More accurate class definitions from AST parsing
    
    def load_csv_data(self):
        """Load class data from the CSV file."""
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Extract base class name (without inheritance)
                    class_name = row['Class Name'].split('(')[0].strip()
                    file_path = row['File Path']
                    
                    # Create a unique key for each class+file combination
                    key = f"{class_name}|{file_path}"
                    
                    self.class_info[key] = {
                        'name': class_name,
                        'full_name': row['Class Name'],
                        'functionality': row['Functionality'],
                        'file_path': file_path,
                        'classification': row['Classification'],
                        'csv_usage_count': int(row['Usage Count']),
                        'csv_usage_locations': row['Usage Locations']
                    }
                    
                    # Create usage info object
                    self.class_usage[key] = ClassUsageInfo(
                        name=class_name,
                        full_name=row['Class Name'],
                        file_path=file_path,
                        classification=row['Classification'],
                        functionality=row['Functionality']
                    )
                    
                    # Extract inheritance relationships
                    if '(' in row['Class Name']:
                        full_name = row['Class Name']
                        base_classes = full_name[full_name.find('(')+1:full_name.find(')')].split(', ')
                        for base in base_classes:
                            self.inheritance_map[base].append(key)
                    
            logger.info(f"Loaded {len(self.class_info)} class entries from CSV")
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            
    def find_python_files(self):
        """Find all Python files in the old_codes directory."""
        self.python_files = []
        
        for root, _, files in os.walk(self.old_codes_path):
            for file in files:
                if file.endswith('.py'):
                    self.python_files.append(os.path.join(root, file))
                    
        logger.info(f"Found {len(self.python_files)} Python files to analyze")
        
    def locate_class_definitions(self):
        """Find where classes are defined in the codebase using AST parsing."""
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use AST to parse Python code accurately
                try:
                    tree = ast.parse(content)
                    file_rel_path = os.path.relpath(file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
                    
                    # Create an AST visitor to find class definitions
                    class ClassVisitor(ast.NodeVisitor):
                        def __init__(self):
                            self.classes = []
                            
                        def visit_ClassDef(self, node):
                            # Get class name and base classes
                            class_name = node.name
                            base_classes = [base.id if isinstance(base, ast.Name) else self._get_attribute_name(base) 
                                           for base in node.bases if isinstance(base, (ast.Name, ast.Attribute))]
                            
                            # Get docstring if available
                            doc = ast.get_docstring(node) or ""
                            
                            # Record class info with location
                            self.classes.append({
                                'name': class_name,
                                'bases': base_classes,
                                'lineno': node.lineno,
                                'doc': doc
                            })
                            
                            # Continue traversing the AST
                            self.generic_visit(node)
                            
                        def _get_attribute_name(self, node):
                            """Get full name for attribute nodes like module.Class."""
                            if isinstance(node, ast.Attribute):
                                if isinstance(node.value, ast.Name):
                                    return f"{node.value.id}.{node.attr}"
                                elif isinstance(node.value, ast.Attribute):
                                    return f"{self._get_attribute_name(node.value)}.{node.attr}"
                            return "UnknownBase"
                    
                    # Apply the visitor
                    visitor = ClassVisitor()
                    visitor.visit(tree)
                    
                    # Record class definitions
                    for class_info in visitor.classes:
                        class_name = class_info['name']
                        self.class_definitions[class_name].append((file_rel_path, class_info['lineno']))
                        
                        # Store more detailed info in ast_class_definitions
                        key = f"{class_name}|{file_rel_path}"
                        self.ast_class_definitions[key] = {
                            'name': class_name,
                            'bases': class_info['bases'],
                            'file': file_rel_path,
                            'line': class_info['lineno'],
                            'doc': class_info['doc']
                        }
                        
                        # Update inheritance map from AST parsing
                        for base in class_info['bases']:
                            self.inheritance_map[base].append(key)
                    
                except SyntaxError:
                    # If AST parsing fails, fall back to regex approach
                    logger.warning(f"AST parsing failed for {file_path}, falling back to regex")
                    
                    # Use more accurate regex to find class definitions
                    # This pattern looks for:
                    # 1. "class" keyword at the beginning of a line or after whitespace
                    # 2. Followed by a valid Python identifier
                    # 3. Optional inheritance in parentheses
                    # 4. Ending with a colon
                    # 5. Avoiding matches in comments (lines starting with #)
                    class_pattern = r'(?<![#"\'])(?:^|\s)class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*:'
                    
                    # Process the file line by line to handle comments properly
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        # Skip comment lines
                        if line.strip().startswith('#'):
                            continue
                        
                        # Find class definitions in this line
                        for match in re.finditer(class_pattern, line):
                            class_name = match.group(1)
                            line_num = i + 1  # Line numbers are 1-based
                            rel_path = os.path.relpath(file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
                            self.class_definitions[class_name].append((rel_path, line_num))
                        
            except Exception as e:
                logger.error(f"Error scanning file {file_path} for class definitions: {e}")
                
        logger.info(f"Located definitions for {len(self.class_definitions)} unique class names")
    
    def analyze_all_class_usage(self):
        """Analyze usage of all classes across the codebase using AST parsing."""
        logger.info("Starting comprehensive class usage analysis")
        
        # For each file, find all usages with AST
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                rel_path = os.path.relpath(file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
                
                # Try to parse the file with AST
                try:
                    tree = ast.parse(content)
                    
                    # Create a visitor to find class references
                    class ReferenceVisitor(ast.NodeVisitor):
                        def __init__(self, analyzer, rel_path):
                            self.analyzer = analyzer
                            self.rel_path = rel_path
                            self.imported_names = {}  # Track imports for resolution
                        
                        def visit_Import(self, node):
                            """Handle regular imports: import module, import module as alias."""
                            for name in node.names:
                                if name.asname:
                                    self.imported_names[name.asname] = name.name
                                else:
                                    self.imported_names[name.name] = name.name
                            self.generic_visit(node)
                            
                        def visit_ImportFrom(self, node):
                            """Handle from imports: from module import name, from module import name as alias."""
                            module = node.module or ""
                            for name in node.names:
                                if name.asname:
                                    self.imported_names[name.asname] = f"{module}.{name.name}"
                                else:
                                    self.imported_names[name.name] = f"{module}.{name.name}"
                            self.generic_visit(node)
                        
                        def visit_ClassDef(self, node):
                            """Record inheritance relationships."""
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    base_name = base.id
                                    self._check_class_usage(base_name, node.lineno, "inheritance")
                            self.generic_visit(node)
                            
                        def visit_Call(self, node):
                            """Find class instantiations: ClassName()."""
                            if isinstance(node.func, ast.Name):
                                class_name = node.func.id
                                self._check_class_usage(class_name, node.lineno, "instantiation")
                            self.generic_visit(node)
                        
                        def visit_Name(self, node):
                            """Find direct references to class names."""
                            self._check_class_usage(node.id, node.lineno, "class_ref")
                            self.generic_visit(node)
                            
                        def visit_Attribute(self, node):
                            """Find attribute access that might be class methods."""
                            if isinstance(node.value, ast.Name):
                                # This could be Class.method
                                class_name = node.value.id
                                self._check_class_usage(class_name, node.lineno, "class_ref")
                            self.generic_visit(node)
                        
                        def _check_class_usage(self, name, lineno, usage_type):
                            """Check if the name refers to a known class and record its usage."""
                            # Check direct class name matches
                            for class_key, class_data in self.analyzer.class_usage.items():
                                if class_data.name == name:
                                    class_data.add_usage(usage_type, self.rel_path, lineno)
                                
                            # Check imported class names
                            if name in self.imported_names:
                                imported_name = self.imported_names[name]
                                for class_key, class_data in self.analyzer.class_usage.items():
                                    if imported_name.endswith(f".{class_data.name}"):
                                        class_data.add_usage("import", self.rel_path, lineno)
                    
                    # Apply the visitor
                    visitor = ReferenceVisitor(self, rel_path)
                    visitor.visit(tree)
                    
                except SyntaxError:
                    # Fall back to regex approach if AST parsing fails
                    logger.warning(f"AST parsing failed for {file_path}, falling back to regex for usage analysis")
                    
                    # For each class, find usages with regex
                    for class_key, class_data in self.class_usage.items():
                        class_name = class_data.name
                        
                        # Skip analyzing the file where the class is defined (to avoid self-reference)
                        is_definition_file = any(rel_path == def_file 
                                                for def_file, _ in self.class_definitions.get(class_name, []))
                        if is_definition_file:
                            continue
                        
                        # 1. Find direct imports - from X import ClassName or import X.ClassName
                        import_pattern = fr'(from\s+\w+(\.\w+)*\s+import\s+(.*\s*,\s*)?{class_name}|import\s+\w+(\.\w+)*\.{class_name})'
                        for match in re.finditer(import_pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            class_data.add_usage("import", rel_path, line_num)
                            
                        # 2. Find class instantiations - ClassName()
                        instantiation_pattern = fr'\b{re.escape(class_name)}\s*\('
                        for match in re.finditer(instantiation_pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            class_data.add_usage("instantiation", rel_path, line_num)
                            
                        # 3. Find method calls or attribute access - obj.method() or isinstance(x, ClassName)
                        reference_patterns = [
                            fr'isinstance\s*\([^,]+,\s*{re.escape(class_name)}\s*\)',  # isinstance check
                            fr'issubclass\s*\([^,]+,\s*{re.escape(class_name)}\s*\)',  # issubclass check
                            fr'\b{re.escape(class_name)}\.[\w_]+',  # static method/attribute
                            fr'\[\s*{re.escape(class_name)}\s*\]',  # dictionary key
                            fr':\s*{re.escape(class_name)}\b'       # type annotation
                        ]
                        
                        for pattern in reference_patterns:
                            for match in re.finditer(pattern, content):
                                line_num = content[:match.start()].count('\n') + 1
                                class_data.add_usage("class_ref", rel_path, line_num)
                            
                        # 4. String literals with class name
                        string_pattern = fr'[\'\"]{re.escape(class_name)}[\'\"]'
                        for match in re.finditer(string_pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            class_data.add_usage("string_ref", rel_path, line_num)
                    
            except Exception as e:
                logger.error(f"Error analyzing class usage in {file_path}: {e}")
        
        # Also analyze inheritance relationships
        self.analyze_inheritance_usage()
        
        logger.info("Completed class usage analysis")
    
    def validate_code_compilation(self):
        """Validate Python files using py_compile to detect syntax errors."""
        logger.info("Validating Python files with py_compile")
        
        import py_compile
        
        compilation_errors = []
        for file_path in self.python_files:
            try:
                py_compile.compile(file_path, doraise=True)
            except py_compile.PyCompileError as e:
                compilation_errors.append((file_path, str(e)))
                logger.warning(f"Compilation error in {file_path}: {e}")
        
        if compilation_errors:
            logger.warning(f"Found {len(compilation_errors)} files with compilation errors")
        else:
            logger.info("All files compile successfully")
        
        return compilation_errors
    
    def analyze_inheritance_usage(self):
        """Analyze inheritance relationships between classes."""
        for base_class, derived_class_keys in self.inheritance_map.items():
            # Find all potential keys for this base class (may appear in different files)
            base_keys = [key for key in self.class_usage.keys() 
                        if self.class_usage[key].name == base_class]
            
            if not base_keys:
                continue
                
            # For each derived class, mark that it uses the base class
            for derived_key in derived_class_keys:
                if derived_key in self.class_usage:
                    derived_data = self.class_usage[derived_key]
                    derived_file = derived_data.file_path
                    
                    # Add inheritance usage for each base class
                    for base_key in base_keys:
                        if base_key in self.class_usage:
                            self.class_usage[base_key].add_usage("inheritance", derived_file, 0)
                            
    def grep_direct_references(self):
        """Use grep for a secondary validation of class references."""
        logger.info("Using grep to validate class references")
        
        for class_key, class_data in self.class_usage.items():
            class_name = class_data.name
            
            try:
                # Use grep to find any mention of the class name
                cmd = f"grep -r --include='*.py' '\\b{class_name}\\b' {self.old_codes_path} | wc -l"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                grep_count = int(result.stdout.strip())
                
                # If grep found more references than our analysis
                if grep_count > class_data.total_usage_count and class_data.total_usage_count == 0:
                    logger.warning(f"Possible missed references for {class_name}: grep found {grep_count}, analysis found {class_data.total_usage_count}")
                    
                    # Get examples of the references
                    example_cmd = f"grep -r --include='*.py' '\\b{class_name}\\b' {self.old_codes_path} | head -3"
                    example_result = subprocess.run(example_cmd, shell=True, capture_output=True, text=True)
                    examples = example_result.stdout.strip().split('\n')
                    
                    for example in examples:
                        if example:
                            parts = example.split(':', 1)
                            if len(parts) >= 2:
                                file_path = os.path.relpath(parts[0], os.path.join(BASE_DIR, OLD_CODES_DIR))
                                # Add as a class reference since we don't know the exact usage type
                                class_data.add_usage("class_ref", file_path, 0)
                
            except Exception as e:
                logger.error(f"Error during grep validation for {class_name}: {e}")
                
    def categorize_classes(self):
        """Categorize classes based on usage analysis."""
        # Initialize counters
        stats = {
            "unused": 0,
            "used": 0,
            "low_usage": 0,  # 1-2 references
            "medium_usage": 0,  # 3-10 references
            "high_usage": 0,  # >10 references
        }
        
        # Count by category
        for class_key, class_data in self.class_usage.items():
            if not class_data.is_used:
                stats["unused"] += 1
            else:
                stats["used"] += 1
                
                total = class_data.total_usage_count
                if total <= 2:
                    stats["low_usage"] += 1
                elif 3 <= total <= 10:
                    stats["medium_usage"] += 1
                else:
                    stats["high_usage"] += 1
                    
        return stats
        
    def generate_report(self, output_path: str):
        """Generate a comprehensive class usage report."""
        try:
            stats = self.categorize_classes()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Class Usage Analysis Report\n\n")
                f.write("This report analyzes how classes are used throughout the codebase.\n\n")
                
                # Overall statistics
                f.write("## Overall Statistics\n\n")
                f.write(f"- **Total Classes**: {len(self.class_usage)}\n")
                f.write(f"- **Used Classes**: {stats['used']}\n")
                f.write(f"- **Unused Classes**: {stats['unused']}\n")
                f.write(f"- **Low Usage (1-2 references)**: {stats['low_usage']}\n")
                f.write(f"- **Medium Usage (3-10 references)**: {stats['medium_usage']}\n")
                f.write(f"- **High Usage (>10 references)**: {stats['high_usage']}\n\n")
                
                # Most heavily used classes
                f.write("## Most Used Classes\n\n")
                f.write("| Class Name | File Path | Classification | Total References | Files Using | Usage Types |\n")
                f.write("|------------|-----------|----------------|-----------------|------------|------------|\n")
                
                # Get most used classes
                most_used = sorted(
                    self.class_usage.items(), 
                    key=lambda x: x[1].total_usage_count, 
                    reverse=True
                )[:25]  # Top 25
                
                for class_key, class_data in most_used:
                    if class_data.total_usage_count > 0:
                        usage_types = ", ".join([
                            f"{name}: {count}" 
                            for name, count in class_data.usage_types.items() 
                            if count > 0
                        ])
                        
                        f.write(f"| {class_data.name} | {class_data.file_path} | " +
                               f"{class_data.classification} | {class_data.total_usage_count} | " +
                               f"{class_data.usage_file_count} | {usage_types} |\n")
                
                # Unused classes
                f.write("\n## Unused Classes\n\n")
                f.write("These classes appear to be completely unused in the codebase:\n\n")
                
                f.write("| Class Name | File Path | Classification | Functionality |\n")
                f.write("|------------|-----------|----------------|---------------|\n")
                
                unused = [data for data in self.class_usage.values() if not data.is_used]
                for class_data in sorted(unused, key=lambda x: x.name):
                    functionality = class_data.functionality or "No description"
                    f.write(f"| {class_data.name} | {class_data.file_path} | " +
                           f"{class_data.classification} | {functionality} |\n")
                
                # Classes with usage discrepancies
                f.write("\n## Usage Analysis Discrepancies\n\n")
                f.write("These classes have significant differences between CSV-reported usage and detected usage:\n\n")
                
                f.write("| Class Name | File Path | CSV Count | Detected Count | Difference |\n")
                f.write("|------------|-----------|-----------|----------------|------------|\n")
                
                for class_key, class_data in self.class_usage.items():
                    csv_count = self.class_info[class_key]['csv_usage_count']
                    detected_count = class_data.total_usage_count
                    difference = abs(detected_count - csv_count)
                    
                    # Report significant differences (>5)
                    if difference > 5:
                        f.write(f"| {class_data.name} | {class_data.file_path} | " +
                               f"{csv_count} | {detected_count} | {difference} |\n")
                
                # Recommendations
                f.write("\n## Recommendations\n\n")
                f.write("1. **Unused Classes**: Consider removing or documenting the purpose of unused classes.\n")
                f.write("2. **Test Classes**: Move test-specific classes to dedicated test utilities.\n")
                f.write("3. **Usage Discrepancies**: Investigate classes with large discrepancies between reported and actual usage.\n")
                f.write("4. **High-Usage Classes**: Ensure high-usage classes have thorough documentation and tests.\n")
                
            logger.info(f"Generated comprehensive usage report at {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            
    def generate_csv_data(self):
        """Generate CSV data by scanning Python files, finding class definitions, and analyzing usage."""
        logger.info("Generating initial CSV data from codebase...")
        
        # First pass: find all class definitions
        class_definitions = {}  # name -> [(file_path, lineno, bases, doc)]
        file_contents = {}      # file_path -> content
        file_ast_trees = {}     # file_path -> parsed AST
        
        # Scan files and find all class definitions first
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                file_contents[file_path] = content
                rel_path = os.path.relpath(file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
                
                try:
                    tree = ast.parse(content)
                    file_ast_trees[file_path] = tree
                    
                    # Find all class definitions in this file
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            
                            # Get inheritance information
                            bases = []
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    bases.append(base.id)
                                elif isinstance(base, ast.Attribute):
                                    # Handle module.Class style inheritance
                                    if isinstance(base.value, ast.Name):
                                        bases.append(f"{base.value.id}.{base.attr}")
                                    else:
                                        bases.append(base.attr)
                            
                            # Get docstring for functionality
                            doc = ast.get_docstring(node) or "No description"
                            doc = doc.split('\n')[0]  # First line only
                            
                            # Store class definition
                            if class_name not in class_definitions:
                                class_definitions[class_name] = []
                            class_definitions[class_name].append((rel_path, node.lineno, bases, doc))
                
                except SyntaxError:
                    logger.warning(f"Syntax error in {file_path}, using regex fallback")
                    
                    # Use regex fallback for syntax error files
                    class_pattern = r'class\s+([A-Za-z0-9_]+)(?:\s*\(([^)]*)\))?:'
                    for match in re.finditer(class_pattern, content):
                        class_name = match.group(1)
                        bases_str = match.group(2) or ""
                        bases = [b.strip() for b in bases_str.split(',') if b.strip()]
                        
                        # Approximate line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        if class_name not in class_definitions:
                            class_definitions[class_name] = []
                        class_definitions[class_name].append((rel_path, line_num, bases, "No description"))
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Found {len(class_definitions)} unique class names in codebase")
        
        # Second pass: analyze usage of each class
        class_usage_counts = defaultdict(int)      # (class_name, file_path) -> count
        class_usage_locations = defaultdict(list)  # (class_name, file_path) -> [(file, line), ...]
        
        for src_file_path, content in file_contents.items():
            src_rel_path = os.path.relpath(src_file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
            
            # For each class, check if it's used in this file
            for class_name, definitions in class_definitions.items():
                # Skip self-references (usage in the same file as definition)
                if any(def_path == src_rel_path for def_path, _, _, _ in definitions):
                    continue
                
                # Look for all occurrences of the class name in this file
                class_pattern = rf'\b{re.escape(class_name)}\b'
                matches = list(re.finditer(class_pattern, content))
                
                if matches:
                    # Check each match to exclude comments and strings
                    valid_matches = []
                    lines = content.split('\n')
                    
                    for match in matches:
                        pos = match.start()
                        line_idx = content[:pos].count('\n')
                        line = lines[line_idx] if line_idx < len(lines) else ""
                        
                        # Skip matches in comments
                        if '#' in line and pos > line.find('#'):
                            continue
                            
                        # Skip string literals (simplistic check)
                        if (line.count('"', 0, pos) % 2 == 1) or (line.count("'", 0, pos) % 2 == 1):
                            continue
                            
                        valid_matches.append((line_idx + 1, line.strip()))
                    
                    # If we have valid matches, record them
                    if valid_matches:
                        for def_path, _, _, _ in definitions:
                            key = (class_name, def_path)
                            class_usage_counts[key] += len(valid_matches)
                            class_usage_locations[key].append((src_rel_path, [line_num for line_num, _ in valid_matches]))
        
        # Also perform AST-based analysis for more accurate usage detection
        self._perform_ast_based_analysis(class_definitions, file_ast_trees, class_usage_counts, class_usage_locations)
        
        # Prepare CSV data with usage information
        csv_data = []
        for class_name, definitions in class_definitions.items():
            for file_path, lineno, bases, doc in definitions:
                # Format full class name with inheritance
                full_name = class_name
                if bases:
                    full_name = f"{class_name}({', '.join(bases)})"
                
                # Get usage count and locations
                key = (class_name, file_path)
                usage_count = class_usage_counts[key]
                
                # Format usage locations
                usage_locations = ""
                if key in class_usage_locations:
                    locations = []
                    for usage_file, lines in class_usage_locations[key]:
                        locations.append(f"{usage_file}:{','.join(map(str, lines))}")
                    usage_locations = "; ".join(locations)
                
                # Guess classification based on name/path
                classification = self._guess_classification(class_name, file_path, bases)
                
                # Add to CSV data
                csv_data.append({
                    "Class Name": full_name,
                    "Functionality": doc,
                    "File Path": file_path,
                    "Classification": classification,
                    "Usage Count": usage_count,
                    "Usage Locations": usage_locations
                })
        
        # Write to CSV
        if csv_data:
            try:
                with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["Class Name", "Functionality", "File Path", 
                                "Classification", "Usage Count", "Usage Locations"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in csv_data:
                        writer.writerow(row)
                
                logger.info(f"Successfully generated CSV with {len(csv_data)} classes at {self.csv_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to write CSV: {e}")
                return False
        else:
            logger.error("No class data found to write to CSV")
            return False
            
    def _perform_ast_based_analysis(self, class_definitions, file_ast_trees, class_usage_counts, class_usage_locations):
        """Perform AST-based analysis for more accurate usage detection."""
        logger.info("Performing AST-based usage analysis")
        
        # Dictionary to track imported names
        imported_classes = {}  # (file_path, imported_name) -> original_class_name
        
        # First pass: gather all import information
        for file_path, tree in file_ast_trees.items():
            rel_path = os.path.relpath(file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
            imported_classes[rel_path] = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.asname:
                            imported_classes[rel_path][name.asname] = name.name
                        else:
                            imported_classes[rel_path][name.name] = name.name
                            
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        if name.asname:
                            imported_classes[rel_path][name.asname] = f"{module}.{name.name}"
                        else:
                            imported_classes[rel_path][name.name] = f"{module}.{name.name}"
        
        # Second pass: analyze usage based on AST
        for file_path, tree in file_ast_trees.items():
            rel_path = os.path.relpath(file_path, os.path.join(BASE_DIR, OLD_CODES_DIR))
            
            # Skip files that couldn't be parsed
            if tree is None:
                continue
                
            for node in ast.walk(tree):
                # Check for direct class references (Name nodes)
                if isinstance(node, ast.Name) and node.id in class_definitions:
                    class_name = node.id
                    
                    # Skip references inside the class definition itself
                    is_self_ref = False
                    for def_path, def_line, _, _ in class_definitions[class_name]:
                        if def_path == rel_path and abs(def_line - node.lineno) < 50:  # Approximate class size
                            is_self_ref = True
                            break
                            
                    if not is_self_ref:
                        for def_path, _, _, _ in class_definitions[class_name]:
                            key = (class_name, def_path)
                            class_usage_counts[key] += 1
                            class_usage_locations[key].append((rel_path, [node.lineno]))
                
                # Check for class instantiations (Call nodes)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in class_definitions:
                    class_name = node.func.id
                    
                    for def_path, _, _, _ in class_definitions[class_name]:
                        key = (class_name, def_path)
                        class_usage_counts[key] += 1
                        class_usage_locations[key].append((rel_path, [node.lineno]))
                        
                # Check for class inheritance (ClassDef bases)
                elif isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in class_definitions:
                            class_name = base.id
                            
                            for def_path, _, _, _ in class_definitions[class_name]:
                                key = (class_name, def_path)
                                class_usage_counts[key] += 1
                                class_usage_locations[key].append((rel_path, [node.lineno]))
    
    def _guess_classification(self, class_name: str, file_path: str, bases: list = None) -> str:
        """Guess classification based on class name, file path, and base classes."""
        bases = bases or []
        
        # Check base classes first
        if any(base.endswith('QMainWindow') or 'QMainWindow' in base for base in bases):
            return "GUI Component"
        if any(base.endswith('QWidget') or 'QWidget' in base for base in bases):
            return "GUI Component"
        if any(base.endswith('QDialog') or 'QDialog' in base for base in bases):
            return "GUI Component"
        if any(base.endswith('QFrame') or 'QFrame' in base for base in bases):
            return "GUI Component"
        if any(base.endswith('QAbstractTableModel') or 'TableModel' in base for base in bases):
            return "Data Model"
        if any(base.endswith('Enum') or base == 'Enum' for base in bases):
            return "Enum/Constant"
        if any(base.endswith('QObject') for base in bases):
            return "Service"
            
        # GUI Components
        if any(term in class_name for term in ["Widget", "Dialog", "Window", "Frame", "Panel", "View"]):
            return "GUI Component"
        
        # Data Models
        if any(term in class_name for term in ["Model", "Table", "Record", "Entry"]):
            return "Data Model"
        
        # Services/Managers
        if any(term in class_name for term in ["Service", "Manager", "Handler", "Provider"]):
            return "Service"
            
        # Enumerations
        if "Enum" in class_name or class_name.endswith('Mode') or class_name.endswith('Type'):
            return "Enum/Constant"
            
        # Utilities
        if any(term in class_name for term in ["Utils", "Helper", "Utility"]):
            return "Utility"
            
        # Default
        return "Other"
    
    def run_analysis(self):
        """Run the complete analysis workflow."""
        # Add diagnostic info for paths
        logger.info(f"BASE_DIR: {BASE_DIR}")
        logger.info(f"OLD_CODES_DIR path: {self.old_codes_path}")
        logger.info(f"CSV_PATH: {self.csv_path}")
        logger.info(f"OUTPUT_PATH: {os.path.join(BASE_DIR, OUTPUT_PATH)}")
        
        # First find all Python files in the codebase
        self.find_python_files()
        logger.info(f"Located {len(self.python_files)} Python files for analysis")
        
        # Exit if no Python files found
        if not self.python_files:
            logger.error(f"No Python files found in {self.old_codes_path}. Check path configuration.")
            return
        
        # Print a few sample file paths for verification
        if self.python_files:
            sample_files = self.python_files[:3]
            logger.info(f"Sample Python files: {sample_files}")
        
        # Generate or regenerate CSV file with proper usage analysis
        logger.info("Regenerating CSV file with class usage analysis...")
        if not self.generate_csv_data():
            logger.error("Failed to generate CSV data. Analysis cannot continue.")
            return
            
        # Locate all class definitions to build a comprehensive class inventory
        self.locate_class_definitions()
        logger.info(f"Discovered {len(self.class_definitions)} class definitions in code")
        
        # Load CSV data for comparison with discovered classes
        self.load_csv_data()
        logger.info(f"Loaded {len(self.class_info)} classes from CSV for reference")
        
        # Exit if no classes loaded from CSV
        if not self.class_info:
            logger.error("No classes loaded from CSV. Check CSV file format and content.")
            return
        
        # Analyze actual usage of all classes across files
        self.analyze_all_class_usage()
        
        # Use grep as a secondary validation method
        self.grep_direct_references()
        
        # Generate the final report with all findings
        try:
            self.generate_report(os.path.join(BASE_DIR, OUTPUT_PATH))
            logger.info(f"Report written to {os.path.join(BASE_DIR, OUTPUT_PATH)}")
            
            # Verify report file exists and has content
            report_path = os.path.join(BASE_DIR, OUTPUT_PATH)
            if os.path.exists(report_path):
                file_size = os.path.getsize(report_path)
                logger.info(f"Report file size: {file_size} bytes")
                if file_size == 0:
                    logger.error("Report file exists but is empty!")
            else:
                logger.error("Failed to create report file!")
        except Exception as e:
            logger.error(f"Error generating report: {e}")
