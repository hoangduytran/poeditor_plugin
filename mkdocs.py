#!/usr/bin/env python3
"""
Script to generate HTML API documentation for the POEditor plugin project.

This script sets up and runs Sphinx to automatically generate API documentation
from the docstrings in the code. It can be run in watch mode to automatically
rebuild documentation when source files change.
"""

import os
import sys
import shutil
import subprocess
import importlib.util
import time
import argparse
import socket
import signal
from pathlib import Path
from typing import List, Set, Optional

def check_port_available(port: int) -> bool:
    """Check if the specified port is available.
    
    Args:
        port: The port number to check
        
    Returns:
        bool: True if the port is available, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Try to bind to the port
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

def find_available_port(start_port: int, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from the specified port.
    
    Args:
        start_port: The port number to start checking from
        max_attempts: Maximum number of ports to check
        
    Returns:
        Optional[int]: An available port number, or None if no port is available
    """
    current_port = start_port
    for _ in range(max_attempts):
        if check_port_available(current_port):
            return current_port
        current_port += 1
    return None

def kill_process_on_port(port: int) -> bool:
    """Attempt to kill the process using the specified port.
    
    Args:
        port: The port number used by the process to kill
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if sys.platform == 'win32':
            # Windows
            result = subprocess.run(
                ['netstat', '-ano', '|', 'findstr', f':{port}'], 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f':{port}' in line:
                        parts = line.strip().split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            subprocess.run(['taskkill', '/F', '/PID', pid])
                            print(f"Killed process {pid} using port {port}")
                            return True
        else:
            # For macOS and Linux
            cmd = f"lsof -i tcp:{port} -t"
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            
            if result.returncode != 0 or not result.stdout.strip():
                return False
            
            # Get PID from the output
            pid = result.stdout.strip().split('\n')[0]
            
            # Kill the process
            try:
                os.kill(int(pid), signal.SIGTERM)
                # Give it a moment to terminate
                time.sleep(0.5)
                
                # Check if it's still running
                if check_port_available(port):
                    return True
                
                # If still not available, try SIGKILL
                os.kill(int(pid), signal.SIGKILL)
                time.sleep(0.5)
                
                return check_port_available(port)
            except ProcessLookupError:
                # Process might have terminated already
                return check_port_available(port)
            except Exception as e:
                print(f"Error killing process: {str(e)}")
                return False
    except Exception as e:
        print(f"Error finding process on port {port}: {str(e)}")
        return False

def check_dependencies():
    """Check if Sphinx and needed extensions are installed."""
    try:
        import sphinx
        import sphinx_rtd_theme
    except ImportError as e:
        print(f"Error: Missing dependency - {str(e)}")
        print("Please install the required packages:")
        print("pip install -U sphinx sphinx_rtd_theme")
        return False
    return True

def create_sphinx_config():
    """Create the Sphinx configuration directory and files."""
    docs_dir = os.path.join(os.getcwd(), 'docs')
    source_dir = os.path.join(docs_dir, 'source')
    
    # Create directories if they don't exist
    os.makedirs(source_dir, exist_ok=True)
    
    # Create conf.py
    conf_py = os.path.join(source_dir, 'conf.py')
    with open(conf_py, 'w') as f:
        f.write('''# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'POEditor Plugin'
copyright = '2025, POEditor Development Team'
author = 'POEditor Development Team'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
''')
    
    # Skip creating index.rst - using existing file in docs directory

def create_module_docs():
    """Create .rst files for each module to document."""
    docs_dir = os.path.join(os.getcwd(), 'docs')
    source_dir = os.path.join(docs_dir, 'source')
    
    # Create services directory
    services_dir = os.path.join(source_dir, 'services')
    os.makedirs(services_dir, exist_ok=True)
    
    # Create services/index.rst
    services_index = os.path.join(services_dir, 'index.rst')
    with open(services_index, 'w') as f:
        f.write('''Services
========

.. toctree::
   :maxdepth: 2
   
   file_numbering_service
   undo_redo_service
   file_operations_service
''')
    
    # Create individual service documentation files
    service_files = {
        'file_numbering_service': 'services/file_numbering_service.py',
        'undo_redo_service': 'services/undo_redo_service.py',
        'file_operations_service': 'services/file_operations_service.py',
        'drag_drop_service': 'services/drag_drop_service.py'
    }
    
    for service_name, service_path in service_files.items():
        service_rst = os.path.join(services_dir, f'{service_name}.rst')
        with open(service_rst, 'w') as f:
            module_path = service_path.replace('/', '.').replace('.py', '')
            title = ' '.join(word.capitalize() for word in service_name.split('_'))
            f.write(f'''{title}
{'=' * len(title)}

.. automodule:: {module_path}
   :members:
   :undoc-members:
   :show-inheritance:
''')
    
    # Create models directory
    models_dir = os.path.join(source_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Create models/index.rst
    models_index = os.path.join(models_dir, 'index.rst')
    with open(models_index, 'w') as f:
        f.write('''Models
======

.. toctree::
   :maxdepth: 2
   
   file_system_models
''')
    
    # Create models/file_system_models.rst
    models_rst = os.path.join(models_dir, 'file_system_models.rst')
    with open(models_rst, 'w') as f:
        f.write('''File System Models
================

.. automodule:: models.file_system_models
   :members:
   :undoc-members:
   :show-inheritance:
''')

def build_documentation():
    """Build the HTML documentation using Sphinx."""
    docs_dir = os.path.join(os.getcwd(), 'docs')
    source_dir = os.path.join(docs_dir, 'source')
    build_dir = os.path.join(docs_dir, 'build/html')
    
    # Create build directory if it doesn't exist
    os.makedirs(os.path.join(docs_dir, 'build'), exist_ok=True)
    
    # Build documentation
    subprocess.check_call(["sphinx-build", "-b", "html", source_dir, build_dir])
    
    print(f"Documentation built successfully at {build_dir}")
    print(f"Open {os.path.join(build_dir, 'index.html')} in your browser to view it")

def get_watched_paths() -> List[Path]:
    """Get a list of paths to watch for changes."""
    root_dir = Path(os.getcwd())
    
    # Watch these directories for changes
    watch_dirs = [
        root_dir / "services",
        root_dir / "models",
        root_dir / "docs" / "source",
    ]
    
    # Add specific extensions to watch
    extensions = [".py", ".rst", ".md", ".css"]
    
    # Build a list of files to watch
    watched_paths = []
    for directory in watch_dirs:
        if directory.exists():
            for ext in extensions:
                watched_paths.extend(directory.glob(f"**/*{ext}"))
    
    return watched_paths

def get_file_modification_times(paths: List[Path]) -> dict:
    """Get the modification times for a list of paths."""
    return {path: path.stat().st_mtime for path in paths if path.exists()}

def watch_for_changes(interval: int = 1):
    """
    Watch for changes in source files and rebuild documentation when changes are detected.
    
    Args:
        interval: The interval in seconds to check for changes
    """
    paths = get_watched_paths()
    mod_times = get_file_modification_times(paths)
    
    print(f"Watching {len(paths)} files for changes (Ctrl+C to stop)...")
    
    try:
        while True:
            time.sleep(interval)
            
            # Check if any files have been modified
            new_mod_times = get_file_modification_times(paths)
            changed_files = []
            
            for path in paths:
                if path.exists() and path in new_mod_times:
                    if path not in mod_times or new_mod_times[path] > mod_times[path]:
                        changed_files.append(path)
            
            # If files have changed, rebuild the docs
            if changed_files:
                print(f"\n{len(changed_files)} files changed. Rebuilding documentation...")
                for file in changed_files[:5]:  # Show up to 5 changed files
                    print(f"  - {file.relative_to(os.getcwd())}")
                if len(changed_files) > 5:
                    print(f"  - and {len(changed_files) - 5} more...")
                
                # Rebuild documentation
                build_documentation()
                
                # Update modification times
                mod_times = new_mod_times
            
            # Check if any new files have been added
            new_paths = get_watched_paths()
            if set(new_paths) != set(paths):
                new_files = set(new_paths) - set(paths)
                removed_files = set(paths) - set(new_paths)
                
                if new_files:
                    print(f"\n{len(new_files)} new files detected. Updating watch list...")
                
                if removed_files:
                    print(f"\n{len(removed_files)} files removed. Updating watch list...")
                
                paths = new_paths
                mod_times = get_file_modification_times(paths)
    
    except KeyboardInterrupt:
        print("\nStopping documentation watch mode.")

# Functions already defined at the top of the file

def main():
    """Main function to generate API documentation."""
    parser = argparse.ArgumentParser(description="Generate API documentation for POEditor Plugin")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch for changes and rebuild automatically")
    parser.add_argument("--serve", "-s", action="store_true", help="Start a simple HTTP server to view documentation")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port for the HTTP server (default: 8080)")
    parser.add_argument("--update-only", "-u", action="store_true", help="Only update API docs, don't build HTML")
    parser.add_argument("--force", "-f", action="store_true", help="Force kill any process using the specified port")
    args = parser.parse_args()
    
    print("Generating API documentation for POEditor Plugin...")
    
    # Check and install dependencies
    check_dependencies()
    
    # Create Sphinx configuration
    create_sphinx_config()
    
    # Create module documentation
    create_module_docs()
    
    # Exit early if only updating API docs
    if args.update_only:
        print("API documentation updated successfully.")
        return
    
    # Build documentation
    build_documentation()
    
    print("Documentation generation complete!")
    
    # Start HTTP server if requested
    if args.serve:
        build_dir = os.path.join(os.getcwd(), 'docs', 'build', 'html')
        
        # Check if port is available
        port_to_use = args.port
        if not check_port_available(port_to_use):
            print(f"Port {port_to_use} is already in use.")
            
            if args.force:
                # Try to kill the process using the port
                print(f"Attempting to kill process using port {port_to_use}...")
                if kill_process_on_port(port_to_use):
                    print(f"Successfully freed port {port_to_use}.")
                    # Wait a moment for the port to be fully released
                    time.sleep(1)
                else:
                    print(f"Failed to free port {port_to_use}.")
                    # Try to find an alternative port
                    alternative_port = find_available_port(port_to_use + 1)
                    if alternative_port:
                        print(f"Using alternative port {alternative_port} instead.")
                        port_to_use = alternative_port
                    else:
                        print("No available ports found. Please free up a port and try again.")
                        return
            else:
                # Try to find an alternative port
                alternative_port = find_available_port(port_to_use + 1)
                if alternative_port:
                    print(f"Using alternative port {alternative_port} instead.")
                    port_to_use = alternative_port
                else:
                    print("No available ports found. Please free up a port and try again.")
                    print("Or use --force to attempt to kill the process using the port.")
                    return
        
        print(f"\nStarting HTTP server at http://localhost:{port_to_use}/")
        print("Press Ctrl+C to stop the server.")
        
        # Start server in a subprocess
        try:
            server_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(port_to_use)],
                cwd=build_dir
            )
        except Exception as e:
            print(f"Error starting server: {str(e)}")
            return
        
        try:
            if args.watch:
                # Watch for changes while server is running
                watch_for_changes()
            else:
                # Just keep the server running
                server_process.wait()
        except KeyboardInterrupt:
            print("\nStopping HTTP server.")
            server_process.terminate()
    
    # Watch for changes if requested (without server)
    elif args.watch:
        watch_for_changes()

if __name__ == "__main__":
    main()
