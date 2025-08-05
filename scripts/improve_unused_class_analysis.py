#!/usr/bin/env python3
"""
Script to verify the accuracy of the unused classes report and generate an improved analysis.
This addresses issues with false negatives (classes incorrectly marked as unused).
"""

import os
import csv
import re
from collections import defaultdict
import subprocess
from typing import Dict, List, Set, Tuple
from lg import logger

# Configuration
OLD_CODES_DIR = os.path.join('project_files', 'old_po_app_design', 'old_codes')
CSV_PATH = os.path.join('project_files', 'old_po_app_design', 'old_classes_analysis.csv')
REPORT_PATH = os.path.join('project_files', 'old_po_app_design', 'unused_classes_report.md')
CORRECTED_REPORT_PATH = os.path.join('project_files', 'old_po_app_design', 'corrected_unused_classes_report.md')
BASE_DIR = os.getcwd()  # Assumes script is run from project root

def read_csv_data() -> Dict:
    """Read class usage data from CSV file."""
    class_data = {}
    
    try:
        with open(os.path.join(BASE_DIR, CSV_PATH), 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract the base class name (without inheritance info)
                class_name = row['Class Name'].split('(')[0].strip()
                
                # Handle duplicate class names with different file paths
                key = f"{class_name}|{row['File Path']}"
                
                class_data[key] = {
                    'class_name': class_name,
                    'full_name': row['Class Name'],
                    'file_path': row['File Path'],
                    'classification': row['Classification'],
                    'usage_count': int(row['Usage Count']),
                    'usage_locations': row['Usage Locations'],
                    'functionality': row['Functionality']
                }
                
        logger.info(f"Loaded {len(class_data)} class entries from CSV")
        return class_data
        
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return {}

def verify_class_usage(class_data: Dict) -> Dict:
    """Verify class usage by searching the codebase for direct references."""
    verified_data = {}
    old_codes_path = os.path.join(BASE_DIR, OLD_CODES_DIR)
    
    for key, data in class_data.items():
        class_name = data['class_name']
        file_path = data['file_path']
        
        # Deep scan for class usage using grep
        try:
            cmd = f"grep -r --include='*.py' '{class_name}' {old_codes_path} | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            grep_count = int(result.stdout.strip())
            
            # Get actual usage examples using grep
            example_cmd = f"grep -r --include='*.py' '{class_name}' {old_codes_path} | head -5"
            example_result = subprocess.run(example_cmd, shell=True, capture_output=True, text=True)
            usage_examples = example_result.stdout.strip().split("\n")
            
            # Store verified data
            verified_data[key] = data.copy()
            verified_data[key]['grep_count'] = grep_count
            verified_data[key]['grep_examples'] = usage_examples
            verified_data[key]['is_actually_used'] = grep_count > 0
            
            # If there's a major discrepancy between CSV and grep
            if data['usage_count'] == 0 and grep_count > 3:
                logger.warning(f"Potential false negative: {class_name} in {file_path} - CSV: 0, Grep: {grep_count}")
                
        except Exception as e:
            logger.error(f"Error verifying {class_name}: {e}")
            
    return verified_data

def analyze_test_classes(verified_data: Dict) -> Dict:
    """Analyze which unused classes are test-only classes."""
    for key, data in verified_data.items():
        # Check if class is in a test file or has 'Test' in the name
        is_test = (
            'tests/' in data['file_path'] or
            data['class_name'].startswith('Test') or
            'Test' in data['class_name'] or
            'Mock' in data['class_name']
        )
        
        verified_data[key]['is_test'] = is_test
        
    return verified_data

def generate_corrected_report(verified_data: Dict):
    """Generate a corrected report based on verified usage data."""
    try:
        # Group the classes
        false_negatives = []
        true_unused = []
        test_only = []
        
        for key, data in verified_data.items():
            if data['usage_count'] == 0 and data['grep_count'] > 0:
                false_negatives.append(data)
            elif data['usage_count'] == 0 and data['is_test']:
                test_only.append(data)
            elif data['usage_count'] == 0:
                true_unused.append(data)
                
        # Sort each group by class name
        false_negatives.sort(key=lambda x: x['class_name'])
        true_unused.sort(key=lambda x: x['class_name'])
        test_only.sort(key=lambda x: x['class_name'])
        
        # Write the report
        with open(os.path.join(BASE_DIR, CORRECTED_REPORT_PATH), 'w', encoding='utf-8') as f:
            f.write("# Corrected Unused Classes Analysis Report\n\n")
            f.write("This report provides a more accurate analysis of unused classes in the codebase.\n\n")
            
            # False negatives section
            f.write("## False Negatives (Actually Used Classes)\n\n")
            f.write("These classes were incorrectly marked as unused but are actually referenced in the codebase:\n\n")
            
            f.write("| Class Name | Classification | File Path | CSV Count | Actual References | Sample Usage |\n")
            f.write("|------------|----------------|-----------|-----------|-------------------|-------------|\n")
            
            for data in false_negatives:
                sample = data['grep_examples'][0] if data['grep_examples'] else "N/A"
                sample = sample.replace("|", "\\|")  # Escape pipe characters in markdown table
                
                f.write(f"| {data['class_name']} | {data['classification']} | {data['file_path']} | {data['usage_count']} | {data['grep_count']} | {sample} |\n")
            
            # Test-only unused classes
            f.write("\n## Test-Only Unused Classes\n\n")
            f.write("These unused classes are part of the test framework and not intended for production use:\n\n")
            
            f.write("| Class Name | Classification | File Path | Functionality |\n")
            f.write("|------------|----------------|-----------|---------------|\n")
            
            for data in test_only:
                functionality = data['functionality'] or "No description"
                f.write(f"| {data['class_name']} | {data['classification']} | {data['file_path']} | {functionality} |\n")
            
            # Truly unused classes
            f.write("\n## Truly Unused Classes\n\n")
            f.write("These classes appear to be completely unused in the codebase:\n\n")
            
            f.write("| Class Name | Classification | File Path | Functionality |\n")
            f.write("|------------|----------------|-----------|---------------|\n")
            
            for data in true_unused:
                functionality = data['functionality'] or "No description"
                f.write(f"| {data['class_name']} | {data['classification']} | {data['file_path']} | {functionality} |\n")
            
            # Summary
            f.write("\n## Summary\n\n")
            f.write(f"- False negatives (incorrectly marked as unused): {len(false_negatives)}\n")
            f.write(f"- Test-only unused classes: {len(test_only)}\n")
            f.write(f"- Truly unused classes: {len(true_unused)}\n")
            f.write(f"- Total analyzed: {len(verified_data)}\n\n")
            
            # Analysis of the issue
            f.write("## Analysis of Previous Report Issues\n\n")
            f.write("The previous analysis contained inaccuracies due to:\n\n")
            f.write("1. **Import detection limitations**: Only counted direct import statements, missing class references in code\n")
            f.write("2. **String-based class usage**: Failed to detect when classes are referenced as strings\n")
            f.write("3. **Dynamic instantiation**: Missed classes instantiated through reflection or factory patterns\n")
            f.write("4. **Inheritance relationships**: Some classes are used as base classes without direct imports\n\n")
            
            f.write("This corrected report uses a more thorough grep-based analysis to find any textual reference to class names.\n")
            
        logger.info(f"Corrected report generated at {CORRECTED_REPORT_PATH}")
        
    except Exception as e:
        logger.error(f"Error generating corrected report: {e}")

def run_analysis():
    """Run the complete analysis workflow."""
    logger.info("Starting improved unused class analysis")
    
    # Read the original CSV data
    class_data = read_csv_data()
    
    # Verify actual class usage with grep
    verified_data = verify_class_usage(class_data)
    
    # Analyze test classes
    verified_data = analyze_test_classes(verified_data)
    
    # Generate corrected report
    generate_corrected_report(verified_data)
    
    logger.info("Analysis complete")


if __name__ == "__main__":
    run_analysis()
