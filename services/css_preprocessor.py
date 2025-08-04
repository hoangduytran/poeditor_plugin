import re
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from lg import logger

class CSSPreprocessor:
    """CSS Preprocessor for handling CSS variables in PySide6

    PySide6 doesn't support CSS custom properties (variables), so this preprocessor
    converts CSS with variables into standard CSS by replacing var(--variable) references
    with their actual values.
    """

    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)

        # Cache for processed CSS to improve performance
        self.cache: Dict[str, Any] = {}

        # Regular expressions for finding variables
        self.var_declaration_pattern = re.compile(r'--([\w-]+)\s*:\s*([^;]+);')
        self.var_usage_pattern = re.compile(r'var\(--([\w-]+)(?:,\s*([^)]+))?\)')

        logger.debug(f"CSS Preprocessor initialized with themes directory: {themes_dir}")

    def extract_variables(self, css_content: str) -> Dict[str, str]:
        """Extract CSS variables and their values from CSS content

        Args:
            css_content: CSS content as string

        Returns:
            Dictionary of variable names and their values
        """
        variables = {}

        # Find all variable declarations
        for match in self.var_declaration_pattern.finditer(css_content):
            var_name = match.group(1)
            var_value = match.group(2).strip()
            variables[var_name] = var_value

        return variables

    def parse_css_file(self, file_path: str) -> Dict[str, str]:
        """Parse CSS file to extract variables

        Args:
            file_path: Path to CSS file

        Returns:
            Dictionary of variable names and values
        """
        if not os.path.exists(file_path):
            logger.warning(f"CSS file not found: {file_path}")
            return {}

        # Check cache
        cache_key = f"file_vars:{file_path}"
        file_mtime = os.path.getmtime(file_path)

        if cache_key in self.cache and self.cache[cache_key]['mtime'] == file_mtime:
            return self.cache[cache_key]['variables']

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Extract variables
        variables = self.extract_variables(css_content)

        # Cache results
        self.cache[cache_key] = {
            'mtime': file_mtime,
            'variables': variables
        }

        return variables

    def process_css(self, css_content: str, variables: Dict[str, str]) -> str:
        """Process CSS content by replacing variable references with actual values

        Args:
            css_content: CSS content as string
            variables: Dictionary of variable names and values

        Returns:
            Processed CSS with variables replaced
        """
        # Cache key based on content hash and variables
        cache_key = f"process:{hash(css_content)}-{hash(str(variables))}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Function to replace variables in a match
        def replace_var(match):
            var_name = match.group(1)
            fallback = match.group(2)

            if var_name in variables:
                value = variables[var_name]

                # Check if value contains variable references
                if 'var(--' in value:
                    # Recursively resolve nested variables
                    value = self._resolve_nested_variables(value, variables)

                return value
            elif fallback:
                return fallback.strip()
            else:
                # Variable not found and no fallback
                logger.warning(f"Variable '--{var_name}' not found and no fallback provided")
                return 'initial'

        # Replace all variable references
        processed_css = self.var_usage_pattern.sub(replace_var, css_content)

        # Remove :root blocks and variable declarations for QSS compatibility
        processed_css = self._remove_css_variable_declarations(processed_css)

        # Cache the result
        self.cache[cache_key] = processed_css

        return processed_css

    def _resolve_nested_variables(self, value: str, variables: Dict[str, str], depth: int = 0) -> str:
        """Recursively resolve nested variable references

        Args:
            value: CSS value potentially containing variable references
            variables: Dictionary of variable names and values
            depth: Recursion depth to prevent infinite loops

        Returns:
            Value with all variable references resolved
        """
        # Prevent infinite recursion
        if depth > 10:
            logger.warning(f"Max recursion depth reached when resolving variables: {value}")
            return value

        # Replace all variable references in this value
        def replace_nested_var(match):
            nested_var_name = match.group(1)
            nested_fallback = match.group(2)

            if nested_var_name in variables:
                nested_value = variables[nested_var_name]

                # Check for nested variables in the replacement
                if 'var(--' in nested_value:
                    return self._resolve_nested_variables(nested_value, variables, depth + 1)
                return nested_value
            elif nested_fallback:
                return nested_fallback.strip()
            else:
                logger.warning(f"Nested variable '--{nested_var_name}' not found and no fallback provided")
                return 'initial'

        return self.var_usage_pattern.sub(replace_nested_var, value)

    def process_css_file(self, file_path: str, variables: Dict[str, str]) -> str:
        """Process a CSS file by replacing variable references with actual values

        Args:
            file_path: Path to CSS file
            variables: Dictionary of variable names and values

        Returns:
            Processed CSS content
        """
        if not os.path.exists(file_path):
            logger.warning(f"CSS file not found: {file_path}")
            return ""

        # Check cache
        file_mtime = os.path.getmtime(file_path)
        cache_key = f"file_process:{file_path}-{hash(str(variables))}-{file_mtime}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Process CSS content
        processed_css = self.process_css(css_content, variables)

        # Cache result
        self.cache[cache_key] = processed_css

        return processed_css

    def combine_css_files(self, file_paths: List[str], variables: Dict[str, str]) -> str:
        """Combine multiple CSS files into a single CSS string with variables replaced

        Args:
            file_paths: List of CSS file paths
            variables: Dictionary of variable names and values

        Returns:
            Combined and processed CSS content
        """
        combined_css = []

        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"CSS file not found: {file_path}")
                continue

            # Process file
            processed_css = self.process_css_file(file_path, variables)
            combined_css.append(f"/* Source: {os.path.basename(file_path)} */\n{processed_css}")

        return "\n\n".join(combined_css)

    def clear_cache(self):
        """Clear the preprocessor cache"""
        self.cache = {}
        logger.debug("Cleared CSS preprocessor cache")

    def generate_final_css(self, theme_name: str) -> str:
        """Generate final CSS for a theme by combining and processing all relevant files

        Args:
            theme_name: Name of the theme (e.g., 'light', 'dark')

        Returns:
            Final processed CSS for the theme
        """
        # Paths to CSS directories
        base_dir = self.themes_dir / "base"
        components_dir = self.themes_dir / "components"
        variants_dir = self.themes_dir / "variants"
        icons_dir = self.themes_dir / "icons"

        # Ensure directories exist
        base_dir.mkdir(exist_ok=True, parents=True)
        components_dir.mkdir(exist_ok=True, parents=True)
        variants_dir.mkdir(exist_ok=True, parents=True)
        icons_dir.mkdir(exist_ok=True, parents=True)

        # Paths to CSS files
        base_variables_path = base_dir / "variables.css"
        reset_path = base_dir / "reset.css"
        theme_path = variants_dir / f"{theme_name}.css"

        # Check if theme exists
        if not theme_path.exists():
            logger.error(f"Theme file not found: {theme_path}")
            return ""

        # Load variables
        variables = {}

        # 1. Base variables
        if base_variables_path.exists():
            base_variables = self.parse_css_file(str(base_variables_path))
            variables.update(base_variables)
            logger.debug(f"Loaded {len(base_variables)} base variables")

        # 2. Theme-specific variables
        theme_variables = self.parse_css_file(str(theme_path))
        variables.update(theme_variables)
        logger.debug(f"Loaded {len(theme_variables)} theme variables for '{theme_name}'")

        # Collect CSS files to process in order
        css_files = []

        # 1. Reset CSS
        if reset_path.exists():
            css_files.append(str(reset_path))

        # 2. Theme CSS
        css_files.append(str(theme_path))

        # 3. Component CSS files
        for component_file in sorted(components_dir.glob("*.css")):
            css_files.append(str(component_file))

        # 4. Icons CSS if exists
        icons_css_path = icons_dir / "icons.css"
        if icons_css_path.exists():
            css_files.append(str(icons_css_path))

        logger.debug(f"Processing {len(css_files)} CSS files for theme '{theme_name}'")

        # Combine and process all CSS files
        start_time = time.time()
        final_css = self.combine_css_files(css_files, variables)
        process_time = (time.time() - start_time) * 1000

        # Add theme information
        header = f"/* Generated CSS for theme: {theme_name} */\n"
        header += f"/* Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')} */\n"
        header += f"/* Processing time: {process_time:.2f} ms */\n\n"

        logger.info(f"Generated CSS for theme '{theme_name}' in {process_time:.2f} ms")

        return header + final_css

    def _remove_css_variable_declarations(self, css_content: str) -> str:
        """Remove CSS variable declarations and :root blocks for QSS compatibility

        Args:
            css_content: CSS content with variable declarations

        Returns:
            CSS content without variable declarations
        """
        # Remove :root blocks and their contents
        # This regex matches :root { ... } blocks including nested braces
        root_pattern = re.compile(r':root\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.MULTILINE | re.DOTALL)
        css_without_root = root_pattern.sub('', css_content)

        # Remove any remaining standalone variable declarations (--variable: value;)
        var_declaration_cleanup = re.compile(r'^\s*--[\w-]+\s*:[^;]+;\s*$', re.MULTILINE)
        css_clean = var_declaration_cleanup.sub('', css_without_root)

        # Clean up extra whitespace and empty lines
        css_clean = re.sub(r'\n\s*\n\s*\n', '\n\n', css_clean)  # Multiple empty lines to double
        css_clean = re.sub(r'^\s*\n', '', css_clean, flags=re.MULTILINE)  # Remove leading empty lines

        return css_clean.strip()
