import os
import ast
from collections import defaultdict, Counter
from pathlib import Path

# Define paths
BASE_DIR = os.getcwd()
OLD_CODES_DIR = os.path.join('project_files', 'old_po_app_design', 'old_codes')
CSV_PATH = os.path.join('project_files', 'old_po_app_design', 'old_classes_analysis.csv')
OUTPUT_PATH = os.path.join('project_files', 'old_po_app_design', 'class_usage_analysis.md')


EXCLUDE_KEYWORDS = ('test', 'mock')  # Exclude class names or file paths with these


def is_excluded(name):
    name_lower = name.lower()
    return any(kw in name_lower for kw in EXCLUDE_KEYWORDS)


class ClassInfoCollector(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        class_name = node.name
        if is_excluded(class_name):
            return
        bases = [base.id if isinstance(base, ast.Name) else ast.unparse(base) for base in node.bases]
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        docstring = ast.get_docstring(node)
        self.classes.append({
            'name': class_name,
            'bases': bases,
            'methods': methods,
            'docstring': docstring,
            'lineno': node.lineno
        })


def collect_classes_from_file(file_path):
    if is_excluded(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return []

    collector = ClassInfoCollector()
    collector.visit(tree)
    return collector.classes


def collect_references(class_names, search_dir):
    usage_counter = Counter()
    for root, _, files in os.walk(search_dir):
        for filename in files:
            if filename.endswith(".py") and not is_excluded(filename):
                path = os.path.join(root, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Could not read {path}: {e}")
                    continue
                for class_name in class_names:
                    usage_counter[class_name] += content.count(class_name)
    return usage_counter


def main():
    class_index = []
    class_names = []

    for root, _, files in os.walk(OLD_CODES_DIR):
        for file in files:
            if file.endswith(".py") and not is_excluded(file):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, OLD_CODES_DIR)
                classes = collect_classes_from_file(abs_path)

                for cls in classes:
                    cls_info = {
                        'name': cls['name'],
                        'bases': cls['bases'],
                        'methods': cls['methods'],
                        'docstring': cls['docstring'],
                        'path': rel_path
                    }
                    class_index.append(cls_info)
                    class_names.append(cls['name'])

    # Analyze usage
    usage_counts = collect_references(class_names, OLD_CODES_DIR)

    # Output Markdown Report
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write("# Class Usage Analysis\n\n")
        for cls in class_index:
            f.write(f"## {cls['name']}\n")
            f.write(f"**File Path**: `{cls['path']}`\n\n")
            f.write(f"**Inheritance**: {', '.join(cls['bases']) if cls['bases'] else 'None'}\n\n")
            if cls['docstring']:
                f.write(f"**Docstring**: {cls['docstring']}\n\n")
            f.write(f"**Methods**:\n")
            if cls['methods']:
                for method in cls['methods']:
                    f.write(f"- `{method}`\n")
            else:
                f.write("- None\n")
            f.write(f"\n**Referenced**: `{usage_counts[cls['name']]}` times in the project.\n\n")
            f.write("---\n\n")

        # Usage Table (sorted descending)
        f.write("## 🔢 Class Usage Count (Descending)\n\n")
        f.write("| Class Name | File Path | Times Referenced |\n")
        f.write("|------------|-----------|------------------|\n")
        for cls in sorted(class_index, key=lambda x: usage_counts[x['name']], reverse=True):
            f.write(f"| `{cls['name']}` | `{cls['path']}` | {usage_counts[cls['name']]} |\n")
        f.write("\n---\n")

        # Alphabetical Table
        f.write("## 🔤 Class Reference Table (Alphabetical)\n\n")
        f.write("| Class Name | File Path | Times Referenced |\n")
        f.write("|------------|-----------|------------------|\n")
        for cls in sorted(class_index, key=lambda x: x['name'].lower()):
            f.write(f"| `{cls['name']}` | `{cls['path']}` | {usage_counts[cls['name']]} |\n")

    print(f"✅ Markdown report generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
