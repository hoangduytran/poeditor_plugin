#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSS Development Tools

Provides development utilities for working with the CSS theming system:
- Watch CSS files for changes and rebuild themes
- Preview themes
- Extract CSS variables
- Generate theme CSS
"""

import sys
import os
from pathlib import Path
import time
import argparse
import json
from typing import Dict, List, Optional, Any
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Style

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.css_preprocessor import CSSPreprocessor
from services.icon_preprocessor import IconPreprocessor

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class CSSDevTools:
    """CSS Development Tools for theming system"""

    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.preprocessor = CSSPreprocessor(themes_dir)
        self.icon_preprocessor = IconPreprocessor("icons")

        # Ensure theme directories exist
        self._ensure_directories()

        logger.info(f"CSS Development Tools initialized with themes directory: {themes_dir}")

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        (self.themes_dir / "base").mkdir(exist_ok=True, parents=True)
        (self.themes_dir / "components").mkdir(exist_ok=True, parents=True)
        (self.themes_dir / "variants").mkdir(exist_ok=True, parents=True)
        (self.themes_dir / "icons" / "svg").mkdir(exist_ok=True, parents=True)

    def get_theme_list(self) -> List[str]:
        """Get list of available themes

        Returns:
            List of theme names
        """
        themes = []
        variants_dir = self.themes_dir / "variants"

        if variants_dir.exists():
            for theme_file in variants_dir.glob("*.css"):
                theme_name = theme_file.stem
                themes.append(theme_name)

        return sorted(themes)

    def watch_css_files(self, callback=None):
        """Watch CSS files for changes and rebuild themes

        Args:
            callback: Optional callback function to call when CSS is rebuilt
        """
        class CSSChangeHandler(FileSystemEventHandler):
            def __init__(self, dev_tools, callback):
                self.dev_tools = dev_tools
                self.callback = callback
                self.last_rebuilt = 0
                self.rebuild_delay = 0.5  # Seconds

            def on_modified(self, event):
                if not event.is_directory and str(event.src_path).endswith(".css"):
                    # Throttle rebuilds
                    current_time = time.time()
                    if current_time - self.last_rebuilt > self.rebuild_delay:
                        self.last_rebuilt = current_time
                        logger.info(f"CSS file changed: {event.src_path}")
                        self.dev_tools.rebuild_all_themes()

                        if self.callback:
                            self.callback()

        event_handler = CSSChangeHandler(self, callback)
        observer = Observer()
        observer.schedule(event_handler, str(self.themes_dir), recursive=True)
        observer.start()

        try:
            logger.info(f"{Fore.GREEN}Watching CSS files for changes in {self.themes_dir}")
            logger.info(f"{Fore.YELLOW}Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def rebuild_all_themes(self):
        """Rebuild all themes"""
        themes = self.get_theme_list()

        if not themes:
            logger.warning(f"No themes found in {self.themes_dir}/variants")
            return

        logger.info(f"Rebuilding {len(themes)} themes...")

        # Clear caches
        self.preprocessor.clear_cache()

        # Rebuild each theme
        for theme in themes:
            output_path = self.themes_dir / "generated" / f"{theme}.css"
            output_path.parent.mkdir(exist_ok=True, parents=True)

            # Generate theme CSS
            css = self.preprocessor.generate_final_css(theme)

            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(css)

            logger.info(f"{Fore.GREEN}✓ {Fore.WHITE}Theme {Fore.CYAN}{theme}{Fore.WHITE} rebuilt -> {output_path}")

        # Rebuild icons CSS
        icon_css = self.icon_preprocessor.generate_icon_css(generate_variables=True)
        icon_output_path = self.themes_dir / "generated" / "icons.css"
        icon_output_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(icon_output_path, 'w', encoding='utf-8') as f:
            f.write(icon_css)
        
        logger.info(f"{Fore.GREEN}✓ {Fore.WHITE}Icons CSS rebuilt -> {icon_output_path}")

    def extract_variables(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Extract CSS variables for a theme

        Args:
            theme_name: Optional theme name (if None, returns base variables)

        Returns:
            Dictionary of variable names and values
        """
        variables = {}

        # Load base variables
        base_variables_path = self.themes_dir / "base" / "variables.css"
        if base_variables_path.exists():
            base_variables = self.preprocessor.parse_css_file(str(base_variables_path))
            variables.update(base_variables)

        # Load theme-specific variables if requested
        if theme_name:
            theme_path = self.themes_dir / "variants" / f"{theme_name}.css"
            if theme_path.exists():
                theme_variables = self.preprocessor.parse_css_file(str(theme_path))
                variables.update(theme_variables)

        return variables

    def print_variables(self, theme_name: Optional[str] = None):
        """Print CSS variables for a theme

        Args:
            theme_name: Optional theme name (if None, prints base variables)
        """
        variables = self.extract_variables(theme_name)

        if not variables:
            logger.warning(f"No variables found")
            return

        title = f"CSS Variables for {theme_name or 'base'}"
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{title}")
        print(f"{Fore.CYAN}{'-' * len(title)}")

        # Group variables by category
        categories = {}

        for name, value in sorted(variables.items()):
            # Determine category from prefix
            category = name.split('-')[0] if '-' in name else 'other'

            if category not in categories:
                categories[category] = []

            categories[category].append((name, value))

        # Print by category
        for category, vars_list in sorted(categories.items()):
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}{category.upper()}:")

            for name, value in sorted(vars_list):
                color_preview = ""
                if name.startswith('color-') and (value.startswith('#') or value.startswith('rgb')):
                    # Add color preview for colors
                    color_preview = "  " + value

                print(f"{Fore.GREEN}--{name}: {Fore.WHITE}{value}{color_preview}")

    def create_theme_skeleton(self, theme_name: str):
        """Create a new theme skeleton

        Args:
            theme_name: Name of the new theme
        """
        # Check if theme already exists
        theme_path = self.themes_dir / "variants" / f"{theme_name}.css"
        if theme_path.exists():
            logger.warning(f"Theme '{theme_name}' already exists: {theme_path}")
            return

        # Create theme file with skeleton
        with open(theme_path, 'w', encoding='utf-8') as f:
            f.write(f"/* {theme_name.capitalize()} Theme Variables */\n")
            f.write(f"/* Created: {time.strftime('%Y-%m-%d %H:%M:%S')} */\n\n")
            f.write(f":root[data-theme=\"{theme_name}\"] {{\n")
            f.write(f"    /* === COLORS === */\n")
            f.write(f"    /* Base colors */\n")
            f.write(f"    --color-white: #FFFFFF;\n")
            f.write(f"    --color-black: #000000;\n\n")
            f.write(f"    /* Text colors */\n")
            f.write(f"    --color-text-primary: #333333;\n")
            f.write(f"    --color-text-secondary: #666666;\n\n")
            f.write(f"    /* Background colors */\n")
            f.write(f"    --color-bg-primary: #FFFFFF;\n")
            f.write(f"    --color-bg-secondary: #F0F0F0;\n\n")
            f.write(f"    /* Add more variables as needed */\n")
            f.write(f"}}\n")

        logger.info(f"{Fore.GREEN}Created new theme skeleton: {theme_path}")
        logger.info(f"Edit the file to define your theme variables")

    def export_theme_json(self, theme_name: str, output_path: Optional[str] = None) -> str:
        """Export theme variables as JSON

        Args:
            theme_name: Name of the theme
            output_path: Optional path to save the JSON file

        Returns:
            JSON string of the theme variables
        """
        variables = self.extract_variables(theme_name)

        if not variables:
            logger.warning(f"No variables found for theme: {theme_name}")
            return "{}"

        # Convert to JSON
        json_data = json.dumps(variables, indent=2, sort_keys=True)

        # Save to file if output path is specified
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_data)

            logger.info(f"Exported theme variables to: {output_path}")

        return json_data

def main():
    parser = argparse.ArgumentParser(description="CSS Development Tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Watch command
    watch_parser = subparsers.add_parser("watch", help="Watch CSS files for changes")
    watch_parser.add_argument("--themes-dir", default="themes", help="Themes directory")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build all themes")
    build_parser.add_argument("--themes-dir", default="themes", help="Themes directory")

    # Variables command
    vars_parser = subparsers.add_parser("vars", help="Show CSS variables")
    vars_parser.add_argument("--theme", help="Theme name (if omitted, shows base variables)")
    vars_parser.add_argument("--themes-dir", default="themes", help="Themes directory")

    # New theme command
    new_parser = subparsers.add_parser("new", help="Create a new theme skeleton")
    new_parser.add_argument("name", help="Theme name")
    new_parser.add_argument("--themes-dir", default="themes", help="Themes directory")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export theme variables as JSON")
    export_parser.add_argument("theme", help="Theme name")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--themes-dir", default="themes", help="Themes directory")

    args = parser.parse_args()

    # Create dev tools
    dev_tools = CSSDevTools(args.themes_dir if hasattr(args, "themes_dir") else "themes")

    if args.command == "watch":
        dev_tools.rebuild_all_themes()  # Initial build
        dev_tools.watch_css_files()
    elif args.command == "build":
        dev_tools.rebuild_all_themes()
    elif args.command == "vars":
        dev_tools.print_variables(args.theme)
    elif args.command == "new":
        dev_tools.create_theme_skeleton(args.name)
    elif args.command == "export":
        dev_tools.export_theme_json(args.theme, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
