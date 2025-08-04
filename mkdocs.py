#!/usr/bin/env python3
"""
Secure documentation builder and server for POEditor Plugin.

This script safely builds and serves Sphinx documentation with proper security measures.
It reads configuration from the existing conf.py file and provides clean build options.
"""

import os
import sys
import shutil
import subprocess
import argparse
import time
import signal
import socket
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any
import importlib.util
import http.server
import socketserver
from contextlib import contextmanager


class DocumentationBuilder:
    """Secure documentation builder and server."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.docs_dir = self.project_root / "docs"
        self.source_dir = self.docs_dir / "source"
        self.build_dir = self.docs_dir / "build"
        self.html_dir = self.build_dir / "html"

        # Validate paths
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {self.project_root}")
        if not self.docs_dir.exists():
            raise ValueError(f"Docs directory does not exist: {self.docs_dir}")

    def load_sphinx_config(self) -> Dict[str, Any]:
        """Safely load configuration from conf.py."""
        conf_path = self.source_dir / "conf.py"
        if not conf_path.exists():
            raise FileNotFoundError(f"Sphinx config not found: {conf_path}")

        # Load the config module safely
        spec = importlib.util.spec_from_file_location("conf", conf_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load config from {conf_path}")

        conf_module = importlib.util.module_from_spec(spec)

        # Set up environment for config loading - but don't change working directory
        original_path = sys.path.copy()

        try:
            # Add source directory to path for imports
            sys.path.insert(0, str(self.source_dir))

            spec.loader.exec_module(conf_module)

            # Extract configuration
            config = {}
            for attr in dir(conf_module):
                if not attr.startswith('_'):
                    config[attr] = getattr(conf_module, attr)

            return config

        finally:
            # Restore environment
            sys.path[:] = original_path

    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        required = ['sphinx', 'sphinx_rtd_theme']
        missing = []

        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if missing:
            print(f"Error: Missing dependencies: {', '.join(missing)}")
            print("Install with: pip install sphinx sphinx_rtd_theme")
            return False

        return True

    def clean_build(self) -> None:
        """Safely clean the build directory."""
        if self.build_dir.exists():
            print(f"Cleaning build directory: {self.build_dir}")
            shutil.rmtree(self.build_dir)

        # Recreate build directory
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def build_docs(self, clean: bool = False) -> bool:
        """Build the documentation using Sphinx."""
        if clean:
            self.clean_build()

        # Ensure build directory exists
        self.build_dir.mkdir(parents=True, exist_ok=True)

        print("Building documentation...")

        try:
            # Use subprocess with explicit arguments (no shell injection)
            cmd = [
                sys.executable, "-m", "sphinx",
                "-b", "html",
                str(self.source_dir),
                str(self.html_dir)
            ]

            result = subprocess.run(
                cmd,
                cwd=str(self.docs_dir),  # Run from docs directory, not project root
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                print("Build failed with errors:")
                print(result.stderr)
                return False

            # Show warnings if any
            if result.stderr.strip():
                print("Build completed with warnings:")
                print(result.stderr)

            print(f"Documentation built successfully: {self.html_dir}")
            return True

        except subprocess.TimeoutExpired:
            print("Error: Build timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"Error building documentation: {e}")
            return False

    def find_available_port(self, start_port: int, max_attempts: int = 10) -> Optional[int]:
        """Find an available port starting from the specified port."""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None

    def serve_docs(self, port: int = 8000, open_browser: bool = False) -> None:
        """Serve the documentation using Python's built-in HTTP server."""
        if not self.html_dir.exists():
            print("Error: Documentation not built. Run with --build first.")
            return

        # Find available port
        available_port = self.find_available_port(port)
        if available_port is None:
            print(f"Error: No available ports found starting from {port}")
            return

        if available_port != port:
            print(f"Port {port} unavailable, using {available_port} instead")

        print(f"Serving documentation at http://localhost:{available_port}/")
        print("Press Ctrl+C to stop the server")

        # Change to html directory for serving
        original_cwd = os.getcwd()
        try:
            os.chdir(self.html_dir)

            # Create custom handler to suppress logs
            class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    # Only log errors
                    if args and len(args) > 1 and args[1].startswith('4'):
                        super().log_message(format, *args)

            with socketserver.TCPServer(("", available_port), QuietHTTPRequestHandler) as httpd:
                # Open browser if requested
                if open_browser:
                    import webbrowser
                    webbrowser.open(f'http://localhost:{available_port}/')

                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\nStopping server...")

        finally:
            os.chdir(original_cwd)

    def watch_and_rebuild(self, interval: int = 1) -> None:
        """Watch for file changes and rebuild documentation."""
        print(f"Watching for changes (checking every {interval}s)...")
        print("Press Ctrl+C to stop watching")

        # Get initial file states
        watched_paths = self._get_watched_files()
        file_times = self._get_file_times(watched_paths)

        try:
            while True:
                time.sleep(interval)

                # Check for changes
                current_paths = self._get_watched_files()
                current_times = self._get_file_times(current_paths)

                # Check for new, removed, or modified files
                changed = False

                # New files
                new_files = set(current_paths) - set(watched_paths)
                if new_files:
                    print(f"New files detected: {len(new_files)}")
                    changed = True

                # Removed files
                removed_files = set(watched_paths) - set(current_paths)
                if removed_files:
                    print(f"Files removed: {len(removed_files)}")
                    changed = True

                # Modified files
                for path in current_paths:
                    if path in file_times and path in current_times:
                        if current_times[path] > file_times[path]:
                            print(f"File changed: {path.relative_to(self.project_root)}")
                            changed = True
                            break

                if changed:
                    print("Rebuilding documentation...")
                    if self.build_docs():
                        print("Rebuild complete!")
                    else:
                        print("Rebuild failed!")

                    # Update tracking
                    watched_paths = current_paths
                    file_times = current_times

        except KeyboardInterrupt:
            print("\nStopping watch mode")

    def _get_watched_files(self) -> List[Path]:
        """Get list of files to watch for changes."""
        patterns = [
            "**/*.py",
            "**/*.rst",
            "**/*.md",
            "**/*.css",
            "**/*.js"
        ]

        watched = []

        # Watch source directory
        for pattern in patterns:
            watched.extend(self.source_dir.glob(pattern))

        # Watch key project files
        project_patterns = ["**/*.py"]
        for pattern in project_patterns:
            watched.extend(self.project_root.glob(pattern))

        return [p for p in watched if p.is_file()]

    def _get_file_times(self, paths: List[Path]) -> Dict[Path, float]:
        """Get modification times for files."""
        times = {}
        for path in paths:
            try:
                if path.exists():
                    times[path] = path.stat().st_mtime
            except OSError:
                # Skip files we can't access
                pass
        return times


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build and serve Sphinx documentation for POEditor Plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --build --clean          # Clean build documentation
  %(prog)s --serve --port 8080      # Serve on port 8080
  %(prog)s --build --serve          # Build and serve
  %(prog)s --watch                  # Watch for changes and rebuild
  %(prog)s --build --serve --watch  # Build, serve, and watch
        """
    )

    parser.add_argument(
        "--build", "-b",
        action="store_true",
        help="Build the documentation"
    )

    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Clean build directory before building"
    )

    parser.add_argument(
        "--serve", "-s",
        action="store_true",
        help="Serve the documentation with HTTP server"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port for HTTP server (default: 8000)"
    )

    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch for file changes and rebuild automatically"
    )

    parser.add_argument(
        "--open", "-o",
        action="store_true",
        help="Open browser when serving"
    )

    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not (args.build or args.serve or args.watch):
        parser.error("Must specify at least one of --build, --serve, or --watch")

    try:
        # Initialize builder
        builder = DocumentationBuilder(args.project_root)

        # Check dependencies
        if not builder.check_dependencies():
            sys.exit(1)

        # Load config to validate
        try:
            config = builder.load_sphinx_config()
            print(f"Loaded configuration for project: {config.get('project', 'Unknown')}")
        except Exception as e:
            print(f"Warning: Could not load Sphinx config: {e}")

        # Build documentation
        if args.build:
            if not builder.build_docs(clean=args.clean):
                print("Build failed!")
                sys.exit(1)

        # Set up serving and/or watching
        if args.serve and args.watch:
            # Run server in background thread
            server_thread = threading.Thread(
                target=builder.serve_docs,
                args=(args.port, args.open),
                daemon=True
            )
            server_thread.start()

            # Watch in main thread
            time.sleep(1)  # Give server time to start
            builder.watch_and_rebuild()

        elif args.serve:
            builder.serve_docs(args.port, args.open)

        elif args.watch:
            builder.watch_and_rebuild()

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
