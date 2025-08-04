#!/usr/bin/env python3
"""
File Timestamp Utility Script

This script lists files in a specified directory and generates date_time prefixes
with milliseconds according to the project rules format: YYYYMMDD_HHMMSSzz_

Usage:
    python file_timestamp_util.py --path <directory_path> [--list-only] [--rename]

Examples:
    python file_timestamp_util.py --path docs/
    python file_timestamp_util.py --path docs/ --list-only
    python file_timestamp_util.py --path docs/ --rename
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import time


def get_file_timestamp_ms(file_path: Path) -> str:
    """
    Get file modification timestamp in the project format: YYYYMMDD_HHMMSSzz_

    Args:
        file_path: Path to the file

    Returns:
        Formatted timestamp string with milliseconds
    """
    try:
        # Get file modification time
        mtime = file_path.stat().st_mtime

        # Convert to datetime
        dt = datetime.fromtimestamp(mtime)

        # Get milliseconds from the fractional part
        milliseconds = int((mtime % 1) * 100)  # Convert to centiseconds (zz)

        # Format: YYYYMMDD_HHMMSSzz_
        timestamp = dt.strftime("%Y%m%d_%H%M%S") + f"{milliseconds:02d}_"

        return timestamp

    except Exception as e:
        print(f"Error getting timestamp for {file_path}: {e}")
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}00_"


def list_files_with_timestamps(directory_path: Path, file_extensions: list = None) -> list:
    """
    List files in directory with their timestamps.

    Args:
        directory_path: Directory to scan
        file_extensions: List of extensions to filter (e.g., ['.md', '.rst'])

    Returns:
        List of tuples (file_path, original_name, timestamp_prefix, new_name)
    """
    if not directory_path.exists():
        print(f"Error: Directory {directory_path} does not exist")
        return []

    if not directory_path.is_dir():
        print(f"Error: {directory_path} is not a directory")
        return []

    files_info = []

    try:
        for file_path in directory_path.iterdir():
            # Skip directories and hidden files
            if file_path.is_dir() or file_path.name.startswith('.'):
                continue

            # Filter by extensions if specified
            if file_extensions and file_path.suffix.lower() not in file_extensions:
                continue

            # Get timestamp prefix
            timestamp_prefix = get_file_timestamp_ms(file_path)

            # Generate new name
            original_name = file_path.name

            # Convert to lowercase and replace spaces/special chars with underscores
            base_name = file_path.stem.lower().replace(' ', '_').replace('-', '_')
            extension = file_path.suffix.lower()
            new_name = f"{timestamp_prefix}{base_name}{extension}"

            files_info.append((file_path, original_name, timestamp_prefix, new_name))

    except Exception as e:
        print(f"Error scanning directory {directory_path}: {e}")

    # Sort by timestamp
    files_info.sort(key=lambda x: x[2])

    return files_info


def print_file_list(files_info: list, show_details: bool = True):
    """
    Print formatted list of files with timestamps.

    Args:
        files_info: List of file information tuples
        show_details: Whether to show detailed information
    """
    if not files_info:
        print("No files found matching criteria.")
        return

    print(f"\nFound {len(files_info)} files:")
    print("=" * 80)

    if show_details:
        print(f"{'Original Name':<30} {'Timestamp':<18} {'New Name':<40}")
        print("-" * 80)

        for file_path, original_name, timestamp_prefix, new_name in files_info:
            # Truncate long names for display
            display_original = original_name[:28] + ".." if len(original_name) > 30 else original_name
            display_new = new_name[:38] + ".." if len(new_name) > 40 else new_name

            print(f"{display_original:<30} {timestamp_prefix:<18} {display_new:<40}")
    else:
        for file_path, original_name, timestamp_prefix, new_name in files_info:
            print(f"{timestamp_prefix}{original_name}")


def rename_files(files_info: list, target_directory: Path, dry_run: bool = True):
    """
    Rename files according to timestamp format.

    Args:
        files_info: List of file information tuples
        target_directory: Directory where renamed files should go
        dry_run: If True, only show what would be renamed
    """
    if not files_info:
        print("No files to rename.")
        return

    print(f"\n{'DRY RUN: ' if dry_run else ''}Renaming {len(files_info)} files:")
    print("=" * 80)

    for file_path, original_name, timestamp_prefix, new_name in files_info:
        target_path = target_directory / new_name

        print(f"{'[DRY RUN] ' if dry_run else ''}Rename:")
        print(f"  From: {file_path}")
        print(f"  To:   {target_path}")

        if not dry_run:
            try:
                # Create target directory if it doesn't exist
                target_directory.mkdir(parents=True, exist_ok=True)

                # Move/rename the file
                file_path.rename(target_path)
                print(f"  ✓ Success")

            except Exception as e:
                print(f"  ✗ Error: {e}")

        print()


def move_to_project_files(files_info: list, project_root: Path, dry_run: bool = True):
    """
    Move design/documentation files to project_files directory with timestamps.

    Args:
        files_info: List of file information tuples
        project_root: Root directory of the project
        dry_run: If True, only show what would be moved
    """
    project_files_dir = project_root / "project_files"

    if not project_files_dir.exists():
        if dry_run:
            print(f"[DRY RUN] Would create directory: {project_files_dir}")
        else:
            project_files_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {project_files_dir}")

    rename_files(files_info, project_files_dir, dry_run)


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="List files with timestamp prefixes according to project rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --path docs/
  %(prog)s --path docs/ --extensions .md .rst
  %(prog)s --path docs/ --list-only
  %(prog)s --path docs/ --rename --target project_files/
  %(prog)s --path docs/ --move-to-project-files --dry-run
        """
    )

    parser.add_argument(
        '--path', '-p',
        type=str,
        required=True,
        help='Directory path to scan for files'
    )

    parser.add_argument(
        '--extensions', '-e',
        nargs='*',
        default=['.md', '.rst'],
        help='File extensions to include (default: .md .rst)'
    )

    parser.add_argument(
        '--list-only', '-l',
        action='store_true',
        help='Only list files with timestamps, don\'t rename'
    )

    parser.add_argument(
        '--rename', '-r',
        action='store_true',
        help='Rename files with timestamp prefixes'
    )

    parser.add_argument(
        '--target', '-t',
        type=str,
        help='Target directory for renamed files (default: same directory)'
    )

    parser.add_argument(
        '--move-to-project-files', '-m',
        action='store_true',
        help='Move files to project_files directory with timestamps'
    )

    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what would be done without actually doing it'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )

    args = parser.parse_args()

    # Parse and validate arguments
    directory_path = Path(args.path).resolve()

    if not directory_path.exists():
        print(f"Error: Directory {directory_path} does not exist")
        sys.exit(1)

    # Get project root (assuming this script is in project root)
    project_root = Path(__file__).parent.resolve()

    print(f"Scanning directory: {directory_path}")
    print(f"File extensions: {args.extensions}")
    print(f"Project root: {project_root}")

    # List files with timestamps
    files_info = list_files_with_timestamps(directory_path, args.extensions)

    # Show file list
    print_file_list(files_info, show_details=args.verbose or not args.list_only)

    # Perform actions based on arguments
    if args.list_only:
        return

    if args.move_to_project_files:
        move_to_project_files(files_info, project_root, dry_run=args.dry_run)
    elif args.rename:
        target_dir = Path(args.target) if args.target else directory_path
        rename_files(files_info, target_dir, dry_run=args.dry_run)
    else:
        print("\nNo action specified. Use --list-only, --rename, or --move-to-project-files")
        print("Add --dry-run to see what would be done without making changes")


if __name__ == "__main__":
    main()
